"""
"MCP Server implementation for Doubao text-to-image generation."
"""

import asyncio
import os
import sys
import logging
import tempfile
import requests
import json
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_encoding():
    """Configure UTF-8 encoding for cross-platform compatibility."""
    if sys.platform == "win32":
        try:
            # Reconfigure all standard streams for UTF-8 on Windows
            sys.stdin.reconfigure(encoding='utf-8', errors='replace')
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        except Exception as e:
            logger.warning(f"Failed to reconfigure stdio streams: {e}")


# Initialize server
server = Server("McpDoubaoImageGenerator")

# Global configuration that can be set via MCP
config = {
    "api_url": os.getenv("ARK_API_URL", "https://ark.cn-beijing.volces.com/api/v3/images/generations"),
    "default_model": os.getenv("ARK_DEFAULT_MODEL", "doubao-seedream-4-5-251128"),
    "api_key": os.getenv("ARK_API_KEY"),  # No default for API key for security reasons
    "output_dir": os.getenv("ARK_OUTPUT_DIR", "./images")
}


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available text-to-image generation tools and configuration tools."""
    return [
        types.Tool(
            name="set_config",
            description="Configure API settings for image generation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_url": {
                        "type": "string",
                        "description": "API endpoint URL for the image generation service."
                    },
                    "default_model": {
                        "type": "string",
                        "description": "Default model to use for image generation."
                    },
                    "api_key": {
                        "type": "string",
                        "description": "API key for authentication."
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to save generated images (default: './images')."
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="generate_image",
            description="Generate an image from text prompt using configured API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description of the image to generate."
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use for generation (overrides default)."
                    },
                    "n": {
                        "type": "integer",
                        "description": "Number of images to generate (default: 1, max: 10).",
                        "default": 1
                    },
                    "size": {
                        "type": "string",
                        "description": "Size of the generated image (default: '1024x1024').",
                        "enum": ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
                    },
                    "style": {
                        "type": "string",
                        "description": "Style of the generated image (default: 'vivid').",
                        "enum": ["vivid", "natural"]
                    },
                    "quality": {
                        "type": "string",
                        "description": "Quality of the generated image (default: 'standard').",
                        "enum": ["standard", "hd"]
                    }
                },
                "required": ["prompt"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for configuration and image generation."""
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    try:
        if not arguments:
            raise ValueError("Missing arguments")
        
        if name == "set_config":
            # Update configuration with provided values
            if "api_url" in arguments:
                config["api_url"] = arguments["api_url"]
            if "default_model" in arguments:
                config["default_model"] = arguments["default_model"]
            if "api_key" in arguments:
                config["api_key"] = arguments["api_key"]
            if "output_dir" in arguments:
                config["output_dir"] = arguments["output_dir"]
                
            # Create output directory if it doesn't exist
            output_path = Path(config["output_dir"])
            output_path.mkdir(parents=True, exist_ok=True)
            
            result_text = f"Configuration updated successfully.\nCurrent config: {json.dumps({k: v for k, v in config.items() if k != 'api_key'}, indent=2)}"
            return [types.TextContent(type="text", text=result_text)]
        
        elif name == "generate_image":
            # Extract parameters
            prompt = arguments.get("prompt")
            if not prompt:
                raise ValueError("Missing prompt argument")
            
            n = arguments.get("n", 1)
            size = arguments.get("size", "1024x1024")
            style = arguments.get("style", "vivid")
            quality = arguments.get("quality", "standard")
            model = arguments.get("model", config["default_model"])
            
            # Validate parameters
            if n < 1 or n > 10:
                raise ValueError("n must be between 1 and 10")
            
            # Get API configuration
            api_url = config["api_url"]
            api_key = config["api_key"]
            
            if not api_url:
                raise ValueError("API URL not configured. Use set_config tool first.")
            # Ensure the API URL is the supported API since that's the only supported API
            if "ark.cn-beijing.volces.com" not in api_url and "doubao" not in api_url.lower() and "api.openai.com" not in api_url:
                raise ValueError("Only Doubao API or OpenAI API is supported in this version")
            if not api_key:
                raise ValueError("API key not configured. Use set_config tool first.")
            
            # Prepare the request for a generic image generation API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request payload based on the API provider
            if "ark.cn-beijing.volces.com" in api_url or "doubao" in api_url.lower():
                # For Doubao API - using the exact format from the official example
                # Convert size format for Doubao API (e.g., 1024x1024 -> 2K)
                doubao_size = size
                if size in ["256x256", "512x512", "1024x1024"]:
                    if size == "1024x1024":
                        doubao_size = "2K"
                    elif size == "512x512":
                        doubao_size = "512x512"
                    elif size == "256x256":
                        doubao_size = "256x256"
                
                payload = {
                    "model": model or "doubao-seedream-4-5-251128",
                    "prompt": prompt,
                    "sequential_image_generation": "disabled",
                    "response_format": "url",
                    "size": doubao_size,
                    "stream": False,
                    "watermark": False
                }
                
                # Add optional parameters if provided
                if style and style != "vivid":
                    payload["style"] = style
                if quality and quality != "standard":
                    payload["quality"] = quality
                
                # Use the exact endpoint format from the official example
                api_endpoint = api_url  # Use the full URL as provided in the example
            elif "api.openai.com" in api_url:
                # For OpenAI API
                payload = {
                    "model": model or config["default_model"],
                    "prompt": prompt,
                    "n": n,
                    "size": size,
                }
                
                # Add optional parameters if provided
                if style and style != "vivid":
                    payload["style"] = style
                if quality and quality != "standard":
                    payload["quality"] = quality
                
                # For OpenAI, we need to use the images/generations endpoint
                api_endpoint = f"{api_url.rstrip('/')}/images/generations"
            else:
                raise ValueError("Only Doubao API or OpenAI API is supported in this version")
            
            # Make the API request
            response = requests.post(api_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            # Debug logging to help troubleshoot API issues
            logger.debug(f"API request sent to {api_endpoint} with payload: {json.dumps(payload, ensure_ascii=False)}")
            
            # Process the response
            response_data = response.json()
            results = []
            
            # Create output directory if it doesn't exist
            output_path = Path(config["output_dir"])
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Check if the API returns image data directly or as URLs
            if "ark.cn-beijing.volces.com" in api_url or "doubao" in api_url.lower():
                # Doubao API response handling
                if "data" in response_data:
                    for i, item in enumerate(response_data["data"]):
                        if "url" in item:
                            # Handle URL-based response
                            image_url = item["url"]
                            image_response = requests.get(image_url)
                            image_response.raise_for_status()
                            
                            # Save the image to the configured output directory
                            image_filename = f"generated_image_{i+1}_{prompt[:20].replace(' ', '_')}.png"
                            image_path = output_path / image_filename
                            with open(image_path, "wb") as f:
                                f.write(image_response.content)
                            
                            # Add image content to results - convert bytes to base64 string for ImageContent
                            import base64
                            image_data_b64 = base64.b64encode(image_response.content).decode('utf-8')
                            results.append(types.ImageContent(
                                type="image",
                                data=image_data_b64,  # ImageContent expects base64 encoded string, not raw bytes
                                mimeType="image/png"
                            ))
                            
                            # Also include text with the result
                            results.append(types.TextContent(
                                type="text",
                                text=f"Image {i+1} generated successfully and saved to {image_path}.\nPrompt: {prompt}"
                            ))
                        elif "b64_json" in item:
                            # Handle base64 encoded image data
                            import base64
                            image_data = base64.b64decode(item["b64_json"])
                            
                            # Save the image to the configured output directory
                            image_filename = f"generated_image_{i+1}_{prompt[:20].replace(' ', '_')}.png"
                            image_path = output_path / image_filename
                            with open(image_path, "wb") as f:
                                f.write(image_data)
                            
                            # Add image content to results
                            image_data_b64 = base64.b64encode(image_data).decode('utf-8')
                            results.append(types.ImageContent(
                                type="image",
                                data=image_data_b64,  # ImageContent expects base64 encoded string, not raw bytes
                                mimeType="image/png"
                            ))
                            
                            # Also include text with the result
                            results.append(types.TextContent(
                                type="text",
                                text=f"Image {i+1} generated successfully and saved to {image_path}.\nPrompt: {prompt}"
                            ))
            elif "api.openai.com" in api_url:
                # Standard OpenAI-style API response
                for i, image_data in enumerate(response_data.get("data", [])):
                    image_url = image_data.get("url")
                    if not image_url:
                        continue
                    
                    # Download the image
                    image_response = requests.get(image_url)
                    image_response.raise_for_status()
                    
                    # Save the image to the configured output directory
                    image_filename = f"generated_image_{i+1}_{prompt[:20].replace(' ', '_')}.png"
                    image_path = output_path / image_filename
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    
                    # Add image content to results - convert bytes to base64 string for ImageContent
                    import base64
                    image_data_b64 = base64.b64encode(image_response.content).decode('utf-8')
                    results.append(types.ImageContent(
                        type="image",
                        data=image_data_b64,  # ImageContent expects base64 encoded string, not raw bytes
                        mimeType="image/png"
                    ))
                    
                    # Also include text with the result
                    results.append(types.TextContent(
                        type="text",
                        text=f"Image {i+1} generated successfully and saved to {image_path}.\nPrompt: {prompt}"
                    ))
            
            logger.info(f"Tool {name} execution successful. Generated {len(results)//2} images.")
            return results
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def run_server():
    """Run the MCP server."""
    logger.info("Starting Universal Image Generator MCP Server...")
    
    # Setup encoding for cross-platform compatibility
    setup_encoding()
    
    # Run the server using stdin/stdout
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="UniversalImageGenerator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
