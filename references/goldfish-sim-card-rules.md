# Regras permanentes pra simuladores de goldfish

> Espelho versionado deste repositório do arquivo canônico em
> `references/goldfish-sim-card-rules.md` dentro do skill `mtg-commander`
> (`/root/.claude/skills/synced/mtg-commander/`, fora do controle de versão
> deste repo). O skill é a cópia que eu realmente consulto antes de escrever
> ou editar um simulador — esta aqui existe pra ficar versionada e visível
> no seu histórico do GitHub. Se as duas divergirem, atualize as duas juntas.

Cartas nesta lista precisam ter o efeito real implementado em código em
**qualquer** simulador Python de goldfish que inclua elas — não basta marcar
com uma tag decorativa (`trigger_doubler`, etc). Checar esta lista sempre que
uma carta daqui aparecer na decklist de um simulador novo ou existente.

Adicionada por pedido explícito do usuário (sessão do Thranduil, 2026-08-21):
"Quero que isso seja feito em todos os decks com essa carta daqui em diante."

---

## Roaming Throne

`{4}` Artifact Creature — Golem, 4/4, Ward {2}.

Oracle text (Scryfall): *"As this creature enters, choose a creature type.
This creature is the chosen type in addition to its other types. If a
triggered ability of another creature you control of the chosen type
triggers, it triggers an additional time."*

**O que implementar:**
- **Passo 0, obrigatório antes de qualquer coisa:** varredura MECÂNICA (regex
  em `oracle_text`, não de memória) em toda criatura do tipo escolhido na
  decklist, procurando linhas que comecem com "Whenever"/"At the beginning
  of"/"When ... enters". No Thranduil isso achou 16 criaturas do tipo Elf
  com gatilho próprio - só 4 estavam implementadas antes dessa varredura
  (as "óbvias": motor de draw do comandante, engines de compra, dano de
  combate). As outras 12 tinham o gatilho em si nem modelado ainda, então a
  duplicação delas também estava faltando. **Implementar Roaming Throne sem
  esse passo 0 sempre vai deixar gatilhos de fora.**
- Checar também se alguma carta do tipo escolhido **concede** um gatilho a
  OUTRAS criaturas desse tipo via habilidade estática (ex: Dionus, Elvish
  Archdruid no Thranduil: "Elves you control have 'whenever this becomes
  tapped...'"). Cada criatura que recebe essa habilidade concedida também
  passa a ter um gatilho próprio dobrável - isso multiplica o efeito do
  Roaming Throne além das cartas nomeadas individualmente. Registrar como
  limitação conhecida se não for implementado (é um trabalho maior).
- Rastrear o tipo de criatura escolhido (na prática: o tipo tribal central do
  deck — Elfo, Dragão, Zumbi, etc — é quase sempre a escolha certa; documentar
  a premissa no código se não for óbvio).
- Para CADA gatilho de criatura desse tipo já modelado no simulador (draw
  engines, geradores de token, gatilhos do próprio comandante, etc), disparar
  uma **segunda vez completa** quando o Roaming Throne estiver em campo — não
  só dobrar o número final. Um gatilho que resolve "compre 2, descarte 1" vira
  dois disparos separados de "compre 2, descarte 1", não vira "compre 4,
  descarte 2" resolvido de uma vez (pra manter fidelidade caso o efeito tenha
  escolhas que podem variar entre os dois disparos).
- **Não dobra habilidades ativadas nem estáticas** — só gatilhos ("whenever"),
  e só de criaturas do tipo escolhido. Enchantments/artifacts/instants/sorceries
  nunca são afetados, mesmo compartilhando o tipo tribal via texto solto. Vale
  mesmo quando a MESMA carta tem gatilho e ativada juntos (ex: Selvala e
  Marwyn no Thranduil - a habilidade de mana delas, que é ativada, nunca dobra,
  só o gatilho de compra/contador).
- Se o gatilho é do tipo "at least once per turn" ou similar auto-limitado no
  próprio texto da carta, o Roaming Throne dispara essa mesma instância de
  novo (não permite burlar o limite gerando um segundo disparo por evento
  subsequente no mesmo turno) - ex: Elrond e Elvish Warmaster no Thranduil.
- Alguns gatilhos alvejam o OPONENTE (mill/exile na biblioteca dele, dano,
  contadores negativos na criatura dele) e não têm efeito numérico modelável
  num goldfish solo sem oponente real em jogo - nesses casos, implementar
  como um contador de "disparou X vezes" sem side-effect no `GameState`
  próprio, e deixar isso documentado explicitamente (não inventar um efeito
  substituto).
- Alguns gatilhos são **negativos pro próprio jogador** (ex: Ruthless
  Winnower no Thranduil - sacrifica sua própria criatura não-Elfo a cada
  upkeep) - dobrar esses é uma PIORA, não uma melhoria. Sinalizar isso
  explicitamente ao reportar a métrica, não tratar toda duplicação como
  benéfica por padrão.
- Rastrear e reportar uma métrica agregada de "quantos gatilhos foram
  dobrados" pra medir o impacto real nos resultados do goldfish.

**Referência de implementação:**
- `thranduil-sultai/thranduil_goldfish_v1.py` (tipo escolhido: Elf) — função
  `roaming_throne_active()` no `GameState`, aplicada em `_apply_etb`,
  `_creature_cast_engines_trigger` e `combat_step`.
- `beorn-fierce/beorn_goldfish_v1.py` (tipo escolhido: Bear, já que a própria
  Beorn e `Legendary Creature — Bear Shapeshifter Warrior`) — mesmo padrão de
  `roaming_throne_active()`, aplicado em `combat_step` dobrando o próprio
  gatilho de combate da Beorn (converte criatura em Urso + checa 3+ Ursos).
- `edgar-markov-mardu/edgar_markov_goldfish_v1.py` (tipo escolhido: Vampire) —
  Passo 0 achou 16 vampiros com gatilho próprio (de 20 + o próprio Edgar
  Markov). Todos implementados como mecânica real via helper `_times()` +
  `_log_doubling()`: Eminence do comandante (token por vampiro conjurado),
  contador de ataque do próprio Edgar, Sanctum Seeker, Champion of Dusk,
  Welcoming Vampire, Clavileño First of the Blessed, Vito Fanatic de
  Aclazotz (3 estágios de sacrifício), e o pacote de morte (Blood Artist/
  Cruel Celebrant/Cordial Vampire/Vindictive Vampire/Vein Ripper) via um
  loop de sacrifício.

**Nota geral:** o tipo escolhido pelo Roaming Throne é sempre o tema tribal
central do deck (Elf, Bear, o que for) — quase nunca ambíguo na prática.
Documentar a premissa no código se não for óbvio olhando a decklist.

---

## Teste de robustez antes de rodar o batch oficial

Adicionada a partir da sessão do Toph, the First Metalbender (2026-08-22):
construindo um simulador que cobre 16 motores diferentes (não 1 ou 2),
5 bugs reais só apareceram rodando um volume grande de partidas com seeds
aleatórias — nunca nos primeiros testes manuais com 1-2 seeds fixas:

- Estado nunca conjurado por estar numa zona (comando) que a lógica de
  casting não verificava.
- Loop infinito por mutar `battlefield`/lista equivalente durante uma
  iteração `for` sobre ela mesma (clone de token entrando na lista sendo
  iterada).
- `ValueError`/crash em efeitos que sacrificam/removem múltiplos
  permanentes de uma lista pré-computada, quando processar o primeiro
  dispara uma cadeia que já removeu o segundo por outro caminho.
- `RecursionError` por um efeito "copiar permanente" não excluir cópias/
  tokens do próprio gatilho que a criou (a carta real diz "outro
  permanente **não-token**" — a implementação inicial não tinha essa
  distinção).
- `RecursionError` por refatoração via find-and-replace em massa
  reescrever a própria linha *dentro* da função que estava sendo chamada
  em todos os outros lugares, criando autorrecursão.

**Prática obrigatória antes de considerar um simulador novo pronto pra
rodar o batch oficial:** rodar uma amostra grande (10.000-20.000 partidas)
com seeds sequenciais e um timeout curto por partida (ex:
`signal.alarm(2)` em Python) capturando exceções e travamentos, **antes**
de rodar o batch de n= pequeno que vira o resultado reportado. Só reportar
resultado depois de zero erros/travamentos nessa varredura.

---

## Checklist obrigatória de categorias de mecânica (não só cartas individuais)

Adicionada por pedido explícito do usuário (sessão do Beorn, 2026-08-28), depois
de eu entregar um simulador (`beorn_goldfish_v1.py`) que **não tinha nenhum
despacho de landfall**, apesar de 6 cartas do deck dependerem dele. Citação
literal: *"Como diabos vc criou um simulador que não leva em conta a porra do
Landfall??? Por tudo que é mais sagrado, acrescente uma maldita regra de
conferir TODAS AS MALDITAS INTERAÇÕES, ATIVAÇÕES e COMBOS do deck na porra do
simulador. Revise gatilhos, tokens, motores de draw e ramp, e os mana dorks,
mana rocks e lands que geram mana fixing em TODOS OS DECKS E SIMULADORES!!!!"*

O "Passo 0" da seção do Roaming Throne acima (varredura mecânica em
`oracle_text`, não de memória) já existia mas só era aplicado à carta que
estava sendo implementada no momento — não como checklist obrigatória pra
QUALQUER simulador, novo ou já existente. Generalizando: antes de considerar
**qualquer** simulador (novo ou em revisão) completo, rodar essa varredura pra
**cada uma** destas categorias, sobre o `oracle_text` real de toda a decklist:

1. **Landfall** — toda carta com "Landfall —" no oracle_text precisa de um
   despachante real chamado em TODO ponto onde um terreno entra em campo: o
   land-drop normal E qualquer terreno buscado por rampa (Cultivate, Nature's
   Lore, Sakura-Tribe Elder, Solemn Simulacrum, etc — a regra de landfall não
   distingue a origem do terreno).
2. **Mana dorks** (criaturas com habilidade de `{T}: Adicionar mana`) —
   conferir (a) se contam pra mana total/fontes coloridas do turno, E (b) se
   respeitam doença de invocação (não produzem mana no turno em que entram,
   CR 302.6) — criatura sem haste não usa habilidade de `{T}` no turno da ETB.
3. **Mana rocks** (artefatos de mana) — não têm doença de invocação (só
   afeta criaturas), mas conferir se o custo de ativação extra (ex: Cabal
   Coffers) e restrições de cor estão implementados corretamente, não só um
   "+1 mana" genérico.
4. **Lands/efeitos de mana fixing** — terrenos ou permanentes que mudam o tipo
   de mana disponível (ex: Yavimaya Cradle of Growth virando todo terreno em
   Floresta, Cavern of Souls/Secluded Courtyard/Haven condicionados a tipo de
   criatura — ver regra #6 do `user-standing-rules.md`) precisam entrar na
   contagem real de fontes por cor, não só "incolor" por padrão.
5. **Motores de draw** ("Whenever you cast/draw/creature enters... draw a
   card") — cada um precisa de um gatilho real, disparado no evento certo
   (cast vs. ETB são momentos diferentes; a maioria dos simuladores atuais
   trata os dois como intercambiáveis, o que é aceitável só se documentado).
6. **Motores de ramp** — incluindo os que buscam terreno específico (básica
   vs. Floresta vs. qualquer terreno — conferir contra o oracle_text exato,
   não assumir "qualquer terreno da lib" quando a carta diz "basic land" ou
   nomeia um tipo).
7. **Habilidades ativadas repetíveis** (token makers, sacrifice outlets,
   descarte-por-valor como Ayula's Influence) — se a carta tem um custo
   pagável mais de uma vez por turno/jogo, o simulador precisa decidir e
   documentar uma heurística de quando a IA ativa (não pode ficar de fora só
   porque "é ativada, não gatilho").
8. **Combos entre peças que já estão na decklist** — depois do passo 0 por
   carta individual, checar explicitamente se duas ou mais cartas já
   implementadas se combinam (ex: sac outlet + payoff de morte + motor de
   mana, ver o pacote Blood Artist/Zulaport do Edgar Markov) — um simulador
   pode ter cada carta implementada isoladamente e ainda assim errar a
   interação entre elas.
9. **Habilidades estáticas** (não são gatilho nem ativação — valem o tempo
   todo enquanto o permanente está em campo: anthems, custo reduzido,
   "criaturas que você controla são do tipo X", terrenos viram outro tipo,
   restrição/expansão de cor de mana, "não pode ser bloqueada", etc). Cada
   uma precisa estar aplicada de verdade em todo cálculo que ela afeta (ex:
   um anthem de +1/+1 tem que entrar em `BASE_POWER`/custo/combate em TODO
   lugar relevante, não só onde foi implementada primeiro) — não é
   suficiente ter a tag na definição da carta.
10. **Métricas básicas do relatório** — todo `run_batch`/resumo de simulador
    precisa reportar, de forma auditável e separada, pelo menos estas 5
    categorias agregadas, mesmo que o deck já tenha métricas específicas de
    carta: **ramp** (mana disponível/peças de aceleração), **draw** (compra
    extra além da normal do turno), **interaction** (remoção/proteção/
    interação com o oponente conjurada), **recursion** (recuperação de
    cartas do cemitério — pra mão, campo, ou topo da biblioteca: reanimação,
    tutor-de-volta, "return target card from your graveyard", etc — ver
    citação literal do usuário abaixo), **finisher/lethality** (taxa e turno
    médio de resolver um fechador de jogo). Se uma dessas 5 categorias não
    existe na decklist, documentar "0 cartas de X, categoria N/A" em vez de
    simplesmente omitir a métrica do relatório.

    Citação literal do usuário (2026-08-28), depois de eu reportar a
    checklist ampliada (estáticas + as 4 métricas originais) em Edgar
    Markov/Hei Bai: *"Vc precisa acrescentar a variável recursão e interação
    à lista de variáveis para avaliar, medir e registrar em todos os decks
    tb!"* — **recursão** entra como 5ª categoria de métrica básica (antes
    não estava na lista original de 4); **interação** já estava na lista,
    mas o reforço deixa explícito que precisa ser uma métrica agregada de
    verdade em TODO deck (não só citada como "N/A por arquitetura" sem uma
    linha própria no relatório) — todo deck com qualquer carta de
    remoção/proteção precisa de um número reportado pra ela, mesmo que o
    número seja 0 por design (goldfish solo sem oponente real).

11. **Cartas de face múltipla / modal (MDFC, transform, Room, Battle,
    Adventure, "Prepared")** — antes de registrar QUALQUER carta com "//"
    no nome (ou qualquer layout multi-face) no `CARD_DB`, consultar o campo
    `layout` real da API do Scryfall (não adivinhar pelo formato do nome) e
    verificar qual face é de fato jogável da mão:
    - **`modal_dfc`** (MDFC verdadeiro, ex: Agadeem's Awakening // Agadeem,
      the Undercrypt): as duas faces são independentemente jogáveis da mão
      — quem escolhe é o jogador no momento do cast/land-drop. Modelar as
      DUAS opções (mesmo que a escolha padrão seja sempre uma delas por
      falta de alvo real) — nunca registrar só uma face permanentemente sem
      checar se a outra faria diferença.
    - **`transform`** (ex: Ojer Taq // Temple of Civilization, Legion's
      Landing // Adanto): só a FRENTE é castável da mão — o verso só é
      alcançável via o gatilho real de transformação do jogo. Registrar a
      carta pela frente (tipo/custo/cor real dela), nunca direto pelo
      verso — isso seria simular uma ação ilegal (jogar como land/ativar
      uma carta que nunca foi conjurada), não só "perder valor".
    - **`split`** com mecânica de "Room" (ex: Funeral Room // Awakening
      Hall): permite destrancar a segunda porta depois, pagando o custo
      dela "as a sorcery" — não é um cast novo (não dispara gatilhos de
      "whenever you cast"), mas é uma ação real que precisa de dispatch.
    - **`battle`**: side do defensor com contadores de defesa, ataca-lo
      (do lado do jogador) exige um "attacking player" que esse tipo de
      simulador solo geralmente não modela — documentar explicitamente por
      que está fora de escopo, não silenciar.
    - **`prepare`** (ex: Emeritus of Woe // Demonic Tutor, Stensian
      Sanguinist // Exsanguinate): a carta entra "prepared" sob uma
      condição real (ver texto), permitindo conjurar uma cópia do verso
      SEM ter a carta física (mas ainda pagando o custo real dele, a menos
      que o texto diga "without paying its mana cost").
    - **Adventure**: o lado Instant/Sorcery pode ser conjurado primeiro
      (exila a carta, permite conjurar a criatura depois do exílio) — as
      duas metades são reais e call cada uma no tempo certo.

    Regra geral: **nunca registrar uma carta de face múltipla direto pela
    face "mais conveniente" de modelar sem antes confirmar, via `layout` da
    API, que essa é de fato uma face jogável da mão** — isso pode estar
    simulando uma ação ilegal do jogo inteiro, não só uma simplificação.

**Prática obrigatória:** antes de declarar QUALQUER simulador (novo ou já
existente, numa auditoria de revisão) completo, rodar essa checklist e citar
explicitamente, por categoria, quantas cartas da decklist se qualificam e se
cada uma tem implementação real — não só reportar "achei um bug, corrigi".
Se uma categoria não se aplica a um deck (ex: deck sem nenhuma carta de
landfall), documentar isso também ("0 cartas de landfall na lista, categoria
N/A"), pra deixar claro que a categoria foi checada e não só ignorada. Isso
vale **sempre**, em qualquer sessão, pra qualquer deck do repositório — não
só o deck sendo discutido no momento em que a regra foi criada ou reforçada.

---

<!-- Adicionar novas entradas abaixo conforme surgirem cartas com efeitos
     estruturais que exigem implementação explícita (não só tag) em qualquer
     simulador que as inclua. -->
