import re
import json
import spacy
import glob
import os

nlp = spacy.load("en_core_web_sm")

def structure_text_instructions(raw_text):
    """
    Converts raw text instructions into a structured JSON format.
    
    Args:
        raw_text (str): Raw text instructions.
    
    Returns:
        dict: A dictionary containing the title, steps, and extracted entities.
    """
    structured_data = {}
    
    # Extract a title (assuming the first line is the title)
    lines = raw_text.strip().splitlines()
    if lines:
        structured_data["title"] = lines[0].strip()
    
    # Segment the instructions into steps using a regex for numbered steps.
    steps = re.split(r'\n\s*\d+\.\s+', raw_text)
    # Remove the title part if it was included as the first element.
    if steps and steps[0].strip() == structured_data.get("title", ""):
        steps = steps[1:]
    structured_data["steps"] = [step.strip() for step in steps if step.strip()]
    
    # Use spaCy to extract entities (e.g., dates, names, etc.)
    doc = nlp(raw_text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    structured_data["entities"] = entities
    
    return structured_data

def process_file(file_path):
    """
    Processes a single text file: reads the raw text, structures it,
    and saves the output as a JSON file with a _structured.json suffix.
    
    Args:
        file_path (str): Path to the raw text file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    structured_instructions = structure_text_instructions(raw_text)
    
    json_path = file_path.replace(".txt", "_structured.json")
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured_instructions, f, indent=4)
        print(f"Processed and saved: {json_path}")
    except Exception as e:
        print(f"Error writing {json_path}: {e}")

def main():
    base_dir = "processed/raw_instructions"
    
    file_list = glob.glob(os.path.join(base_dir, "**", "*.txt"), recursive=True)
    print(f"Found {len(file_list)} text files to process.")
    
    for file_path in file_list:
        process_file(file_path)

if __name__ == "__main__":
    main()
