# Textes à l'écran refaits en français (sans Vmake, 0 crédit)

Polices : `bash /home/user/mes-videos-amine-ia/outils/polices/installer.sh` d'abord (Poppins Bold, Permanent Marker).

## Post-it écrit au feutre — `postit.py`
`python3 .../textes-ecran/postit.py <entree.mp4> <sortie.mp4> reglages.json`
Suit le post-it jaune image par image (même s'il bouge ou si la caméra zoome), refait le fond du papier, garde l'aimant et la main, et écrit le texte en Permanent Marker.
À lancer sur la base vidéo (`src.mp4`, en gardant `src_origine.mp4`), avant le rendu. Exemple de réglages dans le haut du script.
Post-it petit (texte de moins de 8 px) ou très penché : `"effacer_seul": true` (texte effacé, rien de réécrit), ou remplacer le plan par des images voisines.

## Badges jaunes arrondis — `badges_jaunes.py`
`python3 .../textes-ecran/badges_jaunes.py travail/<REF> badges.json [--echelle 3]` : repère chaque badge image par image (apparition animée comprise) et le réécrit (patchs dans la fiche).
Trouver les tranches de hauteur (`lignes_y`) sur une capture zoomée de la fin de la vidéo.

## Écran titre noir — `ecrans_titres.py`
`python3 .../textes-ecran/ecrans_titres.py travail/<REF> titres.json [--echelle 3]` : texte blanc sur fond noir (ex. « TRZY TYGODNIE PÓŹNIEJ » → « TROIS SEMAINES PLUS TARD »).
Passer les mêmes plages à `outils/bandeau-blanc/bandeau.py --sans …` : pas de bandeau sur un écran titre.

Ordre conseillé : post-it (base vidéo) → photos produit (`outils/photos-produit/`) → voix → bandeau → badges, écrans titres → rendu.
