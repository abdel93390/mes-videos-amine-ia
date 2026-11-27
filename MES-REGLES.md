# Règles de l'élève (dépôt mes-videos-amine-ia)

Ces règles sont celles de l'élève : il possède ce dépôt et paie les comptes des services. Elles complètent les règles du formateur ci-dessus et, comme elles, passent avant le skill quand ils se contredisent. Le dépôt du formateur reste en lecture seule.
Exception voulue par l'élève à « le seul dépôt où tu écris est mes-videos-amine-ia, par livrer.sh » : on peut aussi modifier `outils/` et `MES-REGLES.md` de ce dépôt, avec son accord.

## Effacer le texte à l'écran : d'abord l'effaceur gratuit, pas Vmake
Vmake est trop cher pour l'élève (2 crédits par seconde, soit environ 1 000 crédits pour une vidéo de 8 min). Quand la méthode demanderait Vmake (sous-titres incrustés, texte sans fond) :

1. **Effaceur gratuit** (il tourne sur la machine : 0 crédit, 0 €). Il traite les sous-titres blancs à contour sombre.
   - Essai sur 10 s d'abord, puis montrer l'image avant/après à l'élève (SendUserFile) :
     `bash /home/user/mes-videos-amine-ia/outils/effaceur/effacer.sh travail/<REF>/src.mp4 travail/<REF>/essai_effaceur.mp4 --duree 10 --apercu travail/<REF>/essai_effaceur.jpg`
   - Si c'est bon, toute la vidéo, à la place de Vmake :
     `bash /home/user/mes-videos-amine-ia/outils/effaceur/effacer.sh travail/<REF>/src.mp4 travail/<REF>/clean_vmake.mp4 --apercu travail/<REF>/effaceur_avant_apres.jpg`
     puis `python3 amine/scripts/vmake.py travail/<REF> --existant` : il calcule les zones de texte sans appeler Vmake. La suite de la méthode ne change pas.
   - Durée : environ 8 fois la durée de la vidéo (8 min → environ 1 h). L'annoncer à l'élève. Le premier appel de la session installe les outils (quelques minutes).
   - S'il répond « AUCUN sous-titre blanc à contour trouvé », ou si l'aperçu montre des restes : ce style de texte n'est pas encore pris en charge. Passer à l'étape 2 ou 3, et noter le cas dans `outils/effaceur/JOURNAL.md`.
   - Dans le `bilan` de la fiche : `"vmake_s": 0` et `"effaceur": "v<numéro>"`.
2. **Bandeau blanc** (0 crédit) si l'élève est pressé ou si l'effaceur ne convient pas : cacher les sous-titres d'origine sous un bandeau blanc et écrire la traduction en noir dedans.
3. **Vmake** seulement si l'élève le demande, crédits annoncés (2 par seconde de vidéo).

Ne jamais utiliser ProPainter ni MiniMax-Remover, même via Replicate : leurs licences interdisent l'usage commercial, donc les pubs.

## Améliorer l'effaceur
Quand l'élève signale un défaut (reste de lettre, tache, scintillement, autre style de texte) : corriger `outils/effaceur/` dans ce dépôt, tester sur la vidéo concernée, noter le changement et le test dans `outils/effaceur/JOURNAL.md`, monter le numéro de `VERSION` dans `effacer.py`, puis demander à l'élève l'accord de l'enregistrer sur la branche `main` (sinon les sessions suivantes ne le verront pas).
