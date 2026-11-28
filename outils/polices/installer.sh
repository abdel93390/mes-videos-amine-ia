#!/usr/bin/env bash
# Copie les polices du dépôt là où rendu.py les cherche (~/.local/share/fonts).
mkdir -p ~/.local/share/fonts && cp -n "$(dirname "$0")"/*.ttf ~/.local/share/fonts/ && echo "polices installées : $(ls "$(dirname "$0")"/*.ttf | xargs -n1 basename | tr '\n' ' ')"
