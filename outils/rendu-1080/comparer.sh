#!/usr/bin/env bash
# Vidéo comparative : 2 ou 3 vidéos côte à côte, synchronisées, avec une étiquette en haut de chacune ; son de la dernière.
# Usage : bash comparer.sh <sortie.mp4> "<étiquette 1>" <video1> "<étiquette 2>" <video2> ["<étiquette 3>" <video3>]
# Chaque partie en 540x960 (vertical). Moins de 200 Mo pour 8 min.
set -e
out=$1; shift; F="$(cd "$(dirname "$0")/.." && pwd)/polices/Poppins-Bold.ttf"
args=(); filt=""; n=0; lab=""
while [ $# -ge 2 ]; do
  args+=(-i "$2"); e=$(printf '%s' "$1" | sed "s/'/’/g; s/:/\\\\:/g")
  filt+="[$n:v]scale=540:960:flags=lanczos,setsar=1,drawtext=fontfile=$F:text='$e':fontsize=28:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=12:x=(w-tw)/2:y=24[v$n];"
  lab+="[v$n]"; n=$((n+1)); shift 2
done
ffmpeg -v error -y "${args[@]}" -filter_complex "${filt}${lab}hstack=inputs=$n,format=yuv420p[v]" -map "[v]" -map "$((n-1)):a?" -c:v libx264 -preset medium -crf 22 -maxrate 2500k -bufsize 5000k -c:a aac -b:a 128k -movflags +faststart -shortest "$out"
echo "écrit : $out"
