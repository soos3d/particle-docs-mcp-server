"""Main MCP server for Particle documentation."""

import asyncio
import logging
from typing import Any

from mcp.server import Server
import mcp.server.stdio
import mcp.types as types

from .config import ServerConfig, PARTICLE_PAGES
from .docs_fetcher import DocsFetcher
from .resources import ResourceManager

logger = logging.getLogger(__name__)


class ParticleMCPServer:
    """MCP Server for Particle documentation."""
    
    def __init__(self):
        self.config = ServerConfig()
        self.server = Server("particle-docs", version=self.config.version)
        self.fetcher = DocsFetcher(self.config)
        self.resource_manager = ResourceManager(self.fetcher)
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """Handle resource listing requests."""
            logger.info("📋 MCP client requested resource list")
            resources = await self.resource_manager.list_resources()
            logger.info(f"📋 Returning {len(resources)} available resources")
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle resource reading requests."""
            logger.info(f"📖 MCP client requested resource: {uri}")
            content = await self.resource_manager.get_resource(uri)
            if content is None:
                logger.warning(f"❌ Resource not found: {uri}")
                raise ValueError(f"Resource not found: {uri}")
            logger.info(f"📖 Successfully served resource: {uri} ({len(content.text)} chars)")
            return content.text
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            logger.info("🔧 MCP client requested tool list")
            tools = [
                types.Tool(
                    name="search_docs",
                    description="Search across Particle documentation for specific content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant documentation"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="refresh_resource",
                    description="Refresh cached content for a specific documentation page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "uri": {
                                "type": "string",
                                "description": "Resource URI to refresh (e.g., particle://universal-accounts/overview)"
                            }
                        },
                        "required": ["uri"]
                    }
                ),
                types.Tool(
                    name="list_pages",
                    description="List all available Particle documentation pages with their categories",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
            logger.info(f"🔧 Returning {len(tools)} available tools")
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
            """Handle tool execution requests."""
            logger.info(f"⚡ MCP client called tool: {name} with args: {arguments}")
            if arguments is None:
                arguments = {}
            
            if name == "search_docs":
                query = arguments.get("query", "")
                if not query:
                    return [types.TextContent(
                        type="text",
                        text="Error: Query parameter is required"
                    )]
                
                results = await self.resource_manager.search_resources(query)
                
                if not results:
                    return [types.TextContent(
                        type="text",
                        text=f"No results found for query: '{query}'"
                    )]
                
                # Format search results
                response_lines = [f"Search results for '{query}':\n"]
                
                for result in results:
                    response_lines.append(f"## {result['title']} ({result['category']})")
                    response_lines.append(f"Resource: {result['resource_uri']}")
                    response_lines.append("Matching sections:")
                    
                    for section in result['matching_sections']:
                        response_lines.append(f"- **{section['title']}**: {section['content']}")
                    
                    response_lines.append("")
                
                return [types.TextContent(
                    type="text",
                    text="\n".join(response_lines)
                )]
            
            elif name == "refresh_resource":
                uri = arguments.get("uri", "")
                if not uri:
                    return [types.TextContent(
                        type="text",
                        text="Error: URI parameter is required"
                    )]
                
                success = await self.resource_manager.refresh_resource(uri)
                
                if success:
                    return [types.TextContent(
                        type="text",
                        text=f"Successfully refreshed resource: {uri}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Failed to refresh resource: {uri}"
                    )]
            
            elif name == "list_pages":
                response_lines = ["Available Particle Documentation Pages:\n"]
                
                # Group by category
                categories = {}
                for page in PARTICLE_PAGES:
                    if page.category not in categories:
                        categories[page.category] = []
                    categories[page.category].append(page)
                
                for category, pages in categories.items():
                    response_lines.append(f"## {category}")
                    for page in pages:
                        response_lines.append(f"- **{page.title}**")
                        response_lines.append(f"  - URI: {page.resource_uri}")
                        response_lines.append(f"  - URL: {page.url}")
                        response_lines.append(f"  - Description: {page.description}")
                    response_lines.append("")
                
                return [types.TextContent(
                    type="text",
                    text="\n".join(response_lines)
                )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    async def run(self):
        """Run the MCP server."""
        logger.info("🔌 Initializing MCP server connection...")
        try:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                logger.info("✅ MCP server started and listening for requests")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"💥 MCP server error: {e}")
            raise
        finally:
            logger.info("🧹 Cleaning up server resources...")
            await self.fetcher.close()
            logger.info("✅ Server cleanup completed")


async def main():
    """Main entry point."""
    server = ParticleMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
