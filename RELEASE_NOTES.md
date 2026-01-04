# MCP Seedream 发布说明

## 版本 1.1.3

### 优化内容

1. **API错误处理优化**
   - 增强了API请求的错误处理，添加了超时设置
   - 改进了JSON响应解析错误处理
   - 增强了图像下载的错误处理

2. **图像文件保存优化**
   - 改进了目标文件名处理逻辑，支持从URL中提取正确的文件扩展名
   - 添加了文件名安全性验证，防止路径遍历攻击
   - 增加了文件保存后的验证，确保文件非空

3. **MinIO上传功能增强**
   - 添加了`process_image_parameter`函数，自动处理本地图像文件到MinIO URL的转换
   - 支持本地图像文件路径，自动上传到MinIO并返回URL
   - 支持单个图像和多个图像的本地文件上传

4. **工具描述优化**
   - 更新了工具描述，明确支持三种调用方式：文本到图像、图像到图像、多图像融合
   - 明确说明支持本地图像文件路径和公共图像URL

5. **日志记录增强**
   - 添加了更详细的日志记录，便于调试和监控
   - 记录参数验证、API配置、图像保存等关键步骤

6. **文档更新**
   - 更新README.md，添加本地图像文件使用示例
   - 优化了功能描述，使其更清晰明确
   - 增强了工具描述，明确说明何时调用此工具

7. **Agent使用指导**
   - 详细说明了用户请求与工具调用的映射关系
   - 提供了多种使用场景示例
   - 创建了AGENT_USAGE_EXAMPLES.md指导文件

8. **配置文件位置调整**
   - 将config.json文件移动到src/main目录下，与server.py在同一位置
   - 更新了打包配置，确保config.json文件包含在发布的包中
   - 保持了原有的配置加载逻辑，缺少配置文件时会报错

### 使用方式

#### 1. 文本到图像（仅提示词）
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

#### 2. 图像到图像（提示词+单个图像）
- 使用URL：
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

- 使用本地文件：
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

#### 3. 多图像融合（提示词+多个图像）
- 使用URL：
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

- 使用本地文件：
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

### 注意事项

- 本地图像文件将自动上传到MinIO服务器并转换为URL
- 必须提供`output_dir`参数以指定生成图像的保存位置
- 支持的图像格式：JPG, JPEG, PNG, WEBP, GIF
- 生成的图像将保存在指定输出目录中