# MCP Doubao Image Generator

[English](README.md) | [中文](README-CN.md)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that enables AI assistants to generate images from text prompts using Doubao Seedream.

## Features

- **Doubao Seedream Integration**: Generate images from text descriptions using Doubao Seedream API
- **Multiple Parameters**: Support for size, style, quality, and quantity options
- **Dedicated Provider**: Specifically designed for Doubao Seedream service
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Easy Integration**: Simple configuration for MCP clients

## Installation

### Using uvx (Recommended)

```bash
uvx mcp-seedream
```

### Using pip

```bash
pip install mcp-seedream
```

### From Source

```bash
git clone https://github.com/aardpro/mcp-seedream.git
cd mcp-seedream
pip install -e .
```

## Configuration

Add the following to your MCP client configuration (e.g., Claude Desktop, Cursor):

### Option 1: Using uvx with environment variables (Required Configuration)

You must configure the API settings using the `environment` field (or `env` depending on your MCP client implementation) in your MCP configuration to pass environment variables to the server. ARK_API_KEY is required for authentication. These will be used as the initial values when the server starts:

**Note:** Some MCP clients may require `env` instead of `environment`. Please check your MCP client documentation to confirm which field name is supported.

```json
{
  "mcpServers": {
    "McpSeedream": {
      "command": "uvx",
      "args": ["mcp-seedream"],
      "environment": {
        "ARK_API_URL": "https://ark.cn-beijing.volces.com/api/v3/images/generations",
        "ARK_DEFAULT_MODEL": "doubao-seedream-4-5-251128",
        "ARK_API_KEY": "your-api-key-here",
        "ARK_OUTPUT_DIR": "./images"
      }
    }
  }
}
```

### Option 2: Using pip-installed command with `environment` (or `env`) field

```json
{
  "mcpServers": {
    "McpSeedream": {
      "command": "mcp-seedream",
      "environment": {
        "ARK_API_URL": "https://ark.cn-beijing.volces.com/api/v3/images/generations",
        "ARK_DEFAULT_MODEL": "doubao-seedream-4-5-251128",
        "ARK_API_KEY": "your-api-key-here",
        "ARK_OUTPUT_DIR": "./images"
      }
    }
  }
}
```

### Option 3: Windows with Unicode Support

For Windows systems, to ensure proper functionality, use the `environment` field (or `env` depending on your MCP client implementation) in your MCP configuration:

```json
{
  "mcpServers": {
    "McpSeedream": {
      "command": "cmd",
      "args": [
        "/c",
        "chcp 65001 >nul && uvx mcp-seedream"
      ],
      "environment": {
        "ARK_API_URL": "https://ark.cn-beijing.volces.com/api/v3/images/generations",
        "ARK_DEFAULT_MODEL": "doubao-seedream-4-5-251128",
        "ARK_API_KEY": "your-api-key-here",
        "ARK_OUTPUT_DIR": "./images"
      }
    }
  }
}
```

### Option 4: Linux/macOS with Python module

Use the `environment` field (or `env` depending on your MCP client implementation) in your MCP configuration:

```json
{
  "mcpServers": {
    "McpSeedream": {
      "command": "python",
      "args": ["-m", "main"],
      "environment": {
        "ARK_API_URL": "https://ark.cn-beijing.volces.com/api/v3/images/generations",
        "ARK_DEFAULT_MODEL": "doubao-seedream-4-5-251128",
        "ARK_API_KEY": "your-api-key-here",
        "ARK_OUTPUT_DIR": "./images"
      }
    }
  }
}
```

## Available Tools

### `generate_image`

Generate an image from text prompt using Doubao Seedream API.

**Parameters:**
- `prompt` (string, required): Text description of the image to generate
- `model` (string, optional): Model to use for generation (overrides default)
- `n` (integer, optional): Number of images to generate (default: 1, max: 10)
- `size` (string, optional): Size of the generated image (default: '1024x1024')
- `style` (string, optional): Style of the generated image (default: 'vivid')
- `quality` (string, optional): Quality of the generated image (default: 'standard')

**Example:**
```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "A cute柴犬 playing in the park",
    "size": "1024x1024",
    "style": "vivid",
    "n": 1
  }
}
```

## Usage Examples

Once configured, you can ask your AI assistant to:

- "Generate an image of a futuristic cityscape at night"
- "Create an illustration of a fantasy castle surrounded by floating mountains"
- "Make a cartoon-style drawing of a robot reading a book"

## Development

### Setup Development Environment

```bash
git clone https://github.com/aardpro/mcp-seedream.git
cd mcp-seedream
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Build Package

build && upload
```bash
pip install build && python -m build && pip install twine && twine upload dist/*
```

```bash
pip install build
python -m build
```

### Publish to PyPI

```bash
pip install twine
twine upload dist/*
```

## Release Steps After Modifications

When making changes to the project, follow these steps to publish an updated version:

1. Increment the version number in `pyproject.toml`
2. Install build dependencies:
   ```bash
   pip install build twine
   ```
3. Build the package:
   ```bash
   python -m build
   ```
4. Test the built package locally (optional but recommended):
   ```bash
   pip install dist/mcp_seedream-*.whl
   ```
5. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

## Project Structure

```
doubao-image-generator/
├── src/
│   └── main/
│       ├── __init__.py
│       ├── __main__.py
│       └── server.py
├── examples/
│   ├── mcp_config_pip.json
│   ├── mcp_config_uvx.json
│   ├── mcp_config_windows.json
│   └── mcp_config_linux.json
├── pyproject.toml
├── README.md
└── LICENSE
```

## Troubleshooting

### Configuration Issues

Make sure you have configured the API settings using environment variables in your MCP configuration. The ARK_API_KEY is required for authentication:

For MCP environment configuration, see the examples in the Configuration section above.

### Image Generation Failures

If image generation fails, check that:
1. Your API key is valid and has sufficient credits
2. The prompt is not too long or contains no prohibited content
3. The requested image size is supported by your chosen API provider

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
