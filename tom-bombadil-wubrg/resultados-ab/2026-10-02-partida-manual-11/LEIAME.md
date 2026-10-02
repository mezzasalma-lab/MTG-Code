# Tom Bombadil — partida manual #11 (2026-10-02): dados brutos, scripts, ledger e rulings

Arquivo da Regra #8 (`CLAUDE.md`). **Status: dados e análise arquivados; aguardando as respostas do usuário** (as dúvidas estão na seção "Partida manual #11" de `tom-bombadil-wubrg/goldfish-log.md`).
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
| `ledger_compras.py` | conta ESPERADO × LOG das compras (library→mão) e das fichas da Historian's Boon; os eventos por turno são leitura minha do trace (suposições no cabeçalho do script) | usado |
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
