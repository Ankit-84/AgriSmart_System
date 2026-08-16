# utils/models.py
import os
import joblib
import torch
import torchvision.models as models
import torchvision.transforms as transforms

def load_crop_classifier():
    """Loads the tabular crop recommendation model (.pkl)."""
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "crop_recommendation_model.pkl")
    if os.path.exists(model_path):
        try:
            return joblib.load(model_path)
        except Exception as e:
            print(f"Error loading tabular model: {e}")
            return None
    return None

def load_vision_model():
    """
    Loads your locally downloaded pre-trained plant disease vision model (.pth).
    Falls back to a standard architecture if the local file isn't present.
    """
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "plant_disease_model.bin")
    
    # Initialize the base structural framework (e.g., ResNet50)
    model = models.resnet50()
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, 38) # Standard 38 PlantVillage classes
    
    if os.path.exists(model_path):
        try:
            
            model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            print("Successfully loaded local plant disease weights.")
        except Exception as e:
            print(f"Local weights file found but failed to parse: {e}. Using base initialization.")
    else:
        print(f"No local weight file discovered at {model_path}. Using uninitialized structural model.")
        
    model.eval()
    return model

def get_image_transform():
    """Standard transformations required to prepare images for the vision tensor layer."""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406], 
            std=[0.229, 0.224, 0.225]
        )
    ])