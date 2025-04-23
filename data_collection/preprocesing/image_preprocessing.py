import os
import base64
import requests
import time
import json
import openai
from urllib.parse import unquote
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_image_description(
    image_path: str,
    prompt: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 300
) -> str:
    """
    Analyze an image using GPT‑Vision capabilities via OpenAI's chat completions API.
    
    Args:
        image_path: Path to the image file.
        prompt: Custom prompt instructing the model.
        temperature: Controls randomness (0 is deterministic).
        max_tokens: Maximum response length.
    
    Returns:
        Generated analysis (description) of the image.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Read and encode the image as base64
    with open(image_path, "rb") as image_file:
        b64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Default prompt if none provided
    prompt = prompt or (
        "Analyze this image in detail. Describe:\n"
        "1. Key visual elements and composition\n"
        "2. Colors and textures\n"
        "3. Style and aesthetic qualities\n"
        "4. Potential patterns or design elements\n"
        "5. Notable fashion or textile characteristics"
    )
    
    # Construct the message payload as required by GPT‑Vision
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
            ]
        }
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        # Access the response using dictionary keys (new interface)
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API request failed: {str(e)}")
        return ""


def process_image_directory(
    base_input_path: str = "processed/raw_image",
    output_root: str = "descriptions",
    api_key: str = OPENAI_API_KEY,
    batch_size: int = 10,
    delay: float = 1.0
) -> Dict[str, List[str]]:
    """
    Process all images in categorized subfolders and save GPT‑Vision descriptions.
    
    Args:
        base_input_path: Root directory containing category folders.
        output_root: Where to save description files.
        api_key: API key for GPT‑Vision.
        batch_size: Number of images per batch.
        delay: Seconds to wait between batches.
    
    Returns:
        Dictionary mapping categories to a list of processed image file paths.
    """
    from time import sleep 
    processed = {}
    
    for root, dirs, files in os.walk(base_input_path):
        if root == base_input_path:
            continue
            
        rel_path = os.path.relpath(root, base_input_path)
        category = unquote(rel_path).replace('+', ' ') 
        
        print(f"\nProcessing category: {category}")
        
        output_dir = os.path.join(output_root, category)
        os.makedirs(output_dir, exist_ok=True)
        
        image_files = [f for f in files if f.lower().endswith('.png')]
        processed[category] = []
        
        
        for i in range(0, len(image_files), batch_size):
            batch = image_files[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}: {len(batch)} images")
            
            for filename in batch:
                image_path = os.path.join(root, filename)
                output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")
                
                try:
                    description = get_image_description(
                        image_path=image_path,
                        
                        prompt=(
                            f"Analyze this fashion item from the category '{category}'. Focus on:\n"
                            "1. Materials and textures\n"
                            "2. Construction techniques\n"
                            "3. Pattern details\n"
                            "4. Styling elements"
                        )
                    )
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(description)
                    
                    processed[category].append(image_path)
                    print(f"✓ Processed: {filename}")
                
                except Exception as e:
                    print(f"✗ Failed {filename}: {str(e)}")
            
            sleep(delay)
    
    return processed

if __name__ == "__main__":
    try:
        results = process_image_directory()
        print("\nProcessing complete!")
        print(f"Categories processed: {len(results)}")
        print(f"Total images processed: {sum(len(v) for v in results.values())}")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
