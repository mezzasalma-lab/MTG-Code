# The Wise Mothman — partida manual #2 (2026-10-06): dados brutos, scripts, ledger e rulings

Arquivo da Regra #8 (`CLAUDE.md`). **Status: auditoria feita; respostas do usuário recebidas em 2026-10-07** (no fim; a resposta 3 chegou cortada). Resumo em prosa: `../../goldfish-log.md` §9; cláusula a cláusula: `../../checklist-oraculo.md` §9.
Pedido do usuário (2026-10-06): *"Mais um goldfish. 1ª mão sem lands, 2ª mão uma land apenas, 3ª mão (mulligan 1) que dei keep foi essa na foto. […] Me enrolei no começo da fase de combate porque tinha que colocar milhares de marcadores nas criaturas, analise esse e me pergunte qualquer dúvida."*
7 turnos (rodadas); simulador de interação **On**, mas o oponente simulado **não jogou nenhuma interação** (zona `opponentsCards` vazia). O log **termina no meio do gatilho de combate do T7** (só o Ouroboroid recebeu os contadores).

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do Archidekt playtester que o usuário colou (7 elementos = 7 turnos, 154 registros), extraído **por script, sem redigitar** (`orquestracao/extrair_json_da_conversa.py`). A mensagem chegou **no meio de um turno do assistente** e o registro da sessão a guarda como `attachment`, não como mensagem `user`: o script olha as duas formas (a 1ª versão, só com `user`, não achou a mensagem).
- Mão da foto (mulligan, simulador de interação On): Kami of Whispered Hopes, The Party Tree (= **The Great Henge**, nome de capa; Regra #2), Takenuma, Basking Broodscale, Gyre Sage, Island e a 7ª carta fora do enquadramento, a **Freestrider Lookout**, que o log manda para o **fundo da biblioteca** (`hand → library`). A compra do T1 (Zagoth Triome) foi jogada virada.
- Oráculo e rulings **lidos ao vivo** (`resumos/rulings_scryfall.json`, 16 cartas); todas as 23 cartas do log já estavam no `scryfall-cache/oracle-cache.json`.
- Simulador usado no teste dirigido: o arquivo vivo `../../mothman_goldfish_v1.py` (as 5 conferências não dependem da chave `LANDFALL_PAYOFF_FIRST`).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida | usado |
| `analisa_partida.py` → `resumos/trace.md` | trace turno a turno | usado (`cmp`) |
| `orquestracao/estado_por_turno.py` → `resumos/estado_por_turno.txt` | mão / campo / cemitério ao fim de cada turno | apoio |
| `mana_por_turno.py` → `resumos/mana_por_turno.md` | legalidade da mana de T2-T6 sob duas leituras da Gyre Sage (texto real × "por ponto de poder") | usado (`cmp`) |
| `ledger_contadores.py` → `resumos/ledger_contadores.md` | (1) contadores evento a evento com Kami e Constrictor; (2) compras do Henge; (3) rad com o Constrictor; (4) jogadas de terreno | usado (`cmp`); **eventos e alvos são leitura minha do trace**, conferidos por `assert` contra os contadores finais por turno |
| `orquestracao/confere_simulador.py` → `resumos/confere_simulador.txt` | 5 testes dirigidos: o simulador acerta o que o log errou? | usado (`cmp`) |
| `orquestracao/baixar_rulings.py` | oráculo e rulings ao vivo | apoio |
| `orquestracao/verificar_reproducao.sh` | refaz todas as saídas e compara com `cmp` | → `resumos/verificacao_reproducao.txt` |

## Resultado em 1 minuto (medido; as interpretações estão marcadas)
**Provado pelo log, sem depender de nada que ele não registra:**
1. **T3 e T4 não fecham de mana com o texto real da Gyre Sage** (*"{T}: Add {G} for each +1/+1 counter on this creature"*): T3 — Mothman custa 4, havia Swarmyard + Island + Triome = 3 e a Gyre Sage ainda sem contador (0 mana); T4 — o Henge custa `{7}{G}{G}` menos o maior poder (Mothman 3 + 1 contador = 4) = **5**, havia 4 fontes. **Os dois fecham se a Gyre Sage der 1 G por ponto de PODER** (1 e 2), a leitura que parece ter sido usada. T2, T5 e T6 fecham em qualquer leitura.
2. **T4: nenhuma jogada de terreno**, com a Takenuma na mão (foi a única rodada sem terreno); com ela o T4 teria 5 fontes e o Henge caberia.
   → **Resposta:** "Sim, esqueci."
3. **T4: a Broodscale entrou com o Henge em campo e não há a compra do Henge** no log (1 compra a menos); T5 (2 compras) e T6 (1) batem.
4. **Contadores: as substituições do Kami e do Winding Constrictor foram aplicadas pela metade.** Pela regra, cada colocação de `n` contadores vira `n + #Kami + #Constrictor`. No log: T5 Constrictor (Henge) 1 em vez de 2; T5 Kami 2 em vez de 3; T6 Ouroboroid entrando 2 em vez de 3; T6 gatilho do Mothman no Ouroboroid +2 em vez de +3; **T6 gatilho de combate: +6 por criatura (5 + 1) em vez de +7 (5 + 1 + 1)**, +5 na Broodscale, **0 na ficha Eldrazi Spawn** (criatura: devia ter +7). O gatilho do Mothman do T5 (+3 no Mothman) e o do **T7 (11 + 1 + 1 = +13 no Ouroboroid)** estão **certos**. A Gyre Sage ganhou +2 no T5 que o ledger não explicava (a evolve não dispara com Constrictor 2/3 nem Kami 1/1 entrando): **retirado como achado depois da resposta 5** (fonte: mill do rad com o Mothman).
5. **O erro se compõe**, porque o Ouroboroid usa o próprio poder: com c contadores ele passa a **2c + 3** a cada combate (X = 1 + c, mais 2 das substituições). Pelas regras, com as mesmas escolhas de alvo, o fim do T6 seria Mothman 13, Broodscale 10, Constrictor 11, Kami 12, Ouroboroid 15 (log: 10, 6, 7, 8, 10) e o gatilho do T7 seria X = 16, +18 por criatura (log: X = 11, +13).
6. **Rad:** com o Constrictor em campo o Mothman dá **2** rad counters a você por ETB/ataque. T6 e T7 ficam **≥ 1 mill abaixo** do exigido (limite inferior firme); T5 tem 1 mill a mais do que a fonte conhecida.
   → **Resposta:** "Fiz um rad só, e não 2." (confirma o limite inferior dos mills de T6 e T7)
7. **Mulligan:** o log mostra 1 carta indo ao fundo (Freestrider Lookout), coerente com o 1º mulligan grátis + 1 mulligan (London). Nada a corrigir.

**O simulador acerta tudo isso** (`resumos/confere_simulador.txt`, 5 de 5): Gyre Sage dá 1 G por contador, o Henge custa 5 com o Mothman a 4 de poder, 1 contador com Kami + Constrictor vira 3, o Constrictor soma 1 ao rad que você recebe, e o gatilho de combate do Ouroboroid com o estado do T6 do log dá +7 por criatura, ficha inclusive.

## O que o script prova e o que não prova
**Prova:** mana viável por turno (total e cores) sob cada leitura; contadores postos (diferença por registro); compras e mills por turno; jogadas de terreno.
**Não prova:** vida, marcadores de rad (o log não os registra), a ordem da pilha, quais fontes pagaram o quê, os alvos de gatilhos além do que o log mostra, e **nada do que veio depois do último registro** (T7 interrompido). Os registros duplicados (`Winding Constrictor` e `Kami` com dois `hand → battlefield` no T5; a Gyre Sage virada e desvirada no mesmo turno no T5) são ruído do playtester (desfazer): não foram tratados como jogada.

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh` em 2026-10-06: **5 de 5 saídas byte a byte iguais** (`cmp`), cada uma com um `PYTHONHASHSEED` diferente (11-15): trace, estado por turno, mana, ledger e as 5 conferências do simulador.
**Não conferido:** a extração do JSON da conversa (depende do registro da sessão, fora do repositório) e `rulings_scryfall.json` (depende da API).

## Perguntas feitas ao usuário (2026-10-06) e respostas (2026-10-07)
1. **Gyre Sage (T3 e T4):** você leu a mana dela como 1 G por ponto de poder? Pelo texto é 1 G por **contador**. Ou jogou a Takenuma no T4 e o log não registrou?
   → **Resposta:** "Li errado, que ela gerava 1 mana por ponto de poder." (confirma a leitura; o simulador estava certo)
2. **T4:** a compra do Henge para a Broodscale foi esquecida?
   → **Resposta:** "Sim, esqueci."
3. **Kami e Constrictor (T5 e T6):** a colocação do Constrictor no próprio Constrictor (Henge) e a do Kami no próprio Kami você não aplicou de propósito? E no combate do T6 só uma das duas valeu (+6), enquanto no T7 as duas valeram (+13): foi só cansaço da contagem?
   → **Resposta (cortada na mensagem):** "Eu baixei o Constrictor primeiro e o Kami depois, então…". A ordem coincide com a que o ledger já assumia (Constrictor com Kami 0 / Constrictor 1; Kami com 1/1). Não explica o +1 do próprio Constrictor sobre si mesmo; **sem resposta completa**.
4. **Fichas Eldrazi Spawn:** você contou que elas são criaturas e recebem os contadores do Ouroboroid?
   → **Resposta:** "Esqueci."
5. **Gyre Sage +2 no T5:** de onde vieram?
   → **Resposta:** "Do mill do rad counter e Mothman." O Mothman dá rad a cada jogador, então o mill do rad dos oponentes (nos turnos deles, fora do log) também dispara o Mothman: compatível, mas de quem foi o mill **não consta**. Achado "sem fonte" **retirado**; `ledger_contadores.py` passa a usar esse +2 (Gyre Sage 12 no replay do fim do T6).
6. **Rad:** você sabia que o Constrictor dá 2 rad counters por ETB/ataque do Mothman, e fez o mill do rad no T6 e no T7?
   → **Resposta:** "Fiz um rad só, e não 2." (confirma o limite inferior dos mills de T6 e T7)
7. **T7:** o log termina no gatilho do Ouroboroid. O resto do turno (ataque, outros gatilhos) você jogou? Se quiser, mando a fórmula `c → 2c + 3` e uma tabela de contadores por criatura para não precisar clicar um a um.
   → **Resposta:** "Parei antes de somar os counters do Ouroboroid, já tinha errado tudo mesmo." (confirma que o log termina ali por escolha)
