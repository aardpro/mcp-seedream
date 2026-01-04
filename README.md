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
uvx mcp-seedream@latest
```

### 使用 pip

```bash
pip install mcp-seedream@latest
```

### 从源码安装

```bash
git clone https://github.com/aardpro/mcp-seedream.git
cd mcp-seedream
pip install -e .
```

## ⚙️ 配置

### 配置

#### 环境变量配置

在使用 MCP 服务器之前，您需要设置 `ARK_API_KEY` 环境变量。以下是不同操作系统的设置方法：

#### Windows (命令提示符)
```cmd
set ARK_API_KEY=your-api-key-here
```

#### Windows (PowerShell)
```powershell
$env:ARK_API_KEY="your-api-key-here"
```

#### Linux/macOS (Bash/Zsh)
```bash
export ARK_API_KEY="your-api-key-here"
```

#### 永久设置 (Linux/macOS)
将以下行添加到您的 `~/.bashrc` 或 `~/.zshrc` 文件中：
```bash
export ARK_API_KEY="your-api-key-here"
```

#### 永久设置 (Windows)
在 Windows 系统中，您可以通过以下方式永久设置环境变量：
1. 打开“系统属性”对话框 (右键点击“此电脑” -> “属性”)
2. 点击“高级系统设置”
3. 点击“环境变量”
4. 在“用户变量”部分点击“新建”
5. 变量名：`ARK_API_KEY`，变量值：您的 API 密钥

#### 配置文件

服务器会从内部配置文件加载默认设置。如果需要自定义配置，请按照MCP客户端配置指南进行环境变量设置。

### MCP 客户端配置

将以下内容添加到你的 MCP 客户端配置中（例如 Claude Desktop, Cursor）：

#### 选项 1: 使用 uvx 

```json
{
  "mcpServers": {
    "McpSeedream": {
      "command": "uvx",
      "args": ["mcp-seedream"]
    }
  }
}
```

#### 选项 2: 使用 pip

```json
{
  "mcpServers": {
    "McpSeedream": {
      "command": "mcp-seedream"
    }
  }
}
```

#### 选项 3: Windows 系统 

```json
{
  "mcpServers": {
    "McpSeedream": {
      "command": "cmd",
      "args": [
        "/c",
        "chcp 65001 >nul && uvx mcp-seedream"
      ]
    }
  }
}
```

#### 选项 4: Linux/macOS：

```json
{
  "mcpServers": {
    "McpSeedream": {
      "command": "python",
      "args": ["-m", "main"]
    }
  }
}
```

## 🛠️ 可用工具

### `generate_image`

使用配置的 API 从文本提示生成图像。当用户明确或隐含地要求创建、生成、制作、绘制、设计或可视化任何类型的图像、图片、插图、图表、图形、艺术作品、照片、肖像、风景、场景、概念图、设计图、卡通、动漫、海报、封面、图标、徽标等视觉内容时，必须调用此工具。支持三种调用方式：1) 文本到图像（仅提示词） 2) 图像到图像（提示词+单个图像） 3) 多图像融合（提示词+多个图像）。支持本地图像文件路径和公共图像URL（本地文件将自动上传到MinIO）。

**参数:**
- `prompt` (string, 必填): 描述要生成图像的文本
- `model` (string, 可选): 用于生成的模型 (覆盖默认值)
- `n` (integer, 可选): 生成图像的数量 (默认: 1, 最大: 10)
- `size` (string, 可选): 生成图像的尺寸 (默认: '2K')。对于豆包 API，使用 '2K', '4K' 或具体尺寸如 '1024x1024'
- `style` (string, 可选): 生成图像的风格 (默认: 'vivid')
- `quality` (string, 可选): 生成图像的质量 (默认: 'standard')
- `image` (string 或 string 数组, 可选): 用作图像生成参考的单个图像 URL 或图像 URL 数组
- `sequential_image_generation` (string, 可选): 启用 ('auto') 或禁用 ('disabled') 序列图像生成以创建相关图像 (默认: 'disabled')
- `sequential_image_generation_options` (object, 可选): 序列图像生成选项，包括 max_images
- `attempts` (integer, 可选): 生成图像的尝试次数。如果指定多次尝试，将使用相同的提示词和参考图像重复生成，直到达到指定次数 (默认: 1, 最大: 10)
- `output_dir` (string, 必填): 保存生成图像的目录。此参数必须由代理在每次函数调用时提供（不再全局配置）。
- `target_filename` (string, 可选): 生成图像的目标文件名。如果未提供，将使用时间戳和随机数字生成文件名

**示例:**

文生图:
```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "一只可爱的柴犬在公园里玩耍",
    "size": "2K",
    "style": "vivid",
    "n": 1,
    "output_dir": "./images"
  }
}
```

图生图 (使用图像 URL):
```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "将背景改为海滩场景",
    "image": "https://example.com/path/to/image.jpg",
    "size": "2K",
    "output_dir": "./images"
  }
}
```

图生图 (使用本地图像文件):
```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "将背景改为海滩场景",
    "image": "./path/to/local/image.jpg",
    "size": "2K",
    "output_dir": "./images"
  }
}
```

多图融合:
```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "将这些元素合成一个场景",
    "image": ["http://175.178.248.52:9000/ai-images/1704218400_12345.jpg", "http://175.178.248.52:9000/ai-images/1704218400_67890.png"],
    "size": "2K",
    "output_dir": "./images"
  }
}
```

多图融合 (使用本地图像文件):
```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "将这些元素合成一个场景",
    "image": ["./path/to/local/image1.jpg", "./path/to/local/image2.png"],
    "size": "2K",
    "output_dir": "./images"
  }
}
```

序列图像生成:
```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "生成 4 张显示同一角色在不同季节的图像",
    "size": "2K",
    "sequential_image_generation": "auto",
    "sequential_image_generation_options": {
      "max_images": 4
    },
    "output_dir": "./images"
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
rm -rf dist && pip install build && python -m build && pip install twine && twine upload dist/*
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
├── pyproject.toml
├── README.md
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
