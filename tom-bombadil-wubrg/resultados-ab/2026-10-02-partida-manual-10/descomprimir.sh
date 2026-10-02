#!/bin/bash
# Descomprime os dados brutos (mantém os .xz). Rodar dentro desta pasta.
set -e
cd "$(dirname "$0")"
for f in dados/*.xz; do xz -dk -f "$f"; done
echo "ok: $(ls dados/*.json | wc -l) arquivo(s) .json em dados/"
