"""Particle MCP Server package."""

from .server import ParticleMCPServer, main
from .config import ServerConfig, PageConfig, PARTICLE_PAGES
from .docs_fetcher import DocsFetcher
from .docs_parser import DocsParser
from .resources import ResourceManager

__version__ = "1.0.0"
__all__ = [
    "ParticleMCPServer",
    "main",
    "ServerConfig",
    "PageConfig",
    "PARTICLE_PAGES",
    "DocsFetcher",
    "DocsParser",
    "ResourceManager",
]
