# Règles de l'élève (dépôt mes-videos-amine-ia)

Ces règles sont celles de l'élève : il possède ce dépôt et paie les comptes des services. Elles complètent les règles du formateur ci-dessus et, comme elles, passent avant le skill quand ils se contredisent. Le dépôt du formateur reste en lecture seule.
Exception voulue par l'élève à « le seul dépôt où tu écris est mes-videos-amine-ia, par livrer.sh » : on peut aussi modifier `outils/` et `MES-REGLES.md` de ce dépôt, avec son accord.

## Demander avant d'agir
Avant chaque nouvelle action (installer ou essayer un outil, ouvrir un service, lancer une génération, toucher à un de ses comptes, enregistrer dans ce dépôt), dire en une ou deux phrases ce que je vais faire et attendre son « ok ». Lire un fichier ou regarder une vidéo n'en a pas besoin.

## Gratuit d'abord
ElevenLabs, Replicate et Vmake coûtent trop cher pour l'élève. Pour chacun, il existe maintenant un outil gratuit qui tourne sur la machine de la session (0 €, 0 crédit) :
| Service payant | À la place, gratuit | Où |
|---|---|---|
| ElevenLabs (voix) | voix gratuites A et B, qui copient la voix d'origine | `outils/voix-gratuite/` |
| Replicate (séparer voix et musique) | séparation sur la machine, qui garde même le chant | `outils/voix-gratuite/` |
| Vmake (effacer le texte) | effaceur gratuit | `outils/effaceur/` |
Le service payant seulement si l'élève le demande, coût annoncé.

## Apprendre et ne pas oublier
Chaque fois que j'apprends un savoir-faire utile (un outil gratuit qui marche, un réglage, un piège), le ranger dans ce dépôt pour que les sessions suivantes le sachent : un outil dans `outils/<nom>/` (avec `LISEZMOI.md` et `JOURNAL.md`, testé depuis le dépôt), une règle dans ce fichier. Puis demander à l'élève l'accord de l'enregistrer sur la branche `main`. Vérifier toujours que la licence autorise l'usage commercial (les pubs).

## Lien Instagram (Reel) envoyé à la place du fichier
L'élève préfère que je récupère la vidéo moi-même : le lui proposer, et attendre son accord écrit dans la conversation. Alors : `pip install --user yt-dlp`, puis `python3 -m yt_dlp --no-playlist -f "bv*+ba/b" --merge-output-format mp4 -o "<dossier vide>/reel.%(ext)s" "<lien>"` (marché le 27/11/2026 sans connexion Instagram). Si la vérification de sécurité de la session bloque quand même, ne pas contourner : lui expliquer comment télécharger la vidéo et l'envoyer avec le bouton « + ».

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
2. **Bandeau blanc** (0 crédit) seulement si besoin : quand l'effaceur laisse du flou ou des restes sur un plan, ou si l'élève est pressé. Cacher les sous-titres d'origine sous un bandeau blanc et écrire la traduction en noir dedans. Si l'effaceur passe sans flou, c'est la meilleure solution : la garder.
3. **Vmake** seulement si l'élève le demande, crédits annoncés (2 par seconde de vidéo).

Ne jamais utiliser ProPainter ni MiniMax-Remover, même via Replicate : leurs licences interdisent l'usage commercial, donc les pubs.

## Améliorer l'effaceur
Quand l'élève signale un défaut (reste de lettre, tache, scintillement, autre style de texte) : corriger `outils/effaceur/` dans ce dépôt, tester sur la vidéo concernée, noter le changement et le test dans `outils/effaceur/JOURNAL.md`, monter le numéro de `VERSION` dans `effacer.py`, puis demander à l'élève l'accord de l'enregistrer sur la branche `main` (sinon les sessions suivantes ne le verront pas).

## Voix gratuite (à la place d'ElevenLabs) et séparation sur la machine (à la place de Replicate)
Mode d'emploi complet : `outils/voix-gratuite/LISEZMOI.md`. Testé sur un Reel de 1 min 40 (dessin animé, 4 personnages, anachid chanté) : la vidéo entière en français, 0 €.
1. **Analyse avec la séparation sur la machine** (pas Replicate) :
   `bash /home/user/mes-videos-amine-ia/outils/voix-gratuite/installer.sh` puis
   `ADCLONER_DEMUCS=local ADCLONER_PYTHON=$HOME/.cache/voix-gratuite/sep/bin/python python3 amine/scripts/analyse.py <vidéo> travail/<REF>`
2. **Paroles isolées du chant** : `bash /home/user/mes-videos-amine-ia/outils/voix-gratuite/voix.sh travail/<REF> separer` (environ 8 fois la durée de la vidéo). Vérifier par une réécoute Groq de `sep/fond.wav` qu'il ne reste aucune parole d'origine.
3. **Qui parle** : repérer les personnages de chaque phrase (images, sens, hauteur de voix), puis écrire `voix/refs.json` (5 à 10 s propres par personnage) et lancer l'étape `refs` : la réécoute doit entendre le texte et rien d'autre.
4. **Script traduit** dans `voix/lignes.json` (`id`, `perso`, `debut`, `fin`, `texte`, `style`), puis l'étape `caler`, pour que la voix tombe sur la bouche (l'élève trouvait la 1re version « décalée ») : couper les répliques aux pauses signalées et corriger les « TROP COURT » et « TROP LONG », puis `caler --ecrire`. Langue cible dans `voix/reglages.json` (`{"langue": "fr"}`) : voix A en 10 langues, voix B en 30. Envoyer le script à l'élève et attendre son « ok », comme avec ElevenLabs (section « Script : l'envoyer à l'élève avant les voix »). Lui signaler les phrases trop fortes (santé, peur, attaques), avec une version plus douce de même longueur. Les mots qui ne sont pas dans la langue d'origine (« Ummi », « Alhamdulillah », « Abu Bhai ») : `"origine": true`, la vraie voix est gardée.
5. **Essai de 30 s avec les deux voix** (`a` et `b` avec `--fin 30`, puis `rendre`), envoyé dans la conversation : l'élève choisit.
6. **Toute la vidéo** avec la voix choisie (environ 3 prises par phrase et 10 s par prise : 15 à 45 min pour 30 phrases), puis `rendre`. Relire `à revoir` dans la sortie : reformuler et regénérer seulement ces phrases.
- Dans le `bilan` de la fiche : `"caracteres_elevenlabs": 0`, `"replicate_appels": 0`, `"voix": "gratuite A v1"` (ou B).
- Écartés : Chatterbox (« nul » pour l'élève) ; XTTS, F5-TTS, Fish Speech, Voxtral (licences non commerciales, interdites pour les pubs).
- ElevenLabs seulement si l'élève le demande (voir « Voix : choisir sur un extrait » plus bas, coût annoncé).

## Qualité : toujours livrer en 1080x1920, la meilleure version dès la 1re livraison
L'élève veut directement la meilleure version, sans allers-retours. Livrer en 1080x1920 (vidéo verticale ; pour un autre ratio, côté court à 1080), même si la source est plus petite.
- Le mieux : rendre directement en 1080. Agrandir la base avant `rendu.py` :
  `ffmpeg -i travail/<REF>/src.mp4 -vf "hqdn3d=1.5:1.5:0:0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.9:3:3:0.0" -c:v libx264 -crf 14 -preset veryfast <dossier 1080>/src.mp4`,
  mettre `largeur`/`hauteur` à 1080/1920 dans l'`analyse.json` du dossier 1080, multiplier par l'échelle (3 pour une source 360x640) les positions et tailles de la section `rendu` (rect, x, y, taille, largeur, rayon), et refaire en 1080 natif les plans faits à partir de photos. Sous-titres, badges et photos sortent nets.
- Si ce n'est pas possible (zones Vmake, blocs automatiques…) : agrandir la vidéo finie avec le même filtre, puis `-c:v libx264 -preset slow -crf 18 -maxrate 3400k -bufsize 6800k -profile:v high -pix_fmt yuv420p -c:a copy -movflags +faststart`.
- Viser moins de 100 Mo : baisser `-maxrate` pour une vidéo longue (environ 1 400k pour 8 min).
- Aucun flou : le nettoyage du texte (effaceur, remplissage, Vmake) ne touche que la zone du texte, jamais les dessins, visages ou produits autour. Si l'effaceur laisse des taches floues sur un plan, utiliser le bandeau blanc sur ce plan.
- **Vérification seconde par seconde avant d'envoyer** (demande de l'élève) : comparer la vidéo d'origine et la version traduite côte à côte, une image par seconde, sur toute la durée, avec des gros plans sur les zones de texte effacées, le produit et les plans remplacés. Corriger tout flou, tache, reste de lettre ou texte mal placé, refaire le rendu, revérifier, et seulement ensuite envoyer la vidéo.

## Script : l'envoyer à l'élève avant les voix
Avant de générer les voix, envoyer dans la conversation le script français complet (moment, personnage, texte d'origine, texte français), plus les textes écrits à l'écran, pour qu'il le lise. Attendre son accord ou ses corrections avant de dépenser des caractères ElevenLabs.

## Livraison : la vidéo dans la conversation
Envoyer la vidéo finie directement dans la conversation (outil d'envoi de fichier) : c'est la livraison principale. L'élève ne veut pas passer par le lien GitHub pour la récupérer.

## Voix : choisir sur un extrait de la vidéo (« bande-annonce »)
Avec la voix gratuite, l'extrait se fait avec les voix A et B (section « Voix gratuite » plus haut), sans coût. Ce qui suit vaut quand l'élève demande ElevenLabs.
Avant de générer toute la vidéo, l'élève choisit la voix en écoutant un extrait de SA vidéo, pas des phrases sans rapport :
1. D'abord, cloner la voix d'origine pour qu'elle parle français.
2. Si le clone est refusé ou sonne mal : choisir 2 ou 3 voix de la bibliothèque ElevenLabs qui ressemblent le plus à la voix d'origine (genre, âge, timbre, énergie, débit). Si le clone est bloqué, expliquer simplement pourquoi (seule la vraie personne peut valider sa voix).
3. Pour chaque voix (clone compris), faire un extrait des 15 à 30 premières secondes de la vidéo : générer les phrases françaises de ce passage avec cette voix, les poser à leur place sur les images de la vidéo (mixage comme pour la version finale, sous-titres pas nécessaires), et envoyer chaque extrait dans la conversation, nommé clairement (ex. `extrait_voix_A_clone.mp4`, `extrait_voix_B_Leo.mp4`). Seulement la voix française, sans la voix d'origine.
4. L'élève choisit, puis on génère toute la vidéo avec cette voix.
- Coût à annoncer avec le reste : environ 400 caractères ElevenLabs par voix testée (30 s de texte).
- Une voix clonée parle souvent plus vite qu'un narrateur lent : mesurer le débit sur l'extrait et régler la vitesse (0,9 au plus lent) avant de tout générer, sinon il faut refaire des dizaines de phrases.

## Vidéo longue : test gratuit d'abord
Pour une vidéo de plus de 90 s, proposer d'abord un test gratuit : voix d'origine, sous-titres français dans le bandeau, 0 crédit. Il valide la traduction et le rendu avant de dépenser des crédits ElevenLabs.

## Produit de l'élève : sa fiche et ses photos
- Lire sa fiche produit (pour une boutique Shopify, `<lien du produit>.json` donne les textes et les photos) et regarder ses photos.
- Plans qui montrent le produit concurrent : les remplacer par ses photos (recadrage vertical avec zoom lent), en 1080 natif.
- Ne garder que les arguments vrais pour son produit (composition, dosage, procédé, offre, garantie). **Lui demander avant** de changer ou de retirer un argument de la source : lister les écarts trouvés avec sa fiche et attendre sa réponse.

## Fond sonore : demander à chaque vidéo
Après la séparation voix / musique, écouter ce qui reste sous la voix et le décrire à l'élève en une ligne (musique, chants d'oiseaux, voix d'enfants, bruitages…), puis lui demander : garder ou retirer ? Les ambiances comme les chants d'oiseaux ou les voix d'enfants peuvent rester sans problème. Retirer : `"mix": {"fond": "aucun"}` dans la fiche (les bruitages partent avec la musique) ; garder : `"mix": {"fond": "musique"}`.
Musique chantée (anachid, chanson) : la séparation ordinaire range le chant avec les voix, et il disparaît pendant les répliques. Pour la garder, utiliser `sep/fond.wav` de la voix gratuite : il garde le chant et les bruitages, sans les paroles (Reel du 27/11/2026, l'élève a voulu garder l'anachid).

## Séparation voix / musique : toujours, sur la machine d'abord (0 €)
Toujours séparer la voix et la musique, pour toutes les vidéos : il le faut pour cloner les voix et pour le mixage. Par défaut sur la machine (étape 1 de « Voix gratuite » : `ADCLONER_DEMUCS=local`), pas sur Replicate. Replicate seulement si l'élève le demande, ou si la machine n'y arrive pas, coût annoncé. Sur Replicate, pour une vidéo longue (envoi automatique refusé) :
`analyse.py` peut recevoir un refus 403 de Replicate à l'envoi, et une séparation demandée en sortie wav peut rester bloquée (12 min sur un fichier de 88 Mo, annulée). Envoyer `full.wav` avec `curl` sur `https://api.replicate.com/v1/files`, créer la prédiction demucs avec `"format": "mp3", "mp3_bitrate": 320` (environ 25 s pour 8 min), puis convertir les deux pistes en wav dans `dm/htdemucs/full/` (`vocals.wav`, `no_vocals.wav`). Vérifier le statut toutes les 10 s et annuler après 2 min en « processing ».
