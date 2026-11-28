# Pubs « tableau noir » : mots écrits à la craie et étiquette du flacon refaits en français

Écrit pour la pub Betalia FB1464 (animation à la craie, 720x1280, 3 min 28) par une autre session, le 27/11/2026, rangé ici le 28/11/2026.
`craie_flacon.py` remplace, image par image :
- les mots écrits à la craie (texte d'origine → texte français, écrit au même rythme que la main, sans recouvrir la main ni le bras) ;
- l'étiquette du flacon concurrent par la photo de la fiche produit de l'élève (`outils/photos-produit/recuperer.py`).

Usage : `python3 /home/user/mes-videos-amine-ia/outils/craie-tableau/craie_flacon.py reglages.json src.mp4:src_fr.mp4 clean_vmake.mp4:clean_vmake_fr.mp4`
(les masques sont calculés sur la première vidéo et appliqués à toutes ; vidéos alignées image par image).
Réglages : voir `exemple_FB1464.json` (police, mots avec plan, rectangle, texte français, flacon). Police « craie » : `outils/polices/ArchitectsDaughter-Regular.ttf` (OFL).

À adapter avant usage : `W, H = 720, 1280` en haut du script (taille de la vidéo). Pas encore re-testé depuis le dépôt sur une autre vidéo : noter le premier essai dans `JOURNAL.md`.
