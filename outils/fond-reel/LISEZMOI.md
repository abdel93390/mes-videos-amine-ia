# Fond réel : effacer les sous-titres incrustés sans flou (gratuit, sans Vmake)

À quoi ça sert : enlever les sous-titres d'origine (texte blanc avec ombre) **sans laisser de taches floues**. Au lieu d'inventer le fond, l'outil reprend le **vrai décor** caché derrière les lettres dans les images voisines du même plan (quand le texte change ou disparaît, le décor est visible). Il n'invente le fond (LaMa) que là où quelqu'un bouge.

Licences : code maison ; LaMa (big-lama.pt) Apache 2.0 : pubs autorisées.

## Utilisation
1. `bash outils/fond-reel/installer.sh` (une fois par session).
2. Repérer les sous-titres sur une version **360x640** de la vidéo (même nombre d'images) :
   `python3 outils/fond-reel/detecte_st.py travail/<REF>` → `travail/<REF>/sub_boxes.json` (bande y 415-495 par défaut ; la changer si les sous-titres sont ailleurs : `415,495`).
   Écarter les fausses boîtes loin du centre (voir JOURNAL).
3. Effacer sur la source (360x640 : `--echelle 1` ; 720x1280 : `--echelle 2`) :
   `python3 outils/fond-reel/fond_reel.py <source.mp4> <sortie.mp4> 0 <dernière image> --boites travail/<REF>/sub_boxes_ok.json --analyse travail/<REF>/analyse.json --echelle 2`
   (`analyse.json` donne les coupes de plan : le fond n'est jamais pris dans un autre plan.)
4. Poser ensuite nos sous-titres français au même endroit (blancs à ombre, comme l'original) : ils couvrent la zone retouchée.

## Temps (processeur 4 cœurs de la session)
- 360x640 : environ 3 min pour 1 000 images.
- 720x1280 : environ 0,5 s par image sous-titrée (LaMa calculé à mi-résolution).
