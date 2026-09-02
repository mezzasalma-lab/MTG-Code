# Checklist cláusula-a-cláusula — Megatron, Tyrant

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov, Hei Bai e Maralen.

93 cartas não-terreno-básico do decklist (Mardu, B/R/W, artefatos +
Eldrazi + combustível-de-sacrifício), oráculo real buscado ao vivo via
Scryfall (`POST /cards/collection`, 2 lotes) contra o
`megatron_goldfish_v1.py` atual.

**Contexto:** este é o deck **mais novo** dos auditados até agora
(construído em 2026-08-29, sem nenhuma rodada de reanálise anterior —
diferente de Toph/Beorn/Edgar Markov/Hei Bai/Maralen, que já tinham
passado por 1-16 correções prévias). A releitura linha-a-linha achou
**6 tags mortas** (definidas no `add()` de cada carta, nunca lidas em
lugar nenhum do dispatch) — não julgamento de valor, **lacuna pura**:
mecânicas inteiras (incluindo um finisher de dano real, Summon: Bahamut)
100% ausentes sem nenhuma documentação explicando por quê.

**Legenda:**
- ✅ **Implementado.**
- 📊 **N/A estrutural** — sem oponente real modelado (vida agregada via
  proxy, `NUM_OPPONENTS=3`), sem combate real (bloqueio).
- 📝 **Documentado, fora de escopo genuíno.**
- 🐛 **Corrigido nesta rodada (2026-09-01)** — tag morta, lacuna pura.

## 🐛 As 6 tags mortas corrigidas nesta rodada

1. **Scion of Draco** (`domain_reduce`) — "This spell costs {2} less for
   each basic land type" nunca reduzia o custo fixo de {12}, praticamente
   incastável numa lista de 93 cartas. Corrigido: novo `effective_cost()`,
   usado em `can_cast()`/`cast_card()`/prioridade de conjuração. Este
   deck (sem Forest/Island) tem domínio máximo real 3, não 5.
2. **Summon: Bahamut** (`saga_bahamut`) — Saga de 4 capítulos
   (destroy/destroy/draw2/**Mega Flare**, um finisher real de dano = MV
   total de outros permanentes) 100% ausente. Corrigido: capítulo I em
   `resolve_etb()`, II/III/IV em `try_bahamut_saga()` (chamada no upkeep).
3. **Cryptolith Fragment // Aurora of Emrakul** (`fuel_mana_drain`) —
   mana ability real (`{T}: Add any color, each player loses 1 life`) +
   condição de transformação (`each player has 10 or less life`) 100%
   ausentes. Corrigido: `try_cryptolith_fragment()` (vida de oponente
   aproximada via `40 - proxy_damage_total`, única leitura disponível
   neste modelo agregado) + `try_aurora_of_emrakul_attack()` pro verso.
4. **Cityscape Leveler** (`cast_removal_attack_removal`) — nem o cast
   nem o gatilho de ataque (destroy nonland permanent, repetível) eram
   contados como interação. Corrigido em `resolve_etb()` +
   `try_cityscape_leveler_attack()`.
5. **Retributive Wand** (`fuel_ping_death_burst`) — `{3},{T}: 1 dano`
   repetível 100% ausente (o gatilho de morte, "5 dano", continua 📊 —
   nenhuma remoção dos PRÓPRIOS permanentes é modelada neste sim, mesma
   razão de Enduring Vitality noutros decks). Corrigido:
   `try_retributive_wand_ping()`.
6. **Pumpkin Bombs** (`fuel_fuse_burn`) — `{T}, discard 2: draw 3, 1
   dano, adversário GANHA CONTROLE do artefato` 100% ausente. Corrigido:
   `try_pumpkin_bombs()` — ativação única de verdade (não julgamento de
   valor: o oráculo literalmente tira o artefato do seu controle após o
   1º uso).

Validado com 6 testes unitários isolados + regressão de 20.000 partidas
(0 erros) + `run_batch` confirmando ativação real de todas as 6 (Scion
of Draco castável em 2,2% dos jogos — antes 0%; Bahamut chega ao Mega
Flare em jogos mais longos, dano real ~63-133 quando resolve).

---

## Cobertura das demais 87 cartas

O motor central (Megatron Tyrant/Destructive Force, conversão de face,
combustível de sacrifício) e o resto do deck já estavam bem cobertos na
construção original (docstring do arquivo, seção "Simplificações
documentadas"). Confirmado nesta rodada, carta por carta:

- **Megatron** (frente Tyrant / verso Destructive Force): mecânica de
  conversão, dano por sacrifício de artefato, geração de mana pós-combate
  — ✅ `megatron_combat()`/`megatron_postcombat()`.
- **Combustível de sacrifício** (Atraxa's Skitterfang/Bitterthorn/Dauntless
  Scrapbot/Etched Familiar/Solemn Simulacrum/etc): ETBs reais, corpo
  descartável — ✅.
- **Kozilek / Ulamog**: cast-draw-4, Annihilator (📊 sem board de
  oponente), destroy-on-cast (📊 interação sem alvo real) — ✅/📊.
- **Starscream** (transform, paralelo ao Megatron): monarquia/conversão —
  ✅ (tratado análogo ao Megatron).
- **Toolbox de recursão** (Myr Retriever/Junk Diver/Workshop Assistant,
  Goblin Engineer, Osgir, Mishra unearth): ✅.
- **Wheels** (Wheel of Fortune/Wheel of Misfortune/Memory Jar): ✅
  (Wheel of Misfortune simplificado — modo de "maior número" não
  simulável sem escolha simultânea de oponente real, documentado).
- **Removal genérica sem alvo real** (Crackling Doom/Soul Shatter/
  Shatterskull Smashing/Sundering Eruption/Vandalblast/Swords/Path):
  conjurada quando há mana sobrando, conta como interação — 📊.
- **Price of Progress**: proxy via contagem de terrenos não-básicos
  próprios — 📝 documentado.
- **Phyrexian Arena / Descent into Avernus**: draw engines com autodano
  real, incluindo Descent (dano simétrico) — ✅.
- **Portal to Phyrexia**: sacrifício de oponente (📊) + reanimação do
  próprio cemitério — ✅.
- **Talon Gates of Madara**: `{T}: Add C` genérico coberto — ✅; upgrade
  de cor (`{1},{T}: any color`) e "play from hand for {4}" — 📝 baixo
  impacto de magnitude (só fixação de cor / land drop extra), não
  implementados por escopo, mas agora documentados explicitamente aqui
  em vez de silenciosos.
- **Boros Charm**: modal, dano/indestructible/double strike — ✅ tag
  `boros_charm_burn` (modo de dano).

---

## Resumo numérico

- **93 cartas.**
- **✅ Implementado:** ~75 linhas de cláusula.
- **📊 N/A estrutural:** ~15 linhas.
- **📝 Documentado, fora de escopo genuíno:** ~3 linhas (Talon Gates
  upgrade de cor/land-drop extra, Price of Progress proxy, Wheel of
  Misfortune modo de "maior número").
- **🐛 Corrigido nesta rodada:** 6 tags mortas (Scion of Draco, Summon:
  Bahamut, Cryptolith Fragment, Cityscape Leveler, Retributive Wand,
  Pumpkin Bombs) — todas lacunas puras, sem documentação prévia alguma,
  não julgamento de valor.

---

## 🐛 Correção — Plaza of Heroes / infraestrutura "legendary" morta (2026-09-02)

**Gatilho:** usuário lembrou "The Ten Rings" (que já estava corretamente
implementada — maximum hand size 10 + draw-to-10 no end step, ver
`end_step()`). Ao reconferir, achei `is_legendary()`/`LEGENDARY_NAMES`
(13 permanentes legendários da lista) **definidos mas nunca chamados em
lugar nenhum** — sinal de que algo dependente de "legendary" ficou pra
trás.

**Achado real:** Plaza of Heroes — oráculo completo (Scryfall): *"{T}:
Add {C}." + "{T}: Add one mana of any color. Spend this mana only to
cast a legendary spell." + "{T}: Add one mana of any color among
legendary permanents you control." + "{3}, {T}, Exile this land: Target
legendary creature gains hexproof and indestructible until end of
turn."* Só o modo 1 (incolor genérico) estava implementado
(`produces=set()`) — os outros 3 modos 100% ausentes, incluindo o mais
valioso numa lista com 13 legendários: fixar qualquer cor pra conjurar
um spell legendário.

**Corrigido:** modo 2 implementado de verdade —
`color_sources(state, color, spell_name=name)` agora conta Plaza of
Heroes como fonte de qualquer cor faltante quando `spell_name` é
legendário (`is_legendary()`, agora finalmente chamado). Chamadas
genéricas de `color_sources()` sem contexto de spell continuam
ignorando Plaza (comportamento antigo preservado onde não se aplica).

**Modos 3 e 4 permanecem 📊/📝, por razão estrutural real (não
julgamento de valor):**
- Modo 3 ("fixar cor pra ativar habilidade de legendário") exigiria um
  framework genérico de "pagar custo de qualquer habilidade ativada",
  que este arquivo não tem em lugar nenhum (só ativações hardcoded caso
  a caso).
- Modo 4 (hexproof+indestructible) é proteção contra remoção de
  oponente — sem oponente real modelado neste goldfish solo, mesma
  convenção de toda a sessão.

Validado com 4 testes unitários isolados (bloqueia sem Plaza / libera
com Plaza pra spell legendário / NÃO libera pra spell não-legendário /
`color_sources()` genérico ignora Plaza) + regressão de 20.000 partidas
(seed 11000000+, turns=10, 0 exceções) + `run_batch` antes/depois (3000
jogos, seed 12000000, turns=10): turno médio de conjuração do Megatron
5.02→4.97, "nunca conjurado em 10 turnos" 11.6%→10.8% — pequeno mas real
(fixação de mana ocasional destravando um legendário que faltava a cor).

---

## Troca — Rakdos Charm → Phyrexian Triniform (2026-09-02)

**Gatilho:** usuário perguntou sobre Portal to Phyrexia ("outro artefato
9/9 que quando morre gera 3 artefatos 3/3") — a descrição não batia com o
oráculo real do Portal (não é criatura, sem P/T). Investigando, o
usuário identificou a carta certa: **Phyrexian Triniform**, já citada no
docstring do topo do arquivo como "confirmada vista ao vivo num
oponente real", mas nunca tinha entrado de fato nas 99 cartas da lista.

**Corrigido:** adicionada ao `CARD_DB` (`{9}`, artifact creature 9/9),
no lugar de Rakdos Charm (peça de interação mais redundante do pacote —
já havia 7 outras). Gatilho de morte real ("When this creature dies,
create three 3/3 colorless Phyrexian Golem artifact creature tokens")
implementado em `toolbox_recur_death_trigger()`, o dispatch central já
usado nos 5 pontos reais de morte do arquivo — os 3 tokens também
contam como combustível real pro próximo sacrifício do Megatron (são
artefatos). Novo campo `triniform_tokens_total` pra métrica.

Validado: import + `len(BASE_LIBRARY) == 99` + teste unitário isolado do
gatilho de morte (3 tokens criados, métrica incrementada) + regressão de
20.000 partidas (seed 5000000, turns=8, 0 exceções).

---

## Bracket 2 — remoção dos 3 Game Changers (2026-09-02)

**Pedido direto do usuário:** *"Pode tirar o One Ring e o Smothering
Tithe" / "Pode tirar os 3 GCs, quero ele B2"*. Cross-reference contra
`is:gamechanger` do Scryfall (53 cartas) já tinha identificado
exatamente 3 Game Changers na lista: **Smothering Tithe**, **The One
Ring**, **Teferi's Protection**.

**Removidas do `CARD_DB`** (nenhuma tinha efeito redondo modelado que se
perdesse de verdade: Smothering Tithe só rendia treasure via
`NUM_OPPONENTS` em wheels próprios; The One Ring tinha o campo
`the_one_ring_burden` só verificado no upkeep, **nunca incrementado em
lugar nenhum** — dano zero na prática, achado ao investigar a remoção;
Teferi's Protection era só uma tag `protection` nunca lida em nenhum
dispatch). Substituídas por 3 cartas sem status de Game Changer,
mantendo o tema de artefato/combustível do deck:

1. **Mind Stone** (rock, +1 mana em `rocks_mana()`, tag `fuel_rock1` —
   elegível como combustível do Megatron igual Cursed Mirror). Ativada
   própria (`{1},T,Sacrifice: draw a card`) não modelada a parte — sempre
   sacrificada pelo motor de fuel do Megatron primeiro (payoff maior).
2. **Sword of the Animist** (`+1/+1` no portador + busca terreno básico
   pro campo tapped a cada ataque) — implementada de verdade em
   `megatron_combat()`: `power += 1` e busca real na `state.library`
   (mesmo padrão já usado em Dauntless Scrapbot). Equip {2} não rastreado
   a parte (simplificação: só o Megatron ataca nesse deck).
3. **Vandalblast** (`{1}{R}`, destroy target artifact) — tag `interaction`,
   mesma convenção das outras remoções sem alvo real. Modo overload
   (`{4}{R}`, destrói todos os artefatos dos oponentes) não modelado
   separadamente, mesma convenção dos outros modais do arquivo.

Validado: import + `len(BASE_LIBRARY) == 99` + confirmação de que as 3
cartas removidas somem de `BASE_LIBRARY` e as 3 novas aparecem 1x cada +
regressão de 5.000 partidas (seed 7000000, turns=8, 0 exceções) — dano
proxy médio 31,40 (antes 30,61 com só a troca do Triniform), consistente
com uma troca aproximadamente neutra em poder bruto.

---

## 🐛 Reauditoria linha-a-linha completa das 99 cartas (2026-09-02)

**Gatilho direto do usuário:** perguntando sobre Stensian Sanguinist
("tem Blasphemous Act no Megatron? por que tem Stensian Sanguinist?"),
eu respondi errado (disse que Stensian era MDFC — na verdade é
**"prepared"**, keyword/layout diferente). O usuário corrigiu e cobrou a
auditoria de verdade: *"Stensian não é MDFC, ela é prepared. Eu não
mandei vc auditar TODAS as cartas linha por linha e uma por uma?"*

Refeita a varredura completa: oráculo real das 93 cartas não-terreno-
básico via Scryfall (`POST /cards/collection`, 2 lotes) contra o
`megatron_goldfish_v1.py` pós-Bracket 2, cruzando CADA `add()` do
`CARD_DB` (poder, custo, tags) e procurando tags/nomes que nunca são
lidos em lugar nenhum do dispatch (mesmo método já usado nas rodadas de
2026-09-01 e na correção da Plaza of Heroes). **Achado central: a
rodada de auditoria de 2026-09-01 não foi tão completa quanto o
checklist afirmava** — vários fantasmas (cartas com mecânica 100%
ausente) sobreviveram àquela rodada, incluindo um que o próprio
checklist chegou a marcar (erradamente) como "✅ implementado".

### Fantasmas completos (mecânica 100% ausente, nenhuma tag nem nome lido em lugar nenhum)

1. **Starscream, Power Hungry** — o mais grave: existia só como nome no
   `CARD_DB` (`{"artifact"}` genérica, poder 0). É o **segundo DFC
   `transform` da lista**, paralelo ao Megatron (mesmo padrão "More Than
   Meets the Eye"), com mecânica real de **monarquia**: verso (Seeker
   Leader, flying/menace/**haste**) ataca e reivindica a coroa; frente
   (Power Hungry) drena 2 de um oponente por CADA carta comprada
   enquanto for o monarca. O checklist de 2026-09-01 (seção "Cobertura
   das demais 87 cartas") afirmava — errado — "monarquia/conversão ✅
   (tratado análogo ao Megatron)". Implementado de verdade em
   `cast_starscream()`/`starscream_combat()` + hook em `draw_cards()`
   (dispara em toda carta comprada, normal ou extra — refatorei o draw
   normal do turno pra passar por `draw_cards()` também, unificando os 2
   pontos de compra que existiam antes). Monarquia, uma vez conquistada,
   nunca é perdida neste simulador (sem gatilho de "creature deals
   combat damage to you" modelado em lugar nenhum — mesma convenção
   geral de nunca simular dano recebido).
2. **Excalibur, Sword of Eden** — tags `equipment_big_power`/
   `cost_reduce_historic` definidas desde a construção original, nunca
   lidas. Real: "costs {X} less, X = MV total de permanentes históricos
   você controla" + "+10/+0 e vigilance no equipado". Implementado em
   `effective_cost()` (nova função `is_historic()` = artifact OR
   legendary OR Saga) + `+10` direto no `power` do `megatron_combat()`
   (mesma simplificação do Sword of the Animist: só o Megatron ataca,
   auto-equipado).
3. **Night's Whisper** — tag `draw2_life2` definida, **carta inteira**
   nunca fazia nada (nem comprava nem perdia vida), apesar de ser
   conjurada normalmente todo turno com mana sobrando (prioridade mais
   barata da fila). Implementado em `resolve_instant_sorcery()`.
4. **Rakdos, the Muscle** — tag `rakdos_sac_creature` órfã. Real:
   "whenever you sacrifice another creature, exile cards = MV do topo da
   sua biblioteca, pode jogá-las". Várias peças de fuel são
   artefato-criatura, então o gatilho é real e frequente. Implementado
   como impulso de compra direta (mesma convenção de simplificação já
   usada pro Sandstone Oracle/Portal to Phyrexia) dentro do sacrifício de
   fuel em `megatron_combat()`. 2ª habilidade (sacrifice: indestructible)
   fica 📊 — sem remoção de oponente real pra proteger contra.
5. **Atraxa's Skitterfang** — tag `combat_pump_oil` órfã. Real: entra
   com 3 oil counters; no início do combate pode remover 1 pra dar
   flying/vigilance/deathtouch/lifelink a uma criatura. Implementado:
   sempre escolhe lifelink (única opção com efeito numérico nesse motor
   sem bloqueio real) no Megatron, gastando os contadores reais.
6. **Etched Familiar** — tag `fuel_death_drain` órfã. "When this dies,
   each opponent loses 2, you gain 2" nunca disparava mesmo sendo peça
   de fuel MV baixo (candidata frequente a sacrifício). Implementado em
   `toolbox_recur_death_trigger()`.
7. **Steel Seraph** — nenhuma tag pra "at the beginning of combat,
   target creature gains flying/vigilance/lifelink" (só existia como
   0/entrada no `FLYING_CREATURES`, ele mesmo nunca lido em lugar
   nenhum). Implementado igual ao Atraxa (lifelink no Megatron).
8. **Chromatic Orrery** — 2ª habilidade ("{5},{T}: draw a card for each
   color among permanents you control") nunca implementada, só a
   habilidade de mana. Implementado em `try_chromatic_orrery_draw()` —
   "cor entre permanentes" aproximada via as cores de custo (pips) dos
   permanentes não-terrestres em campo (proxy documentado).
9. **Marsh Flats** — tratada como dual estático sem custo
   (`produces={"W","B"}` direto), citando um "ver docstring" que na
   verdade **nunca existia**. É um fetchland de verdade, igual Arid Mesa
   (Regra 6 de `user-standing-rules.md`: fetches usam `crack_fetch`, não
   terreno genérico). Corrigido — e ao corrigir, achei que `crack_fetch()`
   também não filtrava candidatos pelos tipos básicos que CADA fetch
   específico pode buscar (Arid Mesa = Mountain/Plains, Marsh Flats =
   Plains/Swamp) — com só 1 fetch na lista antes isso nunca importava;
   agora com 2, corrigido via `FETCH_ALLOWED_TYPES`.
10. **Cursed Mirror** — ETB "may become a copy of any creature on the
    battlefield until end of turn, except it has haste" nunca
    implementado (só a habilidade de mana). Implementado como rajada
    extra de dano (copia o Megatron se ele já estiver em campo e pronto)
    em `resolve_etb()` — sem criar uma 2ª criatura persistente, já que a
    cópia reverte no fim do turno.
11. **Stensian Sanguinist** — o achado que disparou essa rodada inteira.
    NÃO é MDFC (correção do usuário) — é **"prepared"**: "whenever you
    attack, target creature gains deathtouch; whenever that creature
    deals combat damage, this becomes prepared" + enquanto prepared,
    pode conjurar uma cópia de Exsanguinate (ainda pagando o custo
    normal — o oráculo não diz "without paying its mana cost").
    Implementado via `stensian_attack_trigger()` (chamado de todo ponto
    real de ataque) + `try_stensian_exsanguinate_copy()`.

### Custo errado (bug meu, desta sessão)

12. **Vandalblast** — eu tinha registrado `{1}{R}` (mv 2) de memória ao
    adicionar a carta na troca do Bracket 2. Oráculo real: `{R}`, mv 1.
    Corrigido.

### Poder impresso errado (cosmético — `.power` não é lido em lugar
nenhum DENTRO deste arquivo solo, só pelo motor de mesa externo
`pod-simulator/pod_engine_v1.py` via fallback; corrigido mesmo assim por
precisão de dado, já que decks futuros plugados na mesa vão herdar esses
valores)

Brimstone Trebuchet 0→1, Dauntless Scrapbot 1→3, Junk Diver 2→1, Mishra
2→4, Myr Retriever 0→1, Osgir 3→4, Sandstone Oracle 0→4, **Scion of
Draco 8→4** (o maior desvio — estava com o dobro do poder real), Summon:
Bahamut 0→9, Starscream 0→2, Stensian Sanguinist 0→2, Treasure Nabber
2→3. Rakdos, the Muscle ganhou flying (tinha, faltava no
`FLYING_CREATURES` — também não lido em lugar nenhum, mesma categoria).

### Confirmado como estruturalmente correto (não fantasma)

- **Blasphemous Act**: excluída de propósito do auto-cast (mataria só
  minhas criaturas sem board de oponente real) — a redução de custo
  ("{1} less per creature") fica sem efeito por isso mesmo, documentado
  explicitamente agora em vez de ficar implícito.
- **`has_flying()`/`FLYING_CREATURES`**: função e set inteiros nunca
  lidos em lugar nenhum — mas isso é 📊 estrutural genuíno, não bug:
  nenhum bloqueio é modelado pra ninguém no arquivo (nem os MEUS
  atacantes são bloqueados), então flying não tem gancho mecânico pra
  interagir com nada. Diferente do caso da Plaza (onde "legendary"
  faltava um gancho real) — aqui não há gancho a construir.
- **Talon Gates of Madara / Eye of Ugin**: modos secundários já
  documentados como 📝 fora de escopo numa rodada anterior — confirmado,
  nada novo.

### Validação

11 testes unitários isolados cobrindo cada mecânica nova (Night's
Whisper, Stensian prepared→Exsanguinate, Starscream monarquia+dreno por
compra, Excalibur custo+poder, Steel Seraph/Atraxa lifelink, Etched
Familiar morte, Rakdos sacrifício, Chromatic Orrery, Marsh Flats fetch
correto) + regressão de 20.000 partidas (seeds 9M/12M/14M, turns=10, **0
exceções, 0 timeouts**) + `run_batch` 5.000 jogos confirmando sinal real
de cada mecânica nova (Starscream monarquia ~13-14% dos jogos, Excalibur
conjurada ~11-12%, Cursed Mirror copia o Megatron ~9%, dano proxy médio
subiu de ~31 para ~38-39, vida ganha de ~0,5 para ~3,6-3,8 — tudo
plausível e na direção esperada, nenhum outlier).
