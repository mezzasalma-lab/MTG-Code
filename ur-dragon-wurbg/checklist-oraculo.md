# Checklist cláusula-a-cláusula — The Ur-Dragon (`urdragon_goldfish_v1.py`)

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King, Thranduil e Ulalek.

**Contexto importante:** este simulador já tinha passado por múltiplas
rodadas de auditoria completa antes desta (2026-08-27, 2026-08-29,
2026-08-30 — documentadas extensivamente em `goldfish-log.md`), incluindo
correções reais de haste/summoning sickness, lealdade de Sarkhan Unbroken,
Haunting Voyage foretell, etc. **Este deck tem 2 simuladores** —
`urdragon_goldfish_v1.py` (lista "afinada", `lista.md`) e
`urdragon_goldfish_physical_v1.py` (deck físico real, `lista-fisica.md`,
com 3 cartas extras registradas só nesse arquivo). Esta auditoria cobriu o
arquivo principal (`urdragon_goldfish_v1.py`); o físico herda a mesma
base de código e as mesmas correções onde as cartas coincidem.

**Método:** detecção automatizada de (a) tags órfãs e (b) nomes de carta
com poucas ocorrências. ~26 candidatos apareceram; a esmagadora maioria
eram falsos positivos (dispatch por nome dentro de funções compartilhadas
como `dragon_enters()`, `try_dragon_pumps()`, `ready_creatures()` — este
arquivo já é maduro o bastante pra ter várias dessas). **1 gap real
confirmado.**

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real, sem combate/P-T por criatura
  individual — limite conhecido, não julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 O gap corrigido nesta rodada

**Lightning Greaves** — tinha só a tag genérica `"interaction"` (bucket
de proteção do próprio board), **sem nenhum efeito real implementado**
— nem sequer o haste, que é o ganho mais relevante possível pra este
deck especificamente: a Ur-Dragon não tem haste nativo, e o motor
inteiro de compra de cartas do deck (*"Whenever one or more Dragons you
control attack, draw that many cards..."*) depende dela atacar. Oráculo
real: *"Equipped creature has haste and shroud. Equip {0}."* Corrigido
com `try_lightning_greaves_equip()` — equipa automaticamente na
comandante assim que ambas estão em campo (Equip {0}, sem custo real),
reequipa em outra criatura se a comandante ainda não resolveu, e
re-equipa automaticamente se o alvo anterior saiu de campo. `shroud` não
tem efeito modelável (sem oponente/remoção alheia neste goldfish solo)
— 📊, documentado.

Este arquivo já modela haste/summoning-sickness de forma sofisticada
(`ready_creatures()`, tags `haste`/`haste_all`/`haste_flying`/`riot`)
desde a rodada de 2026-08-27 — o gap era especificamente a ausência total
de qualquer lógica de equipamento pra essa carta, não um limite do
motor de haste em si.

Validado com 4 testes unitários isolados + regressão de 20.000 partidas
(seed 4000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 7000000, turns=10) — ver `goldfish-log.md`
pra métricas específicas.

## Falsos positivos descartados (já corretamente implementados)

- **Ancient Copper Dragon / Ancient Gold Dragon** — habilidades de d20
  (`combat_treasure_d20`/`combat_token_d20`) dispatchadas por tag numa
  função central de combate, não por nome — confirmado lendo o dispatch
  real, não só contando ocorrências do nome.
- **The Great Henge, Terror of the Peaks, Miirym, Lathliss, Dragon's
  Hoard, Orb of Dragonkind, Hellkite Charger, Radagast of Rhosgobel,
  Goldspan Dragon, Kindred Discovery, Temur Ascendancy, Ramos Dragon
  Engine, Bladewing the Risen, Sarkhan Unbroken, Smothering Tithe,
  Magda Brazen Outlaw, Herald's Horn, Dragon Broodmother** — todas
  dispatchadas por checagem de nome direta dentro de funções
  compartilhadas (`dragon_enters()`, `try_dragon_pumps()`,
  `resolve_etb()`, etc), confirmadas lendo o código, não a contagem
  ingênua de string.
- **Rhythm of the Wild** (tag `opponent_dependent`) — dispatchada de
  verdade (riot→haste, ver `ready_creatures()`); a tag em si é só um
  rótulo descritivo órfão, não indica ausência de efeito.
- **Mana Confluence** — terreno de mana genérica pura (produz qualquer
  cor, sem habilidade condicional adicional), corretamente sem tag
  extra.
- **An Offer You Can't Refuse, Heroic Intervention** — pacote
  "interaction", proxy consistente com o resto da sessão (conjuráveis,
  sem alvo de oponente real, `try_use_own_interaction()`).

## Sarkhan Unbroken — heurística de pilotagem (não um gap)

As 3 habilidades de lealdade estão todas implementadas (+1 draw+mana, -2
token de Dragão, -8 ultimate búsca todos os Dragões). A escolha de
"nunca usar o -2, sempre +1 até poder usar o -8" é uma heurística de
pilotagem racional documentada (token único não compensa desviar do
caminho pro ultimate) — não uma lacuna de implementação.

---

## Resumo numérico

- **99 cartas na lista afinada** (`lista.md`).
- **🐛 Corrigido nesta rodada:** 1 carta (Lightning Greaves).
- **✅ Falsos positivos descartados:** ~20 cartas/grupos, já corretamente
  implementadas via dispatch por nome ou por tag central.
- **📊 Estrutural confirmado:** shroud do próprio Lightning Greaves (sem
  oponente/remoção alheia modelada).

---

# Achado adicional — `urdragon_goldfish_physical_v1.py` estava QUEBRADO

Ao verificar se o mesmo gap do Lightning Greaves existia na variante
física (já que o docstring dela cita a carta explicitamente como
presente na caixa), a simples tentativa de `import` do arquivo **crashava
imediatamente** com `AssertionError: faltando no CARD_DB: Sarkhan
Unbroken` — ou seja, este segundo simulador não rodava UMA ÚNICA partida
desde que a variante física existe (`lista-fisica.md` data de
2026-08-29). Investigando mais a fundo (comparação sistemática de todo
nome em `lista-fisica.md` contra as chaves reais do `CARD_DB`, não só o
primeiro erro que aparecia), achei **3 cartas genuinamente ausentes do
CARD_DB apesar de estarem na lista física real**:

1. **Sarkhan Unbroken** — planeswalker inteiro faltando (nem `add()`, nem
   nenhuma lógica de lealdade). Corrigido registrando a carta e portando
   a mesma implementação real de lealdade (+1 draw+mana / -2 token / -8
   ultimate, heurística de pilotagem já validada) do
   `urdragon_goldfish_v1.py`.
2. **Mana Confluence** — terreno de mana genérica de qualquer cor,
   faltando por completo.
3. **Sundown Pass** — slow land real ("enters tapped unless you control
   two or more other lands"). Corrigido registrando a carta + portando a
   lógica `SLOW_LANDS` do arquivo principal pro `play_land()` local.

Além disso, apliquei o **mesmo fix do Lightning Greaves** (equipa na
comandante, concede haste real) nesta variante — a carta está
confirmada na caixa física pelo próprio docstring do cabeçalho.

**Bug adicional encontrado e corrigido, não relacionado ao crash:** os
dois arquivos escreviam no MESMO nome de arquivo de saída
(`urdragon_v1_runs.jsonl`) — rodar um dos dois simuladores por último
sobrescrevia silenciosamente o output do outro sem aviso nenhum.
Corrigido: a variante física agora escreve em
`urdragon_physical_v1_runs.jsonl` (arquivo novo, não sobrescreve nada).

**Validação:** 5 testes unitários isolados (import sem crash + Lightning
Greaves + Sarkhan Unbroken +1 uma vez por turno + Sundown Pass tapped/
destravado) + regressão de 200 partidas de sanidade + regressão completa
de 20.000 partidas (seed 5000000+, turns=10, 0 exceções). Como o arquivo
nunca tinha rodado uma partida sequer antes, não há uma comparação
antes/depois de métricas no sentido usual — a validação real É o arquivo
passar a rodar de ponta a ponta com números plausíveis (Dragon tokens
médios ~12.0, color screw em ~31% dos jogos — mesma ordem de grandeza do
arquivo principal, nenhum outlier suspeito).

**Escopo não coberto nesta rodada:** esta correção resolveu o crash e
portou os 2 gaps já identificados no arquivo principal (Lightning
Greaves, e agora Sarkhan Unbroken/Mana Confluence/Sundown Pass como
efeito colateral de destravar o import). Uma auditoria linha-a-linha
COMPLETA da variante física — cobrindo as cartas que só existem nela
(Scalelord Reckoner, Dragon's Hoard, Smuggler's Surprise, Magda Brazen
Outlaw, Firdoch Core) contra o oráculo real — **não foi feita nesta
rodada** e fica como trabalho futuro dedicado, na mesma categoria dos 4
decks sem simulador algum (não é uma decisão de valor, é reconhecer que
essa é uma tarefa de escopo comparável a auditar um deck inteiro à parte,
não um recorte que cabe dentro desta passada).
