from fastapi import FastAPI, UploadFile, File, Form 
import io
import json

from mlops_projet.data.processing import *
from mlops_projet.solveur.sudoku import *
from mlops_projet.models.resnet import *

import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import torch
import torchvision
from pathlib import Path

# init de l'API 
app = FastAPI(title = "API Solveur Sudoku")

# init du modèle
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ResNet().to(device)
chemin_poids = Path(__file__).parent / "weights" / "sudoku2.pth"
model.load_state_dict(torch.load(chemin_poids, map_location=torch.device('cpu')))
model.eval()

test_transform = torchvision.transforms.Compose([
    torchvision.transforms.Grayscale(num_output_channels = 1),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean = [0.5], std = [0.5])
])


# Definition de l'endpoint/route (éxécutée à chaque fois qu'une image est envoyée)
@app.post("/resoudre")
async def resoudre_sudoku(
    fichier: UploadFile = File(...),
    # on ajoute un paramètre pour recevoir les coins depuis le frontend
    coins: str = Form(None, description = "Coordonnées JSON des 4 coins")):


    # 1- Lire l'image envoyée sous forme de bytes
    image_bytes = await fichier.read()
    image = Image.open(io.BytesIO(image_bytes))

    # 2- correction photo : Orientation EXIF et transparence RGBA -> RGB
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")

    # 3- Automatiser keypoints
    #keypoints = trouver_coins_sudoku(image, afficher_debug = False) méthode temporaire
    keypoints = json.loads(coins)

    # 4 - Data processing
    vignette_pil = processing_inference(image, keypoints)
    vignette_tensor = torch.stack([test_transform(vign) for vign in vignette_pil]).to(device)

    # 5- Inférence
    with torch.no_grad():
        y_pred = model(vignette_tensor)
        probs = torch.softmax(y_pred, dim = 1)
        max_probs, preds = torch.max(probs, dim =1)

    seuil = 0.90
    cases_incertaines = []

    grille_initiale = np.zeros((9,9), dtype = int)
    for idx in range(81):
        i, j = idx // 9, idx % 9
        prediction = preds[idx].item()
        probabilite = max_probs[idx].item()

        if prediction != 0:
            if probabilite >= seuil:
                grille_initiale[i,j] = prediction 
            else:
                cases_incertaines.append({"ligne": i, "colonne": j, "probabilite": round(probabilite, 3) })


    # 6 Solveur
    
    est_valide = validité_grille(grille_initiale)

    # 6 valeur par defaut si la grille est invalide
    statut = "invalid"
    instructions = []
    difficulte = 0
    grille_finale = grille_initiale.tolist() # JSON natif préfère 

    if est_valide:

        grille_indices = np.broadcast_to(np.arange(1,10),(9,9,9)).copy()
        grille_resolue, _, difficulte, instructions = solveur(grille_initiale.copy(), grille_indices, False, True)

        grille_finale = grille_resolue.tolist()

        if np.count_nonzero(grille_resolue) == 81:
            statut = "resolue"
        else:
            statut = "incomplète"

   


    # 6 retour de l'API
    # On convertit les arrays numpy en listes python pour que FastAPI puisse générer du JSON
    return {
        "fichier_recu": fichier.filename,
        "statut": statut,
        "cases incertaines": cases_incertaines,
        "difficulte": str(difficulte),
        "Instructions": instructions,
        "grille_resolue": grille_finale
    }

