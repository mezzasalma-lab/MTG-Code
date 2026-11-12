# 2026-10-23 — Beorn: Ram Through → Herd Heirloom (e o gatilho da Beorn no início do combate)

Pedido do usuário (2026-10-23): *"O deck do Beorn está completo e troquei o Ram Through por Herd Heirloom para dar Trample e compra de cartas!"*. A troca é **decisão dele** (já feita na mesa); este arquivo registra o que mudou na `lista.md` e no simulador, valida a implementação das **duas** habilidades do Herd Heirloom e mede o que a troca faz no deck, pelo método da Regra #4 (oráculo ao vivo → motores do deck → Spellbook antes/depois → condições enumeradas por script).
Simulador: `../../beorn_goldfish_v1.py`. Código **anterior** em `codigo/beorn_goldfish_v1_ANTES_1b7dd73.py`; o código que roda esta pasta é a cópia fixa `codigo/beorn_goldfish_v1_DEPOIS.py` (idêntica ao arquivo vivo no commit da rodada; o `config.json` aponta para ela). Listas: `codigo/lista_ANTES.md` e `codigo/lista_DEPOIS.md` (só difere uma linha, na mesma posição).

## Conclusão (N = 10.000 pareado, sementes 3.000.000+i, 8 turnos; `*` = a diferença excede o IC95%)

1. **Spellbook: a troca não cria nem desfaz nenhum combo.** 0 combos incluídos antes e depois; as 21 combinações "a uma carta de distância" são as mesmas nos dois lados; os 74 nomes foram reconhecidos; controle positivo (Basalt Monolith + Rings of Brighthearth aparece) e de corte (sem o Rings some) passaram (`dados/spellbook_antes_depois.json`). Bracket não muda.
2. **No simulador, a troca traz a Beorn mais cedo e +1,1 carta por partida, sem mudar o fechamento.** Modo padrão, `depois` × `so_gatilho_beorn` (a TROCA, com o gatilho da Beorn corrigido nos dois lados): **Beorn conjurada até T3 17,4% → 19,1% (+1,7 ± 0,25 pts), até T4 62,0% → 66,5% (+4,5 ± 0,4)**, T5 +1,1, T6 +1,0; **cartas extras compradas 22,78 → 23,91 (+1,13 ± 0,12)**; magias conjuradas +0,32; peças de rampa +0,37; contadores +0,56. **Primeiro finisher até T6 +0,3 ± 0,2 pts e "sem finisher em 8 turnos" +0,1 ± 0,4 (dentro do ruído).** Na resiliência: Beorn até T4 +2,4 ± 0,4 pts, cartas extras +0,72 ± 0,09, finisher dentro do ruído.
3. **O custo da troca é a interação própria:** a remoção proxy conjurada cai de 0,71 → 0,57 por partida (−0,135 ± 0,007; −0,13 na resiliência). É contagem de uso, não efeito (Regra #1: sem oponente real); o que o deck perde de verdade é um **instantâneo de 2 mana que causa dano igual ao poder e, com trample, passa o excesso para o dono** (oráculo do Ram Through). Com a troca, o deck fica com: Beast Within, Song of the Dryads, Archdruid's Charm (modo luta), Ezuri's Predation (8 mana), Haywire Mite (só artefato/encantamento). O ponto crítico já registrado em `auditoria.md` §6 (pouca remoção) **piora**; não é recomendação de desfazer a troca.
4. **Quanto vem de cada habilidade** (padrão; contra o Heirloom "em branco", sem habilidades): a **1ª (mana de criatura)** sozinha traz Beorn até T4 **+3,4 ± 0,4 pts**, "sem finisher" −1,2 ± 0,3 pts, cartas extras +0,67; a **2ª (trample + compra por dano)** sozinha **não mexe no tempo da Beorn** (−0,0) e traz **+0,90 ± 0,08 carta extra por partida**. No `depois` as duas **disputam o mesmo `{T}`**: o mana é usado 0,14 vez por partida (contra 0,72 quando só ele existe) porque, com criatura elegível para atacar, a política guarda o `{T}` para a compra (0,80 ativação, 0,89 carta por partida, incluindo as dobradas pela Roaming Throne).
5. **Parte do ganho de tempo é convenção do simulador, não da carta.** O Heirloom "em branco" já leva a Beorn **+1,1 pt até T4** (`troca_sem_habilidades` − `antes`): é porque o simulador conjura sua remoção própria nos turnos 3 e 6 (`try_use_own_interaction`) ANTES da fase principal e o Ram Through gasta 2 mana do turno em que a Beorn caberia. Numa mesa real o Ram Through só é conjurado se houver alvo. Isso é limite do goldfish (Regra #5), não valor da carta.
6. **Achado de leitura de cláusula, fora da troca: o gatilho da Beorn estava preso a `can_attack(Beorn)`.** Oráculo: *"At the beginning of combat on your turn, put a trample counter on up to one target creature you control. It becomes a Bear in addition to its other types. Then if you control three or more Bears, draw two cards."* É gatilho de **início de combate**, não "whenever Beorn attacks": dispara com a Beorn doente de invocação e sem atacar. O código (comentário "Whenever Beorn attacks … ilegal no turno do cast, CR 302.6") perdia o 1º gatilho de cada partida. Corrigido atrás da chave `BEORN_TRIGGER_AT_BEGINNING_OF_COMBAT` (padrão ligada). Efeito isolado (`so_gatilho_beorn` − `antes`, Ram Through nos dois lados): **cartas extras +1,64 ± 0,15**, compras de 2 da Beorn +0,43, conversões +0,38, Ursos em campo +0,65, contadores +1,34; o tempo de conjuração da Beorn não muda (+0,0). **As linhas de base anteriores do Beorn (goldfish-log) subestimam o deck em ~1,6 carta extra por partida por causa disso.**

### Tabela (N = 10.000; `antes` = lista e simulador de antes; `só gatilho` = Ram Through + gatilho corrigido; `depois` = Heirloom + gatilho corrigido)

| padrão | antes | só gatilho | depois |
|---|---|---|---|
| Beorn conjurada até T3 / T4 / T5 / T6 | 17,4% / 62,0% / 89,6% / 93,8% | 17,4% / 62,0% / 89,7% / 93,8% | 19,1% / 66,5% / 90,8% / 94,8% |
| nunca conjurada em 8 turnos | 1,3% | 1,3% | 1,1% |
| 1º finisher até T5 / T6; sem finisher | 8,0% / 18,1%; 55,4% | 8,0% / 18,5%; 55,2% | 8,3% / 18,8%; 55,3% |
| cartas extras compradas | 21,14 | 22,78 | 23,91 |
| magias conjuradas | 13,40 | 13,78 | 14,09 |
| Ursos em campo no fim; compras de 2 da Beorn | 8,82; 3,38 | 9,47; 3,81 | 9,64; 3,87 |
| compras por dano de combate (Ohran/Toski) | 7,77 | 8,30 | 8,36 |
| remoção própria conjurada (proxy) | 0,69 | 0,71 | 0,57 |

| resiliência | antes | só gatilho | depois |
|---|---|---|---|
| Beorn conjurada até T3 / T4 / T5 / T6 | 8,4% / 33,6% / 55,7% / 65,8% | 8,2% / 33,0% / 54,9% / 65,0% | 8,9% / 35,5% / 55,2% / 65,7% |
| cartas extras compradas | 11,05 | 12,29 | 13,01 |
| remoção própria conjurada (proxy) | 0,61 | 0,63 | 0,50 |

Na resiliência o corte `só gatilho` mostra a Beorn até T5/T6 **−0,8 pt** (± 0,4): não é efeito do gatilho sobre o cast; a resiliência escolhe a atenção do oponente por `interaction_chance` = 0,10 + 0,03 × permanentes não-terreno, e mais compras = mais permanentes = mais remoção = mais recastes (o campo registra o turno do último recast). Explicação por mecanismo do modelo, **não medida separadamente**.

## O que mudou no código (`beorn_goldfish_v1.py`)

| chave (padrão) | o quê |
|---|---|
| `HERD_HEIRLOOM_IN_DECK` (`True`) | a lista de 99 (`current_decklist()`); `False` troca a linha do Heirloom pela do Ram Through **na mesma posição** (mesma permutação da semente ⇒ A/B pareado carta a carta) |
| `HERD_HEIRLOOM_MANA` (`True`) | habilidade 1: `{T}`: 1 mana de qualquer cor, **só para magia de criatura** (`creature_mana_bonus` / `can_cast` / `spend_for_spell`; vale para o comandante e para a criatura do exílio da Beorn, Reluctant Host; nunca entra em `remaining_mana`; não paga magia não-criatura nem habilidade ativada) |
| `HERD_HEIRLOOM_DRAW` (`True`) | habilidade 2: `{T}`: criatura minha com **poder ≥ 4** (apta a atacar) ganha trample e "whenever this creature deals combat damage to a player, draw a card" (`try_heirloom_draw`, início do combate, depois do gatilho da Beorn; **Roaming Throne dobra** o gatilho concedido a OUTRO Urso) |
| `BEORN_TRIGGER_AT_BEGINNING_OF_COMBAT` (`True`) | o gatilho da Beorn no início do combate, sem exigir `can_attack` |
| (sem chave) `bear_trigger_times("Roaming Throne") = 1` | a Throne nunca dobra o gatilho dela mesma ("another creature"); nenhum chamador antigo passava a Throne, então não muda resultado anterior |

As duas habilidades **dividem o mesmo `{T}`** (`heirloom_tapped_this_turn`). Política (`arm_heirloom`, minha, não é regra): guarda o `{T}` para a compra se já há alvo elegível; vira mana se não há, ou se a Beorn só cabe com ele. O Heirloom não é peça de mulligan (`KEEPERS`).

## Oráculo e rulings lidos ao vivo — `dados/scryfall_oraculo_rulings_2026-10-23.json`
**Lidos antes de escrever o código** (Regra #3): Herd Heirloom (1 ruling, 2025-04-04: *depois que a 2ª habilidade resolve, baixar o poder abaixo de 4 não tira as habilidades*), Ram Through (4 rulings; saiu da lista), **Beorn the Fierce** (1: o tipo Urso dura para sempre), **Roaming Throne** (2: não copia a habilidade, ela dispara uma vez a mais; escolhas são feitas por instância), Ohran Frostfang (2), Toski (2), Goreclaw (3). Nenhuma contradiz o código.
Condições enumeradas por script (`resumos/enumera_condicoes_lista_{antes,depois}.txt`): criaturas com poder ≥ 4 na lista (Beorn, Beorn Reluctant Host, Chameleon Colossus, Craterhoof, Defiler of Vigor, Ghalta, Gigantic Big Bear, Goreclaw, Roaming Throne; Lumra é CDA); 29 magias de criatura (as únicas que o mana restrito paga) e 33 não-criatura-não-terreno; cartas que já dão trample (Beorn, Garruk's Uprising, Chronicle of Victory, Craterhoof, Defiler, Ghalta, Goreclaw, Managorger): **o trample do Heirloom é redundante em boa parte do deck, o valor está na compra**; quem compra por dano de combate (Ohran, Toski): o Heirloom soma 1 por turno.

## Validação (Regras #1 e #10)
| verificação | resultado | arquivo |
|---|---|---|
| smoke: 99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos (vivo e snapshot) | 0 exceções | `resumos/smoke.txt` |
| testes dirigidos (`../../test_beorn_goldfish.py`) | **22/22** (8 anteriores + 14 novos: mana só de criatura, um `{T}` por turno, poder ≥ 4 e doença de invocação, contadores agregados, Throne dobra / não dobra a própria Throne, política de reserva e exceção do comandante, Medallion/devoção/sem tag de rampa, gatilho da Beorn doente de invocação, baralho de antes, partidas inteiras com contagem > 0) | `../../test_beorn_goldfish.py` |
| **bit-identidade**: as 4 chaves desligadas == snapshot `1b7dd73`, 20.000 partidas × 2 modos, impressão digital do resultado inteiro | **0 divergências** nos dois modos | `resumos/bitident_20000.txt` |
| regressão 20.000 × 2 modos × (`depois`, chave desligada) | **0 exceções, 0 carta acima do baralho, 0 campo negativo**; `Traceback` no log: 0 | `resumos/regressao_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo | **0 divergências** | `resumos/determinismo.txt` |
| A/B pareado 2.000 e 10.000 × 2 modos, 6 variantes + `antes` | tabelas acima; N = 2.000 dá as mesmas direções na troca (Beorn até T4 +4,2 ± 0,9 pts, cartas extras +1,07 ± 0,24, remoção própria −0,13) | `resumos/ab_*.txt` |
| reprodutibilidade (tabelas refeitas só dos brutos, `cmp`) | **10/10 byte a byte iguais**; `--tudo` (re-simulação) **não rodado** | `resumos/verificacao_reproducao.txt` |
| varreduras da Regra #10 sobre o Beorn | `audit_landfall_ordem` 0 candidatos (20 simuladores), `audit_compra_t1` COMPRA 20/20, `ast_sets` Beorn 0 hits | `../../../varredura-2026-10-05/resumos/*_2026-10-23.txt` |

**Aviso sobre a coluna "idênticas" da resiliência:** nas variantes com o Heirloom no baralho a resiliência mostra ~1% de partidas idênticas ao `antes`, porque o resultado dela é o `GameState` inteiro, que contém `library`/`hand`/`graveyard` com o **nome** da carta trocada; é artefato do critério, não "98% das partidas mudaram de caminho". Vale só para `so_gatilho_beorn` (mesmo baralho): 49,1%. O padrão compara um dicionário de métricas (sem nomes) e a coluna é interpretável (71% sem o Heirloom ou o Ram Through nas 8 turnos).

## Mapa arquivo → o que é → status
| arquivo | o que é | status |
|---|---|---|
| `codigo/beorn_goldfish_v1_ANTES_1b7dd73.py`, `codigo/beorn_goldfish_v1_DEPOIS.py`, `codigo/lista_{ANTES,DEPOIS}.md` | simulador e lista de antes / depois | usado |
| `dados/raw_ab_{2000,10000}[_resiliencia].json.xz` | bruto por partida, 7 variantes: `antes`, `depois`, `so_gatilho_beorn`, `troca_sem_habilidades`, `troca_so_mana`, `troca_so_compra`, `troca_gatilho_antigo` | usado |
| `dados/scryfall_oraculo_rulings_2026-10-23.json`, `dados/spellbook_antes_depois.json` | oráculo + rulings crus; respostas cruas do Spellbook | usado |
| `resumos/ab_*.txt` | cada variante × `antes` | usado |
| `resumos/comparacoes_entre_variantes_10000.txt` | a troca com o gatilho novo (`depois` − `so_gatilho_beorn`), a troca com o gatilho antigo, o que cada habilidade soma | usado |
| `resumos/resumo_descritivo_{antes,so_gatilho_beorn,depois}_10000.txt` | médias ± IC95% por campo | usado |
| `resumos/{smoke,bitident_20000,regressao_20000,determinismo,indice_dados,verificacao_reproducao}.*`, `cadeia_horarios.txt`, `log_driver.txt` | validação e índice | usado |
| `orquestracao/` | `driver.py`, `abgen.py`, `config.json`, `cadeia.sh`, `csb_beorn.py`, `enumera_condicoes.py`, `comparacoes.py`, `resumo_descritivo.py`, `verificar_reproducao.sh` | usado |

## Como refazer
```
bash descomprimir.sh                                   # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 comparacoes.py 10000 | cmp - ../resumos/comparacoes_entre_variantes_10000.txt
python3 resumo_descritivo.py depois 10000 | cmp - ../resumos/resumo_descritivo_depois_10000.txt
bash verificar_reproducao.sh                           # tabelas do A/B, comparações, resumos e índice: cmp byte a byte (~1 min)
bash verificar_reproducao.sh --tudo                    # re-simula smoke, bit-identidade, regressão e os 4 lotes do A/B (a cadeia original levou 9 min; não mude `config.json` nem `codigo/…DEPOIS.py`)
python3 csb_beorn.py ../../lista.md ../dados/spellbook_antes_depois.json   # refaz o Spellbook (rede) — a lista precisa ter o Ram Through; use codigo/lista_ANTES.md
sha256sum -c ../SHA256SUMS
```

## Escopo (Regra #7)
**Varrido:** as duas habilidades do Herd Heirloom contra o oráculo e a ruling; o gatilho da Beorn contra o oráculo e a ruling; as interações com as cartas da lista que o oráculo cita (script, acima); Spellbook antes/depois com controles; 14 testes dirigidos; bit-identidade, regressão e determinismo; A/B pareado; varredura dos 20 simuladores atrás do mesmo erro do gatilho de início de combate (`audit_inicio_de_combate.py`: 21 cartas em 10 decks). **Lidas à mão e sem o gate de ataque:** Kutzil (`beginning_of_combat_triggers`, 8 cartas), Mothman (Ouroboroid), Megatron (Nexus of Becoming e Steel Seraph), Prismatic Bridge (Innkeeper's Talent e Oko), Vihaan (Urabrask's Forge e o comandante), Rat King (Lord Skitter, função de uma linha). **Já corrigida antes:** Toph, Avatar Kyoshi (a nota está no `goldfish-log` do Toph: "nunca disparava se ela tivesse doença de invocação"; mesma classe). **NÃO lidas à mão:** The Ozolith nos 3 decks que o têm (Captain Storm, Bumbleflower, Toph); o script não acusa `can_attack` por perto, mas isso é só triagem.
**Não varrido / limites:** (1) **trample** não tem efeito neste goldfish (sem bloqueio modelado): 📊, só contagem; (2) **Genji Glove** (combate extra e dano duplo) faria o gatilho concedido disparar mais de uma vez por turno numa mesa real; o simulador não repete nenhuma compra por dano de combate no combate extra (já era assim para Ohran/Toski), então o valor do Heirloom com a Glove é **piso**; (3) a **política do `{T}`** é minha (compra primeiro; mana só sem alvo ou para o comandante) e não foi otimizada nem variada; (4) o valor real do Ram Through (interação a 2 mana com instantâneo) não cabe num goldfish solo; o proxy de "remoção própria conjurada" é contagem; (5) `--tudo` não foi rodado; (6) uma só família de sementes por lote; (7) a leitura "Beorn mais cedo" inclui +1,1 pt de convenção do simulador (item 5 da conclusão).
