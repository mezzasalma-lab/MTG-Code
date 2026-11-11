# The Wise Mothman: partida manual #3 (2026-11-11): dados brutos, scripts, ledger, rulings, testes e conferência do simulador

Arquivo da Regra #8 (`CLAUDE.md`). **Status: compilada com as respostas do usuário (2026-11-11)**. Resumo em prosa: `../../goldfish-log.md` §25; cláusula a cláusula: `../../checklist-oraculo.md` §25. A correção do simulador que esta partida revelou está em `../2026-11-11-plaza-comandante/`.
Pedido do usuário (2026-11-11): *"Mais um goldfish DO Wise Mothman: Mão inicial na foto. Segue o log"* (e, depois das minhas 7 dúvidas, as respostas dele). **6 turnos**; simulador de interação **On** (uma só interação: a Dark Deal no T4); o usuário **parou o goldfish no T6**.

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do playtester do Archidekt que o usuário colou (6 elementos = 6 turnos, 84 registros), extraído **por script, sem redigitar** (`orquestracao/extrair_json_da_conversa.py`); o `.json` solto foi conferido contra o `.xz` e apagado. `dados/mensagem_usuario_original.txt.xz` guarda a mensagem inteira.
- **Foto da mão inicial** (`dados/mao_inicial_foto.webp`; "Keep this", **Mulligan (0)**, simulador de interação **On**): Breeding Pool, Forest, Plaza of Heroes, Forest, An Offer You Can't Refuse, Tropical Island, Forest. É exatamente a ordem das 7 primeiras compras do T1; a 8ª (Altar of the Brood) é a compra do turno. Sem mulligan.
- Oráculos: `scryfall-cache/oracle-cache.json` (as 17 cartas reais do log estão no cache e na `lista.md`; a **Dark Deal** é do oponente simulado).
- Rulings (Scryfall, ao vivo, 2026-11-11) de 17 cartas em `resumos/rulings_scryfall.json` (40 rulings, 0 erros), **lidas antes de concluir**: as decisivas são as do **The Wise Mothman de 2024-03-08** (*"The cards are milled all at once, so abilities that trigger 'whenever one or more nonland cards are milled' will trigger exactly once as long as at least one nonland card was milled"* e *"If more than one player is instructed to mill at the same time ... The Wise Mothman's last ability will trigger just once"*).
- Regras: `rules-cache/comprehensive-rules.txt` (CR em vigor desde 2026-09-25, regra permanente §18); trechos em `resumos/cr_trechos.txt` (728.1 rad, 702.81a retrace, 701.17a mill, 305.2 um terreno por turno, 122.1i).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz`, `dados/mensagem_usuario_original.txt.xz`, `dados/mao_inicial_foto.webp` | log bruto, mensagem e foto | bruto |
| `analisa_partida.py` → `resumos/trace.md` | trace por turno (cópia do script da #2) | usado (`cmp`) |
| `orquestracao/estado_por_turno.py` → `resumos/estado_por_turno.txt`; `orquestracao/sequencia_bruta.py` → `resumos/sequencia_bruta.txt` | estado ao fim de cada turno; os 84 registros em ordem | apoio (o log **não registra ficha que some nem mill de oponente**) |
| `orquestracao/checagens_preliminares.py` → `resumos/checagens_preliminares.txt` | cor do Mothman no T4, Dark Deal, devoluções do T6, terrenos, mills próprios, contadores | usado (`cmp`) |
| `ledger_contadores.py` → `resumos/ledger_contadores.md` | TETO de gatilhos legítimos do Mothman por bloco × contadores do log; devoluções da Witness × eventos de contador | usado (`cmp`); as fontes são leitura minha + respostas do usuário (cabeçalho do script) |
| `testes_manual3.py` → `resumos/testes_manual3.txt` | 13 testes dirigidos contra o bruto, o oráculo, as rulings e a CR, cada um com controle de corte | **13/13** (`cmp`) |
| `orquestracao/confere_simulador.py` → `resumos/confere_simulador_ANTES_plaza.txt` / `..._DEPOIS_plaza.txt` | 6 conferências do simulador com as cláusulas da partida; roda na cópia arquivada ANTES da correção (5/6: falha a linha legal do T4) e no simulador vivo (6/6) | usado (`cmp`) |
| `codigo/mothman_goldfish_v1_ANTES_plaza_c59226f.py` | o simulador como estava (commit `c59226f`), com o qual a medição e a conferência ANTES foram feitas | snapshot |
| `orquestracao/medir_plaza.py` → `dados/medicao_plaza_ANTES_{padrao,resiliencia}_N10000.json` | quantas vezes o simulador joga OUTRO terreno quando a Plaza deixaria o comandante conjurável no turno (N = 10.000, sementes 1.000.000+i, `PYTHONHASHSEED=0`) | usado (`--tudo` re-executa o modo padrão) |
| `orquestracao/baixar_rulings.py`, `orquestracao/extrair_cr_trechos.py`, `orquestracao/extrair_json_da_conversa.py` | rulings ao vivo, trechos da CR, extração do JSON | apoio |
| `verificar_reproducao.sh`, `descomprimir.sh`, `SHA256SUMS` | refaz cada saída e compara com `cmp`; descomprime `dados/*.xz`; somas | ver abaixo |

Reproduz (qualquer pasta): `bash wise-mothman-sultai/resultados-ab/2026-11-11-partida-manual-3/verificar_reproducao.sh [--tudo]`.

## Resultado em 1 minuto
**Provado pelo log + oráculo (`resumos/checagens_preliminares.txt`, `resumos/testes_manual3.txt`), todos confirmados pelo usuário:**
1. **T4: The Wise Mothman (`{1}{B}{G}{U}`) conjurado sem {B}.** Os 4 terrenos virados só davam G e U; a **Plaza of Heroes** (qualquer cor para magia lendária) estava na mão e foi descartada pela Dark Deal. Resposta: *"Foi erro meu, era para eu ter jogado o plaza!"* A linha legal existia (Plaza como terreno do T4 paga o {B}).
2. **T4: Dark Deal** ("discards all the cards in their hand, then draws that many cards minus one"): 6 descartadas, 4 compradas (esperado 5). Resposta: *"Faltou, achei que só joguei 5 fora"*.
3. **Contadores do Mothman: erro de MÉTODO confirmado.** O usuário contou *"1 do rad do Mothman e 6 dos 3 oponentes milling pelo terreno e pelo Six"* e *"com o Altar na mesa, cada permanente que eu coloco na mesa são 3 mills (1 de cada oponente)"*: 3 gatilhos por permanente. **A ruling de 2024-03-08 diz 1** (mills simultâneos disparam o Mothman uma vez só). Os 7 cliques após a Six (todos no Mothman, de propósito) viram, pela regra, 2 gatilhos do Altar (Forest e Six). **Mas o total do log (8 ao fim do T5) fica dentro do teto de 10 gatilhos legítimos de T4+T5** (`resumos/ledger_contadores.md`), porque os gatilhos esquecidos do T4 (Altar na entrada do Mothman + rad dos 3 oponentes: **"1º, erro meu"**) e o rad dos oponentes cobrem a diferença: **não dá para dizer qual seria o valor certo** (depende de quantas cartas milladas eram não-terreno, e o log não mostra mill de oponente). O 8º contador do T5 ficou sem explicação (a conta do usuário fecha 7).
4. **T6: o mill do rad foi esquecido** (nenhum mill próprio no T6; no T5 há). Resposta: *"Esqueci sim"*.
5. **T6: Rejuvenating Springs** foi do cemitério direto ao campo: *"misclick, erro, era para ter ido para a mão"* (seria também o 2º terreno do turno). A Gyre Sage foi ao campo e depois à mão (arrastada e corrigida).
6. **T6: a Evolution Witness devolve "target permanent card" e o log leva à mão Didn't Say Please e An Offer You Can't Refuse (Instants).** Resposta: *"Erro meu ao trazer instants para a mão!"*; os contadores da Witness e da Six *"vieram do Mothman"* (e a Witness devolve uma carta *"para cada counter +1/+1"*: certo quando cada contador vem de um gatilho separado, que é o caso do log). **Contagem:** 6 cartas distintas saem do cemitério no T6 para 5 eventos de contador na Witness (**+1**, sem resposta).
7. **Fim:** *"Eu parei o goldfish aí!"* (T6, depois do ataque do Mothman).

**O simulador acerta 5 das 6 conferências** (`resumos/confere_simulador_ANTES_plaza.txt`): o Altar vale 1 gatilho por permanente e +1 no Mothman, o gatilho dá 1 contador em cada alvo, a Witness só devolve permanente, o retrace da Six exige um terreno na mão, o rad mila no início da fase principal 1. **A 6ª falhava: no T4 do log o simulador também joga um terreno G/U (Rejuvenating Springs) e não conjura o Mothman**, porque `land_play_score` dá −4 à Plaza e a trata como terreno incolor. **Medido (N = 10.000):** em **6,69%** das partidas do modo padrão e **7,01%** da resiliência, o simulador jogou outro terreno quando a Plaza deixaria o comandante conjurável no turno (669 e 701 partidas; 1.005 e 1.091 ocasiões, quase todas em T3 e T4). **Correção** (`PLAZA_ENABLES_COMMANDER`) e A/B em `../2026-11-11-plaza-comandante/`; com ela as 6 conferências passam (`resumos/confere_simulador_DEPOIS_plaza.txt`).

## O que o script prova e o que não prova
**Prova:** mana viável por turno (cores dos terrenos virados), compras e mills próprios por turno, terrenos por turno (objetos distintos), contadores postos, tipos das cartas devolvidas.
**Não prova:** vida, mill de oponente (o rad e o Altar dos oponentes), a ordem da pilha, o que sumiu sem registro (fichas), a intenção do usuário, e se cada mill de oponente tinha carta não-terreno (o teto do ledger supõe que sim).

## Respostas do usuário (2026-11-11), na ordem das dúvidas
1. T4 Mothman sem {B}: erro dele (devia ter jogado a Plaza). 2. T4 Dark Deal: achou que só descartou 5. 3. Contadores: T4 esquecido; os 7 no Mothman de propósito; método de 3 gatilhos por permanente (errado pela ruling). 4. T6 rad: esqueceu. 5. T6 Springs: misclick; Gyre Sage arrastada. 6. T6 Witness: instants foram erro; contadores vieram do Mothman. 7. Parou no T6.
**Não perguntei/ficou sem resposta:** quantas interações por rodada estavam configuradas (a Dark Deal é "sorcery" jogada no turno dele); de onde veio o 8º contador do T5; a 6ª devolução do T6.

## Verificação de reprodutibilidade
`bash verificar_reproducao.sh` (2026-11-11): ver o resultado no `goldfish-log.md` §25. **Não conferidos por `cmp`:** `resumos/rulings_scryfall.json` (API ao vivo), a extração do JSON da conversa (depende do registro da sessão) e, sem `--tudo`, a medição de 10.000 partidas (o modo resiliência não é re-executado).
