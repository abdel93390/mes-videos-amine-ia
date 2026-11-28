#!/usr/bin/env bash
# Voix gratuite d'une vidéo, de bout en bout, sans service payant (voir LISEZMOI.md).
# Usage :
#   bash voix.sh <dossier> separer          # paroles isolées + fond (musique, chant) : sep/parole.wav, sep/fond.wav
#   bash voix.sh <dossier> refs             # voix de référence de chaque personnage (voix/refs.json)
#   bash voix.sh <dossier> caler [--ecrire] # début réel, durée et pauses de chaque réplique d'origine (voir caler.py)
#   bash voix.sh <dossier> a|b [--prises 3] [--fin 30] [ids...]
#       génère (un processus par personnage), choisit la meilleure prise, mixe : voix/mix_<a|b>.wav
#   bash voix.sh <dossier> rendre a|b <sortie.mp4> [--fin 30]   # vidéo finale en 1080 de large (règle de l'élève)
set -e
ICI="$(cd "$(dirname "$0")" && pwd)"
C="${VOIX_GRATUITE_CACHE:-$HOME/.cache/voix-gratuite}"
D="$1"; ETAPE="$2"; shift 2
[ -d "$D" ] || { echo "dossier introuvable : $D"; exit 1; }

case "$ETAPE" in
separer)
  bash "$ICI/installer.sh" sep
  "$C/sep/bin/python" "$ICI/separer.py" "$D" ;;
refs)
  bash "$ICI/installer.sh" sep
  "$C/sep/bin/python" "$ICI/refs.py" "$D" ;;
caler)
  bash "$ICI/installer.sh" sep
  "$C/sep/bin/python" "$ICI/caler.py" "$D" "$@" ;;
a|b)
  M="$ETAPE"; [ "$M" = a ] && ENV=qwen || ENV=voxcpm
  bash "$ICI/installer.sh" sep "$ENV"
  PRISES=3; FIN=""; IDS=()
  while [ $# -gt 0 ]; do
    case "$1" in --prises) PRISES="$2"; shift 2 ;; --fin) FIN="$2"; shift 2 ;; *) IDS+=("$1"); shift ;; esac
  done
  PERSOS=$("$C/sep/bin/python" -c "import json,sys;l=json.load(open('$D/voix/lignes.json'));f=float('${FIN:-1e9}');print(' '.join(dict.fromkeys(x['perso'] for x in l if x['debut']<f and not x.get('origine'))))")
  for P in $PERSOS; do
    if [ ${#IDS[@]} -eq 0 ] && [ -n "$FIN" ]; then
      SEL=$("$C/sep/bin/python" -c "import json;l=json.load(open('$D/voix/lignes.json'));print(' '.join(x['id'] for x in l if x['perso']=='$P' and x['debut']<$FIN))")
    else SEL="${IDS[*]}"; fi
    # un processus par personnage : la mémoire repart de zéro (voix A)
    "$C/$ENV/bin/python" "$ICI/generer_$M.py" "$D" "$P" --prises "$PRISES" $SEL 2>&1 | grep --line-buffered -E "chargée|prise|_[0-9]+ :|Traceback|Error|Killed" || true
  done
  "$C/sep/bin/python" "$ICI/choisir.py" "$D" "$M" 2>&1 | grep --line-buffered -vE "Warning|warn|HF_TOKEN|^\s*$"
  "$C/sep/bin/python" "$ICI/mixer.py" "$D" "$M" ${FIN:+--fin $FIN} ;;
rendre)
  M="$1"; SORTIE="$2"; shift 2; FIN=""
  [ "$1" = "--fin" ] && FIN="$2"
  # 1080 de large (1080x1920 en vertical), même filtre que la règle de l'élève ; vise moins de 100 Mo
  ffmpeg -v error -y ${FIN:+-t $FIN} -i "$D/src.mp4" -i "$D/voix/mix_$M.wav" -map 0:v -map 1:a \
    -vf "hqdn3d=1.5:1.5:0:0,scale=1080:-2:flags=lanczos,unsharp=5:5:0.9:3:3:0.0" \
    -c:v libx264 -preset slow -crf 18 -maxrate 3400k -bufsize 6800k -profile:v high -pix_fmt yuv420p \
    -c:a aac -b:a 192k -movflags +faststart -shortest "$SORTIE"
  echo "écrit $SORTIE" ;;
*) echo "étape inconnue : $ETAPE (separer, refs, a, b, rendre)"; exit 1 ;;
esac
