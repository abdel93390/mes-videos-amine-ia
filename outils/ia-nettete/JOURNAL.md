# Journal de l'IA de netteté

## v1 — 28/11/2026 (pub MYBEET → Betalia, 3D animée, 360x640 → 1080x1920)
- Revue seconde par seconde de la version 1080 « lanczos » : environ 30 % de petits détails perdus par rapport à l'original (87 % gardés après l'agrandissement + débruitage, 82 % après le rendu, 70 % après la compression finale à 98 Mo).
- Essai sur 3 extraits de 5 s (gros plan du garçon, globules, chantier) : comparaison « actuelle / IA animation / IA générale » envoyée à l'élève. Générale = la plus nette (échafaudage, briques) ; animation = plus lisse. L'élève a choisi la générale.
- Vitesse : 2,52 s/image (général) et 1,40 s/image (animation) en float32 ; channels_last : 1,61 s ; **bfloat16 + channels_last : 0,49 s** (processeur avec AMX). 10 h 30 → environ 2 h 15 pour 8 min.
- Outil rangé ici (installer.sh, sr.py, agrandir.py), testé depuis le dépôt sur 1 s de vidéo (30 images, 1080x1920).
- Vidéo entière (MYBEET, 15 083 images) le 28/11 : agrandissement IA 1 h 48 (6 476 s, 0,43 s/image hors essais), rendu.py en 1080 : 13 min (machine libre), contrôle et comparaison : 7 min.
- Résultat : détails (variance du laplacien, ramenée à 360x640, bandeau exclu) **3,2 fois ceux de l'original** (médiane), contre 0,9 pour la version lanczos ; 5 secondes sur 503 sous 0,9 (écrans noirs, photos). Aucune trace d'origine ni écart anormal.
- Fichier final crf 20 : 303 Mo pour 8 min 23 (4,7 Mbit/s : l'IA ajoute du détail, donc plus lourd que les 200 Mo prévus). Envoyé tel quel dans la conversation, sans problème ; la comparaison 3 vidéos (crf 22, plafond 2 500k) : 158 Mo.
- Avis de l'élève sur l'extrait de 30 s : « c'est parfait » → IA de netteté par défaut (MES-REGLES.md).
