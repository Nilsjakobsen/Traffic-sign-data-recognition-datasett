"""
Base Image Extractor - Extract/crop signs from composite map images.

Takes composite images from Map-with-signs/<sign_name>/ and extracts 
the signs using saved positions, saving them to base-images/<sign_name>/.

Usage:
    Just edit SIGN_NAME below, then run:
    python Sign_processing/base_image_extractor.py
"""

import sys
import json
from pathlib import Path

import cv2

# ========== EDIT THIS ==========
SIGN_NAME = "102_2"  # Sign name (without .png) - must match folder in Map-with-signs
PADDING = 2          # Extra pixels around each crop
# ================================

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "Map-with-signs"
OUTPUT_DIR = BASE_DIR / "base-images"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_EXTS


def main():
    sign_name = SIGN_NAME
    
    # Input folder with composite images
    input_folder = INPUT_DIR / sign_name
    if not input_folder.exists():
        print(f"Error: Input folder not found: {input_folder}")
        print(f"Run sign_compositor.py first to generate composite images.")
        sys.exit(1)
    
    # Load positions file
    positions_file = input_folder / "positions.json"
    if not positions_file.exists():
        print(f"Error: positions.json not found in {input_folder}")
        print(f"Re-run sign_compositor.py to generate it.")
        sys.exit(1)
    
    with open(positions_file, "r") as f:
        all_positions = json.load(f)
    
    # Output folder for extracted signs
    output_folder = OUTPUT_DIR / sign_name
    output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"Sign: {sign_name}")
    print(f"Input: {input_folder}")
    print(f"Output: {output_folder}")
    print(f"Extracting signs...")
    
    total_extracted = 0
    
    for img_name, positions in all_positions.items():
        img_path = input_folder / img_name
        if not img_path.exists():
            print(f"  Warning: Image not found: {img_name}")
            continue
        
        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  Warning: Could not load: {img_name}")
            continue
        
        img_h, img_w = img.shape[:2]
        
        # Crop each sign using saved positions
        for j, pos in enumerate(positions):
            x, y, w, h = pos["x"], pos["y"], pos["w"], pos["h"]
            
            # Add padding and clamp to image bounds
            x1 = max(0, x - PADDING)
            y1 = max(0, y - PADDING)
            x2 = min(img_w, x + w + PADDING)
            y2 = min(img_h, y + h + PADDING)
            
            # Crop
            crop = img[y1:y2, x1:x2]
            
            # Save
            base_name = Path(img_name).stem
            out_name = f"{base_name}_sign{j:02d}.png"
            out_path = output_folder / out_name
            cv2.imwrite(str(out_path), crop)
            total_extracted += 1
    
    print(f"\nDone! Extracted {total_extracted} signs to {output_folder}")


if __name__ == "__main__":
    main()
