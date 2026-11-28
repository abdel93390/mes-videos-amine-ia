"""Voix A (Qwen3-TTS 1.7B Base, Apache 2.0) : chaque personnage garde sa voix d'origine et parle la langue cible.
Usage : python generer_a.py <dossier> <perso> [--prises 3] [ids...]
Un seul personnage par appel : la mémoire monte à chaque génération sur processeur (tué vers 14 Go le 27/11/2026),
voix.sh relance donc un processus par personnage. Lots de 6 phrases au plus. Les prises déjà faites sont gardées.
Écrit voix/a/<id>_<k>.wav ; environ 10 s par phrase et par prise sur 4 cœurs."""
import os, sys, time
import soundfile as sf, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import charger, langue, LANGUES_A
from qwen_tts import Qwen3TTSModel

av = sys.argv[1:]
prises = 3
if "--prises" in av:
    i = av.index("--prises"); prises = int(av[i + 1]); del av[i:i + 2]
d, perso, ids = av[0], av[1], set(av[2:])
lignes, refs = charger(d, "a")
code = langue(d)
if code not in LANGUES_A:
    raise SystemExit(f"la voix A ne parle pas « {code} » : prendre la voix B")
out = os.path.join(d, "voix", "a"); os.makedirs(out, exist_ok=True)
tous = [l for l in lignes if l["perso"] == perso and not l.get("origine") and (not ids or l["id"] in ids)]
if not tous:
    raise SystemExit(0)
torch.set_num_threads(os.cpu_count() or 4)
t0 = time.time()
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32)
r = refs[perso]
prompt = m.create_voice_clone_prompt(ref_audio=os.path.join(d, r["audio"]), ref_text=r["texte"], x_vector_only_mode=False)
print(f"voix A chargée en {time.time()-t0:.0f} s ({perso}, {len(tous)} phrases, langue {code})", flush=True)
for i in range(0, len(tous), 6):
    ls = tous[i:i + 6]
    for k in range(1, prises + 1):
        if all(os.path.exists(os.path.join(out, f"{l['id']}_{k}.wav")) for l in ls):
            continue
        t = time.time(); torch.manual_seed(k)
        wavs, sr = m.generate_voice_clone(text=[l["texte"] for l in ls], language=[LANGUES_A[code]] * len(ls),
                                          voice_clone_prompt=prompt * len(ls), max_new_tokens=400)
        for l, w in zip(ls, wavs):
            sf.write(os.path.join(out, f"{l['id']}_{k}.wav"), w, sr)
        print(f"{perso} prise {k} : {len(ls)} phrases en {time.time()-t:.0f} s | " +
              " ".join(f"{l['id']}={len(w)/sr:.1f}s" for l, w in zip(ls, wavs)), flush=True)
