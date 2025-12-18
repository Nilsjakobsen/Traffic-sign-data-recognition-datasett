"""
Sign Compositor - Paste a sign onto map backgrounds at various sizes.

Takes a sign from cleaned_signs_lovdata and pastes it onto all maps
from Map-pictures at different sizes to generate training images.

Usage:
    Just edit SIGN_NAME and NUM_IMAGES below, then run:
    python Sign_processing/sign_compositor.py
"""

import os
import sys
import random
import json
from pathlib import Path

import cv2
import numpy as np


# ========== EDIT THESE ==========
SIGN_NAME = "102_2.png"  # Sign filename from cleaned_signs_lovdata
SIGNS_PER_MAP = 10        # Number of signs to place on each map
# ================================

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
SIGNS_DIR = BASE_DIR / "cleaned_signs_lovdata"
MAPS_DIR = BASE_DIR / "Map-pictures"
OUTPUT_DIR = BASE_DIR / "Map-with-signs"

# Sign sizes to use (pixels)
SIGN_SIZES = [30, 40, 50, 60, 70, 80, 90, 100, 120, 140]

# Rotation range for signs (degrees)
ROTATION_RANGE = (-180, 180)

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
    """Paste sign onto map at position (x, y). Replaces transparent areas with white."""
    result = map_img.copy()
    sh, sw = sign_img.shape[:2]
    mh, mw = map_img.shape[:2]
    
    # Clamp to bounds
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(mw, x + sw), min(mh, y + sh)
    sx1, sy1 = x1 - x, y1 - y
    sx2, sy2 = sx1 + (x2 - x1), sy1 + (y2 - y1)
    
    if x2 <= x1 or y2 <= y1:
        return result
    
    sign_region = sign_img[sy1:sy2, sx1:sx2].copy()
    
    # Handle alpha channel - make white background where transparent
    if sign_region.shape[2] == 4:
        alpha = sign_region[:, :, 3]
        transparent_mask = alpha < 250
        # Replace transparent pixels with white
        sign_region[transparent_mask, 0] = 255  # B
        sign_region[transparent_mask, 1] = 255  # G
        sign_region[transparent_mask, 2] = 255  # R
        
    # Paste (no blending, just copy RGB)
    result[y1:y2, x1:x2] = sign_region[:, :, :3]
    
    return result


def random_position(map_shape, sign_shape, margin=0.05):
    """Get random position with margin from edges."""
    mh, mw = map_shape[:2]
    sh, sw = sign_shape[:2]
    mx, my = int(mw * margin), int(mh * margin)
    
    x = random.randint(mx, max(mx, mw - sw - mx))
    y = random.randint(my, max(my, mh - sh - my))
    return x, y


def check_overlap(x, y, w, h, placed_signs, padding=10):
    """Check if a new sign overlaps with any already placed signs."""
    for (px, py, pw, ph) in placed_signs:
        # Check if rectangles overlap (with padding)
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
    
    # If no position found, return None
    return None, None


def main():
    sign_name = SIGN_NAME
    
    # Find sign
    sign_path = SIGNS_DIR / sign_name
    if not sign_path.exists():
        # Try adding .png
        sign_path = SIGNS_DIR / f"{Path(sign_name).stem}.png"
    if not sign_path.exists():
        print(f"Error: Sign not found: {sign_name}")
        sys.exit(1)
    
    # Get all maps
    map_paths = sorted([p for p in MAPS_DIR.iterdir() if is_image(p)])
    if not map_paths:
        print(f"Error: No maps found in {MAPS_DIR}")
        sys.exit(1)
    
    print(f"Sign: {sign_path.name}")
    print(f"Maps: {len(map_paths)} (using ALL)")
    print(f"Signs per map: {SIGNS_PER_MAP}")
    print(f"Expected base images: {len(map_paths) * SIGNS_PER_MAP}")
    
    # Load sign
    sign = load_sign(sign_path)
    
    # Load all maps
    maps = [(p, load_map(p)) for p in map_paths]
    
    # Create output dir
    sign_stem = sign_path.stem
    out_dir = OUTPUT_DIR / sign_stem
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Store all positions for later extraction
    all_positions = {}
    
    # Generate images - use ALL maps
    random.seed(42)
    count = 0
    
    for i, (map_path, map_img) in enumerate(maps):
        result = map_img.copy()
        placed_signs = []  # Track placed sign positions
        
        # Place multiple signs on the map
        for _ in range(SIGNS_PER_MAP):
            size = random.choice(SIGN_SIZES)
            
            # Resize sign
            resized = resize_sign(sign, size)
            
            # Random rotation
            angle = random.uniform(*ROTATION_RANGE)
            resized = rotate_sign(resized, angle)
            
            sh, sw = resized.shape[:2]
            
            # Find non-overlapping position
            x, y = find_non_overlapping_position(result.shape, resized.shape, placed_signs)
            
            if x is None:
                # Could not find space, skip this sign
                continue
            
            # Paste onto result (accumulate signs)
            result = paste_sign(result, resized, x, y)
            placed_signs.append((x, y, sw, sh))
        
        # Save image
        out_name = f"{sign_stem}_{map_path.stem}_{i:04d}.png"
        out_path = out_dir / out_name
        cv2.imwrite(str(out_path), result)
        
        # Save positions for this image
        all_positions[out_name] = [
            {"x": x, "y": y, "w": w, "h": h} 
            for (x, y, w, h) in placed_signs
        ]
        
        count += 1
    
    # Save positions JSON
    positions_file = out_dir / "positions.json"
    with open(positions_file, "w") as f:
        json.dump(all_positions, f, indent=2)
    
    print(f"\nDone! Saved {count} images to {out_dir}")
    print(f"Sign positions saved to {positions_file}")


if __name__ == "__main__":
    main()
