#!/bin/bash
# Refaz as tabelas dos brutos arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh [--tudo]
#  (sem opcao) todas as tabelas (A/B por lote, compactos, rankings, condicional) refeitas SO' dos .json.xz;
#  --tudo      tambem RE-EXECUTA o lote 1 da triagem `no lugar` (N=2000, 15 variantes x 2 modos): tabelas e brutos (.json.xz descomprimidos) IDENTICOS aos arquivados.
#              NAO re-executa a triagem 2-6, o lote final de 10.000, o pacote, a regressao de 20.000, a bit-identidade nem o determinismo (saidas das execucoes originais).
# NAO edite o simulador enquanto roda (re-simula o arquivo VIVO).
cd "$(dirname "$0")"
ok=0; total=0
tmp=$(mktemp -d); mkdir -p "$tmp/resumos" "$tmp/dados"
cmpf() { total=$((total+1)); if cmp -s "$tmp/resumos/$1" "../resumos/$1"; then echo "IGUAL  $1$2"; ok=$((ok+1)); else echo "DIFERE $1$2"; fi; }
soma() { # config TAG lote
  DRIVER_OUT="$tmp" LOTES=$3 TAG=$2 python3 driver_mm.py $1 sum > /dev/null
  for modo in "" "_resiliencia"; do cmpf "$2_$3$modo.txt"; cmpf "compacto_$2_$3$modo.txt"; done
}
for k in 1 2 3 4 5 6; do soma config_triagem_$k.json triagem_$k 2000; soma config_triagem_ip_$k.json triagemip_$k 2000; done
for k in 1 2 3 4; do soma config_final_$k.json final_$k 10000; done
soma config_pacote.json pacote 10000
python3 rank_triagem.py 2000 triagemip > "$tmp/resumos/rank_triagem_no_lugar.txt"; cmpf rank_triagem_no_lugar.txt
python3 rank_triagem.py 2000 triagem > "$tmp/resumos/rank_triagem_remove_append_SUPERADA.txt"; cmpf rank_triagem_remove_append_SUPERADA.txt
python3 rank_final.py > "$tmp/resumos/rank_final.txt"; cmpf rank_final.txt
python3 rank_pacote.py > "$tmp/resumos/rank_pacote.txt"; cmpf rank_pacote.txt
python3 condicional.py > "$tmp/resumos/condicional.txt"; cmpf condicional.txt
python3 resumo_spellbook.py > "$tmp/resumos/resumo_spellbook.md"; cmpf resumo_spellbook.md
python3 tabela_md.py > "$tmp/resumos/tabela_final.md"; cmpf tabela_final.md
python3 motores_com_monument.py > "$tmp/resumos/motores_por_script.txt"; cmpf motores_por_script.txt
python3 confere_gatilho_de_ativar.py > "$tmp/resumos/confere_gatilho_de_ativar.txt"; cmpf confere_gatilho_de_ativar.txt
if [ "$1" == "--tudo" ]; then
  LOTES=2000 TAG=triagemip_1 DRIVER_OUT="$tmp" python3 driver_mm.py config_triagem_ip_1.json ab > /dev/null
  for modo in "" "_resiliencia"; do
    cmpf "triagemip_1_2000$modo.txt" " (re-execucao)"
    r="raw_triagemip_1_2000$modo"; total=$((total+1))
    if cmp -s <(xz -dc "$tmp/dados/$r.json.xz") <(xz -dc "../dados/$r.json.xz"); then echo "IGUAL  $r.json.xz (bruto re-simulado identico)"; ok=$((ok+1)); else echo "DIFERE $r.json.xz (bruto)"; fi
  done
fi
rm -rf "$tmp"
echo "$ok/$total saidas byte a byte iguais"
