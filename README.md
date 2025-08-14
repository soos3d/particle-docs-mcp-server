# Particle MCP Server

An MCP (Model Context Protocol) server that provides access to selected Particle Network documentation pages.

## Features

- **Resource Access**: Exposes 9 key Particle documentation pages as MCP resources
- **Content Caching**: Intelligent caching with configurable TTL (24 hours default)
- **Content Parsing**: Structured parsing of documentation with sections, code blocks, and links
- **Search Functionality**: Search across all documentation content
- **Tools**: Built-in tools for searching, refreshing, and listing pages

## Supported Documentation Pages

### Core
- Universal Accounts Overview
- Supported Chains

### Getting Started
- Web Quickstart

### How-To Guides
- Provider Setup
- Getting Balances
- Transaction Preview
- Token Conversions

### Reference
- Web SDK Reference
- FAQ

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the MCP server:
```bash
python main.py
```

The server will start and listen for MCP protocol messages via stdio.

## MCP Resources

Each documentation page is exposed as an MCP resource with URIs like:
- `particle://universal-accounts/overview`
- `particle://guides/balances`
- `particle://reference/web-sdk`

## Available Tools

1. **search_docs**: Search across all documentation
2. **refresh_resource**: Force refresh cached content for a specific page
3. **list_pages**: List all available pages with metadata

## Project Structure

```
particle-mcp-server/
├── src/
│   ├── server.py          # Main MCP server implementation
│   ├── config.py          # Configuration and page definitions
│   ├── docs_fetcher.py    # Fetch and cache documentation
│   ├── docs_parser.py     # Parse and structure content
│   └── resources.py       # MCP resource handlers
├── data/cache/            # Cached documentation content
├── requirements.txt       # Python dependencies
└── main.py               # Entry point
```
