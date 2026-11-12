# Ms. Bumbleflower: Oakhollow Village rendia 2 mana (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo; o que NÃO foi coberto está em "Não coberto"). Origem: pedido do usuário *"Vc vai precisar revisar e corrigir o Plaza e demais terrenos em todos os simuladores"*, depois da partida manual #3 do Wise Mothman (`../../../varredura-2026-10-05/resumos/revisao_terrenos_2026-11-11.md`). Classe (p) da Regra #10 (mana contada em dobro / terreno fora da regra do `{T}`), achada por grep dos nomes de terreno restrito em linhas de acúmulo de mana + teste dirigido (não por auditoria carta-a-carta).

## O erro (provado por teste dirigido, estado mínimo)
Oráculo (Scryfall): `{T}: Add {C}.` / `{T}: Add {G}. Spend this mana only to cast a creature spell.` / `{G}, {T}: Put a +1/+1 counter on each Frog, Rabbit, Raccoon, or Squirrel you control that entered the battlefield this turn.` **Uma habilidade de `{T}` por vez: 1 mana por virada.**
1. **Mana em dobro:** a Oakhollow Village está em `LAND_NAMES` (contada em `lands_available`) e `rocks_mana` somava +1 de novo ("aproximado como mana geral disponível"). **Teste dirigido: 2 Forest + Oakhollow = 4 de mana; 3 Forest = 3.**
2. **Terreno tratado como criatura:** `color_sources` só contava o `{G}` do terreno se `entered_turn < turn` (terreno não tem enjoo de invocação, CR 302.6).
3. **`{G}` para qualquer magia:** o `{G}` vale só para magia de criatura (o `{C}` segue pagando o genérico de qualquer magia).

## A correção (`ms-bumbleflower-bant/bumbleflower_goldfish_v1.py`)
- `OAKHOLLOW_COUNTS_ONCE` (padrão ligada): `rocks_mana` não soma o terreno de novo.
- `OAKHOLLOW_MANA_RULES` (padrão ligada): `color_sources(state, color, creature_spell)` conta o `{G}` do Oakhollow só para magia de criatura e sem exigir `entered_turn < turn`; `has_color_sources_for` passa o tipo da magia.
- Com as duas chaves desligadas o comportamento é o de `99fde54`, bit a bit. Teste dirigido com chaves ligadas: 2 Forest + Oakhollow = 3 de mana; `{G}` para não-criatura 2 (era 3); Oakhollow entrando hoje conta 3 (era 2).

## Resultado (pareado, mesmas sementes; `resumos/ab_*.txt`, `depois` = as 2 chaves, mais 2 variantes de uma chave só)
**A correção tira mana que não existia, então o comandante entra mais devagar; os dois erros de regra empurram em sentidos opostos.**

| N, modo | partidas idênticas ao antes | comandante até T3 | até T4 | até T5 | até T6 |
|---|---|---|---|---|---|
| 10.000, padrão | 78,0% | 27,11% → 24,61%: **−2,50 ±0,32 pontos** | −1,35 ±0,26 | −0,61 ±0,19 | −0,44 ±0,14 |
| 10.000, resiliência | 79,5% | 25,26% → 22,96%: **−2,30 ±0,31** | −1,49 ±0,29 | −1,04 ±0,24 | −0,77 ±0,20 |
| 2.000, padrão | 79,5% | −2,15 ±0,68 | −1,20 ±0,55 | −0,95 ±0,45 | −0,55 ±0,32 |
| 2.000, resiliência | 79,8% | −2,20 ±0,67 | −1,75 ±0,62 | −1,40 ±0,53 | −1,00 ±0,44 |

**Decomposição por chave (N = 10.000, padrão; comandante até T3):** só `OAKHOLLOW_COUNTS_ONCE` (mana em dobro): **−2,79 ±0,33** pontos (78,2% idênticas); só `OAKHOLLOW_MANA_RULES` (sem enjoo no terreno e `{G}` só para criatura): **+0,46 ±0,14** (96,0% idênticas); as duas: −2,50. Resiliência: −2,58 ±0,32 / +0,39 ±0,15 / −2,30. As 3 variantes diferem entre si (fração de partidas idênticas 78,2% / 96,0% / 78,0%): nenhuma variante é vácua.
Outros efeitos (padrão, N = 10.000): dano total proxy −9,4 ±1,8 (de 223,3); marcadores postos −4,4 ±1,0; Treasures criados −0,13 ±0,03; compras extras −0,34 ±0,06; `commander_cast_turn__nunca` +0,05 ±0,05 (dentro do ruído).

## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): 99 cartas, 93 distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo, antes e depois, sem exceção.
- **Regressão 20.000 × 2 modos × 2 configurações** (`resumos/regressao_20000.txt`): 0 exceções, 0 carta acima do baralho, 0 campos negativos, com as chaves ligadas e desligadas.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`, 4 blocos de 5.000 sementes 5.000.000–5.019.999; `orquestracao/bitident_bf.py`): chaves desligadas == `99fde54` em **40.000 de 40.000** execuções; chaves ligadas: **30.511 partidas em que o Oakhollow nunca esteve em campo durante um cálculo de mana, idênticas ao `99fde54`, e 9.489 com ele em campo** (as únicas que podem diferir); **0 divergências**. O script vigia `total_mana` e exige > 0 partidas em cada grupo.
- **Determinismo** (`resumos/determinismo.txt`): 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final: **0 sementes divergentes** nos dois modos.

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{2000,10000}{,_resiliencia}.json.xz` | bruto do A/B (variantes `antes`, `depois`, `so_conta_uma_vez`, `so_regras_de_mana`; colunas-v1) | usado |
| `resumos/ab_*.txt` | tabelas (função só do bruto: `driver.py sum`) | usado (`cmp`) |
| `resumos/{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}.txt`, `resumos/bitident_chunk_*.txt` | saída de cada etapa | usado |
| `codigo/bumbleflower_goldfish_v1_ANTES_99fde54.py` | o simulador como estava | snapshot |
| `orquestracao/{abgen.py,driver.py,config.json,bitident_bf.py,rodar_tudo.sh,verificar_reproducao.sh}` | harness (o `driver.py`/`abgen.py` são os da rodada de 2026-10-05 do Bumbleflower) | usado |
| `SHA256SUMS`, `descomprimir.sh` | somas e descompressão | ver abaixo |

Reproduz: `bash ms-bumbleflower-bant/resultados-ab/2026-11-11-oakhollow-mana/orquestracao/verificar_reproducao.sh` (refaz as 4 tabelas dos brutos e compara por `cmp`, testa os `.xz` e confere o `SHA256SUMS`). **Não re-executa** as simulações (A/B, regressão, bit-identidade, determinismo): são as saídas das execuções originais.

## Não coberto (Regra #7)
- **A única mana de terreno restrita lida à mão neste arquivo foi a do Oakhollow Village**; as outras linhas de acúmulo de mana (Rishkar, Devoted Druid, Faeburrow Elder, filtros Overflowing Basin/Skycloud Expanse/Sungrass Prairie) não foram revistas aqui.
- A **terceira habilidade** do Oakhollow (`{G}, {T}`: marcadores nas criaturas Frog/Rabbit/Raccoon/Squirrel que entraram no turno) já existia (linha ~1129 antes da correção) e **não foi reauditada**; o seu custo `{G}` usa `color_sources(state, "G")` sem tipo de magia (padrão `creature_spell=True`: uma habilidade não é "magia de criatura", então o `{G}` do próprio Oakhollow não deveria pagá-la; **não corrigido, não medido**).
- A cadeia de bit-identidade vigia `total_mana`; uma partida em que o Oakhollow esteve em campo sem nenhum cálculo de mana é contada como "sem Oakhollow" (conservador para o grupo "idêntico": só afirma identidade onde a mana nunca foi calculada com o terreno).
- Sem calibração contra a mesa real do usuário.
