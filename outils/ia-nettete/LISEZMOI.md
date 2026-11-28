# IA de netteté (Real-ESRGAN) : rendre une vidéo plus nette et plus grande, gratuitement

À quoi ça sert : les pubs récupérées sont souvent petites (360x640) et floues. Agrandir simplement (lanczos) donne une image molle ; cette IA recrée de vrais détails (bords, textures). 0 €, 0 crédit, sur la machine de la session (pas besoin de carte graphique).

Licence : Real-ESRGAN, BSD-3 (usage commercial autorisé, donc les pubs). Modèles téléchargés depuis les « releases » GitHub de xinntao/Real-ESRGAN.

## Utilisation
1. Installer (environ 3 min, une fois par session) :
   `bash /home/user/mes-videos-amine-ia/outils/ia-nettete/installer.sh`
2. Agrandir la **base vidéo** (avant `rendu.py`, pour que sous-titres, badges et photos soient ensuite dessinés nets en 1080) :
   `~/.cache/sr/env/bin/python /home/user/mes-videos-amine-ia/outils/ia-nettete/agrandir.py travail/<REF>/src.mp4 <dossier 1080>/src.mp4 --taille 1080x1920`
   - `--modele general` (par défaut) : le plus net, conseillé pour la 3D et les vraies images ; `--modele anime` : plus lisse, 2 fois plus rapide (dessins animés plats).
   - `--debut 40 --duree 5` : essai sur un extrait. Toujours faire un essai et le montrer à l'élève avant la vidéo entière.
   - Reprise automatique : si la session coupe, relancer la même commande (morceaux de 1000 images dans `<sortie>_morceaux/`).
3. Ensuite, comme pour la version 1080 (MES-REGLES.md, « Qualité ») : `analyse.json` à 1080x1920, positions et tailles de la section `rendu` multipliées par l'échelle, `rendu.py`, et **une seule compression finale** (le `crf` de la fiche, 20 conseillé ; pas de recompression derrière).

## Temps de calcul (mesuré le 28/11/2026, processeur Xeon 4 cœurs de la session)
- Modèle général : 2,5 s par image en calcul normal, **0,5 s par image en bfloat16** (le script l'active seul si le processeur le permet : `amx_bf16` / `avx512_bf16` dans /proc/cpuinfo). Écart d'image invisible (0,16 sur 255).
- Vidéo de 8 min 23 (15 083 images) : environ 2 h 15 avec le modèle général, 1 h 10 avec le modèle animation.
- Ne pas lancer autre chose de lourd en même temps : tout ralentit (essai d'1 s : 57 s au lieu de 15 s pendant un autre calcul).
- Traiter 2 images à la fois n'accélère pas (essayé : plus lent).

## Pièges
- Ne pas recompresser plusieurs fois : sur MYBEET, la compression finale à 98 Mo (1,45 Mbit/s pour 8 min en 1080) faisait perdre 15 % de netteté, plus que l'agrandissement lui-même. Compter environ 300 Mo pour 8 min avec l'IA (crf 20), envoyés dans la conversation (pas GitHub, limité à 100 Mo).
- Le débruitage `hqdn3d` de la méthode 1080 simple efface un peu de texture : inutile avec l'IA.
