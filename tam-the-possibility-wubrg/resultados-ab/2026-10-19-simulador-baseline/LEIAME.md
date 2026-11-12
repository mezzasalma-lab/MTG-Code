# Tam, the Possibility — simulador e linha de base (2026-10-19)

Arquivo da Regra #8 da CLAUDE.md para a construção do `tam_goldfish_v1.py` e a linha de base da `lista.md` **como está** (nenhuma troca aplicada). As conclusões e a leitura dos números estão em [`../../goldfish-log.md`](../../goldfish-log.md); a auditoria de oráculo em [`../../checklist-oraculo.md`](../../checklist-oraculo.md).

## Como foi gerado

- **Simulador:** `tam_goldfish_v1.py` no commit `e265cb5` (cópia em `codigo/tam_goldfish_v1_e265cb5.py`). Depois dele só mudou **comentário** (a AST do arquivo vivo é idêntica à da cópia, verificada por `ast.dump`). 12 turnos, mesa de 4 (3 oponentes), compra no T1.
- **Dois modos:** `padrao` (`simulate_one`: oponentes passivos, todo atacante conecta) e `resiliencia` (`simulate_one_with_interaction`: tabuleiro de oponente por arquétipo, gate de atenção 1/3, remoção, wipe, descarte, anulação de magia, wipe de cemitério, ataque a planeswalker).
- **Sementes:** lote de 2.000 = `1.000.000+i`; lote de 10.000 = `3.000.000+i`; regressão e conservação = `5.000.000+i` (20.000); bit-identidade = `9.000.000+i`. A mesma semente nos dois modos.
- **Variante única** (`base`), então não há A/B: as tabelas são descritivas (média ± IC95% = 1,96·dp/√N). As métricas são **todos os campos numéricos** do estado final (`abgen.numericos`); listas/dicts viram o tamanho. `finalize()` do simulador achata `state.m` em campos `m_*` e cria os indicadores `cleared_T*`, `first_elim_T*`, `died_T*`, `pws_T*`, `mana_T*` (partida já encerrada carrega o último valor adiante).
- **Cadeia que gerou tudo no código final:** `orquestracao/cadeia_final.sh` (regressão → conservação → lotes → bit-identidade → determinismo; horários em `resumos/cadeia_final_horarios.txt`).

## Mapa: arquivo → o que é → status

| arquivo | o que é | status |
|---|---|---|
| `dados/raw_baseline_2000.json.xz`, `…_2000_resiliencia.json.xz` | bruto do lote de 2.000 (colunas-v1: uma lista por campo, partida a partida, `fp` = impressão digital do estado inteiro) | usado |
| `dados/raw_baseline_10000.json.xz`, `…_10000_resiliencia.json.xz` | bruto do lote de 10.000 | usado (é a base das tabelas do `goldfish-log.md`) |
| `dados/raw_baseline_*_parcial.json.xz` | retomada por variante do driver (mesmo conteúdo, só `base`) | usado |
| `dados/oraculos_vistos.json.xz`, `dados/rulings_deck.json` | oráculos novos acrescentados ao cache e rulings das 100 cartas (JSON do Scryfall + `rulings_uri`) | usado (Regras #1/#3) |
| `resumos/resumo_descritivo_10000.txt` (e `_2000`) | **a tabela do `goldfish-log.md`**: média ± IC95% de ~70 métricas, por modo | usado |
| `resumos/resumo_extra_10000.txt` | medianas e quartis, tetos que apertaram, combos, turno da mesa limpa | usado |
| `resumos/baseline_*.txt`, `compacto_baseline_*.txt` | saídas do `driver_tam.py` (`ab`, `compacto`) | usado |
| `resumos/regressao_regressao_20000.txt`, `regressao_log_bruto.txt` | regressão 20.000 × 2: 0 exceções, 0 "carta acima do baralho", 0 campo negativo | usado |
| `resumos/conservacao_20000.txt` | conservação de cartas 20.000 × 2: 0 a mais, 0 a menos, 0 exceções | usado |
| `resumos/bitidentidade_ghost_1000.txt` | ensaio a seco do "terreno virado primeiro": ghost × desligado, 1.000 × 2 modos, 0 diferenças | usado |
| `resumos/determinismo_600_sementes.txt` | 3 `PYTHONHASHSEED` × 600 sementes × 2 modos, campo a campo: 0 divergentes | usado |
| `resumos/smoke_smoke.txt` | 99 cartas, 0 desconhecidas, 0 duplicadas, 0 exceções em 200 × 2 | usado |
| `orquestracao/` | `driver_tam.py` (+`abgen.py`, copiados do Mothman/generic), `config.json`, `resumo_base.py`, `resumo_extra.py`, `conservacao.py`, `bitident_ghost.py`, `scan_slow.py`, `cadeia_final.sh`, e os scripts do cache/rulings da rodada anterior | usado |
| `codigo/tam_goldfish_v1_e265cb5.py` | o simulador que rodou os lotes | usado |

**Lote INVÁLIDO apagado (não está aqui):** a primeira linha de base (e uma segunda) foi gerada com versões anteriores do simulador (sem a compra do T1, com o `finalize` que contava partida encerrada como 0 em T8/T10, e antes de eu achar a Kasmina `-8`) e chegou a ser commitada; o `driver_tam.py` reaproveita brutos existentes ("retomada após reinício do contêiner") e iria republicá-los sem aviso. Apaguei os brutos, relancei com `REFAZ=1` e conferi que o log dizia `feito`, nunca `reaproveitado`. Os lotes superados continuam no histórico do git, nos commits `9b292c2` (primeiro, antes da compra do T1 e da correção da Kasmina; apagado em `245def6`) e `2db278b`, `1aa3759`, `62d34e0` (segundo, com o `finalize` antigo; apagado em `0b04efb`). Estão marcados como superados por esta nota e não alimentam nenhuma tabela.

## Reproduzir cada tabela (verificado com `cmp`: idêntico, 11 de 11)

```
cd resultados-ab/2026-10-19-simulador-baseline/orquestracao
python3 resumo_base.py baseline 10000 > ../resumos/resumo_descritivo_10000.txt   # idem 2000
python3 resumo_extra.py baseline 10000   > ../resumos/resumo_extra_10000.txt
TAG=baseline DRIVER_OUT=/tmp/x python3 driver_tam.py config.json sum        # baseline_*.txt
TAG=baseline DRIVER_OUT=/tmp/x python3 driver_tam.py config.json compacto   # compacto_baseline_*.txt
```
Refazer os brutos (re-simula o arquivo VIVO; não edite o simulador enquanto roda): `REFAZ=1 TAG=baseline python3 driver_tam.py config.json ab` (~10 min nos 4 núcleos). Regressão: `TAG=regressao python3 driver_tam.py config.json reg 20000`; conservação: `python3 conservacao.py 20000`; bit-identidade: `python3 bitident_ghost.py 1000`; determinismo: `bash varredura-2026-10-05/scripts/det_check.sh tam-the-possibility-wubrg tam_goldfish_v1.py 12 600`.
Verificação de integridade: `sha256sum -c SHA256SUMS`.

## Escopo (Regra #7)

**Verificado, com método e número:** o mesmo código passou por regressão (exceções, zonas, campos negativos), conservação de cartas, determinismo entre processos, bit-identidade do ensaio a seco, smoke e 146 testes dirigidos (`python3 testes/rodar_testes.py`).
**Não verificado / limites:** (1) determinismo com 600 sementes por `PYTHONHASHSEED` (o das rodadas anteriores foi 1.500; a primeira checagem de 1.500 rodou numa versão anterior do código e deu 0 divergentes); (2) a bit-identidade foi de 1.000 sementes, não 20.000; (3) a invariante de conservação exclui partidas que acabam com magia no ar e partidas com a Aminatou `-6` entregando permanentes; (4) o modo de resiliência é o do Prismatic Bridge, **não calibrado** com a mesa do usuário; (5) os tetos de 80 ativações e 60 magias por turno apertaram em 0,39% (padrão) e 0,07% (resiliência) das partidas do lote de 10.000, e nessas o número da partida é piso; (6) o combo Orrery + Tezzeret + Chain Veil só fecha a partida com pagamento em campo, então "combo montado" (3,1%) é piso do que o combo faria numa mesa real; (7) não rodei a verificação completa do tipo `verificar_reproducao.sh --tudo` das outras pastas (re-simular tudo a partir do zero e comparar a impressão digital); refiz as tabelas dos brutos e comparei com `cmp`, mas não re-simulei os 10.000.

## Reprodução dos brutos (2026-10-22)

**Pedido pendente desde 2026-10-19: re-simular a linha de base com o código dela e comparar com o arquivado.** `bash orquestracao/resimulacao_baseline.sh` copia `codigo/tam_goldfish_v1_e265cb5.py` (+ `tam_cartas.json` do repositório de hoje) para uma pasta temporária, re-simula os 4 lotes (2.000 e 10.000 × padrão e resiliência, `REFAZ=1`, mesmas sementes) e compara cada bruto decomprimido (`xz -dc`) com o arquivado em `dados/` por `cmp`: **4/4 byte a byte iguais** (7 min 53 s; `resumos/verificacao_resimulacao_2026-10-22.txt`). Uma primeira passada manual, antes de o script existir, deu os mesmos 4 brutos **e** os 4 `*_parcial.json.xz` idênticos aos arquivados.
**O que NÃO foi conferido:** (a) as **tabelas** (`resumos/baseline_*.txt`, `compacto_*`) não foram refeitas pelo script, só os brutos (as tabelas são função dos brutos, mas não rodei `cmp` nelas); (b) a regressão, a conservação, a bit-identidade e o determinismo desta pasta não foram re-simulados; (c) a etapa final do driver (`compacto()`) falha na pasta temporária com `FileNotFoundError` porque lê o `dados/` da pasta de origem; os brutos já estão gravados antes disso, então a comparação vale, mas o log do driver termina em erro (esperado e documentado no script); (d) o `tam_cartas.json` usado é o do repositório de hoje, não uma cópia datada de 2026-10-19 (os resultados idênticos mostram que ele não alterou nada nos lotes).
