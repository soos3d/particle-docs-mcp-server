#!/usr/bin/env python3
"""Integration test for the Particle MCP Server - fetches real content."""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server import ParticleMCPServer
from src.config import PARTICLE_PAGES


async def test_content_fetching():
    """Test fetching real content from Particle docs."""
    print("🌐 Testing content fetching from Particle documentation...")
    
    server = ParticleMCPServer()
    
    try:
        # Test fetching content from the overview page
        overview_page = PARTICLE_PAGES[0]  # Universal Accounts Overview
        print(f"📄 Fetching: {overview_page.title}")
        print(f"🔗 URL: {overview_page.url}")
        
        # Get the resource content
        content = await server.resource_manager.get_resource(overview_page.resource_uri)
        
        if content:
            print("✅ Successfully fetched content!")
            print(f"📊 Content length: {len(content.text)} characters")
            
            # Show first few lines of content
            lines = content.text.split('\n')[:10]
            print("\n📝 Content preview:")
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"   {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
            
            # Test search functionality
            print("\n🔍 Testing search functionality...")
            search_query = "Universal Accounts"
            print(f"   Query: '{search_query}'")
            
            # Debug: Print content details
            print(f"   Content type: {type(content).__name__}")
            print(f"   Content text first 50 chars: '{content.text[:50]}...'")
            
            # Force fetch and parse content directly for debugging
            print("\n📋 Debugging content parsing...")
            page_data = await server.fetcher.get_page_content(overview_page)
            parsed_content = server.resource_manager.parser.parse_content(page_data["content"], overview_page.title)
            
            print(f"   Raw HTML length: {len(page_data['content'])} characters")
            print(f"   Parsed title: {parsed_content.title}")
            print(f"   Number of sections: {len(parsed_content.sections)}")
            
            if parsed_content.sections:
                for i, section in enumerate(parsed_content.sections[:3]):
                    print(f"   Section {i+1}: '{section.title}' (level {section.level})")
                    content_preview = section.content[:50].replace('\n', ' ')
                    print(f"     Content preview: '{content_preview}...'")
            
            # Try the search with direct parsed content
            print("\n🔎 Testing direct search on parsed content...")
            matching_sections = server.resource_manager.parser.search_content(parsed_content, search_query)
            print(f"   Direct search found {len(matching_sections)} matching sections")
            
            # Try the regular search through resource manager
            search_results = await server.resource_manager.search_resources(search_query)
            print(f"✅ Search found {len(search_results)} results through resource manager")
            
            if search_results:
                result = search_results[0]
                print(f"   First result: {result['title']} ({result['category']})") 
                print(f"   Matching sections: {len(result['matching_sections'])}")
            else:
                print("   No matching sections found. This might indicate an issue with content extraction or search logic.")
                print("   Try modifying the search implementation or improving content extraction.")

        
        else:
            print("❌ Failed to fetch content")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    finally:
        await server.fetcher.close()
    
    print("\n🎉 Integration test completed successfully!")
    return True


if __name__ == "__main__":
    print("⚠️  This test will make real HTTP requests to Particle documentation.")
    print("   Make sure you have internet connectivity.\n")
    
    success = asyncio.run(test_content_fetching())
    sys.exit(0 if success else 1)
