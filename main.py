#!/usr/bin/env python3
"""Entry point for the Particle MCP Server."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server import main

def setup_logging():
    """Setup logging configuration."""
    # Create log file in the project directory
    log_file = Path(__file__).parent / 'particle-mcp-server.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_file)
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Starting Particle MCP Server...")
        logger.info("📚 Serving 9 Particle documentation pages via MCP protocol")
        logger.info("🔧 Server ready to accept MCP connections via stdio")
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("⏹️  Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)
    finally:
        logger.info("🛑 Particle MCP Server stopped")
