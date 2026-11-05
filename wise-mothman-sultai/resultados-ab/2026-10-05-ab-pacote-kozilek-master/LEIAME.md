# A/B pareado no simulador do Mothman: pacote de 5 trocas, Master of Lake-town, Kozilek e controles (2026-10-05)

Arquivo **permanente e auditável** do que sustenta os números de `../../goldfish-log.md` e do §0b de `../../candidatas-pos-eoe.md`.
Simulador: `../../mothman_goldfish_v1.py` no commit **`91b1a3d`** (código congelado: nada foi editado durante a bateria). Validação do simulador: `../2026-10-05-simulador-v1-validacao/`.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver a conclusão | `../../goldfish-log.md` (resumo) e `../../candidatas-pos-eoe.md` §0b |
| ver uma tabela pronta | `resumos/compacto_10000.txt` (principal), `resumos/ab_10000.txt` (todas as métricas, com IC95%), versões `_resiliencia`, e `_2000` |
| refazer as tabelas a partir dos brutos | `bash orquestracao/verificar_reproducao.sh` (pasta temporária; compara com `cmp`) |
| re-simular o lote de 2.000 e comparar o bruto | `bash orquestracao/verificar_reproducao.sh --tudo` |
| só descomprimir os dados | `bash descomprimir.sh` (vai para `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` |

## Como foi gerado

- **Pareamento:** a MESMA semente nas duas variantes (base × variante); IC95% = 1,96·dp(diferença pareada)/√N; a tabela mostra a média da base e a diferença pareada. Métricas = **todos** os campos numéricos do estado final (`abgen.numericos`), inclusive os indicadores `cleared_T6..T10`, `first_elim_T6/T8`, `self_lost`.
- **Lotes:** N = 2.000 (sementes 1.000.000+i, **25 variantes**) e N = 10.000 (sementes 3.000.000+i, **15 variantes**), 12 turnos, modos **padrão** e **resiliência**. Regressão: sementes 5.000.000+i, 20.000 por variante × modo.
- **Variantes** (`orquestracao/config.json`; `SWAPS` = pares carta-que-sai → carta-que-entra aplicados à biblioteca de 99): `pacote5` = Evolution Sage←Cold-Eyed Selkie, Karn's Bastion←Swarmyard, Bruvac←Soul-Guide Lantern, Garruk's Uprising←An Offer You Can't Refuse, Opulent Palace←Bojuka Bog;
  `S1..S5` = cada troca sozinha; `master_por_X` = The Master of Lake-town no lugar de X (Negate, Strip Mine, Yavimaya Hollow, Toxic Deluge, Wave Goodbye, Cold-Eyed Selkie); `pacote5+master_por_X`; `kozilek_sem_embaralhar` (chave `KOZILEK_SHUFFLE_ENABLED=False`: a carta existe e compra 4, mas **não** embaralha o cemitério);
  `kozilek_cortado_por_forest` (Kozilek ← Forest); **controles**: `controle_scales_cortado` (Hardened Scales ← Forest: tem que MOVER `counters_placed_total` para baixo), `controle_guarda_desligada` (`SELF_MILL_GUARD_ENABLED=False`: tem que MOVER `self_lost` para cima); sensibilidade: Palantír (oponente sempre deixa/sempre recusa), `OPP_TARGET_PROB` 0,3 e 1,0.
- **Código:** `orquestracao/driver_mm.py` (etapas `smoke`, `ab`, `sum`, `reg`, `compacto`), `abgen.py` (harness genérico do repositório), `config.json`. O driver é **retomável** (reaproveita um lote já gravado se o contêiner reiniciar; `REFAZ=1` força); os 4 lotes arquivados foram gerados do zero, de uma vez, por este driver, no commit `91b1a3d`.
- **Execuções NÃO arquivadas (superadas):** duas baterias interrompidas por **erros raros de combate** achados por este próprio A/B (mesa eliminada pelos gatilhos de ataque entre dois pontos do mesmo passo: `max()` de lista vazia e `KeyError`), corrigidos nos commits `1445adc` e `91b1a3d`; e uma interrompida por reinício do contêiner. Nenhuma foi usada.

## Mapa: arquivo → o que é → status → onde é usado

| arquivo | o que é | status | usado em |
|---|---|---|---|
| `dados/raw_ab_2000.json.xz` | bruto por partida, 25 variantes × 2.000, modo padrão | usado | `resumos/ab_2000.txt`, `compacto_2000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, modo resiliência | usado | `ab_2000_resiliencia.txt`, `compacto_2000_resiliencia.txt` |
| `dados/raw_ab_10000.json.xz` | bruto, 15 variantes × 10.000, modo padrão | usado | `ab_10000.txt`, `compacto_10000.txt`, `../../goldfish-log.md` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, modo resiliência | usado | `ab_10000_resiliencia.txt`, `compacto_10000_resiliencia.txt` |
| `resumos/smoke.txt` | 25 variantes: 99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 0 exceções em 200 partidas/modo | usado | — |
| `resumos/regressao_20000.txt` | 12 configurações × 20.000, 0 exceções | usado | — |

Inválido: nenhum. Superado: ver "Execuções NÃO arquivadas".

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-05, no commit `91b1a3d`: **12 de 12 saídas byte a byte iguais** (`cmp`): as 4 tabelas `ab_*.txt` e as 4 `compacto_*.txt` refeitas **só** dos `.json.xz`, e, **re-simulando** o lote de 2.000 nos dois modos (pasta temporária), as 2 tabelas e os 2 **brutos** (descomprimidos) idênticos aos arquivados (saída: `resumos/verificacao_reproducao.txt`).
Isso também prova o determinismo do simulador entre processos nesse lote.
**Não conferido:** os lotes de 10.000 foram verificados só das tabelas a partir do bruto (não re-simulados: ~25 min cada); `smoke.txt` e `regressao_20000.txt` não foram refeitos pelo script (saídas das execuções originais); `log_*.txt` ficam fora do git.

## Atualização (2026-10-06): a ordem terreno × payoff de landfall mudou no simulador; estes lotes são da ordem ANTIGA
O padrão do simulador passou a ligar `LANDFALL_PAYOFF_FIRST` (payoff de landfall conjurado antes do terreno; `../2026-10-06-landfall-payoff-primeiro/`). Os lotes desta pasta são do simulador `91b1a3d` = chave **desligada**. Para que a re-execução continue idêntica aos brutos arquivados, `orquestracao/driver_mm.py` fixa `LANDFALL_PAYOFF_FIRST = False` em toda variante (`setdefault`) e `orquestracao/abgen.py` ignora o campo novo `payoff_first_casts` (sempre 0 com a chave desligada). `bash orquestracao/verificar_reproducao.sh --tudo` refeito em 2026-10-06: **12 de 12 iguais** (`resumos/verificacao_reproducao.txt`).

