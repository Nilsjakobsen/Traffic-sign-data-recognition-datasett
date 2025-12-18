"""
CNN Trainer for the full Norwegian Traffic Sign dataset (Finalboss)
Optimized for RTX 3090 GPU with 24GB VRAM

This trainer:
- Uses the Finalboss directory structure (ImageFolder format)
- Automatically creates train/validation splits
- Uses the larger CNNLarge model for 300+ classes
- Implements learning rate scheduling and early stopping
- Saves checkpoints and training history

Usage:
    python -m Sign_processing.cnnTrainerFinalboss train
    python -m Sign_processing.cnnTrainerFinalboss train --resume
"""

import sys
import json
import random
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingWarmRestarts

from Sign_processing.cnn import CNN, CNNLarge


class FinalbossTrainer:
    def __init__(self, data_dir: Path, output_dir: Path, val_split: float = 0.15):
        """
        Initialize the trainer for the Finalboss dataset.
        
        Args:
            data_dir: Path to Finalboss directory containing class folders
            output_dir: Path to save model, classes.json, and training logs
            val_split: Fraction of data to use for validation (default 15%)
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.val_split = val_split
        
        # Training parameters optimized for RTX 3090
        self.img_size = 128
        self.batch_size = 256  # RTX 3090 can handle larger batches
        self.epochs = 50
        self.lr = 1e-3
        self.num_workers = 8  # Parallel data loading
        self.allowed_exts = {".png", ".jpg", ".jpeg"}
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Paths for outputs
        self.model_path = self.output_dir / "cnn_finalboss.pth"
        self.classes_path = self.output_dir / "classes_finalboss.json"
        self.history_path = self.output_dir / "training_history.json"
        self.checkpoint_path = self.output_dir / "checkpoint.pth"
        
    def get_train_transforms(self):
        """Data augmentation for training - more aggressive for better generalization."""
        return transforms.Compose([
            transforms.Resize((self.img_size + 16, self.img_size + 16)),
            transforms.RandomCrop(self.img_size),
            transforms.RandomHorizontalFlip(p=0.3),  # Some signs shouldn't be flipped
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            transforms.RandomErasing(p=0.2, scale=(0.02, 0.1)),
        ])
    
    def get_val_transforms(self):
        """Simple transforms for validation - no augmentation."""
        return transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ])
    
    def is_allowed_file(self, path: str) -> bool:
        """Check if file has valid image extension."""
        return Path(path).suffix.lower() in self.allowed_exts
    
    def build_datasets(self):
        """
        Build train and validation datasets with stratified split.
        Each class maintains the same train/val ratio.
        """
        # Load full dataset to get class info
        full_dataset = datasets.ImageFolder(
            str(self.data_dir),
            is_valid_file=self.is_allowed_file,
        )
        
        class_names = full_dataset.classes
        num_classes = len(class_names)
        print(f"Found {num_classes} classes in {self.data_dir}")
        print(f"Total images: {len(full_dataset)}")
        
        # Save class names
        with open(self.classes_path, "w", encoding="utf-8") as f:
            json.dump({"classes": class_names}, f, indent=2)
        print(f"Saved class names to {self.classes_path}")
        
        # Group samples by class for stratified split
        class_indices = defaultdict(list)
        for idx, (path, label) in enumerate(full_dataset.samples):
            class_indices[label].append(idx)
        
        train_indices = []
        val_indices = []
        
        # Stratified split - same ratio per class
        random.seed(42)  # Reproducibility
        for label, indices in class_indices.items():
            random.shuffle(indices)
            split_idx = int(len(indices) * (1 - self.val_split))
            train_indices.extend(indices[:split_idx])
            val_indices.extend(indices[split_idx:])
        
        print(f"Train samples: {len(train_indices)}, Val samples: {len(val_indices)}")
        
        # Create datasets with appropriate transforms
        train_dataset = datasets.ImageFolder(
            str(self.data_dir),
            transform=self.get_train_transforms(),
            is_valid_file=self.is_allowed_file,
        )
        val_dataset = datasets.ImageFolder(
            str(self.data_dir),
            transform=self.get_val_transforms(),
            is_valid_file=self.is_allowed_file,
        )
        
        # Create subset datasets
        train_subset = Subset(train_dataset, train_indices)
        val_subset = Subset(val_dataset, val_indices)
        
        return train_subset, val_subset, class_names
    
    @torch.no_grad()
    def evaluate(self, model, device, loader, class_names):
        """
        Evaluate model on validation set.
        Returns overall accuracy, macro accuracy, and per-class metrics.
        """
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
        
        # Calculate per-class accuracy
        per_class_acc = {}
        for c in range(len(class_names)):
            if per_class_total[c] > 0:
                per_class_acc[class_names[c]] = per_class_correct[c] / per_class_total[c]
            else:
                per_class_acc[class_names[c]] = 0.0
        
        macro_acc = sum(per_class_acc.values()) / max(1, len(per_class_acc))
        
        return overall_acc, macro_acc, per_class_acc
    
    def save_checkpoint(self, model, optimizer, scheduler, epoch, best_acc, history):
        """Save training checkpoint for resume capability."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
            'best_acc': best_acc,
            'history': history,
        }
        torch.save(checkpoint, self.checkpoint_path)
    
    def load_checkpoint(self, model, optimizer, scheduler):
        """Load training checkpoint."""
        if not self.checkpoint_path.exists():
            return 0, 0.0, {'train_loss': [], 'train_acc': [], 'val_acc': [], 'val_macro_acc': [], 'lr': []}
        
        checkpoint = torch.load(self.checkpoint_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if scheduler and checkpoint['scheduler_state_dict']:
            scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        return checkpoint['epoch'], checkpoint['best_acc'], checkpoint['history']
    
    def train(self, resume=False, use_small_model=False):
        """
        Train the CNN model on the Finalboss dataset.
        
        Args:
            resume: Whether to resume from checkpoint
            use_small_model: Use the smaller CNN instead of CNNLarge
        """
        print("=" * 60)
        print("FINALBOSS CNN TRAINER")
        print("=" * 60)
        print(f"Data directory: {self.data_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Image size: {self.img_size}x{self.img_size}")
        print(f"Batch size: {self.batch_size}")
        print(f"Max epochs: {self.epochs}")
        print(f"Initial LR: {self.lr}")
        print("=" * 60)
        
        # Build datasets
        train_subset, val_subset, class_names = self.build_datasets()
        num_classes = len(class_names)
        
        # Setup device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"\nUsing device: {device}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # Create model
        if use_small_model:
            print(f"\nUsing small CNN model (original)")
            model = CNN(num_classes=num_classes).to(device)
        else:
            print(f"\nUsing large CNN model (CNNLarge)")
            model = CNNLarge(num_classes=num_classes, img_size=self.img_size).to(device)
        
        # Count parameters
        num_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"Model parameters: {num_params:,}")
        
        # Loss, optimizer, scheduler
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(model.parameters(), lr=self.lr, weight_decay=1e-4)
        scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3)
        
        # Data loaders
        pin = torch.cuda.is_available()
        train_loader = DataLoader(
            train_subset, batch_size=self.batch_size, shuffle=True,
            num_workers=self.num_workers, pin_memory=pin, drop_last=True,
        )
        val_loader = DataLoader(
            val_subset, batch_size=self.batch_size, shuffle=False,
            num_workers=self.num_workers, pin_memory=pin,
        )
        
        # Resume or initialize
        start_epoch = 0
        best_val_acc = 0.0
        history = {'train_loss': [], 'train_acc': [], 'val_acc': [], 'val_macro_acc': [], 'lr': []}
        
        if resume:
            start_epoch, best_val_acc, history = self.load_checkpoint(model, optimizer, scheduler)
            print(f"\nResuming from epoch {start_epoch + 1}, best val acc: {best_val_acc:.4f}")
        
        # Early stopping
        patience = 10
        no_improve_count = 0
        
        print(f"\nStarting training...")
        print("-" * 60)
        
        for epoch in range(start_epoch, self.epochs):
            # Training phase
            model.train()
            run_loss, correct, total = 0.0, 0, 0
            
            for batch_idx, (imgs, labels) in enumerate(train_loader):
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
                
                # Progress update every 50 batches
                if (batch_idx + 1) % 50 == 0:
                    print(f"  Batch {batch_idx + 1}/{len(train_loader)} | "
                          f"Loss: {loss.item():.4f} | Acc: {correct/total:.4f}")
            
            train_loss = run_loss / max(1, total)
            train_acc = correct / max(1, total)
            
            # Validation phase
            val_acc, val_macro_acc, per_class_acc = self.evaluate(model, device, val_loader, class_names)
            
            # Update scheduler
            scheduler.step(val_acc)
            current_lr = optimizer.param_groups[0]['lr']
            
            # Log history
            history['train_loss'].append(train_loss)
            history['train_acc'].append(train_acc)
            history['val_acc'].append(val_acc)
            history['val_macro_acc'].append(val_macro_acc)
            history['lr'].append(current_lr)
            
            # Print epoch summary
            print(f"\nEpoch {epoch + 1}/{self.epochs}")
            print(f"  Train | Loss: {train_loss:.4f} | Acc: {train_acc:.4f}")
            print(f"  Val   | Acc: {val_acc:.4f} | Macro Acc: {val_macro_acc:.4f}")
            print(f"  LR: {current_lr:.2e}")
            
            # Find worst performing classes
            sorted_classes = sorted(per_class_acc.items(), key=lambda x: x[1])
            print(f"  Worst 5 classes: {', '.join(f'{k}:{v:.2f}' for k, v in sorted_classes[:5])}")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), self.model_path)
                print(f"  >>> NEW BEST MODEL SAVED (val_acc: {best_val_acc:.4f}) <<<")
                no_improve_count = 0
            else:
                no_improve_count += 1
                print(f"  No improvement for {no_improve_count} epochs")
            
            # Save checkpoint
            self.save_checkpoint(model, optimizer, scheduler, epoch + 1, best_val_acc, history)
            
            # Save history
            with open(self.history_path, 'w') as f:
                json.dump(history, f, indent=2)
            
            # Early stopping
            if no_improve_count >= patience:
                print(f"\nEarly stopping after {patience} epochs without improvement")
                break
            
            print("-" * 60)
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print(f"Best validation accuracy: {best_val_acc:.4f}")
        print(f"Model saved to: {self.model_path}")
        print(f"Classes saved to: {self.classes_path}")
        print(f"History saved to: {self.history_path}")
        print("=" * 60)
        
        return best_val_acc


def main():
    # Default paths
    root = Path(__file__).parent.parent
    data_dir = root / "Finalboss"
    output_dir = root / "Sign_processing" / "finalboss_model"
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m Sign_processing.cnnTrainerFinalboss train")
        print("  python -m Sign_processing.cnnTrainerFinalboss train --resume")
        print("  python -m Sign_processing.cnnTrainerFinalboss train --small  (use smaller model)")
        sys.exit(0)
    
    command = sys.argv[1]
    resume = "--resume" in sys.argv
    use_small = "--small" in sys.argv
    
    if command == "train":
        trainer = FinalbossTrainer(data_dir, output_dir)
        trainer.train(resume=resume, use_small_model=use_small)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
