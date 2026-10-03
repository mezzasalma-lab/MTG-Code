# Tom Bombadil — partida manual #11 (2026-10-02): dados brutos, scripts, ledger e rulings

Arquivo da Regra #8 (`CLAUDE.md`). **Status: concluída com as respostas do usuário (2026-10-03)**; a análise em prosa e os pontos ainda em aberto estão na seção "Partida manual #11" de `tom-bombadil-wubrg/goldfish-log.md`.
É a partida mais longa até agora (**19 turnos**), feita pelo usuário "para testar a resiliência do deck": 16 interações simuladas do oponente (Edict, Martial Coup, Bane of Progress, All Is Dust, Soul Shatter ×2, Casualties of War etc.).

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do Archidekt playtester que o usuário colou na conversa (19 elementos = 19 turnos), extraído por script do registro da conversa
  (`orquestracao/extrair_json_da_conversa.py`, sem redigitar) e conferido `==` com o texto extraído (ver abaixo).
- Foto da mão inicial (mulligan 0, simulador de interação **On**): Raugrin Triome, Windswept Heath, The Eldest Reborn, In the Darkness Bind Them, Jugan Defends the Temple, Fertile Ground, Ketria Triome (7 cartas, keep);
  a 8ª carta do T1 (O'aka, Traveling Merchant) é a compra do turno (Commander multiplayer: ninguém pula a 1ª compra).
- Oráculo: `scryfall-cache/oracle-cache.json` (ao vivo). Adicionados nesta rodada: Blasphemous Edict, No Mercy e a ficha Angel 4/4 (voar, vigilância: a da Historian's Boon).
  Fichas do oponente simulado (Squid, Beast, Kraken e o Angel do T7) não têm variante identificável no log e não foram cacheadas.
- Rulings (Scryfall, ao vivo) de 36 cartas em `resumos/rulings_scryfall.json` (lidas antes de concluir): Tom Bombadil, Narci, Starfield of Nyx, Resurgent Belief, Nexus Mentality, Blasphemous Edict, All Is Dust, Soul Shatter, Bane of Progress, Sagas (regra 714.3b), entre outras.

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida #11 | usado |
| `analisa_partida.py` | o script das partidas #6–#10 com **1 mudança** (só nesta pasta): `FETCH` exclui cartas com "God card" (The World Tree se sacrifica mas busca Deuses; no #10 o script antigo a marcava como fetchland falso) | usado |
| `resumos/trace.md` | saída do script | usado (`cmp` conferido) |
| `ledger_compras.py` | conta ESPERADO × LOG das compras (library→mão) e das fichas da Historian's Boon; os eventos por turno são leitura minha do trace (suposições no cabeçalho do script). Atualizado em 2026-10-03 com as respostas (T14: Eldest salva, não conta a Narci dela; T18: 14 compras sem base) | usado |
| `resumos/ledger_compras.md` | saída do ledger | usado (`cmp` conferido) |
| `resumos/saber_por_saga.txt` | linha do tempo de marcadores de saber por objeto-Saga (id fixo) | usado |
| `resumos/estado_por_turno.txt` | estado do campo/cemitério/mão/zona de comando ao fim de cada turno (por id, último registro) | apoio (ids de fichas que sumiram ficam "vivos" no dump: o log não registra fichas que somem) |
| `resumos/rulings_scryfall.json` | rulings ao vivo de 36 cartas | usado (não conferido por `cmp`: depende da API) |
| `orquestracao/*.py` | extração do JSON da conversa, download de rulings, estado por turno, sequência bruta (com marcadores e virada) | apoio |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |

Reproduz (a partir da raiz do repositório): `bash tom-bombadil-wubrg/resultados-ab/2026-10-02-partida-manual-11/descomprimir.sh`;
`python3 .../analisa_partida.py .../dados/partida.json.xz > /tmp/trace11.md` (= `resumos/trace.md`); `python3 .../ledger_compras.py > /tmp/ledger11.md` (= `resumos/ledger_compras.md`).
Simulador (`tom_goldfish_v1.py`): não alterado. (O `upkeep_step` do simulador faz a Starfield **antes** do passo de marcadores da fase principal, como manda a regra 714.3b.)

## O que o script prova e o que não prova
O script lista, por turno, mudanças de zona e fichas e verifica: 1 terreno da mão por turno, fetchland sem busca, marcadores de saber por objeto-Saga e o limite de 1 gatilho do Tom por turno.
Das 2 "violações provadas" que sobram na saída: **T18 (2 terrenos da mão)** é um achado real a perguntar; **T14 (Verdant Catacombs "sem busca")** é falso positivo (o terreno ficou em campo, virado para mana pela The World Tree, que dá "qualquer cor" a todos os terrenos com 6+ terrenos; a Island do T14 veio do capítulo I da Summon: Fenrir).
**Não verificado** (nenhum script do log prova): cor de mana (conferi só o total por turno), ordem da pilha, alvos dos capítulos I que miram o oponente, pontos de vida (Narci, Sythis, Cruelty II, City of Brass, shocklands), efeitos do oponente além do que o log mostra,
ataque do Ring-bearer (assumi "virado = atacou") e o que o oponente simulado fez com as fichas Squid/Beast/Kraken.

## Respostas do usuário (2026-10-03) e efeito nos arquivos
Eldest Reborn T14 salva 3→2 (fonte compatível: Power Conduit); T11 sem fonte de remoção em campo (aberto). Starfield × marcador natural: o marcador natural é ação da fase principal 1, não gatilho de upkeep (a ordem livre vale entre gatilhos próprios).
Gatilho do Tom no T12, loot do Anel (T10–T17), Mountain do There and Back Again II (T14), +1/+1 do Scholar e terrenos de T8/T12: esquecidos. Narci compra ao sacrificar encantamento (o usuário não sabia).
**T18: 14 compras vieram de Sythis lida como "encantamento entra" (ela dispara ao conjurar); Scholar, Serra's Sanctum, Teferi's Protection e o descarte a 7 vêm delas e são inválidos.** Boon: Soldier 1/1 e ela conta; Knights do T13/T14 e 14 fichas (eram 16) no T18 foram erro.
Soul Shatter T13: com a Starfield e 9 encantamentos, a Eldest era criatura (MV 5, empatada com o Tom). `resumos/ledger_compras.md` regenerado (`cmp` conferido com o script); `resumos/trace.md` não mudou.
Confirmado em 2026-10-03: o usuário achava que os marcadores de saber aumentam no upkeep e esqueceu que a Starfield torna os encantamentos criaturas. O mesmo engano do upkeep aparece nas partidas #8 e #10 (nota em `goldfish-log.md` e no LEIAME da #10).
