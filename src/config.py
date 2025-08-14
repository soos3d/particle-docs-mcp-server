"""Configuration for the Particle MCP Server."""

import os
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel


class PageConfig(BaseModel):
    """Configuration for a documentation page."""
    url: str
    resource_uri: str
    title: str
    category: str
    description: str


class ServerConfig(BaseModel):
    """Main server configuration."""
    name: str = "particle-docs"
    version: str = "1.0.0"
    cache_dir: str = str(Path.home() / ".cache" / "particle-mcp-server")
    cache_ttl_hours: int = 24


# Predefined list of Particle documentation pages
PARTICLE_PAGES: List[PageConfig] = [
    PageConfig(
        url="https://developers.particle.network/universal-accounts/cha/overview",
        resource_uri="particle://universal-accounts/overview",
        title="Universal Accounts Overview",
        category="Core",
        description="Learn about the Universal Accounts SDK—your entry point to integrating chain abstraction."
    ),
    PageConfig(
        url="https://developers.particle.network/universal-accounts/cha/chains",
        resource_uri="particle://universal-accounts/chains",
        title="Supported Chains",
        category="Core",
        description="List of chains supported by Universal Accounts."
    ),
    PageConfig(
        url="https://developers.particle.network/universal-accounts/cha/web-quickstart",
        resource_uri="particle://universal-accounts/quickstart",
        title="Web Quickstart",
        category="Getting Started",
        description="A step-by-step setup guide for integrating the UAs SDK into your application."
    ),
    PageConfig(
        url="https://developers.particle.network/universal-accounts/cha/how-to/provider",
        resource_uri="particle://guides/provider",
        title="Provider Setup",
        category="How-To",
        description="Learn how to set up and configure providers for Universal Accounts."
    ),
    PageConfig(
        url="https://developers.particle.network/universal-accounts/cha/how-to/balances",
        resource_uri="particle://guides/balances",
        title="Getting Balances",
        category="How-To",
        description="Learn how to fetch and display the unified balance of a Universal Account."
    ),
    PageConfig(
        url="https://developers.particle.network/universal-accounts/cha/how-to/tx-preview",
        resource_uri="particle://guides/tx-preview",
        title="Transaction Preview",
        category="How-To",
        description="Learn how to preview transactions before execution."
    ),
    PageConfig(
        url="https://developers.particle.network/universal-accounts/cha/how-to/conversions",
        resource_uri="particle://guides/conversions",
        title="Token Conversions",
        category="How-To",
        description="Learn how to handle token conversions in Universal Accounts."
    ),
    PageConfig(
        url="https://developers.particle.network/universal-accounts/ua-reference/desktop/web",
        resource_uri="particle://reference/web-sdk",
        title="Web SDK Reference",
        category="Reference",
        description="SDK and API reference for the Universal Accounts Web SDK."
    ),
    PageConfig(
        url="https://developers.particle.network/universal-accounts/ua-reference/faq",
        resource_uri="particle://reference/faq",
        title="FAQ",
        category="Reference",
        description="Frequently asked questions about Universal Accounts."
    ),
]

# Create lookup dictionaries for easy access
PAGES_BY_URI: Dict[str, PageConfig] = {page.resource_uri: page for page in PARTICLE_PAGES}
PAGES_BY_URL: Dict[str, PageConfig] = {page.url: page for page in PARTICLE_PAGES}
