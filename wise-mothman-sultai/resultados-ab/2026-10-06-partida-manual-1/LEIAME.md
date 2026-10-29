# The Wise Mothman — partida manual #1 (2026-10-06): dados brutos, scripts, ledger e rulings

Arquivo da Regra #8 (`CLAUDE.md`). **Status: auditoria feita; aguardando as respostas do usuário** (perguntas no fim). Resumo em prosa: `../../goldfish-log.md` §7; cláusula a cláusula: `../../checklist-oraculo.md` §7.
Pedido do usuário (2026-10-06): *"Goldfish do Mothman manual, mão inicial em anexo"*, com o aviso de que **o log não contém o mill dos oponentes** (nem o de Memory Erosion por magia, nem o do Ruin Crab quando entram terrenos, que "pode chegar a 2 vezes/turno com o Icetill Explorer").
É a 1ª partida manual do Mothman; 9 turnos (rodadas); simulador de interação **On** (o oponente simulado conjurou Aven Mindcensor no T6 e Evacuation no T7).

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do Archidekt playtester que o usuário colou na conversa (9 elementos = 9 turnos, 176 registros), extraído **por script, sem redigitar** (`orquestracao/extrair_json_da_conversa.py`, lê o registro da sessão).
- `dados/mao_inicial.webp`: a foto da mão inicial (mulligan **0**, 7 cartas, *keep*): Six, Misty Rainforest, Hedge Shredder, Memory Erosion, Wave Goodbye, Strip Mine, Takenuma, Abandoned Mire. A 8ª carta do T1 (Watery Grave) é a compra do turno (Commander multiplayer: ninguém pula a 1ª compra).
- Oráculo e rulings **lidos ao vivo** do Scryfall (`resumos/rulings_scryfall.json`, 23 cartas; lidas antes de concluir, Regra #3). Foram acrescentadas ao `scryfall-cache/oracle-cache.json` as 2 que faltavam: **Evacuation** e **Aven Mindcensor** (interação do oponente simulado).
- Simulador usado no ensaio: cópia **fixada** do commit `91b1a3d` (`codigo/mothman_goldfish_v1_91b1a3d.py`, idêntica ao arquivo vivo no momento da cópia).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida | usado |
| `dados/mao_inicial.webp` | foto da mão inicial | referência |
| `analisa_partida.py` → `resumos/trace.md` | trace turno a turno: mudanças de zona, viradas, marcadores, resumo por turno | usado (`cmp` conferido) |
| `orquestracao/estado_por_turno.py` → `resumos/estado_por_turno.txt` | mão / campo / cemitério / zona do oponente ao fim de cada turno (último registro de cada id) | apoio |
| `mana_por_turno.py` → `resumos/mana_por_turno.md` | prova de que a mana de cada turno T2-T9 é **viável** (total e cores) com as fontes que o log mostra viradas | usado (`cmp`) |
| `ledger_mill.py` → `resumos/ledger_mill.md` | (1) mill meu esperado × log; (2) contadores +1/+1 esperados (com Kami e Hardened Scales) × log; (3) mill de oponente reconstruído; (4) jogadas de terreno × Ruin Crab; (5) Six que não atacou | usado (`cmp`); **os eventos por turno são leitura minha do trace** (suposições no cabeçalho do script, conferidas por `assert` contra os contadores do log) |
| `orquestracao/ensaio_simulador.py` → `resumos/ensaio_simulador.txt` | reconstrói no simulador o **início** de T6-T9 a partir do log (biblioteca = lista menos as cartas já vistas) e roda 1 turno, 300 sementes cada | apoio (Regra #5: o simulador não é o árbitro) |
| `orquestracao/baixar_rulings.py` | baixa oráculo e rulings e acrescenta ao cache só as cartas novas | apoio |
| `orquestracao/verificar_reproducao.sh` | refaz todas as saídas de `resumos/` e compara com `cmp` | → `resumos/verificacao_reproducao.txt` |

## Resultado em 1 minuto (o que está medido; as interpretações estão marcadas)
**Provado pelo log, sem depender do mill de oponente:**
1. **Nenhuma jogada impossível.** A mana de T2-T9 fecha (6 dos 8 turnos sem nenhuma sobra), os retraces da Six (Icetill T5, Ruin Crab T6, Hardened Scales T7) descartam terreno e pagam o custo, a Wave Goodbye devolveu exatamente as criaturas **sem** contador (Patron e Shredder) e a Evacuation devolveu as outras 5.
2. **A substituição do Kami of Whispered Hopes nunca foi aplicada.** Houve **7 colocações** de contador com o Kami em campo (T5: 1, T6: 3, T7: 3) e todas aparecem com +1 onde a regra manda +2 ("that many plus one"; vale também para o próprio Kami). São 7 contadores a menos.
3. **3 gatilhos do Mothman por mill MEU ficaram sem nenhum contador:** T4 (Six ataca: Bramble Familiar + Icetill Explorer, X = 2, Mothman já em campo), T7 (Hollowmurk Siege, X = 1) e T8 (Palantír, X = 1). Pode ter sido "até X" = 0 alvos; a pergunta 2 abaixo decide.
4. **Faltam mills MEUS:** T6 e T8 ficam com **≥ 1 carta a menos** do que as regras exigem (limite inferior firme, pelo rad garantido pelo ataque do Mothman no turno anterior). O log não diz se foi o rad ou o landfall do Icetill.
5. **Jogadas de terreno:** Icetill dá 2 jogadas por turno e deixa jogar terreno do cemitério. T6: 1 de 2; T7: **0 de 2**; T8: 1 de 2; T9: 0 de 2 (o log termina depois do ataque). Em T6-T9 havia terreno disponível (Misty, Waterlogged Grove, Urza's Saga, Takenuma, Agadeem) e o Ruin Crab em campo: **6 gatilhos do Crab perdidos** (T6: 1, T7: 2, T8: 1, T9: ≤ 2).
6. **A Six não atacou em T5, T6 e T7** (desvirada): 3 ataques que seriam 3 eventos de mill meu de 3 cartas + 1 terreno para a mão cada.

**Reconstruído (não está no log; o usuário avisou):** o mill de oponente acontece em **4 eventos** (Memory Erosion no T6 e no T7; Ruin Crab no T7 via Hedge Shredder e no T8 via Urza's Saga do cemitério) = **22 cartas milladas, ~13,8 não-terrenos**, e 4 gatilhos extras do Mothman (esperado: X ≈ 5,6 não-terrenos por gatilho do Crab, com 3 oponentes). Total de contadores esperados pelas regras: **45,3 contra 7 no log** (23,3 deles dependem desse mill de oponente; 15,0 são colocações/gatilhos do mill meu).

**Ensaio no simulador (evidência de apoio):** o mesmo campo, jogado pelo simulador, entra em média **7,0 terrenos no T7** (2,0 deles saem do cemitério pelo Icetill; o resto vem do Hedge Shredder e de fetch), com **7,0 gatilhos do Ruin Crab e 64 cartas milladas dos oponentes**; no jogo manual foi 1 terreno e 1 gatilho. T8: 2,9 gatilhos (manual: 1); T9: 2,9 (manual: 0 até o fim do log).
Isto não diz que o simulador joga certo: ele só mostra que as regras, o Icetill e o Hedge Shredder produzem essa cadeia (terreno milado vira terreno em campo, que dispara o Crab e o Icetill de novo).

## O que o script prova e o que não prova
**Prova:** mana viável por turno; terrenos que entram, de onde, e quando (por registro); contadores postos (diferença por registro); que o Kami estava em campo quando cada contador foi posto.
**Não prova:** vida (shocks, fetch, Waterlogged Grove, rad), marcadores de rad (o log não os registra), a ordem da pilha, quais fontes pagaram o quê, **quais cartas** o oponente milou, escolhas de alvo do Mothman além do que o log mostra, e o que o usuário fez depois do ataque do T9.
**Limites do ensaio:** rad = 0; biblioteca desconhecida além do que o log mostra (a lista menos as cartas já vistas, embaralhada por semente); o Mothman devolvido à mão vale como zona de comando sem imposto; o simulador joga com a política dele (ataca com tudo, 3 oponentes passivos).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh` em 2026-10-06: **5 de 5 saídas byte a byte iguais** (`cmp`): trace, estado por turno, ledger, mana e ensaio (300 sementes × 4 turnos, simulador fixado), cada uma re-gerada com um `PYTHONHASHSEED` diferente (11-15). Os scripts de texto também foram rodados com `PYTHONHASHSEED` 0, 1 e 99: saída idêntica.
**Não conferido:** a extração do JSON da conversa (depende do registro da sessão, que não está no repositório) e `rulings_scryfall.json` (depende da API).

## Perguntas ao usuário (nada abaixo foi tratado como erro seu até você responder)
1. **Kami (T5-T7):** os contadores +1 (e não +2) foram esquecimento da substituição do Kami, ou você jogou assim de propósito?
2. **Mothman T4 (X = 2), T7 (Siege) e T8 (Palantír):** você escolheu "até X" = 0 alvos, ou esqueceu o gatilho?
3. **Rad:** você fez o mill do rad no início da fase principal (T5-T9)? O log mostra 2 cartas no T5 (rad + landfall), mas só 3 no T6 (esperado ≥ 4) e 1 no T8 (esperado ≥ 2).
4. **Contadores do mill de oponente:** os gatilhos do Mothman do Ruin Crab (T7, T8) e do Memory Erosion (T6, T7) foram aplicados fora do log, ou ficaram de fora?
5. **T7:** por que a Wave Goodbye na própria mesa (devolveu Patron e Shredder)? Era para rejogar o Patron?
6. **Jogadas de terreno T6-T9:** não usar a 2ª jogada / terreno do cemitério foi escolha ou esquecimento? E o T9 continuou depois do ataque?
7. **Six sem atacar em T5-T7:** escolha (por causa do Aven Mindcensor?) ou esquecimento?
8. **T7, Forest `cv1h`:** o log tem `graveyard → hand` e depois `graveyard → battlefield` (tapada). Foi o Hedge Shredder (milada → campo) e você arrastou à mão por engano e desfez?
