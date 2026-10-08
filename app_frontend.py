import streamlit as st
import requests 
from PIL import Image, ImageDraw
import io
import json
from streamlit_image_coordinates import streamlit_image_coordinates

st.title("Solveur de Sudoku maison")
st.write("Télécharge une image de Sudoku")

# 1 Widget pour uploader l'image 
fichier_upload = st.file_uploader("Choisir une image", type=["jpg","jpeg","png"])

if fichier_upload is not None:

    # 2 Affichage de l'image
    image = Image.open(fichier_upload)

    # on reduit la taille de l'image
    image.thumbnail((600,600))
    st.write("Ajuste le rectangle autour de la grille :")

    # si le coffre 'coins' n'existe pas encore on le crée vide
    if 'coins' not in st.session_state:
        st.session_state['coins'] = []

    # on dessine un petit point rouge sur l'image pour chaque coin
    image_dessin = image.copy()
    draw = ImageDraw.Draw(image_dessin)
    for x,y in st.session_state['coins']:
        draw.ellipse((x-5,y-5,x+5,y+5), fill ='red')

    # l'outil de clic
    clic = streamlit_image_coordinates(image_dessin, key="points")

    # Si l'utilisateur clique sur l'image, on récupère sur x et y
    if clic is not None:
        point = [clic['x'], clic['y']]

    # Si on a moins de 4 points, on ajoute le clic dans la mémoire
        if point not in st.session_state['coins'] and len(st.session_state['coins']) < 4:
            st.session_state['coins'].append(point)
            st.rerun() # On force la page à se recharger pour afficher le point rouge

    # Un bouton tout simple pour vider la mémoire si on a mal cliqué
    if st.button("Effacer les clics"):
        st.session_state['coins'] = []
        st.rerun()

    # 3. ENVOI À L'API (apparaît seulement quand on a nos 4 points)
    if len(st.session_state['coins']) == 4:
        st.success("4 coins validés !")
        
        if st.button("Résoudre le Sudoku"):
            with st.spinner("L'API travaille..."):

                # CORRECTION 1 : Tri des points pour OpenCV (TL, BL, BR, TR)
                pts = st.session_state['coins']
                tl = min(pts, key=lambda p: p[0] + p[1]) # Haut-Gauche
                br = max(pts, key=lambda p: p[0] + p[1]) # Bas-Droite
                bl = max(pts, key=lambda p: p[1] - p[0]) # Bas-Gauche
                tr = min(pts, key=lambda p: p[1] - p[0]) # Haut-Droite
                coins_ordonnes = [tl, bl, br, tr]

                # CORRECTION 2 : Sauvegarde de l'image REDIMENSIONNÉE en mémoire
                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                image_bytes = buf.getvalue()

                # On prépare le fichier et les 4 points ordonnés à envoyer
                fichiers = {"fichier": ("image_resize.jpg", image_bytes, "image/jpeg")}
                donnees = {"coins": json.dumps(coins_ordonnes)}

                # Envoi au backend
                reponse = requests.post("http://127.0.0.1:8000/resoudre", files=fichiers, data=donnees)

                # 4. AFFICHAGE DU RÉSULTAT
                if reponse.status_code == 200:
                    data = reponse.json()
                    st.success(f"Statut : {data['statut']}")

                    if data["Instructions"]:
                        with st.expander("Voir les étapes logiques"):
                            for etape in data["Instructions"]:
                                st.write(f"- {etape}")

                    st.write("**Grille finale :**")
                    lignes = [" ".join(str(case) for case in ligne) for ligne in data["grille_resolue"]]
                    st.code("\n".join(lignes), language="text")

                else:
                    st.error("Erreur lors de la communication avec l'API.")