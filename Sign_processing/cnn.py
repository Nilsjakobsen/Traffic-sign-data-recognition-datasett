import json
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image


#This class implements a Convolutional Neural Network for image classification
#The network uses 4 convolutional layers and 2 fully connected layers
#This is the original small model for demo purposes
class CNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.num_classes=num_classes
        
        self.conv1 =nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 =nn.Conv2d(32,  64, kernel_size=3, padding=1)

        self.pool = nn.MaxPool2d(2, 2)

        self.conv3= nn.Conv2d(64, 128,  kernel_size=3, padding=1)
        self.conv4= nn.Conv2d(128,  128, kernel_size=3, padding=1)
        self.dropout = nn.Dropout(0.3)

        self.fc1 = nn.Linear(128 * 16 * 16, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = self.pool(F.relu(self.conv4(x)))

        x = torch.flatten(x, 1)
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)
        return x


# Larger CNN model for the full traffic sign dataset (300+ classes)
# This model has more capacity to handle the increased complexity
# Optimized for RTX 3090 GPU with 24GB VRAM
class CNNLarge(nn.Module):
    def __init__(self, num_classes, img_size=128):
        super().__init__()
        self.num_classes = num_classes
        self.img_size = img_size
        
        # First conv block
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        
        # Second conv block  
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.conv4 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(128)
        
        # Third conv block
        self.conv5 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn5 = nn.BatchNorm2d(256)
        self.conv6 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.bn6 = nn.BatchNorm2d(256)
        
        # Fourth conv block
        self.conv7 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
        self.bn7 = nn.BatchNorm2d(512)
        self.conv8 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.bn8 = nn.BatchNorm2d(512)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout_conv = nn.Dropout2d(0.25)
        self.dropout_fc = nn.Dropout(0.5)
        
        # Calculate flattened size: img_size / 2^4 = 128/16 = 8
        flat_size = 512 * (img_size // 16) * (img_size // 16)
        
        self.fc1 = nn.Linear(flat_size, 1024)
        self.bn_fc1 = nn.BatchNorm1d(1024)
        self.fc2 = nn.Linear(1024, 512)
        self.bn_fc2 = nn.BatchNorm1d(512)
        self.fc3 = nn.Linear(512, num_classes)

    def forward(self, x):
        # Block 1
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.dropout_conv(x)
        
        # Block 2
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        x = self.dropout_conv(x)
        
        # Block 3
        x = F.relu(self.bn5(self.conv5(x)))
        x = self.pool(F.relu(self.bn6(self.conv6(x))))
        x = self.dropout_conv(x)
        
        # Block 4
        x = F.relu(self.bn7(self.conv7(x)))
        x = self.pool(F.relu(self.bn8(self.conv8(x))))
        x = self.dropout_conv(x)
        
        # Fully connected
        x = torch.flatten(x, 1)
        x = self.dropout_fc(F.relu(self.bn_fc1(self.fc1(x))))
        x = self.dropout_fc(F.relu(self.bn_fc2(self.fc2(x))))
        x = self.fc3(x)
        return x


#This class handles prediction using a trained CNN model
#It loads the model weights and predicts the top-k classes for an input image
#Supports both the original CNN and the larger CNNLarge model
class CNNPredictor:
    def __init__(self, model_path, classes_path, use_large_model=True):
        self.model_path = model_path
        self.classes_path = classes_path
        self.img_size = 128
        self.use_large_model = use_large_model

    def get_transforms(self):
        tfm = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5),  (0.5, 0.5, 0.5)),

        ])
        return tfm
    
    def predict(self, img_path, topk=5):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        with open(self.classes_path) as f:
            classes =json.load(f)["classes"]
        num_classes=len(classes)

        # Use appropriate model based on configuration
        if self.use_large_model:
            model = CNNLarge(num_classes, self.img_size).to(device)
        else:
            model = CNN(num_classes).to(device)
        
        model.load_state_dict(torch.load(self.model_path, map_location=device, weights_only=True))
        model.eval()

        tfm = self.get_transforms()
        img= Image.open(img_path).convert("RGB")
        x = tfm(img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            logits = model(x)
            probs = torch.softmax(logits, dim=1)[0]
            top_probs, top_idxs = probs.topk(min(topk, num_classes))
        
        results = []   
        for p, idx in zip(top_probs.tolist(), top_idxs.tolist()):
            print(f"{classes[idx]:<20}  {p:.3f}")
            results.append((classes[idx], p)) 
        
        return results 


