# Mothman: Muldrotha por partida (2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Origem: o usuário perguntou *"Muldrotha não é a melhor recursão do deck?"* depois que eu a pus em 3º nos cortes do Monument (`../2026-10-07-riverchurn-monument/`), e aceitou medir quanto ela rende por partida em que entra. A correção de leitura (oráculo) já está em `../../goldfish-log.md` §11; este arquivo é a medição (§12).

## Resposta curta (MEDIDO, lista atual sem trocas, N = 10.000 por modo)
1. **Entra tarde:** em campo até T6 em 6,9% das partidas, até T8 em 21,5%, até T12 em 29,9% (resiliência 4,3% / 13,6% / 24,8%).
2. **Nas partidas em que entra (padrão, 2.994):** 2,08 turnos em campo, **2,65 jogadas do cemitério por partida** (1,91 magias + 0,74 terrenos), 0,92 magias recastadas por turno; 77% das partidas com 1+ recast; **58% dos recasts são peças-chave** (topo: Walking Ballista, Hardened Scales, The Great Henge, Winding Constrictor, Ruin Crab, Hollowmurk Siege).
3. **É a maior fonte de magias devolvidas do deck** (por partida, todas as partidas): Muldrotha 0,57 magias (+0,22 terrenos) × Six 0,40 retraces × Icetill 0,88 (só terreno).
4. **Valor da habilidade** (base − `sem_habilidade`, mesmas sementes): todas as partidas, mesa limpa até T8 **+0,58 ± 0,24** (padrão) e **+0,57 ± 0,19** (resiliência); **entrando até T6: +4,64 ± 2,62 (padrão) e +10,88 ± 3,52 (resiliência)**. Custo: entrando até T6 no padrão, deck-out meu +2,03 ± 1,75 ponto (no limite do IC).
5. **Leitura (raciocinada):** valor médio pequeno porque chega tarde; concentrado em chegar cedo contra uma mesa que reage. Mede resiliência, não velocidade: **não é corte**.

**NÃO verificado (Regra #7):** valor isolado das outras recursões (Six, Icetill, Evolution Witness, Agadeem) para comparar por presença; `sem_habilidade` mede só a habilidade (o corpo 6/6 continua no baralho); a política de recast do simulador (primeira opção livre por tipo) é um piso; vida e rad contra oponente real; oponente por categoria, não varredor real.

## Como foi gerado
- **Simulador:** `../../mothman_goldfish_v1.py` no commit `4a1c6be` (nenhuma edição nesta rodada). **Nenhum código do simulador foi tocado**: o ensaio `sem_habilidade` é um *monkeypatch* no processo de medição (`orquestracao/mede_muldrotha.py`): depois de cada `upkeep_step` o `muldrotha_used` é pré-preenchido com os 5 tipos, então nenhum tipo está livre e a habilidade do cemitério (terreno e magias) não faz nada, a Six e o resto continuam normais. Testado em 400 sementes: 0 recasts e 0 `muldrotha_plays` em `sem_habilidade`, 119 de 400 partidas com a Muldrotha em campo nas duas variantes.
- **Contagem só no estado real:** os ensaios a seco do simulador (`_hoist_loses_a_play` etc.) copiam o estado e também chamam `execute_cast`; o monkeypatch só conta quando `state is g["st"]` (o estado que `play_turn` está jogando).
- **Dados:** sementes `3.000.000+i`, N = 10.000, 12 turnos, modos padrão e resiliência, `PYTHONHASHSEED=0`; `base` e `sem_habilidade` têm o mesmo baralho e a mesma semente, então 80% (padrão) e 82% (resiliência) das partidas têm todas as métricas idênticas e o IC95% pareado é curto. Campos `mul_*` (turno de entrada, turnos ativa, recasts por tipo, peças-chave, terrenos) somados a todos os campos numéricos do estado final.
- **Peças-chave** (lista do script, escolha minha): Henge, Altar of Dementia, Altar of the Brood, Mindcrank, Mesmeric Orb, Psychic Corrosion, Memory Erosion, Palantír, Hardened Scales, Winding Constrictor, Kami, Ruin Crab, Hollowmurk Siege, Danny Pink, Agatha's Soul Cauldron, Hedge Shredder, Walking Ballista, Swiftfoot Boots. A tabela completa de nomes está em `dados/recasts_por_nome.json`.

## Mapa arquivo → o que é → status
| arquivo | o que é | status | tabela que o usa |
|---|---|---|---|
| `dados/raw_muldrotha_10000.json.xz` | bruto por partida, modo padrão, `base` e `sem_habilidade` | usado | `resumos/muldrotha.md`, `goldfish-log.md` §12 |
| `dados/raw_muldrotha_10000_resiliencia.json.xz` | idem, modo resiliência | usado | idem |
| `dados/recasts_por_nome.json` | cartas rejogadas do cemitério, por nome, modo e variante | usado | `resumos/muldrotha.md` |
| `resumos/muldrotha.md` | todas as tabelas (`orquestracao/resume_muldrotha.py`, só lê os brutos) | usado | `goldfish-log.md` §12 |
| `resumos/indice_dados.md`, `log_medicao.txt`, `verificacao_reproducao.txt` | índice, log da medição (0 `Traceback`), verificação | apoio | — |
| `orquestracao/` | `mede_muldrotha.py`, `resume_muldrotha.py`, `abgen.py`, `lanca.sh`, `verificar_reproducao.sh` | apoio | — |

## Reprodução
- Medição: `bash orquestracao/lanca.sh` (≈ 7 min em 4 núcleos); tabela: `python3 orquestracao/resume_muldrotha.py > resumos/muldrotha.md`.
- Dados brutos: `bash descomprimir.sh`; índice: `python3 indice_dados.py`.
- Verificação: `bash orquestracao/verificar_reproducao.sh [--tudo]` (**não edite o simulador enquanto roda**).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` (2026-10-07): **4 de 4 saídas byte a byte iguais** (`cmp`): `resumos/muldrotha.md` refeito só dos `.json.xz`, e, **re-simulando a medição inteira** (10.000 × 2 modos × 2 variantes) com o arquivo vivo numa pasta temporária, os 2 brutos descomprimidos e `recasts_por_nome.json` idênticos aos arquivados. Não conferido: nada além disso foi executado (não há regressão de 20.000 nem bit-identidade porque **o simulador não foi editado** nesta rodada; o `monkeypatch` vive só no processo de medição).
