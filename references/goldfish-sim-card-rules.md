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

<!-- Adicionar novas entradas abaixo conforme surgirem cartas com efeitos
     estruturais que exigem implementação explícita (não só tag) em qualquer
     simulador que as inclua. -->
