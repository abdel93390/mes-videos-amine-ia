# Journal du fond réel

## v1 — 28/11/2026 (pub MYBEET → Betalia, mini-film IA, 337 s)
- Version 2 avec LaMa seul (le fond inventé image par image) : l'élève voyait « du flou à côté de chaque sous-titre » (taches qui bougent, faux collier sur la femme).
- Fond réel : carrés de 6 px (12 px en HD) repris dans l'image la plus proche du même plan où le carré est libre, si le voisinage (5 px autour) diffère de moins de 9 niveaux ; décalage de lumière corrigé. Sur les 30 premières secondes : 61 % des carrés avec le vrai fond, 39 % LaMa. Plus de faux détails, beaucoup moins de flou.
- Masque des lettres : blanc > 185 dont le pixel décalé de 2 px (4 px en HD) en bas à droite est plus sombre de 40, + lettres entières, + ombre sombre autour, élargi de 3 px (6 px en HD). Moins large, l'ombre des lettres restait (lettres fantômes noires).
- Détection des boîtes (detecte_st.py) sur la 360x640 : 6 024 images sous-titrées sur 10 110 ; 1 fausse boîte (petit objet blanc au bord) écartée : garder les boîtes dont le centre est à moins de 45 px du milieu et dans la bande 420-485.
- Source HD fournie par l'élève (720x1280, mêmes 10 110 images) : boîtes 360 multipliées par 2, `--echelle 2`.
