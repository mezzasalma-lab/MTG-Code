# Checklist cláusula-a-cláusula — Esika // The Prismatic Bridge

## Auditoria oráculo-por-oráculo completa — 2026-09-13/14

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil/Nekusar/Ms.
Bumbleflower/Rat King. Oráculo real via Scryfall pras 65 cartas + 29
terrenos + comandante (MDFC modal, layout `modal_dfc` confirmado —
Esika, God of the Tree {1}{G}{G} / The Prismatic Bridge {W}{U}{B}{R}{G}),
comparado cláusula-por-cláusula contra o código já existente (que já
tinha passado por 3 rodadas anteriores — 2026-08-21, 08-28, 09-01 — e é
um dos arquivos mais maduros e documentados do repositório).

**Achado principal — 3 fontes reais de "ativar lealdade mais de 1x por
turno" nunca implementadas, num deck com 17 planeswalkers:**

1. **Oath of Teferi** — "You may activate the loyalty abilities of
   planeswalkers you control **twice each turn** rather than only
   once." Estático, sempre ligado enquanto em campo — a carta inteira
   tinha `tags=set()` (nem fantasma, tag nenhuma).
2. **The Chain Veil** — "{4}, {T}: For each planeswalker you control,
   you may activate one of its loyalty abilities **once this turn** as
   though none of its loyalty abilities have been activated this
   turn." Habilidade ativada real, paga — também `tags=set()`.
3. **Urza Assembles the Titans** — Saga (Read ahead) 100% ausente:
   capítulo I (revela o topo, planeswalker vai pra mão — scry 4 não
   modelado, sem infra de scry neste arquivo), capítulo II (planeswalker
   MV≤6 da mão pra campo de graça), capítulo III (dobra ativação de
   lealdade só naquele turno, depois sacrifica).

Com 17 planeswalkers na lista, esses 3 multiplicadores de ativação são
provavelmente o maior bloco de valor real do deck fora da própria Bridge
— nenhum estava implementado. Corrigido com uma função central
`extra_pw_activation_sources()` (as 3 fontes são aditivas, não mutuamente
exclusivas — Oath of Teferi permite 2x, Chain Veil/Urza cap. III cada
um concede "mais uma" em cima disso), consumida por
`activate_planeswalkers()` (que já ativava 1x por planeswalker por
turno, CR 606.3 — agora ativa `1 + extras` vezes, respeitando a taxa do
Carth the Lion em CADA ativação individual, inclusive as extras).

**Achado secundário — 11 cartas de interação nunca contavam pra métrica,
ao contrário de todos os outros decks da sessão:** Counterspell, Mana
Drain, Path to Exile, Swords to Plowshares, Anguished Unmaking, Damn,
Void Rend, Toxic Deluge, Blasphemous Act, Supreme Verdict e Farewell
tinham as tags reais (`removal`/`counterspell`/`wipe`) desde a
construção original, mas essas tags nunca eram lidas em lugar nenhum —
as cartas eram conjuradas pelo loop genérico (corretamente sem efeito
de bordo real, Regra 1: sem oponente/spell real pra mirar, e nenhum
wipe destrói o próprio board sem motivo), mas nem sequer contavam como
"interação conjurada" na métrica agregada, inconsistente com a
convenção das 5 métricas básicas usada em todos os outros decks
auditados nesta sessão. Corrigido com `interaction_spells_cast_total`.

**Validação:** smoke test (105 nomes no `CARD_DB`, 99 cartas na
decklist, 0 desconhecidas) + 2.000 partidas antes/depois (mesma seed
3000000) + 20.000 partidas de regressão (seed 7000000), 0 exceções em
ambas. Testes unitários dirigidos confirmaram cada correção: Oath of
Teferi e The Chain Veil dobram as ativações reais de um planeswalker no
mesmo turno; Urza dispara os 3 capítulos corretamente (tutora
planeswalker no I, coloca em campo de graça no II, marca a flag de
dobra no III e se sacrifica); Swords to Plowshares agora conta pra
`interaction_spells_cast_total` ao ser conjurada. Métricas de 2.000
partidas subiram como esperado: ativações de planeswalker por partida
7.01→8.65, ultimates usados 1.18→1.48, draws via planeswalker
3.87→4.66 — nenhuma mudança de categoria no comportamento típico do
deck, só o motor de superfriends ficando mais completo.

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron e Nekusar.

**Aviso importante sobre este deck especificamente:** diferente dos
outros, este simulador foi construído **deliberadamente com escopo
restrito** (docstring original: *"Este é um simulador FOCADO, não um
goldfish completo de curva geral... Escopo deliberadamente restrito ao
que a pergunta do usuário pede: turno em que a Bridge resolve, taxa de
acerto da Bridge em criatura/planeswalker, e sobrevivência da
Bridge/protetores sob remoção do oponente"*). Não modela casting geral de
toda a lista com a mesma profundidade dos outros 6 decks — mas modela
com precisão real tudo que compõe o motor central (Bridge + 17
planeswalkers com lealdade rastreada). Nesta rodada, apliquei o mesmo
padrão "compile TUDO" às lacunas que **estavam documentadas como
deferidas**, não ao escopo original do simulador em si.

## 🐛 Achados corrigidos nesta rodada

O docstring antigo tinha 2 notas de "deferido": uma citando "14 cartas
tageadas draw sem gatilho" (na verdade só 2 não-planeswalker, ambas
genuinamente 📊 — ver abaixo) e outra citando 6 fontes de proliferate
fora de escopo "por volume". Investigando cada uma individualmente
contra o oráculo real (não a alegação do comentário antigo):

1. **Sphinx of the Second Sun** — "if you cast it, take an extra turn"
   nunca implementado (nem a fila de turnos extras existia no arquivo).
   Corrigido: `extra_turns_pending`/`sphinx_sacrifice_pending`, mesma
   convenção já usada nos simuladores do Maralen/Megatron desta sessão.
   Verificado que a condição "if you cast it" **não** é satisfeita
   quando a Bridge põe a carta em campo (ela não conjura, só coloca) —
   isso é regra real, não uma lacuna.
2. **Carth the Lion** — ETB "look at top 7, reveal planeswalker, put in
   hand" 100% ausente (eu tinha memorizado errado o texto dela antes de
   verificar — não é a habilidade que eu assumi inicialmente). Corrigido:
   `do_carth_etb()`. Estático real "planeswalker loyalty abilities cost
   {1} more" também implementado (`activate_planeswalkers()`, taxa real
   nas nossas próprias ativações).
3. **Flux Channeler / Inexorable Tide** — "whenever you cast a
   noncreature/any spell, proliferate" 100% ausentes apesar de reusarem
   uma função (`proliferate_loyalty()`) já testada pro Evolution
   Sage/Vraska. Corrigidos, disparam independentemente se ambos em campo.
4. **Mutational Advantage / Ripples of Potential** — proliferate no
   próprio efeito ao serem conjuradas, 100% ausente. Corrigido.

Validado com 6+ testes unitários isolados + regressão de 20.000 partidas
(0 erros, alternando `with_greater_auramancy`) + `run_batch` confirmando
ativação real (Sphinx extra turn 4,7% dos jogos, Carth tutor 11,2%).

## Reclassificações (não bugs, verificação corrigiu minha própria memória)

- **Arena Rector**: eu lembrava errado como ETB "exile + recast lendário
  do cemitério" — o texto real é um **gatilho de MORTE** ("When this
  creature dies..."). Como nada remove nossas próprias
  criaturas/planeswalkers neste modelo (`resolve_removal_round()` só
  atinge Sterling Grove/Greater Auramancy/a própria Bridge), esse
  gatilho nunca teria janela real — 📊 estrutural confirmado, não gap.
- **The Peregrine Dynamo**: "{1},{T}: copy target activated/triggered
  ability from another legendary source" — exceção arquitetural real
  (escolher QUAL dentre N fontes legendárias copiar), mesma classe do
  Strionic Resonator/Weaver of Harmony noutros decks — 📝.
- **Rhystic Study / Veil of Summer**: ambas opponent-dependent de
  verdade ("whenever an opponent casts a spell" / "if an opponent has
  cast a blue or black spell this turn") — 📊, mesma convenção
  consistente em todo o resto da sessão. A nota antiga do docstring
  ("14 cartas") estava contando os 12 planeswalkers com tag "draw" que
  JÁ tinham sido corrigidos na rodada de lealdade (2026-08-28) — a nota
  ficou desatualizada, não os gaps continuavam reais.

## Deferido, confirmado genuinamente fora de escopo (não implementado)

- **Nicol Bolas, Dragon-God** — estático "has all loyalty abilities of
  all other planeswalkers" exigiria uma segunda camada de escolha por PW
  em cima da lógica já hardcoded de `resolve_planeswalker()`.
- **Ichormoon Gauntlet** — concede uma habilidade de lealdade NOVA
  ("[0]: Proliferate", "[−12]: extra turn") a cada um dos 17
  planeswalkers — mesma classe de reestruturação do Nicol Bolas, escopo
  desproporcional ao resto desta rodada.

---

## Resumo numérico

- **~65 cartas não-terreno** (escopo do simulador — foco no motor
  Bridge/planeswalker, não curva geral completa).
- **🐛 Corrigido nesta rodada:** 5 cartas (Sphinx of the Second Sun,
  Carth the Lion, Flux Channeler, Inexorable Tide, Mutational
  Advantage/Ripples of Potential).
- **📊/📝 Confirmado estrutural (2 reclassificações de memória errada,
  não bugs):** Arena Rector, The Peregrine Dynamo.
- **Deferido, genuinamente desproporcional:** Nicol Bolas, Ichormoon
  Gauntlet (ambos exigiriam reestruturar a arquitetura hardcoded de
  planeswalker deste arquivo especificamente, não um julgamento de
  valor sobre a carta em si).
