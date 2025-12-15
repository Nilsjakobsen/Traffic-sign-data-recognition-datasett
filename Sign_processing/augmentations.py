import os
from pathlib import Path
import cv2
import numpy as np
import random
import re


# The purpose of this moduel is to make as much randomness as possible to te
# training data by applying varuious augmentations to the base images.
# The augmentations are generaly not that intense. For example, we do not 
# change the actual color of signs. We do however apply some brightness/contrast
# changes, in addition to slight hue/saturation shifts to make the CNN more robust
# to quality differences in maps and varying light conditions.
# We experienced that these slight augmentations greatly improved the accuracy of our model.

# We acknowledge that this is not a perfect training set and it should be further improved
# and tweaked in the future. We have basically just done all augmentations we could think of.
# But the model works for our purpose as it is, for now
# (to count and calssify signs on maps given by us by Ramudden).

# Some of the functions we have gotten some help from online resources,
# and also Open AI's ChatGPT. We saw it as acceptable because we didn't have
# any pre-made dataset on the internet for our assignment.


# ---------- General settings ----------
BASE_DIR = Path("Sign_processing/demo")                         # base directory for augmentation
TRAIN_DIR = BASE_DIR / "train"                                  # destination for augs
VAL_DIR = BASE_DIR / "val"                                      # validation root
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"} # Valid image types
TARGET_SIZE = (128, 128)                                        # (width, height)
ROTATION_STEP_DEG = 2                                           # how many degrees rotation every step
VARIANTS_PER_ANGLE = 3                                          # number of random augs per angle per base image
TIGHT_CROPS_PER_ANGLE = 1                                       # how many of the above are tight crops
RANDOM_SEED = 1337                                              # Set for pre deterministic results
# Aug settings for training
SCALE_MIN, SCALE_MAX = 0.95, 1.25                               # Range of scaling
SHIFT_PX = 8                                                    # Max pixels to shift in x and y  
BRIGHT_ALPHA_MIN, BRIGHT_ALPHA_MAX = 0.75, 1.25                 # Brigntness/contrast alpha range
BRIGHT_BETA_MIN,  BRIGHT_BETA_MAX  = -5, 5                      # Brightness beta range
GAUSS_BLUR_P   = 0.2                                            # Probability of applying Gaussian blur
GAUSS_BLUR_KS  = [3, 5]                                         # Gaussian blur kernel sizes
NOISE_P        = 0.2                                            # Probability of applying noise                        
NOISE_STD      = 5.0                                            # Standard deviation of Gaussian noise
TIGHT_MARGIN_FRAC = 0.08                                        # Margin fraction for tight cropping
ZOOM_P          = 0.2                                           # Probability of zoom
ZOOM_AMOUNT_MAX = 1.6                                           # Max zoom factor
CLEAN_FIRST = True                          # delete old files with *_ang* in it before creating new ones
# VAL blur for validation
VAL_BLUR_VARIANTS = 3                                           # Number of blur-only variants per base image
VAL_SUFFIX_RE = re.compile(r".*_valblur_v\d+\.png$", re.IGNORECASE)
# ------------------------------

#
# HELPERS
#

# Sets the random seed
if RANDOM_SEED is not None:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

# Regex to identify augmented training images
AUG_NAME_RE = re.compile(r".*_ang\d{3}_v\d+\.png$", re.IGNORECASE)

# Check if path is allowed image file
# (in IMAGE_EXTS)
def is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_EXTS

# Function that checks if a file is an augmented image
# (train aug or val blur)
def is_augmented_file(p: Path) -> bool:
    # train augs
    if bool(AUG_NAME_RE.match(p.name)):
        return True
    # val blur augs
    if bool(VAL_SUFFIX_RE.match(p.name)):
        return True
    return False

#
# TRAINING AUGMENTATIONS
#

# Function for resizing image to target size
def resize_to_target(img, size=TARGET_SIZE):
    if (img.shape[1], img.shape[0]) != size:
        return cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    return img

# Fuction for rotating with expansion to avoid cutting off anything
# Taken from https://stackoverflow.com/questions/43892506/opencv-python-rotate-image-without-cropping-sides
def rotate_expand(image, angle):

    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2.0, h / 2.0)

    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])

    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    M[0, 2] += (nW / 2.0) - cX
    M[1, 2] += (nH / 2.0) - cY

    return cv2.warpAffine(
        image, M, (nW, nH),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255)
    )

# Function to apply random affine transformation
# i.e scaling and translation
def random_affine(img):
    h, w = img.shape[:2]
    s = random.uniform(SCALE_MIN, SCALE_MAX)
    tx = random.randint(-SHIFT_PX, SHIFT_PX)
    ty = random.randint(-SHIFT_PX, SHIFT_PX)
    M = np.array([[s, 0, tx],
                  [0, s, ty]], dtype=np.float32)
    return cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255)
    )

# Function to apply random brightness and contrast
def random_brightness_contrast(img):
    alpha = random.uniform(BRIGHT_ALPHA_MIN, BRIGHT_ALPHA_MAX)
    beta  = random.uniform(BRIGHT_BETA_MIN,  BRIGHT_BETA_MAX)
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

# Functiono to apply gaussion blur
def maybe_blur(img):
    if random.random() < GAUSS_BLUR_P:
        k = random.choice(GAUSS_BLUR_KS)
        return cv2.GaussianBlur(img, (k, k), 0)
    return img

# Function to apply noise
def maybe_noise(img):
    if random.random() < NOISE_P:
        noise = np.random.normal(0, NOISE_STD, img.shape).astype(np.float32)
        return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return img

# Function to apply HSV jitter
def maybe_hsv_jitter(img, p=0.6):
    if random.random() < p:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        dh = random.uniform(-5, 5)
        h = (h + dh) % 180
        s *= random.uniform(0.9, 1.1)
        v *= random.uniform(0.95, 1.05)
        hsv = cv2.merge([h, np.clip(s, 0, 255), np.clip(v, 0, 255)]).astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img

# Function to apply random zoom-in (crop + resize)
def random_zoom_in(img, img_name="", zoom_min=1.0, zoom_max=ZOOM_AMOUNT_MAX, p=ZOOM_P):
    # No zoom for "110+132g" signs (avoid classifying as one single 110 or 132g)
    if "110+132g" in img_name.lower():
        return img
    # Return original if random > p
    if random.random() > p:
        return img
    h, w = img.shape[:2]
    zoom_factor = random.uniform(zoom_min, zoom_max)
    crop_w = int(w / zoom_factor)
    crop_h = int(h / zoom_factor)
    crop_w = max(1, min(w, crop_w))
    crop_h = max(1, min(h, crop_h))
    x1 = random.randint(0, w - crop_w)
    y1 = random.randint(0, h - crop_h)
    cropped = img[y1:y1+crop_h, x1:x1+crop_w]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

# Function to apply tight crop to square around sign
# (Remove unecessary white-space)
def tight_crop_to_square(img, margin_frac=TIGHT_MARGIN_FRAC, min_size=12):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 5, 255, cv2.THRESH_BINARY)
    if cv2.countNonZero(mask) < min_size:
        return img
    ys, xs = np.where(mask > 0)
    y1, y2 = np.min(ys), np.max(ys)
    x1, x2 = np.min(xs), np.max(xs)
    h, w = (y2 - y1 + 1), (x2 - x1 + 1)
    side = int(max(h, w) * (1 + 2 * margin_frac))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    x1s = int(round(cx - side / 2))
    y1s = int(round(cy - side / 2))
    x2s = x1s + side
    y2s = y1s + side
    pad_left   = max(0, -x1s)
    pad_top    = max(0, -y1s)
    pad_right  = max(0, x2s - img.shape[1])
    pad_bottom = max(0, y2s - img.shape[0])
    if any(v > 0 for v in (pad_left, pad_top, pad_right, pad_bottom)):
        img = cv2.copyMakeBorder(
            img, pad_top, pad_bottom, pad_left, pad_right,
            borderType=cv2.BORDER_CONSTANT, value=(255, 255, 255)
        )
        x1s += pad_left; x2s += pad_left
        y1s += pad_top;  y2s += pad_top
    crop = img[y1s:y2s, x1s:x2s]
    if crop.size == 0:
        return img
    return crop

# Function to augment and save an image
def augment_and_save(image_path: Path, dst_dir: Path):
    img = cv2.imread(str(image_path))
    # preceed only if the image file is supported or exists
    if img is None:
        print(f"Could not read image: {image_path}")
        return
    
    img = resize_to_target(img, TARGET_SIZE)
    dst_dir.mkdir(parents=True, exist_ok=True)
    basefile = image_path.stem

    # Clean the previous augmented files
    if CLEAN_FIRST:
        for f in dst_dir.glob(f"{basefile}_ang???_v*.png"):
            try:
                f.unlink()
            except Exception as e:
                print(f"Could not remove old aug file {f}: {e}")

    angles = list(range(0, 360, ROTATION_STEP_DEG))
    total = len(angles) * VARIANTS_PER_ANGLE

    # Loop for all angles and variants and apply augmentations
    for angle in angles:
        for variant in range(VARIANTS_PER_ANGLE):
            aug = rotate_expand(img, angle)
            aug = random_brightness_contrast(aug)
            aug = maybe_hsv_jitter(aug)
            aug = maybe_blur(aug)
            aug = maybe_noise(aug)
            aug = random_zoom_in(aug, img_name=str(image_path))

            if variant < TIGHT_CROPS_PER_ANGLE:
                aug = tight_crop_to_square(aug)
                aug = resize_to_target(aug, TARGET_SIZE)
            else:
                aug = resize_to_target(aug, TARGET_SIZE)
                aug = random_affine(aug)

            # Ensure background is clean white
            mask = (aug[...,0] > 200) & (aug[...,1] > 200) & (aug[...,2] > 200)
            aug[mask] = 255

            # Save augmentated image
            out_name = f"{variant}_ang{angle:03d}_v{variant+1}.png"
            out_path = dst_dir / out_name
            if not out_path.exists():
                cv2.imwrite(str(out_path), aug)
    # Print the totla images crweated for some overview
    print(f"Saved {total} augmented images for {image_path} -> {dst_dir}")


# Function to process all images in a folder and move to augmented files to training folder (TRAIN_DIR)
def process_folder(src_folder: Path):

    rel = src_folder.relative_to(BASE_DIR)
    dst_dir = TRAIN_DIR / rel

    originals = [
        p for p in src_folder.iterdir()
        if is_image(p) and not is_augmented_file(p)
    ]
    if not originals:
        return
    for img_path in originals:
        augment_and_save(img_path, dst_dir)

# Function to process all folders under BASE_DIR
# Without inlcluding training and validation folders
def process_all_folders(base_dir: Path):
    if not base_dir.exists():
        print(f"Base directory not found: {base_dir}")
        return

    for folder, _subdirs, files in os.walk(base_dir):
        folder_path = Path(folder)

        if folder_path == TRAIN_DIR or folder_path == VAL_DIR:
            continue
        if TRAIN_DIR in folder_path.parents or VAL_DIR in folder_path.parents:
            continue

        has_image = any(
            (folder_path / f).suffix.lower() in IMAGE_EXTS and
            not is_augmented_file(folder_path / f)
            for f in files
        )
        if not has_image:
            continue

        process_folder(folder_path)

#
# Added functions to create blur-only variants after creating validation set
# blur for validation iamges. More variants (VAL_BLUR_VARIANTS) = more intense blur
#
def val_blur_variants(img):
    outs = []
    # Starting kernel size at 3. Increase by 2 every step
    for i in range(VAL_BLUR_VARIANTS):
        k = 3 + 2 * i
        if i % 3 == 0:
            out = cv2.GaussianBlur(img, (k, k), 0)
        elif i % 3 == 1:
            out = cv2.medianBlur(img, k)
        else:
            out = cv2.blur(img, (k, k))
        outs.append(out)
    return outs

# Function to process validation folders and create blur variants
def process_validation_blurs(val_root: Path):
    if not val_root.exists():
        print(f"Validation directory not found: {val_root}")
        return

    for class_dir in sorted([p for p in val_root.iterdir() if p.is_dir()]):
        images = [p for p in class_dir.iterdir() if is_image(p) and not is_augmented_file(p)]
        if not images:
            continue

        for img_path in images:
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"Could not read val image: {img_path}")
                continue

            variants = val_blur_variants(img)
            base = img_path.stem
            for i, v in enumerate(variants, start=1):
                out_name = f"{base}_valblur_v{i}.png"
                out_path = class_dir / out_name
                if not out_path.exists():
                    cv2.imwrite(str(out_path), v)

        print(f"Val blur: wrote up to {VAL_BLUR_VARIANTS} per image in {class_dir}")

if __name__ == "__main__":
    # 1) Generate train augmentations for all images in source subfolders
    process_all_folders(BASE_DIR)
    # 2) Generate blur validation augmentations
    process_validation_blurs(VAL_DIR)
