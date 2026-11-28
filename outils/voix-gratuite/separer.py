"""Sépare la parole d'origine de tout le reste, même quand la musique est chantée (anachid, chanson).
Usage : python separer.py <dossier>
Il faut d'abord dm/htdemucs/full/vocals.wav et no_vocals.wav (analyse.py avec ADCLONER_DEMUCS=local, voir LISEZMOI.md).
Écrit : sep/parole.wav (paroles seules, 48 kHz mono) : pour les voix de référence et le niveau des voix ;
        sep/fond.wav (musique + chant + bruitages, sans les paroles, 44,1 kHz stéréo) : le fond de la vidéo traduite.
MossFormer2_SE_48K (ClearVoice, Apache 2.0) : environ 8 fois la durée de la vidéo sur processeur."""
import os, sys, subprocess, tempfile, time
import numpy as np, soundfile as sf, librosa

d = os.path.abspath(sys.argv[1])
dm = os.path.join(d, "dm", "htdemucs", "full")
# ClearVoice range son modèle dans ./checkpoints du dossier courant : travailler dans le cache, jamais dans un dépôt
CACHE_CV = os.path.join(os.environ.get("VOIX_GRATUITE_CACHE", os.path.expanduser("~/.cache/voix-gratuite")), "clearvoice")
os.makedirs(CACHE_CV, exist_ok=True)
for f in ("vocals.wav", "no_vocals.wav"):
    if not os.path.exists(os.path.join(dm, f)):
        raise SystemExit(f"manque {dm}/{f} : lancer d'abord analyse.py avec ADCLONER_DEMUCS=local (voir LISEZMOI.md)")
os.makedirs(os.path.join(d, "sep"), exist_ok=True)
t0 = time.time()
with tempfile.TemporaryDirectory() as t:
    entree = os.path.join(t, "voix48.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(dm, "vocals.wav"), "-ar", "48000", "-ac", "1", entree], check=True)
    from clearvoice import ClearVoice
    os.chdir(CACHE_CV)
    cv = ClearVoice(task="speech_enhancement", model_names=["MossFormer2_SE_48K"])
    w = cv(input_path=entree, online_write=False)
    cv.write(w, output_path=os.path.join(d, "sep", "parole.wav"))
    v, sr = sf.read(entree)
p, _ = sf.read(os.path.join(d, "sep", "parole.wav"))
n = min(len(v), len(p))
reste = librosa.resample(v[:n] - p[:n], orig_sr=sr, target_sr=44100)  # chant, foule, pleurs : tout sauf les paroles
fond, fsr = sf.read(os.path.join(dm, "no_vocals.wav"), always_2d=True)
fond = librosa.resample(fond.T, orig_sr=fsr, target_sr=44100).T if fsr != 44100 else fond
m = min(len(fond), len(reste))
sf.write(os.path.join(d, "sep", "fond.wav"), fond[:m] + reste[:m, None], 44100)
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
print(f"séparation faite en {time.time()-t0:.0f} s : paroles {db(p):.0f} dB, reste (chant, ambiance) {db(reste):.0f} dB")
print("vérifier qu'il ne reste aucune parole d'origine dans sep/fond.wav (réécoute Groq, voir LISEZMOI.md)")
