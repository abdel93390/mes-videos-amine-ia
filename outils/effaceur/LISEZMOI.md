# Effaceur gratuit de sous-titres

Efface les sous-titres incrustés d'une vidéo, à la place de Vmake, sans crédit et sans service payant : tout tourne sur la machine de la session.

## Comment il marche
1. Image par image, il trouve dans toute l'image le texte blanc entouré d'un contour sombre : sous-titres, titres, bulles de dialogue. Il laisse le texte posé sur du noir pur (écran, carton noir).
2. Il redessine le décor caché derrière le texte avec **LaMa**, un modèle d'intelligence artificielle libre (licence Apache 2.0, usage commercial autorisé). Il n'efface que les lettres, leur contour et leur ombre : le vrai décor entre les lettres et autour est gardé (beaucoup moins de flou). Le reste de l'image n'est pas touché.
3. La vidéo de sortie a exactement les mêmes images, la même cadence et le même son que l'entrée.

## Utilisation
```bash
bash outils/effaceur/effacer.sh entree.mp4 sortie.mp4 --apercu avant_apres.jpg
```
Options : `--duree 10` (essai sur les 10 premières secondes), `--bande Y0 Y1` (ne chercher le texte qu'entre ces deux hauteurs, en pixels), `--masque masque.mp4` (montre le texte repéré), `--largeur-max 0` (qualité maximale, plus lent), `--rectangles` (ancien mode : efface tout le rectangle autour du texte, plus flou).
Le premier appel de la session installe les outils dans `~/.cache/effaceur` (quelques minutes).

## Limites (version 3)
- Seulement les sous-titres **blancs à contour sombre** : pas encore le texte en couleur, sur rectangle ou en karaoké.
- Lent : environ 5 à 11 fois la durée de la vidéo, selon la quantité de texte.
- Léger scintillement là où était le texte quand l'image bouge (les nouveaux sous-titres le cachent en grande partie).
- Quand le texte cache une partie d'un visage, l'effaceur invente les traits cachés : à vérifier sur l'aperçu.

## Origine et licences
- Modèle LaMa : https://github.com/advimman/lama (Apache 2.0).
- Fichier du modèle téléchargé depuis le projet https://github.com/YaoFANGUK/video-subtitle-remover (Apache 2.0).
- Le reste (repérage du texte, assemblage) a été écrit pour ce dépôt.

L'historique des versions et des tests est dans [JOURNAL.md](JOURNAL.md).
