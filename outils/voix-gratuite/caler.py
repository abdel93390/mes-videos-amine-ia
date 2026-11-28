"""Cale chaque réplique sur la vraie parole d'origine (sep/parole.wav), pour que la voix traduite tombe sur la bouche.
Usage : python caler.py <dossier> [--ecrire]
Pour chaque ligne de voix/lignes.json, cherche la parole entre la fin de la ligne précédente et le début de la suivante :
- début réel (Whisper le donne souvent 0,3 s trop tard) et fin réelle -> "debut", "duree_origine" ;
- pauses de plus de 0,45 s au milieu -> à couper en deux lignes (S1a, S1b), chacune avec son début ;
- durée cible et nombre de caractères conseillé pour la traduction (environ 15 caractères par seconde pour ces voix).
Sans --ecrire : affiche seulement le rapport. Avec --ecrire : met à jour debut et duree_origine dans lignes.json.
Après la génération, mixer.py étire chaque réplique (0,87 à 1,18) pour qu'elle dure comme l'original."""
import json, os, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import charger

d = sys.argv[1]; ecrire = "--ecrire" in sys.argv
CAR_PAR_S = 15
lignes, _ = charger(d)
y, sr = sf.read(os.path.join(d, "sep", "parole.wav"))
if y.ndim > 1:
    y = y.mean(axis=1)
PAS = 0.02; h = int(PAS * sr)
e = np.array([np.sqrt(np.mean(y[i:i + h] ** 2)) for i in range(0, len(y) - h, h)])
db = 20 * np.log10(e + 1e-9)
seuil = np.percentile(db, 95) - 25  # parole = moins de 25 dB sous les passages forts

def segments(a, b):
    i0, i1 = max(0, int(a / PAS)), min(len(db), int(b / PAS))
    segs, s = [], None
    for k in range(i0, i1):
        if db[k] > seuil and s is None: s = k * PAS
        if db[k] <= seuil and s is not None: segs.append([s, k * PAS]); s = None
    if s is not None: segs.append([s, i1 * PAS])
    out = []
    for s_ in segs:  # trous de moins de 0,25 s = même mot ; bouts de moins de 0,1 s = bruit
        if out and s_[0] - out[-1][1] < 0.25: out[-1][1] = s_[1]
        else: out.append(s_)
    return [[round(p, 2), round(q, 2)] for p, q in out if q - p >= 0.1]

fin_prec = 0.0
for i, l in enumerate(lignes):
    suivante = lignes[i + 1]["debut"] if i + 1 < len(lignes) else l["fin"] + 1.0
    a = max(fin_prec, l["debut"] - 0.35)
    b = min(suivante - 0.05, l["fin"] + 0.5) if suivante > l["debut"] else l["fin"] + 0.5
    s = segments(a, b)
    if not s:
        print(f"{l['id']:5} pas de parole trouvée entre {a:.2f} et {b:.2f} : garder les temps de Whisper"); continue
    debut, fin = s[0][0], s[-1][1]
    if debut <= a + 0.04:  # un son durait déjà au début de la fenêtre (pleurs, chant) : le début mesuré n'est pas fiable
        debut = max(debut, l["debut"]); s[0][0] = debut
    pauses = [(s[k][1], s[k + 1][0]) for k in range(len(s) - 1) if s[k + 1][0] - s[k][1] >= 0.45]
    cible = fin - debut
    conseil = f"{int(cible * CAR_PAR_S * 0.85)}-{int(cible * CAR_PAR_S * 1.1)} car."
    alerte = ""
    n = len(l["texte"])
    if n < cible * CAR_PAR_S * 0.7: alerte = "TROP COURT : rallonger la traduction"
    if n > cible * CAR_PAR_S * 1.25: alerte = "TROP LONG : raccourcir"
    coupe = " | À COUPER aux pauses : " + ", ".join(f"{p:.2f}-{q:.2f}" for p, q in pauses) if pauses and not l.get("origine") else ""
    print(f"{l['id']:5} {l['perso']:10} {debut:6.2f}-{fin:6.2f} ({cible:.1f} s, conseil {conseil}, texte {n}) "
          f"décalage {debut - l['debut']:+.2f} s {alerte}{coupe}")
    if ecrire:
        l["debut"] = debut; l["duree_origine"] = round(cible, 2); l["fin"] = max(l["fin"], fin) if l.get("origine") else fin
        l.pop("place", None)
    fin_prec = fin
if ecrire:
    json.dump(lignes, open(os.path.join(d, "voix", "lignes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("lignes.json mis à jour (debut réel, duree_origine)")
