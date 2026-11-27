#!/usr/bin/env bash
# Efface les sous-titres incrustés d'une vidéo, gratuitement (à la place de Vmake).
# Usage : bash effacer.sh <entree.mp4> <sortie.mp4> [--duree 10] [--apercu avant_apres.jpg] [--bande Y0 Y1] [--masque masque.mp4]
# Installe ce qu'il faut au premier appel de la session, puis lance effacer.py (détails : son en-tête).
set -e
[ $# -ge 2 ] || { sed -n 2,4p "$0"; exit 1; }
ici="$(cd "$(dirname "$0")" && pwd)"
C="${EFFACEUR_CACHE:-$HOME/.cache/effaceur}"
bash "$ici/installer.sh"
exec "$C/env/bin/python" "$ici/effacer.py" "$@" --modele "$C/big-lama.pt"
