#!/bin/bash
# Verificacao de reprodutibilidade. Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) refaz as tabelas SO' dos .json.xz (mill_oponentes.py --do-bruto) e compara com `cmp` (sem as linhas de auto-verificacao, que exigem simular);
#  --tudo      alem disso RE-SIMULA o lote de resiliencia , a frequencia do annihilator e o teto do crime/Deepmuck (PYTHONHASHSEED=777, diferente do original) e compara o bruto descomprimido e o texto inteiro.
# NAO edite o simulador enquanto roda.
set -u
AQUI="$(cd "$(dirname "$0")/.." && pwd)"
DECK="$(cd "$AQUI/../.." && pwd)"
T="$(mktemp -d)"
ok=0; falha=0
cmp_ok() { if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; falha=$((falha+1)); fi; }
for m in padrao resiliencia; do
  python3 "$DECK/ferramentas/mill_oponentes.py" --do-bruto "$AQUI/dados/mill_oponentes_${m}_5000.json.xz" -o "$T/$m.txt" > /dev/null
  grep -v '^auto-verificacao' "$AQUI/resumos/mill_oponentes_${m}_5000.txt" > "$T/${m}_arq.txt"
  cmp_ok "$T/$m.txt" "$T/${m}_arq.txt" "tabela $m refeita so' do bruto"
done
if [ "${1:-}" = "--tudo" ]; then
  PYTHONHASHSEED=777 python3 "$DECK/ferramentas/mill_oponentes.py" -n 5000 --modo resiliencia -v base -v pacote5+master -o "$T/resim.txt" --bruto "$T/resim.json.xz" > /dev/null
  xz -dc "$AQUI/dados/mill_oponentes_resiliencia_5000.json.xz" > "$T/arq.json"; xz -dc "$T/resim.json.xz" > "$T/resim.json"
  [ -s "$T/resim.json" ] || { echo "VACUO: bruto re-simulado vazio"; falha=$((falha+1)); }
  cmp_ok "$T/resim.json" "$T/arq.json" "bruto da resiliencia RE-SIMULADO (PYTHONHASHSEED=777)"
  cmp_ok "$T/resim.txt" "$AQUI/resumos/mill_oponentes_resiliencia_5000.txt" "texto da resiliencia re-simulado (inclui auto-verificacao)"
  (PYTHONHASHSEED=5 python3 "$AQUI/orquestracao/frequencia_annihilator.py" 10000 padrao; PYTHONHASHSEED=6 python3 "$AQUI/orquestracao/frequencia_annihilator.py" 10000 resiliencia) > "$T/annih.txt" 2>&1
  [ -s "$T/annih.txt" ] || { echo "VACUO: annihilator vazio"; falha=$((falha+1)); }
  cmp_ok "$T/annih.txt" "$AQUI/resumos/frequencia_annihilator.txt" "frequencia do annihilator re-simulada (10.000 x 2 modos)"
  (PYTHONHASHSEED=8 python3 "$AQUI/orquestracao/crime_deepmuck.py" 5000 padrao; PYTHONHASHSEED=9 python3 "$AQUI/orquestracao/crime_deepmuck.py" 5000 resiliencia) > "$T/crime.txt" 2>&1
  [ -s "$T/crime.txt" ] || { echo "VACUO: crime_deepmuck vazio"; falha=$((falha+1)); }
  cmp_ok "$T/crime.txt" "$AQUI/resumos/crime_deepmuck.txt" "teto Lantern->crime->Deepmuck re-simulado (5.000 x 2 modos)"
fi
echo "$ok iguais, $falha diferentes"; rm -rf "$T"; [ "$falha" -eq 0 ] && [ "$ok" -gt 0 ]
