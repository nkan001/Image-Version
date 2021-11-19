from PIL import Image
import numpy as np
import os
import json
import random
import torch
from torch.utils.data import Dataset
from torchvision import transforms
import pandas as pd
import random
random.seed(42)
torch.manual_seed(42)

class RecipeDataset(Dataset):
    def __init__(self, image_size=224, data_dir="dataset", name = "train"):
        self.image_size = image_size
        self.examples = pd.read_csv(os.path.join(data_dir, f"{name}.csv"))
            
        self.mean = [0.485, 0.456, 0.406] # taken from imagenet
        self.std= [0.229, 0.224, 0.225] # taken from imagenet
        
        if name =="train":
            self.transform = transforms.Compose([
                transforms.RandomResizedCrop((self.image_size, self.image_size)), # crop random area and aspect ratio, then resize to 224x224 https://pytorch.org/vision/stable/transforms.html#torchvision.transforms.RandomResizedCrop
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.2),
                transforms.ToTensor(),  # torchvision.transforms.ToTensor changes the (-1, H, W, C) PIL Image to channels first which is expected by the model
                transforms.Normalize(self.mean, self.std),
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize((int(self.image_size / 0.875), int(self.image_size / 0.875))),  
                transforms.CenterCrop(self.image_size),
                # TODO not sure what 0.875 and centercrop is for; why can't we just do the same as the training set?
                transforms.ToTensor(),
                transforms.Normalize(self.mean, self.std),
            ])

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        example = self.examples.iloc[i]
        # print("EXAMPLE", example.id)
        img = Image.open(example.filename)
        # print("IN RECIPEDATASET GETITEM:", np.array(img).shape)
        while np.array(img).shape[-1] != 3:  # TODO: not an RGB image; skip (i think this is not a very good workaround haha)
            print("SKIPPING IMAGE IN RECIPEDATASET.PY:", i)
            i += 1
            example = self.examples.iloc[i]
            img = Image.open(example.filename)
        img = self.transform(img)
        label = example.maincat
        return img, int(label), example.id
