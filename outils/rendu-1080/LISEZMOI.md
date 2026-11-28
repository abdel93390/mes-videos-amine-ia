# Rendu en 1080x1920 et vidéo comparative

## Rendu 1080 (règle de l'élève : toujours 1080x1920, la meilleure version dès la 1re livraison)
1. Travailler normalement dans `travail/<REF>` (taille de la source).
2. `python3 /home/user/mes-videos-amine-ia/outils/rendu-1080/passer_en_1080.py travail/<REF> travail/<REF>_1080`
3. Base agrandie : `~/.cache/sr/env/bin/python .../outils/ia-nettete/agrandir.py travail/<REF>/src.mp4 travail/<REF>_1080/src.mp4` (IA, conseillé),
   puis les photos produit en 1080 natif (`outils/photos-produit/inserer.py`).
4. `python3 amine/scripts/rendu.py travail/<REF>_1080`, puis `cp travail/<REF>_1080/cues_final.json travail/<REF>_1080/cues.json` et `controle.py`.
5. Envoyer la vidéo telle quelle dans la conversation (une seule compression, environ 200 Mo pour 8 min).

## Vidéo comparative (demandée par l'élève)
`bash /home/user/mes-videos-amine-ia/outils/rendu-1080/comparer.sh comparaison.mp4 "CONCURRENT" source.mp4 "AVANT" v01.mp4 "APRÈS (IA)" v02.mp4`
2 ou 3 parties synchronisées, son de la dernière vidéo.

## Vérification seconde par seconde (MES-REGLES.md)
Mesurer la netteté (variance du laplacien) de chaque seconde, version traduite ramenée à la taille de l'original, bandeau exclu : sur MYBEET, 0,7 = 30 % de détails perdus (surtout la compression finale).
Puis une planche « original | traduit » par plan (image du milieu de chaque plan, 48 plans par planche) à regarder entièrement.
