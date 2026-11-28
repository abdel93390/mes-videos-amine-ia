# Journal de l'effaceur

Une entrée par version : ce qui a changé, sur quelle vidéo c'est testé, ce qui reste à faire.

## v1 (27/11/2026)
**Contenu :** repérage du texte blanc pur collé à un contour sombre, dans la bande des sous-titres trouvée toute seule. Le masque de chaque image réunit celui des 2 images d'avant et d'après, pour attraper les fondus. Ensuite, LaMa (big-lama, Apache 2.0) efface seulement autour du texte, avec 40 px de contexte et une zone réduite à 480 px de large au plus.

**Test :** pub MyBeet en polonais, 85 s, 360x640, sous-titres blancs à contour, animation 3D.
- Essai sur 10 s : texte effacé sur 279 images sur 300, en 1,2 min (7,3 fois la durée). Décor bien refait (os, sol, escalier).
- Vidéo entière : 2562 images sur 2562, texte effacé sur 2435, en 10,2 min (7,2 fois la durée). Ensuite, `vmake.py --existant` de la méthode accepte le résultat : même nombre d'images, 13 périodes de texte toutes dans la bande des sous-titres (y 500-556). Petit flou par endroits sur les fonds détaillés.

**Comparé ce jour-là, et non retenu :**
- Replicate `hjunior29/video-text-remover` (environ 0,015 $) : taches floues visibles.
- Replicate ProPainter : propre, mais licence non commerciale, donc interdit pour les pubs.
- MiniMax-Remover : licence non commerciale.
- Flux optique fait maison : collages faux.
- `video-subtitle-remover` utilisé tel quel, sans carte graphique : mode STTN, 12 min pour 10 s et rien d'effacé ; mode LaMa, propre mais environ 35 fois la durée (sa détection du texte est lente).

**Reste à faire :**
- Moins de scintillement dans la zone effacée quand l'image bouge.
- Texte en couleur, texte sur rectangle, karaoké.
- Plus de vitesse : sauter les images presque identiques.

## Vérification de v1 sur une vidéo longue (28/11/2026, MB1470, 4 min 19, 3D réaliste, 360x640)
Vidéo entière : texte effacé sur 4 013 images sur 7 782 en 21 min (4,9 fois la durée). `verifier.py` (nouveau) : netteté de la zone effacée / décor = 1,05 en médiane, 0,86 pour les 5 % les plus bas ; pires à 0,6 (pull rouge à flocons, 0:16) invisibles à l'œil en gros plan ; aucun reste de lettre sur 3 765 images. Pas besoin du bandeau blanc sur cette vidéo.
