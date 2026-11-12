# Validação do simulador v1 do Mothman — varreduras mecânicas, testes dirigidos, determinismo, regressão (2026-10-05)

Arquivo **permanente e auditável** do que sustenta a afirmação "o simulador `mothman_goldfish_v1.py` está validado" (Regras #1, #8 e #10 de `CLAUDE.md`). Simulador construído do zero em 2026-10-05; não existe versão "antes".
Os A/B (pacote, Kozilek, Master) estão em `../2026-10-05-ab-pacote-kozilek-master/` e `../2026-10-05-ab-kozilek-self-deck/`; a auditoria cláusula-a-cláusula em `../../checklist-oraculo.md`.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| rodar os 134 testes dirigidos | `cd wise-mothman-sultai && python3 testes/testes_dirigidos.py` (saída arquivada em `resumos/testes_dirigidos.txt`) |
| refazer as varreduras de entrada/fetch/landfall | `cd wise-mothman-sultai && python3 resultados-ab/2026-10-05-simulador-v1-validacao/orquestracao/varredura_mecanica_mothman.py` |
| refazer a regressão | `python3 orquestracao/reg_mm.py 20000 1` (precisa de `abgen.py` na mesma pasta; o driver dos A/B também roda a regressão com as variantes) |
| refazer o determinismo | `cd varredura-2026-10-05/scripts && bash det_check.sh wise-mothman-sultai mothman_goldfish_v1.py 12 1500` |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` |

## O que foi verificado, como, e com que resultado

| classe (Regra #10) | método | resultado | arquivo |
|---|---|---|---|
| ver. por cláusula | 134 testes dirigidos; cada um confere um número esperado **> 0** (um teste que passa em vazio é bug) | 134/134 | `resumos/testes_dirigidos.txt` |
| entrada de terreno × oráculo | 29 terrenos do `CARD_DB` (27 da lista + Karn's Bastion e Opulent Palace, candidatas): esperado derivado do TEXTO do oráculo em cache × `land_enters_tapped`; condições (Woodland com/sem Floresta e com Triome, slowlands com 3/2/1 oponentes, choques com vida 40 e 8) | 29/29 conferidos, 0 divergências | `resumos/varredura_mecanica.txt` §1 |
| fetch real | 4 fetches × 40 partidas: sacrificada → cemitério, 1 vida (Fabled Passage não), busca por subtipo, biblioteca −1 | 160/160 | idem §2 |
| jogar terreno ≠ magia | `spells_cast_this_turn` não muda em `play_land_phase` (100 partidas) | 0 contagens indevidas | idem §3 |
| landfall em todo ponto de entrada | entradas de terreno × chamadas de `landfall`, 300 partidas × 2 modos | 7.275 = 7.275 (8 origens: play 4.888, fetch 610, Kodama 537, Hedge Shredder 352, ramp 348, Fabled Passage 227, Frogantua 213, Freestrider 100) | idem §4 |
| estado por nome × instância | busca por conjunto de nomes de terrenos virados | 0 ocorrências: o estado vive em `Permanent.tapped` | idem §5 |
| determinismo entre processos | `det_check.sh`: 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final, **no código `91b1a3d`** | **0 sementes divergentes** nos 2 modos | `resumos/determinismo.txt` |
| AST de sets | `ast_sets.py`: 5 candidatos no arquivo do Mothman, todos lidos: 4 acumulam em `Counter`/`set` (ordem irrelevante, 4 restantes na saída arquivada); 1 (soma de float em Freestrider) passou a iterar `sorted(...)` | 1 correção | `resumos/ast_sets_mothman.txt` |
| regressão | 20.000 partidas × 2 modos em 12 configurações (lista atual, pacote, pacote+Master, Kozilek sem/cortado, guarda desligada) + 4 extremas no outro A/B | **0 exceções**, 0 carta acima do baralho, 0 campos negativos (código `91b1a3d`) | `../2026-10-05-ab-pacote-kozilek-master/resumos/regressao_20000.txt`, `../2026-10-05-ab-kozilek-self-deck/resumos/regressao_20000.txt` |

**Achados reais durante a construção (cada um virou teste):** busca da fetch antes do gatilho do cemitério (Gitrog) → `ValueError` em 3/6.000; Cauldron/Lantern com o cemitério alterado pelo gatilho de crime (Deepmuck) → `ValueError`; Six retrace devolvendo a própria carta antes de pagar; "uma vez por turno" contado só nos meus turnos e resetado depois do untap (o Mesmeric Orb milava antes do reset); Plaza of Heroes sem a 3ª habilidade; Syr Konrad sem a 3ª cláusula e sem mortes simultâneas; Frogantua milando parcial; Hollowmurk sem "entra com contadores"/persist; Lantern sem a 2ª ativada. Detalhes em `../../checklist-oraculo.md` §2 (marcados 🐛).

## O que NÃO foi conferido

- Os `driver.py` dos A/B fixam `PYTHONHASHSEED=0`; a dependência de hash só é vista por `det_check.sh` (acima) — ela foi rodada **no código congelado do A/B** (commit citado no `LEIAME.md` de cada A/B).
- `audit_entrada*.py`/`audit_fetch.py` originais usam `total_mana` (outros simuladores); aqui foram **reescritos** (`varredura_mecanica_mothman.py`) com o mesmo critério. `colisao_nome.py`: não aplicável (sem conjunto de nomes), conferido por grep.
- O modo de resiliência é uma amostra estatística de interação (design comum do repositório), não uma mesa real. Parâmetros dos oponentes passivos (37/28/34, 0/1/2 magias, `OPP_TARGET_PROB` 0,7) são premissas declaradas.
- Escopo completo do que foi e não foi varrido: `../../checklist-oraculo.md` §0.
