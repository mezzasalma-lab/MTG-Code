#!/bin/bash
# Refaz a tabela da nova linha de base SO' dos brutos arquivados na pasta irma (`../2026-10-10-underground-sea-sem-bojuka/dados`) e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh
cd "$(dirname "$0")"
python3 base_nova.py > /tmp/base_nova_refeita.md
if cmp -s /tmp/base_nova_refeita.md ../resumos/base_nova.md; then echo "IGUAL  base_nova.md (refeita so' dos brutos da pasta irma)"; echo "1/1 saidas iguais"; else echo "DIFERE base_nova.md"; echo "0/1 saidas iguais"; fi
rm -f /tmp/base_nova_refeita.md
