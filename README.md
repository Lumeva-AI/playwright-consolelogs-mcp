# Console and Network Logs Playwright MCP Server

[![smithery badge](https://smithery.ai/badge/@Lumeva-AI/playwright-consolelogs-mcp)](https://smithery.ai/server/@Lumeva-AI/playwright-consolelogs-mcp)

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

## Installation in claude

Edit the file:
`~/Library/Application\ Support/Claude/claude_desktop_config.json`

Add this:

```json
"playwright": {
   "command": "/Users/christophersettles/.local/bin/uv",
   "args": [
      "--directory",
      "/ABSOLUTE/PATH/TO/playwrightdebugger/",
      "run",
      "mcp_playwright.py"
   ]
}
```

(Replace `/ABSOLUTE/PATH/TO/playwrightdebugger/` with the absolute path to the directory where you cloned the repository)

## Commands

Open localhost:3000/dashboard and look at console logs and network requests

Close the browser

## How It Works

The server uses Playwright's event listeners to capture console messages and network activity. When a client requests this information, the server returns it in a structured format that can be used by the LLM.
