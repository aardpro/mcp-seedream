# seedream模型的基础使用

## 文生图（纯文本输入单图输出）
通过给模型提供清晰准确的文字指令，即可快速获得符合描述的高质量单张图片。
```bash
curl https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "充满活力的特写编辑肖像，模特眼神犀利，头戴雕塑感帽子，色彩拼接丰富，眼部焦点锐利，景深较浅，具有Vogue杂志封面的美学风格，采用中画幅拍摄，工作室灯光效果强烈。",
    "size": "2K",
    "watermark": false
}'
```

## 图文生图（单图输入单图输出）
基于已有图片，结合文字指令进行图像编辑，包括图像元素增删、风格转化、材质替换、色调迁移、改变背景/视角/尺寸等。
```bash
curl https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "保持模特姿势和液态服装的流动形状不变。将服装材质从银色金属改为完全透明的清水（或玻璃）。透过液态水流，可以看到模特的皮肤细节。光影从反射变为折射。",
    "image": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_5_imageToimage.png",
    "size": "2K",
    "watermark": false
}'
```

## 多图融合（多图输入单图输出）
根据您输入的文本描述和多张参考图片，融合它们的风格、元素等特征来生成新图像。如衣裤鞋帽与模特图融合成穿搭图，人物与风景融合为人物风景图等。
```bash
curl https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "将图1的服装换为图2的服装",
    "image": ["https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imagesToimage_1.png", "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_5_imagesToimage_2.png"],
    "sequential_image_generation": "disabled",
    "size": "2K",
    "watermark": false
}'
```

## 组图输出（多图输出）
支持通过一张或者多张图片和文字信息，生成漫画分镜、品牌视觉等一组内容关联的图片。    
需指定参数 sequential_image_generation 为auto。
```bash
curl https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "生成一组共4张连贯插画，核心为同一庭院一角的四季变迁，以统一风格展现四季独特色彩、元素与氛围",
    "size": "2K",
    "sequential_image_generation": "auto",
    "sequential_image_generation_options": {
        "max_images": 4
    },
    "stream": false,
    "response_format": "url",
    "watermark": false
}'
```

### 单张图生组图
```bash
curl https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "参考这个LOGO，做一套户外运动品牌视觉设计，品牌名称为“GREEN"，包括包装袋、帽子、卡片、挂绳等。绿色视觉主色调，趣味、简约现代风格",
    "image": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imageToimages.png",
    "size": "2K",
    "sequential_image_generation": "auto",
    "sequential_image_generation_options": {
        "max_images": 4
    },
    "stream": false,
    "response_format": "url",
    "watermark": false
}'
```

### 多参考图生组图
```bash
curl https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "生成3张女孩和奶牛玩偶在游乐园开心地坐过山车的图片，涵盖早晨、中午、晚上",
    "image": ["https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imagesToimages_1.png", "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imagesToimages_2.png"],
    "sequential_image_generation": "auto",
    "sequential_image_generation_options": {
        "max_images": 3
    },
    "size": "2K",
    "watermark": false
}'
```

## 入参说明
- image 输入的图片信息，支持 URL，推荐Agent将本地图片文件上传到MinIO获取公共URL使用。    
  + 图片URL：请确保图片URL可被访问，如MinIO公共访问URL。
- size 指定生成图像的尺寸信息，支持以下两种方式，不可混用。推荐默认使用2K。    
  + 方式 1 ：指定生成图像的分辨率，并在 prompt 中用自然语言描述图片宽高比、图片形状或图片用途，最终由模型判断生成图片的大小。    
  可选值：1K(Seedream 4.5 不支持)、2K、4K    
  + 方式2 ：指定生成图像的宽高像素值。    
  默认值：2048x2048    
  总像素取值范围：    
  seedream 4.5：[2560x1440=3686400, 4096x4096=16777216]    
  宽高比取值范围：[1/16, 16]   
- response_format 指定生成图像的返回格式。推荐使用url。        
  + url：返回图片下载链接。    
    
```json
    {
        "response_format": "url"
    }
```
- watermark 指定是否为输出图片添加水印, 推荐写死false。    

## 输出示例
```json
{
    "model": "doubao-seedream-4-5-251128",
    "created": 1757321139,
    "data": [
        {
            "url": "https://...",
            "size": "3104x1312"
        }
    ],
    "usage": {
        "generated_images": 1,
        "output_tokens": xxx,
        "total_tokens": xxx
    }
}
```