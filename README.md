# Particle MCP Server

An MCP (Model Context Protocol) server that provides access to selected Particle Network Universal Accounts docs.

## Features

- **Resource Access**: Exposes 9 key Particle Universal Accounts docs as MCP resources.
- **Content Caching**: Intelligent caching with a configurable TTL (24 hours by default).
- **Content Parsing**: Structured parsing of documentation, including sections, code blocks, and links.
- **Search Functionality**: Search across all documentation content.
- **Built-in Tools**: Includes tools for searching, refreshing, and listing pages.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/soos3d/particle-mcp-server.git
    cd particle-mcp-server
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

You can run the server directly from the command line:

```bash
python3 main.py
```

The server will start and listen for MCP protocol messages via `stdio`.

## IDE Setup

### Windsurf Setup

To use this server as a tool source in Windsurf:

1.  Go to `Windsurf` > `Settings` > `Windsurf Settings` > `Cascade` > `Manage MCPs`.
2.  Click `View Raw Config`, this will open a JSON file, `mcp_config.json`.
3.  Add the following configuration:
    ```json
    {
        "mcpServers": {
        "particle-docs": {
            "command": "/YOUR-PATH-TO/particle-mcp-server/.venv/bin/python3",
            "args": ["/YOUR-PATH-TO/particle-mcp-server/main.py"],
            "env": {}
        }
        }
    }
    ```
4.  Save the configuration. Click `Refresh` in the MCPs settings.
5.  The server should now be available as a tool in Windsurf.

## Available Tools

The following tools are exposed by the server:

-   `search_docs`: Search across all documentation.
-   `refresh_resource`: Force a refresh of the cached content for a specific page.
-   `list_pages`: List all available documentation pages.

## Project Structure

```
particle-mcp-server/
├── src/                  # Source code
│   ├── server.py         # Main MCP server implementation
│   ├── config.py         # Configuration and page definitions
│   ├── docs_fetcher.py   # Fetches and caches documentation
│   ├── docs_parser.py    # Parses and structures content
│   └── resources.py      # MCP resource handlers
├── data/cache/           # Cached documentation content
├── requirements.txt      # Python dependencies
└── main.py               # Entry point
```
