# Journal de l'effaceur

Une entrée par version : ce qui a changé, sur quelle vidéo c'est testé, ce qui reste à faire.

## v2 (27/11/2026)
**Changements :**
- Le texte est cherché **dans toute l'image**, plus seulement dans une bande : ça couvre les titres en haut et les bulles de dialogue placées près des personnages. `--bande` permet encore de limiter la recherche.
- Filtre plus strict : il faut au moins 3 lettres blanches séparées, et le texte posé sur du noir pur est ignoré (écran de montre « 72 BPM », carton noir « MIESIĄC PÓŹNIEJ » : la méthode les traite autrement).
- Chaque groupe de texte (titre, bulle, sous-titre) est effacé à part.
- Calculs d'image plus rapides avec OpenCV (une première version de la v2 prenait 54 fois la durée de la vidéo).

**Test :** pub MyBeet 2 en polonais, 3 min 12 s, 360x640, animation 3D, avec titre d'accroche en haut et bulles de dialogue un peu partout.
- Repérage sur une image toutes les 4 s : tous les sous-titres, bulles et titres trouvés, scènes de nuit comprises ; plus de faux repérages (montre, reflet sur une machine).
- Essai sur 10 s : texte effacé sur 262 images sur 300, en 2,3 min (13,9 fois la durée, à cause du titre et des bulles effacés en même temps). Visages et décor bien refaits ; léger flou par endroits.
- Pas traité (et c'est voulu) : la carte de fin en couleur (« 2+1 GRATIS » rouge, « Link poniżej » jaune), le carton noir. Ils restent à faire avec les patches de la méthode.

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
