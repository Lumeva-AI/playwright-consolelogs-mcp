#!/usr/bin/env python3

import asyncio
import json
import time
from typing import Dict, List, Optional, Any

# MCP imports
from mcp.server.fastmcp import FastMCP

# Note: Before running this script, you need to install:
# pip install playwright
# pip install modelcontextprotocol
# playwright install

class PlaywrightBrowserManager:
    def __init__(self, headless: bool = False):
        self.playwright = None
        self.browser = None
        self.page = None
        self.console_logs = []
        self.network_requests = []
        self.is_initialized = False
        self.headless = headless

    async def initialize(self) -> None:
        """Initialize the Playwright browser if not already initialized."""
        if self.is_initialized:
            return
            
        # Import here to avoid module import issues
        import asyncio
        from playwright.async_api import async_playwright

        self.playwright = await async_playwright().start()
        launch_options = {}
        if self.headless:
            launch_options["headless"] = True
        self.browser = await self.playwright.chromium.launch(**launch_options)
        self.is_initialized = True

    async def close(self) -> None:
        """Close the browser and Playwright instance."""
        if self.page:
            await self.page.close()
            self.page = None
            
        if self.browser:
            await self.browser.close()
            self.browser = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            
        self.is_initialized = False
        self.console_logs = []
        self.network_requests = []

    async def open_url(self, url: str) -> str:
        """Open a URL in the browser and start monitoring console and network.
        The browser will stay open for user interaction."""
        if not self.is_initialized:
            await self.initialize()
            
        # Close existing page if any
        if self.page:
            await self.page.close()
            
        # Clear previous logs and requests
        self.console_logs = []
        self.network_requests = []
        
        # Create a new page
        self.page = await self.browser.new_page()
        
        # Set up console log listener
        self.page.on("console", self._handle_console_message)
        
        # Set up network request listener
        self.page.on("request", self._handle_request)
        self.page.on("response", self._handle_response)
        
        # Navigate to the URL
        await self.page.goto(url, wait_until="networkidle")
        
        # Add a message to let the user know the browser will stay open
        
        return f"Opened {url} successfully. The browser window will remain open for you to interact with."

    def _handle_console_message(self, message) -> None:
        """Handle console messages from the page."""
        log_entry = {
            "type": message.type,
            "text": message.text,
            "location": message.location,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.console_logs.append(log_entry)

    def _handle_request(self, request) -> None:
        """Handle network requests."""
        request_entry = {
            "url": request.url,
            "method": request.method,
            "headers": request.headers,
            "timestamp": asyncio.get_event_loop().time(),
            "resourceType": request.resource_type,
            "id": id(request)
        }
        self.network_requests.append(request_entry)

    def _handle_response(self, response) -> None:
        """Handle network responses."""
        # Find the matching request and update it with response data
        for request in self.network_requests:
            if request.get("url") == response.url and "response" not in request:
                request["response"] = {
                    "status": response.status,
                    "statusText": response.status_text,
                    "headers": response.headers,
                    "timestamp": asyncio.get_event_loop().time()
                }
                break

    async def get_console_logs(self, last_n: int) -> List[Dict]:
        """Get console logs collected so far with deduplication of repeated messages.
        
        Args:
            last_n: Number of log entries to return, prioritizing the most recent ones.
                   Use a large number to get all logs.
        
        Returns:
            A list of deduplicated console log entries
        """
        if not self.console_logs:
            return []
            
        # Create a deduplicated version of the logs
        deduplicated_logs = []
        current_group = None
        
        # Sort logs by timestamp to ensure proper grouping
        sorted_logs = sorted(self.console_logs, key=lambda x: x.get('timestamp', 0))
        
        for log in sorted_logs:
            # If we have no current group or this log is different from the current group
            if (current_group is None or 
                log['type'] != current_group['type'] or 
                log['text'] != current_group['text']):
                
                # Start a new group
                current_group = {
                    'type': log['type'],
                    'text': log['text'],
                    'location': log['location'],
                    'timestamp': log['timestamp'],
                    'count': 1,
                    'timestamps': [log['timestamp']]
                }
                deduplicated_logs.append(current_group)
            else:
                # This is a repeated message, increment count and add timestamp
                current_group['count'] += 1
                current_group['timestamps'].append(log['timestamp'])
                # Update the text to show repetition count for repeated messages
                if current_group['count'] > 1:
                    current_group['text'] = f"{log['text']} (repeated {current_group['count']} times)"
        
        # Return only the last N entries
        # Sort by timestamp (descending) to get the most recent logs first
        deduplicated_logs.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        deduplicated_logs = deduplicated_logs[:last_n]
        # Sort back by timestamp (ascending) for consistent output
        deduplicated_logs.sort(key=lambda x: x.get('timestamp', 0))
        
        return deduplicated_logs

    async def get_network_requests(self, last_n: int) -> List[Dict]:
        """Get network requests collected so far.
        
        Args:
            last_n: Number of network request entries to return, prioritizing the most recent ones.
                   Use a large number to get all requests.
        
        Returns:
            A list of network request entries
        """
        if not self.network_requests:
            return []
            
        # Sort by timestamp (descending) to get the most recent requests first
        sorted_requests = sorted(self.network_requests, key=lambda x: x.get('timestamp', 0), reverse=True)
        # Take only the last N entries
        limited_requests = sorted_requests[:last_n]
        # Sort back by timestamp (ascending) for consistent output
        limited_requests.sort(key=lambda x: x.get('timestamp', 0))
        
        return limited_requests

# Create the MCP server
mcp = FastMCP("browser-monitor", headless=True)

# Create a browser manager instance
browser_manager = PlaywrightBrowserManager(headless=mcp.headless)

# Define MCP tools
@mcp.tool()
async def open_browser(url: str) -> str:
    """Open a browser at the specified URL and start monitoring console logs and network requests.
    
    Args:
        url: The URL to open in the browser
        
    Returns:
        A confirmation message
    """
    return await browser_manager.open_url(url)

@mcp.tool()
async def get_console_logs(last_n: int) -> List[Dict]:
    """Get console logs from the currently open browser page.
    Repeated messages are deduplicated and shown with a count of repetitions.
    
    Args:
        last_n: Number of log entries to return, prioritizing the most recent ones.
               Use a large number to get all logs.
    
    Returns:
        A list of console log entries with type, text, location, timestamp, and count for repeated messages
    """
    return await browser_manager.get_console_logs(last_n)

@mcp.tool()
async def get_network_requests(last_n: int) -> List[Dict]:
    """Get network requests from the currently open browser page.
    
    Args:
        last_n: Number of network request entries to return, prioritizing the most recent ones.
               Use a large number to get all requests.
    
    Returns:
        A list of network request entries with URL, method, headers, and response data
    """
    return await browser_manager.get_network_requests(last_n)

@mcp.tool()
async def close_browser() -> str:
    """Close the browser and clean up resources.
    
    Returns:
        A confirmation message
    """
    await browser_manager.close()
    return "Browser closed successfully"

def main():
    mcp.run()

# Run the server when the script is executed directly
if __name__ == "__main__":
    # This will automatically handle the server lifecycle and run it
    main()