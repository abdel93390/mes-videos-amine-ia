"""Fonctions communes aux outils de voix gratuite."""
import json, os

VERSION = "v1 (28/11/2026)"
CACHE = os.environ.get("VOIX_GRATUITE_CACHE", os.path.expanduser("~/.cache/voix-gratuite"))

# Langues : code court -> nom attendu par la voix A (Qwen3-TTS). La voix B (VoxCPM2) n'a pas besoin du nom.
LANGUES_A = {"fr": "french", "en": "english", "de": "german", "es": "spanish", "it": "italian", "pt": "portuguese",
             "ru": "russian", "ja": "japanese", "ko": "korean", "zh": "chinese"}
LANGUES_B = {"ar", "my", "da", "nl", "fi", "fr", "de", "el", "he", "hi", "id", "it", "ja", "km", "ko", "lo", "ms", "no",
             "pl", "pt", "ru", "es", "sw", "sv", "tl", "th", "tr", "vi", "zh", "en"}


def charger(dossier):
    """Lit <dossier>/voix/lignes.json et refs.json ; complète 'place' (temps disponible jusqu'à la réplique suivante)."""
    v = os.path.join(dossier, "voix")
    lignes = json.load(open(os.path.join(v, "lignes.json"), encoding="utf-8"))
    refs = json.load(open(os.path.join(v, "refs.json"), encoding="utf-8"))
    for i, l in enumerate(lignes):
        if "place" not in l:
            suivante = lignes[i + 1]["debut"] if i + 1 < len(lignes) else l["fin"] + 1.0
            l["place"] = round(max(l["fin"] - l["debut"], suivante - l["debut"] - 0.1), 2)
    return lignes, refs


def langue(dossier):
    """Langue cible : voix/reglages.json {"langue": "fr"} sinon fiche.json langue_cible, sinon fr."""
    for f in ("voix/reglages.json", "fiche.json"):
        p = os.path.join(dossier, f)
        if os.path.exists(p):
            d = json.load(open(p, encoding="utf-8"))
            if d.get("langue") or d.get("langue_cible"):
                return d.get("langue") or d.get("langue_cible")
    return "fr"
