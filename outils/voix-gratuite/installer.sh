#!/usr/bin/env bash
# Installe les outils de voix gratuite (une fois par session) dans ~/.cache/voix-gratuite :
#   sep    : séparation voix/musique (demucs), parole isolée du chant (MossFormer2), choix des prises (ECAPA), mixage
#   qwen   : voix A (Qwen3-TTS 1.7B Base)
#   voxcpm : voix B (VoxCPM2)
# Usage : bash installer.sh [sep] [qwen] [voxcpm]   (sans argument : les trois)
# Chaque partie prend 3 à 5 min ; les modèles se téléchargent au premier usage (Hugging Face).
# Rien n'est installé dans le dépôt : le cache n'est jamais versionné.
set -e
C="${VOIX_GRATUITE_CACHE:-$HOME/.cache/voix-gratuite}"
mkdir -p "$C"
PARTIES="${*:-sep qwen voxcpm}"
CPU=https://download.pytorch.org/whl/cpu

creer() {  # creer <dossier> <python>
  rm -rf "$1"
  if command -v uv >/dev/null; then uv venv -q -p "$2" "$1"; else "$2" -m venv "$1"; "$1/bin/pip" install -q --upgrade pip; fi
}
pipi() {  # pipi <dossier> <arguments pip...>
  local d="$1"; shift
  if command -v uv >/dev/null; then uv pip install -q --python "$d/bin/python" "$@"; else "$d/bin/pip" install -q "$@"; fi
}

for p in $PARTIES; do
  case "$p" in
  sep)
    # Python 3.11 : ClearVoice demande numpy<2. demucs sans ses dépendances (il bloque torchaudio<2.1, inutile ici).
    if ! "$C/sep/bin/python" -c "import torch, demucs, clearvoice, librosa, soundfile, speechbrain; assert speechbrain.__version__ >= '1.1'; from speechbrain.inference.speaker import EncoderClassifier" 2>/dev/null; then
      echo "installation : séparation et choix des prises (quelques minutes)..."
      PY=$(command -v python3.11 || command -v python3.12)
      creer "$C/sep" "$PY"
      pipi "$C/sep" torch==2.7.1 torchaudio==2.7.1 torchvision==0.22.1 --index-url $CPU
      pipi "$C/sep" clearvoice==0.1.2 speechbrain==1.1.2 soundfile librosa
      pipi "$C/sep" --no-deps demucs==4.0.1
      pipi "$C/sep" dora-search einops julius lameenc openunmix pyyaml tqdm
    fi ;;
  qwen)
    if ! "$C/qwen/bin/python" -c "import qwen_tts, torch" 2>/dev/null; then
      echo "installation : voix A (quelques minutes)..."
      PY=$(command -v python3.13 || command -v python3.12 || command -v python3.11)
      creer "$C/qwen" "$PY"
      pipi "$C/qwen" torch==2.6.0 torchaudio==2.6.0 --index-url $CPU
      pipi "$C/qwen" qwen-tts==0.1.1
    fi ;;
  voxcpm)
    if ! "$C/voxcpm/bin/python" -c "import voxcpm, torch" 2>/dev/null; then
      echo "installation : voix B (quelques minutes)..."
      PY=$(command -v python3.13 || command -v python3.12 || command -v python3.11)
      creer "$C/voxcpm" "$PY"
      pipi "$C/voxcpm" torch torchaudio --index-url $CPU
      pipi "$C/voxcpm" voxcpm==2.0.3
    fi ;;
  *) echo "partie inconnue : $p (sep, qwen ou voxcpm)"; exit 1 ;;
  esac
done
echo "voix gratuite prête ($PARTIES)"
