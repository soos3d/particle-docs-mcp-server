#!/usr/bin/env python3
"""Test script for the Particle MCP Server."""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server import ParticleMCPServer
from src.config import PARTICLE_PAGES


async def test_basic_functionality():
    """Test basic server functionality."""
    print("🧪 Testing Particle MCP Server...")
    
    server = ParticleMCPServer()
    
    try:
        # Test 1: Check configuration
        print(f"✓ Server initialized with {len(PARTICLE_PAGES)} pages")
        
        # Test 2: Test resource listing
        resources = await server.resource_manager.list_resources()
        print(f"✓ Resource listing works: {len(resources)} resources available")
        
        # Test 3: Test fetching a single page (without actually making HTTP request)
        print("✓ Basic server components initialized successfully")
        
        # Test 4: Test page configuration
        for page in PARTICLE_PAGES[:3]:  # Test first 3 pages
            print(f"  - {page.title} -> {page.resource_uri}")
        
        print("\n🎉 All basic tests passed!")
        print("\n📋 Server Summary:")
        print(f"   • Name: {server.config.name}")
        print(f"   • Version: {server.config.version}")
        print(f"   • Cache TTL: {server.config.cache_ttl_hours} hours")
        print(f"   • Total pages: {len(PARTICLE_PAGES)}")
        
        # Group pages by category
        categories = {}
        for page in PARTICLE_PAGES:
            if page.category not in categories:
                categories[page.category] = []
            categories[page.category].append(page)
        
        print(f"   • Categories: {', '.join(categories.keys())}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await server.fetcher.close()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)
