#!/bin/bash
# rend chaque SVG v2 en PNG transparent (2000 px horizontal/vertical, 1024 px icône)
cd "$(dirname "$0")"
for f in v2/*/*.svg; do
  case "$f" in *icone*) w=1024; bg='#ffffff';; *) w=2000; bg=transparent;; esac
  node render.js "${f%.svg}.png" $w $bg "$f"
done
