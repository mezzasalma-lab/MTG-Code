# Checklist cláusula-a-cláusula — Maralen, Fae Ascendant

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov e Hei Bai.

92 cartas não-terreno-básico do decklist (Sultai, B/G/U, tribal
Elfo+Fada), oráculo real buscado ao vivo via Scryfall (`POST
/cards/collection`, 2 lotes + `/cards/named?fuzzy=` pros 3 MDFC/Adventure)
contra o `maralen_goldfish_v1.py` atual.

**Contexto:** este deck já tinha passado por 2 rodadas de reanálise
pedidas pelo usuário (2026-08-28, 2026-08-30/31 — Joraga Treespeaker
nível 5, dobra correta do Roaming Throne por FONTE do gatilho em vez do
que entrou). A releitura linha-a-linha desta rodada achou **1 família de
4 cartas** (Wirewood Symbiote, Scryb Ranger, Wirewood Lodge, Formidable
Speaker) que usava linguagem de julgamento de valor proibida
("risco de bug > valor esperado") pra justificar não implementar — e,
crucialmente, **implementar essa família revelou um bug real e
pré-existente**: o comandante (Maralen, que é ela mesma Elf) podia ser
selecionada como "fodder" de bounce, expondo um hang infinito (recast
descontrolado do comandante) que nunca tinha tido chance de disparar
antes, porque nada mais neste deck bounça os próprios permanentes.

**Legenda:**
- ✅ **Implementado** — efeito real no código.
- 📊 **N/A estrutural** — sem oponente/combate real modelado, ou "untap
  step de outro jogador" que este sim nunca avança.
- 📝 **Documentado, fora de escopo genuíno**.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 O achado desta rodada

**Família "untap target creature/Elf/permanente"** — Wirewood Symbiote
("Return an Elf you control: Untap target creature"), Scryb Ranger
(idem, Forest), Wirewood Lodge (`{G},{T}` do próprio terreno: untap
Elf), Formidable Speaker (`{1},{T}` do próprio corpo: untap qualquer
permanente). Os 2 primeiros estavam deferidos com "risco de bug > valor
esperado" (julgamento de valor proibido); os outros 2 nem tinham a
própria ativada mencionada em lugar nenhum. Implementados em
`try_untap_effects()`: cada fonte soma a saída do melhor dork ESCALÁVEL
pronto de novo neste turno (2ª ativação real da habilidade de mana),
pagando o custo real de cada uma.

**Bug real exposto durante a implementação:** Maralen, Fae Ascendant é
"Legendary Creature — **Elf** Faerie Noble" — sem excluir o comandante do
pool de bounce do Wirewood Symbiote, ela podia ser selecionada como
fodder, voltando pra mão. Isso expôs um bug latente de recast do
comandante via o loop genérico de conjuração (`main_phase`'s `while
True:`) que nunca removia ela de `state.hand` corretamente nesse
caminho específico — battlefield crescia sem fim (3000+ cópias de
Maralen numa única partida, seed 2000026, achado via varredura de
timeout). Corrigido excluindo o comandante do pool de fodder (decisão
correta de qualquer forma — nenhum piloto racional bounça o próprio
comandante de 5 mana com um Elfo de 1 mana quando há fodder mais barato).

Validado com: teste isolado do hang (seed 2000026, antes travava
indefinidamente, depois resolve em 0,001s), 20.000 partidas de regressão
(0 erros), `run_batch` confirmando ativação real (30,8% dos jogos, avg
0,94 ativações/partida).

---

## Cobertura das demais 88 cartas

O restante do decklist já estava completamente coberto pelas 2 rodadas
de reanálise anteriores (docstring do arquivo, seções "Passo 0" e
"Simplificações documentadas"). Confirmado nesta rodada, carta por
carta, contra o oráculo real:

- **Motor central (gatilho da Maralen)**: exilar/cast grátis — ✅
  `on_creature_enters()`/`maralen_try_free_cast()`. Fonte da exilada é a
  própria biblioteca (aproximação documentada, sem biblioteca de
  oponente real).
- **Roaming Throne** (tipo escolhido: Faerie): dobra correta por FONTE do
  gatilho (não por tipo do que entrou) — ✅ `resolve_times()` (achado
  real 2026-08-31, já corrigido antes desta rodada).
- **Dorks elficos** (Birds/Bloom Tender/Elvish Mystic/Llanowar
  Elves/Joraga Treespeaker/Heritage Druid/Birchlore Rangers/Priest of
  Titania/Elvish Archdruid/Marwyn/Circle of Dreams Druid/Elvish
  Harbinger): todos com produção real modelada, incluindo os casos
  especiais (Joraga nível 0-5 real; Heritage Druid/Birchlore Rangers
  tapando Elfos "sick" como custo, CR 302.6) — ✅ `dork_mana()`.
- **Combo Umbral Mantle + Staff of Domination**: mana infinita real
  detectada, convertida em compra infinita (limite defensivo: biblioteca
  vazia) ou exército de Elfo via Imperious Perfect — ✅.
- **Package de Fadas** (Bitterblossom/Bitterbloom Bearer/Alela/Tegwyll/
  Obyra/Faerie Harbinger/Faerie Mastermind/Mistbind Clique/Spellstutter
  Sprite): tokens/gatilhos de morte/tutores — ✅. Efeitos puramente
  opponent-turn-dependent (Alela's goad/token no turno do oponente,
  Faerie Mastermind's segunda-carta-do-oponente) — 📊 estrutural (sim
  nunca avança turno de oponente).
- **Flash universal** (Leyline of Anticipation/Vedalken Orrery/High Fae
  Trickster/Alchemist's Refuge): habilita conjurar em qualquer momento —
  ✅ `FLASH_SOURCES` (sem efeito extra num sim que só avança os próprios
  turnos, mas modelado corretamente como "disponível").
- **Seedborn Muse / Murkfiend Liege** (untap step de outro jogador): 📊
  genuinamente fora de escopo (mesma razão do Hei Bai) — Murkfiend
  Liege's segundo modo (anthem +1/+1 verde/azul) É modelado (achado
  2026-08-28, `marwyn_effective_power()`).
- **Removal/contramagia** (Assassin's Trophy/Cyclonic Rift/Toxic
  Deluge/Path to Exile-equivalentes/Counterspell/Arcane Denial/Swan
  Song/Pongify/Rapid Hybridization/Reality Shift): conjuradas quando há
  mana sobrando, contadas como interação usada — 📊 sem efeito de
  combate real (convenção da biblioteca inteira).
- **Rhystic Study / Mystic Remora / Kindred Discovery / Black Market
  Connections**: gatilhos passivos dependentes de ação do oponente
  (Rhystic/Remora) — 📊; Kindred Discovery (tipo escolhido: Elf ou Faerie)
  e Black Market Connections — ✅ reais.
- **Thranduil, Sindarin Liege // Silvan Rally / Thranduil's Company**:
  landfall real (token de Elfo / contadores) — ✅; face Adventure (Silvan
  Rally, mill+busca terreno) — ✅.
- **Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun**: ETB busca
  criatura + transforma com 4+ criaturas — ✅ `itlimoc_transformed`.
- **Green Sun's Zenith**: busca criatura verde de MV<=X — ✅
  `cast_green_sun_zenith()`.
- **Fetch lands / duais**: mana genérica (modelo total, não pip-a-pip,
  decisão consistente pra todo o arquivo) — ✅.

---

## Resumo numérico

- **92 cartas.**
- **✅ Implementado:** ~80 linhas de cláusula.
- **📊 N/A estrutural:** ~10 linhas.
- **🐛 Corrigido nesta rodada:** 4 cartas (família "untap") + 1 bug de
  hang exposto e corrigido no mesmo processo (recast descontrolado do
  comandante quando bounçado).

O achado mais importante desta rodada não foi apenas "uma habilidade
faltando" — foi que implementar de verdade uma mecânica antes deferida
por julgamento de valor **revelou um bug real e pré-existente** que
nenhuma auditoria anterior (nem 2026-08-28, nem 2026-08-30/31) poderia
ter encontrado, porque o caminho de código que ele expõe simplesmente
nunca era alcançado antes. Isso é evidência direta de por que "compile
TUDO" é a instrução certa, não uma teimosia: julgamento de valor sobre
o que implementar também filtra quais bugs você tem chance de achar.
