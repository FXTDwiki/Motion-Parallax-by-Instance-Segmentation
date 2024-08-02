import os
import json
import re
from tkinter import Tk
from tkinter.filedialog import askdirectory

def parse_frame_number(filename):
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else None

def renumber_frames(directory):
    # Get a list of all image files in the directory
    image_files = [f for f in os.listdir(directory) if f.endswith(".jpg") and not f.endswith("_saliency.jpg")]

    if not image_files:
        print("No valid image files found.")
        return

    # Dictionary to store original names
    original_names = {}

    # Remove any json files without corresponding image files
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            corresponding_image = file_name.replace(".json", ".jpg")
            if not os.path.exists(os.path.join(directory, corresponding_image)):
                os.remove(os.path.join(directory, file_name))
                print(f"Removed orphan json file: {file_name}")

    # Group files by frame number
    frame_files = {}
    for file in os.listdir(directory):
        frame_number = parse_frame_number(file)
        if frame_number is not None:
            if frame_number not in frame_files:
                frame_files[frame_number] = []
            frame_files[frame_number].append(file)

    # Renumber the files
    for new_number, old_number in enumerate(sorted(frame_files.keys()), start=0):
        for old_name in frame_files[old_number]:
            base, ext = os.path.splitext(old_name)
            if '_saliency' in base:
                new_name = f"image_{new_number:05d}_saliency{ext}"
            else:
                new_name = f"image_{new_number:05d}{ext}"
            
            os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
            original_names[new_name] = old_name

    # Save the original names to a JSON file
    with open(os.path.join(directory, "original_names.json"), "w") as f:
        json.dump(original_names, f, indent=4)
    print("Renumbering complete and original names saved.")

if __name__ == "__main__":
    # Prompt user to select the source folder
    Tk().withdraw()  # Hide the root window
    source_folder = askdirectory(title='Choose the source folder')
    
    if source_folder:
        renumber_frames(source_folder)        
    else:
        print("No source folder selected.")