import numpy as np

# 1.1
# test sur la validité de la grille
# aucune double sur une colonne, ligne, et carré (3*3)

# Séparé valide et complète pour que le backtracking marche avec une grille à trous
def validité_grille(grille):

  erreur = 0

  if  grille.shape != (9,9):
    erreur += 1


  for i in range(9):
    ligne = grille[i,:]
    ligne_original = ligne[ligne != 0]
    if len(np.unique(ligne_original)) != len(ligne_original):

      erreur += 1
      print(f"erreur ligne: {i}")


    colonne = grille[:,i]
    colonne_original = colonne[colonne != 0]
    if len(np.unique(colonne_original)) != len(colonne_original):

      erreur += 1
      print(f"erreur colonne: {i}")

  for i in range(0,9,3):
    for j in range(0,9,3):
      carre = grille[i:i+3,j:j+3]
      carre_original = carre[carre != 0]
      if len(np.unique(carre_original)) != len(carre_original):

        erreur += 1
        print(f"erreur à la case: ({i},{j})")


  if erreur != 0:
      return False
  else:
      return True



def grille_complete(grille):
  if np.count_nonzero(grille) == 81 and validité_grille(grille):
    return True
  else:
    return False


def solution_valide(grille):
  if grille_complete(grille):
    print("La solution est valide")
  else:
    print("La solution est fausse")


# Solveur Backtracking -> Fonction récursive

def backtracking(grille):

  for i in range(9):
    for j in range(9):
      if grille[i,j] == 0:

        for k in range(9):
          grille[i,j] = k + 1
          if validité_grille(grille):
            if backtracking(grille):
              return True


        grille[i,j] = 0
        return False


  return True

# 1.2
# Création d'un solveur de sudoku logique + backtracking

# méthodes les plus simples :
#    - Il reste une seule possibilité (ligne, colonne, carré)
#    - Un chiffre sur une ligne, colonne, carré elimine les indices possibles
#    - Paires nues

# méthodes moyennes:
#    - Paires cachées
#    - X-Wing


# creation des indices par case de la grille (9x9x9)
grille_indices = np.broadcast_to(np.arange(1,10),(9,9,9)).copy()
print(grille_indices.shape)



def retirer_indices(grille, grille_indices):
  # reconnaissance des lignes et colonnes
  for i in range(9):
    ligne_unique = np.unique(grille[i,:][grille[i,:] != 0])
    for r in ligne_unique:
      pos = np.where(grille[i,:] == r) # sup les indices des chiffres deja existant
      grille_indices[i,int(pos[0][0]),:] = 0
      grille_indices[i,:,int(r-1)] = 0

  for i in range(9): # colonne
    colonne_unique = np.unique(grille[:,i][grille[:,i] != 0])
    for r in colonne_unique:
      grille_indices[:,i,int(r-1)] = 0

  for i in range(0,9,3): # carré
    for j in range(0,9,3):
      carre_unique = np.unique(grille[i:i+3,j:j+3][grille[i:i+3,j:j+3] != 0])
      for r in carre_unique:
        for k in range(3):
          for l in range(3):
            grille_indices[k+i,l+j,int(r-1)] = 0

  return grille, grille_indices

  # Aperçu de la grille d'indices
  #print(grille_indices)




def methodes_solveur(grille, grille_indices, instruction_boolean = True):

  difficulté = 0 # evaluation de la difficulté du Sodoku
  instruction = []

  # Indice isolé par case
  for i in range(9):
    for j in range(9):
      if len(np.nonzero(grille_indices[i,j,:])[0]) == 1:
        grille[i,j] = np.nonzero(grille_indices[i,j,:])[0][0] + 1

        if instruction_boolean == True:
          print(f"seule possibilité pour ({i+1},{j+1}) est {np.nonzero(grille_indices[i,j,:])[0][0] + 1}")
          instruction.append(f"seule possibilité pour ({i+1},{j+1}) est {np.nonzero(grille_indices[i,j,:])[0][0] + 1}")

        grille_indices[i, j, :] = 0
        

  grille, grille_indices = retirer_indices(grille, grille_indices)


  # Indice isolé par ligne et colonne
  for i in range(9):
    for k in range(9):
      if len(np.nonzero(grille_indices[i,:,k])[0]) == 1:

        pos = np.where(grille_indices[i,:,k] == k+1)

        grille[i, int(pos[0][0])] = k+1

        if instruction_boolean == True:
          print(f"seul possibilité sur la ligne {i+1} à la colonne {pos[0][0]} est {k+1} ")
          instruction.append(f"seul possibilité sur la ligne {i+1} à la colonne {pos[0][0]} est {k+1} ")

        grille_indices[i,:,k] = 0
        grille_indices[i,int(pos[0][0]),:] = 0
        

        grille, grille_indices = retirer_indices(grille, grille_indices)

      if len(np.nonzero(grille_indices[:,i,k])[0]) == 1:
        pos = np.where(grille_indices[:,i,k] == k+1)

        grille[int(pos[0][0]), i] = k+1

        if instruction_boolean == True:
          print(f"seul possibilité sur la colonne {i+1} à la ligne {pos[0][0]}  est {k+1} ")
          instruction.append(f"seul possibilité sur la colonne {i+1} à la ligne {pos[0][0]}  est {k+1} ")

        grille_indices[:,i,k] = 0
        grille_indices[int(pos[0][0]),i,:] = 0
        

        grille, grille_indices = retirer_indices(grille, grille_indices)




  # Indice isolé dans un carré
  for i in range(0,9,3):
    for j in range(0,9,3):
      for k in range(9):

        if len(np.nonzero(grille_indices[i:i+3, j:j+3, k])[0]) == 1:

          pos = np.where(grille_indices[i:i+3,j:j+3,k] == k+1)
          grille[i + int(pos[0][0]),j + int(pos[1][0])] = k + 1

          if instruction_boolean == True:
          
            print(f"seule possibilité pour le carré ({i+1},{j+1}) est {k + 1}")
            instruction.append(f"seule possibilité pour le carré ({i+1},{j+1}) est {k + 1}")
            

          grille_indices[i + int(pos[0][0]),j + int(pos[1][0]), :] = 0
          

          grille, grille_indices = retirer_indices(grille, grille_indices)



  # 2 indices uniques sur une ligne / colonne / carré

  # ligne et colonne -> supprime les indices dans le carré
  paires_ligne = []
  paires_col = []
  info_ligne = []
  info_col = []
  info_ligne_k = []
  info_col_k = []
  for i in range(9):
    for k in range(9):

      # Lignes
      # Si 2 candidats (Paire)
      if len(np.nonzero(grille_indices[i,:,k])[0]) == 2:
        pos = np.where(grille_indices[i,:,k])[0]
        paires_ligne.append(pos)
        info_ligne_k.append(k)
        info_ligne.append(i)

        if pos[0] // 3 == pos[1] // 3:

          grille_indices[(i // 3) * 3: (i // 3) * 3 + 3, (pos[0]//3)*3:(pos[0]//3)*3 + 3, k] = 0
          grille_indices[i,pos[0],k] = k + 1
          grille_indices[i,pos[1],k] = k + 1

      # si 3 candidats (Triplet)
      elif len(np.nonzero(grille_indices[i,:,k])[0]) == 3:
        pos = np.where(grille_indices[i,:,k])[0]
        # On n'ajoute pas aux listes X-Wing !
        if pos[0] // 3 == pos[1] // 3 == pos[2] // 3: # Si dans le même carré
          grille_indices[(i // 3) * 3: (i // 3) * 3 + 3, (pos[0]//3)*3:(pos[0]//3)*3 + 3, k] = 0
          grille_indices[i,pos[0],k] = k + 1
          grille_indices[i,pos[1],k] = k + 1
          grille_indices[i,pos[2],k] = k + 1

      # colonnes
      # si 2 candidats (Paire)
      if len(np.nonzero(grille_indices[:,i,k])[0]) == 2:
        pos = np.where(grille_indices[:,i,k])[0]
        paires_col.append(pos)
        info_col_k.append(k)
        info_col.append(i)
        if pos[0] // 3 == pos[1] // 3:

          grille_indices[(pos[0]//3)*3:(pos[0]//3)*3 + 3,(i // 3) * 3: (i // 3) * 3 + 3, k] = 0
          grille_indices[pos[0],i,k] = k + 1
          grille_indices[pos[1],i,k] = k + 1

      # si 3 candidats (Triplet)
      if len(np.nonzero(grille_indices[:,i,k])[0]) == 3:
        pos = np.where(grille_indices[:,i,k])[0]
        if pos[0] // 3 == pos[1] // 3 == pos[2] // 3: # Si dans le même carré
          grille_indices[(pos[0]//3)*3:(pos[0]//3)*3 + 3,(i // 3) * 3: (i // 3) * 3 + 3, k] = 0
          grille_indices[pos[0],i,k] = k + 1
          grille_indices[pos[1],i,k] = k + 1
          grille_indices[pos[2],i,k] = k + 1


  # Paires Nues Lignes
  for i in range(9):
    for j1 in range(9):
      candidat1 = np.nonzero(grille_indices[i,j1,:])[0]

      if len(candidat1) == 2:

        for j2 in range(j1+1,9):
          candidat2 = np.nonzero(grille_indices[i,j2,:])[0]

          if len(candidat2) == 2 and np.array_equal(candidat1, candidat2):

            for j3 in range(9):

              if j3 != j1 and j3 != j2:
              
                grille_indices[i,j3,candidat1[0]] = 0
                grille_indices[i,j3,candidat1[1]] = 0

            if instruction_boolean == True:
                        
              print(f"Paire nue sur la ligne {i} aux colonnes {j1} et {j2}. Candidats: {candidat1 + 1}")
              instruction.append(f"Paire nue sur la ligne {i} aux colonnes {j1} et {j2}. Candidats: {candidat1 + 1}")
        

  # Paires Nues colonnes
  for i in range(9):
    for j1 in range(9):
      candidat1 = np.nonzero(grille_indices[j1,i,:])[0]

      if len(candidat1) == 2:

        for j2 in range(j1+1,9):
          candidat2 = np.nonzero(grille_indices[j2,i,:])[0]

          if len(candidat2) == 2 and np.array_equal(candidat1, candidat2):

            for j3 in range(9):

              if j3 != j1 and j3 != j2:
              
                grille_indices[j3,i,candidat1[0]] = 0
                grille_indices[j3,i,candidat1[1]] = 0

            if instruction_boolean == True:

              print(f"Paire nue sur la ligne {i} aux colonnes {j1} et {j2}. Candidats: {candidat1 + 1}")
              instruction.append(f"Paire nue sur la ligne {i} aux colonnes {j1} et {j2}. Candidats: {candidat1 + 1}")

  # Paires nues carrées
  for i in range(0, 9, 3):
    for j in range(0, 9, 3):
        # On liste les coordonnées des 9 cases du carré pour faciliter la double boucle
        cases_carre = [(i + k // 3, j + k % 3) for k in range(9)]
        
        for index1 in range(9):
            r1, c1 = cases_carre[index1]
            candidat1 = np.nonzero(grille_indices[r1, c1, :])[0]
            
            if len(candidat1) == 2:
                for index2 in range(index1 + 1, 9):
                    r2, c2 = cases_carre[index2]
                    candidat2 = np.nonzero(grille_indices[r2, c2, :])[0]
                    
                    if len(candidat2) == 2 and np.array_equal(candidat1, candidat2):
                        # Paire trouvée dans le carré, on nettoie les autres cases de ce carré
                        for index3 in range(9):
                            if index3 != index1 and index3 != index2:
                                r3, c3 = cases_carre[index3]
                                grille_indices[r3, c3, candidat1[0]] = 0
                                grille_indices[r3, c3, candidat1[1]] = 0
                        if instruction_boolean == True:
                        
                            print(f"Paire nue dans le carré ({i//3},{j//3}) aux cases ({r1},{c1}) et ({r2},{c2}). Candidats: {candidat1 + 1}")
                            instruction.append(f"Paire nue dans le carré ({i//3},{j//3}) aux cases ({r1},{c1}) et ({r2},{c2}). Candidats: {candidat1 + 1}")
        

  # Paires cachées
  # Lignes
  compte_m = 0
  compte_n = 0
  for m in paires_ligne:
    compte_m += 1
    compte_n = 0
    for n in paires_ligne:
      compte_n += 1
      if np.array_equal(m,n) and compte_m != compte_n and info_ligne[compte_m - 1] == info_ligne[compte_n - 1]:

        grille_indices[info_ligne[compte_m-1],m[0],:]    = 0
        grille_indices[info_ligne[compte_m-1],m[0],info_ligne_k[compte_m-1]] = info_ligne_k[compte_m-1] +1
        grille_indices[info_ligne[compte_m-1],m[0],info_ligne_k[compte_n-1]] = info_ligne_k[compte_n-1] +1
        grille_indices[info_ligne[compte_m-1],m[1],:]    = 0
        grille_indices[info_ligne[compte_m-1],m[1],info_ligne_k[compte_m-1]] = info_ligne_k[compte_m-1] +1
        grille_indices[info_ligne[compte_m-1],m[1],info_ligne_k[compte_n-1]] = info_ligne_k[compte_n-1] +1

        #difficulté += 1

      # X-Wing
      if np.array_equal(m,n) and compte_m != compte_n and info_ligne_k[compte_m -1] == info_ligne_k[compte_n -1] and info_ligne[compte_m -1] != info_ligne[compte_n -1]:
        grille_indices[:,m[0], info_ligne_k[compte_m -1]] = 0
        grille_indices[info_ligne[compte_m-1],m[0],info_ligne_k[compte_m-1]] = info_ligne_k[compte_m-1] +1
        grille_indices[info_ligne[compte_n-1],m[0],info_ligne_k[compte_n-1]] = info_ligne_k[compte_n-1] +1
        grille_indices[:,m[1], info_ligne_k[compte_m -1]] = 0
        grille_indices[info_ligne[compte_m-1],m[1],info_ligne_k[compte_m-1]] = info_ligne_k[compte_m-1] +1
        grille_indices[info_ligne[compte_n-1],m[1],info_ligne_k[compte_n-1]] = info_ligne_k[compte_n-1] +1

        difficulté += 1

  grille, grille_indices = retirer_indices(grille, grille_indices)


  # Colonnes
  compte_m = 0
  compte_n = 0
  for m in paires_col:
    compte_m += 1
    compte_n = 0
    for n in paires_col:
      compte_n += 1
      if np.array_equal(m,n) and compte_m != compte_n and info_col[compte_m - 1] == info_col[compte_n - 1]:

        grille_indices[m[0],info_col[compte_m-1],:]    = 0
        grille_indices[m[0],info_col[compte_m-1],info_col_k[compte_m-1]] = info_col_k[compte_m-1] +1
        grille_indices[m[0],info_col[compte_m-1],info_col_k[compte_n-1]] = info_col_k[compte_n-1] +1
        grille_indices[m[1],info_col[compte_m-1],:]    = 0
        grille_indices[m[1],info_col[compte_m-1],info_col_k[compte_m-1]] = info_col_k[compte_m-1] +1
        grille_indices[m[1],info_col[compte_m-1],info_col_k[compte_n-1]] = info_col_k[compte_n-1] +1

        #difficulté += 1

      # X-Wing
      if np.array_equal(m,n) and compte_m < compte_n and info_col_k[compte_m -1] == info_col_k[compte_n -1] and info_col[compte_m -1] != info_col[compte_n -1]:
        grille_indices[m[0],:, info_col_k[compte_m -1]] = 0
        grille_indices[m[0],info_col[compte_m-1],info_col_k[compte_m-1]] = info_col_k[compte_m-1] +1
        grille_indices[m[0],info_col[compte_n-1],info_col_k[compte_n-1]] = info_col_k[compte_n-1] +1
        grille_indices[m[1],:, info_col_k[compte_m -1]] = 0
        grille_indices[m[1],info_col[compte_m-1],info_col_k[compte_m-1]] = info_col_k[compte_m-1] +1
        grille_indices[m[1],info_col[compte_n-1],info_col_k[compte_n-1]] = info_col_k[compte_n-1] +1
        print(f"X-Wing indice {m[0]}")
        difficulté += 1



  # 2 ou 3 indices uniques dans un carré - > élimine les autres candidats possibles sur ligne / colonne
  for i in range(0,9,3):
    for j in range(0,9,3):
      for k in range(9):

        # 2 indices
        if len(np.nonzero(grille_indices[i:i+3, j:j+3, k])[0]) == 2:
          pos = np.where(grille_indices[i:i+3,j:j+3,k] == k+1)

          if pos[0][0] == pos[0][1] : # même ligne
            grille_indices[i + int(pos[0][0]) , :j , k] = 0
            grille_indices[i + int(pos[0][0]) , j+3:, k] = 0

          elif pos[1][0] == pos[1][1]: #même colonne
            grille_indices[:i, j+ int(pos[1][0]) , k] = 0
            grille_indices[i+3: ,j+ int(pos[1][0]), k] = 0

        # 3 indices 
        if len(np.nonzero(grille_indices[i:i+3, j:j+3, k])[0]) == 3:
          pos = np.where(grille_indices[i:i+3,j:j+3,k] == k+1)
       
          if pos[0][0] == pos[0][1] == pos[0][2]: # alignés sur la même ligne
            grille_indices[i + int(pos[0][0]) , :j , k] = 0
            grille_indices[i + int(pos[0][0]) , j+3:, k] = 0
          elif pos[1][0] == pos[1][1] == pos[1][2]: # alignés sur la même colonne
            grille_indices[:i, j+ int(pos[1][0]) , k] = 0
            grille_indices[i+3: ,j+ int(pos[1][0]), k] = 0



  return grille, grille_indices, difficulté, instruction



def solveur(grille, grille_indices, utiliser_backtracking = False, print_difficulté = False):
  # boucle qui utilise les methodes de résolutions de Sudoku
  liste_grilles_indices = []
  liste_grilles = []
  liste_difficulté = []
  difficulté = 0
  instructions = []
  n = 0
  if validité_grille(grille) == True:
    while np.count_nonzero(grille) < 81:
      grille, grille_indices = retirer_indices(grille, grille_indices)
      grille, grille_indices, difficulté, instruction = methodes_solveur(grille, grille_indices)
      liste_grilles_indices.append(grille_indices.copy())
      liste_grilles.append(grille.copy())
      liste_difficulté.append(difficulté)

      instructions.extend(instruction)
      n += 1
      # pas de changement

      if n >= 2:
        if np.array_equal(liste_grilles_indices[n - 1], liste_grilles_indices[n - 2]) and np.array_equal(liste_grilles[n - 1], liste_grilles[n - 2]):
          #print("les méthodes classiques ne suffisent pas")
          if utiliser_backtracking == True:
            # rajout de backtracking pour finir le Sudoku
            succes = backtracking(grille)
            liste_difficulté.append(100) # Extreme
            if succes == False:
              print("Il y a eu une erreur avec le solveur logique")
              break

          break
    if print_difficulté == True:
      difficulté = np.sum(liste_difficulté)
      if difficulté <= 8 :
          print("Sudoku niveau : facile")
      elif difficulté <= 16: # fixé approximativement
          print("Sudoku niveau : moyen")
      else:
          print("Sudoku niveau : difficile")

    return grille, grille_indices, difficulté, instructions

  else: 
    print("La grille n'est pas valide")
    return grille, grille_indices, difficulté, instructions 





