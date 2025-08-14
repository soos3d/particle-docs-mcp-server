"""Documentation fetcher for Particle docs."""

import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import aiofiles
import httpx
from bs4 import BeautifulSoup

from .config import PageConfig, ServerConfig


class DocsFetcher:
    """Handles fetching and caching of documentation pages."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Particle-MCP-Server/1.0.0"
            }
        )
    
    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path for a URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.json"
    
    async def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cached content is still valid."""
        if not cache_path.exists():
            return False
        
        try:
            async with aiofiles.open(cache_path, 'r') as f:
                cache_data = json.loads(await f.read())
            
            cached_time = datetime.fromisoformat(cache_data['cached_at'])
            expiry_time = cached_time + timedelta(hours=self.config.cache_ttl_hours)
            
            return datetime.now() < expiry_time
        except (json.JSONDecodeError, KeyError, ValueError):
            return False
    
    async def _save_to_cache(self, url: str, content: str, metadata: Dict) -> None:
        """Save content to cache."""
        cache_path = self._get_cache_path(url)
        cache_data = {
            "url": url,
            "content": content,
            "metadata": metadata,
            "cached_at": datetime.now().isoformat()
        }
        
        async with aiofiles.open(cache_path, 'w') as f:
            await f.write(json.dumps(cache_data, indent=2))
    
    async def _load_from_cache(self, url: str) -> Optional[Dict]:
        """Load content from cache."""
        cache_path = self._get_cache_path(url)
        
        if not await self._is_cache_valid(cache_path):
            return None
        
        try:
            async with aiofiles.open(cache_path, 'r') as f:
                return json.loads(await f.read())
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def _html_to_markdown(self, element) -> str:
        """Convert HTML element to markdown-like text, preserving headers."""
        if not element:
            return ""
        
        lines = []
        
        # Process each child element
        for child in element.descendants:
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Convert HTML headers to markdown headers
                level = int(child.name[1])  # Extract number from h1, h2, etc.
                header_text = child.get_text(strip=True)
                if header_text:
                    lines.append(f"{'#' * level} {header_text}")
                    lines.append("")  # Add blank line after header
            elif child.name == 'p':
                # Add paragraph text
                para_text = child.get_text(strip=True)
                if para_text:
                    lines.append(para_text)
                    lines.append("")  # Add blank line after paragraph
            elif child.name in ['code', 'pre']:
                # Preserve code blocks
                code_text = child.get_text(strip=True)
                if code_text:
                    lines.append(f"```")
                    lines.append(code_text)
                    lines.append("```")
                    lines.append("")
            elif child.name in ['ul', 'ol']:
                # Handle lists
                for li in child.find_all('li', recursive=False):
                    li_text = li.get_text(strip=True)
                    if li_text:
                        lines.append(f"- {li_text}")
                lines.append("")
        
        # Clean up multiple consecutive blank lines
        result = []
        prev_blank = False
        for line in lines:
            if line.strip() == "":
                if not prev_blank:
                    result.append("")
                prev_blank = True
            else:
                result.append(line)
                prev_blank = False
        
        return "\n".join(result).strip()

    async def _fetch_page_content(self, url: str) -> tuple[str, Dict]:
        """Fetch page content from URL."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Parse HTML to extract main content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_elem = soup.find('title')
            title = title_elem.get_text().strip() if title_elem else "Untitled"
            
            # Extract main content (adjust selectors based on Particle docs structure)
            content_selectors = [
                'main',
                '.content',
                'article',
                '[role="main"]',
                '.markdown-body'
            ]
            
            content_elem = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    break
            
            if not content_elem:
                content_elem = soup.find('body')
            
            # Extract text content while preserving header structure
            content = self._html_to_markdown(content_elem) if content_elem else ""
            
            # Extract metadata
            metadata = {
                "title": title,
                "url": url,
                "fetched_at": datetime.now().isoformat(),
                "content_length": len(content)
            }
            
            return content, metadata
            
        except httpx.RequestError as e:
            raise Exception(f"Failed to fetch {url}: {e}")
        except Exception as e:
            raise Exception(f"Error processing {url}: {e}")
    
    async def get_page_content(self, page_config: PageConfig) -> Dict:
        """Get page content, using cache if available."""
        # Try cache first
        cached_data = await self._load_from_cache(page_config.url)
        if cached_data:
            return {
                "content": cached_data["content"],
                "metadata": cached_data["metadata"],
                "from_cache": True
            }
        
        # Fetch fresh content
        content, metadata = await self._fetch_page_content(page_config.url)
        
        # Save to cache
        await self._save_to_cache(page_config.url, content, metadata)
        
        return {
            "content": content,
            "metadata": metadata,
            "from_cache": False
        }
    
    async def refresh_cache(self, page_config: PageConfig) -> Dict:
        """Force refresh cache for a specific page."""
        content, metadata = await self._fetch_page_content(page_config.url)
        await self._save_to_cache(page_config.url, content, metadata)
        
        return {
            "content": content,
            "metadata": metadata,
            "from_cache": False
        }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
