# Varredura transversal de 2026-10-05 — scripts e resultados

Pedido do usuário (2026-10-05): *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*.
Esta pasta guarda as **varreduras mecânicas** (script + saída) que sustentam os achados que não são "de uma carta" e por isso nenhuma auditoria carta-a-carta pega. As correções de cada deck estão em
`<deck>/resultados-ab/2026-10-05-*/` (cada uma com `LEIAME.md`, dados brutos, A/B e reprodução) e nas seções de 2026-10-05 do `goldfish-log.md`/`checklist-oraculo.md` do deck.

## O que cada varredura mede (e o que NÃO mede)

| script | pergunta | método | saída (`resumos/`) | limite |
|---|---|---|---|---|
| `det_test.py` / `det_all.sh` | a mesma semente dá o mesmo resultado em processos diferentes? | 2 `PYTHONHASHSEED` (1, 2) × 200 sementes × 2 modos, impressão digital do resultado inteiro | `determinismo_200_sementes_ANTES.txt` (árvore `HEAD` de antes das correções) | só 200 sementes: pega divergência frequente |
| `det_fields.py` / `det_check.sh` / `det_wide.sh` | idem, em escala e **campo a campo** | 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos nos 18 simuladores | `determinismo_1500_sementes_estado_final.txt` (estado final, com as correções) | só compara o estado FINAL; divergência rara demais (≪ 1/1.500) pode escapar |
| `det_controle.sh` | a correção de determinismo resolve? | controle (chave desligada) × correção, mesmas sementes | `determinismo_<deck>.txt` (Hei Bai, Thranduil, Bumbleflower, Edgar) | — |
| `ast_sets.py` | onde o código itera `set`/`frozenset` de forma que a ordem decide algo? | AST: `for`/compreensão/`list()`/`next(iter())`/`pop()` sobre `set`, nos 18 `*_goldfish_v1.py` | `ast_sets_ANTES.txt` | heurística: marca candidatos, não prova que a ordem importe; cada item foi lido |
| `audit_entrada.py` | o terreno entra virado quando o oráculo manda? | T1, campo vazio, mão `[terreno]`, delta de `total_mana` do simulador × texto do oráculo em cache | `audit_entrada_ANTES.txt` | só campo vazio; só decks com `total_mana`; filtros (Cabal Coffers, filter lands, fetch) dão falso positivo, listados abaixo |
| `audit_entrada2.py` | condição satisfeita × violada | padrões "unless you control a/an X or Y", "two or more/fewer other lands", "two or more basic lands", "a basic land", "reveal a/an X card" | `audit_entrada2_ANTES.txt` | terrenos cujos básicos/duais necessários não existem no `CARD_DB` do deck foram **pulados** (coluna `pulados`) |
| `audit_fetch.py` | a fetch é sacrificada, busca de verdade e paga a vida? | T1, mão `[fetch]`, estado antes/depois | `audit_fetch_ANTES.txt` | só `play_land`; Grixis Panorama/Fabled Passage/Windswept Heath (Kutzil) quebram por rotina própria (`try_*`) e aparecem "em campo" no T1 — não é erro |
| `audit_terreno_nao_e_magia.py` | jogar terreno mexe em contador de magia/storm? | `play_land` com terreno comum, compara atributos `spell|cast|storm` | `audit_terreno_nao_e_magia_ANTES.txt` | só o caminho `play_land` com terreno comum |

`ANTES` = executado sobre `git archive HEAD` de `4fcf97c` (estado anterior a esta rodada), pelo argumento `ROOT=`. Os scripts importam `abgen.py` desta pasta; os `det_*.sh` usam `/tmp` para saídas intermediárias.

## Achados (todos conferidos à mão no código antes de corrigir)

| classe | decks | medido |
|---|---|---|
| ordem de `set` decide o jogo (varia com `PYTHONHASHSEED`) | Thranduil (efeito de jogo), Hei Bai (só a ordem de `battlefield`) | Thranduil 14/1.500 (padrão) e 36/1.500 (resiliência) sementes mudam de resultado entre processos; Hei Bai 4/1.500 e 1/1.500 (só ordem). Tom: só o campo interno `_mana_cache` (sem efeito de jogo). |
| terreno entra desvirado contra o oráculo | Maralen (5: Drowned Catacomb, Hinterland Harbor, Woodland Cemetery, Sunken Hollow, Gilt-Leaf Palace), Ulalek (Ruins of Oran-Rief), Captain Storm (Izzet Boilerworks) | `audit_entrada_ANTES.txt`, `audit_entrada2_ANTES.txt` |
| jogar terreno contado como magia; storm do Brain Freeze contando a si mesma | Nekusar | Brain Freeze como 1ª magia: mill 18 em vez de 9; com 1 terreno antes: 27 em vez de 9 |
| fetchland deixada em campo como dual (sem busca/sacrifício/vida) | Hei Bai (8), Nekusar (9, só paga a vida), Edgar (3) | `audit_fetch_ANTES.txt` |

Falsos positivos da varredura de entrada (verificados): Blackcleave Cliffs, Botanical Sanctum, Seachrome Coast (fastlands: com campo vazio **entram desvirados** — "unless you control two or fewer other lands"); Cabal Coffers, Desolate Mire,
Shadowblood Ridge, Overflowing Basin/Skycloud Expanse/Sungrass Prairie, Serra's Sanctum (não produzem mana sozinhos com campo vazio: delta 0 por outro motivo); Evolving Wilds/Terramorphic Expanse/Rocky Tar Pit (fetch tapped, já
modeladas no Megatron); os 10 choques do Prismatic Bridge (política deliberada `_shock_pays_life`: paga 2 de vida só se a mana muda o que dá pra conjurar).

## Escopo (Regra #7)

**Varrido:** as 5 classes acima, nos 18 simuladores (Vihaan e Megatron incluídos como controle: 0 achado novo).
**NÃO varrido:** caminhos de conjuração fora da mão e "whenever you cast"; sacrifício × destroy; contadores `_sick` agregados; fórmulas dinâmicas achatadas — triados por `grep`/leitura pontual, sem instrumentação em runtime.
Entrada de terrenos: não coberta a **combinação** de condições (p.ex. checkland com o tipo vindo de um terreno que entra no mesmo turno), nem terrenos cujos básicos necessários não estão no `CARD_DB` do deck.
**Pendência registrada (não corrigida):** o `do_cascade` do Ulalek devolve os exilados ao fundo na mesma ordem (oráculo: ordem aleatória); o estado desse simulador não tem RNG e o efeito só existe perto de esgotar o grimório. A convenção "choque sempre paga 2 de vida": verifiquei que Ur-Dragon, Nekusar, Tom e Prismatic Bridge deduzem a vida; nos demais decks com choque a dedução não foi verificada (não corrigido).

Nota sobre a saída `determinismo_1500_sementes_estado_final.txt`: duas linhas de erro de shell no meio (`det_check.sh: line 25`) vieram de eu ter editado o script enquanto ele rodava (o Toph terminou antes do erro e tem as duas linhas de resultado); nenhum resultado foi perdido.
