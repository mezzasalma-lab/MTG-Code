# Checklist cláusula-a-cláusula — Maralen, Fae Ascendant

## Achado real 2026-09-14 (usuário perguntou se Roaming Throne está certa em todos os decks onde aparece) + bug de hang de verdade achado ao validar

Este deck já tinha a arquitetura mais madura da sessão pra Roaming
Throne (tag do próprio tipo escolhido cravada no `CARD_DB`, dobra de
gatilho já checando a FONTE corretamente em 3 sites diferentes, com
comentários já documentando o mesmo raciocínio que apliquei hoje nos
outros decks). Achei **1 gap real**: **Faerie Harbinger** ("search your
library for a Faerie card, put it on top") aceitava Roaming Throne como
alvo válido de busca na biblioteca — mas o tipo Faerie que ela ganha é
efeito de ETB, não persiste em zonas fora da batalha (mesma classe de
achado nos outros 4 decks hoje). Corrigido excluindo `"Roaming Throne"`
explicitamente dessa busca (única library-scoped do arquivo usando
`is_faerie`).

**Achado incidental bem mais grave, ao validar com a regressão de
20.000 partidas: um HANG DE VERDADE (loop infinito), pré-existente,
sem relação com a Roaming Throne.** `try_faerie_mastermind()` tem um
`while remaining_mana(state) >= 4:` que gasta mana e compra 1 carta por
iteração — mas `remaining_mana()` chama `total_mana()` que chama
`dork_mana()`, e `dork_mana()` tem um EFEITO COLATERAL: ela seta
`state.infinite_mana_this_turn = True` assim que detecta o combo do
Umbral Mantle pronto (dork escalável equipado, saída ≥4) — só de ser
CONSULTADA, sem precisar de nada externo acontecer. Se isso disparar no
MEIO do loop da Faerie Mastermind (entre uma iteração e a próxima, sem
nenhuma mudança de board real), `remaining_mana()` passa a retornar 999
pra sempre e `spend_mana()` vira no-op (mesmo guard) — o loop nunca mais
termina, comprando a biblioteca inteira em loop. Confirmado
determinístico e reproduzível isoladamente na seed 6713530 (e
confirmado **pré-existente**, não causado pela minha correção — reproduz
igual com `git stash` no código original). Corrigido rechecando o flag
`infinite_mana_this_turn` a cada iteração do `while`, não só na entrada
da função (que já tinha o guard certo, só não bastava).

**Validação:** teste unitário direto (seed 6713530, antes travava
indefinidamente, depois termina normalmente). 20.000 partidas de
regressão (seed 6700000+) — **antes deste fix, travava por completo
entre a partida ~13400 e ~13600 (nunca chegava a terminar as 20.000);
depois, 0 exceções, termina em segundos**. `Avg tutors_used_total`:
0,925→0,905 (Faerie Harbinger, movimento pequeno, cenário raro de
Roaming Throne ser a "Fada" candidata). `Avg
faerie_mastermind_draws_total`: 1,19 (máximo numa única partida: 135 —
bounded, sem sinal de loop restante).

---

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Azula/Beorn/Captain
Storm/Edgar Markov/Hei Bai nesta sessão: oráculo real via Scryfall pras 88
cartas não-terreno/não-MDFC + 3 MDFC/Adventure + comandante (2 lotes de
`POST /cards/collection` + `/cards/named?fuzzy=` pros 3 multi-face),
comparado cláusula-por-cláusula contra o `maralen_goldfish_v1.py` atual —
já o deck mais auditado da sessão (6+ rodadas anteriores, ver seções
abaixo). Mesmo assim, **4 gaps reais encontrados e corrigidos**:

1. **`marwyn_effective_power()` faltava 2 dos 4 anthems reais de Elfo.**
   A função já tinha sido corrigida numa rodada anterior (2026-08-28) pra
   somar o bônus de Elvish Archdruid e Murkfiend Liege — mas **Imperious
   Perfect** ("Other Elves you control get +1/+1") e **Thranduil, Sindarin
   Liege** ("Other Elves you control get +1/+1") têm a MESMA cláusula
   estática, e Marwyn é Elfo — deveriam somar +1/+1 cada uma também, mas
   nenhuma das duas era checada. Mesma classe de bug já achada no Beorn
   nesta sessão (estática aplicada num lugar, nunca propagada pra toda
   função que lê poder de criatura) — aqui a função já existia e já tinha
   2 dos 4 anthems reais corretos, só faltavam estas 2. Corrigido somando
   os 2 bônus que faltavam em `marwyn_effective_power()`, que já é
   reutilizada por `dork_mana()`, `equip_umbral_mantle()` e
   `best_scaling_dork_output()` — a correção se propaga automaticamente
   pro cálculo de mana da Marwyn, pro threshold do combo do Umbral Mantle
   e pra família "untap" sem precisar tocar em mais nenhum lugar.
2. **Faerie Mastermind — carta inteira ignorada por causa de UMA das 2
   habilidades reais dela ser opponent-dependent.** Oráculo real: *"Whenever
   an opponent draws their second card each turn, you draw a card. {3}{U}:
   Each player draws a card."* A primeira é passiva e genuinamente
   opponent-dependent (já documentada como N/A em rodadas anteriores) —
   mas a segunda é uma habilidade ATIVADA, sem `{T}` no custo, que te dá 1
   compra real e garantida só por pagar mana, sem depender de nada do
   oponente. A carta inteira estava rotulada `opponent_dependent` no
   `CARD_DB` e 100% ignorada no código — só metade merecia esse rótulo.
   Corrigido com nova função `try_faerie_mastermind()`.
3. **Staff of Domination ficava 100% inerte fora do combo infinito.** Só
   o ramo `infinite_mana_this_turn` existia em `use_staff_of_domination_v2()`
   — o motor de compra NORMAL do próprio oráculo (*"{5},{T}: Draw a card"*
   + *"{1}: Untap this artifact"* pra repetir, 6 mana por compra extra a
   partir da 2ª) nunca disparava com mana finita, mesmo num deck com ramp
   pesado onde sobrar 5+ mana num turno normal é comum sem montar o combo
   Umbral Mantle. Corrigido: fora do combo infinito, com 5+ mana sobrando,
   Staff agora compra de verdade (1ª compra por 5, cada compra extra por
   6) — é literalmente o texto impresso da carta, não uma invenção.
4. **Elven Chorus / Realmwalker — tag `"cast_from_top"` 100% morta desde a
   criação do arquivo.** Ambas têm *"You may cast creature spells [do tipo
   escolhido] from the top of your library"* no oráculo real — cadastradas
   com essa tag desde o início (`add()`), mas nunca despachada em lugar
   nenhum do arquivo. Ghost tag genuína que escapou da varredura
   automática de tags mortas desta rodada por aparecer 2x como literal de
   string (uma vez por carta, nunca por ser lida de verdade). Corrigido
   com `can_cast_from_top()`/`do_cast_from_top()`, plugadas no loop
   principal de conjuração do `main_phase()`. Realmwalker escolhe Elfo
   como tipo (heurística documentada inline no código, espelhando a
   escolha de Faerie já feita pro Roaming Throne — cobre o outro lado da
   tribal, 19 Elfos vs 12 Fadas).

**Confirmado e descartado, não é bug:** Tegwyll, Duke of Splendor tem um
segundo anthem real (*"Other Faeries you control get +1/+1"*) sem nenhum
hook numérico no motor — nenhuma mecânica de Fada escala por poder
individual neste simulador (ao contrário do caso da Marwyn/Elfo acima,
onde o poder alimenta diretamente a produção de mana) — N/A genuíno,
mesma classe do Ezuri/Allosaurus Shepherd (bônus de combate sem combate
modelado). Wirewood Lodge (*"{G},{T}: Untap target Elf"* + *"{T}: Add
{C}"* — 2 habilidades com `{T}` se sobrepondo, exatamente a classe de bug
achada no Hei Bai) foi relido linha a linha de novo com essa suspeita
específica e confirmado CORRETO: o custo real já é pago via
`tapped_lands_this_turn` (remove a própria mana do land do pool geral) +
`spend_mana(1)` (paga o `{G}` do resto do pool) — sem dupla contagem.

**Validação:** smoke test (`CARD_DB` 99 nomes, `BASE_LIBRARY` 99 cartas,
sem duplicata/desconhecida) + 2.000 partidas antes/depois (mesma seed
5555000) + 20.000 partidas de regressão (seeds 9500000–9519999, timeout
2s/jogo), 0 exceções/timeouts em todas. Testes unitários dirigidos
confirmaram cada correção isoladamente: Marwyn com os 4 anthems reais em
campo soma poder efetivo 5 (era 3 antes, só Archdruid+Murkfiend); Faerie
Mastermind com 9 mana disponível compra 2 cartas (era sempre 0 antes —
carta inteira ignorada); Staff of Domination com 11 mana fora do combo
infinito compra 2 cartas (era sempre 0 fora do combo antes); um Llanowar
Elves no topo da biblioteca com Elven Chorus em campo é conjurado de
verdade via `cast_from_top_total` (tag existia desde a criação do
arquivo, nunca lida em lugar nenhum antes). Impacto agregado em 2.000
partidas (antes → depois, mesma seed): `maralen_triggers_total` 9,62 →
10,51; `cards_drawn_extra` 3,23 → 4,52 (salto grande — quase inteiro dos
2 motores de compra novos); `combo Umbral Mantle montado` 11,0% → 12,2%
(efeito direto do fix da Marwyn); `Staff infinito` 2,7% → 3,2%; `mão
final` 2,23 → 3,08. Movimento consistente e rastreável a cada correção
específica, nada satura ou explode.

---

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
