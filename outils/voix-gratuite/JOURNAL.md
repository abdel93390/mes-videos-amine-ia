# Journal de la voix gratuite

Une entrée par version : ce qui a changé, sur quelle vidéo c'est testé, ce qui reste à faire.

## v1 (28/11/2026)
**Contenu :** séparation sur la machine (demucs, puis MossFormer2 pour isoler les paroles du chant). Deux voix qui copient la voix d'origine : A (Qwen3-TTS 1.7B Base) et B (VoxCPM2). Choix de la meilleure prise : d'abord les mots justes (réécoute Groq), puis la ressemblance (ECAPA). Mixage sur le fond d'origine avec le chant gardé, et rendu en 1080 de large.

**Test :** Reel Instagram de 1 min 40, en anglais vers le français (réf. IGDGB, 27 et 28/11/2026). Dessin animé 3D, 4 personnages (un homme, un petit garçon, une vieille femme, un grand-père), musique = anachid chanté en arabe.
- Essais sur 30 s :
  1. Chatterbox, avec des références prises dans la piste voix de demucs : « nul » pour l'élève.
  2. Voix A, mêmes références : « beaucoup mieux, mais c'est toujours pas ça ».
  3. Voix A et B avec des références propres (paroles isolées du chant) et l'anachid gardé : « pas mal, un bon début ».
- Vidéo entière, 31 répliques, 3 prises chacune :
  - voix A : 29 sur 31 bien entendues ;
  - voix B : 28 sur 31 ;
  - les 3 exclamations (« Ummi », « Alhamdulillah », « Abu Bhai ») gardées avec la voix d'origine ;
  - retard maximal 0,75 s sur la bouche ;
  - aucune parole anglaise restée dans le fond (réécoute de `sep/fond.wav`) ;
  - environ 1 h 30 en tout pour les deux voix, 0 € ;
  - l'élève a répondu « Parfait ».
- Test des scripts depuis le dépôt (28/11/2026), sur les 30 premières secondes. Tout est passé :
  - installation : 1 min avec uv ;
  - analyse avec demucs ;
  - `separer` : 29 s ;
  - `refs` : la réécoute entend exactement le texte de référence ;
  - `a` : 8 répliques sur 8 bien entendues ;
  - mixage sans retard ;
  - `rendre` en 1080x1920.
- Remarque de l'élève sur la version complète : « on a l'impression que c'est décalé ». Mesure faite sur la parole d'origine :
  - les phrases françaises étaient souvent plus courtes que l'original (« Ne cours pas, petit frère » 1,5 s contre 5,2 s parlées) ou plus longues (« Je sais, Oummi… » 4,5 s contre 2,4 s) ;
  - les pauses au milieu des répliques n'étaient pas reprises (« Jeune homme… [1 s] …c'est vrai que… »).
  Ajout de `caler.py` et de l'étirement à la durée d'origine dans `mixer.py`. Script refait : 39 lignes, coupées aux pauses et à la bonne longueur.

**Piège de mesure :** quand un son dure déjà au début de la fenêtre (pleurs, chant), le « début réel » sort 0,3 s trop tôt. `caler.py` garde alors le début de la ligne.

**Problèmes rencontrés :**
- Voix A tuée faute de mémoire (14 Go) en générant tous les personnages d'un coup : un processus par personnage maintenant.
- Voix B avec des références bruitées (chant derrière) : beaucoup de mots déformés. Avec la parole isolée : 8 sur 8.
- Voix B en mode « référence + transcription » : le pire des trois modes, retiré.
- Le choix gardait une prise à 0,90 alors qu'une autre était à 1,00 : maintenant, d'abord les meilleurs mots.
- SpeechBrain 1.0.3 avec huggingface_hub 2.x : erreur `use_auth_token`. L'environnement `sep` passe à torch 2.7.1 et SpeechBrain 1.1.2.

**Reste à faire :**
- Écouter les deux versions complètes avec l'élève et noter ses remarques ici.
- Essayer CosyVoice 3 (Apache 2.0, 9 langues dont le français) comme voix C.
- Haute définition gratuite (Real-ESRGAN, version dessin animé), si l'élève le veut.
