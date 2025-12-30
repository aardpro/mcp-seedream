# MCP Doubao 图像生成器 (MCP Doubao Image Generator)

[English](README.md) | [中文](README-CN.md)

一个 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器，赋予 AI 助手使用豆包 Seedream 从文本提示生成图像的能力。

## ✨ 功能特性

- **豆包 Seedream 集成**：使用豆包 Seedream API 从文本描述生成图像
- **多参数支持**：支持尺寸、样式、质量和数量选项
- **专用提供商**：专为豆包 Seedream 服务设计
- **跨平台**：完美支持 Windows、Linux 和 macOS
- **易于集成**：为 MCP 客户端提供简单配置

## 🚀 安装

### 使用 uvx (推荐)

```bash
uvx mcp-seedream
```

### 使用 pip

```bash
pip install mcp-seedream
```

### 从源码安装

```bash
git clone https://github.com/aardpro/mcp-seedream.git
cd mcp-seedream
pip install -e .
```

## ⚙️ 配置

将以下内容添加到你的 MCP 客户端配置中（例如 Claude Desktop, Cursor）：

### 选项 1: 使用 uvx 和环境变量（必需配置）

你必须使用 MCP 配置中的 `environment` 字段（或根据你的 MCP 客户端实现使用 `env`）来传递环境变量给服务器。这些将在服务器启动时用作初始值：

**注意：** 某些 MCP 客户端可能需要使用 `env` 而不是 `environment`。请检查你的 MCP 客户端文档以确认支持哪个字段名。

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

### 选项 2: 使用 pip 安装的命令和 `environment` (或 `env`) 字段

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

### 选项 3: Windows 系统 (支持中文路径)

对于 Windows 系统，为确保正常功能，使用 MCP 配置中的 `environment` 字段（或根据你的 MCP 客户端实现使用 `env`）来传递环境变量给服务器：

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

### 选项 4: Linux/macOS 使用 Python 模块

使用 MCP 配置中的 `environment` 字段（或根据你的 MCP 客户端实现使用 `env`）来传递环境变量给服务器：

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

## 🛠️ 可用工具

### `generate_image`

使用配置的 API 从文本提示生成图像。

**参数:**
- `prompt` (string, 必填): 描述要生成图像的文本
- `model` (string, 可选): 用于生成的模型 (覆盖默认值)
- `n` (integer, 可选): 生成图像的数量 (默认: 1, 最大: 10)
- `size` (string, 可选): 生成图像的尺寸 (默认: '1024x1024')
- `style` (string, 可选): 生成图像的风格 (默认: 'vivid')
- `quality` (string, 可选): 生成图像的质量 (默认: 'standard')

**示例:**
```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "一只可爱的柴犬在公园里玩耍",
    "size": "1024x1024",
    "style": "vivid",
    "n": 1
  }
}
```

## 💡 使用示例

配置完成后，你可以直接让 AI 助手：

- "生成一张未来城市夜景的图像"
- "创建一幅奇幻城堡被浮空山脉环绕的插图"
- "制作一张机器人读书的卡通风格绘画"

## 💻 开发

### 设置开发环境

```bash
git clone https://github.com/aardpro/mcp-seedream.git
cd mcp-seedream
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 构建包

build && upload
```bash
pip install build && python -m build && pip install twine && twine upload dist/*
```

```bash
pip install build
python -m build
```

### 发布到 PyPI

```bash
pip install twine
twine upload dist/*
```

## 修改后的发布步骤

当对项目进行修改后，按照以下步骤发布更新版本：

1. 在 `pyproject.toml` 中增加版本号
2. 安装构建依赖：
   ```bash
   pip install build twine
   ```
3. 构建包：
   ```bash
   python -m build
   ```
4. 本地测试构建的包（可选但推荐）：
   ```bash
   pip install dist/mcp_seedream-*.whl
   ```
5. 上传到 PyPI：
   ```bash
   twine upload dist/*
   ```

## 📂 项目结构

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
├── README-CN.md
└── LICENSE
```

## ❓ 常见问题

### 配置问题

请确保首先使用环境变量配置 API 设置。ARK_API_KEY 是必需的：

对于 MCP 环境变量配置，参见上面配置部分的示例。

### 图像生成失败

如果图像生成失败，请检查：
1. 您的 API 密钥是否有效且有足够的积分
2. 提示词是否过长或包含禁止内容
3. 请求的图像尺寸是否受您选择的 API 提供商支持

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Pull Request 来改进这个项目！
