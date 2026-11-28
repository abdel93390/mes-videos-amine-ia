"""Découpe la voix de référence de chaque personnage dans les paroles isolées (sep/parole.wav).
Usage : python refs.py <dossier>
voix/refs.json : {"perso": {"segments": [[debut, fin], ...], "texte": "transcription exacte des segments", "style": "consigne de ton (voix B)"}}
Prendre 5 à 10 s d'un seul personnage, sans autre voix par-dessus. Écrit voix/refs/<perso>.wav (24 kHz mono, niveau réglé)
et affiche ce que Whisper (Groq, gratuit) y entend : ce doit être le texte, et rien d'autre."""
import json, os, subprocess, sys

d = sys.argv[1]
f = os.path.join(d, "voix", "refs.json")
refs = json.load(open(f, encoding="utf-8"))
os.makedirs(os.path.join(d, "voix", "refs"), exist_ok=True)
for perso, r in refs.items():
    segs = r["segments"]
    filtre = ";".join(f"[0]atrim={a}:{b},asetpts=N/SR/TB[s{i}]" for i, (a, b) in enumerate(segs))
    filtre += ";" + "".join(f"[s{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,highpass=f=80,loudnorm=I=-20:TP=-2[o]"
    sortie = os.path.join(d, "voix", "refs", f"{perso}.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(d, "sep", "parole.wav"), "-filter_complex", filtre,
                    "-map", "[o]", "-ar", "24000", "-ac", "1", sortie], check=True)
    r["audio"] = os.path.relpath(sortie, d)
    duree = sum(b - a for a, b in segs)
    entendu = subprocess.run(["curl", "-s", "https://api.groq.com/openai/v1/audio/transcriptions", "-H", "Authorization: Bearer cloud",
                              "-H", "User-Agent: amine", "-F", "model=whisper-large-v3", "-F", "response_format=text",
                              "-F", f"file=@{sortie}"], capture_output=True, text=True).stdout.strip()
    print(f"{perso} : {duree:.1f} s | entendu : {entendu}")
json.dump(refs, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
