#!hf download Lexski/sudoku-image-recognition --repo-type dataset --local-dir ./sudoku_dataset

import numpy as np
import matplotlib.pyplot as plt
import torch as torch



# Résultats reproductible
random_state = 42

# Calcul sur GPU si disponible
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Importation du Dataset
from datasets import load_dataset

dataset = load_dataset("sudoku_dataset")
print(dataset)

# Importation des méthodes de processing.py


from mlops_projet.data.processing import *

dataset_crop = traitement_dataset(dataset)
print(dataset_crop)


# 1 CustomDataset

from torch.utils.data import Dataset, DataLoader
import torchvision

class CustomDataset(Dataset):

  def __init__(self, dataset, transforms = None):
    self.data = dataset
    self.vignettes = []
    self.labels = []
    self.transforms = transforms


    for i in self.data:
      self.vignettes.extend(i['vignettes_pil'])
      self.labels.extend(i['etiquettes'])


  def __len__(self):
    return len(self.vignettes)

  def __getitem__(self,idx):
    vignette = self.vignettes[idx]
    label = self.labels[idx]

    if self.transforms :
      vignette = self.transforms(vignette)


    return vignette, int(label)

# Data Transform
train_transform = torchvision.transforms.Compose([
    torchvision.transforms.Grayscale(num_output_channels = 1),
    # Ajout de fill = 255 pour que le fond généré soit blanc
    torchvision.transforms.RandomRotation(degrees = 10, fill = 255),
    torchvision.transforms.RandomAffine(degrees = 0.1, translate = (0.1,0.1), fill = 255), # on remarque que les erreurs sont dus à cases mal centrées
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean = [0.5], std = [0.5])
    ])

test_transform = torchvision.transforms.Compose([
    torchvision.transforms.Grayscale(num_output_channels = 1),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean = [0.5], std = [0.5])
])

# Instance du dataset
train_set = CustomDataset(dataset_crop['train'], transforms = train_transform)
val_set = CustomDataset(dataset_crop['validation'], transforms = test_transform)
test_set = CustomDataset(dataset_crop['test'], transforms = test_transform)

vign, label = train_set[137]
plt.imshow(vign.squeeze(), cmap = 'gray')
plt.title(label)

# Creation des Batchs -> DataLoader
train_loader = DataLoader(train_set, batch_size = 32, shuffle = True)
valid_loader = DataLoader(val_set, batch_size = 32, shuffle = False)
test_loader = DataLoader(test_set, batch_size = 32, shuffle = False)

