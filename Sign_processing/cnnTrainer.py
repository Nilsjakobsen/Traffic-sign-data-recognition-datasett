import sys
import json
from pathlib import Path
from collections import defaultdict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, transforms

from Sign_processing.cnn import CNN


# WARNING: To run the trainer, you first need to run the augmentations.py script to generate
# the training -and validation data and augmentations
# Then you run this script to train the CNN model on the generated data.

# This class handles the training of the CNN model:
# loads data, trains, validates, and saves the best weights.
class CNNTrainer:
    def __init__(self, train_dir: Path, val_dir: Path, model_path: Path, classes_path: Path):
        # Initialize paths
        self.train_dir = Path(train_dir)
        self.val_dir = Path(val_dir)
        self.model_path = Path(model_path)
        self.classes_path = Path(classes_path)

        # Training parameters
        self.img_size = 128
        self.batch_size = 128
        self.epochs = 15
        self.lr = 1e-3
        self.num_workers = 0
        self.allowed_exts = {".png", ".jpg", ".jpeg"}

        # Check if output directories exist
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.classes_path.parent.mkdir(parents=True, exist_ok=True)

    # Function to eesize image to desired size, convert to tensor and normalize
    def get_transforms(self):
        return transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])

    # Function to check if file has valid extension
    def is_allowed_file(self, path: str) -> bool:
        return Path(path).suffix.lower() in self.allowed_exts

    # Function to build training and validation datasets.
    # This creates a class for every subfolder in train.dir and val.dir.
    # So to add new classes, we can just make a new subfolder and put some 
    # base images there. Could be easy to make a program that people without any
    # coding experience can use to add new classes and retrain the model.
    # Validation images must be created manually, in val.dir.
    def build_datasets(self):
        tfm = self.get_transforms()

        # Get training data from train.dir with torchvision
        train_ds = datasets.ImageFolder(
            str(self.train_dir),
            transform=tfm,
            is_valid_file=self.is_allowed_file,
        )
        # Get validation data from val.dir with torchvision
        val_ds = datasets.ImageFolder(
            str(self.val_dir),
            transform=tfm,
            is_valid_file=self.is_allowed_file,
        )

        # If some validation classes are missing or not part
        # of the training, this makes sure validation use the same class indexes as training.
        # (In our case, we have no validation images for the vegmarkeringMangler sign)
        # Ideally, the dataset should be balanced to avoid this. But if we roll this out
        # to someone else to use, we want it to work regardless.
        train_map = train_ds.class_to_idx
        val_classes = val_ds.classes
        new_samples = []
        for path, val_y in val_ds.samples:
            class_name = val_classes[val_y]
            if class_name in train_map:
                new_samples.append((path, train_map[class_name]))
        val_ds.samples = new_samples
        val_ds.targets = [y for _, y in new_samples]
        val_ds.classes = train_ds.classes
        val_ds.class_to_idx = train_map

        return train_ds, val_ds
    
    # This function evaluates the model on the validation set without tracking gradients.
    # Computes the overall accuracy, macro accuracy, and per-class accuracy.
    # For classes that get bad accuracy, we find/create more training data.
    @torch.no_grad()
    def evaluate(self, model, device, loader, class_names):
        model.eval()
        total = 0
        correct = 0
        per_class_total = defaultdict(int)
        per_class_correct = defaultdict(int)

        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            preds = logits.argmax(1)
            total += y.size(0)
            correct += (preds == y).sum().item()
            for yi, pi in zip(y.tolist(), preds.tolist()):
                per_class_total[yi] += 1
                if yi == pi:
                    per_class_correct[yi] += 1

        overall_acc = correct / max(1, total)
        per_class_acc = {
            class_names[c]: (per_class_correct[c] / max(1, per_class_total[c]))
            for c in range(len(class_names))
        }
        macro_acc = sum(per_class_acc.values()) / max(1, len(per_class_acc))
        return overall_acc, macro_acc, per_class_acc

    # Function to train the CNN model.
    # Loads the dataset and trains for a pre determined number of epochs
    # and saves the best model based on validation accuracy.
    # Trains on GPU if one is available, otherwise uses CPU.
    # The mdoel uses cross-entropy loss and Adam optimizer.
    def train(self):
        train_ds, val_ds = self.build_datasets()
        class_names = train_ds.classes

        with open(self.classes_path, "w", encoding="utf-8") as f:
            json.dump({"classes": class_names}, f)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}  |  num_classes={len(class_names)}")

        model = CNN(num_classes=len(class_names)).to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=self.lr)

        pin = torch.cuda.is_available()
        train_loader = DataLoader(
            train_ds, batch_size=self.batch_size, shuffle=True,
            num_workers=self.num_workers, pin_memory=pin,
        )
        val_loader = DataLoader(
            val_ds, batch_size=self.batch_size, shuffle=False,
            num_workers=self.num_workers, pin_memory=pin,
        )
        best_val_acc = -1.0

        for epoch in range(1, self.epochs + 1):
            print(f"\nEpoch {epoch}/{self.epochs}")
            model.train()
            run_loss, correct, total = 0.0, 0, 0

            for imgs, labels in train_loader:
                imgs, labels = imgs.to(device), labels.to(device)

                optimizer.zero_grad()
                logits = model(imgs)
                loss = criterion(logits, labels)
                loss.backward()
                optimizer.step()

                run_loss += loss.item() * imgs.size(0)
                preds = logits.argmax(1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

            train_loss = run_loss / max(1, total)
            train_acc = correct / max(1, total)
            print(f"  Train  | Loss: {train_loss:.4f}  Accuracy: {train_acc:.4f}")

            val_acc, val_macro, per_class = self.evaluate(model, device, val_loader, class_names)
            print(f"  Val    | Accuracy (overall): {val_acc:.4f}  Accuracy (macro): {val_macro:.4f}")
            print("  Per-class accuracy: " + ", ".join(f"{k}:{v:.2f}" for k, v in per_class.items()))

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), self.model_path)

                print(f"\n")
                print(f"------------------------------------------------")
                print(f"SAVED BEST MODEL SO FAR TO {self.model_path}")
                print(f"------------------------------------------------")

        print(f"\nTraining complete. Best val acc: {best_val_acc:.4f}. Best model at {self.model_path}")


if __name__ == "__main__":
    root = Path(__file__).parent / "demo"
    train_dir = root / "train"
    val_dir = root / "val"
    model_path = root / "cnn.pth"
    classes_path = root / "classes.json"

    if len(sys.argv) < 2:
        print("Usage: python -m Sign_processing.cnnTrainer train")
        sys.exit(0)

    if sys.argv[1] == "train":
        trainer = CNNTrainer(train_dir, val_dir, model_path, classes_path)
        trainer.train()
    else:
        print("Unknown command.")


# be sure to run this from inside .venv
# to train with gpu (cuda).
#-----------------------------------
# python3 -m Sign_processing.cnnTrainer train
#-----------------------------------