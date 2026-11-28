# Bandeau blanc : cacher les sous-titres d'origine sans Vmake (0 crédit)

Un bandeau blanc fixe, à la place des sous-titres d'origine, avec la traduction en noir dedans. Validé par l'élève sur MYBEET (pub de 8 min 23, sous-titres karaoké blancs/jaunes sans fond).
À utiliser quand l'effaceur gratuit (`outils/effaceur/`) laisse du flou ou des restes, ou pour un test rapide (MES-REGLES.md).

## 1. Repérer les sous-titres d'origine (une fois par vidéo)
`python3 /home/user/mes-videos-amine-ia/outils/bandeau-blanc/detecter.py travail/<REF>` → `st_boites.json` (environ 40 s pour 8 min en 360x640).
`--bande 0.65,0.79` : bande de recherche en fraction de la hauteur (à adapter si les sous-titres sont ailleurs : regarder la planche d'analyse).
Texte blanc ou jaune à contour sombre seulement. Des objets clairs du décor sont parfois pris : sans conséquence (le bandeau a une largeur fixe).

## 2a. Test gratuit (voix d'origine + sous-titres français, aucun crédit)
Écrire `traduction.json` : `[["0-6", "Mon fils a appelé une ambulance pour moi,"], ["t120.3-121.5", "J'y suis allé."], ...]`
(`"i-j"` = numéros de mots dans `analyse.json` → `mots` ; `"tA-B"` = secondes, pour les passages que Whisper a sautés : lire les sous-titres à l'écran ; « | » force une coupure).
`python3 .../bandeau.py travail/<REF> --traduction traduction.json`, puis copier `full.wav` en `mix.wav` et lancer `rendu.py`.

## 2b. Version finale (après la voix : voix.py, enchainer.py, mix.py)
`python3 .../bandeau.py travail/<REF> [--echelle 3] [--sans 12205-12260,12635-12690]`
- Sous-titres tirés de l'alignement de la voix finale (mêmes mots que la voix), coupés en 1 ligne (2 si la phrase va trop vite), jamais sur un petit mot.
- `--echelle 3` : rendu en 1080x1920 d'une source 360x640 (positions et police multipliées : texte net).
- `--sans` : images où le bandeau ne doit jamais s'afficher (écrans titres noirs…).
- Le bandeau passe en 2 lignes de haut là où l'original a 2 lignes (sinon une ligne dépasse).
- Plans remplacés (`rendu.remplacements`) : la boîte de l'image donneuse est utilisée. Images de `inserts.json` (photos produit) : pas de sous-titre d'origine.
- Après `rendu.py` : `cp travail/<REF>/cues_final.json travail/<REF>/cues.json` (rendu.py l'écrase), puis `controle.py`.

## Vérifier
Une planche « original | traduit » par plan (une image au milieu de chaque plan), et une recherche automatique de lettres d'origine hors du bandeau : voir `JOURNAL.md`.
