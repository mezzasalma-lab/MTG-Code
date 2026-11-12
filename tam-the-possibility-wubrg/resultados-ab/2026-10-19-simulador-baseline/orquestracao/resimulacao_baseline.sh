#!/bin/bash
# Re-simula os 4 lotes da linha de base de 2026-10-19 (2.000 e 10.000, modos padrao e resiliencia) com o CODIGO ARQUIVADO (codigo/tam_goldfish_v1_e265cb5.py) numa pasta temporaria
# e compara o BRUTO decomprimido (xz -dc) com o arquivado em dados/ (cmp). Uso: bash resimulacao_baseline.sh   (~8 min; nao toca no simulador do repositorio)
# Observacao: a ultima etapa do driver (`compacto()`) le dados/ da pasta de ORIGEM, que na pasta temporaria nao existe, e termina com FileNotFoundError; os brutos ja' foram gravados em $T/out/dados antes disso.
AQUI="$(cd "$(dirname "$0")" && pwd)"; BASE="$(cd "$AQUI/.." && pwd)"; DECK="$(cd "$AQUI/../../.." && pwd)"
T=$(mktemp -d); O="$T/resultados-ab/2026-10-19-simulador-baseline/orquestracao"
mkdir -p "$O"
cp "$BASE/codigo/tam_goldfish_v1_e265cb5.py" "$T/tam_goldfish_v1.py"
cp "$DECK/tam_cartas.json" "$T/tam_cartas.json"
cp "$AQUI/abgen.py" "$AQUI/config.json" "$AQUI/driver_tam.py" "$O/"
(cd "$O" && REFAZ=1 TAG=baseline DRIVER_OUT="$T/out" python3 driver_tam.py config.json ab > "$T/log.txt" 2>&1)
ok=0; total=0
for f in raw_baseline_2000 raw_baseline_2000_resiliencia raw_baseline_10000 raw_baseline_10000_resiliencia; do
  total=$((total+1))
  if [ -f "$T/out/dados/$f.json.xz" ] && cmp -s <(xz -dc "$BASE/dados/$f.json.xz") <(xz -dc "$T/out/dados/$f.json.xz"); then echo "IGUAL  $f (bruto re-simulado == arquivado)"; ok=$((ok+1)); else echo "DIFERE $f"; fi
done
echo "$ok/$total brutos re-simulados byte a byte iguais aos arquivados"
echo "--- fim do log do driver (esperado: FileNotFoundError em compacto(), ver comentario acima):"; tail -3 "$T/log.txt" | cut -c1-200
rm -rf "$T"
