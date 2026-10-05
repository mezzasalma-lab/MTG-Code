#!/bin/bash
# Refaz TODAS as tabelas publicadas (resumos/) SO' a partir dos .json.xz de dados/ + lista.md + scryfall-cache, e compara com cmp.
# Uso: bash verificar_reproducao.sh      (nao toca em resumos/; escreve numa pasta temporaria)
cd "$(dirname "$0")"
T=$(mktemp -d); mkdir -p "$T/dados_json" "$T/resumos"
for f in dados/*.json.xz; do xz -dkc "$f" > "$T/dados_json/$(basename "${f%.xz}")"; done
LISTA=../../lista.md; O=orquestracao; ok=0; ruim=0
chk() { if cmp -s "$1" "$2"; then echo "OK   $3"; ok=$((ok+1)); else echo "DIFF $3"; ruim=$((ruim+1)); fi; }
python3 $O/mm_candidatas.py "$T/dados_json" "$T/resumos" > /dev/null;                 chk "$T/dados_json/candidatas_indice.json" <(xz -dc dados/candidatas_indice.json.xz) "dados/candidatas_indice.json (do bruto de impressoes)"
python3 $O/mm_listas_por_etiqueta.py "$T/dados_json" "$T/resumos/candidatas_por_etiqueta.md" > /dev/null; chk "$T/resumos/candidatas_por_etiqueta.md" resumos/candidatas_por_etiqueta.md "resumos/candidatas_por_etiqueta.md"
python3 $O/mm_auditoria.py $LISTA "$T/resumos/auditoria_mecanica.txt" > /dev/null; chk "$T/resumos/auditoria_mecanica.txt" resumos/auditoria_mecanica.txt "resumos/auditoria_mecanica.txt"
python3 $O/mm_auditoria.py resumos/lista_pacote_final_proposta.md "$T/resumos/auditoria_pacote_final.txt" > /dev/null; chk "$T/resumos/auditoria_pacote_final.txt" resumos/auditoria_pacote_final.txt "resumos/auditoria_pacote_final.txt"
python3 $O/mm_motores.py $LISTA "$T/resumos/motores_por_script.txt" > /dev/null;      chk "$T/resumos/motores_por_script.txt" resumos/motores_por_script.txt "resumos/motores_por_script.txt"
python3 $O/mm_numeros.py $LISTA "$T/resumos/numeros_por_script.txt" > /dev/null;      chk "$T/resumos/numeros_por_script.txt" resumos/numeros_por_script.txt "resumos/numeros_por_script.txt"
python3 $O/mm_condicoes.py $LISTA "$T/resumos/condicoes_por_script.txt" > /dev/null;  chk "$T/resumos/condicoes_por_script.txt" resumos/condicoes_por_script.txt "resumos/condicoes_por_script.txt"
python3 $O/resumo_spellbook.py "$T/dados_json" > "$T/resumos/spellbook_resumo.md";      chk "$T/resumos/spellbook_resumo.md" resumos/spellbook_resumo.md "resumos/spellbook_resumo.md"
python3 $O/resumo_rulings.py "$T/dados_json" > "$T/resumos/rulings_principais.md";      chk "$T/resumos/rulings_principais.md" resumos/rulings_principais.md "resumos/rulings_principais.md"
echo "bateram: $ok | diferentes: $ruim"; rm -rf "$T"; [ "$ruim" = 0 ]
