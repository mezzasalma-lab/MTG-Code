# 2026-10-22 — Tam: 3 políticas viram regra do simulador (rodada 1)

Origem: a lista de "o que falta" que dei ao usuário (2026-10-21/22) e o pedido **"Termine tudo que falta!"**. Eram três lacunas que eu tinha classificado como "diferenças de política, nenhuma alterada" (goldfish-log §6) e que, pela Regra #5 da CLAUDE.md, são candidatas a **fix no simulador** (a linha de jogo real do usuário existe nos goldfish #2 e #3), não convenções. Cada uma ficou atrás de uma chave; `False` nas três = o simulador do commit `2380566`, bit a bit.

## Conclusão (medido, N = 10.000 pareado)

1. **Tam atacando é a mudança que move a linha de base, e só no modo padrão.** Mesa limpa até T8 / T9 / T10: **13,2% → 15,2% / 38,8% → 42,7% / 64,8% → 68,5%** (+2,0 / +3,9 / **+3,7 ± 0,5** pontos); 1º oponente fora até T6 / T8: **2,4% → 4,3% / 54,4% → 64,3%**. Mecanismo: ela ataca em 99,7% das partidas (5,07 ataques por partida, 2 de dano cada, contra oponente passivo) e a Tamiyo compra +0,11 carta por partida; custo: a Tam fica virada e perde 0,09 ativação de proliferate por partida (1,178 → 1,085). **Na resiliência o efeito some (+0,16 ponto no T10, dentro do ruído)**: com criatura de oponente em campo ela fica em casa de bloqueadora (16% das partidas ainda atacam). **O §1 do `goldfish-log.md` deixa de valer no modo padrão**; vai ser refeito na rodada 2.
2. **Piscar permanente de mana virado** (Aminatou `−1` e Displacer Kitten): 99,0% das partidas idênticas no padrão, 98,6% na resiliência; dispara em 0,74% (Aminatou) e 0,26% (Kitten) das partidas do padrão. Efeito dentro do ruído (mesa limpa até T10 +0,04 ± 0,09 pontos). É uma jogada real do usuário (goldfish #2, T7), rara no baralho todo.
3. **Saheeli copiando criatura de mana, Flux Channeler / Displacer Kitten e o Staff of Compleation**: 93,3% das partidas idênticas no padrão, 97,2% na resiliência; copia o Flux/Kitten em 4,8% das partidas do padrão, criatura de mana em 1,85%, Staff em 0,45%; +0,14 proliferate do Flux Channeler por partida, +0,06 mana de cópia, +0,19 piscadas do Kitten. Efeito no resultado dentro do ruído.

| (depois − antes, N = 10.000) | padrão | resiliência |
|---|---|---|
| mesa limpa até T8 | 13,19% → 15,16% (**+1,97 ± 0,37**) | 0,42% → 0,41% (−0,01 ± 0,05) |
| mesa limpa até T10 | 64,84% → 68,50% (**+3,66 ± 0,46**) | 4,80% → 4,96% (+0,16 ± 0,11) |
| 1º oponente fora até T6 | 2,43% → 4,33% (**+1,90 ± 0,28**) | — |
| planeswalkers no fim de T6 | 3,137 → 3,140 (+0,003 ± 0,006) | 1,634 → 1,635 (+0,002 ± 0,002) |
| mana disponível no início de T6 | 7,117 → 7,125 (+0,008 ± 0,005) | 6,220 → 6,219 (−0,001 ± 0,002) |
| entradas de planeswalker de carta por partida | 10,07 → 9,91 (−0,16 ± 0,06) | 6,46 → 6,53 (+0,07 ± 0,03) |
| ativações da Tam por partida | 1,178 → 1,085 (−0,093 ± 0,010) | — |
| compras da Tamiyo por dano de combate | 0,506 → 0,614 (+0,108 ± 0,013) | 0,293 → 0,298 (+0,005 ± 0,004) |
| partidas com resultado idêntico ao do simulador anterior | 0,3% | 80,5% |

Cada variante de uma chave só (`so_tam_ataca`, `so_pisca_mana`, `so_saheeli_criatura`) está em `resumos/ab_*.txt`: o efeito grande vem todo de `so_tam_ataca` (mesa limpa até T10 +3,67 ± 0,45 no padrão).

## O que mudou no código (`tam_goldfish_v1.py`)

- `TAM_ATTACKS`: `can_attack` deixa a Tam (2/4) atacar quando **`tam_activation_check` = 0** (refatoração de `act_tam_proliferate` que só lê: sem `{W}{U}{B}{R}{G}` pagável, ou X < 2, ou poucos alvos) e, na resiliência, só se nenhum oponente tem criatura com poder. Sem doença de invocação, desvirada, sem vigilância (CR 508.1: o atacante fica virado e não bloqueia). Dorks de mana (Birds, Bloom Tender, Hierarchs) e a Kiora continuam em `NON_ATTACKERS` (o `{T}` de mana vale mais). Métrica `m_tam_attacks`.
- `BLINK_UNTAP_MANA`: `blink_unlock_options` (ensaio a seco: desvira o permanente, testa `mana_sources` e `can_cast_name`, volta ao estado) acha o permanente de mana virado que, piscado, faz uma carta valiosa da mão (prioridade ≥ 40) passar a caber; criatura volta com doença de invocação (excluída); terreno que entra virado (triome, choque sem vida) não rende; terreno entra pelo mesmo ponto de entrada de terreno (`blink_any` → `put_land_onto_battlefield`: choque paga 2 de vida). Aminatou `−1` com esse alvo vale 62 (acima do `+1` = 56); Kitten só mira não-terreno ("nonland permanent"). Oath of Teferi e The Eternal Wanderer **não** entram: o retorno deles é no próximo end step (não rende mana agora).
- `SAHEELI_COPY_CREATURES`: `saheeli_mana_choices` passa a listar também criaturas de mana (Birds, Bloom Tender, Faeburrow Elder, Hierarchs; 1 mana por cor entre os permanentes no caso do Bloom/Elder); o Servo precisa estar em campo desde o início do turno (copia de criatura tem doença de invocação, CR 302.6); `saheeli_trigger_wanted` (Flux Channeler / Displacer Kitten, ANTES de conjurar, com uma magia não-criatura valiosa que cabe e efeito a render); `saheeli_staff_wanted` (Staff no 2º main, mesma condição do `act_staff`). Gatilhos leem `perms_eff` / `count_eff` (o permanente ou a cópia até o fim do turno); o resto do arquivo lê o nome impresso. **Legendárias (Tam, Kiora) nunca entram** (regra da lenda).
- Testes dirigidos: `testes/t_politicas.py` (17, um por cláusula e os casos negativos/chaves desligadas) e `testes/t_manual5.py` (15, do goldfish #5).

## O que NÃO está coberto (Regra #7)

(1) Dorks de mana e a Kiora não atacam (decisão de política, não de oráculo); a Tam não tem lógica "ficar em casa" além da regra acima (opponentes com ameaça só na resiliência). (2) Piscar da Chain Veil virada (para ativar de novo) e de criatura de mana (Kitten blinka nonland, criatura volta doente) não entram. (3) Copias da Saheeli de Whale, Peacemaker, Kiora, Oathkeeper e Lurker: `count_eff` conta o efeito se a cópia existir, mas **a política nunca escolhe** essas fontes (Kiora é lendária; Lurker/Oathkeeper são estáticos duplicados; Whale/Peacemaker só rendem na vez do oponente ou na 2ª magia). (4) O efeito na resiliência é do modelo do Prismatic Bridge (não calibrado ainda; ver `../2026-10-22-calibracao-playtester/`). (5) Uma só família de sementes por lote.

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| testes dirigidos (182 anteriores + 17 de `t_politicas.py` + 15 de `t_manual5.py`) | **212 passam, 2 falham**: os 2 que falham são lacunas do simulador que o goldfish #5 revelou e que a rodada 2 corrige (turnos extras empilhados; ordem de pagamento do Bloom Tender no T4), mantidos falhando de propósito | `../../testes/` |
| smoke (99 cartas, 0 desconhecidas, 0 duplicadas, 200 partidas × 2 modos × 2 versões) | 0 exceções | `resumos/smoke.txt` |
| **bit-identidade:** vivo com `TAM_ATTACKS`, `BLINK_UNTAP_MANA` e `SAHEELI_COPY_CREATURES` = `False` == snapshot `2380566` (sementes 5.000.000+i, impressão digital do resultado inteiro) | **20.000 / 20.000 por modo, 0 diferenças** | `resumos/bitident_20000.txt` |
| regressão 20.000 × 2 modos, `depois` e `chave_desligada` | 0 exceções, 0 carta acima do baralho, 0 campo negativo (4 configurações) | `resumos/regressao_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo, chaves ligadas | 0 divergências | `resumos/determinismo.txt` |
| A/B pareado `antes` × `depois` + 3 variantes de uma chave só, N = 2.000 e 10.000 × 2 modos | tabela acima | `resumos/ab_*.txt`, `resumo_politicas.md` |
| reprodutibilidade (tabelas refeitas só dos brutos `.json.xz`, `cmp`) | 6/6 saídas byte a byte iguais | `resumos/verificacao_reproducao.txt` |

## Mapa arquivo → o que é → status

| arquivo | o que é | status |
|---|---|---|
| `codigo/tam_goldfish_v1_ANTES_2380566.py` (+ `tam_cartas.json`) | o simulador antes (variante `antes`) | usado |
| `codigo/tam_goldfish_v1_DEPOIS_rodada1.py` | o simulador desta rodada (idêntico ao do repositório no commit da rodada; o `config.json` aponta para ele para a pasta ser verificável mesmo depois da rodada 2 mudar o arquivo vivo) | usado |
| `dados/raw_ab_2000[_resiliencia].json.xz`, `raw_ab_10000[_resiliencia].json.xz` | bruto por partida (colunas-v1), 5 variantes: `antes`, `depois`, `so_tam_ataca`, `so_pisca_mana`, `so_saheeli_criatura` | usado |
| `resumos/` | resultados (A/B, bit-identidade, regressão, determinismo, smoke, frequências, índice, `cadeia_horarios.txt`, `log_driver.txt`) | usado |
| `orquestracao/` | `driver.py`, `abgen.py`, `config.json`, `cadeia.sh`, `resumo_politicas.py`, `verificar_reproducao.sh` | usado |

## Como refazer

```
bash descomprimir.sh                                                  # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 resumo_politicas.py | cmp - ../resumos/resumo_politicas.md    # a frequência de cada mudança, só dos brutos
bash verificar_reproducao.sh                                          # tabelas do A/B, resumo e índice: cmp byte a byte
bash verificar_reproducao.sh --tudo                                   # re-simula smoke, bit-identidade, regressão e os 4 lotes do A/B (~90 min; não mude o `config.json`)
sha256sum -c ../SHA256SUMS                                            # integridade (rodar na pasta do arquivo)
```
