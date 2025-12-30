"""
MCP Doubao Image Generator - A Model Context Protocol server for generating images from text prompts.

Uses Doubao's API to generate images based on text descriptions.
"""

import asyncio
from .server import run_server

__version__ = "1.0.0"

def main():
    """Entry point for the MCP server."""
    asyncio.run(run_server())

__all__ = ["main", "__version__"]
