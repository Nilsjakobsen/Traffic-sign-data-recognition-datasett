import json
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image


#This class implements a Convolutional Neural Network for image classification
#The network uses 4 convolutional layers and 2 fully connected layers
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




#This class handles prediction using a trained CNN model
#It loads the model weights and predicts the top-k classes for an input image
class CNNPredictor:
    def __init__(self, model_path, classes_path):
        self.model_path = model_path
        self.classes_path = classes_path
        self.img_size = 128

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

        model = CNN(num_classes).to(device)
        model.load_state_dict(torch.load(self.model_path, map_location=device))
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


