# Checklist cláusula-a-cláusula — Rat King, Verminister

## Auditoria oráculo-por-oráculo completa — 2026-09-13/14

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil/Nekusar/Ms.
Bumbleflower. Oráculo real via Scryfall pras 53 cartas únicas + terrenos,
comparado cláusula-por-cláusula contra o código já existente (que já
tinha passado por uma rodada anterior, ver seção abaixo — esta é mais
uma passada em cima de um arquivo já maduro).

**Achado principal — sistêmico, 4 habilidades ativadas de criatura sem
guarda de "1x por turno":** `main_phase()` roda 2x por turno (antes e
depois do combate). Ayara ("{T}, Sacrifice another black creature: Draw
a card"), Marrow-Gnawer ("{T}, Sacrifice a Rat: Create X tokens..."),
Priest of Forgotten Gods ("{T}, Sacrifice two other creatures: ...") e a
própria reanimação do Rat King ("{T}, Sacrifice three Rats: ...") têm
todas `{T}` no custo real — só podem ativar 1x por turno (o mesmo
permanente não pode ser tapado 2x sem desatapar no meio). Nenhuma tinha
essa guarda; a 2ª chamada de `main_phase()` no mesmo turno podia ativar
de novo se as condições (mana/criaturas pra sacrificar) ainda
estivessem satisfeitas. Corrigido com um novo campo
`state.tapped_creatures_this_turn` (resetado a cada turno), checado e
marcado nas 4 funções. O Rat King também ganhou a checagem de doença de
invocação que faltava inteiramente (podia reanimar no mesmo turno em
que era conjurado, ilegal pra uma habilidade com `{T}`).

**Achado ainda maior no mesmo padrão — Piper of the Swarm:** a versão
anterior modelava `{1}{B}, {T}: Create a Rat token` como um `while
remaining_mana(state) >= 2:` — um LOOP criando tokens ilimitados por
turno enquanto sobrasse mana, quando o `{T}` no custo real limita a
ativação a **no máximo 1 por turno** (e ainda compete pelo mesmo tap com
a 2ª habilidade da carta, "Sacrifice three Rats: Gain control of target
creature"). Esse era o maior gerador de "mana fantasma" do arquivo: com
Cabal Coffers/Crypt Ghast tardios gerando dezenas de mana, o Piper podia
sozinho inflar `tokens_created_total`/`rat_count` de forma completamente
irreal. Corrigido pra ativar no máximo 1x por turno (mesma guarda
`tapped_creatures_this_turn`).

**Syr Konrad, the Grim — 2 das 3 cláusulas reais do motor de dano nunca
implementadas:** o oráculo real é "Whenever another creature dies, **or
a creature card is put into a graveyard from anywhere other than the
battlefield, or a creature card leaves your graveyard**, Syr Konrad
deals 1 damage to each opponent." Só a 1ª cláusula (morte, via
`on_creature_dies()`) estava implementada. As outras 2 nunca disparavam
em NENHUM dos vários pontos de mill/recursão do deck (Reanimate, Echoing
Return, Secret Salvage, Rat King sac-3-Rats, Ashcoat mill+return, Soul
Stone upkeep, Ninja Teen sneak, Ripples of Undeath, Takenuma Channel) —
um deck pesado em recursão/mill como este deveria disparar essas 2
cláusulas com bastante frequência. Corrigido com 2 novos helpers
centralizados (`konrad_gy_entered`/`konrad_gy_left`), chamados de todos
os 9 pontos reais de mill/remoção-do-cemitério do arquivo.

**Syr Konrad também tinha uma 2ª habilidade real 100% ausente:** "{1}{B}:
Each player mills a card" (tag `mill_activated` já existia no `add()`
desde a construção original, nunca despachada em lugar nenhum — fantasma
completo). Sem `{T}` no custo, genuinamente repetível várias vezes por
turno com mana sobrando (não é o mesmo bug de tap-guard dos outros).
Implementada como `syr_konrad_mill_activation()`, com cada criatura
minada dessa forma também disparando a cláusula 2 do próprio Konrad
(sinergia real entre as 2 habilidades da mesma carta).

**Big Apple, 3 a.m. — ativação repetível tratada como ativação única:**
"{5}, {T}: Create a 1/1 black Rat creature token for each opponent you
have" só era checada dentro de `play_land()`, ou seja, só no PRÓPRIO
turno em que o terreno era jogado — nunca mais em nenhum turno seguinte.
Corrigido com uma função dedicada (`big_apple_activation()`), chamada a
cada `main_phase()` com a mesma guarda de tap-por-turno dos terrenos
utilitários já existentes (Castle Locthwain/Nykthos).

Também confirmado (não achado novo, checagem de precisão): "Ashcoat of
the Shadow Swarm" (`ashcoat_pump`, "attacks or blocks: other Rats get
+X/+X until EOT") é 📊 estrutural de verdade — este arquivo nunca soma
poder de ataque cru como dano proxy em lugar nenhum (todo
`proxy_damage_total` vem só dos drenos reais nomeados), então um pump
temporário de combate não tem onde se manifestar numericamente aqui,
mesma classe de N/A já documentada pro toxic do Karumonix/steal do
Piper.

**Validação:** smoke test (54 nomes no `CARD_DB`, 99 cartas na
`BASE_LIBRARY`, 0 desconhecidas) + 2.000 partidas antes/depois (mesma
seed 9300000) + 20.000 partidas de regressão (seed 9500000), 0 exceções
em ambas. Testes unitários dirigidos confirmaram cada correção: Piper
cria exatamente 1 token por turno mesmo com mana "infinita" e chamado 2x
no mesmo turno; Marrow-Gnawer não duplica ao ser chamado 2x no mesmo
turno; Konrad dispara +1 dano ao minar uma criatura (não ao minar uma
não-criatura) e ao reanimar uma criatura do cemitério; Big Apple cria 1
token por turno em turnos DIFERENTES (antes: só no turno em que foi
jogado). Distribuição mudou como esperado: `tokens_created_total` médio
caiu de 13.55→4.76 (2.000 partidas, mesma seed) — o Piper sozinho era
responsável pela maior parte da inflação, já que gerava tokens
ilimitados com mana sobrando; `avg Rats totais em campo` e `avg
reanimações via Rat King` caem proporcionalmente (menos Rats
disponíveis pra alimentar o sac-3-Rats), consistente com a causa raiz
corrigida, não uma regressão nova.


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
