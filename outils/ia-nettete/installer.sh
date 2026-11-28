#!/usr/bin/env bash
# Installe l'IA de netteté (Real-ESRGAN, licence BSD-3 : pubs autorisées) sur la machine de la session : PyTorch processeur + 2 modèles.
# Environ 3 min, 0 €. Rien à refaire tant que la session tourne (dossier ~/.cache/sr).
set -e
D=~/.cache/sr; mkdir -p "$D"; cd "$D"
[ -x env/bin/python ] || python3 -m venv env
env/bin/python -c "import torch" 2>/dev/null || { env/bin/pip install -q --upgrade pip; env/bin/pip install -q torch --index-url https://download.pytorch.org/whl/cpu; env/bin/pip install -q numpy pillow; }
[ -s general-x4v3.pth ] || curl -sL -o general-x4v3.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth
[ -s animevideov3.pth ] || curl -sL -o animevideov3.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth
env/bin/python -c "import torch; print('IA de netteté prête : torch', torch.__version__)"
grep -q -E "amx_bf16|avx512_bf16" /proc/cpuinfo && echo "processeur avec calcul bfloat16 : environ 0,5 s par image (modèle général)" || echo "processeur SANS bfloat16 : compter 2,5 s par image (modèle général), 1,3 s (animation)"
