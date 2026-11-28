# Effaceur gratuit de sous-titres

Efface les sous-titres incrustés d'une vidéo, à la place de Vmake, sans crédit et sans service payant : tout tourne sur la machine de la session.

## Comment il marche
1. Il trouve la bande où se trouvent les sous-titres, puis, image par image, le texte blanc entouré d'un contour sombre.
2. Il redessine le décor caché derrière le texte avec **LaMa**, un modèle d'intelligence artificielle libre (licence Apache 2.0, usage commercial autorisé). Il ne travaille que la zone autour du texte : le reste de l'image n'est pas touché.
3. La vidéo de sortie a exactement les mêmes images, la même cadence et le même son que l'entrée.

## Utilisation
```bash
bash outils/effaceur/effacer.sh entree.mp4 sortie.mp4 --apercu avant_apres.jpg
```
Options : `--duree 10` (essai sur les 10 premières secondes), `--bande Y0 Y1` (bande des sous-titres en pixels, si elle est mal trouvée), `--masque masque.mp4` (montre le texte repéré), `--largeur-max 0` (qualité maximale, plus lent).
Le premier appel de la session installe les outils dans `~/.cache/effaceur` (quelques minutes).

## Limites (version 1)
- Seulement les sous-titres **blancs à contour sombre** : pas encore le texte en couleur, sur rectangle ou en karaoké.
- Lent : environ 8 fois la durée de la vidéo (une vidéo de 8 min prend environ 1 h).
- Léger scintillement là où était le texte quand l'image bouge (les nouveaux sous-titres le cachent en grande partie).

## Origine et licences
- Modèle LaMa : https://github.com/advimman/lama (Apache 2.0).
- Fichier du modèle téléchargé depuis le projet https://github.com/YaoFANGUK/video-subtitle-remover (Apache 2.0).
- Le reste (repérage du texte, assemblage) a été écrit pour ce dépôt.

L'historique des versions et des tests est dans [JOURNAL.md](JOURNAL.md).

## Vérifier qu'il n'y a ni flou ni reste de lettre (demande de l'élève)
`python3 /home/user/mes-videos-amine-ia/outils/effaceur/verifier.py travail/<REF>/src.mp4 travail/<REF>/clean_vmake.mp4 --bande Y0 Y1`
Donne la netteté de la zone effacée par rapport au décor autour (1 = aussi net) et les pires images, puis le nombre d'images avec des restes de lettres. Regarder les pires en gros plan (original | effacé | final) et montrer l'image à l'élève.
