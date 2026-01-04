"""
MCP 服务器实现，用于文本到图像生成。

此服务器使 AI 代理能够使用 
Doubao Seedream API 或兼容的图像生成服务从文本提示生成图像。
当用户请求图像生成、视觉内容创建或要求从描述创建图片时，AI 代理应调用此服务器。

重要提示：生成的图像默认保存到用户主目录下的 'images' 文件夹中。
用户可能需要将这些文件移动到项目目录中。
"""

import os
import sys
import logging
import requests
import json
import time
import random
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# MinIO imports
from minio import Minio
from minio.error import S3Error

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_encoding():
    """配置 UTF-8 编码以实现跨平台兼容性。"""
    if sys.platform == "win32":
        try:
            # Reconfigure all standard streams for UTF-8 on Windows
            sys.stdin.reconfigure(encoding='utf-8', errors='replace')
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        except Exception as e:
            logger.warning(f"重新配置标准流失败: {e}")





# Initialize server
server = Server("McpSeedream")

def load_config() -> Dict[str, Any]:
    """从 config.json 文件加载配置。"""
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件未找到: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load configuration from config.json
config_from_file = load_config()

# 从环境变量获取 API 密钥，如果未提供则失败
ark_api_key = os.getenv("ARK_API_KEY")
if not ark_api_key:
    raise ValueError("ARK_API_KEY 环境变量是必需的但未设置")

# Global configuration with values from config.json and API key from environment
config = {
    "api_url": config_from_file.get("api_url", "https://ark.cn-beijing.volces.com/api/v3/images/generations"),  # Default to hardcoded value if not in config
    "default_model": config_from_file.get("default_model", "doubao-seedream-4-5-251128"),  # Default to hardcoded value if not in config
    "api_key": ark_api_key,
    "minio_host": config_from_file.get("minio_host", "175.178.248.52"),
    "minio_port": config_from_file.get("minio_port", "9000"),
    "minio_user": config_from_file.get("minio_user", "admin"),
    "minio_password": config_from_file.get("minio_password", "mmmpass888"),
    "minio_bucket": config_from_file.get("minio_bucket", "ai-images"),
    "minio_use_ssl": config_from_file.get("minio_use_ssl", False)  # Default to False if not specified in config
}


def create_minio_client():
    """使用配置文件中的配置创建并返回 MinIO 客户端。"""
    minio_host = config["minio_host"]
    minio_port = config["minio_port"]
    minio_user = config["minio_user"]
    minio_password = config["minio_password"]
    use_ssl = config["minio_use_ssl"]
    
    # Construct the MinIO endpoint
    endpoint = f"{minio_host}:{minio_port}"
    
    # Create MinIO client
    client = Minio(
        endpoint=endpoint,
        access_key=minio_user,
        secret_key=minio_password,
        secure=use_ssl
    )
    
    return client


def upload_image_to_minio(image_path: str) -> str:
    """将图像文件上传到 MinIO 并返回公共 URL。
    
    参数:
        image_path: 图像文件的路径
        
    返回:
        上传图像的公共 URL
        
    异常:
        FileNotFoundError: 如果图像文件不存在
        ValueError: 如果文件不是有效的图像
        S3Error: 如果上传到 MinIO 时出错
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")
    
    # Determine image type from extension
    suffix = path.suffix.lower()
    if suffix not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        raise ValueError(f"不支持的图像格式: {suffix}. 支持的格式: .jpg, .jpeg, .png, .webp, .gif")
    
    # Create MinIO client
    minio_client = create_minio_client()
    bucket_name = config["minio_bucket"]
    
    # Generate a unique filename using timestamp and random number
    timestamp = int(time.time())
    random_num = random.randint(10000, 99999)
    unique_filename = f"{timestamp}_{random_num}{suffix}"
    
    # Ensure the bucket exists
    try:
        if not minio_client.bucket_exists(bucket_name):
            logger.info(f"创建存储桶 {bucket_name}")
            minio_client.make_bucket(bucket_name)
    except S3Error as e:
        # If bucket already exists or there's an error creating it, continue
        logger.warning(f"无法创建存储桶 {bucket_name}, 假设它已存在: {e}")
    
    # Upload the file
    try:
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=unique_filename,
            file_path=str(path),
            content_type=f"image/{suffix[1:] if suffix[1:] != 'jpeg' else 'jpg'}"
        )
        
        # Construct the public URL
        # For MinIO with public access, the URL format is: http://host:port/bucket_name/object_name
        protocol = "https" if config.get("minio_use_ssl", False) else "http"
        minio_url = f"{protocol}://{config['minio_host']}:{config['minio_port']}/{bucket_name}/{unique_filename}"
        
        logger.info(f"图像上传成功。URL: {minio_url}")
        return minio_url
    
    except S3Error as e:
        logger.error(f"上传到 MinIO 时出错: {e}")
        raise e


def delete_image_from_minio(image_url: str):
    """从 MinIO 删除图像文件。"""
    try:
        # Parse bucket and object name from URL
        # URL format: http(s)://host:port/bucket/object
        parsed = urlparse(image_url)
        path_parts = parsed.path.strip("/").split("/")
        
        if len(path_parts) < 2:
            logger.warning(f"无法从 URL 解析 Bucket 和对象名: {image_url}")
            return

        bucket_name = path_parts[0]
        object_name = "/".join(path_parts[1:])
        
        minio_client = create_minio_client()
        minio_client.remove_object(bucket_name, object_name)
        logger.info(f"已从 MinIO 删除临时图像: {object_name}")
        
    except Exception as e:
        logger.error(f"删除 MinIO 图像失败: {e}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出可用的文本到图像生成工具。"""
    return [
        types.Tool(
            name="generate_image",
            description="使用配置的 API 从文本提示生成图像。当用户明确或隐含地要求创建、生成、制作、绘制、设计或可视化任何类型的图像、图片、插图、图表、图形、艺术作品、照片、肖像、风景、场景、概念图、设计图、卡通、动漫、海报、封面、图标、徽标等视觉内容时，必须调用此工具。支持三种调用方式：1) 文本到图像（仅提示词） 2) 图像到图像（提示词+单个图像） 3) 多图像融合（提示词+多个图像）。支持本地图像文件路径和公共图像URL（本地文件将自动上传到MinIO）。重要提示：您必须指定输出目录，并可选择指定目标文件名。如果未提供目标文件名，则会使用时间戳和随机数生成文件名。",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "要生成的图像的文本描述。"
                    },
                    "model": {
                        "type": "string",
                        "description": "用于生成的模型（覆盖默认值）。"
                    },
                    "n": {
                        "type": "integer",
                        "description": "要生成的图像数量（默认值：1，最大值：10）。",
                        "default": 1
                    },
                    "size": {
                        "type": "string",
                        "description": "生成图像的尺寸（默认值：'2K'）。对于 Doubao API，使用 '2K'、'4K' 或特定尺寸如 '1024x1024'。",
                        "enum": ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792", "1K", "2K", "4K"]
                    },
                    "style": {
                        "type": "string",
                        "description": "生成图像的样式（默认值：'vivid'）。",
                        "enum": ["vivid", "natural"]
                    },
                    "quality": {
                        "type": "string",
                        "description": "生成图像的质量（默认值：'standard'）。",
                        "enum": ["standard", "hd"]
                    },
                    "image": {
                        "oneOf": [
                            {"type": "string", "description": "用作图像生成参考的公共 URL"}, 
                            {"type": "array", "items": {"type": "string"}, "description": "用作图像生成参考的公共 URL 数组"}
                        ],
                        "description": "用作图像生成参考的单个图像 URL 或图像 URL 数组。可选参数。"
                    },
                    "sequential_image_generation": {
                        "type": "string",
                        "enum": ["auto", "disabled"],
                        "description": "启用（'auto'）或禁用（'disabled'）顺序图像生成以创建相关图像。默认值：'disabled'。"
                    },
                    "sequential_image_generation_options": {
                        "type": "object",
                        "properties": {
                            "max_images": {
                                "type": "integer",
                                "description": "当 sequential_image_generation 为 'auto' 时顺序生成的最大图像数。"
                            }
                        },
                        "description": "顺序图像生成选项。"
                    },
                    "attempts": {
                        "type": "integer",
                        "description": "生成图像的尝试次数。如果指定多次尝试，将使用相同的提示词和参考图像重复生成，直到达到指定次数。默认值：1。",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 10
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "保存生成图像的目录。此参数是必需的。"
                    },
                    "target_filename": {
                        "type": "string",
                        "description": "生成图像的可选目标文件名。如果未提供，则会使用时间戳和随机数生成文件名。"
                    }
                },
                "required": ["prompt", "output_dir"]
            }
        ),
        
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.EmbeddedResource]:
    """处理图像生成的工具调用。"""
    logger.info(f"工具被调用: {name} 参数: {arguments}")
    
    try:
        if not arguments:
            raise ValueError("缺少参数")
        
        if name == "generate_image":
            # Extract parameters
            prompt = arguments.get("prompt")
            if not prompt:
                raise ValueError("缺少 prompt 参数")
            
            n = arguments.get("n", 1)
            size = arguments.get("size", "2K")  # Default to 2K for Doubao API
            style = arguments.get("style", "vivid")
            quality = arguments.get("quality", "standard")
            model = arguments.get("model", config["default_model"])
            output_dir = arguments.get("output_dir")
            target_filename = arguments.get("target_filename")
            image = arguments.get("image")
            sequential_image_generation = arguments.get("sequential_image_generation", "disabled")
            sequential_image_generation_options = arguments.get("sequential_image_generation_options")
            attempts = arguments.get("attempts", 1)
            
            # Log the parameters for debugging
            logger.info(f"图像生成参数: n={n}, size={size}, style={style}, quality={quality}, model={model}, output_dir={output_dir}, target_filename={target_filename}, attempts={attempts}")
            if image:
                logger.info(f"图像参数: {type(image).__name__} with {len(image) if isinstance(image, list) else 'single'} item(s)")
            
            # Validate parameters
            if n < 1 or n > 10:
                raise ValueError("n 必须在 1 到 10 之间")
            
            if attempts < 1 or attempts > 10:
                raise ValueError("attempts 必须在 1 到 10 之间")
            
            if not output_dir:
                raise ValueError("缺少 output_dir 参数")
            
            # Validate target_filename if provided
            if target_filename:
                # Remove potentially dangerous characters and paths
                import re
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', target_filename)  # Replace invalid filename characters with underscore
                if '..' in target_filename or safe_filename != target_filename:
                    logger.warning(f"目标文件名包含无效字符或路径遍历尝试: {target_filename}, 已清理为: {safe_filename}")
                    target_filename = safe_filename
                # Ensure the filename has a valid extension
                if not any(target_filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                    logger.warning(f"目标文件名缺少有效扩展名: {target_filename}, 添加默认扩展名 .png")
                    target_filename += '.png'
            
            logger.info(f"参数验证完成: 生成 {n} 张图像，大小 {size}，保存到 {output_dir}")
            
            # Get API configuration
            api_url = config["api_url"]
            api_key = config["api_key"]
            
            logger.info(f"使用 API URL: {api_url}")
            
            if not api_url:
                raise ValueError("未配置 API URL。请确保在 config.json 文件中配置了 api_url，或在环境变量中设置了 ARK_API_URL。")
            # Ensure the API URL is the supported API since that's the only supported API
            if "ark.cn-beijing.volces.com" not in api_url and "doubao" not in api_url.lower():
                raise ValueError("此版本仅支持 Doubao API")
            if not api_key:
                raise ValueError("未配置 API 密钥。必需: ARK_API_KEY 环境变量必须在服务器启动时设置。")
            
            logger.info(f"API 配置验证完成，模型: {model}")
            
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
                # Only convert standard dimensions to 2K if they're not already in the right format
                if size == "1024x1024":
                    doubao_size = "2K"
                elif size == "256x256" or size == "512x512":
                    # Keep these as they are since they're supported as pixel dimensions
                    doubao_size = size
                # For '1K', '2K', '4K' formats, use them as is
                # For other dimensions like '1792x1024', '1024x1792', they should be sent as-is to the API
                
                payload = {
                    "model": model or "doubao-seedream-4-5-251128",
                    "prompt": prompt,
                    "sequential_image_generation": sequential_image_generation,
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
                if image:
                    # Image parameter will be processed inside the attempt loop
                    pass

                if sequential_image_generation == "auto" and sequential_image_generation_options:
                    payload["sequential_image_generation_options"] = sequential_image_generation_options
                
                # Use the exact endpoint format from the official example
                api_endpoint = api_url  # Use the full URL as provided in the example
            else:
                raise ValueError("Only Doubao API is supported in this version")
            
            results = []
            
            # Create output directory if it doesn't exist
            output_path = Path(output_dir)
            logger.info(f"尝试在目录中创建/保存图像: {output_path}")
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"创建输出目录失败 {output_path}: {e}")
                return [types.TextContent(type="text", text=f"错误: 创建输出目录失败 {output_path}: {str(e)}")]
            
            # Process attempts
            for attempt in range(attempts):
                logger.info(f"开始第 {attempt + 1} 次尝试")
                
                uploaded_urls = []
                current_payload = payload.copy()
                
                try:
                    # Handle image uploading for this attempt
                    if image:
                        if isinstance(image, str):
                            if Path(image).exists():
                                url = upload_image_to_minio(image)
                                uploaded_urls.append(url)
                                current_payload["image"] = url
                            else:
                                current_payload["image"] = image
                        elif isinstance(image, list):
                            processed_images = []
                            for img in image:
                                if isinstance(img, str) and Path(img).exists():
                                    url = upload_image_to_minio(img)
                                    uploaded_urls.append(url)
                                    processed_images.append(url)
                                else:
                                    processed_images.append(img)
                            current_payload["image"] = processed_images
                    
                    # Make the API request
                    try:
                        response = requests.post(api_endpoint, headers=headers, json=current_payload, timeout=60)
                        response.raise_for_status()
                    except requests.exceptions.HTTPError as e:
                        logger.error(f"API 请求失败，状态码: {response.status_code}, 响应: {response.text}")
                        if attempt == attempts - 1:  # Last attempt
                            return [types.TextContent(type="text", text=f"错误: API 请求失败，状态码 {response.status_code}: {response.text}")]
                        else:
                            logger.info(f"第 {attempt + 1} 次尝试失败，继续下一次尝试")
                            continue
                    except requests.exceptions.RequestException as e:
                        logger.error(f"API 请求异常: {e}")
                        if attempt == attempts - 1:  # Last attempt
                            return [types.TextContent(type="text", text=f"错误: API 请求异常: {str(e)}")]
                        else:
                            logger.info(f"第 {attempt + 1} 次尝试失败，继续下一次尝试")
                            continue
                    
                    # Debug logging to help troubleshoot API issues
                    logger.debug(f"API 请求发送到 {api_endpoint} 载荷: {json.dumps(current_payload, ensure_ascii=False)}")
                    
                    # Process the response
                    try:
                        response_data = response.json()
                    except json.JSONDecodeError as e:
                        logger.error(f"API 响应 JSON 解析失败: {e}")
                        if attempt == attempts - 1:  # Last attempt
                            return [types.TextContent(type="text", text=f"错误: API 响应格式错误，无法解析 JSON: {str(e)}")]
                        else:
                            logger.info(f"第 {attempt + 1} 次尝试失败，继续下一次尝试")
                            continue
                    
                    # Check if the API returns image data directly or as URLs
                    if "ark.cn-beijing.volces.com" in api_url or "doubao" in api_url.lower():
                        # Doubao API response handling
                        if "data" in response_data:
                            for i, item in enumerate(response_data["data"]):
                                if "url" in item:
                                    # Handle URL-based response
                                    image_url = item["url"]
                                    try:
                                        image_response = requests.get(image_url, timeout=60)
                                        image_response.raise_for_status()
                                    except requests.exceptions.HTTPError as e:
                                        logger.error(f"下载图像失败，状态码: {image_response.status_code}, URL: {image_url}")
                                        if attempt == attempts - 1:  # Last attempt
                                            return [types.TextContent(type="text", text=f"错误: 下载图像失败，状态码 {image_response.status_code}")]
                                        else:
                                            logger.info(f"第 {attempt + 1} 次尝试失败，继续下一次尝试")
                                            continue
                                    except requests.exceptions.RequestException as e:
                                        logger.error(f"下载图像异常: {e}, URL: {image_url}")
                                        if attempt == attempts - 1:  # Last attempt
                                            return [types.TextContent(type="text", text=f"错误: 下载图像异常: {str(e)}")]
                                        else:
                                            logger.info(f"第 {attempt + 1} 次尝试失败，继续下一次尝试")
                                            continue
                                    
                                    # Save the image to the configured output directory
                                    # Use target_filename if provided, otherwise generate using timestamp and random number
                                    if target_filename:
                                        image_filename = target_filename
                                        # If there are multiple images, add a suffix to distinguish them
                                        if n > 1 or attempts > 1:
                                            name_part, ext_part = os.path.splitext(target_filename)
                                            # Include both attempt and image number in the filename if both are > 1
                                            if n > 1 and attempts > 1:
                                                image_filename = f"{name_part}_attempt_{attempt+1}_img_{i+1}{ext_part}"
                                            elif attempts > 1:
                                                image_filename = f"{name_part}_attempt_{attempt+1}{ext_part}"
                                            else:
                                                image_filename = f"{name_part}_{i+1}{ext_part}"
                                    else:
                                        timestamp = int(time.time())
                                        random_num = random.randint(1000, 9999)
                                        # Extract extension from the URL if possible, otherwise default to png
                                        image_url_lower = image_url.lower()
                                        if image_url_lower.endswith('.jpg') or image_url_lower.endswith('.jpeg'):
                                            # Include attempt number in filename if multiple attempts
                                            if attempts > 1:
                                                image_filename = f"generated_image_attempt_{attempt+1}_{i+1}_{timestamp}_{random_num}.jpg"
                                            else:
                                                image_filename = f"generated_image_{i+1}_{timestamp}_{random_num}.jpg"
                                        elif image_url_lower.endswith('.png'):
                                            # Include attempt number in filename if multiple attempts
                                            if attempts > 1:
                                                image_filename = f"generated_image_attempt_{attempt+1}_{i+1}_{timestamp}_{random_num}.png"
                                            else:
                                                image_filename = f"generated_image_{i+1}_{timestamp}_{random_num}.png"
                                        elif image_url_lower.endswith('.webp'):
                                            # Include attempt number in filename if multiple attempts
                                            if attempts > 1:
                                                image_filename = f"generated_image_attempt_{attempt+1}_{i+1}_{timestamp}_{random_num}.webp"
                                            else:
                                                image_filename = f"generated_image_{i+1}_{timestamp}_{random_num}.webp"
                                        else:
                                            # Include attempt number in filename if multiple attempts
                                            if attempts > 1:
                                                image_filename = f"generated_image_attempt_{attempt+1}_{i+1}_{timestamp}_{random_num}.png"  # Default to png
                                            else:
                                                image_filename = f"generated_image_{i+1}_{timestamp}_{random_num}.png"  # Default to png
                                    
                                    # Sanitize the filename to prevent path traversal attacks
                                    import re
                                    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', image_filename)
                                    if '..' in image_filename or safe_filename != image_filename:
                                        logger.warning(f"文件名包含无效字符或路径遍历尝试: {image_filename}, 已清理为: {safe_filename}")
                                        if attempts > 1:
                                            safe_filename = f"generated_image_attempt_{attempt+1}_{i+1}_{timestamp}_{random_num}.png"
                                        else:
                                            safe_filename = f"generated_image_{i+1}_{timestamp}_{random_num}.png"
                                    
                                    image_path = output_path / safe_filename
                                    try:
                                        with open(image_path, "wb") as f:
                                            f.write(image_response.content)
                                        logger.info(f"图像保存到 {image_path}")
                                    except Exception as e:
                                        logger.error(f"保存图像到 {image_path} 失败: {e}")
                                        if attempt == attempts - 1:  # Last attempt
                                            return [types.TextContent(type="text", text=f"错误: 保存图像到 {image_path} 失败: {str(e)}")]
                                        else:
                                            logger.info(f"第 {attempt + 1} 次尝试失败，继续下一次尝试")
                                            continue
                                    
                                    # Verify that the file was actually saved
                                    if not image_path.exists():
                                        logger.error(f"图像文件未成功保存: {image_path}")
                                        if attempt == attempts - 1:  # Last attempt
                                            return [types.TextContent(type="text", text=f"错误: 图像文件未成功保存: {image_path}")]
                                        else:
                                            logger.info(f"第 {attempt + 1} 次尝试失败，继续下一次尝试")
                                            continue
                                    
                                    # Check if the file has content
                                    if image_path.stat().st_size == 0:
                                        logger.error(f"保存的图像文件为空: {image_path}")
                                        if attempt == attempts - 1:  # Last attempt
                                            return [types.TextContent(type="text", text=f"错误: 保存的图像文件为空: {image_path}")]
                                        else:
                                            logger.info(f"第 {attempt + 1} 次尝试失败，继续下一次尝试")
                                            continue
                                    
                                    # Include text with the result showing the file path
                                    result_text = f"尝试 {attempt + 1}, 图像 {i+1} 生成成功。文件保存: {image_path}"
                                    results.append(types.TextContent(
                                        type="text",
                                        text=result_text
                                    ))
                                    logger.info(result_text)
                    else:
                        raise ValueError("Only Doubao API is supported in this version")
                
                finally:
                    # Cleanup uploaded images
                    if uploaded_urls:
                        logger.info(f"清理本次尝试上传的 {len(uploaded_urls)} 个临时图像")
                        for url in uploaded_urls:
                            delete_image_from_minio(url)
            
            logger.info(f"工具 {name} 执行成功。总共进行了 {attempts} 次尝试，生成 {len(results)} 个结果。")
            return results
        else:
            raise ValueError(f"未知工具: {name}")

    except Exception as e:
        logger.error(f"执行工具 {name} 时出错: {e}")
        return [types.TextContent(type="text", text=f"错误: {str(e)}")]


async def run_server():
    """运行 MCP 服务器。"""
    logger.info("启动 McpSeedream - 文本到图像生成 MCP 服务器...")
    
    # Setup encoding for cross-platform compatibility
    setup_encoding()
    
    # Run the server using stdin/stdout
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="McpSeedream",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
