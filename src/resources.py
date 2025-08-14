"""MCP resource handlers for Particle documentation."""

from typing import Dict, List, Optional
import mcp.types as types

from .config import PageConfig, PARTICLE_PAGES, PAGES_BY_URI
from .docs_fetcher import DocsFetcher
from .docs_parser import DocsParser, ParsedContent


class ResourceManager:
    """Manages MCP resources for Particle documentation."""
    
    def __init__(self, fetcher: DocsFetcher):
        self.fetcher = fetcher
        self.parser = DocsParser()
        self._content_cache: Dict[str, ParsedContent] = {}
    
    async def list_resources(self) -> List[types.Resource]:
        """List all available documentation resources."""
        resources = []
        
        for page in PARTICLE_PAGES:
            resource = types.Resource(
                uri=page.resource_uri,
                name=page.title,
                description=page.description,
                mimeType="text/plain"
            )
            resources.append(resource)
        
        return resources
    
    async def get_resource(self, uri: str) -> Optional[types.TextResourceContents]:
        """Get content for a specific resource URI."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Convert URI to string in case it's an AnyUrl object
        uri_str = str(uri)
        
        logger.info(f"🔍 Looking up resource URI: {uri_str}")
        logger.info(f"🔍 URI bytes: {uri_str.encode('utf-8')}")
        logger.info(f"🔍 URI repr: {repr(uri_str)}")
        
        # Debug: Check exact matches
        for available_uri in PAGES_BY_URI.keys():
            logger.info(f"🔍 Comparing with: {repr(available_uri)} (bytes: {available_uri.encode('utf-8')})")
            if uri_str == available_uri:
                logger.info(f"✅ Found exact match!")
                break
        
        page_config = PAGES_BY_URI.get(uri_str)
        if not page_config:
            logger.error(f"❌ URI not found in PAGES_BY_URI: {uri_str}")
            logger.info(f"📋 Available URIs: {list(PAGES_BY_URI.keys())}")
            return None
        
        logger.info(f"✅ Found page config for {uri_str}: {page_config.title}")
        
        # Check if we have parsed content cached
        if uri_str in self._content_cache:
            logger.info(f"📦 Using cached content for {uri_str}")
            parsed_content = self._content_cache[uri_str]
        else:
            try:
                logger.info(f"🌐 Fetching content from {page_config.url}")
                # Fetch and parse content
                page_data = await self.fetcher.get_page_content(page_config)
                logger.info(f"📄 Received {len(page_data.get('content', ''))} chars of content")
                
                parsed_content = self.parser.parse_content(
                    page_data["content"], 
                    page_config.title
                )
                logger.info(f"✅ Parsed content: {len(parsed_content.sections)} sections")
                self._content_cache[uri_str] = parsed_content
            except Exception as e:
                logger.error(f"❌ Failed to fetch/parse content for {uri_str}: {e}")
                return None
        
        # Format content for MCP
        try:
            formatted_content = self._format_content_for_mcp(parsed_content, page_config)
            logger.info(f"📝 Formatted content: {len(formatted_content)} chars")
            
            return types.TextResourceContents(
                uri=uri_str,
                text=formatted_content,
                mimeType="text/plain"
            )
        except Exception as e:
            logger.error(f"❌ Failed to format content for {uri_str}: {e}")
            return None
    
    def _format_content_for_mcp(self, parsed_content: ParsedContent, page_config: PageConfig) -> str:
        """Format parsed content for MCP consumption."""
        lines = []
        
        # Header with metadata
        lines.append(f"# {parsed_content.title}")
        lines.append(f"**Category:** {page_config.category}")
        lines.append(f"**URL:** {page_config.url}")
        lines.append(f"**Description:** {page_config.description}")
        lines.append("")
        
        # Summary
        if parsed_content.summary:
            lines.append("## Summary")
            lines.append(parsed_content.summary)
            lines.append("")
        
        # Table of Contents
        if len(parsed_content.sections) > 1:
            lines.append("## Table of Contents")
            for section in parsed_content.sections:
                indent = "  " * (section.level - 1)
                lines.append(f"{indent}- {section.title}")
            lines.append("")
        
        # Sections
        lines.append("## Content")
        for section in parsed_content.sections:
            if section.level == 1:
                lines.append(f"# {section.title}")
            else:
                lines.append(f"{'#' * section.level} {section.title}")
            
            if section.content:
                lines.append(section.content)
            lines.append("")
        
        # Code blocks summary
        if parsed_content.code_blocks:
            lines.append("## Code Examples")
            for i, code_block in enumerate(parsed_content.code_blocks, 1):
                lang = code_block.language or "text"
                lines.append(f"### Example {i} ({lang})")
                lines.append(f"```{lang}")
                lines.append(code_block.content)
                lines.append("```")
                lines.append("")
        
        # Links
        if parsed_content.links:
            lines.append("## Related Links")
            for link in parsed_content.links:
                link_type = "External" if link["is_external"] else "Internal"
                lines.append(f"- [{link['text']}]({link['url']}) ({link_type})")
            lines.append("")
        
        return "\n".join(lines)
    
    async def search_resources(self, query: str) -> List[Dict]:
        """Search across all resources for content matching the query."""
        results = []
        
        for page in PARTICLE_PAGES:
            try:
                # Get or fetch content
                if page.resource_uri in self._content_cache:
                    parsed_content = self._content_cache[page.resource_uri]
                else:
                    page_data = await self.fetcher.get_page_content(page)
                    parsed_content = self.parser.parse_content(
                        page_data["content"], 
                        page.title
                    )
                    self._content_cache[page.resource_uri] = parsed_content
                
                # Search within content
                matching_sections = self.parser.search_content(parsed_content, query)
                
                if matching_sections:
                    results.append({
                        "resource_uri": page.resource_uri,
                        "title": page.title,
                        "category": page.category,
                        "matching_sections": [
                            {
                                "title": section.title,
                                "content": section.content[:200] + "..." if len(section.content) > 200 else section.content,
                                "anchor": section.anchor
                            }
                            for section in matching_sections
                        ]
                    })
            
            except Exception as e:
                # Log error but continue with other pages
                print(f"Error searching {page.resource_uri}: {e}")
                continue
        
        return results
    
    async def refresh_resource(self, uri: str) -> bool:
        """Refresh cached content for a specific resource."""
        # Convert URI to string in case it's an AnyUrl object
        uri_str = str(uri)
        
        page_config = PAGES_BY_URI.get(uri_str)
        if not page_config:
            return False
        
        try:
            # Force refresh from source
            page_data = await self.fetcher.refresh_cache(page_config)
            parsed_content = self.parser.parse_content(
                page_data["content"], 
                page_config.title
            )
            self._content_cache[uri_str] = parsed_content
            return True
        except Exception as e:
            print(f"Error refreshing {uri}: {e}")
            return False
    
    def clear_cache(self):
        """Clear all cached content."""
        self._content_cache.clear()
