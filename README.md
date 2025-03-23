# Browser Monitoring MCP Server

This MCP (Model Context Protocol) server uses Playwright to open a browser, monitor console logs, and track network requests. It exposes these capabilities as tools that can be used by MCP clients.

## Features

- Open a browser at a specified URL
- Monitor and retrieve console logs
- Track and retrieve network requests
- Close the browser when done

## Requirements

- Python 3.8+
- Playwright
- Model Context Protocol (MCP) Python SDK

## Installation

1. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```
   playwright install
   ```

## Usage

1. Start the MCP server:
   ```
   python playwright.py
   ```

2. Connect to the server using an MCP client (like Claude Desktop, Continue, etc.)

3. Use the following tools:

   - `open_browser(url)`: Open a browser at the specified URL
   - `get_console_logs()`: Get all console logs from the current page
   - `get_network_requests()`: Get all network requests from the current page
   - `close_browser()`: Close the browser and clean up resources

## Example

Using Claude Desktop or another MCP client, you can:

1. Open a website:
   ```
   I'll use the open_browser tool to navigate to example.com
   ```

2. Retrieve console logs:
   ```
   Can you show me the console logs from the page?
   ```

3. Analyze network requests:
   ```
   What network requests were made when loading the page?
   ```

4. Close the browser when done:
   ```
   Please close the browser now
   ```

## How It Works

The server uses Playwright's event listeners to capture console messages and network activity. When a client requests this information, the server returns it in a structured format that can be used by the LLM.
