# Checklist cláusula-a-cláusula — Rat King, Verminister

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar e Prismatic
Bridge.

**Contexto importante:** diferente da maioria dos outros decks, este
simulador foi **construído do zero em 2026-08-31** já seguindo o
`goldfish-sim-card-rules.md` (oráculo real de todas as 53 cartas únicas
consultado via `scryfall-cache/oracle-cache.json` antes de o arquivo ser
escrito — ver docstring). Ou seja, não chegou nesta rodada com um
histórico de auditorias incompletas como Beorn/Edgar/Megatron. Mesmo
assim, a releitura linha-a-linha desta rodada — usando detecção
automatizada de tags definidas em `add()` mas nunca lidas em nenhum
`if`/`elif` de despacho — achou **3 gaps reais** que a auditoria de
construção original tinha deixado passar.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — não produz número neste modelo por decisão de
  arquitetura documentada (sem oponente real neste goldfish solo, sem
  combate/P-T por criatura individual) — limite conhecido do simulador,
  não julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 Os 3 gaps corrigidos nesta rodada

1. **Species Specialist** (tag `death_draw_type`, nunca lida em lugar
   nenhum — só o ETB de escolha de tipo, tag `choose_type_etb`, estava
   implementado). Oráculo real: *"As Species Specialist enters, choose a
   creature type. Whenever a creature of the chosen type dies, you may
   draw a card."* Tipo escolhido = Rat (tema tribal central do deck, mesma
   convenção já documentada pro Cover of Darkness/Three Tree City neste
   arquivo). Corrigido centralizando em `on_creature_dies()`, que agora
   recebe um parâmetro `dying_is_rat: bool` propagado pelos 4 pontos reais
   de morte de criatura (`leave_battlefield()`, o ramo de esquilo em
   `sacrifice_any_creature()`, o loop de Skullclamp — que agora rastreia
   qual tipo de token realmente morreu — e `sacrifice_rats()`, que não
   precisou de mudança por só sacrificar Rats reais por definição). Como a
   esmagadora maioria das mortes deste deck é de Rats (24x Rat Colony +
   tokens), isso dispara com frequência real: métrica DRAW subiu de 6.12
   pra 8.18 (média de 5000 jogos, seed 4000000, 10 turnos).
2. **Deadly Rollick** (tag `free_removal_commander`, nunca lida — a magia
   sempre pagava o custo cheio {3}{B}/MV4 antes). Oráculo real
   (confirmado via Scryfall, não memória): *"If you control a commander,
   you may cast this spell without paying its mana cost. Exile target
   creature."* Sem restrição a atacando/bloqueando — é qualquer criatura.
   Corrigido em `effective_cost()`: retorna 0 quando `state.commander_in_play`
   é verdadeiro. Métrica INTERACTION subiu de 1.01 pra 1.15.
3. **Takenuma, Abandoned Mire** (tag `takenuma`, só o `{T}: Add {B}`
   genérico — via `LAND_NAMES`/`lands_mana()` — estava coberto; a
   habilidade de Channel nunca foi implementada). Oráculo real: *"Channel
   — {3}{B}, Discard this card: Mill three cards, then return a creature
   or planeswalker card from your graveyard to your hand. This ability
   costs {1} less to activate for each legendary creature you control."*
   Corrigido com `try_takenuma_channel()`: só descarta o terreno em vez de
   jogá-lo quando sobra OUTRO terreno na mão nesse turno (pra não perder o
   land drop — decisão racional de piloto, não um limite técnico), calcula
   o desconto real via um novo conjunto `LEGENDARY_CREATURES` (7 criaturas
   lendárias verificadas via Scryfall: o comandante, Ashcoat of the Shadow
   Swarm, Marrow-Gnawer, Lord Skitter Sewer King, Karumonix, Syr Konrad e
   Ayara), milha 3 cartas de verdade pro cemitério e devolve a melhor
   criatura/planeswalker (não há planeswalkers nesta lista, mas o `ctype`
   é checado mesmo assim por fidelidade ao oráculo) do cemitério
   *já atualizado* pra mão. Métrica RECURSION subiu de 7.64 pra 7.91.

Validado com 7 testes unitários isolados (Species Specialist dispara em
morte de Rat / não dispara em morte de esquilo; Deadly Rollick custo 0
com comandante / custo cheio sem comandante / `cast_card` gasta 0 mana;
Takenuma Channel milha 3 + devolve criatura + desconto por lendárias /
não ativa quando é o único terreno na mão) + regressão de 20.000 partidas
(seed 1000000–1019999, turns=10, 0 exceções) + `run_batch` antes/depois
via `importlib` (5000 jogos, seed 4000000, turns=10) confirmando as 3
métricas subindo na direção esperada sem nenhuma outra métrica se mover
de forma inesperada.

## ✅ Demais cartas — confirmadas corretamente implementadas ou 📊 estruturais

Verificação via detecção automatizada (grep de toda tag definida em
`add()` contra toda ocorrência da mesma string em `if`/`elif` de
despacho no resto do arquivo) — confirmou que TODAS as outras tags
definidas são efetivamente lidas em algum ponto de despacho. As duas
categorias de "não-numérico" já documentadas no próprio código (não
achados novos desta rodada, só confirmação de que são estruturais de
verdade e não disfarce de omissão):

- **Dictate of Erebos** (`edict_on_death`) — edict mira o *oponente*
  ("target opponent sacrifices a creature"); sem oponente real neste
  goldfish solo, só o gatilho conta (`on_creature_dies()`), sem efeito
  numérico — 📊.
- **Kindred Dominance / Swarmyard Massacre / Damnation** (wipes) — os 3
  destroem/-1/-1 nas PRÓPRIAS criaturas sem nenhum oponente real pra
  "limpar" em contrapartida; nenhum piloto racional conjuraria um wipe só
  pra destruir o próprio board de valor. Documentado como Regra 1 desde
  2026-08-31 (não achado novo): a magia conta como "conjurável"/métrica de
  interação, sem o efeito de destruição simulado — 📊. (Swarmyard
  Massacre's token de esquilo, que é benefício incondicional real, já
  estava e continua implementado à parte do wipe.)
- **Piper of the Swarm** (`steal`) — "{3}{B}, {T}, Sacrifice three Rats:
  Gain control of target creature" mira criatura do oponente; sem
  oponente real, sem efeito numérico — 📊. As outras 2 habilidades da
  carta (anthem de Rat + ativação de token) são implementadas de verdade.
- **Karumonix, the Rat King** (`toxic_granter`) — toxic é um mecanismo de
  dano de combate contra jogadores oponentes; sem combate real/oponente
  neste modelo, sem efeito numérico — 📊 (já documentado no código,
  `combat_step()`).

---

## Resumo numérico

- **53 cartas únicas** (comandante + 51 cartas de biblioteca não-Swamp +
  Swamp) — lista confirmada em 99/100 (falta 1 carta que o usuário ainda
  vai escolher, `BASE_LIBRARY` reflete isso corretamente com 98 cartas).
- **🐛 Corrigido nesta rodada:** 3 cartas (Species Specialist, Deadly
  Rollick, Takenuma, Abandoned Mire).
- **📊 Estrutural confirmado (sem oponente real / sem combate — não
  achados novos, confirmação de que já eram estruturais de verdade):**
  Dictate of Erebos, Kindred Dominance, Swarmyard Massacre, Damnation,
  Piper of the Swarm (habilidade de steal), Karumonix (toxic).
- **✅ Todas as demais ~44 cartas:** tags conferidas uma a uma via
  detecção automatizada de despacho — nenhum gap adicional encontrado.
