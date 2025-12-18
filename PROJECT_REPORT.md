# Traffic Sign Recognition Project: Dataset & Methodology

## 1. Introduction
This project aims to develop a robust traffic sign recognition system using a Convolutional Neural Network (CNN). The core of our approach lies in generating a high-quality, synthetic dataset that mimics real-world conditions, allowing us to train a model capable of recognizing over 300 distinct classes of Norwegian traffic signs.

## 2. Dataset Generation Pipeline
We created a custom pipeline to generate a massive dataset from a set of clean, transparent traffic sign images (`cleaned_signs_lovdata`).

### Step 1: Map Composition (`run_all_signs.py`)
To ensure the model learns to recognize signs in their natural context, we composite the clean sign images onto random map backgrounds.
- **Process**: We take a clean sign and paste it onto various map images.
- **Output**: This creates "base images" where the sign is embedded in a realistic background, rather than a plain white or black background. This helps the model distinguish the sign from complex surroundings.

### Step 2: Augmentation (`augment_all.py`)
The base images are then passed through an extensive augmentation pipeline to create the final training set (`Finalboss`). This step is crucial for making the model invariant to changes in lighting, orientation, and quality.

**Key Augmentations:**
1.  **Geometric Transformations**:
    *   **Rotation**: Random rotations (±10 degrees) to simulate signs that are not perfectly straight.
    *   **Scaling**: Random scaling (95-105%) to simulate different distances.
    *   **Perspective Transform**: Simulates viewing the sign from different angles (e.g., from the side of the road).
2.  **Visual Corruptions**:
    *   **Blur**: Gaussian blur to simulate motion blur or out-of-focus cameras.
    *   **Noise**: Gaussian noise to simulate sensor grain or low-light conditions.
    *   **Shadows**: Random shadow masks to simulate partial occlusion or lighting changes.
3.  **Color Adjustments**:
    *   **Brightness/Contrast**: Random adjustments to simulate different times of day and weather.
    *   **HSV Jitter**: Slight color variations.

## 3. Model Architecture
We utilize a custom Convolutional Neural Network (CNN) designed for this specific task.

- **Input**: 128x128 pixel RGB images.
- **Architecture**:
    *   **Convolutional Layers**: 4 layers with increasing filter sizes (32 -> 64 -> 128 -> 128) to capture hierarchical features (edges -> shapes -> complex patterns).
    *   **Pooling**: Max pooling layers to reduce spatial dimensions and provide translation invariance.
    *   **Fully Connected Layers**: Two dense layers to map the extracted features to the 300+ class probabilities.
    *   **Dropout**: Applied to prevent overfitting.

## 4. Results & Analysis

We compared two training runs to evaluate the impact of our augmentation strategy, specifically focusing on geometric transformations (angles/rotation).

### Experiment A: No Angle/Rotation Augmentation
*   **Training Accuracy**: 76.52%
*   **Validation Accuracy**: 91.37%
*   **Loss**: 0.6767

### Experiment B: With Angle/Rotation Augmentation (Final Model)
*   **Training Accuracy**: 79.04%
*   **Validation Accuracy**: 92.65%
*   **Loss**: 0.6171

### Key Findings
1.  **Improved Generalization**: Adding angle and rotation augmentations significantly improved the model's performance. The validation accuracy jumped from **91.37%** to **92.65%** after just one epoch. This confirms that training the model to recognize tilted or angled signs helps it generalize better to unseen data.
2.  **Rapid Convergence**: The model converges very quickly, reaching >90% accuracy in the first epoch. This indicates the high quality of the synthetic dataset.
3.  **Challenge with Mirrored Signs**: The "Worst 5 classes" analysis revealed that the model struggles with certain signs (e.g., `402_2`, `402_3`). These are often mirrored versions of each other (e.g., "Keep Right" vs. "Keep Left"). Since the visual features are identical but flipped, the model requires more training epochs to distinguish the subtle directional cues.

## 5. Conclusion
Our synthetic data generation pipeline, combined with aggressive augmentation (especially perspective and rotation), has proven highly effective. We achieved a validation accuracy of **92.65%** in the very first epoch, demonstrating that the model is learning robust features for traffic sign recognition. Future work will focus on resolving the confusion between mirrored sign classes.
