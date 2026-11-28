# Journal des voix expressives

## v1 — 28/11/2026 (MYBEET → Betalia, 6 personnages, 5 min 37)
- 1re version avec des voix « narrateur » de la bibliothèque (eleven_multilingual_v2) : l'élève a trouvé les voix plates. 5 900 caractères perdus quand on a tout refait : valider la voix AVANT la génération complète.
- Clonage des 4 voix principales bloqué deux fois (detected_captcha_voice), même après passage à un abonnement supérieur : ce sont sans doute des voix de la bibliothèque. `/v1/similar-voices` a retrouvé des voix polonaises très proches (Adam, Magdalena, Luke, Rafał, Ian), qui parlent français avec eleven_v4 (réécoute Whisper : français).
- eleven_v4 + balises d'émotion : répliques plus longues (souffles, pauses). Correctifs : couper le souffle d'avant au-delà de 0,35 s, accélération ≤ 1,12, raccourcir ~8 répliques ; retard max 0,61 s.
- Mots courts seuls mal prononcés (« Je lis » entendu « Alice ») : reformuler (« Je cherche »).
- Coût de la vidéo : environ 5 100 caractères (dont ~1 800 de balises) pour 129 répliques.
