# Voix expressives : plusieurs personnages, émotions jouées (ElevenLabs v4)

À quoi ça sert : pour une pub « mini-film » avec plusieurs personnages, faire **jouer** les répliques (cris, larmes, soulagement) au lieu de les lire comme un narrateur, avec **une voix par personnage**, puis caler les phrases sur le montage.

Coût : caractères ElevenLabs. **Attention : les balises d'émotion (`[crying]`, `[shouting]`…) sont facturées comme du texte** (environ 15 caractères par réplique). Valider les voix sur des tests courts avant de tout générer (une génération complète refaite = tout payé deux fois).

## Utilisation
1. Fiche : chaque ligne a `perso` (ex. RICHARD) et `ton` (balise anglaise, ex. `crying, pleading`) ; `voix.par_perso` = {perso: voice_id}.
2. Clonage bloqué (`detected_captcha_voice`) : ne pas contourner. Chercher la voix d'origine dans la bibliothèque : `python3 voix_proches.py voix_echantillons/RICHARD.mp3` (gratuit), ajouter la voix au compte, faire 2 phrases de test.
3. `python3 voix_v4.py travail/<REF> [L1 L2 …]` : génère (modèle `eleven_v4`), garde l'alignement sans la balise (pour les sous-titres), réécoute avec Whisper.
4. `python3 ajuste_voix.py travail/<REF>` : coupe le souffle avant la parole (max 0,35 s), accélère au plus de 1,12 si la réplique déborde, enchaîne les répliques (retard max affiché : viser < 0,6 s, sinon raccourcir le texte).
5. `mix.py` puis `rendu.py` comme d'habitude.
