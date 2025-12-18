"""
Run All Signs Pipeline - Process all signs through compositor + extractor.

For each sign in cleaned_signs_lovdata:
1. Paste it onto ALL maps (10 signs per map)
2. Crop out the signs using exact positions

Output:
- Map-with-signs/<sign_name>/  - composite images + positions.json
- base-images/<sign_name>/     - cropped sign images

Usage:
    python Sign_processing/run_all_signs.py
"""

import os
import sys
import random
import json
from pathlib import Path

import cv2
import numpy as np


# ========== SETTINGS ==========
SIGNS_PER_MAP = 10     # Number of signs to place on each map
PADDING = 2            # Extra pixels around each crop
OUTPUT_SIZE = 128      # Resize all crops to this size (128x128) for ML training
ROTATION_RANGE = (-180, 180)  # Full rotation range (degrees)
# ==============================

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
SIGNS_DIR = BASE_DIR / "cleaned_signs_lovdata"
MAPS_DIR = BASE_DIR / "Map-pictures"
COMPOSITES_DIR = BASE_DIR / "Map-with-signs"
OUTPUT_DIR = BASE_DIR / "base-images"

# Sign sizes to use (pixels)
SIGN_SIZES = [30, 40, 50, 60, 70, 80, 90, 100, 120, 140]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_EXTS


def load_sign(path: Path) -> np.ndarray:
    """Load sign with alpha channel (BGRA)."""
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not load: {path}")
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    elif img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    return img


def load_map(path: Path) -> np.ndarray:
    """Load map as BGR."""
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not load: {path}")
    return img


def resize_sign(sign: np.ndarray, size: int) -> np.ndarray:
    """Resize sign to fit within size (maintains aspect ratio)."""
    h, w = sign.shape[:2]
    scale = size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(sign, (new_w, new_h), interpolation=cv2.INTER_AREA)


def rotate_sign(sign: np.ndarray, angle: float) -> np.ndarray:
    """Rotate sign by angle degrees, keeping alpha channel and expanding canvas to fit."""
    h, w = sign.shape[:2]
    
    # Calculate new bounding box size after rotation (works for any angle)
    angle_rad = np.deg2rad(angle)
    cos_a = abs(np.cos(angle_rad))
    sin_a = abs(np.sin(angle_rad))
    new_w = int(np.ceil(w * cos_a + h * sin_a))
    new_h = int(np.ceil(h * cos_a + w * sin_a))
    
    # Rotation matrix around center of original image
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Adjust translation to center rotated image in new canvas
    M[0, 2] += (new_w - w) / 2
    M[1, 2] += (new_h - h) / 2
    
    # Rotate with transparent background (0,0,0,0)
    rotated = cv2.warpAffine(sign, M, (new_w, new_h), 
                              borderMode=cv2.BORDER_CONSTANT, 
                              borderValue=(0, 0, 0, 0))
    return rotated


def paste_sign(map_img: np.ndarray, sign_img: np.ndarray, x: int, y: int) -> np.ndarray:
    """Paste sign onto map at position (x, y) with alpha blending."""
    result = map_img.copy()
    sh, sw = sign_img.shape[:2]
    mh, mw = map_img.shape[:2]
    
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(mw, x + sw), min(mh, y + sh)
    sx1, sy1 = x1 - x, y1 - y
    sx2, sy2 = sx1 + (x2 - x1), sy1 + (y2 - y1)
    
    if x2 <= x1 or y2 <= y1:
        return result
    
    sign_region = sign_img[sy1:sy2, sx1:sx2]
    
    if sign_region.shape[2] == 4:
        alpha = sign_region[:, :, 3:4].astype(np.float32) / 255.0
        blended = (alpha * sign_region[:, :, :3] + (1 - alpha) * result[y1:y2, x1:x2]).astype(np.uint8)
        result[y1:y2, x1:x2] = blended
    else:
        result[y1:y2, x1:x2] = sign_region[:, :, :3]
    
    return result


def check_overlap(x, y, w, h, placed_signs, padding=10):
    """Check if a new sign overlaps with any already placed signs."""
    for (px, py, pw, ph) in placed_signs:
        if (x < px + pw + padding and
            x + w + padding > px and
            y < py + ph + padding and
            y + h + padding > py):
            return True
    return False


def find_non_overlapping_position(map_shape, sign_shape, placed_signs, margin=0.05, max_attempts=100):
    """Try to find a position that doesn't overlap with existing signs."""
    mh, mw = map_shape[:2]
    sh, sw = sign_shape[:2]
    mx, my = int(mw * margin), int(mh * margin)
    
    for _ in range(max_attempts):
        x = random.randint(mx, max(mx, mw - sw - mx))
        y = random.randint(my, max(my, mh - sh - my))
        
        if not check_overlap(x, y, sw, sh, placed_signs):
            return x, y
    
    return None, None


def process_sign(sign_path: Path, maps: list, signs_per_map: int):
    """Process a single sign through the full pipeline."""
    sign_stem = sign_path.stem
    
    # Load sign
    sign = load_sign(sign_path)
    
    # Create output dirs
    composites_out = COMPOSITES_DIR / sign_stem
    composites_out.mkdir(parents=True, exist_ok=True)
    
    base_images_out = OUTPUT_DIR / sign_stem
    base_images_out.mkdir(parents=True, exist_ok=True)
    
    # Store all positions
    all_positions = {}
    
    # Generate composite images - use ALL maps
    for map_idx, (map_path, map_img) in enumerate(maps):
        result = map_img.copy()
        placed_signs = []
        
        for _ in range(signs_per_map):
            size = random.choice(SIGN_SIZES)
            resized = resize_sign(sign, size)
            
            # Random rotation
            angle = random.uniform(*ROTATION_RANGE)
            resized = rotate_sign(resized, angle)
            
            sh, sw = resized.shape[:2]
            
            x, y = find_non_overlapping_position(result.shape, resized.shape, placed_signs)
            
            if x is None:
                continue
            
            result = paste_sign(result, resized, x, y)
            placed_signs.append((x, y, sw, sh))
        
        # Save composite image
        out_name = f"{sign_stem}_{map_path.stem}_{map_idx:04d}.png"
        out_path = composites_out / out_name
        cv2.imwrite(str(out_path), result)
        
        all_positions[out_name] = [
            {"x": x, "y": y, "w": w, "h": h}
            for (x, y, w, h) in placed_signs
        ]
    
    # Save positions JSON
    with open(composites_out / "positions.json", "w") as f:
        json.dump(all_positions, f, indent=2)
    
    # Extract signs using positions
    total_extracted = 0
    for img_name, positions in all_positions.items():
        img_path = composites_out / img_name
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        
        img_h, img_w = img.shape[:2]
        
        for j, pos in enumerate(positions):
            x, y, w, h = pos["x"], pos["y"], pos["w"], pos["h"]
            
            x1 = max(0, x - PADDING)
            y1 = max(0, y - PADDING)
            x2 = min(img_w, x + w + PADDING)
            y2 = min(img_h, y + h + PADDING)
            
            crop = img[y1:y2, x1:x2]
            
            # Resize to fixed size for ML training
            crop = cv2.resize(crop, (OUTPUT_SIZE, OUTPUT_SIZE), interpolation=cv2.INTER_AREA)
            
            base_name = Path(img_name).stem
            crop_name = f"{base_name}_sign{j:02d}.png"
            cv2.imwrite(str(base_images_out / crop_name), crop)
            total_extracted += 1
    
    return len(maps), total_extracted


def main():
    signs_per_map = SIGNS_PER_MAP
    
    # Get all signs
    sign_paths = sorted([p for p in SIGNS_DIR.iterdir() if is_image(p)])
    if not sign_paths:
        print(f"Error: No signs found in {SIGNS_DIR}")
        sys.exit(1)
    
    # Get all maps
    map_paths = sorted([p for p in MAPS_DIR.iterdir() if is_image(p)])
    if not map_paths:
        print(f"Error: No maps found in {MAPS_DIR}")
        sys.exit(1)
    
    # Load all maps once
    print(f"Loading {len(map_paths)} maps...")
    maps = [(p, load_map(p)) for p in map_paths]
    
    print(f"\n{'='*60}")
    print(f"Processing {len(sign_paths)} signs")
    print(f"  - Using ALL {len(maps)} maps for each sign")
    print(f"  - {signs_per_map} signs per map")
    print(f"  - Expected: {len(sign_paths)} signs × {len(maps)} maps × {signs_per_map} = {len(sign_paths) * len(maps) * signs_per_map} base images")
    print(f"{'='*60}\n")
    
    # Set seed for reproducibility
    random.seed(42)
    
    total_composites = 0
    total_crops = 0
    
    for i, sign_path in enumerate(sign_paths):
        print(f"[{i+1}/{len(sign_paths)}] {sign_path.name}...", end=" ", flush=True)
        
        try:
            n_composites, n_crops = process_sign(sign_path, maps, signs_per_map)
            total_composites += n_composites
            total_crops += n_crops
            print(f"✓ {n_composites} composites, {n_crops} crops")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"DONE!")
    print(f"  - Total signs processed: {len(sign_paths)}")
    print(f"  - Total composite images: {total_composites}")
    print(f"  - Total cropped images: {total_crops}")
    print(f"  - Composites saved to: {COMPOSITES_DIR}")
    print(f"  - Cropped signs saved to: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
