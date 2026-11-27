# Journal de l'effaceur

Une entrée par version : ce qui a changé, sur quelle vidéo c'est testé, ce qui reste à faire.

## v1 (27/11/2026)
**Contenu :** repérage du texte blanc pur collé à un contour sombre, dans la bande des sous-titres trouvée toute seule. Le masque de chaque image réunit celui des 2 images d'avant et d'après, pour attraper les fondus. Ensuite, LaMa (big-lama, Apache 2.0) efface seulement autour du texte, avec 40 px de contexte et une zone réduite à 480 px de large au plus.

**Test :** pub MyBeet en polonais, 85 s, 360x640, sous-titres blancs à contour, animation 3D.
- Essai sur 10 s : texte effacé sur 279 images sur 300, en 1,2 min (7,3 fois la durée). Décor bien refait (os, sol, escalier).
- Vidéo entière : voir plus bas.

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
