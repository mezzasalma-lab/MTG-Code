#!/bin/bash
# Refaz as tabelas do A/B SO' a partir dos brutos arquivados (.json.xz, `driver.py sum`) e compara byte a byte (cmp) com os resumos salvos; testa os .xz e confere o SHA256SUMS da pasta.
# Uso (de qualquer pasta):  bash verificar_reproducao.sh
# NAO re-executa as simulacoes (A/B, regressao, bit-identidade, determinismo: saidas das execucoes originais; ver o LEIAME). NAO edite o simulador enquanto roda outra verificacao.
cd "$(dirname "$0")" || exit 2
ok=0; ruim=0
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/resumos"
cmpf() { if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL   | $1"; ok=$((ok+1)); else echo "DIFERE  | $1"; ruim=$((ruim+1)); fi; }
for f in ../dados/*.xz; do if xz -t "$f"; then echo "XZ ok   | $f"; ok=$((ok+1)); else echo "XZ RUIM | $f"; ruim=$((ruim+1)); fi; done
DRIVER_OUT="$tmp" python3 driver.py config.json sum > /dev/null
for f in ab_2000.txt ab_10000.txt ab_2000_resiliencia.txt ab_10000_resiliencia.txt; do cmpf $f; done
if [ -f ../SHA256SUMS ]; then if (cd .. && sha256sum -c --quiet SHA256SUMS); then echo "SHA256  | SHA256SUMS confere"; ok=$((ok+1)); else echo "SHA256  | SHA256SUMS NAO confere"; ruim=$((ruim+1)); fi; fi
echo "---"; echo "$ok conferencias ok, $ruim falhas"
[ "$ruim" -eq 0 ]
