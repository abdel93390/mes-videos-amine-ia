"""Voix B (VoxCPM2, Apache 2.0, 30 langues) : copie la voix d'origine et joue l'émotion de la réplique.
Usage : python generer_b.py <dossier> <perso> [--prises 3] [ids...]
Prises : 1 = voix de référence seule, 2 = référence + consigne de ton ("style" de la ligne, sinon celui du personnage),
3 = référence seule, autre tirage ; au-delà, on alterne. Le mode « référence + transcription » donnait de mauvais mots (27/11/2026).
Écrit voix/b/<id>_<k>.wav ; environ 10 s par prise sur 4 cœurs. Il faut des références propres (sep/parole.wav)."""
import os, sys, time
import soundfile as sf, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import charger, langue, LANGUES_B
from voxcpm import VoxCPM

av = sys.argv[1:]
prises = 3
if "--prises" in av:
    i = av.index("--prises"); prises = int(av[i + 1]); del av[i:i + 2]
d, perso, ids = av[0], av[1], set(av[2:])
lignes, refs = charger(d, "b")
code = langue(d)
if code not in LANGUES_B:
    raise SystemExit(f"la voix B ne parle pas « {code} »")
out = os.path.join(d, "voix", "b"); os.makedirs(out, exist_ok=True)
tous = [l for l in lignes if l["perso"] == perso and not l.get("origine") and (not ids or l["id"] in ids)]
if not tous:
    raise SystemExit(0)
torch.set_num_threads(os.cpu_count() or 4)
t0 = time.time()
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False, device="cpu")
sr = m.tts_model.sample_rate
r = refs[perso]
print(f"voix B chargée en {time.time()-t0:.0f} s ({perso}, {len(tous)} phrases, langue {code})", flush=True)
for l in tous:
    for k in range(1, prises + 1):
        p = os.path.join(out, f"{l['id']}_{k}.wav")
        if os.path.exists(p):
            continue
        t = time.time(); torch.manual_seed(k)
        texte = l["texte"]
        if k % 2 == 0:
            texte = f"({l.get('style') or r.get('style', '')}){texte}"
        w = m.generate(text=texte, reference_wav_path=os.path.join(d, r["audio"]), cfg_value=2.0, inference_timesteps=10)
        sf.write(p, w, sr)
        print(f"{l['id']}_{k} : {len(w)/sr:.1f} s en {time.time()-t:.0f} s", flush=True)
