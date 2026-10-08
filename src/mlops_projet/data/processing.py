import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt 




# Import des fonctions Data Processing

def pretraitement(exemple_pour_map):

  new_cells = np.zeros((9,9))

  for i in range(9):
    for j in range(9):
      if exemple_pour_map['cells'][i][j][0] != 0:

        new_cells[i][j] = int(np.nonzero(exemple_pour_map['cells'][i][j])[0][1])

      else:
        new_cells[i][j] = 0

  return {
      "cells" : new_cells.tolist()
  }



def crop_grille(exemple, size = 450):

  img = np.array(exemple['image'])


  trapeze = np.array(exemple['keypoints'], dtype = np.float32).reshape(4,2)
  carre = np.array([[0,0],
                      [0,size],
                      [size,size],
                      [size,0]],dtype = np.float32)
  matrice = cv2.getPerspectiveTransform(trapeze, carre)
  # transformation de l'image à partir de la matrice de transformation
  new_image = cv2.warpPerspective(img, matrice, (size,size))

  # On sauve la RAM colab , on repasse en mode PIL image compressée
  #new_image_pil = Image.fromarray(new_image)
  vignettes_pil = []
  marge = 5
  for i in range(0,size,size//9):
    for j in range(0,size, size//9):
      # ajout de la marge pour eviter d'avoir les bandes noirs dans les cases
      vignette = new_image[i + marge:i+size//9 - marge,j + marge:j+size//9 - marge] # [y:y_suivant, ..] pour PIL
      vignette_pil = Image.fromarray(vignette).resize((size//9, size//9))
      vignettes_pil.append(vignette_pil)

  etiquettes = np.array(exemple['cells']).reshape(81)
  return {
      'vignettes_pil' : vignettes_pil,
      'etiquettes' : etiquettes
  }


def traitement_dataset(dataset):
  # On force la désactivation du cache d'Hugging Face
  dataset = dataset.map(pretraitement, writer_batch_size = 50, load_from_cache_file=False)
  dataset_crop = dataset.map(crop_grille, writer_batch_size = 50, load_from_cache_file=False)
  return dataset_crop




def processing_inference(image, keypoints, size = 450):

  img = np.array(image)
  
  
  trapeze = np.array(keypoints, dtype = np.float32).reshape(4,2)
  carre = np.array([[0,0],
                        [0,size],
                        [size,size],
                        [size,0]],dtype = np.float32)
  matrice = cv2.getPerspectiveTransform(trapeze, carre)
  # transformation de l'image à partir de la matrice de transformation
  new_image = cv2.warpPerspective(img, matrice, (size,size))
  
    # On sauve la RAM colab , on repasse en mode PIL image compressée
    #new_image_pil = Image.fromarray(new_image)
  vignettes_pil = []
  marge = 5
  for i in range(0,size,size//9):
    for j in range(0,size, size//9):
      # ajout de la marge pour eviter d'avoir les bandes noirs dans les cases
      vignette = new_image[i + marge:i+size//9 - marge,j + marge:j+size//9 - marge] # [y:y_suivant, ..] pour PIL
      vignette_pil = Image.fromarray(vignette).resize((size//9, size//9))
      vignettes_pil.append(vignette_pil)
  
  
  return vignettes_pil


# Keypoints (code généré avec llm)
  
def ordonner_points(points_bruts):
    # Transformer la liste plate [x1, y1, x2, y2...] en matrice 4x2 : [[x1, y1], ...]
    pts = np.array(points_bruts).reshape(4, 2)
    
    # Créer un tableau vide pour stocker les 4 points dans le bon ordre
    rect = np.zeros((4, 2), dtype="float32")

    # 1. Haut-Gauche (Somme minimale) et Bas-Droite (Somme maximale)
    somme = pts.sum(axis=1)
    rect[0] = pts[np.argmin(somme)] # Haut-Gauche
    rect[2] = pts[np.argmax(somme)] # Bas-Droite

    # 2. Bas-Gauche (Différence y-x maximale) et Haut-Droite (Différence y-x minimale)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmax(diff)] # Bas-Gauche
    rect[3] = pts[np.argmin(diff)] # Haut-Droite

    # Aplatir le résultat pour qu'il corresponde exactement à ton format de keypoints
    return rect.flatten().astype(int).tolist()


def trouver_coins_sudoku(image_pil, afficher_debug=False):
    # 1. Convertir l'image PIL en format OpenCV (numpy array)
    img_cv2 = np.array(image_pil)
    
    # Si l'image est en RGB, on la passe en niveaux de gris pour l'analyse
    if len(img_cv2.shape) == 3:
        gris = cv2.cvtColor(img_cv2, cv2.COLOR_RGB2GRAY)
    else:
        gris = img_cv2
        
    # 2. Nettoyer l'image (réduire le bruit et accentuer les contrastes)
    flou = cv2.GaussianBlur(gris, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(flou, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # 3. Trouver les contours dans l'image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 4. Trier les contours par taille (le Sudoku est généralement le plus gros élément)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    grille_contour = None
    for contour in contours:
        # Simplifier le contour pour vérifier s'il a 4 coins
        perimetre = cv2.arcLength(contour, True)
        approximation = cv2.approxPolyDP(contour, 0.02 * perimetre, True)
        
        if len(approximation) == 4:
            grille_contour = approximation
            break
            
    # 5. Affichage visuel du test et extraction des coordonnées
    if grille_contour is not None:
        
        # BLOC D'AFFICHAGE POUR LE DEBUG
        if afficher_debug:
            # On fait une copie pour ne pas gâcher l'image originale
            img_test = img_cv2.copy()
            # Dessiner le contour en rouge (255, 0, 0) avec une épaisseur de 5 pixels
            cv2.drawContours(img_test, [grille_contour], -1, (255, 0, 0), 10)
            
            # Afficher le résultat
            plt.figure(figsize=(8, 8))
            plt.imshow(img_test)
            plt.title("Vérification : Contour du Sudoku détecté")
            plt.axis('off')
            plt.show()

        # CORRECTION : On extrait les points et on les ordonne avant de renvoyer
        points_desordonnes = grille_contour.reshape(-1).tolist()
        points_ordonnes = ordonner_points(points_desordonnes)
        
        return points_ordonnes
    else:
        raise ValueError("Impossible de trouver la grille de Sudoku sur cette image.")