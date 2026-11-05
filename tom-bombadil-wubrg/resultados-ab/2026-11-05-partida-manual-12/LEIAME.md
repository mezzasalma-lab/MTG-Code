# Tom Bombadil: partida manual #12 (2026-11-05): dados brutos, scripts, ledgers, testes e rulings

Arquivo da Regra #8 (`CLAUDE.md`). **Status: compilada com as respostas do usuário (2026-11-05)**; a análise em prosa e os pontos em aberto estão na seção "Partida manual #12" de `tom-bombadil-wubrg/goldfish-log.md`.
**10 turnos**, simulador de interação **On** (uma interação por rodada de T4 a T9), mulligan não informado, sem foto. O usuário parou no T10 "para não se alongar".

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do playtester do Archidekt que o usuário colou na conversa com *"MAIS UM GOLDFISH MANUAL DO TOM BOMBADIL ... ME PERGUNTE AS DUVIDAS"* (10 blocos de turno, 221 eventos), extraído por script da transcrição da sessão
  (`orquestracao/extrair_json_da_conversa.py`, sem redigitar). Conferido byte a byte contra o JSON extraído antes de apagar o `.json` solto. A mensagem inteira está em `dados/mensagem_usuario_original.txt.xz`.
- **Sem foto da mão inicial.** O usuário disse: *"são as cartas antes da primeira compra do jogo que estavam na mão"*. Leio as 7 primeiras entradas library→mão do T1 como a mão (Fertile Ground, Jugan, The First Iroan Games, Prismatic Omen, Enchantress's Presence, Forest, Ketria Triome) e a 8ª (In the Darkness Bind Them) como a compra do turno: **leitura minha pela ordem do log, não confirmada**.
- Oráculos: `scryfall-cache/oracle-cache.json` (as 29 cartas reais do log estavam lá). Consultados ao vivo no Scryfall nesta rodada: **Fold into Aether** (Fifth Dawn, {2}{U}{U}, "Counter target spell. If that spell is countered this way, its controller may put a creature card from their hand onto the battlefield"), a ficha **Walker** (Zombie 2/2, Secret Lair) e a ficha **Plant Warrior** (4/2 com alcance, Outlaws of Thunder Junction Commander). As duas fichas e as 4 interações são do oponente simulado.
- Rulings (Scryfall, ao vivo, 2026-11-05) de 29 cartas em `resumos/rulings_scryfall.json` (126 rulings, 0 erros de rede), **lidas antes de concluir**: Resurgent Belief (17), Kiora Bests the Sea God e The First Iroan Games (regras de Saga), Nesting Grounds, In the Darkness Bind Them (Anel), Tom Bombadil, Enchantress's Presence, Austere Command, Soul Shatter, Jugan, entre outras.
- Regras: **`rules-cache/comprehensive-rules.txt` (CR em vigor desde 2026-09-25), regra permanente §18**. Eu a baixei de novo de media.wizards.com antes de notar que já estava no repositório; é **idêntica byte a byte** (sha256 `8d860e45...70ca`) e por isso não foi duplicada aqui. Trechos citados: `resumos/cr_2026-09-25_trechos.txt` (714.2b, 714.3c, 714.4, 117.5, 603.2, 603.3, 603.3b, 307.5, 602.5d, 702.62a, 903.8, 701.54a, 701.54c, 302.6).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida #12 | usado |
| `dados/mensagem_usuario_original.txt.xz` | a mensagem do usuário, textual | bruto |
| `analisa_partida.py` | o script da #11 com **2 mudanças** (só nesta pasta): o MESMO objeto jogado 2× da mão no turno é desfazer/refazer, não 2 terrenos; fetchland parada no ÚLTIMO turno do log é nota, não violação | usado |
| `resumos/trace.md` | saída do script | usado (`cmp` conferido) |
| `ledger_compras.py` + `resumos/ledger_compras.md` | compras ESPERADO × LOG por turno (25 × 25) e a "linha legal" que o usuário não jogou; os eventos esperados são leitura minha (cabeçalho do script) | usado (`cmp` conferido) |
| `ledger_mana.py` + `resumos/ledger_mana.md` | mana disponível × custo por turno, lido à mão do log (fontes viradas); T8 fica **aberto** (7 de mana para 8 de gastos) | usado (`cmp` conferido) |
| `testes_manual12.py` + `resumos/testes_manual12.txt` | 17 testes dirigidos contra o bruto, o oráculo, as rulings e a CR, cada um com controle de corte | **17/17** |
| `resumos/estado_por_turno.txt` | estado ao fim de cada turno (por id, último registro) | apoio: **o log não registra ficha que some**, então este dump mostra 2 Krakens e Wraith/Soldier que a Austere matou (o usuário confirmou 1 Kraken) |
| `resumos/sequencia_bruta.txt` | os 221 eventos em ordem (zona, origem→destino, virada, marcadores) | apoio |
| `resumos/rulings_scryfall.json` | rulings ao vivo de 29 cartas | usado (**não** conferido por `cmp`: depende da API) |
| `resumos/cr_2026-09-25_trechos.txt` | trechos da CR do `rules-cache` | usado (`cmp` conferido) |
| `orquestracao/*.py` | extração do JSON da conversa, rulings, estado por turno, sequência bruta, trechos da CR | apoio |
| `verificar_reproducao.sh` | refaz cada saída de `resumos/` a partir dos `.xz`, compara com `cmp`, testa os `.xz` e confere o `SHA256SUMS` | ver abaixo |
| `descomprimir.sh`, `SHA256SUMS` | descomprime `dados/*.xz`; somas de verificação | — |

Reproduz (qualquer pasta): `bash tom-bombadil-wubrg/resultados-ab/2026-11-05-partida-manual-12/verificar_reproducao.sh`. Simulador (`tom_goldfish_v1.py`): **não alterado**. **Verificação de 2026-11-05: 11 conferências, 0 falhas** (2 `.xz` íntegros, 8 saídas de `resumos/` refeitas e iguais por `cmp`, `SHA256SUMS` confere). **Não conferidos por `cmp`**: `resumos/rulings_scryfall.json` (vem da API ao vivo) e as leituras minhas dos ledgers (os eventos esperados são suposição declarada no cabeçalho de cada script).

## O que o script prova e o que não prova
Prova só o que o log permite: 1 terreno por objeto por turno (o mesmo id repetido é desfazer), fetch, marcadores de saber por objeto-Saga, 1 gatilho do Tom por turno, compras library→mão. Resultado: **0 violações provadas** e **1 anomalia sem fonte** (Iroan Lore 2→3 no T7, depois de o Tom sair; ver o goldfish-log).
**Não verificado** (nenhum script do log prova): cor da mana (só o total por turno), ordem da pilha, pontos de vida, ataque (assumi "virado = atacou"), o que sumiu sem registro (fichas), a intenção do usuário, e a escolha de Ring-bearer a cada gatilho do Anel.

## Respostas do usuário (2026-11-05), na ordem das dúvidas
1. **Imposto do Tom (T8):** pagou 7 mana; a Fertile Ground estava na **Floresta** (rende 2). O `commandTax` do log ficou 0 (não contou no contador). A conta por terreno do log não fecha por 1 mana (T8, aberto).
2. **Nesting Grounds (T8):** o usuário pensava que podia ir ao Lore 4 e tirar o marcador antes do sacrifício, e admitiu *"errei ao usar como instant, o efeito é sorcery speed"*. Regra conferida ao lado (CR 714.4, 602.5d, 307.5, rulings da Kiora e da Iroan).
3. **Resurgent Belief (T9):** (a) esquecimento (devia sair no upkeep). Ele perguntou se não pode ordenar os gatilhos porque os Sagas ganham o 2º marcador no mesmo turno em que entram: **gatilhos que disparam juntos têm ordem livre (CR 603.3b; ruling da Kiora), mas o marcador natural não é gatilho, é ação de turno do início da fase principal 1 (CR 714.3c), depois do upkeep e da compra**, e o suspend não pode ser adiado (se não conjurar quando o último contador sai, a carta fica exilada sem contadores: ruling 2024-02-02, CR 702.62a). Mesmo engano já registrado na #11, item 2. (b) A Kiora foi conjurada **antes** da Resurgent, ele **voltou atrás e a conjurou depois**: **1 Kraken** (a ficha do 1º cast sumiu sem registro no log).
4. **T10:** esqueceu os marcadores e efeitos. O log mostra os efeitos do cap. II de Iroan, Jugan e ITDBT aplicados (Wraith; Tom +4 e Kraken +1 em contadores +1/+1) sem nenhum clique de saber; **quais "efeitos" faltaram além disso não foi dito** (minha leitura: o Anel e a Kiora II; não confirmada).
5. **T7:** (a) o Soldier do T7 é o cap. I da Iroan, esquecido no T6; (b) a Iroan morreu na Austere Command (isso responde a parte do T8; o 3º marcador do T7 depois da Soul Shatter **não foi explicado**); (c) errou o enjoo de invocação do Soldier e esqueceu o compre-descarte do Anel.
6. **T6:** a Jugan foi **anulada** pela carta do gerador de interação (Fold into Aether); a Presence comprou mesmo assim (ruling 2021-06-18; o log tem a Plains logo depois).
7. **T8/T9:** a Fertile Ground foi destruída pela Austere no T8; o lembrete da interação estava em cima da carta e ele só pôde movê-la no T9. O 2º modo da Austere: "eliminar criaturas com menos de 3" (**o oráculo diz "mana value 3 or less", ou seja, 3 ou menos; as fichas têm MV 0**).
8. **Gerador de interação:** a resposta 6 cobre a Fold into Aether (**minha leitura, não dita por ele**: a Fold aparece no log no fim do T5 e vale na 1ª magia do T6). Quantas por rodada e o que Walker e Plant Warrior fizeram: **sem resposta** (o log mostra 1 por rodada de T4 a T9).
9. **Fim:** parou no T10 para não se alongar (a Verdant Catacombs ficou sem ser acionada).
10. **Foto:** esqueceu; ver o item de mão inicial acima.

## Em aberto (sem resposta do usuário)
Iroan Lore 2→3 no T7 depois da Soul Shatter; o 1 mana a mais do T8; quais efeitos além dos marcadores foram esquecidos no T10; quantas interações por rodada estavam configuradas e o destino de Walker e Plant Warrior; mulligan e mão inicial (sem foto); por que o Soldier foi virado no T7 (ele respondeu o enjoo, não o motivo); intenção das cartas que ficaram na mão (Ripples of Potential, The Coming of Galactus, Estrid's Invocation, Elspeth Conquers Death).
