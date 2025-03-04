import os
import glob
import pdfplumber
import cv2
import numpy as np
import time

raw_pdf_folder = os.path.join(os.getcwd(), "scrapper/input_file/")  
print(f"Found the folder with the raw pdf files: {raw_pdf_folder}")
raw_image_folder = os.path.join(os.getcwd(), "processed/raw_image")
raw_instructions_folder = os.path.join(os.getcwd(), "processed/raw_instructions")

def makedirs():
    os.makedirs(raw_pdf_folder, exist_ok=True)
    os.makedirs(raw_image_folder, exist_ok=True)
    os.makedirs(raw_instructions_folder, exist_ok=True)

def extract_text_from_pdf_local(pdf_path):
    """
    Extract text from a PDF using pdfplumber.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] Failed to extract text from {pdf_path}: {e}")
    return text

def extract_largest_image(pdf_path, output_image_path):
    """
    Extract the largest image from the first page of the PDF.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            images = first_page.images
            if not images:
                print(f"[WARNING] No images found on the first page of {pdf_path}.")
                return
            # Find the largest image by area
            largest_image = max(images, key=lambda img: (img["x1"] - img["x0"]) * (img["bottom"] - img["top"]))
            
            # Get image bounding box
            x0, y0, x1, y1 = largest_image["x0"], largest_image["top"], largest_image["x1"], largest_image["bottom"]
            page_width, page_height = first_page.width, first_page.height
            
            # Clamp the bounding box within page dimensions
            x0 = max(0, x0)
            y0 = max(0, y0)
            x1 = min(page_width, x1)
            y1 = min(page_height, y1)
            
            if x1 <= x0 or y1 <= y0:
                print(f"[ERROR] Invalid bounding box in {pdf_path}: ({x0}, {y0}, {x1}, {y1})")
                return
            
            # Crop and save the image
            cropped_img = first_page.within_bbox((x0, y0, x1, y1)).to_image().original
            output_img = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
            cv2.imwrite(output_image_path, output_img)
            print(f"[SUCCESS] Extracted image saved as {output_image_path}")
    except Exception as e:
        print(f"[ERROR] Failed to extract image from {pdf_path}: {e}")

def process_pdf(pdf_path):
    """
    Process a single PDF: extract text and the largest image.
    This function preserves the subfolder structure in the output directories.
    """
    # Get the relative path of the PDF file with respect to the raw_pdf_folder
    relative_path = os.path.relpath(pdf_path, raw_pdf_folder)
    pdf_base, _ = os.path.splitext(relative_path)
    
    # Construct output paths that preserve the subfolder structure
    text_file_path = os.path.join(raw_instructions_folder, pdf_base + ".txt")
    image_file_path = os.path.join(raw_image_folder, pdf_base + ".png")
    
    # Ensure the output directories exist
    os.makedirs(os.path.dirname(text_file_path), exist_ok=True)
    os.makedirs(os.path.dirname(image_file_path), exist_ok=True)
    
    # Extract text
    text = extract_text_from_pdf_local(pdf_path)
    try:
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[SUCCESS] Extracted text saved to {text_file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save extracted text for {pdf_path}: {e}")
    
    # Extract image
    extract_largest_image(pdf_path, image_file_path)

def main():
    makedirs()
    processed_count = 0
    
    # Recursively search for PDF files in raw_pdf_folder (including subfolders)
    pdf_files = glob.glob(os.path.join(raw_pdf_folder, '**', '*.pdf'), recursive=True)
    print(f"[INFO] Found {len(pdf_files)} PDF files to process.")

    for pdf_file in pdf_files:
        # Determine output file paths based on relative structure
        relative_path = os.path.relpath(pdf_file, raw_pdf_folder)
        pdf_base, _ = os.path.splitext(relative_path)
        image_path = os.path.join(raw_image_folder, pdf_base + ".png")
        text_path = os.path.join(raw_instructions_folder, pdf_base + ".txt")
        
        # Skip if both image and text already exist
        if os.path.exists(image_path) and os.path.exists(text_path):
            print(f"[INFO] {pdf_file} already processed, skipping!")
            continue
        
        print(f"[INFO] Processing {pdf_file}...")
        process_pdf(pdf_file)
        processed_count += 1
        print(f"[INFO] Processed PDF count: {processed_count}")
        time.sleep(1)  # Optional delay

    print(f"[INFO] Processing complete. Total PDFs processed: {processed_count}")

if __name__ == "__main__":
    main()
