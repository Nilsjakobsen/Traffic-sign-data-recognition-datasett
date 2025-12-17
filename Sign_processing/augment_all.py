"""
Augment All Base Images - Create augmented training data for ML.

Takes all base images from base-images/<sign_name>/ and applies augmentations,
saving them to finalboss/<sign_name>/.

This is optimized for processing 50000+ images efficiently.

Usage:
    python Sign_processing/augment_all.py
"""

import os
import sys
import random
from pathlib import Path
from multiprocessing import Pool, cpu_count

import cv2
import numpy as np


# ========== SETTINGS ==========
TARGET_SIZE = (128, 128)           # Output size (width, height)
AUGMENTATIONS_PER_IMAGE = 30       # Number of augmented versions per base image
RANDOM_SEED = 1337                 # For reproducibility

# Augmentation parameters
ROTATION_RANGE = (-180, 180)       # Full rotation (all angles)
SCALE_MIN, SCALE_MAX = 0.80, 1.20  # Scale range (wider)
SHIFT_PX = 8                       # Max shift in pixels
BRIGHT_ALPHA = (0.70, 1.30)        # Brightness/contrast alpha range (wider)
BRIGHT_BETA = (-15, 15)            # Brightness beta range (wider)
BLUR_P = 0.4                       # Probability of blur
BLUR_KERNELS = [3, 5, 7]           # Blur kernel sizes (added 7)
NOISE_P = 0.4                      # Probability of noise
NOISE_STD = 10.0                   # Noise standard deviation
HSV_JITTER_P = 0.6                 # Probability of HSV jitter
PERSPECTIVE_P = 0.3                # Probability of perspective transform
# ==============================

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "base-images"
OUTPUT_DIR = BASE_DIR / "Finalboss"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_EXTS


def resize_to_target(img, size=TARGET_SIZE):
    """Resize image to target size."""
    if (img.shape[1], img.shape[0]) != size:
        return cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    return img


def random_rotation(img, angle_range=ROTATION_RANGE):
    """Apply random rotation."""
    angle = random.uniform(*angle_range)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), 
                          borderMode=cv2.BORDER_REPLICATE)


def random_affine(img):
    """Apply random scale and translation."""
    h, w = img.shape[:2]
    s = random.uniform(SCALE_MIN, SCALE_MAX)
    tx = random.randint(-SHIFT_PX, SHIFT_PX)
    ty = random.randint(-SHIFT_PX, SHIFT_PX)
    M = np.array([[s, 0, tx + (1-s)*w/2],
                  [0, s, ty + (1-s)*h/2]], dtype=np.float32)
    return cv2.warpAffine(img, M, (w, h), 
                          borderMode=cv2.BORDER_REPLICATE)


def random_brightness_contrast(img):
    """Apply random brightness and contrast."""
    alpha = random.uniform(*BRIGHT_ALPHA)
    beta = random.uniform(*BRIGHT_BETA)
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)


def maybe_blur(img):
    """Maybe apply Gaussian blur."""
    if random.random() < BLUR_P:
        k = random.choice(BLUR_KERNELS)
        return cv2.GaussianBlur(img, (k, k), 0)
    return img


def maybe_noise(img):
    """Maybe apply Gaussian noise."""
    if random.random() < NOISE_P:
        noise = np.random.normal(0, NOISE_STD, img.shape).astype(np.float32)
        return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return img


def maybe_hsv_jitter(img):
    """Maybe apply HSV color jitter."""
    if random.random() < HSV_JITTER_P:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        # Hue shift
        h = (h + random.uniform(-8, 8)) % 180
        # Saturation scale
        s = np.clip(s * random.uniform(0.8, 1.2), 0, 255)
        # Value scale
        v = np.clip(v * random.uniform(0.9, 1.1), 0, 255)
        hsv = cv2.merge([h, s, v]).astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img


def maybe_flip(img):
    """Maybe apply horizontal flip (50% chance)."""
    if random.random() < 0.5:
        return cv2.flip(img, 1)
    return img


def maybe_perspective(img):
    """Maybe apply perspective transform to simulate viewing angle."""
    if random.random() < PERSPECTIVE_P:
        h, w = img.shape[:2]
        # Random perspective shift (small)
        shift = int(w * 0.08)
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        pts2 = np.float32([
            [random.randint(0, shift), random.randint(0, shift)],
            [w - random.randint(0, shift), random.randint(0, shift)],
            [random.randint(0, shift), h - random.randint(0, shift)],
            [w - random.randint(0, shift), h - random.randint(0, shift)]
        ])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return img


def maybe_shadow(img):
    """Maybe add random shadow effect."""
    if random.random() < 0.3:
        h, w = img.shape[:2]
        # Create shadow mask
        x1, x2 = sorted([random.randint(0, w), random.randint(0, w)])
        shadow = np.ones_like(img, dtype=np.float32)
        shadow[:, x1:x2] = random.uniform(0.5, 0.8)
        return np.clip(img * shadow, 0, 255).astype(np.uint8)
    return img


def augment_image(img):
    """Apply random augmentations to an image."""
    aug = img.copy()
    
    # Apply augmentations in sequence
    aug = random_rotation(aug)
    aug = random_affine(aug)
    aug = maybe_perspective(aug)
    aug = random_brightness_contrast(aug)
    aug = maybe_hsv_jitter(aug)
    aug = maybe_blur(aug)
    aug = maybe_noise(aug)
    # Note: Not flipping traffic signs as some are directional
    
    # Ensure correct size
    aug = resize_to_target(aug, TARGET_SIZE)
    
    return aug


def process_sign_folder(args):
    """Process all images in a sign folder."""
    sign_folder, output_base = args
    sign_name = sign_folder.name
    
    # Get all base images
    images = sorted([p for p in sign_folder.iterdir() if is_image(p)])
    if not images:
        return sign_name, 0
    
    # Create output folder
    out_folder = output_base / sign_name
    out_folder.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for img_path in images:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        
        img = resize_to_target(img, TARGET_SIZE)
        base_name = img_path.stem
        
        # Save original (resized)
        cv2.imwrite(str(out_folder / f"{base_name}_orig.png"), img)
        count += 1
        
        # Create augmented versions
        for i in range(AUGMENTATIONS_PER_IMAGE):
            aug = augment_image(img)
            cv2.imwrite(str(out_folder / f"{base_name}_aug{i:02d}.png"), aug)
            count += 1
    
    return sign_name, count


def main():
    # Set seed
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    
    # Get all sign folders
    if not INPUT_DIR.exists():
        print(f"Error: Input directory not found: {INPUT_DIR}")
        print("Run run_all_signs.py first to generate base images.")
        sys.exit(1)
    
    sign_folders = sorted([p for p in INPUT_DIR.iterdir() if p.is_dir()])
    if not sign_folders:
        print(f"Error: No sign folders found in {INPUT_DIR}")
        sys.exit(1)
    
    # Count total images
    total_base = sum(
        len([f for f in folder.iterdir() if is_image(f)])
        for folder in sign_folders
    )
    expected_output = total_base * (1 + AUGMENTATIONS_PER_IMAGE)
    
    print(f"\n{'='*60}")
    print(f"Augmenting base images")
    print(f"  - Input: {INPUT_DIR}")
    print(f"  - Output: {OUTPUT_DIR}")
    print(f"  - Sign folders: {len(sign_folders)}")
    print(f"  - Base images: {total_base}")
    print(f"  - Augmentations per image: {AUGMENTATIONS_PER_IMAGE}")
    print(f"  - Expected output: ~{expected_output} images")
    print(f"{'='*60}\n")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process all folders
    total_output = 0
    
    for i, sign_folder in enumerate(sign_folders):
        # Reset seed for each folder for consistency
        random.seed(RANDOM_SEED + i)
        np.random.seed(RANDOM_SEED + i)
        
        sign_name, count = process_sign_folder((sign_folder, OUTPUT_DIR))
        total_output += count
        
        print(f"[{i+1}/{len(sign_folders)}] {sign_name}: {count} images")
    
    print(f"\n{'='*60}")
    print(f"DONE!")
    print(f"  - Total images created: {total_output}")
    print(f"  - Saved to: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
