# Regras permanentes do usuário (mezzasalma)

> Espelho versionado deste repositório do arquivo canônico em
> `references/user-standing-rules.md` dentro do skill `mtg-commander`
> (`/root/.claude/skills/synced/mtg-commander/`, fora do controle de versão
> deste repo). O skill é a cópia que eu realmente consulto antes de agir —
> esta aqui existe pra ficar versionada e visível no seu histórico do
> GitHub. Se as duas divergirem, atualize as duas juntas.


Instruções dadas explicitamente pelo usuário ao longo de sessões de trabalho
com decks de Commander, que valem **sempre**, não só na conversa em que foram
ditas. Checar este arquivo no início de qualquer trabalho novo com decks
desse usuário.

---

## 1. Nunca inventar dado, sempre citar fonte oficial

Citação literal do usuário: *"Pare de me elogiar e sempre me diga as fontes
oficiais das suas informações, não quero que vc crie ou invente nada, mesmo
que eu não peça explicitamente, ok?"*

- Toda afirmação sobre uma carta (custo, texto, legalidade, preço) precisa
  vir de uma consulta real à API do Scryfall (ou cache local dela),
  citada explicitamente — nunca de memória.
- Toda afirmação sobre popularidade/inclusão de carta num arquétipo precisa
  vir de uma consulta real ao EDHREC — nunca de memória ou "impressão".
- Nenhum elogio gratuito ("ótima pergunta", "excelente ideia") — só
  informação e análise direta.
- Qualquer número que dependa de uma premissa não-verificável (ex: quantos
  spells um oponente conjura por turno num goldfish solo) precisa ser
  marcado explicitamente como premissa assumida, não como dado real — e
  a premissa deve ser validada pelo usuário antes de virar "confirmada".

## 2. Toda vez que um deck for adicionado, rodar a auditoria completa

Citação literal do usuário: *"sempre que eu adicionar um deck aqui RODE A
AUDITORIA COMPLETA"*.

- Não esperar o usuário pedir a auditoria separadamente — ela é automática
  assim que uma lista de deck nova é salva.
- Auditoria completa = checklist de `references/commander-rules.md#analise`
  (identidade de cor, terrenos, curva, ramp, draw, remoção, win conditions,
  sinergia, bracket) com tudo sourced via Scryfall/EDHREC.

## 3. Qualquer efeito de carta com regra estrutural precisa de implementação real em simulador, não só tag

Ver `references/goldfish-sim-card-rules.md` — lista de cartas específicas
(Roaming Throne é a primeira) cujo efeito precisa estar em código de
verdade em **qualquer** simulador de goldfish que as inclua, não só uma tag
decorativa. Checar essa lista antes de considerar um simulador completo.

## 4. Toda regra permanente criada numa sessão tem que ser espelhada no GitHub também

Citação literal do usuário (2026-08-21): *"TODA E QUALQUER REGRA QUE EU
CRIAR AQUI TEM QUE SER COPIADA NO GITHUB TB!"*

- O skill (`/root/.claude/skills/synced/mtg-commander/`) é onde a regra é
  realmente consultada durante o trabalho — mas não é versionada no
  controle de versão do usuário.
- Toda regra permanente registrada aqui precisa ter uma cópia espelhada
  em `references/` na raiz do repositório `MTG-Code` do usuário, commitada
  e enviada pro GitHub. Este arquivo (`user-standing-rules.md`) e o
  `goldfish-sim-card-rules.md` são os dois primeiros exemplos.
- Se as duas cópias divergirem (uma foi atualizada e a outra não),
  atualizar as duas juntas antes de continuar qualquer trabalho.

## 5. Cartas protegidas contra corte, por deck (nunca sugerir cortar, mesmo com baixa sinergia)

Cartas que o usuário vetou explicitamente, independente do que qualquer
métrica (EDHREC, matriz de sinergia, goldfish) mostrar sobre elas.

**Thranduil, the Elvenking (thranduil-sultai):**
- **Roaming Throne** e **Maralen, Fae Ascendant** — *"Nem pensar em tirar o
  trono ou a Maralen"* (stop hook feedback, sessão 2026-08-20/21).
- **Thranduil's Company** — *"Não vamos tirar o Thranduil's Company em
  hipótese alguma."* (2026-08-21), mesmo sendo o único card do deck sem
  nenhuma proteção em nenhuma dimensão da matriz de sinergia
  (`thranduil_synergy_matrix.py`) — vetada por decisão direta do usuário,
  não por análise.

## 6. Auditoria de manabase: sempre contar Command Tower, fetches, Arcane Signet e outros fixers flexíveis como fontes reais

Citação literal do usuário (2026-08-24): *"Sempre que vc for avaliar a
manabase, lembre de contar Command Tower, os fixers (fetch lands, arcane
signet e outros corretores como Dryad) daqui para frente, ok?"*

Contexto: numa auditoria de pips do Hei Bai, um cálculo inicial contou
fetch lands como fontes de só as 2 cores "nomeadas" no texto delas (ex:
Arid Mesa = R ou W), subestimando o alcance real. Fetches buscam por
**tipo** de terreno, não só básica — então também pegam qualquer
dual/triome que carregue aquele tipo. Testado no Hei Bai: as 8 fetches da
lista, cada uma, alcançavam as 5 cores, porque a manabase tinha duais/
triomes multicoloridos suficientes conectando todo tipo básico a todo o
resto.

- **Command Tower, Arcane Signet** (e qualquer fonte "any color in your
  commander's color identity") contam como fonte de TODAS as cores da
  identidade do comandante, não de uma cor só.
- **Fetch lands**: não contar só as 2 cores nomeadas no texto. Cruzar
  contra `type_line` de TODO terreno da lista (duais, triomes, básicas)
  pra achar quais compartilham um dos 2 tipos buscados, e somar a união
  de cores de todos esses alvos — não só o par nomeado.
- **Fixers estáticos que mudam terrenos** (ex: Dryad of the Ilysian
  Grove — "Lands you control are every basic land type"; Yavimaya,
  Cradle of Growth — "Each land is a Forest in addition to its other
  land types") contam como fonte real de cada cor que passam a habilitar,
  uma vez em campo — mas são condicionais (precisam resolver primeiro),
  então registrar separado da contagem "sempre disponível desde o turno 1"
  (terrenos básicos, duais, fetches, rocks), não misturado nela.
- Toda contagem de fonte-por-cor precisa citar de qual das categorias
  acima veio (fixa incondicional vs. condicional-uma-vez-resolvida), não
  só o número final — pra não repetir o erro de subestimar (ou
  superestimar) o alcance real da manabase.

**Adendo (2026-08-27), Ur-Dragon:** citação literal do usuário — *"Vc por
acaso colocou Cavern of Souls, Haven of the Spirit Dragon e Secluded
Courtyard como condicionais, mas elas geram mana de qualquer cor para o
tipo de criatura escolhida (Dragão). Mais um erro importante conceitual e
prático de sua parte!"* Eu tinha essas 3 terras tratadas como puramente
incolores no simulador, com a justificativa de que a restrição "só pra
criatura do tipo escolhido" era real demais pra modelar sem inflar
fixação pro resto do deck — mas isso ignorou que, num deck com identidade
tribal clara (comandante do tipo X + várias criaturas do tipo X), o tipo
escolhido é óbvio e fixo, e essas fontes viram fixação real de qualquer
cor pra exatamente a fatia de maior demanda de pips do deck. No Ur-Dragon:
21 criaturas Dragão carregam 49% de todos os pips coloridos (70,7% da
demanda de vermelho especificamente) — Cavern/Courtyard/Haven cobrem
integralmente essa fatia.

- **Terrenos "any color" restritos a um tipo de criatura escolhido** (ex:
  Cavern of Souls, Secluded Courtyard) **ou fixos num tipo** (ex: Haven of
  the Spirit Dragon): não tratar como incolor só porque a restrição
  existe. Contar como fonte real de qualquer cor, mas só pro subconjunto
  de spells daquele tipo — nunca despejar no `produces` geral do resto do
  deck (isso infla artificialmente a fixação pra spells que não se
  beneficiam, ex: removal, ramp genérico, artifacts).
  - Calcular e citar explicitamente que fração da demanda de pips (por
    cor) vem desse subconjunto de criaturas — se for uma fração grande
    (tribal focado), o "incolor" está subestimando a manabase real; se for
    pequena, o tratamento incolor pode seguir sendo a aproximação certa.
  - Documentar a contagem separada (fontes gerais vs. fontes só-pro-tipo),
    igual à distinção já feita acima pra fixers condicionais.

## 7. Combo achado no Commander Spellbook: sempre calcular turno/probabilidade real antes de tratar como achado de Bracket

Citação literal do usuário (2026-08-27), depois de eu alarmar sobre 2
combos infinitos "já montados" no Ur-Dragon sem checar viabilidade: *"Não
viaja, quando eu consigo executar esses combos? Algum antes do turno
8?"* — e depois: *"Adicione nas regras a questão do turno dos combos e
de final do jogo dos brackets na sua análise."*

Contexto: Commander Spellbook (`backend.commanderspellbook.com`) confirma
se uma combinação de cartas FUNCIONA nas regras, dado que todas estão na
lista — não diz nada sobre quão rápido ou provável é montá-la numa
partida real. Achar um combo "included" lá não é, por si só, motivo pra
reclassificar Bracket. No caso do Ur-Dragon, calculei a probabilidade
hipergeométrica real de ter as peças específicas na mão (sem tutor
dedicado buscando as duas juntas) — deu **1,9% até o turno 8** pro combo
de 2 cartas mais provável, **0,23%** pro de 3 cartas — antes ainda de
contar mana, haste, e sobreviver a remoção numa mesa real de 4
jogadores. Não é um "combo turno 3-4", é um evento de cauda.

**Daqui pra frente, sempre que um combo for encontrado via Commander
Spellbook (ou qualquer fonte que só verifique legalidade/funcionamento,
não velocidade):**
- Calcular a probabilidade hipergeométrica real de ter TODAS as peças na
  mão até um turno de referência (6, 8, 10, 12), considerando o tamanho
  real do deck e se existe algum tutor que busque especificamente essas
  peças (o que muda a conta radicalmente).
- Checar custo de mana de cada peça e se alguma tem haste/enabler de
  haste já na lista — combos que exigem sobreviver um ciclo de turno
  sem summoning sickness são mais lentos ainda do que a probabilidade de
  draw sozinha sugere.
- Só tratar um combo como relevante pro critério oficial de Bracket
  ("combo infinito de 2 cartas cedo no jogo") se a análise acima mostrar
  que ele é rápido E provável — não só "existe" — citando o número
  calculado, não uma impressão.
- Registrar esse cálculo explicitamente na auditoria/log, não só a
  conclusão — pra não repetir o erro de alarmar sobre reclassificação de
  Bracket antes de checar viabilidade real.

## 8. Necessidade real de mana é turno-a-turno, não soma agregada de pips

Citação literal do usuário (2026-08-27), Ur-Dragon: *"Não, quero a
análise real da necessidade de mana, pq quando vc soma todos os pips,
não considera que dificilmente eu irei cast 3 dragões que precisam de
pips vermelho no mesmo turno! Ou eles entram por habilidade do
Ur-Dragon, ou por outras habilidades!"*

Contexto: a auditoria de pips usada nas Correções #5-#10 (somar todos os
pips coloridos do deck inteiro e comparar contra fontes de mana
agregadas) é útil pra saber SE a manabase tem cor suficiente no
agregado, mas superestima a pressão real — ignora que (a) só uma fração
do deck é jogada numa partida, (b) parte relevante das ameaças pode
entrar em campo sem pagar pip nenhum (tokens, reanimação, tutor,
habilidades como a da própria Ur-Dragon), e (c) mesmo o que é conjurado
de verdade está espalhado ao longo de vários turnos, não simultâneo.
Verificado no Ur-Dragon: de ~7,85 Dragões em campo no fim de uma
partida de 8 turnos, só 44,6% (3,50) foram realmente conjurados pagando
mana — 48,2% eram tokens, 7,2% entraram de graça por reanimação/tutor.

- **Nunca apresentar a soma agregada de pips vs. fontes agregadas como
  "a" medida de necessidade de mana.** Ela serve só como triagem inicial
  (existe desequilíbrio grosseiro de cor no deck?), não como conclusão
  final sobre pressão de jogo real.
- **A métrica correta é turno-a-turno**, calculada rodando o goldfish de
  verdade: `color_screw_turns` / `first_color_screw_turn` (turnos onde a
  mana total bastava mas a cor certa não estava disponível) — isso já
  reflete curva real, mão real, e qualquer via de entrada gratuita
  corretamente implementada no simulador.
- **Antes de reportar "demanda de X% na cor Y", separar o que é
  conjurado pagando mana do que entra por outra via** (token, reanimação,
  tutor pra campo, habilidade de ataque/ETB de outra carta) — a soma de
  pips do deck inteiro conta ameaças que nunca vão exigir aquele pip na
  prática.
- Isso não invalida a auditoria de pips como ferramenta (ainda é o jeito
  mais rápido de notar "essa cor está claramente sub-representada"), só
  não deve ser tratada como o número final sem cruzar com dado
  turno-a-turno do simulador.

## 9. Checklist obrigatória de categorias de mecânica em TODO simulador (não só a carta sendo trabalhada no momento)

Citação literal do usuário (2026-08-28), depois de eu entregar o Beorn sem
nenhum despacho de landfall apesar de 6 cartas do deck dependerem dele: *"Como
diabos vc criou um simulador que não leva em conta a porra do Landfall???
[...] acrescente uma maldita regra de conferir TODAS AS MALDITAS INTERAÇÕES,
ATIVAÇÕES e COMBOS do deck na porra do simulador. Revise gatilhos, tokens,
motores de draw e ramp, e os mana dorks, mana rocks e lands que geram mana
fixing em TODOS OS DECKS E SIMULADORES!!!!"*

Checklist completa (landfall, mana dorks/rocks/fixing, draw engines, ramp
engines, ativadas repetíveis, combos entre peças já na lista) em
`references/goldfish-sim-card-rules.md#checklist-obrigatória-de-categorias-de-mecânica-não-só-cartas-individuais`.
Obrigatória antes de declarar **qualquer** simulador (novo ou em revisão)
completo — inclusive os já existentes, não só o que está sendo escrito no
momento.

**Reforço/ampliação (2026-08-28), depois da rodada final do Beorn:** citação
literal do usuário — *"Lembre da regra que criamos: TODA SIMULAÇÃO E DECK TEM
QUE TER TODAS AS Ativações, gatilhos, habilidades estáticas, combos e
métricas básicas (ramp, draw, interaction, finisher/lethality) contabilizados
e auditados SEMPRE!"*

- Duas categorias novas na checklist (itens 9 e 10 no `goldfish-sim-card-rules.md`):
  **habilidades estáticas** (anthems, custo reduzido, "criaturas são do tipo
  X", mudança de tipo de terreno, restrição/expansão de cor — precisam estar
  aplicadas em TODO cálculo que afetam, não só onde foram implementadas
  primeiro) e **métricas básicas obrigatórias no relatório de todo simulador**
  (ramp, draw, interaction, finisher/lethality — reportadas de forma
  auditável e separada, mesmo quando o deck já tem métricas específicas por
  carta).
- **"SEMPRE" é literal:** essa checklist (10 categorias completas) vale pra
  **todo deck e todo simulador do repositório, em toda sessão**, não só o
  deck sendo trabalhado no momento em que a regra foi criada ou reforçada —
  inclusive decks já auditados anteriormente, que devem ser revisados de novo
  se alguma categoria não tiver sido explicitamente checada e documentada.

**2º reforço (2026-08-28), depois da checklist ampliada aplicada em Edgar
Markov/Hei Bai:** citação literal do usuário — *"Vc precisa acrescentar a
variável recursão e interação à lista de variáveis para avaliar, medir e
registrar em todos os decks tb!"*

- **Recursão** vira a **5ª categoria obrigatória de métrica básica** (antes
  eram 4: ramp/draw/interaction/finisher-lethality) — ver
  `references/goldfish-sim-card-rules.md#checklist-obrigatória-de-categorias-de-mecânica-não-só-cartas-individuais`,
  item 10. Cobre qualquer efeito de recuperar carta do cemitério (pra mão,
  campo, ou topo da biblioteca): reanimação, "return target card from your
  graveyard", tutor-de-volta, etc.
- **Interação** já estava na lista de 4, mas o reforço deixa explícito:
  precisa de uma métrica agregada de verdade reportada no `run_batch` de
  TODO deck com pelo menos 1 carta de remoção/proteção/interação — mesmo
  quando o valor é 0 por decisão de arquitetura (goldfish solo sem oponente
  real pra mirar), documentar isso como uma linha própria do relatório, não
  como uma nota de rodapé sem número.
- Aplica-se retroativamente aos decks já concluídos nesta sessão (Beorn,
  Edgar Markov, Hei Bai) e a todo deck futuro, desde a auditoria inicial —
  não é um adendo só pros próximos decks.

**3º reforço (2026-08-28) — cartas de face múltipla:** depois de eu
reportar RECURSION quase zerada no Edgar Markov, o usuário perguntou direto
— citação literal: *"Como Edgar Markov não tem recursão? Vc auditou tudo
mesmo? E Agadeem's Awakening e Bloodline Bidding? Rise of the Dark
Realms?"* — e, depois de eu confirmar que Agadeem's Awakening estava
land-primary por engano (achado real: MDFC verdadeiro nunca conjurado como
spell) e que Rise of the Dark Realms não está na lista real: *"Então já
tinha tirado o Rise, verifique mais uma vez todas as cartas modais/
aventuras/preparadas/dupla face dos dois decks e acrescente essa regra de
verificar e compilar TODOS OS EFEITOS DAS CARTAS: Rooms, battles, mdfcs,
adventures, prepared, etc, para TODOS OS DECKS."*

- Nova categoria 11 na checklist (`goldfish-sim-card-rules.md`): antes de
  registrar QUALQUER carta com "//" no nome (ou layout multi-face), checar
  o campo `layout` real da API do Scryfall — não adivinhar. `modal_dfc`
  (2 faces independentes) é diferente de `transform` (só a frente é
  castável da mão, o verso só chega via gatilho real) é diferente de
  `split`/Room (destranca a 2ª porta depois) é diferente de `prepare`
  (Emeritus of Woe/Stensian Sanguinist) é diferente de Adventure é
  diferente de `battle`.
- **Achado real que motivou a regra:** Ojer Taq, Deepest Foundation //
  Temple of Civilization e Legion's Landing // Adanto, the First Fort
  (Edgar Markov) tinham layout `transform` mas eram registradas DIRETO como
  Land — isso não era só "perder valor", era simular uma ação ilegal do
  jogo (jogar um verso que nunca poderia ter sido alcançado sem conjurar a
  frente primeiro). Corrigido, ver `edgar-markov-mardu/goldfish-log.md`,
  Correção #13.
- Vale pra **todo deck do repositório**, não só o Edgar Markov — qualquer
  carta com "//" no nome em qualquer decklist precisa passar por essa
  verificação antes de ser considerada auditada.

**4º reforço (2026-08-28) — planeswalkers:** depois de eu confirmar que o
Prismatic Bridge (17 planeswalkers na lista) só rastreava SE a Bridge
acertava um planeswalker, nunca o que ele fazia depois de entrar em campo
(nenhuma lealdade, nenhuma ativação, nenhum efeito) — citação literal do
usuário: *"Preciso que os counters de lealdade e ativações de planeswalker
sejam sempre contabilizados, a base do Prismatic Bridge é essa! Adicione
essa regra para tudo, sempre também!"*

- Nova categoria 12 na checklist (`goldfish-sim-card-rules.md`): todo
  planeswalker em qualquer deck do repositório precisa de lealdade
  rastreada de verdade, uma decisão real de qual habilidade ativar a cada
  turno, e o efeito de cada habilidade implementado — não só a tag
  decorativa `"planeswalker"`.
- Vale retroativamente pra qualquer deck já auditado que tenha
  planeswalker e ainda não modele isso (Edgar Markov tem Sorin/Elspeth
  deferidos por essa mesma razão — precisa ser revisitado) e pra todo deck
  futuro desde a auditoria inicial.

**5º reforço (2026-08-28) — Classes e Sagas ("níveis"):** citação literal
do usuário — *"Não esqueça de verificar as cartas com 'níveis', como
classes e sagas. Vc tb precisa criar a regra de verificar e contabilizar
isso, pq o caretaker's talent se elevado ao nível 3 aumenta todos as token
creatures e o innkeeper's no Prismatic no nível 3 DOBRA TODOS OS COUNTERS,
inclusive os de lealdade de PWs ao entrarem no jogo!"*

- Nova categoria 13 na checklist (`goldfish-sim-card-rules.md`): antes de
  decidir que só a habilidade BASE de uma Class é modelável, ler o texto
  de TODOS os níveis contra o oráculo real — um nível alto pode ser um
  efeito de campo inteiro (anthem, dobrador de counter) que muda o valor
  real da carta por completo. Sagas também entram (capítulos automáticos,
  não pagos, mas podem conceder habilidade ativada que compete pelo `{T}`
  da própria mana da carta).
- **Achado real que motivou a regra:** Innkeeper's Talent (Prismatic
  Bridge) nível 3 dobra TODOS os counters — incluindo a lealdade inicial
  de planeswalker ao entrar em campo, uma interação direta com o sistema
  de lealdade construído na correção anterior, que eu tinha deixado de
  fora citando "precisa de engine de leveling" sem tentar construir essa
  engine. Caretaker's Talent (Hei Bai) nível 3 dá +2/+2 a criaturas-token,
  um anthem de campo inteiro, também deixado de fora.
- Vale pra **todo deck do repositório** com Class/Saga na lista.

---

<!-- Adicionar novas regras permanentes abaixo conforme o usuário as
     estabelecer explicitamente. Cada entrada deve citar a frase literal
     do usuário quando possível, pra não perder o contexto original. -->
