# Bloodline Recollector // Ancestral Craving (Reality Fracture) no Edgar Markov — avaliação de 2026-11-04

Arquivo **permanente e auditável** do que sustenta a resposta ao usuário. A decisão e as tabelas legíveis estão em `edgar-markov-mardu/goldfish-log.md` (seção do topo) e `checklist-oraculo.md` (oráculo e as 15 rulings). **A carta NÃO entrou na `lista.md` nem no simulador do deck**; o que existe aqui é uma avaliação.

Pedido do usuário (2026-11-04): *"Consegui um bloodline recollector de reality fracture para o Edgar Markov. O Que vc me indicaria cogitar como carta para retirar para ele entrar? Ele vale mesmo a pena?"*

> **STATUS DESTA PASTA:** fechada em 2026-11-04. Verificação de reprodutibilidade: `bash orquestracao/verificar_reproducao.sh --tudo` → **15/15 saídas byte a byte iguais** (`resumos/verificacao_reproducao.txt`): tabelas do A/B refeitas só dos brutos, resumo, arquivo vivo == `codigo/..._VIVO_2026-11-04.py`, medição de mortes por turno e os 4 brutos do A/B re-simulados idênticos. A 1ª execução deu 14/15 (a diferença era só a linha de `time` colada na saída da medição; os números eram idênticos): guardada em `resumos/verificacao_reproducao_1a_execucao_14_de_15.txt`. **Não coberto por `cmp`:** o Spellbook (API externa; só o bruto da resposta está arquivado) e o texto interpretado deste LEIAME.

## Veredito (resumo; os números estão abaixo)

Vale como **troca barata, não como peça nova do motor**. 1ª opção de corte: **Bloodline Bidding**; 2ª: **Sevinne's Reclamation**. Não cortar peça de drain, de fichas ou do combo (as 4 peças que o Spellbook usa: Exquisite Blood, Vito Thorn of the Dusk Rose, Enduring Tenacity, Bloodthirsty Conqueror).

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver a decisão e o porquê | `../../goldfish-log.md` (seção do topo) |
| ver o oráculo e as rulings | `../../checklist-oraculo.md` (seção do topo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` |
| refazer TUDO (re-simula ~3 min; **não editar o simulador enquanto roda**) | `bash orquestracao/verificar_reproducao.sh --tudo` |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |

## O que foi feito, na ordem da CLAUDE.md (Regras #1 a #5 e o adendo da #4)

1. **Oráculo ao vivo (Regra #1/#2):** busca no Scryfall (`/cards/search?q="Bloodline Recollector"`): é o nome real da carta (`fra` nº 49, também 402, 427 e a promo 49p), **sem `flavor_name`**; layout `prepare`, `{1}{B}` 2/2 Vampire Warlock // `{B}` Instant. A carta já estava em `scryfall-cache/oracle-cache.json`. As 15 rulings foram baixadas (`rulings_uri`) e listadas no checklist **antes** de avaliar (Regra #3).
2. **Documentação do deck lida antes de listar motores (adendo, item 1):** `auditoria.md` (motores: Eminence, drenagem por morte, o combo Exquisite Blood + Vito, Bracket 3 com 3 Game Changers), `checklist-oraculo.md` e `goldfish-log.md`, com grep de "combo/infinit/loop" e do nome de cada candidata a corte.
3. **Condições enumeradas por script (adendo, item 4), lendo o `oracle_text` e o `type_line` do cache:** **21 Vampiros** na lista fora o Edgar (22 com a BR); 14 formas de sacrificar (6 grátis: Viscera Seer, Bartolomé, os 2 altares, Goblin Bombardment, Phyrexian Tower; 5 pagas: Indulgent Aristocrat, Fountainport, Mondrak, Westvale Abbey, Sorin; 3 magias: Plumb the Forbidden, Diabolic Intent, Rite of Oblivion); 9 pagadores de morte (Blood Artist, Zulaport, Cruel Celebrant, Vindictive Vampire, Bastion, Funeral Room, Vein Ripper, Meathook Massacre, e a Cordial Vampire com contadores); 4 formas de recursão em massa ou barata (Sevinne's Reclamation, Bloodline Bidding, Agadeem's Awakening, Awakening Hall) mais Nullpriest e Rite of Oblivion. A classificação por regex foi triagem; as candidatas foram lidas à mão.
4. **Commander Spellbook antes/depois, com controles (adendo, item 2):** os 98 nomes (lista + a BR + os 3 do controle) foram resolvidos antes (**0 não reconhecidos**; a BR é reconhecida como `Bloodline Recollector // Ancestral Craving`); controle positivo (Basalt Monolith + Rings of Brighthearth) apareceu e controle de corte (com Mind Stone sumiu) passou. Resultado: ANTES = 4 combos (Exquisite Blood + Vito Thorn; Exquisite Blood + Enduring Tenacity; Bloodthirsty Conqueror + Vito Thorn; Bloodthirsty Conqueror + Enduring Tenacity), 183 "quase", tag **S**, 3 Game Changers; **+BR = os mesmos 4 combos, os mesmos 183 "quase" (nenhum cita a BR), mesmo bracket**. Das **93 trocas (sai X, entra a BR) só 4 perdem combo**: as 4 peças acima, 2 combos cada. Nenhuma troca ganha combo.
5. **Simulador como apoio (Regra #5), não como árbitro:**
   - **`medir_mortes_e_potencial.py`:** o gatilho da carta ("three or more creatures died this turn") o simulador **não consegue exercer por construção**: `sac_loop` sacrifica no máximo 2 fichas de Vampiro por turno e nunca uma criatura nomeada. Em 10.000 partidas (8 turnos): ≥ 2 mortes no fim de algum turno em 39,6% das partidas (é o gatilho do Emeritus of Woe, já modelado), **≥ 3 em 3,4%**, e "outlet grátis em campo + ≥ 3 fichas de Vampiro no início do `sac_loop`" em 13,8%. É um **piso** (só as fichas da Eminence entram na conta; o simulador não sacrifica criatura nomeada nem conta fichas de outras fontes).
   - **`ab_br.py`:** A/B pareado (mesmas sementes; N=2.000 e 10.000; modos padrão e resiliência) com a BR entrando como **proxy-piso** (`codigo/edgar_markov_goldfish_v1_BR_PROXY.py`: corpo 2/2 Vampiro, Eminence e Welcoming Vampire, **sem** a habilidade de preparar) no lugar de cada candidata, na MESMA posição da lista. Controle: o arquivo-proxy com a lista atual é **idêntico** ao `antes` em todas as partidas (N=10.000 e N=2.000, nos 2 modos).

## Resultado do A/B (N=10.000, modo padrão; diferença pareada ± IC95%; médias do `antes`: dreno 5,883, fichas da Eminence 3,006, ganho de vida 4,030)

| BR no lugar de… | dreno | fichas Eminence | ganho de vida | leitura |
|---|---|---|---|---|
| Zulaport Cutthroat | −0,176 ± 0,027 | +0,172 ± 0,009 | −0,162 ± 0,020 | custa dreno (não é Vampiro; ganha fichas) |
| Vindictive Vampire | −0,198 ± 0,034 | +0,062 ± 0,008 | −0,146 ± 0,026 | custa dreno |
| Cordial Vampire | 0,000 | 0,000 | 0,000 | o simulador não vê os contadores dele (sem payoff numérico modelado) |
| Funeral Room // Awakening Hall | +0,075 ± 0,034 | +0,213 ± 0,012 | −0,001 ± 0,024 | no modo resiliência dreno −0,190 ± 0,036 |
| Sevinne's Reclamation | +0,173 ± 0,033 | +0,177 ± 0,010 | +0,115 ± 0,022 | o simulador quase não a usa |
| **Bloodline Bidding** | **+0,187 ± 0,038** | +0,194 ± 0,012 | +0,153 ± 0,027 | maior ganho no simulador |
| Call the Coppercoats | +0,066 ± 0,025 | +0,144 ± 0,009 | +0,059 ± 0,019 | **a carta nunca é conjurada no simulador** (`EXCLUDE_BLIND_CAST`: depende de criatura de oponente), então "custo 0" é artefato |
| Charismatic Conqueror | +0,008 ± 0,011 | +0,004 ± 0,002 | +0,003 ± 0,007 | corpo por corpo; o gatilho dela também depende de oponente |
| Spectator Seating (terreno) | −0,134 ± 0,058 | +0,117 ± 0,014 | −0,073 ± 0,041 | −0,124 terrenos jogados |
| Plains (terreno) | −0,086 ± 0,058 | +0,101 ± 0,014 | −0,086 ± 0,045 | −0,110 terrenos jogados |

Tabelas inteiras (15 campos + os mais movidos) em `resumos/ab_*.txt`; esta tabela em `resumos/resumo_ab_10000.md` (também modo resiliência). Fração de partidas idênticas ao `antes`: 78% a 98% por variante no modo padrão. **No modo resiliência a fração aparece 0,0% por um artefato:** a impressão digital inclui a biblioteca inteira, que muda sempre que a lista muda; o controle (lista atual) dá todas as partidas idênticas.

## Por que essas escolhas (deck primeiro, simulador depois)

- **Cortar o Bloodline Bidding:** `{6}{B}{B}` com convoke, devolve todos os Vampiros do cemitério; a recursão da lista já tem o **Awakening Hall** (também `{6}{B}{B}` e em massa), o Agadeem's Awakening, o Sevinne's Reclamation, o kicker do Nullpriest e o flashback do Rite of Oblivion. Nenhum motor depende dele e o simulador ganha dreno e fichas quando ele sai (modo padrão e resiliência).
- **Segunda opção, Sevinne's Reclamation:** é a recursão BARATA (MV ≤ 3, flashback) que devolve Blood Artist, Cruel Celebrant, os altares e o Skullclamp depois de um wipe; só cortar se preferir manter o Bidding como seguro tardio.
- **Não cortar Zulaport/Vindictive Vampire:** são pagadores de morte (o simulador mostra −0,18 e −0,20 de dreno) e o Zulaport é um dos iniciadores redundantes do combo; **não cortar** Exquisite Blood, Vito Thorn, Enduring Tenacity e Bloodthirsty Conqueror (o Spellbook mostra que cada uma carrega 2 combos).
- **A carta em si:** Vampiro de 2 de mana que dispara a Eminence (ficha 1/1 lifelink) e o Welcoming Vampire; o "comprar 3" exige 3 mortes no mesmo turno (qualquer criatura, de qualquer jogador, em qualquer end step). Linhas diretas na lista: **The Meathook Massacre com X=1** (mata as fichas 1/1 e a BR 2/2 sobrevive, e cada morte minha drena 1), **Plumb the Forbidden** sacrificando 3, e qualquer outlet com 3 corpos. Ela é do mesmo tipo que o **Emeritus of Woe** (prepara com 2+ mortes no MEU end step), com limiar maior (3) e janela maior (todo end step). A cópia é Instant (não é Vampiro), então lançá-la não dispara a Eminence; mirar um oponente é um início possível do loop (redundante e dá 3 cartas a ele).

## Mapa: arquivo → o que é → código → status → onde aparece

| arquivo | o que é | código | status | onde aparece |
|---|---|---|---|---|
| `dados/spellbook_br_raw_2026-11-04.json.xz` | respostas CRUAS do Spellbook (ANTES, +BR, 2 controles, 93 trocas) com a entrada enviada | `orquestracao/spellbook_br.py` | usado (API externa: não re-executado na verificação) | goldfish-log; este LEIAME |
| `dados/spellbook_br_2026-11-04.json` | resumo derivado (nomes reconhecidos, controles, combos, o que cada troca perde/ganha) | idem | usado | idem |
| `dados/raw_ab_2000.json.xz`, `raw_ab_10000.json.xz` (+ `_resiliencia`) | A/B pareado: `antes`, controle do proxy e 10 trocas, N=2.000 / 10.000 | `orquestracao/ab_br.py` | usado | `resumos/ab_*.txt`, `resumo_ab_10000.md`; log |
| `resumos/ab_*.txt` | tabelas pareadas (diferença ± IC95%) | `orquestracao/refaz_tabelas.py` (só dos brutos) | usado | log |
| `resumos/resumo_ab_10000.md` | tabela-resumo + médias do `antes` | `orquestracao/resumo_br.py` | usado | log |
| `resumos/mortes_e_potencial_10000.txt` | mortes por fim de turno e potencial de linha deliberada | `orquestracao/medir_mortes_e_potencial.py` | usado | log |
| `resumos/mortes_e_potencial_10000_COM_tempo_1a_saida.txt` | a mesma saída com as linhas de `time` coladas (números idênticos) | idem | **SUPERADO** (guardado) | — |
| `resumos/spellbook_br_saida.txt`, `log_ab.txt` | logs | — | log | — |
| `resumos/verificacao_reproducao.txt` (+ `_1a_execucao_14_de_15`) | saída de `verificar_reproducao.sh --tudo` (15/15) e da 1ª execução (14/15, superada) | `orquestracao/verificar_reproducao.sh` | verificação | — |
| `resumos/indice_dados.md` | o que há em cada arquivo de `dados/` | `indice_dados.py` | índice | — |
| `codigo/edgar_markov_goldfish_v1_VIVO_2026-11-04.py` | o simulador vivo usado como `antes` (== `edgar-markov-mardu/edgar_markov_goldfish_v1.py`, `cmp` em `--tudo`) | — | usado | — |
| `codigo/edgar_markov_goldfish_v1_BR_PROXY.py` | o mesmo arquivo + a BR como corpo de Vampiro (**proxy-piso, não a carta completa**) | — | usado | — |

## Atualização de 2026-11-05: a mesa do usuário tem 3 oponentes em média (mesa de 4)

Resposta do usuário à pergunta que ficou em aberto: *"3 oponentes em media"* (sobre wipes ele não respondeu). Efeito na avaliação, **sem novo A/B** (o modo resiliência do simulador já assume `NUM_OPPONENTS = 3`, então as linhas "resiliência" acima já são de mesa de 4):

- **A BR sobe de valor:** o gatilho checa 4 end steps por rodada (1 meu e 3 deles) e conta morte de qualquer jogador; Meathook X=1 também mata os x/1 dos oponentes; o Ophiomancer cria uma Cobra em CADA upkeep (4 por rodada) e vira combustível de outlet. O Craving se mira em si mesmo (dar 3 cartas a um de 3 oponentes só como finalização).
- **Pagadores "each opponent" valem mais que o simulador mostra:** `lose_life_opponent` soma 1 por gatilho, não 1 por oponente, então os −0,18 (Zulaport) e −0,20 (Vindictive Vampire) do A/B são **pisos**; mais um motivo para não cortá-los.
- **Call the Coppercoats e Charismatic Conqueror sobem** (o simulador é cego a eles): a Coppercoats mirando os 3 oponentes custa 7 de mana (`{2}{W}` + 2 × `{1}{W}`) e cria uma ficha por criatura deles; a Conqueror dispara com cada permanente que eles põem. Não cortar.
- **Recomendação mantida: cortar o Bloodline Bidding** (o Awakening Hall faz o mesmo trabalho pesado). Jogos mais longos e wipes dão mais valor à recursão barata, então o **Sevinne's Reclamation deixa de ser uma boa 2ª opção**; só vale cortá-lo se a mesa quase não tiver wipe (pergunta ainda sem resposta).
- Terrenos `Spectator Seating` e `Luxury Suite` entram desvirados com 2+ oponentes, então ficam melhores nesta mesa.

## Escopo (Regra #7): o que esta avaliação NÃO fez

- **Não modelei a habilidade da carta** (preparar com 3 mortes e a cópia do Ancestral Craving): o simulador não a exerce (cap de 2 sacrifícios de ficha por turno, nunca criatura nomeada). Os números do A/B são o custo de cada corte e o valor do **corpo**, um piso. Modelar linhas deliberadas de 3 mortes seria um conserto do simulador (Regra #5), não feito aqui.
- **Não sei a frequência real do gatilho na mesa do usuário** (nº de oponentes, wipes, combate). O 13,8% é um piso do simulador.
- **O simulador é cego a:** os contadores da Cordial Vampire (sem payoff numérico) e ao Call the Coppercoats e ao Charismatic Conqueror (dependem de criatura de oponente). Para esses três o "custo" do A/B não vale como evidência.
- Não rodei as varreduras da Regra #10 (a lista e o simulador do Edgar não mudaram) e não alterei `lista.md`, `edgar_markov_goldfish_v1.py` nem a skill.
- O Spellbook só vê combos que ele conhece; a BR é recente (lançada em 2026-10-02) e pode ainda não ter combos cadastrados: "nenhum combo novo" vale para o que ele sabe hoje.
