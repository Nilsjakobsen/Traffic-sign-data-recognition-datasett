# Run Description

This document describes how to run the data generation and training pipeline.

## 1. Generate Base Images

This step takes the clean sign images from `cleaned_signs_lovdata`, composites them onto map backgrounds, and extracts the "base images" into the `base-images/` directory.

```bash
python Sign_processing/run_all_signs.py
```

**Output:**
- `base-images/<sign_class>/`: Cropped images of signs from the map composites.
- `Map-with-signs/`: Full map images with signs pasted on them.

## 2. Augment Images

This step takes the images from `base-images/` and applies various augmentations (rotation, scaling, noise, etc.) to create a large, robust dataset in `Finalboss/`.

```bash
python Sign_processing/augment_all.py
```

**Output:**
- `Finalboss/<sign_class>/`: Multiple augmented versions of each base image.

## 3. Train the Model

The training script `cnnTrainer.py` is used to train the CNN.

**Note:** By default, the script is configured to run on a small demo dataset located in `Sign_processing/demo/`.

To run the training on the demo data:

```bash
# Ensure you are in the virtual environment
source .venv/bin/activate
python -m Sign_processing.cnnTrainer train
```

### Training on the Full Dataset (Finalboss)

To train on the full dataset generated in `Finalboss/`, use the dedicated trainer script:

```bash
# Ensure you are in the virtual environment
source .venv/bin/activate
python -m Sign_processing.cnnTrainerFinalboss train
```

This script is pre-configured to use the `Finalboss` directory and handles the training process for the full dataset.

1.  **Split the data**: Organize the `Finalboss` folder into training and validation sets. You should create a structure like:
    ```
    dataset/
      train/
        class1/
        class2/
        ...
      val/
        class1/
        class2/
        ...
    ```
    You can move a percentage (e.g., 20%) of the images from `Finalboss` to a `val` folder, and the rest to `train`.

2.  **Update the script**: Edit `Sign_processing/cnnTrainer.py` to point to your new dataset directories.
    Change the `root`, `train_dir`, and `val_dir` variables in the `if __name__ == "__main__":` block at the bottom of the file.

    ```python
    # Example modification in Sign_processing/cnnTrainer.py
    # root = Path("/path/to/your/dataset")
    # train_dir = root / "train"
    # val_dir = root / "val"
    ```

3.  **Run the trainer**:
    ```bash
    python -m Sign_processing.cnnTrainer train
    ```

**Output:**
- The script will save the best model weights to `cnn.pth` (or the path specified in the script).
