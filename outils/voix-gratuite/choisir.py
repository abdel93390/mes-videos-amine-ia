"""Choisit la meilleure prise de chaque réplique :
1) les mots justes (réécoute Whisper par Groq, gratuite) ; 2) parmi elles, la plus proche de la voix d'origine du personnage
(empreinte de voix ECAPA, SpeechBrain, Apache 2.0) ; 3) celle qui rentre dans sa place.
Usage : python choisir.py <dossier> <a|b>
Écrit voix/<a|b>/<id>.wav (prise gardée) et choix.json. Les réécoutes sont gardées dans ecoutes.json :
relancer ne refait pas d'appel. Affiche les répliques à revoir (mots < 0,9)."""
import json, os, sys, glob, time, subprocess, difflib, re, shutil, unicodedata
import numpy as np, soundfile as sf, librosa, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import charger, langue, CACHE
from speechbrain.inference.speaker import EncoderClassifier

d, moteur = sys.argv[1], sys.argv[2]
lignes, refs = charger(d, moteur)
code = langue(d)
dv = os.path.join(d, "voix", moteur)
enc = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir=os.path.join(CACHE, "ecapa"),
                                     run_opts={"device": "cpu"})

def emb(p):
    y, sr = sf.read(p, always_2d=True)
    y = librosa.resample(y.mean(axis=1), orig_sr=sr, target_sr=16000)
    with torch.no_grad():
        e = enc.encode_batch(torch.tensor(y, dtype=torch.float32)[None]).squeeze()
    return (e / e.norm()).numpy()

ref_emb = {p: emb(os.path.join(d, r["audio"])) for p, r in refs.items()}

def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    for a, b in (("oummi", "ummi"), ("oumi", "ummi"), ("alhamdoulillah", "alhamdulillah"), ("alhamdoulilah", "alhamdulillah"),
                 ("soubhanallah", "subhanallah"), ("hadji", "haji")):
        t = t.replace(a, b)
    t = re.sub(r"\b(oumi|umi|oumy|umy|oummi)\b", "ummi", t)
    mots = re.sub(r"[^a-z ]", " ", t.replace("'", " ")).split()
    # « nourri » / « nourrie » / « nourris » se prononcent pareil : ne pas compter la fin muette
    return [m.rstrip("s").rstrip("e") if len(m) > 3 else m for m in mots]

fe = os.path.join(dv, "ecoutes.json")
ecoutes = json.load(open(fe, encoding="utf-8")) if os.path.exists(fe) else {}

def ecoute(p):
    k = os.path.basename(p)
    if k in ecoutes:
        return ecoutes[k]
    for essai in range(5):
        r = subprocess.run(["curl", "-s", "https://api.groq.com/openai/v1/audio/transcriptions", "-H", "Authorization: Bearer cloud",
                            "-H", "User-Agent: amine", "-F", "model=whisper-large-v3", "-F", f"language={code}",
                            "-F", "response_format=text", "-F", f"file=@{p}"], capture_output=True, text=True).stdout
        if r and not r.lstrip().startswith("{"):
            ecoutes[k] = r.strip()
            json.dump(ecoutes, open(fe, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
            time.sleep(3)  # palier gratuit Groq : 20 demandes par minute
            return ecoutes[k]
        time.sleep(15)
    return ""

choix, revoir = {}, []
for l in lignes:
    if l.get("origine"):
        continue
    prises = []
    for p in sorted(glob.glob(os.path.join(dv, f"{l['id']}_*.wav"))):
        v, sr = sf.read(p)
        _, (a, b) = librosa.effects.trim(v, top_db=35)
        duree = (b - a) / sr
        txt = ecoute(p)
        mots = difflib.SequenceMatcher(None, norm(l["texte"]), norm(txt)).ratio()
        voix = float(np.dot(emb(p), ref_emb[l["perso"]]))
        prises.append(dict(p=p, mots=mots, voix=voix, d=duree, trop=max(0, duree / l["place"] - 1), txt=txt))
    if not prises:
        print(f"{l['id']} : AUCUNE PRISE"); revoir.append(l["id"]); continue
    meilleur = max(x["mots"] for x in prises)
    bonnes = [x for x in prises if x["mots"] >= max(0.9, meilleur - 0.02)] or [max(prises, key=lambda x: x["mots"])]
    best = max(bonnes, key=lambda x: x["voix"] - 0.3 * x["trop"])
    shutil.copy(best["p"], os.path.join(dv, f"{l['id']}.wav"))
    choix[l["id"]] = {"prise": os.path.basename(best["p"]), "mots": round(best["mots"], 2), "ressemblance": round(best["voix"], 2),
                      "duree": round(best["d"], 2), "place": l["place"], "entendu": best["txt"]}
    if best["mots"] < 0.9:
        revoir.append(l["id"])
    print(f"{l['id']} -> {os.path.basename(best['p'])} | mots {best['mots']:.2f} | ressemblance {best['voix']:.2f} | "
          f"{best['d']:.1f}/{l['place']:.1f} s | {best['txt']}", flush=True)
json.dump(choix, open(os.path.join(dv, "choix.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("à revoir (mots mal entendus) :", ", ".join(revoir) if revoir else "aucune")
