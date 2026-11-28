# Journal du rendu 1080

## v1 — 27-28/11/2026 (MYBEET, 360x640 → 1080x1920)
- Agrandir la vidéo finie (premier essai) rendait sous-titres et badges flous. Rendre directement en 1080 (base agrandie, patchs ×3, photos natives) : texte net.
- Rendu 1080 avec rendu.py : environ 35 min pour 8 min 23 (4 cœurs). Fichier crf 19 : 292 Mo ; recompressé à 98 Mo (1,45 Mbit/s) → 15 % de netteté perdue. Désormais crf 20 dans rendu.py et plus de recompression.
- Revue seconde par seconde : aucun défaut visible (texte d'origine, taches, plans remplacés) ; seule la finesse était en dessous de l'original → outils/ia-nettete.
- Comparaison « concurrent | notre version » côte à côte envoyée à l'élève (environ 99 Mo pour 8 min, 2 parties).
