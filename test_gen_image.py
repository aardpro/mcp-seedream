import sys
import os
import asyncio
from pathlib import Path
import logging

# Configure logging to see server output
logging.basicConfig(level=logging.INFO)

# Add src/main to path so we can import server
project_root = os.getcwd()
sys.path.append(os.path.join(project_root, "src", "main"))

try:
    from server import handle_call_tool
except ImportError:
    # If running from a different directory, try to adjust
    sys.path.append(os.path.join(os.path.dirname(__file__), "src", "main"))
    from server import handle_call_tool

async def main():
    print("Starting test...")
    
    # Define paths
    input_image = os.path.join(project_root, "images", "zhuangyan.png")
    output_dir = os.path.join(project_root, "images", "output")
    
    print(f"Input image: {input_image}")
    print(f"Output directory: {output_dir}")
    
    if not os.path.exists(input_image):
        print(f"Error: Input image not found at {input_image}")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Arguments for the tool
    arguments = {
        "prompt": "把参考图人物的衣服颜色换成淡黄色，给她带一个手表，给她戴上一副银边眼镜",
        "image": input_image,
        "output_dir": output_dir,
        "model": "doubao-seedream-4-5-251128",  # Explicitly setting the model or relying on default
        "n": 1,
        "size": "2K"
    }
    
    print("Calling generate_image tool...")
    try:
        results = await handle_call_tool("generate_image", arguments)
        
        print("\nResults:")
        for result in results:
            if hasattr(result, 'text'):
                print(result.text)
            else:
                print(result)
                
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
