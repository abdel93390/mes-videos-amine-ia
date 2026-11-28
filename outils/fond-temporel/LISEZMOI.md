# Fond temporel : effacer les sous-titres avec le vrai fond des images voisines (fond fixe)

Écrit pour FB1464 (tableau noir, 720x1280) par une autre session le 27/11/2026, rangé ici le 28/11/2026.

## fond_temporel.py
Dans la bande des sous-titres, chaque pixel caché par le texte prend la valeur du même pixel dans l'image la plus proche du même plan (±240 images) où il n'est ni sous un sous-titre ni sous la main ; sinon la valeur Vmake (ou effaceur). Sur un fond fixe (tableau, mur), c'est le vrai fond : plus de « flous » qui bougent à chaque changement de sous-titre. Un fond fixe peut s'en passer de Vmake (0 crédit).
Usage : `python3 .../fond-temporel/fond_temporel.py src.mp4 clean_vmake.mp4 vmake_zones.json sortie.mp4`
**À adapter en haut du script** : `W, H` (taille), `Y0, Y1` (bande des sous-titres), `COUPES` (débuts de plans : `analyse.json` → `plans`), `FLACON` (plage et colonnes où un objet traverse la bande : on y garde Vmake). Les sous-titres sont repérés à leur ombre décalée de 3 px (`sous_titres()`).
Avant de livrer : vérifier image par image qu'aucun sous-titre d'origine ne reste dans la bande (`sous_titres()`).

## realigner_vmake.py
Vmake rend parfois une vidéo qui a perdu des images en cours de route (FB1464 : 20 images perdues réparties dans toute la vidéo). Ce script recale la sortie Vmake image par image sur la source.
Usage : `python3 .../fond-temporel/realigner_vmake.py src.mp4 vmake_original.mp4 clean_vmake.mp4`, puis `python3 amine/scripts/vmake.py travail/<REF> --existant`.
