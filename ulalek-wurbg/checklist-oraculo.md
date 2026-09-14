# Checklist cláusula-a-cláusula — Ulalek, Fused Atrocity

## Achado real 2026-09-14 (usuário perguntou se Roaming Throne está certa em todos os decks onde aparece)

Mesma varredura pedida depois dos fixes no Beorn/Edgar Markov/Ur-Dragon.
Este deck (tribal Eldrazi, `ROAMING_THRONE_TYPE = "eldrazi"`) já tinha a
dobra do gatilho corretamente implementada como função central
(checando o tipo da FONTE do gatilho, não do que entrou — mesmo padrão
certo do Ur-Dragon/Maralen). Achado real: **Spawnbed Protector** ("At the
beginning of your end step, return up to one target **Eldrazi creature
card** from your graveyard to your hand") aceitava Roaming Throne como
alvo válido se ela estivesse no cemitério — mas o tipo Eldrazi que ela
ganha ("as this creature enters, choose a creature type") é um efeito de
ETB, não uma característica que persiste em outras zonas (diferente de
Changeling) — uma Roaming Throne morta no cemitério não é mais "an
Eldrazi creature card".

**Corrigido:** novo helper `is_eldrazi_card(name)` (= `is_eldrazi(name)
and name != "Roaming Throne"`), usado só no Spawnbed Protector.
`is_eldrazi()` puro continua correto pras checagens de battlefield
(inalterado).

**Validação:** 2 testes unitários dirigidos (Spawnbed Protector recupera
um Eldrazi real do cemitério ignorando Roaming Throne; sem Eldrazi real
no cemitério, não recupera Roaming Throne como substituto) — passando.
Batch de 2.000 partidas: `spawnbed_protector_recursion_total` já estava
em 0,0 na seed testada antes E depois (evento raro o bastante — Spawnbed
Protector em campo + Eldrazi real no cemitério simultaneamente — pra não
aparecer em 2.000 jogos nessa seed específica; a correção é real e
comprovada pelos testes unitários, só não muda a média agregada aqui).
20.000 partidas de regressão (seed 8200000+), **0 exceções**.

---

## Auditoria oráculo-por-oráculo completa — 2026-09-14

Extensão pra este deck da mesma auditoria já feita em Beorn/Captain
Storm/Edgar Markov/Hei Bai/Maralen/Megatron/Nekusar/Prismatic Bridge/Rat
King/Thranduil (13 decks no total). Este deck já tinha passado por **2
rodadas anteriores** (2026-08-28 e 2026-08-30/31/09-01, ver seção acima)
com vários "achado real" documentados — mesmo assim, a releitura
linha-a-linha completa desta rodada (oráculo real de todas as 84 cartas
únicas + terrenos, buscado ao vivo via Scryfall, cruzado clausula-a-
clausula contra o código) achou **5 gaps reais adicionais**.

**5 gaps reais encontrados e corrigidos:**

1. **Farseek/Nature's Lore/Three Visits buscavam terreno SEM a restrição
   real de tipo.** As 3 compartilhavam a mesma tag `land_tutor1` tratada
   como "busca qualquer um dos 37 terrenos da lista" — mas o oráculo real
   restringe cada uma: Farseek = *"Search your library for a **Plains,
   Island, Swamp, or Mountain** card"*; Nature's Lore/Three Visits =
   *"Search your library for a **Forest** card"*. Esta decklist não tem
   nenhum básico Plains/Island/Swamp/Mountain/Forest — só os terrenos
   duais ABUR têm os subtipos básicos reais (confirmado via
   `type_line` do Scryfall, não presumido): **Farseek** aceita os 10
   duais ABUR (cada um tem pelo menos um dos 4 tipos — ex: Badlands é
   Swamp Mountain); **Nature's Lore/Three Visits** só aceitam os 4 com
   subtipo Forest (Bayou, Savannah, Taiga, Tropical Island). O código
   anterior podia "buscar" qualquer terreno da lista, incluindo
   utilitários como Ancient Tomb/Command Tower/Eye of Ugin — nenhum dos
   quais é um alvo legal real pra nenhuma das 3. Corrigido com
   `FARSEEK_TARGETS`/`FOREST_TYPE_TARGETS` dedicados.
2. **Farseek também não marcava o terreno buscado como tapped**, mesmo
   padrão exato já achado no Beorn (Cultivate/Sakura-Tribe Elder/etc):
   oráculo real diz *"put it onto the battlefield **tapped**"*, mas o
   terreno buscado produzia mana no MESMO turno (mana fantasma).
   Nature's Lore/Three Visits, por contraste, genuinamente NÃO têm
   "tapped" no oráculo (fetches premium clássicos) — corrigido só pra
   Farseek, com um contador novo por turno
   (`tapped_phantom_mana_this_turn`, deduzido em `total_mana()`).
3. **`ctype == "creature"` estrito (não `is_creature_card()`/
   `CREATURE_ISH`) excluía artifact creature em 4 lugares do arquivo** —
   2 com impacto real em jogo: (a) o dispatch de **Kozilek's Unsealing**
   ("creature spell MV 4-6/7+") nunca disparava pra Roaming Throne
   (artifact creature, MV4 — cai na faixa 4-6, mas `ctype` real é
   `"artifact_creature"` ≠ `"creature"`); (b) o desconto real "the first
   creature spell you cast each turn costs {2} less" (Conduit of
   Ruin/Radagast) nunca se aplicava a Roaming Throne (MV4) nem Liberator,
   Urza's Battlethopter (MV3) pelo mesmo motivo. Corrigido nos 4 lugares
   (2 deles sem impacto observável nesta decklist específica, mas
   corrigidos por correção/consistência).
4. **Writhing Chrysalis** — "Whenever you sacrifice another Eldrazi, put
   a +1/+1 counter on this creature" 100% ausente (só o cast-trigger
   "cria 2 spawn tokens" estava implementado). Eldrazi Spawn/Eldrazi
   Scion tokens SÃO Eldrazi de verdade (tipo real da carta, confirmado
   via Scryfall) e são sacrificados por mana o tempo todo neste motor
   (`sac_spawns_for_mana()`, chamada todo turno) — um gatilho que deveria
   disparar com bastante frequência num deck deste perfil nunca existia.
   Corrigido: tag `"eldrazi"` adicionada ao token, contador agregado
   `writhing_chrysalis_counters_total` incrementado a cada sacrifício
   (mesma convenção do Ruins of Oran-Rief — sem P/T por criatura
   individual neste modelo).
5. **Spawning Bed** ("{6}, {T}, Sacrifice this land: Create three 1/1
   colorless Eldrazi Scion creature tokens") ficou de fora da correção
   de 2026-09-01 que resgatou Eye of Ugin/Urza's Cave/Ruins of Oran-Rief
   do mesmo loop genérico de 34 terrenos — 100% ausente até agora.
   Corrigido com `try_spawning_bed()`, guardado por `lands_in_play() > 7`
   (trocar uma fonte de mana PERMANENTE por 3 fontes de uso único é uma
   troca ruim na maioria dos casos — só ativa com excedente real de
   terrenos, heurística documentada inline).

**Bônus (mesmo padrão de alt-cost já usado pro Warp da Anticausal
Vestige, mas achado numa carta diferente): Nulldrifter tem Evoke {2}{U}**
— 100% ausente, sempre pagava o custo cheio de 7. Como este simulador não
modela combate (0 ocorrências de "annihilator"/"attack" no arquivo
inteiro antes desta rodada), o corpo 7/7 voador com annihilator nunca
produzia nenhum efeito numérico aqui — o cast-trigger real ("draw two
cards") dispara igual via evoke, então evocar é estritamente mais barato
(3 mana genérica vs. 7) pelo mesmo valor modelado. Corrigido com
`EVOKE_COST`/`evoke_mode`, sempre evocado da mão (mesma heurística greedy
já documentada pro Warp).

**Validação:** smoke test (103 nomes no `CARD_DB` incluindo tokens
sintéticos e o Radagast de teste comparativo, 99 cartas na
`BASE_LIBRARY`, 0 desconhecidas/duplicatas) + 5 testes unitários
dirigidos isolados (1 por correção, todos confirmando o comportamento
ANTES incorreto e DEPOIS correto) + `run_batch` antes/depois via
`importlib`+`git stash` (2000 jogos, seed 6000000, turns=8) + regressão
de 20.000 partidas (seed 9100000, turns=8), 0 exceções em ambas. Métricas
se moveram na direção esperada sem nenhum salto inexplicável — ver
`goldfish-log.md` pra tabela completa.

---


Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King e Thranduil.

**Contexto importante:** este simulador já tinha passado por 2 rodadas de
auditoria completa de oráculo antes desta (2026-08-28 e 2026-08-30,
documentadas extensivamente no docstring do cabeçalho e em
`goldfish-log.md`), incluindo correções reais como Forsaken Monument's
mana doubling, Sanctum of Ugin, Emrakul's graveyard cost reduction, os
8 painlands faltando em `TRUE_C_LANDS`, etc.

**Método:** detecção automatizada de (a) tags definidas em `add()` nunca
lidas em dispatch e (b) nomes de carta que só aparecem em `add()`+
`DECKLIST_TEXT`. ~39 candidatos apareceram no total; a esmagadora maioria
eram falsos positivos porque este arquivo mistura 3 convenções de
dispatch diferentes:
- Tabela de tag→função pros cast-triggers dos titãs Eldrazi
  (`CT_TRIGGERS`: Kozilek x3, Ulamog x2, Emrakul, Flayer, Conduit,
  Nulldrifter, Sowing Mycospawn, Writhing Chrysalis) — todos corretos.
- Checagem de nome direta dentro de funções compartilhadas
  (`eldrazi_cost_discount()` cobre Urza's Incubator, It That Heralds the
  End, Eye of Ugin's estática, Emrakul's redução por tipo em cemitério;
  `on_colorless_creature_etb()` cobre Glaring Fleshraker) — todos
  corretos.
- Tag genérica `"interaction"` pra toda a pacote de remoção/contramagia
  (Swords to Plowshares, Toxic Deluge, Beast Within, Swan Song, etc.) —
  tratadas como proxy (conjuráveis, sem alvo de oponente real), consistente
  com o resto da sessão.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real, sem combate/P-T por criatura
  individual, ou sem modelo de mana pip-a-pip — limite conhecido, não
  julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 Os 3 gaps corrigidos nesta rodada

Todos em terrenos que estavam registrados genericamente dentro de um
loop de 34 terrenos (`add(n, 0, "land", {"colorless"})`) — só a mana
{C} básica coberta, nenhuma habilidade adicional real.

1. **Eye of Ugin** — a redução estática ("Colorless Eldrazi spells you
   cast cost {2} less") já era coberta por nome em
   `eldrazi_cost_discount()` desde 2026-08-28/30. Faltava a ativada real:
   *"{7}, {T}: Search your library for a colorless creature card, reveal
   it, put it into your hand, then shuffle."* O próprio docstring já
   documentava isso como deferido ("2 habilidades ativadas a mais, ficam
   pra uma rodada dedicada"). Corrigido com `try_eye_of_ugin()` — 1x por
   turno, tutora a criatura colorless de maior MV disponível.
2. **Urza's Cave** — *"{3}, {T}, Sacrifice this land: Search your library
   for a land card, put it onto the battlefield tapped, then shuffle."*
   100% ausente (mesma nota de deferimento do docstring). Corrigido com
   `try_urzas_cave()` — busca Ancient Tomb (maior valor: {C}{C}) se ainda
   estiver na biblioteca, senão qualquer terreno disponível. Uso único
   por partida (a própria habilidade sacrifica o terreno).
3. **Ruins of Oran-Rief** — 2ª habilidade real *"{T}: Put a +1/+1 counter
   on target colorless creature that entered this turn"* (mutuamente
   exclusiva com o modo de mana {C} básica, mesmo `{T}`) nunca
   implementada — só o modo de mana genérica estava coberto (contado
   dentro do loop de 34 terrenos). Corrigido com `try_ruins_oran_rief()`,
   contador agregado (este modelo não rastreia P/T por criatura
   individual). Simplificação documentada: só dispara pra criaturas
   conjuradas via `resolve_cast`/`creature_etb_hooks` nesse turno, não
   cobre tokens Spawn/Scion/Manifest criados fora desse fluxo específico
   (este arquivo não centraliza toda criação de token num único ponto de
   entrada).

**Reclassificação de linguagem (não um bug, correção de fraseado):** o
comentário do cabeçalho sobre Void Grafter/Liberator/Ruins of Oran-Rief
dizia *"presentes na decklist mas sem efeito numérico relevante pro
goldfish"* — fraseado próximo do "julgamento de valor" que o pedido do
usuário proíbe. Reescrito com a razão estrutural real por carta: Void
Grafter (sem oponente/remoção real modelada pra proteger contra — 📊
genuíno), Liberator (exigiria comparar o power dele contador-a-contador
contra cada gasto de mana futuro — mesmo limite de "sem P/T por criatura"
já documentado no resto do arquivo, não um recorte específico desta
carta).

Validado com 6 testes unitários isolados + regressão de 20.000 partidas
(seed 3000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 6000000, turns=10): tutores usados
0.60→0.70, RAMP 2.33→2.52, Urza's Cave ativado em 17.0% dos jogos, Ruins
of Oran-Rief avg 0.66 contadores/partida.

## Falsos positivos descartados (já corretamente implementados)

- **Kozilek/Ulamog/Emrakul (todas as variantes) + Flayer of
  Loyalties/Conduit of Ruin/Nulldrifter/Sowing Mycospawn/Writhing
  Chrysalis** — cast-triggers reais dispatchados via `CT_TRIGGERS`
  (tag→função), não por nome — meu primeiro método de detecção (contagem
  de ocorrência de nome) apontou falso positivo, corrigido cruzando com
  a tabela de dispatch real.
- **Urza's Incubator, It That Heralds the End** — cost reduction
  estática já implementada por nome dentro de `eldrazi_cost_discount()`.
- **Sanctum of Ugin** — já implementado desde 2026-08-28 (mill-trigger
  gratuito ao conjurar spell colorless MV7+, `on_any_spell_cast_hooks`).
- **Rhystic Study, Sire of Stagnation, Defense of the Heart** —
  genuinamente opponent-dependent (gatilhos exigem ação do oponente), 📊
  consistente com o resto da sessão.
- **Sire of Seven Deaths** — só keywords de combate (reach/first
  strike/vigilance/menace/trample/lifelink/ward), sem gatilho numérico —
  nada a implementar.
- **Morophon, the Boundless** — não é órfã de tag (tags só `{"colorless"}`,
  sem tag própria); redução "{W}{U}{B}{R}{G} less" e anthem "+1/+1"
  ambas 📊 estruturais: este arquivo não modela custo por pip de cor
  (mana pool fungível única, sem rastreio WUBRG) nem P/T por criatura.

---

## Resumo numérico

- **~100 cartas na lista** (comandante + biblioteca, incluindo os 34
  terrenos genéricos + Ancient Tomb).
- **🐛 Corrigido nesta rodada:** 3 cartas (Eye of Ugin, Urza's Cave,
  Ruins of Oran-Rief).
- **✅ Falsos positivos descartados (já implementados corretamente,
  métodos de dispatch diferentes do esperado pela varredura inicial):**
  11 cartas/grupos (Kozilek x3, Ulamog x2, Emrakul, Flayer, Conduit,
  Nulldrifter, Sowing Mycospawn, Writhing Chrysalis, Urza's Incubator, It
  That Heralds the End, Sanctum of Ugin).
- **📊 Estrutural confirmado:** Rhystic Study, Sire of Stagnation, Defense
  of the Heart (opponent-dependent), Sire of Seven Deaths (combate puro),
  Morophon (sem modelo de pip de cor / sem P/T por criatura), Void
  Grafter, Liberator.
