# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Setup

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd Traffic-sign-data-recognition-datasett
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    If `requirements.txt` is not present, install the following packages manually:
    ```bash
    pip install torch torchvision opencv-python numpy
    ```

## Verification

To verify the installation, you can try importing the modules in python:
```bash
python3 -c "import torch; import cv2; import numpy; print('Imports successful')"
```
