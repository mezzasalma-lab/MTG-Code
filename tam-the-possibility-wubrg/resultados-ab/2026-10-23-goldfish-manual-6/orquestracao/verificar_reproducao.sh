#!/bin/bash
# Refaz os resumos do goldfish manual #6 so' do bruto (dados/goldfish_manual_6_bruto.json) e compara byte a byte (cmp) com os salvos.
# Os replays e os testes usam o simulador do repositorio (../../../tam_goldfish_v1.py): se o simulador mudar, eles mudam.
# Uso: bash verificar_reproducao.sh          -> resumos do bruto + 3 replays + replay em 300 ordens (3 modos)
cd "$(dirname "$0")"
ok=0; total=0; T=$(mktemp -d)
cmpf() { total=$((total+1)); if cmp -s "$T/$1" "../resumos/$2"; then echo "IGUAL  $2"; ok=$((ok+1)); else echo "DIFERE $2"; fi; }
python3 -I linha_do_tempo.py > $T/a; cmpf a linha_do_tempo.txt
python3 -I eventos_compactos.py > $T/b; cmpf b eventos_compactos.txt
python3 -I deltas_lealdade.py > $T/c; cmpf c deltas_lealdade.txt
python3 -I pws_por_turno.py > $T/d; cmpf d pws_por_turno.txt
python3 -I pws_por_turno.py --premissa-fracture > $T/e; cmpf e pws_por_turno_premissa_fracture.txt
for n in 1 2 3; do PYTHONHASHSEED=0 python3 -I replay_manual_6.py $n > $T/r$n 2>&1; cmpf r$n replay_semente_$n.txt; done
for cfg in "padrao default" "resiliencia default" "resiliencia playtester"; do set -- $cfg; PYTHONHASHSEED=0 python3 -I replay_escala_6.py 300 $1 $2 > $T/s_$1_$2 2>&1; cmpf s_$1_$2 replay_escala_300_$1_$2.txt; done
(cd ../../../testes && PYTHONHASHSEED=0 python3 -I rodar_testes.py 2>&1 | tail -1) > $T/t; cmpf t testes_tam_todos.txt
rm -rf $T
echo "$ok/$total saidas byte a byte iguais"
