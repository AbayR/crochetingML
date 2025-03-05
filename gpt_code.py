import os
import json
import time

# Assume get_image_description() is your function that processes an image via GPT‑Vision.
# We'll modify your processing loop to log failed images.

FAILED_LOG_FILE = "failed_images.json"

def save_failed_images(failed_list, log_file=FAILED_LOG_FILE):
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(failed_list, f, indent=2)

def load_failed_images(log_file=FAILED_LOG_FILE):
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Example processing function
def process_images(image_paths):
    failed_images = []
    for image_path in image_paths:
        try:
            description = get_image_description(
                image_path=image_path,
                prompt=f"Analyze this fashion item. Focus on materials, patterns, and styling."
            )
            # Save the description as needed
            output_path = image_path.replace("raw_image", "descriptions").replace(".png", ".txt")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(description)
            print(f"✓ Processed: {os.path.basename(image_path)}")
        except Exception as e:
            print(f"✗ Failed {os.path.basename(image_path)}: {str(e)}")
            failed_images.append(image_path)
        time.sleep(1)  # Rate limiting
    # Save failed image paths for later reprocessing
    save_failed_images(failed_images)
    return failed_images

# Example main block for primary processing:
if __name__ == "__main__":
    # For example, suppose we collect a list of image paths from your directory.
    image_paths = []  # Populate this list with paths to your PNG images.
    for root, dirs, files in os.walk("processed/raw_image"):
        for file in files:
            if file.lower().endswith(".png"):
                image_paths.append(os.path.join(root, file))
    
    failed = process_images(image_paths)
    print(f"Primary processing complete. {len(failed)} images failed.")

    # Later, run a separate reprocessing script or block:
    # Load the failed images from the log file.
    failed_images = load_failed_images()
    if failed_images:
        print(f"Reprocessing {len(failed_images)} failed images using an alternative method...")
        # Here you could call an alternative processing function, e.g.:
        # for img in failed_images:
        #     alt_description = fallback_processing(img)
        #     # Save or log alt_description accordingly.
