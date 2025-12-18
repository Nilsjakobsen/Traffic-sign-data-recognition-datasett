# Traffic Sign Data Recognition Dataset

This project is designed to generate, augment, and train a Convolutional Neural Network (CNN) for traffic sign recognition. It includes a pipeline for creating synthetic training data by compositing traffic signs onto map backgrounds, extracting them, and applying various augmentations.

## Project Structure

- **`cleaned_signs_lovdata/`**: Contains the source images of traffic signs (clean, transparent background).
- **`base-images/`**: Generated base images. These are created by pasting signs onto map backgrounds and then cropping them out.
- **`Finalboss/`**: The final augmented dataset used for training. Contains multiple augmented versions of each base image.
- **`Sign_processing/`**: Contains the Python scripts for the data pipeline and model training.
  - `run_all_signs.py`: Composites signs onto maps and extracts base images.
  - `augment_all.py`: Augments the base images to create the final dataset.
  - `cnnTrainer.py`: Trains the CNN model.
  - `cnn.py`: Defines the CNN architecture.
- **`Map-pictures/`**: Background map images used for compositing.
- **`Map-with-signs/`**: Intermediate output showing signs pasted onto maps (with JSON position data).

## Workflow

1.  **Data Generation**: Signs from `cleaned_signs_lovdata` are placed onto random map backgrounds to create realistic context.
2.  **Extraction**: The signs are cropped from these scenes to create `base-images`.
3.  **Augmentation**: The base images are augmented (rotated, scaled, blurred, noise added, etc.) to create a robust dataset in `Finalboss`.
4.  **Training**: A CNN is trained on the augmented data to recognize the traffic signs.

## Getting Started

See [INSTALL.md](INSTALL.md) for installation instructions.
See [RUN.md](RUN.md) for details on how to run the pipeline.
