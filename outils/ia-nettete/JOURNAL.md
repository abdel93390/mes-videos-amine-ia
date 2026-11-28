# Journal de l'IA de netteté

## v1 — 28/11/2026 (pub MYBEET → Betalia, 3D animée, 360x640 → 1080x1920)
- Revue seconde par seconde de la version 1080 « lanczos » : environ 30 % de petits détails perdus par rapport à l'original (87 % gardés après l'agrandissement + débruitage, 82 % après le rendu, 70 % après la compression finale à 98 Mo).
- Essai sur 3 extraits de 5 s (gros plan du garçon, globules, chantier) : comparaison « actuelle / IA animation / IA générale » envoyée à l'élève. Générale = la plus nette (échafaudage, briques) ; animation = plus lisse. L'élève a choisi la générale.
- Vitesse : 2,52 s/image (général) et 1,40 s/image (animation) en float32 ; channels_last : 1,61 s ; **bfloat16 + channels_last : 0,49 s** (processeur avec AMX). 10 h 30 → environ 2 h 15 pour 8 min.
- Outil rangé ici (installer.sh, sr.py, agrandir.py), testé depuis le dépôt sur 1 s de vidéo (30 images, 1080x1920).
