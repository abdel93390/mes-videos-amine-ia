"""Pose les répliques traduites sur le fond d'origine (musique + chant + bruitages, sans les paroles : sep/fond.wav).
Usage : python mixer.py <dossier> <a|b> [--fin secondes]
Chaque réplique : silences retirés ; si caler.py a mesuré la durée d'origine, étirée pour durer pareil (0,87 à 1,18),
sinon accélérée jusqu'à 1,15 si elle dépasse sa place (sans changer la hauteur de la voix) ;
niveau calé sur la parole d'origine de sa fenêtre, posée à son début, jamais avant la fin de la précédente + 0,1 s.
Ligne avec "origine": true : la parole d'origine est gardée telle quelle (mot qui n'est pas dans la langue source :
« Ummi », « Alhamdulillah »…). Écrit voix/mix_<a|b>.wav et affiche le retard de chaque réplique (garder sous 0,8 s)."""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf, librosa
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import charger

av = sys.argv[1:]
fin = None
if "--fin" in av:
    i = av.index("--fin"); fin = float(av[i + 1]); del av[i:i + 2]
d, moteur = av[0], av[1]
SR = 44100
lignes, _ = charger(d)
fond, _ = sf.read(os.path.join(d, "sep", "fond.wav"), always_2d=True)
pa, psr = sf.read(os.path.join(d, "sep", "parole.wav"), always_2d=True)
parole = librosa.resample(pa.mean(axis=1), orig_sr=psr, target_sr=SR)
n = len(fond) if fin is None else int(fin * SR)
mix = fond[:n].copy()

def rms(x):
    x = x[np.abs(x) > 1e-4]
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0

def fondus(v, s):
    f = int(s * SR); v[:f] *= np.linspace(0, 1, f); v[-f:] *= np.linspace(1, 0, f); return v

fin_prec, retard_max = 0.0, 0.0
for l in lignes:
    if fin and l["debut"] >= fin:
        continue
    if l.get("origine"):
        a, b = int(max(0, l["debut"] - 0.05) * SR), int((l["fin"] + 0.12) * SR)
        v = fondus(parole[a:b].copy(), 0.02)
        debut = max(l["debut"] - 0.05, fin_prec + 0.05)
        a = int(debut * SR); e = min(n, a + len(v)); mix[a:e] += v[: e - a, None]; fin_prec = debut + len(v) / SR
        print(f"{l['id']} : {debut:.2f}-{fin_prec:.2f} s, voix d'origine gardée"); continue
    p = os.path.join(d, "voix", moteur, f"{l['id']}.wav")
    if not os.path.exists(p):
        print(f"{l['id']} : MANQUE {p}"); continue
    v, vsr = sf.read(p, always_2d=True)
    v, _ = librosa.effects.trim(librosa.resample(v.mean(axis=1), orig_sr=vsr, target_sr=SR), top_db=35)
    if l.get("duree_origine"):  # calé par caler.py : même durée que la parole d'origine (0,87 à 1,18 au plus)
        tempo = min(1.18, max(0.87, len(v) / SR / l["duree_origine"]))
    else:
        tempo = min(1.15, max(1.0, len(v) / SR / l["place"]))
    if abs(tempo - 1) > 0.01:
        with tempfile.TemporaryDirectory() as t:
            sf.write(f"{t}/a.wav", v, SR)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{t}/a.wav", "-af", f"atempo={tempo:.3f}", f"{t}/b.wav"], check=True)
            v, _ = sf.read(f"{t}/b.wav")
    a, b = int(l["debut"] * SR), int(l["fin"] * SR)
    ref = rms(parole[a:b])
    # voix toujours bien au-dessus du fond (8 dB au moins) : une réplique chuchotée dans l'original devient
    # incompréhensible en traduction (« Ne cours pas » entendu « Le coup de pas », Reel IGDGB du 28/11/2026)
    ref = max(ref, rms(fond[a:b].mean(axis=1)) * 10 ** (8 / 20))
    if ref > 0 and rms(v) > 0:
        v = v * (ref / rms(v))
    v = fondus(v, 0.01)
    debut = max(l["debut"], fin_prec + (0.05 if l.get("duree_origine") else 0.1))
    a = int(debut * SR); e = min(n, a + len(v)); mix[a:e] += v[: e - a, None]
    fin_prec = debut + len(v) / SR; retard_max = max(retard_max, debut - l["debut"])
    print(f"{l['id']} : {debut:.2f}-{fin_prec:.2f} s (retard {debut-l['debut']:.2f} s, vitesse {tempo:.2f})")
pic = np.abs(mix).max()
if pic > 0.98:
    mix *= 0.98 / pic
sortie = os.path.join(d, "voix", f"mix_{moteur}.wav")
sf.write(sortie, mix, SR)
print(f"écrit {sortie} | retard maximal {retard_max:.2f} s")
