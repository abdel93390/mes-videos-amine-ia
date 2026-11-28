# Voix gratuite (à la place d'ElevenLabs et de Replicate)

Traduit les voix d'une vidéo sans service payant : tout tourne sur la machine de la session (0 €, 0 crédit).
Chaque personnage garde **sa propre voix**, copiée sur l'original, et parle la langue cible. La musique, le chant (anachid, chanson) et les bruitages d'origine restent.

## Comment ça marche
1. **Séparer** : demucs sépare les voix de la musique, puis MossFormer2 sépare les **paroles** du **chant** dans la piste des voix.
   - `sep/parole.wav` contient les paroles seules : on y prend la voix de chaque personnage.
   - `sep/fond.wav` contient la musique, le chant et les bruitages, sans les paroles : c'est le fond de la vidéo traduite.
2. **Voix** : deux voix gratuites, à faire écouter à l'élève sur un essai de 30 s.
   - **Voix A** : Qwen3-TTS. Bonne prononciation, 10 langues.
   - **Voix B** : VoxCPM2. Joue l'émotion de la réplique (consigne `style`), 30 langues.
3. **Choisir** : chaque réplique est générée plusieurs fois (prises). On garde celle dont les mots sont justes (réécoute Whisper par Groq, gratuite), puis la plus ressemblante à la voix d'origine (empreinte de voix).
4. **Mixer** : chaque réplique est posée à sa place sur `sep/fond.wav`, au niveau de la voix d'origine. Elle est accélérée de 15 % au plus si elle dépasse, et le retard est affiché.
5. **Rendre** : vidéo en 1080 de large (1080x1920 en vertical), comme le demande l'élève.

## Utilisation
Toutes les commandes se lancent depuis `/home/user/amine-monteur-video-ia`. `V=/home/user/mes-videos-amine-ia/outils/voix-gratuite/voix.sh`.
```bash
bash /home/user/mes-videos-amine-ia/outils/voix-gratuite/installer.sh      # 1 min avec uv, sinon quelques minutes
ADCLONER_DEMUCS=local ADCLONER_PYTHON=$HOME/.cache/voix-gratuite/sep/bin/python python3 amine/scripts/analyse.py <vidéo> travail/<REF>
bash $V travail/<REF> separer          # environ 8 fois la durée de la vidéo
bash $V travail/<REF> refs             # après avoir écrit voix/refs.json
bash $V travail/<REF> caler            # après avoir écrit voix/lignes.json : début réel, durée, pauses, longueur conseillée
bash $V travail/<REF> caler --ecrire   # quand le rapport est propre : écrit debut et duree_origine dans lignes.json
bash $V travail/<REF> a --fin 30       # essai 30 s, voix A (pareil avec b)
bash $V travail/<REF> rendre a travail/<REF>/essai_voix_A.mp4 --fin 30
bash $V travail/<REF> a                # toute la vidéo
bash $V travail/<REF> rendre a travail/<REF>/<REF>_FR_9x16_voix_A.mp4
```
Pour refaire seulement quelques répliques, après avoir changé leur texte : effacer leurs prises (`voix/a/S11_*.wav`) et leurs lignes dans `voix/a/ecoutes.json`, puis `bash $V travail/<REF> a --prises 6 S11`. Le choix et le mixage repartent tout seuls.

## Fichiers à écrire (dans `travail/<REF>/voix/`)
- `reglages.json` : `{"langue": "fr"}` (sinon `langue_cible` de `fiche.json`, sinon le français).
- `refs.json` : une entrée par personnage, avec 5 à 10 s propres de sa voix, sans autre voix par-dessus :
  `{"homme": {"segments": [[14.76, 20.48]], "texte": "Because Allah gave to me first. Now take it and say Bismillah.", "style": "warm, kind young man"}}`
  `texte` est la transcription exacte des segments, dans la langue d'origine (voir `analyse.json` → `mots`).
- `lignes.json` : une entrée par réplique.
  `[{"id": "S1", "perso": "homme", "debut": 0.6, "fin": 5.78, "texte": "Ne cours pas, petit frère.", "style": "gentle, caring young man"}]`
  - `debut` et `fin` viennent de la réplique d'origine. `place`, le temps jusqu'à la réplique suivante, est calculé tout seul.
  - `"origine": true` garde la vraie voix pour un mot qui n'est pas dans la langue d'origine (« Ummi », « Alhamdulillah »).
  - Écrire les mots étrangers comme ils se prononcent dans la langue cible : « Oummi », « Alhamdoulillah », « Soubhanallah », « Hadji ».
  - Éviter les mots qui se confondent : « Allah voit ta faim » était entendu « ta femme » ; « Allah voit que tu as faim » passe.

## Caler la voix sur la bouche (sinon « on a l'impression que c'est décalé »)
Remarque de l'élève du 28/11/2026. `caler` mesure la vraie parole d'origine de chaque réplique dans `sep/parole.wav`, et le mixage s'en sert :
- **Pauses** : une pause de plus de 0,45 s au milieu d'une réplique est signalée « À COUPER ». Couper la ligne en deux (`S17a` « Jeune homme, », `S17b` « tu as vraiment nourri… »), chacune avec son début, pour que la voix s'arrête quand la bouche s'arrête.
- **Longueur** : « TROP COURT » ou « TROP LONG » compare le texte à la durée d'origine (environ 15 caractères par seconde pour ces voix). Rallonger, en traduisant plus complètement, ou raccourcir, jusqu'à ce que le rapport soit propre.
- **Durée** : avec `--ecrire`, chaque ligne reçoit `duree_origine`. Le mixage étire alors chaque réplique (0,87 à 1,18) pour qu'elle commence et finisse comme l'original.
- **Début** : le début mesuré remplace celui de Whisper. Quand un son dure déjà avant la réplique (pleurs, chant), le début de la ligne est gardé.

## Trouver qui parle
Regarder les images (qui est à l'écran, qui a la bouche qui bouge) et le sens. La hauteur de voix aide aussi (pyin sur `sep/parole.wav`) : un homme parle vers 100 à 150 Hz, une vieille femme vers 150 à 200 Hz, un enfant au-dessus de 250 Hz. Elle se trompe quand deux voix se chevauchent.

## Limites (version 1)
- Moins naturel qu'ElevenLabs. L'élève a jugé la version complète « parfait » le 28/11/2026, mais les voix copiées restent à juger à l'oreille.
- Les exclamations très courtes (un ou deux mots) sortent mal avec les deux voix : garder la voix d'origine (`origine`) quand elles ne sont pas en anglais.
- Lent sur processeur : environ 10 s par prise. Une vidéo de 30 répliques avec 3 prises prend 15 à 20 min par voix.
- Voix A : la mémoire monte à chaque génération (tuée vers 14 Go). `voix.sh` relance donc un processus par personnage, par lots de 6 phrases.
- Réécoute Groq : 20 demandes par minute au plus. `choisir.py` attend 3 s entre deux demandes et garde les réécoutes.

## Origine et licences (toutes autorisent l'usage commercial)
- Qwen3-TTS 1.7B Base, Alibaba : https://github.com/QwenLM/Qwen3-TTS (Apache 2.0).
- VoxCPM2, OpenBMB : https://huggingface.co/openbmb/VoxCPM2 (Apache 2.0).
- MossFormer2_SE_48K, ClearVoice : https://huggingface.co/alibabasglab/MossFormer2_SE_48K (Apache 2.0).
- demucs htdemucs, Meta : MIT.
- ECAPA, SpeechBrain : https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb (Apache 2.0).
- Écartés : XTTS-v2, F5-TTS, Fish Speech / OpenAudio, Voxtral TTS (non commerciaux) ; Chatterbox (résultat jugé mauvais).

L'historique des versions et des tests est dans [JOURNAL.md](JOURNAL.md).
