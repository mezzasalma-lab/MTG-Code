# Checklist cláusula-a-cláusula — Megatron, Tyrant

## +The Ten Rings / -Phyrexian Arena, +BlightSteel Colossus / -Gilded Lotus — 2026-09-18

**Gatilho:** usuário questionou 2 pontos da minha análise anterior das
7 sugestões de carta — "The Ten Rings SEMPRE enche minha mão... vc não
computou isso" e "quanto de mana incolor... pra vc afirmar que hardcast
[do BlightSteel] é impossível?". Ambos os pontos eram reais; instrumentei
com dado do motor (Regra #5, simulador como evidência de apoio) antes de
responder, em vez de defender a análise original.

### The Ten Rings (oráculo real, Scryfall)

`{8}` Legendary Artifact — "Your maximum hand size is ten. At the
beginning of your end step, if you have fewer than ten cards in hand,
draw cards equal to the difference."

**Achado real:** instrumentei `len(state.hand)` no fim de cada turno em
3.000 jogos — a mão estabiliza em ~3,3 cartas do turno 6 em diante
(3.42/3.33/3.29/3.33/3.38 nos turnos 6-10). Como The Ten Rings compra a
DIFERENÇA até 10 (não 1 fixa como a Phyrexian Arena), em campo a partir
do turno 6+ ela compraria ~6-7 cartas TODO end step.

**Implementado:**
- `try_ten_rings_draw(state)` — calcula `10 - len(state.hand)` ANTES de
  comprar (pra métrica correta), chama `draw_cards`, incrementa
  `state.ten_rings_draws_total`. Chamada no início de `end_step`
  (oráculo real: "at the beginning of your end step").
- `max_hand` no cleanup de `end_step` sobe pra 10 quando ela está em
  campo (era fixo em 7) — segunda cláusula real ("your maximum hand size
  is ten"), senão a mão comprada seria descartada na mesma passada.

### BlightSteel Colossus (oráculo real, Scryfall) + bug real achado

`{12}` Artifact Creature 11/11, Trample/Infect/Indestructible —
"If Blightsteel Colossus would be put into a graveyard from anywhere,
reveal Blightsteel Colossus and shuffle it into its owner's library
instead."

**Achado real (mana):** instrumentei `megatron_postcombat` (o 2º flip,
que gera `{C}` = vida perdida pelos oponentes no turno) por EVENTO
individual em 5.000 jogos: média de 14,58 mana incolor por evento
(mediana 12), 57% dos eventos já ≥12 (custo cheio do BlightSteel), subindo
pra 68% no turno 8 e 84% no turno 10.

**Bug real achado ao investigar isso:** `megatron_postcombat` estava
sendo chamado dentro de `end_step`, que roda DEPOIS da 2ª chamada de
`main_phase` do turno (`play_turn`: main_phase → combat_step →
main_phase → end_step). A mana gerada pelo 2º flip nunca era gastável
em nenhum cast daquele turno — só alimentava o contador
`megatron_mana_generated_total`, nunca o `remaining_mana()` real na hora
de conjurar algo. Oráculo real: "At the beginning of each of your
postcombat main phases, you may convert Megatron" — o gatilho tem que
resolver ANTES do main phase pós-combate rodar. Corrigido: `megatron_
postcombat(state)` movido pra `play_turn`, entre `combat_step` e a 2ª
chamada de `main_phase`.

**Achado real (combo com Chandra's Ignition):** usuário apontou "esse
com o infect e o Chandra's Ignition vira auto-win". Confirmado via
oráculo: Chandra's Ignition = "Target creature you control deals damage
equal to its power to each other creature and each opponent" — sem
+X/+X (não precisa dobrar poder). Infect faz QUALQUER dano dessa fonte
virar veneno nos oponentes; 11 de poder já excede o teto real de derrota
por veneno (`POISON_LETHAL = 10`), sozinho, sem dobrar nada. **Correção
importante sobre a linha via Nexus of Becoming que o usuário sugeriu**:
o token do Nexus é fixado em 3/3 ("except it's a 3/3 Golem artifact
creature"), então exilar o BlightSteel por ele dá um corpo de só 3 de
poder — 3 de veneno, insuficiente. A linha real funciona via hardcast
(dado do motor acima), Sneak Attack ou o ataque do Anrakyr (poder cheio
11), não via Nexus.

**Implementado:**
1. `sacrifice()` ganhou um redirect pra "Blightsteel Colossus": em vez
   de ir pro cemitério, é inserido de volta na biblioteca em posição
   aleatória (`state.rng`, o mesmo rng do mulligan/shuffle inicial,
   agora guardado em `state.rng` pra esse uso). Nunca fica preso no
   cemitério — nunca é alvo de Goblin Welder/Scrap Welder/Trash for
   Treasure/Osgir/Scarecrone/Portal to Phyrexia (todos exigem
   "graveyard" no oráculo real deles).
2. `all_attackers_combat()`: criatura com tag `"infect"` e poder ≥
   `POISON_LETHAL` marca `state.blightsteel_poison_win = True` ao
   atacar — já é letal sozinho, sem precisar da Ignition (basta atacar
   desbloqueado, convenção de sempre: sem bloqueio real modelado pra
   nenhum atacante meu).
3. `try_chandras_ignition()` reescrita: se BlightSteel Colossus está em
   campo com poder ≥10, ele passa a ser a fonte (bypassa o `CHANDRAS_
   IGNITION_LETHAL_THRESHOLD` — esse threshold só faz sentido pra dano
   de vida, veneno mata em qualquer vida). Não usa `ready_creatures`
   pra esse check — "target creature you control" não exige ausência de
   doença de invocação pra ser alvo legal de spell.

**Corte de Phyrexian Arena**: 1 carta/turno por 1 de vida, redundante
com o volume muito maior do Ten Rings a partir de quando ele resolve
(ver dado real acima).

**Corte de Gilded Lotus**: pior rate de rampa da lista (3 mana da MESMA
cor por 5 mana) — nenhuma outra carta da lista pede 3 pips da mesma cor
(os custos duplos mais pesados são `{R}{R}`/`{B}{B}`/`{W}{W}`, só 2),
então o "upside" dela nunca é usado de verdade; The Eternity Elevator já
cobre o mesmo slot de 5-mana-ramp com upside real (station escalando).

### Validação

- Smoke test: 99 cartas, 0 desconhecidas (achou 1 problema real ao
  rodar: `lista.md` ainda tinha "Gilded Lotus"/"Phyrexian Arena" como
  linhas do decklist mesmo depois de removidas do `CARD_DB` —
  `KeyError` real, corrigido atualizando as 2 linhas em `lista.md`).
- 5 testes unitários isolados: Ten Rings compra a diferença exata (3→10,
  +7) e não dispara sem estar em campo; BlightSteel sacrificado vai pra
  biblioteca (não cemitério); BlightSteel atacando sozinho (poder 11,
  sem doença de invocação) marca `blightsteel_poison_win`; Metalwork
  Colossus (sem infect) NÃO marca; Chandra's Ignition conjura mesmo com
  `proxy_damage_total=0` quando BlightSteel está em campo (bypassa o
  threshold) e ainda funciona no modo antigo (Megatron + threshold)
  quando BlightSteel não está presente.
- `run_batch` 2000 jogos, mesma seed, antes vs depois: mana gerada pela
  conversão do Megatron 33,89→55,90 (fix do timing realmente disponibiliza
  a mana), dano proxy total 41,13→66,73, cartas compradas extra
  9,79→13,37, Chandra's Ignition como finalizador 0,1%→5,7%, Ayara
  transformou 2,3%→11,6% — tudo na direção esperada (motor mais forte),
  nenhuma métrica quebrada ou negativa. Novo auto-win via veneno em
  1,6% das partidas (0,9% via combo com a Ignition).
- Regressão de 20.000 partidas no goldfish padrão + 20.000 no modo de
  resiliência + 3.000 em turns=14 — 0 exceções nos três.

## Megatron ataca SOZINHO de propósito pro combo com Ironsoul Enforcer — 2026-09-17

**Gatilho:** usuário pediu 3 candidatas a corte "SEM ERROS". Sugeri
Ironsoul Enforcer (4/4, "whenever this creature or a commander you
control attacks alone, return target artifact card from your graveyard
to the battlefield") como corte, com base numa instrumentação que media
a taxa de disparo assumindo a IA fixa do `all_attackers_combat()` (ataca
com tudo que está pronto, convenção "todo mundo ataca" desde
2026-09-02). O usuário corrigiu: **"Ironsoul traz de volta pro campo qq
artefato quando ele OU o comandante ataca sozinho... Megatron ataca,
traz de volta, sacrifica causando dano, flipa, causa dano de combate,
gera mana incolor e flipa de novo. Ele não precisa atacar!"** — Megatron
é o próprio comandante, então "attacks alone" é satisfeito só com ELE
atacando, sem nenhuma outra criatura envolvida; a métrica que eu tinha
medido não capturava esse combo porque a IA do goldfish nunca escolhe
deliberadamente atacar só com o Megatron — ela sempre ataca com tudo.
Confirmado via Scryfall: Megatron, Tyrant (verso Destructive Force) —
"Whenever Megatron attacks, you may sacrifice another artifact. When
you do, Megatron deals damage equal to the sacrificed artifact's mana
value to target creature. If excess damage would be dealt to that
creature this way, instead that damage is dealt to that creature's
controller and you convert Megatron."

**Sequência real do combo** (os 2 gatilhos disparam juntos na
declaração de ataque; o controlador escolhe a ordem deles na pilha —
coloca-se o do Ironsoul pra resolver PRIMEIRO): Ironsoul devolve o
artefato de maior CMC do cemitério pro campo → esse artefato recém-
chegado fica disponível como fuel do próprio gatilho de ataque do
Megatron → dano extra (excesso vai pro controlador do alvo) + flipa
Megatron no meio do combate (trocar de face não remove do combate,
ainda causa dano de combate normal) → no postcombat main da face Tyrant
pode converter de novo, ganhando `{C}` = vida perdida pelos oponentes
esse turno. O corpo reanimado, se sobrar (não for usado como fuel),
fica permanente no campo (fuel pro weld/Ultron/Metalwork Colossus).

**Implementado:**
1. `ironsoul_reanimate(state)` — corpo real do gatilho do Ironsoul,
   fatorado numa função própria (antes estava só dentro de
   `ironsoul_enforcer_trigger`) pra poder ser chamado tanto pelo caso
   orgânico (poucas criaturas prontas por acaso) quanto pelo caso
   deliberado, ANTES da escolha de fuel do Megatron.
2. `try_megatron_alone_with_ironsoul(state)` — decide se vale abrir mão
   do ataque do resto do time: só quando Ironsoul Enforcer está em
   campo, o Megatron está pronto pra atacar, há artefato no cemitério, E
   o CMC do maior artefato do cemitério bate mais poder-equivalente do
   que a soma do poder das outras criaturas prontas (sem bloqueio real
   modelado, atacar com todo mundo é sempre pelo menos tão bom quanto
   não atacar — só compensa abrir mão disso quando o combo entrega
   mais). Se decide ir sozinho: chama `ironsoul_reanimate` ANTES de
   `megatron_combat`, marca `ironsoul_triggered_this_combat` (evita
   reanimar 2x) e incrementa `megatron_alone_combos_total`.
3. `combat_step()` reordenado: decide "sozinho" antes de crewar o
   Demonic Junker (crewar e depois não atacar desperdiçaria o crew) e
   antes de `all_attackers_combat()` (pulado quando vai sozinho).
   `ironsoul_enforcer_trigger()` continua cobrindo o caso orgânico
   (poucas criaturas prontas por acaso), com guarda pra não duplicar
   quando o caso deliberado já disparou.

**Validação:**
- Smoke test: 0 nomes desconhecidos.
- 4 testes unitários isolados: (1) combo dispara com Metalwork Colossus
  (CMC 11) no cemitério e nenhuma outra criatura pronta; confirma que o
  artefato reanimado é sacrificado como fuel do próprio ataque do
  Megatron no mesmo combate (dano proxy 17 = 10 de excesso + 7 do
  Megatron já convertido pra Tyrant); (2) NÃO dispara quando as outras
  criaturas prontas somam mais poder (10) do que o CMC do cemitério (2,
  Fellwar Stone); (3) NÃO dispara sem Ironsoul Enforcer em campo; (4)
  NÃO dispara com cemitério vazio.
- `run_batch` 2000 partidas, mesma seed, antes vs depois: dano proxy
  total 41,05→41,13, eventos de recursão 0,63→0,67, solda 0,41→0,42 —
  todas na direção esperada (mais valor), nenhuma métrica regrediu.
  Novo combo dispara em 0,04 partidas/média (esperado — 1 cópia de
  Ironsoul Enforcer em 65 cartas não-terrestres, raro de estar em
  campo).
- Regressão de 20.000 partidas no goldfish padrão + 20.000 no modo de
  resiliência (separado, garantindo que a mudança em `combat_step` não
  quebrou esse modo opcional) — 0 exceções nos dois.

## Perfis variados de token no modo de resiliência (ataque) — 2026-09-16

**Gatilho:** usuário pediu pra variar o tipo de token de ataque
("Knight, saproling, vampiro, etc") em vez do perfil fixo 2/2
calibrado no round anterior.

**Implementado:** `OPPONENT_ATTACKER_PROFILES` — lista de 7 perfis com
stats típicos reais de cada tipo de token comum em Commander (Knight
2/2, Saproling 1/1, Vampire 1/1, Zombie 2/2, Soldier 1/1, Goblin 1/1,
Elemental 3/3), sorteada via `state.interaction_rng.choice()` a cada
ataque. Keywords de evasão (ex.: flying do Vampire token) ficam FORA
de propósito — mesma convenção de "sem bloqueio real modelado" já
documentada no resto do arquivo, só poder/resistência entram na conta.
`try_smart_opponent_attack()` agora retorna o nome do token (não mais
bool) pra log/relatório; novo `state.smart_attack_log` rastreia
`(turno, nome, "blocked"/"unblocked")`.

**Validação:** 4 testes unitários isolados (sem `interaction_rng`
nunca ataca; Feldon 2/3 bloqueia e mata o Knight 2/2 sorteado à força;
**Elemental 3/3 sorteado à força passa até pelo Feldon** — poder 2 <
resistência 3, não consegue matar — confirma que a variedade muda o
resultado de verdade, não é só cosmético; os 7 perfis existem com
valores plausíveis) + smoke test + batch de 2000 (breakdown por tipo:
Elemental conecta em 286 de 2000 jogos contra só 20 bloqueios, tokens
1/1 bloqueiam com taxa muito mais alta — direção esperada) + regressão
de 20.000 partidas em cada modo, 0 exceções.

## Modo de resiliência estendido: ataque de oponente + bloqueio — 2026-09-16

**Gatilho:** usuário narrou um bloqueio real do último goldfish manual —
*"O ataque o Knight token do adversário absorvi com o Feldon, ele é 2/3
e os knights eram 2/2! Um passou e outro morreu"* — confirmando que
Feldon (2/3) mata um Knight 2/2 no bloqueio e sobrevive. Pediu pra
estender o modo de resiliência (removeção já implementada) pra também
cobrir esse eixo: ataque de oponente + decisão de bloqueio, que o
goldfish puro nunca modela ("sem bloqueio real modelado pra ninguém").

**Implementado:**
1. `interaction_chance()` — fórmula de chance extraída pra função
   compartilhada (era duplicada dentro de `try_smart_opponent_removal`)
   — usada agora por ambos os eventos (remoção E ataque), que rolam
   **independente** um do outro no mesmo turno.
2. `OPPONENT_ATTACKER_POWER/TOUGHNESS = 2/2` — perfil genérico
   calibrado pelo exemplo real do usuário (Knight token 2/2).
3. `try_smart_opponent_attack()` — bloqueia com a MENOR criatura pronta
   que mata o atacante E sobrevive (`power >= 2 and toughness > 2`,
   preserva as criaturas grandes pro meu próprio ataque); sem
   bloqueador bom disponível, leva 2 de dano na cara. Megatron NUNCA
   bloqueia — já atacou nesse ciclo (tapped), e na face Vehicle só é
   criatura durante O MEU turno ("Living metal") — não existe como
   bloqueador em nenhuma das duas faces no turno do oponente.

**Validação:** 5 testes unitários isolados (sem `interaction_rng` nunca
ataca; **Feldon 2/3 bloqueia e mata o Knight 2/2 sem dano — cenário
real exato do usuário**; sem bloqueador disponível leva o dano; Megatron
nunca bloqueia; turnos de setup nunca atacam) + smoke test + A/B 2000
jogos mesma seed (vida final 37,44→35,82 com o ataque ativo, direção
esperada) + regressão de 20.000 partidas em cada modo, 0 exceções.
`smart_attacks_taken_total` confirmado em 0,82/partida, `smart_blocks_
total` em 0,20/partida.

## Modo opcional de resiliência: remoção "inteligente" de oponente — 2026-09-16

**Gatilho:** usuário jogou com o simulador de interação do Archidekt
(injeta ataque/remoção/counterspell aleatório num goldfish solo) e
apontou uma observação real: um oponente de mesa de verdade não remove
aleatório — mira sempre a peça que virou motor recorrente ("quando
estava com Portal na mesa a remoção de artefato automaticamente pega
ele, por causa do motor que ele traz pro deck"). Perguntei 3 decisões
de design antes de implementar (frequência, critério de alvo, escopo)
— usuário confirmou: setup nos turnos 1-2, chance escalando com
"poder/tamanho/impacto do boardstate" a partir daí; lista curada de
peças-motor (não maior MV genérico); **modo separado e opcional**, sem
tocar o goldfish padrão.

**Implementado:**
1. `INTERACTION_ENGINE_PRIORITY` — lista curada por prioridade
   (Warstorm Surge, Portal to Phyrexia, Goblin Welder, Pia's
   Revolution, Genesis Chamber, Ultron, Cosmic Cube, Daretti Scrap
   Savant, Osgir, Scrap Trawler). Metalwork Colossus fica DE FORA de
   propósito — ele já quer ser removido/sacrificado pra voltar via
   `try_metalwork_colossus_recursion`, remover ele não atrapalha o
   plano, um oponente esperto não gastaria a remoção nele.
2. `try_smart_opponent_removal()` — a partir do turno 3
   (`INTERACTION_SETUP_TURNS = 2`), rola 1x por turno contra a peça de
   maior prioridade presente em campo; chance = `min(0.10 + 0.03 *
   permanentes_nao_terreno_em_campo, 0.75)` (aproximação documentada de
   "impacto do boardstate" — mais desenvolvido, mais provável reagir).
   Sem nenhuma peça curada em campo, nunca dispara (oponente não gasta
   remoção "aleatória" em corpo grande vanilla).
3. **Achado real ao implementar**: `sacrifice()` (função central)
   disparava Rakdos, the Muscle incondicionalmente — mas o oráculo dele
   é `"whenever YOU sacrifice another creature"`, não `"whenever a
   creature dies"`. Destruição de oponente não é MEU sacrifício.
   Corrigido: novo parâmetro `is_own_sacrifice: bool = True` (default
   preserva 100% do comportamento existente em todos os call sites
   atuais) — só pula o gatilho do Rakdos quando `False`.
4. Novos `simulate_one_with_interaction()`/`run_batch_with_interaction()`
   — funções TOTALMENTE separadas, nunca chamadas por
   `simulate_one`/`run_batch` padrão. Novo campo `state.interaction_rng`
   (só setado por esse modo — `try_smart_opponent_removal` retorna
   `None` de imediato se for `None`, preservando o goldfish puro
   intacto).

**Validação:** 5 testes unitários isolados (sem `interaction_rng` nunca
remove; turnos 1-2 nunca removem; destruição NÃO dispara Rakdos;
sacrifício MEU continua disparando Rakdos normalmente — regressão; modo
padrão `simulate_one` nunca seta `interaction_rng`) + smoke test (99
cartas) + batch de 2000 no modo resiliência (0,34 remoções/partida em
média; Goblin Welder o mais atingido, 8,0% dos jogos — faz sentido, é o
mais barato/cedo da lista curada) + A/B mesma seed contra `run_batch`
padrão (dano 41,27→40,22, ativações de solda 0,44→0,35, recursão
0,60→0,55 — todas na direção esperada, interação real puxa pra baixo)
+ regressão de 20.000 partidas em CADA modo (resiliência e padrão), 0
exceções nos dois.

## Goblin Engineer prioriza artefato-criatura (Portal to Phyrexia/Scarecrone) — 2026-09-15

**Gatilho:** usuário perguntou se havia busca de artefato no deck por
causa do Portal to Phyrexia. Resposta real: só o Goblin Engineer busca
biblioteca (`search your library for an artifact card, put it into
your graveyard`) — mas confirmei com teste que a heurística anterior
(`max` só por MV) podia empatar Portal to Phyrexia (MV9, NÃO criatura)
com Triplicate Titan/Skitterbeam Battalion (MV9, criaturas) e escolher
o Portal — mandando ele pro cemitério onde fica inútil tanto pra sua
própria recursão (`try_portal_phyrexia_upkeep`, exige "creature card")
quanto pra do Scarecrone (exige "artifact CREATURE card").

**Corrigido:** `max(gy_targets, key=lambda n: (is_creature_card(n),
CARD_DB[n].mv))` — prioriza criatura-artefato primeiro, MV descendente
como critério secundário. Nunca "whiffa": se não houver nenhuma
criatura-artefato na biblioteca, ainda busca o melhor não-criatura
disponível (não é obrigatório achar target, "may search").

**Validação:** 3 testes unitários isolados (empate MV9 escolhe a
criatura; sem criatura disponível ainda busca o melhor não-criatura;
continua preferindo maior MV entre criaturas) + smoke test + A/B 2000
jogos mesma seed (idêntico — só muda QUAL alvo é escolhido em empates
raros, não a frequência) + regressão de 20.000 partidas, 0 exceções.

## Auditoria comparativa completa das 65 cartas + Noxious Gearhulk/Cityscape Leveler corrigidas — 2026-09-15

**Gatilho:** usuário pediu pra eu sugerir novos candidatos de corte pro
Dauntless Scrapbot, mas depois do histórico de hoje (3 rodadas de
"cartas fracas" que na verdade eram bugs reais), decidi fazer uma
auditoria de verdade primeiro em vez de julgar por memória de novo:
puxei oráculo real via `/cards/collection` das 65 cartas não-terreno de
uma vez, cruzei `type_line` contra `ctype` (0 mismatches novos — o
Demonic Junker já tinha sido corrigido), e busquei todo texto com
"destroy"/"exile" pra comparar tratamento entre cartas parecidas.

**Achado real (2 cartas, mesma classe de bug de hoje):**

1. **Noxious Gearhulk** — `"you may destroy another target creature.
   If a creature is destroyed this way, you gain life equal to its
   toughness."` Estava um `pass` completo, documentado como "📊
   estrutural" — mas é remoção de ALVO ÚNICO no oponente, MESMA forma
   de Path to Exile/Swords to Plowshares/Generous Gift, todas já
   creditadas como `interaction_spells_cast_total`. Inconsistente
   deixar só essa zerada. Corrigido: credita interação + ganho de vida
   proxy (3, aproximação de resistência média de criatura — sem
   resistência real de oponente rastreada).

2. **Cityscape Leveler** — `"When you cast this spell and whenever
   this creature attacks, destroy up to one target nonland
   permanent."` Mesmo problema: tratada como zero por "só alvo válido
   no oponente", mesma categoria das já creditadas. Corrigido: nova tag
   `cityscape_leveler`, credita interação no ETB (cast) E em cada
   ataque (`all_attackers_combat`). Também achei que o **Unearth {8}**
   dela nunca foi implementado, excluído com o raciocínio "custo igual
   ao hardcast, sem ganho de modelar separado" — o MESMO raciocínio que
   teria rejeitado o Warp {3} do Bygone Colossus, que É modelado
   (`try_bygone_colossus_warp`). Inconsistente excluir só esse.
   Implementada `try_cityscape_leveler_unearth()`, mesmo padrão do
   Warp: reanima do cemitério com haste, exilada no fim do turno,
   dispara o ETB completo de novo (Warstorm Surge + a remoção real).

**Achado lateral:** `interaction_spells_cast_total` era incrementado em
8 pontos diferentes do arquivo mas NUNCA aparecia em nenhum print do
`run_batch` — métrica cega, sem visibilidade de validação nenhuma.
Adicionada linha de print dedicada.

**Confirmado limpo no resto da auditoria:** Bahamut (capítulos I/II) já
credita interação corretamente pra "destroy up to one target nonland
permanent" — mesmo padrão agora aplicado a Noxious Gearhulk/Cityscape
Leveler. Os 62 outros `ctype` batem com o `type_line` real (sem novo
caso tipo Demonic Junker/Vehicle).

**Achado adicional (pergunta de regra do usuário, ao vivo): sacrificar
um permanente Warp/Unearth vai pro EXÍLIO, não pro cemitério** — usuário
perguntou se o Cityscape Leveler reanimado via Unearth, ao ser
sacrificado pro Megatron ANTES do fim do turno, iria pro cemitério ou
exílio, e se ganhava um "finality counter". Ele mesmo confirmou via
ruling oficial: *"If a permanent returned to the battlefield with
unearth would leave the battlefield for any reason, it's exiled
instead"* — sem counter nenhum, é substituição de zona embutida no
próprio Unearth (Warp do Bygone Colossus tem o mesmo texto). Achado
real: `sacrifice()` (função central de todo sacrifício do arquivo)
sempre mandava pro `state.graveyard` incondicionalmente, ignorando
`state.temp_creatures_pending_exile` — sacrificar um Warp/Unearth antes
do fim do turno colocava a carta no cemitério ERRADO, disparando
Scrap Trawler/Pia's Revolution/morte do Triplicate Titan (todos exigem
"put into a GRAVEYARD", que nunca acontece de verdade aqui) e deixando
a carta disponível pra weld/re-Warp/re-Unearth de novo — que a regra
real não permite. Corrigido: `sacrifice()` agora checa
`temp_creatures_pending_exile` primeiro e redireciona pro `state.exile`
nesse caso, pulando os gatilhos "put into a graveyard" mas mantendo o
gatilho de sacrifício em si (Rakdos, the Muscle dispara em QUALQUER
sacrifício, não em "dies"). Vale tanto pro Cityscape Leveler (Unearth)
quanto pro Bygone Colossus (Warp) — mesmo texto de substituição,
mesma função central corrigida uma vez só.

**Validação:** smoke test (99 cartas, 0 desconhecidas/duplicatas) + 6
testes unitários isolados (Noxious Gearhulk credita interação+vida;
Cityscape Leveler credita no ETB e a cada ataque; Unearth reanima com
haste e credita de novo; sacrificar o Cityscape Leveler reanimado vai
pro exílio nunca pro cemitério; mesmo redirect vale pro Bygone Colossus
warpado; sacrifício NORMAL sem Warp/Unearth continua indo pro cemitério
normalmente) + A/B 2000 jogos mesma seed (vida ganha 0,11→0,31,
criaturas cheatadas 0,34→0,40, resto estável) + regressão de 20.000
partidas, 0 exceções. `interaction_spells_cast_total` confirmado em
1,13/partida (antes invisível, mesmo disparando).

## Crew 2 do Demonic Junker implementado — 2026-09-15

**Gatilho:** minutos depois de eu documentar "usuário confirmou que
nunca vai crewar" (rodada anterior desta mesma sessão), o usuário
descreveu exatamente uma linha de crew: *"Nexus of becoming Exila um
talisma, cria um token 3/3 dele com CVC 2, esse token pode crew o
Demonic Junker, Junker e Megatron atacam e Megatron sacrifica o token
para flipar e causar mais dano!"* — mudança real de plano, implementada
na hora em vez de deixar "0" documentado.

**Oráculo real confirmado:** `"Crew 2"` = texto de reminder padrão
`"Tap any number of untapped creatures you control with total power 2
or greater: This Vehicle becomes an artifact creature until end of
turn."`

**Achado lateral do próprio usuário, ANTES de eu implementar:** *"O
token do Nexus não tem haste, infelizmente"* — correto, e já bate com
`ready_creatures()` (doença de invocação já existente): crewar é custo
de `{T}`, sujeito à mesma restrição de atacar — um token criado NESSE
combate (Nexus dispara "at the beginning of combat") nunca pode crewar
no mesmo turno sem haste real. A combo específica descrita não funciona
turn-1 do token, mas funciona com fodder de um turno anterior (Myr
Token do Genesis Chamber, Fish Token do Fountainport, etc.) — testado e
confirmado.

**Implementação:**
1. Novo conceito `state.crewed_creatures_tapped` (set) — primeira vez
   que o arquivo modela "esta criatura tapou por outro motivo esse
   turno" (`ready_creatures()` agora exclui essas, correção que também
   vale pra `Welder`/`Scrap Welder`/`Engineer`/`Scarecrone`/estação, que
   também exigem `{T}` — regra real: tapado não tapa de novo).
2. Nova `try_crew_demonic_junker()` — tapa as criaturas prontas de
   MENOR poder disponíveis até somar Crew 2 (preserva atacantes
   grandes), nunca tapa o Megatron.
3. `all_attackers_combat()` — Demonic Junker crewado esse turno passa a
   contar como atacante explícito (não aparece em `ready_creatures()`
   por ser `ctype: "artifact"` por padrão).

**Bug real achado ao testar a combo do usuário:** `best_megatron_fuel()`
prioriza sempre o MAIOR MV disponível — como o Demonic Junker (MV 7) é
o maior artefato do campo, ele era sacrificado como o PRÓPRIO
combustível assim que crewado, perdendo o ataque que o crew tinha
acabado de habilitar (desperdiça a criatura/token que tapou pra nada).
Corrigido: `KEEP_ALWAYS` de `best_megatron_fuel()` exclui "Demonic
Junker" enquanto `state.demonic_junker_crewed_this_turn` for `True` —
depois do combate (ou se nunca foi crewado), volta a ser candidato
normal.

**Validação:** 4 testes unitários isolados (2 tokens de turno anterior
somando poder 2 crewam; 1 token de poder 1 sozinho não crewa; token
criado nesse turno não crewa — doença de invocação; Junker crewado
ataca E sobrevive, Megatron sacrifica outra coisa como fuel) + smoke
test + A/B 2000 jogos mesma seed (métricas estáveis) + regressão de
20.000 partidas, 0 exceções. `demonic_junker_crews_total` confirmado em
0,06/partida (raro mas real — exige Junker + fodder pronto de turno
anterior simultaneamente).

## Demonic Junker (Vehicle) + Chandra's Ignition (finalizador) + Nexus of Becoming (cópia real) + bug do Trash for Treasure — 2026-09-15

**Gatilho:** usuário rejeitou os 3 candidatos de corte que eu tinha
proposto pro Dauntless Scrapbot, explicando o uso real de cada carta —
achado real que eu tinha classificado como "estrutural/dead" por
análise superficial, sem verificar oráculo exato ou testar o fluxo de
cast de verdade. Ao verificar, achei 4 problemas reais (3 apontados
pelo usuário + 1 lateral achado ao investigar).

**1. Demonic Junker é VEHICLE, não Artifact Creature** — oráculo real:
`"Artifact — Vehicle"`, `Crew 2`. Estava registrado com `ctype:
"creature"` no `CARD_DB`, um erro de categorização real com efeito em
cascata:
- Disparava Warstorm Surge no ETB (errado — Vehicle não-crewado não é
  criatura).
- Aparecia em `ready_creatures()`/`all_attackers_combat()`, atacando
  sozinho todo turno como se fosse criatura de verdade (errado).
- NÃO contava pro desconto do Metalwork Colossus (`noncreature
  artifacts you control` — devia contar, já que Vehicle não-crewado É
  artefato não-criatura).

  Corrigido: `ctype: "artifact"`. A habilidade real do ETB (`"for each
  player, destroy up to one target creature that player controls"`)
  estava um `pass` completo (tratada erroneamente como 📊 estrutural,
  igual Noxious Gearhulk) — mas "for each player" bate em CADA
  oponente de verdade (mesma convenção de "each opponent" já usada no
  arquivo, não é alvo único isolado). Implementado:
  `interaction_spells_cast_total += NUM_OPPONENTS` + novo contador
  dedicado `demonic_junker_removals_total`. Usuário confirmou que nunca
  vai crewar (Crew 2 fica de fora, 0 — decisão consciente, não
  estrutural) — **decisão revertida na mesma sessão, ver seção
  seguinte**.

**2. Chandra's Ignition era wrath incondicional excluído, mas é
finalizador condicional** — usuário: *"se tiver 2 oponentes com 7 ou
menos de vida vale usar no Megatron e eliminar estes 2, além de ser
boardwipe"*. Oráculo real: `"Target creature you control deals damage
equal to its power to each other creature and each opponent."` A carta
estava em `NO_SELF_HARM_EXCLUDE`, nunca conjurada — tratando o efeito
só pelo lado ruim (perder o próprio board) sem modelar o lado bom
(queima real em TODOS os oponentes, "each opponent" × NUM_OPPONENTS).
Nova `try_chandras_ignition()`: só ativa quando `proxy_damage_total >=
CHANDRAS_IGNITION_LETHAL_THRESHOLD` (70, aproximação documentada — sem
vida real de oponente rastreada, é a melhor métrica proxy disponível),
sempre aponta pro Megatron, mata minhas próprias criaturas com
resistência ≤ poder do Megatron via `sacrifice()` (dispara os gatilhos
reais de morte).

**3. Nexus of Becoming criava token vanilla desconectado, não uma
cópia real** — usuário: *"Permite criar tokens de Demonic Junker...
alimentando o sac do Megatron"*. Oráculo real: `"create a token that's
a copy of the exiled card, except it's a 3/3 Golem artifact creature in
addition to its other types."` A versão anterior exilava a carta de
MENOR MV e criava um "Nexus Golem Token" genérico sem nenhuma tag/
habilidade da carta original — nunca modelava a cópia de verdade.
Corrigido: nova `make_nexus_copy_name()` (mesma técnica de aliasing do
`make_token_copy_name`, preservando tags/MV do original, só
sobrescrevendo poder/resistência pra 3/3 — regra real de cópia); escolha
mudou de MENOR pra MAIOR MV (exilar o card mais caro da mão é "cheatar"
o ETB mais valioso pro campo pelo preço da ativação). Confirmado com
teste: exilar Demonic Junker via Nexus faz o token 3/3 disparar a
remoção real dele E manter MV 7 (fuel pro Megatron/desconto do
Metalwork Colossus).

**4. Bug lateral achado ao verificar o caminho de Trash for Treasure**
— ao confirmar que a função dedicada roda corretamente, descobri que o
loop genérico de castables (`main_phase`) conjurava "Trash for
Treasure" como qualquer sorcery afordável ANTES da função dedicada
(`try_trash_for_treasure`, que paga o custo adicional real de
sacrificar um artefato) rodar — `resolve_instant_sorcery()` não tem
dispatch pra essa tag, então a carta era gasta (mana + carta pro
cemitério) por ZERO efeito. Confirmado com teste isolado ANTES da
correção. Corrigido: "Trash for Treasure" adicionada à exclusão do loop
genérico (mesmo conjunto do `NO_SELF_HARM_EXCLUDE`, motivo diferente —
custo adicional não pago pelo caminho genérico).

**Validação:** smoke test (99 cartas, 0 desconhecidas/duplicatas) + 5
testes unitários isolados (Demonic Junker não dispara Warstorm/não
ataca sozinho; Chandra's Ignition não ativa com pouco dano
acumulado/ativa e poupa criatura resistente com dano suficiente; Nexus
exila a maior MV e o token herda a habilidade real) + A/B 2000 jogos
mesma seed (métricas estáveis, artefatos sacrificados 3,64→3,73) +
regressão de 20.000 partidas, 0 exceções. Novos contadores confirmados
disparando: `demonic_junker_removals_total` 0,31/partida, Chandra's
Ignition usada como finalizador em 0,1% dos jogos (raro mas real —
exige atingir o threshold dentro de só 8 turnos simulados).

## +Triplicate Titan / -Phyrexian Triniform — 2026-09-15

**Gatilho:** usuário confirmou a troca que eu tinha recomendado numa
rodada anterior (nunca aplicada). Reverifiquei o oráculo antes de
aplicar, seguindo a Regra #4 mesmo numa troca já "decidida".

**Oráculo real (ambas {9}, Artifact Creature 9/9):**
> Phyrexian Triniform: "When this creature dies, create three 3/3
> colorless Phyrexian Golem artifact creature tokens. Encore {12}
> ({12}, Exile this card from your graveyard: For each opponent, create
> a token copy that attacks that opponent this turn if able. They gain
> haste. Sacrifice them at the beginning of the next end step. Activate
> only as a sorcery.)"
>
> Triplicate Titan: "Flying, vigilance, trample. When this creature
> dies, create a 3/3 colorless Golem artifact creature token with
> flying, a ... with vigilance, and a ... with trample."

**Achado real ao comparar:** o Encore do Triniform NUNCA tinha sido
implementado (só o death-trigger dos 3 tokens tinha dispatch) — e é
estruturalmente modelável via `NUM_OPPONENTS=3` (mesma convenção usada
pra todo "for each opponent" no arquivo). Isso seria um gap real a
corrigir SE o Triniform ficasse na lista — como ele sai com a troca, o
gap fica resolvido pela remoção, não precisa de correção separada.

**Clausula-a-clausula do Triplicate Titan:**
1. ✅ "on death: create 3x 3/3 Golem artifact creature token" —
   `death_trigger()`, dispatch por nome (`dying_name == "Triplicate
   Titan"`), token renomeado de "Phyrexian Golem Token" pra "Golem
   Token" (nome real do tipo de token da carta).
2. 📊 Flying/vigilance/trample (no corpo E em cada 1 dos 3 tokens) —
   sem bloqueio real modelado pra NINGUÉM no arquivo inteiro (nenhuma
   criatura tem essa restrição em lugar nenhum), então evasão/
   vigilância/trample não tem efeito numérico possível aqui —
   estrutural, documentado no comentário do `death_trigger`, não
   julgamento de valor.

**Bug lateral achado ao editar `lista.md`:** `build_library()` só
excluía a seção "## Comandante" (`section == "cmd"`) do parser de
contagem — qualquer linha de PROSA antes de "## Comandante" que por
acaso começasse com um número (ex.: "3 tokens ganha..." dentro do meu
próprio parágrafo de histórico) era lida como entrada de decklist.
Confirmado ao adicionar o parágrafo desta troca: biblioteca inflou de 99
pra 102 cartas com 3 "cartas" fantasma vindas do texto corrido. Corrigido
pra só aceitar linhas dentro de `section in ("deck", "land")` — fecha a
classe inteira do bug, não só o caso específico que apareceu agora.

**Validação:** smoke test (99 cartas, 0 desconhecidas/duplicatas, re-
confirmado depois do fix do parser) + teste unitário isolado (morte do
Triplicate Titan cria exatamente 3 "Golem Token", contador
`triplicate_titan_tokens_total` bate) + batch de 2000 jogos (novo
contador confirmado disparando: 0,07 Golem tokens/partida) + regressão
de 20.000 partidas, 0 exceções.

## Correção da heurística do Ultron + bug real de contagem em rocks_mana() — 2026-09-15

**Gatilho:** eu tinha descrito pro usuário que Fellwar Stone "não vira
alvo de cópia" do Ultron por causa de um "corte de MV≥3" — usuário
corrigiu: o oráculo real (`whenever ANOTHER nontoken artifact you
control enters, you may pay {2}. If you do, create a copy`) não tem
restrição de custo nenhuma, e mais importante, **duplicar um mana rock
de custo 2 é motor real de rampa recorrente + combustível de graça pro
Megatron** — a heurística `mv < 3: return` estava certa em rejeitar
copiar coisa cara demais, mas errada em achar rocks baratos "não valem a
pena": eu confundi "+1 mana nesse instante" (rate ruim) com o valor real
("+1 mana TODO turno daí em diante", ganho recorrente).

**Bug real encontrado ao testar a correção:** `rocks_mana()` checava só
PRESENÇA (`"Sol Ring" in state.battlefield`), nunca contagem de
instâncias. Uma cópia via Ultron tem nome com sufixo `" (copia)"`
(`make_token_copy_name`) — nunca bate no nome fixo do original, então a
cópia de um rock renderia ZERO mana extra mesmo estando de verdade em
campo. Confirmado com teste isolado antes da correção: `total_mana()`
com 1 Fellwar Stone + 1 cópia via Ultron = 1 (deveria ser 2).

**Correções:**
1. `rocks_mana()` reescrita pra somar por instância real na
   `battlefield`, lendo a tag (`rock1`=1/`rock2`=2/`rock3`=3, preservada
   em toda cópia porque `make_token_copy_name` aponta pro mesmo objeto
   `Card` do original) em vez do nome fixo — generaliza pra qualquer
   número de cópias, não só a do Ultron.
2. `artifact_etb_hooks()` (Ultron): novo `CHEAP_WORTH_COPYING_TAGS =
   {"rock1", "rock2", "rock3", "melded_moxite"}` — copia mesmo com MV<3
   quando a tag bate. Isso também corrige uma inconsistência do commit
   anterior (Melded Moxite): eu tinha vendido pro usuário "Ultron pode
   copiar e dobrar o loot" da Moxite como argumento pra troca por Demand
   Answers, mas ela é MV 2 — a MESMA heurística já bloqueava isso antes,
   então essa sinergia nunca disparava de verdade no simulador.
3. Novo contador `ultron_cheap_copies_total` pra validar que o caminho
   específico (MV<3 mas tag elegível) dispara de verdade, separado do
   `recursion_events_total` genérico.

**Validação:** 4 testes unitários isolados (rocks_mana conta a cópia;
Ultron copia Fellwar Stone com mana sobrando; Ultron copia Melded Moxite
e o ETB de loot dispara 2x; Ultron NÃO copia sem mana sobrando) + A/B
2000 jogos mesma seed (`recursao_events_total` 0,56→0,58, resto estável)
+ regressão de 20.000 partidas, 0 exceções. `ultron_cheap_copies_total`
confirmado > 0 numa fração real dos jogos (0,02/partida — baixo porque
exige Ultron já em campo + mana sobrando depois de outros gastos, mas
real).

## +Melded Moxite / -Demand Answers — 2026-09-15

**Gatilho:** usuário propôs a troca depois de eu confirmar que as duas
cartas fazem "discard 1, draw 2" na prática (oráculo real via Scryfall,
ambas {1}{R}, Edge of Eternities 2025-08-01). Pedi pra comparar contra
os motores do deck em vez de julgar por poder isolado — o usuário trouxe
a lógica certa por conta própria antes de eu terminar a análise, e isso
foi codificado como regra permanente (`CLAUDE.md`, Regra #4: toda
avaliação de carta futura tem que citar com quais motores/cartas
específicas da lista ela interage, nunca só "é mais forte").

**Oráculo real (Melded Moxite):**
> "When this artifact enters, you may discard a card. If you do, draw
> two cards.
> {3}, Sacrifice this artifact: Create a tapped 2/2 colorless Robot
> artifact creature token."

**Clausula-a-clausula:**
1. ✅ ETB "may discard a card. If you do, draw two cards" —
   `resolve_etb()`, tag `melded_moxite`. Sempre descarta se houver carta
   na mão (a própria Moxite já foi removida antes do ETB resolver, mesma
   convenção do arquivo inteiro) — +1 carta líquida garantida quando há
   o que descartar.
2. ✅ "{3}, Sacrifice this artifact: Create a tapped 2/2 colorless Robot
   artifact creature token" — nova `try_melded_moxite_sac()`, chamada
   por último no `main_phase` (mesmo padrão do Mind Stone). Sacrifício
   dispara Pia's Revolution (artefato não-token) via `sacrifice()`
   genérico; a entrada do token dispara Warstorm Surge de novo via
   `creature_enters()` genérico — nenhum código extra precisou tocar
   nesses 2 gatilhos, só usar a infra central já existente.

**Por que Melded Moxite bate mais motores que Demand Answers** (a lógica
que motivou a Regra #4): Demand Answers era instant — nunca "entra no
campo", nunca toca Ultron (`whenever another nontoken artifact you
control enters`), nunca reduz o custo do Metalwork Colossus (`total mana
value of noncreature artifacts you control`), e uma vez resolvido não é
mais "artifact card" — Goblin Engineer (busca sem restrição + reanima
MV≤3)/Goblin Welder/Trash for Treasure (todos exigem "artifact card" no
cemitério) nunca mais o tocam. Melded Moxite (MV 2, artefato permanente)
entra em TODOS esses pontos: dispara Ultron (pode ser copiado, dobrando
o loot), conta pro desconto do Metalwork Colossus enquanto em campo, e
continua "artifact card" no cemitério depois de sacrificado — alvo
válido de Engineer/Welder/Trash for Treasure pro resto do jogo.

**Validação:** smoke test (99 cartas na library, 0 desconhecidas, 0
duplicatas) + 4 testes unitários isolados (ETB loot com/sem carta na
mão, sac-for-token com/sem mana suficiente, confirmando Warstorm Surge
disparando no token) + comparação A/B 2000 jogos mesma seed (antes
Demand Answers, depois Melded Moxite: "nunca conjurado" 6,1%→6,6%, mão
final 3,17→3,25, cartas compradas 9,48→9,44 — dentro do ruído esperado
de uma troca lateral no mesmo custo de mana) + regressão de 20.000
partidas, 0 exceções. Métricas novas confirmadas disparando de verdade
(`melded_moxite_loots_total`, `melded_moxite_tokens_total` > 0 numa
fração real dos jogos).

## Auditoria oráculo-por-oráculo completa — 2026-09-13

**Gatilho:** um goldfish real mostrou o Ultron copiando o Portal to
Phyrexia 2x parecendo "overpowered" — investigando, achei que faltava a
metade real da carta (reanimação repetível todo upkeep, só a metade do
ETB estava implementada). Implementei sem avisar antes; usuário reclamou
com razão (não era pra eu sair implementando mecânica nova sem perguntar
por uma observação casual) — mas confirmou que queria a correção, e
pediu pra eu fazer essa auditoria completa em TODAS as 65 cartas não-
terreno da lista, não só reagir card a card.

**Método, dessa vez diferente do de 2026-09-04:** o script de auditoria
anterior (`audit_ghosts2.py`) só pega tags/nomes NUNCA referenciados —
não pega o caso real que motivou essa rodada (Portal to Phyrexia tinha a
tag `portal_phyrexia` referenciada, só faltava uma das DUAS habilidades
da carta). Dessa vez: puxei o oráculo real via Scryfall (`cards/
collection`, as 65 de uma vez) pra um dump completo, e comparei cláusula
por cláusula contra a implementação, lendo o arquivo inteiro.

**Achados reais (6 gaps confirmados, todos implementados e validados):**

1. **Portal to Phyrexia** — só o ETB ("each opponent sacrifices three
   creatures") tinha dispatch; a 2ª habilidade real, repetível todo
   upkeep ("put target creature card from a graveyard onto the
   battlefield under your control"), nunca disparava. Nova
   `try_portal_phyrexia_upkeep()` — 1 gatilho por cópia em campo
   (original + tokens via Ultron/Cursed Mirror/Osgir).
2. **Goblin Engineer** — ETB inteiro ("search your library for an
   artifact card, put it into your graveyard") nunca tinha dispatch, só
   a habilidade ativada. Corrigido em `resolve_etb()`.
3. **Mind Stone** — tag `fuel_rock1` existia (compartilhada sem sentido
   com o Cursed Mirror) mas nunca era lida em lugar nenhum — a habilidade
   real "{1},{T},Sacrifice: Draw a card" nunca disparava. Nova
   `try_mind_stone_sac()`, só ativa com mana de sobra (não sacrifica a
   única rampa disponível).
4. **Osgir, the Reconstructor** — só a habilidade principal de clonagem
   estava implementada; a de bombar ("{1}, Sacrifice an artifact: Target
   creature you control gets +2/+0") nunca disparava. Nova
   `try_osgir_pump()` + novo campo `temp_power_boost` em `GameState`
   (bônus temporário lido em `get_power()`, resetado todo turno).
5. **Summon: Bahamut** — só o Capítulo I (ETB) disparava; os campos
   `bahamut_entered_turn`/`bahamut_chapter` eram setados mas NUNCA lidos
   de novo — a saga nunca avançava, perdendo os Capítulos II (interação),
   III (draw 2) e principalmente **IV — Mega Flare** (dano = MV total dos
   outros permanentes que controlamos, pra cada oponente), o maior payoff
   da carta. Nova `try_bahamut_saga_tick()`, chamada 1x por turno após o
   draw step (mesma cadência real "after your draw step").
6. **Brass's Tunnel-Grinder** — só o ETB (looter) tinha dispatch; a
   habilidade de "descended" + bore counters + transformação pro verso
   **Tecutlan, the Searing Rift** (terreno, {T}: Add {R}) nunca existia.
   Nova `try_tunnel_grinder_transform()`, com "descended" aproximado
   comparando a contagem de permanentes no cemitério no início do turno
   vs no fim (sem instrumentar as dezenas de `state.graveyard.append`
   espalhadas pelo arquivo). Cláusula de "discover X" do verso fica de
   fora — estruturalmente impossível de rastrear sem saber qual fonte de
   mana específica pagou cada gasto (mesma limitação que já impede
   modelar o dano das Talismans).

**Achado de brinde (não é carta, é bug de código):** duas definições
duplicadas de `effective_cost()`/`can_cast()` no arquivo — a primeira
(mais simples, sem os descontos do Metalwork Colossus/Demonic Junker)
era 100% código morto, sempre sobrescrita pela segunda antes de qualquer
chamada real acontecer. As cartas já usavam a versão certa (os descontos
já funcionavam), mas a duplicata sobrando era uma armadilha real pra
qualquer edição futura. Removida.

**Validação:** smoke test (99 cartas inalteradas, é tudo mudança de
código), `audit_ghosts2.py` limpo (só os 2 falsos-positivos esperados),
batch de 2000 + regressão de 20.000 sem exceções. Instrumentado à parte
em 20.000 jogos pra confirmar que cada mecanismo dispara de verdade (não
é fantasma novo): Goblin Engineer ETB 2.526x, Mind Stone sac 1.551x,
Osgir pump 2.066x, Tunnel-Grinder transformou 45x, Bahamut Mega Flare 2x
(raro mas real — exige sobreviver 3+ turnos depois de conjurar uma
criatura de 9 mana).

---

## Auditoria sistemática de mecânicas fantasma 2026-09-04

**Gatilho:** usuário, com razão, cobrou uma varredura completa depois de
eu ter esquecido cartas repetidamente (Mirrorworks, Nexus of Becoming
2x) em respostas incrementais/reativas em vez de fazer a checagem
completa que ele já tinha pedido antes.

**Método:** script (`/tmp/.../scratchpad/audit_ghosts2.py`) que pega
toda carta definida via `add()` no `megatron_goldfish_v1.py` (70 no
total) e verifica se o NOME da carta OU alguma tag dela aparece em
QUALQUER outro lugar do arquivo, fora da própria linha do `add()`. Isso
cobre tanto dispatch por tag quanto por nome literal (a maioria das
mecânicas do arquivo é despachada checando `if "Nome" in
state.battlefield`, não só por tag) — não dá falso-negativo por causa do
estilo de código.

**Resultado:** 4 suspeitos brutos, 3 confirmados reais:

- **Nexus of Becoming** — `nexus_combat_draw_copy` nunca lido (já
  documentado antes, agora corrigido de vez).
- **Lightning Greaves** — `haste_shroud_equip` nunca lido, e não existia
  NENHUMA lógica de equip no arquivo inteiro. Confirmado com
  instrumentação real (patch em `cast_card` + 2000 jogos): conjurado 345
  vezes, equipado 0 vezes — mana e carta gastos por zero efeito, sempre.
- **Swiftfoot Boots** — mesma situação, `hexproof_haste_equip` nunca
  lido. Conjurado 267 vezes em 2000 jogos, equipado 0 vezes.
- **Treasure Nabber** — apareceu na varredura mas checado manualmente e
  NÃO é bug: o corpo dele ataca normal via `all_attackers_combat()`
  (poder 3, já corrigido junto com os outros finalizadores no combate
  expandido de 2026-09-02). Só a habilidade "whenever an opponent taps
  an artifact for mana, gain control of that artifact" fica de fora —
  estruturalmente correto, precisa de tabuleiro real de oponente
  (mesma convenção documentada em toda a sessão pra esse tipo de efeito).

Todas as outras 66 cartas do `CARD_DB` passaram — nome ou tag
referenciados em algum outro ponto do arquivo.

**Corrigido:**

- `try_nexus_of_becoming()` — oráculo real: "At the beginning of combat
  on your turn, draw a card. Then you may exile an artifact or creature
  card from your hand. If you do, create a token that's a copy of the
  exiled card, except it's a 3/3 Golem artifact creature in addition to
  its other types." Chamada no início de `combat_step()` (antes até do
  ataque, já que o gatilho é "beginning of combat"). Exila sempre a
  carta artefato/criatura de MENOR MV da mão (perder a mais barata é
  sempre lucro líquido por um corpo 3/3 grátis + gatilho do Warstorm
  Surge). Simplificação: o token não herda os "outros tipos" do card
  original (mesma convenção do Phyrexian Golem Token/Shapeshifter
  Token).
- `try_equip_haste()` — Lightning Greaves/Swiftfoot Boots. Como não há
  oponente real modelado, a metade de proteção (shroud/hexproof) não
  tem efeito mecânico possível aqui (mesma convenção já documentada pra
  Clever Concealment/Blacksmith's Skill). A metade real é o haste: uma
  criatura com doença de invocação não ataca esse turno em
  `ready_creatures()`. Equipa na criatura de maior poder que entrou esse
  turno e ainda não tem haste — grátis pro Greaves (Equip {0}), custa 1
  mana pro Boots (Equip {1}, só ativa se sobrar mana). Chamada em
  `play_turn()`, depois do primeiro `main_phase()` (criaturas já
  conjuradas) e antes de `combat_step()`.

**Validado:** rodei o script de auditoria de novo depois da correção —
as 3 tags pararam de aparecer como suspeitas (só Treasure Nabber, que já
é esperado). `run_batch` de 2000 jogos confirmou os 3 contadores novos
disparando (`nexus_tokens_created_total`, `equip_haste_activations_total`
> 0) + regressão de 20.000 partidas, 0 exceções.

---

## Correção de draw 2026-09-03 — +2 draw/valor, -2 redundantes

Oráculo confirmado via Scryfall `cards/search?order=released&dir=asc&unique=prints`
(earliest printing, não `cards/named?exact=`) antes de escrever qualquer
código — checados por `released_at` pra não repetir o erro do Shields Up!:

- **Phyrexian Arena** ({1}{B}{B}, enchantment, `released_at: 2001-06-04`)
  — "At the beginning of your upkeep, you draw a card and you lose 1
  life." Implementado literal: `try_phyrexian_arena_upkeep()`, chamado
  no início de `play_turn()` (upkeep acontece todo turno, inclusive
  turno 1 na frente — só o draw normal é pulado nesse caso).
- **Cosmic Cube** ({5}, artifact, Ward {2} — não modelado, sem remoção
  real de oponente pra ele proteger contra, `released_at: 2026-06-26`) —
  "Whenever you attack, look at the top six cards of your library. You
  may cast a spell from among them with mana value less than or equal
  to the greatest power among attacking creatures you control without
  paying its mana cost." Implementado em `try_cosmic_cube_attack_trigger()`,
  1x por combate (não por atacante), usando o novo campo
  `state.max_attacker_power_this_combat` (acumulado tanto em
  `megatron_combat()` quanto em `all_attackers_combat()`, já que aqui
  todo mundo ataca de verdade). Conjuração SEM `spend_mana` (é "without
  paying its mana cost" de verdade, não "may play").

**Cortes** (lista fixa em 99 — 2 adições exigem 2 cortes): Everflowing
Chalice (rampa redundante — 8 peças de rampa fixa já na lista antes
dela), Sandstone Oracle (7 mana por draw condicional, obsoleto com draw
melhor entrando). `cast_kickable_chalice()` e o bloco `etb_hand_diff_draw`
removidos do código junto com as cartas (não fantasmas — as cartas
deixaram de existir na lista de verdade).

**Erro real cometido e corrigido nesta rodada:** a primeira versão desta
troca também cortava Myr Retriever (achando a recursão duplicada com
Junk Diver) pra abrir espaço pra uma 3ª adição, **Florian, Voldaren
Scion** — SEM perguntar antes. Usuário reclamou direto: *"Myr retriever
nao pode sair. Pq vc cortou sem me perguntar?"*. Corrigido: Myr Retriever
voltou pra `CARD_DB`/`lista.md` (linha `add("Myr Retriever", ...)` e o
`dying_name in ("Myr Retriever", "Junk Diver")` no `death_trigger`
restaurados); usuário escolheu cortar Florian em vez disso pra fechar as
contas em 99 — toda a implementação do Florian (`try_florian_postcombat()`,
o campo `florian_cards_played_total`, a entrada em `LEGENDARY_NAMES`, a
chamada em `play_turn()` e a linha de print em `run_batch()`) foi
removida por completo do arquivo. Lição registrada: cortes de carta
precisam da MESMA confirmação explícita que adições — decidir um corte
sozinho e só avisar depois não é a mesma coisa que perguntar antes.

**Decisão Skullclamp vs. Phyrexian Arena** (usuário ficou em dúvida entre
os 2): confirmado com os próprios números do simulador que o motor de
sacrifício do deck é majoritariamente de ARTEFATOS (Megatron/Ayara/Susur
Secundi) — `Avg criaturas sacrificadas` (~1,1-1,8/partida) bem abaixo de
`Avg artefatos sacrificados` (~2,5-3,1/partida). Skullclamp dependeria de
um outlet de sacrifício de CRIATURA que o deck não tem de sobra;
Phyrexian Arena é incondicional. Detalhe completo em `goldfish-log.md`.

**Validado:** smoke test (`len(BASE_LIBRARY) == 99`, 0 nomes
desconhecidos em `CARD_DB`, 0 duplicatas fora de básicas) + `run_batch`
de 2000 jogos (0 exceções) + regressão de 20.000 partidas (seed 2M,
turns=8, 0 exceções) — rodados de novo depois da correção do Myr
Retriever/Florian.

---

## Reconstrução completa 2026-09-02 — shell de weld/cheat/sacrifice

**Contexto:** o simulador anterior (documentado nas seções abaixo,
preservadas como histórico) modelava um motor de "Megatron sacrifica
combustível barato todo turno", montado por frequência entre decklists
públicas + primer de comunidade. O dono real do deck (oponente citado
nas partidas presenciadas pelo usuário) passou a lista inicial dele, e
ficou claro que o plano de jogo real é outro: **solda/recupera artefato
+ cheat pra campo + Warstorm Surge como motor de dano**. Arquivo
reescrito do zero (`megatron_goldfish_v1.py`). Decisão carta a carta da
lista (8 cortes + 8 adições) em `lista.md`.

Oráculo de todas as 76 cartas não-terrenas confirmado ao vivo via
Scryfall (`POST /cards/collection`, 2 lotes) antes de qualquer código
ser escrito — nenhuma mecânica implementada de memória.

### Motor central implementado

- **Megatron, Tyrant / Destructive Force** — mecânica DFC `transform`
  idêntica à versão anterior (já verificada), reaproveitada: conversão
  de face, dano por sacrifício de artefato como fuel, geração de mana
  pós-combate. `cast_megatron()`/`megatron_combat()`/`megatron_postcombat()`.
  Fuel escolhido via `best_megatron_fuel()` — sempre o MAIOR MV
  disponível (achado real 2026-09-02: por engano estava reaproveitando
  `best_weld_fodder()`, que faz o oposto de propósito pro seu uso real
  de solda — corrigido depois de conferir um goldfish real do usuário
  onde ele sacrificou o maior artefato em campo como fuel).
- **Warstorm Surge** — "whenever a creature you control enters, it deals
  damage equal to its power to any target." Implementado como o ÚNICO
  ponto real de entrada de criatura no arquivo inteiro: `creature_enters()`,
  chamado por TODO cast normal, token (Feldon/Skitterbeam/Osgir/Mirrorworks/
  Adagia/Triniform) e reanimação (Trash for Treasure/Scrap Welder/Goblin
  Welder/Ayara-flip/Anrakyr/Mishra unearth/Daretti/emblema). Poder
  dinâmico via `get_power()` (cobre Daretti, Rocketeer Engineer: "power
  equal to the greatest mana value among artifacts you control").
- **Solda/recuperação de artefato**: Goblin Welder (`try_goblin_welder`),
  Scrap Welder (`try_scrap_welder`), Trash for Treasure
  (`try_trash_for_treasure`), Goblin Engineer (`try_goblin_engineer_activation`),
  Scrap Trawler (gatilho passivo em `scrap_trawler_trigger`, chamado de
  dentro de `sacrifice()`), Daretti Scrap Savant (`try_daretti_savant` —
  +2 loot / -2 solda / -10 emblema real via `daretti_ultimate_recursion_check`),
  Metalwork Colossus (`try_metalwork_colossus_recursion` — sacrifica 2,
  volta pra mão), Osgir the Reconstructor (`try_osgir_activation` — exile
  + 2 cópias-token), Mishra unearth-all (`try_mishra_unearth`).
- **Cheat pra campo**: Sneak Attack (`try_sneak_attack`, repetível — sem
  limite de 1x/turno no oráculo real, ativa em loop enquanto houver mana
  E criatura na mão), Feldon of the Third Path (`try_feldon` — token
  hasty do cemitério), Anrakyr the Traveller (gatilho próprio via
  `anrakyr_attack_ability`, chamado de dentro de `all_attackers_combat`),
  Ayara flip/Furnace Queen (`try_ayara_flip_reanimate`), Bygone Colossus
  Warp (`try_bygone_colossus_warp`, repetível).
- **Combate expandido (2026-09-02, achado real de goldfish no
  Archidekt)**: `all_attackers_combat()` — toda criatura pronta com
  poder > 0 ataca de verdade agora (não só o Megatron/Anrakyr como na
  versão original desta reconstrução), cada uma somando no mesmo pool
  compartilhado de "vida perdida pelos oponentes esse turno" que
  alimenta o pós-combate do Megatron. Ragavan, Nimble Pilferer
  (`ragavan_attack_ability`) e Daretti, Rocketeer Engineer
  (`daretti_rocketeer_attack_ability`, chamada tanto do ETB quanto do
  ataque) eram fantasmas até essa correção — as tags existiam desde a
  construção original mas nunca tinham dispatch, porque até então nada
  além de Megatron/Anrakyr atacava de verdade.
- **Sacrifício central**: `sacrifice()` é o único ponto real do arquivo
  onde algo vai pro cemitério por escolha própria — dispara Scrap
  Trawler, toolbox (Myr Retriever/Junk Diver), Phyrexian Triniform,
  Solemn Simulacrum, e o gatilho passivo do Rakdos, the Muscle
  ("whenever you sacrifice another creature", automático, não é
  escolha). Fodder escolhido via `best_weld_fodder()` (menor MV
  disponível, prioriza sempre criaturas temporárias que iam morrer de
  qualquer jeito) e `best_payoff_fodder()` (só consome fodder "grátis"
  pendente — nunca sacrifica board real por payoff puro, decisão
  documentada de escopo pra manter a heurística simples e segura).
- **Payoffs de sacrifício**: Ayara, Widow of the Realm (`try_ayara`),
  Rakdos, the Muscle (passivo, `rakdos_muscle_trigger`), Altar of the
  Wretched (ETB, dentro de `resolve_etb`), Susur Secundi, Void Altar
  (`try_susur_secundi`, gated por 12+ contadores de carga via Station).
- **Station** (Adagia/Susur Secundi/The Eternity Elevator):
  `try_station_lands` tapa a maior criatura pronta disponível (nunca o
  Megatron) pra gerar contadores; `try_adagia_copy` (12+, copia artefato/
  encantamento) e `try_susur_secundi` (12+, sacrifica criatura por
  compra) consomem os contadores.
- **Ironsoul Enforcer**: "attacks alone" real via `state.attackers_this_combat`
  — agora que todo mundo pode atacar, só dispara quando genuinamente
  sobra 1 criatura pronta no combate (early game ou board reduzido).
- **Fetch/land abilities**: Ash Barrens landcycling (`try_ash_barrens_cycle`),
  Smoldering Marsh condicional (`etb_tapped_check`), Susur Secundi sempre
  tapa (`etb_tapped`).

### Simplificações documentadas (estruturais, não julgamento de valor)

- **Sem oponente real** (mesma convenção de toda a sessão): dano/perda de
  vida direcionado a oponente é proxy agregado, `NUM_OPPONENTS=3` quando
  o oráculo diz "each opponent"; valor único quando diz "target opponent"
  (ex: Starscream-like — aqui não se aplica, mas Warstorm Surge e a
  maioria dos gatilhos de dano ATÉ oponente único não multiplicam).
- **Combate real de verdade pra todo mundo** (revisado 2026-09-02 —
  antes só o Megatron/Anrakyr atacavam, decisão de escopo que um
  goldfish real no Archidekt mostrou estar incompleta: o dano de outros
  atacantes tambem alimenta o pós-combate do Megatron via oráculo
  real, "life your opponents have lost THIS TURN"). Sem bloqueio real
  modelado pra ninguém (nenhum oponente de verdade), então atacar com
  tudo é sempre a jogada correta neste motor.
- **`NO_SELF_HARM_EXCLUDE`**: Blasphemous Act, Decree of Pain, Heartless
  Conscription, Chandra's Ignition — excluídas do auto-cast de propósito
  (mesma convenção já usada pro Blasphemous Act em toda a sessão): sem
  board real de oponente, esses efeitos só machucariam o próprio board
  (Decree/Heartless exilam/destroem TODAS as criaturas incluindo o
  Megatron; Chandra's Ignition acerta "each OTHER creature" que eu
  controlo também). Tags permanecem definidas e documentadas — não são
  fantasmas, é uma decisão estrutural real.
- **Noxious/Combustible Gearhulk "may destroy/mill opponent"**: sem alvo
  real de oponente pra destruir; Combustible assume "oponente nunca
  deixa eu comprar" (premissa documentada, pior escolha pra ele, gera
  dano real via mill). Noxious fica 📊 (sem efeito numérico).
- **Everflowing Chalice**: multikicker paga o máximo de mana sobrando
  (`cast_kickable_chalice`), vira rampa permanente real.
- **Skitterbeam Battalion**: sempre assumido conjurado pelo custo cheio
  ({9}, gera 2 cópias-token reais), nunca a versão Prototype barata —
  mesma convenção de "escolhe sempre a linha de maior valor" já usada
  pro Boros Charm/etc na versão anterior. O "if you cast it" real é
  respeitado (tokens copiando Skitterbeam NÃO retriggam o efeito —
  achado real ao testar, ver seção de bugs abaixo).
- **Daretti, Scrap Savant, emblema do -10**: rastreado como flag
  (`daretti_savant_ultimate_active`) com fila própria
  (`daretti_emblem_pending_return`) que devolve artefatos sacrificados
  no fim do turno — implementado e funcional, validado em testes
  unitários e presente nas métricas do `run_batch` (% de jogos que
  chegam ao -10).

### Bugs reais achados e corrigidos durante a construção (testados, não hipotéticos)

1. **`cast_megatron` nunca disparava** — checava `COMMANDER not in
   state.hand`, mas o comandante corretamente NUNCA entra na mão (vem da
   zona de comando, `BASE_LIBRARY` o exclui de propósito). Resultado:
   Megatron nunca era conjurado em partida nenhuma (100% dos 2.000 jogos
   testados). Corrigido: `cast_megatron` agora só depende de mana/cor,
   não de estar na mão.
2. **Looting descartava terrenos preferencialmente** — a heurística de
   "pior carta" usava só menor mana value; terrenos (MV 0) eram sempre
   "a pior carta", então Faithless Looting/Laughing Mad/limite de mão
   descartavam os próprios terrenos da mão antes de conseguirem ser
   jogados, travando o desenvolvimento de mana da partida inteira (só 2
   terrenos em campo até o turno 6 numa trace de teste). Corrigido com
   `worst_discard_target()`: nunca descarta terreno com menos de 6 em
   campo enquanto houver carta não-terreno pra descartar no lugar.
3. **Recursão infinita real** — Mirrorworks copiando um artefato de
   MV≥3 cria um TOKEN; esse token entrando em campo disparava o próprio
   Mirrorworks de novo (checagem não excluía tokens, mas o oráculo real
   diz "another NONTOKEN artifact"). Corrigido com parâmetro `token`
   propagado por `creature_enters`/`artifact_etb_hooks`. Mesma classe de
   bug no Skitterbeam Battalion (token copiando Skitterbeam recriava 2
   tokens de novo, infinito) — oráculo real diz "if you cast it", tokens
   não foram conjurados; corrigido com o mesmo parâmetro `token`.
4. **`ValueError` em 5 pontos de solda/recuperação** — escolher um alvo
   no cemitério e SÓ DEPOIS sacrificar o fodder cria uma janela real
   onde o próprio sacrifício (gatilho de morte do toolbox Myr Retriever/
   Junk Diver, "return ANOTHER artifact from graveyard to hand") pode
   consumir o mesmo alvo escolhido. Corrigido com guardas defensivas
   (`if target not in state.graveyard: return`) em Goblin Welder, Scrap
   Welder, Trash for Treasure, Goblin Engineer, Daretti -2 e Metalwork
   Colossus.

### Validação

11 testes unitários isolados (1 por mecânica nova: Warstorm Surge,
solda, cheat, sacrifício, Station, Ironsoul "attacks alone", etc.) + 3
rodadas de regressão de 20.000 partidas cada (seeds 1M/2M, turns=10, **0
exceções, 0 timeouts**) + `run_batch` comparando turns=8 vs turns=14
(3.000 jogos cada): todas as métricas do motor escalam de forma real e
não-linear com mais turnos (Daretti chega ao -10 em 3,4%→11,7% dos
jogos, Ayara transforma em 1,5%→10,9%, artefatos sacrificados 2,78→8,90),
consistente com um motor de valor que precisa de tempo pra montar, não
um bug.

---

## Histórico — versão anterior do simulador (motor de fuel, pré-2026-09-02)

As seções abaixo documentam o simulador ANTERIOR (motor "Megatron
sacrifica combustível barato todo turno"), substituído pela reconstrução
acima. Preservadas como registro histórico da evolução do deck — a
lógica descrita não existe mais no arquivo atual.

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov, Hei Bai e Maralen. Rodadas subsequentes de
correção (Plaza of Heroes, Phyrexian Triniform, Bracket 2, reauditoria
completa 2026-09-02 pré-reconstrução) documentadas em `goldfish-log.md`.
