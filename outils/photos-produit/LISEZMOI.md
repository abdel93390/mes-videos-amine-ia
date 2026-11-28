# Photos du produit de l'élève à la place du produit concurrent

1. Récupérer sa fiche et ses photos (boutique Shopify) :
   `python3 /home/user/mes-videos-amine-ia/outils/photos-produit/recuperer.py <lien du produit> travail/<REF>/produit`
   Lire la description : composition, dosage, procédé, offre, garantie. Lister les écarts avec la pub d'origine et **demander à l'élève** avant de changer un argument (MES-REGLES.md).
2. Repérer les plans du produit concurrent sur une planche détaillée (une image toutes les 16 images de la fin de la vidéo) : début et fin de chaque plan, flacon visible même à moitié.
3. Écrire `reglages.json` (exemple en haut de `inserer.py`) et lancer sur la base 1080 :
   `python3 .../photos-produit/inserer.py <base 1080>.mp4 <sortie>.mp4 reglages.json --inserts travail/<REF>/inserts.json`
4. Plans où le flacon passe dans la main (verser des gélules…) : plutôt garder les images voisines sans flacon (`rendu.remplacements`, mode `aller_retour`).
Regarder un aperçu des recadrages avant toute la vidéo (bords coupés, texte de la photo coupé, badge qui cache l'étiquette).

## Petit flacon concurrent qui reste dans un plan (posé sur une table, posé par une main)
Quand remplacer tout le plan par une photo casserait la scène (le personnage parle encore), remplacer seulement le corps du flacon par celui du flacon de l'élève, suivi image par image :
`~/.cache/effaceur/env/bin/python /home/user/mes-videos-amine-ia/outils/photos-produit/etiquette_flacon.py <base 1080>.mp4 <sortie>.mp4 reglages.json --essai <1re>,<milieu>,<dernière> --apercu travail/<REF>/essai_flacon`
Regarder les aperçus (avant | après), puis relancer sans `--essai`. Le faire sur `src.mp4` ET `clean_vmake.mp4` de la base 1080. Mode d'emploi et pièges en haut du script.
