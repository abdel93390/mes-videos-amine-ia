#!/usr/bin/env bash
# Installe l'effaceur gratuit (une fois par session, environ 3 à 5 min) dans ~/.cache/effaceur :
# un Python à part avec torch (version processeur), OpenCV, numpy, scipy, et le modèle LaMa (205 Mo).
# Ne rien installer dans le dépôt : le dossier du cache n'est jamais versionné.
set -e
C="${EFFACEUR_CACHE:-$HOME/.cache/effaceur}"
mkdir -p "$C"
PYV="$C/env/bin/python"

if ! "$PYV" -c "import torch, cv2, scipy, numpy" 2>/dev/null; then
  echo "installation des outils de l'effaceur (quelques minutes)..."
  PY=$(command -v python3.12 || command -v python3.11 || command -v python3)
  rm -rf "$C/env"
  if command -v uv >/dev/null; then
    uv venv -q -p "$PY" "$C/env"
    uv pip install -q --python "$PYV" torch==2.7.0 --index-url https://download.pytorch.org/whl/cpu
    uv pip install -q --python "$PYV" opencv-python-headless numpy scipy
  else
    "$PY" -m venv "$C/env"
    "$C/env/bin/pip" install -q torch==2.7.0 --index-url https://download.pytorch.org/whl/cpu
    "$C/env/bin/pip" install -q opencv-python-headless numpy scipy
  fi
fi

# Modèle LaMa (big-lama, licence Apache 2.0), copie publiée par le projet video-subtitle-remover (Apache 2.0)
M="$C/big-lama.pt"
EMPREINTE=19970cd5673cd1326c70885ea2b5dbb8
if [ "$(md5sum "$M" 2>/dev/null | cut -c1-32)" != "$EMPREINTE" ]; then
  echo "téléchargement du modèle LaMa (205 Mo)..."
  B=https://raw.githubusercontent.com/YaoFANGUK/video-subtitle-remover/e109b9ddc1d0e8f153199dfa05c1d767546906d8/backend/models/big-lama
  rm -f "$M.tmp"
  for i in 1 2 3 4 5; do curl -sfL --retry 3 "$B/big-lama_$i.pt" >> "$M.tmp"; done
  if [ "$(md5sum "$M.tmp" | cut -c1-32)" != "$EMPREINTE" ]; then
    rm -f "$M.tmp"; echo "ERREUR : modèle LaMa incomplet ou modifié, relancer l'installation"; exit 1
  fi
  mv "$M.tmp" "$M"
fi
echo "effaceur prêt"
