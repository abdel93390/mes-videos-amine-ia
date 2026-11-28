#!/usr/bin/env bash
# Installe ce qu'il faut pour fond_reel.py : PyTorch processeur + modèle LaMa (Apache 2.0). Environ 3 min, 0 €.
set -e
python3 -c "import torch" 2>/dev/null || pip install -q torch --index-url https://download.pytorch.org/whl/cpu
python3 -c "import scipy, PIL" 2>/dev/null || pip install -q scipy pillow
mkdir -p ~/.cache/lama
[ -s ~/.cache/lama/big-lama.pt ] || curl -sL -o ~/.cache/lama/big-lama.pt https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt
echo "fond réel prêt"
