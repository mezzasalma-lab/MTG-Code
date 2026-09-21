# Checklist cláusula-a-cláusula — Kutzil, Malamet Exemplar

## Porte completo do modo de resiliência (interação de oponente) + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** *"Agora faz o Kutzil"* — seguindo diretamente o porte
concluído no Nekusar, Azula, Beorn, Thranduil e Ms. Bumbleflower (mesma
sessão, mesmo protocolo). Este deck nunca tinha o modo de resiliência
atual — porte completo do zero, nascendo já com a correção de CR 903.9a
nativa desde a 1ª linha.

**Arquitetura:** `state.battlefield` aqui é lista de objetos
`Permanent` (`uid`, `card`, `counters`...) — mas diferente do Bumbleflower/
Kutzil-anterior, `perm.card` é o próprio objeto `Card` (não uma string de
nome), então `remove_permanent` compara por `perm.card.name`.
`remove_permanent` **envolve** a `leave_battlefield` já existente (que já
tratava Rancor voltando pra mão, Goldvein Hydra criando Treasures, Puca's
Covenant recursão, e transferência de contadores pro Ozolith) e adiciona
só o tratamento do comandante (CR 903.9a — cemitério de verdade primeiro,
CR 700.4/704, só depois removida de lá pra representar a zona de
comando). `life_total` já existia ativo neste arquivo (não precisou ser
adicionado, diferente do Beorn/Thranduil/Bumbleflower).

## Achado real CRÍTICO: `Damning Verdict` já deixava a comandante "fantasma" em partidas de modo PADRÃO — não era um bug latente do modo de resiliência, já acontecia hoje — 2026-09-21

**Gatilho:** auditoria de pontos de sacrifício/destruição pré-existentes
(disciplina obrigatória antes de construir o modo de resiliência, Regra
#6 do CLAUDE.md) — grep de `leave_battlefield(` achou 3 call sites reais
(Summon: Fenrir capítulo III, Warp do Broodguard Elite, e **Damning
Verdict**). Os 2 primeiros só afetam a própria carta que os contém, sem
risco. **Damning Verdict** ("Destroy all creatures with no counters on
them") destrói toda criatura própria com 0 contadores — `should_cast_
damning_verdict()` já tinha uma heurística real ("só vale a pena se a
perda for pequena"), mas **nunca excluía a comandante da contagem**.
Kutzil é criatura recém-conjurada com 0 contadores até ganhar o 1º buff
— exatamente o perfil que esse próprio wrath mata.

**Diferente de todos os achados anteriores desta sessão (Beorn/
Thranduil), este bug NÃO era estrutural/latente — já estava ATIVO em
partidas de modo PADRÃO**, sem precisar do modo de resiliência pra se
manifestar: `leave_battlefield` nunca tratava o comandante (sem
`commander_in_play`/`commander_uid` reset), então toda vez que Damning
Verdict matava a própria Kutzil, ela ia pro cemitério e **ficava lá
presa como "fantasma"** — `state.commander_in_play` continuava `True`
(nunca resetado), mas ela não estava fisicamente em lugar nenhum útil
(nem battlefield, nem recastável — `main_phase`'s `if not state.
commander_in_play and can_cast(...)` nunca dispararia de novo, já que a
flag mentia dizendo que ela "ainda está em campo"). Confirmado ao vivo:
6 de 10.000 partidas (seed_base 1000000) tinham esse estado quebrado
ANTES do fix.

**Corrigido:**
1. `should_cast_damning_verdict()` agora recusa conjurar enquanto isso
   mataria a própria comandante — diferente de um sacrifice outlet com
   pool de candidatos escolhido pelo piloto (Beorn/Thranduil), "destroy
   all creatures with no counters" não tem exceção nenhuma no oráculo
   real, então a única linha de jogo racional é **nunca conjurar**
   enquanto a perda incluiria o motor central de draw (não dá pra
   "proteger" ela do efeito sem trapacear a carta).
2. `remove_permanent()` novo (envolve `leave_battlefield`) trata o
   comandante corretamente pra qualquer OUTRA fonte de remoção que vier
   a existir (o modo de resiliência).

**Validação:** bit-identidade em modo padrão (20.000 seeds, seed_base
1000000) contra o commit anterior: **13/20000 mismatches (0,07%)** —
divergência real e esperada, confirmada via trace direto da seed
1002983: `commander_in_play=True` mas Kutzil ausente do battlefield E
presente no cemitério na versão ANTIGA (o estado fantasma descrito
acima); na versão corrigida ela nunca chega a morrer (Damning Verdict
não é conjurada), continua em campo, e segue batendo (`commander_
damage_dealt` 26→31 no mesmo seed). Comparação A/B agregada (10.000
seeds): `proxy_damage_total`/`counters_placed_total`/`commander_damage_
dealt`/`cards_drawn_extra` todos dentro de margem de ruído mínima,
"comandante nunca conjurada" idêntico (2,52%/2,52%), e o contador direto
de "comandante fantasma" cai de **6/10000 pra 0/10000**.

## Achado real ADICIONAL: taxa de comandante (CR 903.8) tinha o contador declarado mas nunca era incrementado nem lido (mesma classe do achado no Bumbleflower) — 2026-09-21

**Gatilho:** ao inserir o contra-ataque em `cast_card`, notei que
`GameState.commander_cast_count` **já existia** (campo declarado) — mas
grep confirmou **0 outras ocorrências** no arquivo inteiro: nunca era
incrementado, nunca era lido em `effective_cost()`. Só passou a importar
de verdade agora que o modo de resiliência pode genuinamente remover o
comandante e forçar um recast.

**Corrigido:** `effective_cost()` agora soma `2 *
state.commander_cast_count` ao MV base quando `name == COMMANDER`;
`cast_card()` incrementa o contador logo após pagar o custo (antes do
contra-ataque, já que CR 903.10a/608.2b contam "cast", não "resolved").

**Validação:** 3 testes dirigidos confirmando `effective_cost(COMMANDER)`
sobe exatamente +2 por `commander_cast_count` (0→3, 1→5, 3→9).

**Nota de determinismo:** diferente do Azula/Bumbleflower, este arquivo
**não tinha** bug de RNG não-seedado — `mulligan(rng)` já recebia e usava
o `random.Random(seed)` corretamente (grep confirmado: única outra
ocorrência de `random.` no arquivo inteiro era a própria criação do RNG
em `simulate_one`). Nenhum fix de determinismo foi necessário aqui.

**Resumo da validação completa:** regressão de 20.000 partidas em modo
de resiliência: 0 exceções, 0 comandantes presos no cemitério/fantasma,
52,76% das partidas com `commander_cast_count >= 2` (recast pagando a
taxa CR 903.8 depois de removida). 23 testes dirigidos: `remove_
permanent` no comandante (não presa no cemitério, `commander_in_play`/
`commander_uid` resetados), `remove_permanent` em criatura comum (vai
pro cemitério normalmente), transferência de contadores pro Ozolith
preservada, taxa de comandante em `effective_cost` (3 casos), `cast_
card` debita taxa e incrementa contador, contra-ataque intercepta o
cast, `try_smart_opponent_wipe` inclui o comandante nos alvos de
criatura, `should_cast_damning_verdict` recusa/aprova corretamente (2
casos), mulligan determinístico (300 amostras).

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai (detalhes de cada um no topo dos
respectivos `checklist-oraculo.md`). Kutzil foi um dos primeiros
simuladores construídos do zero nesta sessão (antes de Azula/Captain
Storm) e já tinha passado por 1 rodada de auditoria na própria construção
(12 gaps achados por varredura de tags órfãs, ver seção abaixo) — mesmo
assim esta rodada, linha-a-linha contra o oráculo real via Scryfall (91
cartas não-básicas + comandante, 1 lote de `/cards/collection` + 4
`/cards/named?fuzzy=` pros MDFCs), achou **11 gaps reais novos**, a
maioria no próprio motor central de contadores (`place_counters()`) e no
modelo de mana — exatamente o tipo de coisa que só aparece numa 2ª
passada depois que o motor já está "estável" e ninguém mais olha pra ele
com ceticismo.

**Achado principal — o próprio motor central de contadores tinha um gap
de gating:** Hardened Scales / Michelangelo / Branching Evolution / The
Earth Crystal dizem todos "...put on a **creature** you control"
(restrito), mas "Ozolith, the Shattered Spire" diz "an **artifact or
creature** you control" (mais amplo) — o código original aplicava os 4
efeitos restritos sem checar se o alvo (`perm`) era de fato uma criatura.
Nunca deu errado até agora porque todo alvo real de `place_counters()`
sempre foi uma criatura — mas o 2º achado abaixo (transferência de
contadores pro próprio "The Ozolith") introduz o primeiro alvo real
não-criatura, e sem o gate os 4 efeitos restritos vazariam pra ele
incorretamente. Corrigido com `is_creature(perm)` / "artifact or
creature" checados explicitamente dentro do motor.

**11 gaps reais encontrados e corrigidos:**

1. **"The Ozolith" (a carta separada, distinta de "Ozolith, the
   Shattered Spire" — as duas estão na lista) recebia contadores de
   criaturas que morrem via atribuição direta (`+=`), sem passar pelo
   motor central `place_counters()`.** Oráculo real: "put those
   counters on The Ozolith" É um evento de "put a counter" (CR 616),
   sujeito aos MESMOS efeitos de substituição de qualquer outro —
   inclusive a própria estática de "Ozolith, the Shattered Spire" (que
   vale pra si mesma, já que é "artifact or creature") e o Innkeeper's
   Talent nível 3. Passava direto reto, sem nenhum multiplicador.
   Mesmo bug no gatilho equivalente de **Broodguard Elite** ("When this
   creature leaves the battlefield, put its counters on target creature
   you control"). Corrigido roteando ambos por `place_counters()`
   (com o gating do achado principal acima pra não vazar Hardened
   Scales/Michelangelo indevidamente).
2. **O mesmo bloco só disparava com `to_graveyard=True`** — mas o
   oráculo real de ambas as cartas diz "leaves the battlefield" (não
   "dies"), então deveria disparar em QUALQUER saída de campo, inclusive
   exílio (relevante agora que o Warp de Broodguard Elite — achado #8 —
   exila a própria criatura no end step). Corrigido junto com o #1.
3. **Wakka, Devoted Guardian — "Blitzball Captain" ("at the beginning of
   your end step, if a counter was put on Wakka this turn...")** só
   disparava se o contador viesse especificamente do gatilho de dano de
   combate da própria Wakka — qualquer OUTRA fonte real de contador
   (Ozolith movendo pra ela, Luminarch Aspirant mirando nela, Requisition
   Raid acertando todo o board) não setava a flag. Centralizado dentro
   do próprio `place_counters()` (único ponto real de "put a counter on
   Wakka"), cobrindo QUALQUER fonte — mesma classe de bug do Edgar
   Markov (cascata de gatilho só ligada num dos vários pontos reais).
4. **Kodama of the West Tree — "modified creature" (CR 400.7 = tem
   Equipment, Aura OU contador)** só checava `p.counters > 0`, ignorando
   Rancor (a única Aura real desta lista). Uma criatura só com Rancor (0
   contadores) também é "modified" e deveria disparar a busca de
   terreno básico no dano de combate. Corrigido incluindo
   `p.has_rancor`.
5. **District Mascot — "Whenever this creature attacks while saddled,
   put a +1/+1 counter on it."** 100% ausente — `try_saddle()` já
   marcava `.saddled=True`, mas nada no combate lia isso pra aplicar o
   bônus. Tag `saddle1_attack_counter` confirmada órfã (varredura
   automatizada). Corrigido no loop de atacantes de `combat_step()`.
6. **Ornery Tumblewagg — "Whenever this creature attacks while saddled,
   double the number of +1/+1 counters on target creature."** Mesmo
   padrão, 100% ausente (tag `saddle2_attack_double` órfã). Ruling real:
   "double the number of counters" conta como "put a counter" pra
   efeitos de substituição — implementado via `place_counters()` com
   `base_amount` = contadores já presentes no alvo (sujeito aos mesmos
   multiplicadores de novo, corretamente).
7. **Requisition Raid — Spree, custo real cobrado errado.** O `mv`
   registrado (1, só o `{W}` base impresso) estava sendo usado como o
   custo INTEIRO da conjuração, mas o único modo escolhido de verdade
   (`+ {1} — put a +1/+1 counter on each creature target player
   controls`, o único com valor real sem oponente) cobra `{1}`
   ADICIONAL por modo — custo real é `{W}+{1}=2`, não `{W}=1`. Corrigido
   em `effective_cost()`.
8. **Broodguard Elite — Warp {X}{G} 100% ausente.** Só o hardcast
   normal (`{X}{G}{G}`) funcionava (campo `warp_pending` órfão, tag
   `warp` órfã, `exile_warp` nunca populado). Warp é estritamente melhor
   aqui: custa 1 pip a menos E — ao entrar de novo depois de exilada e
   reconjurada num turno futuro — redispara TODOS os ETBs reais de novo
   (The Great Henge, Railway Brawler, Champion of Lambholt, Selvala).
   Implementado com o mesmo critério de prioridade já usado pro Plot do
   Railway Brawler (hardcast normal tem prioridade se a mana alcançar;
   Warp só entra com a sobra) — `try_warp_broodguard()` +
   `try_recast_warp_exile()` (essa última paga o custo NORMAL de novo,
   diferente do Plot que é de graça).
9. **Restoration Seminar — Paradigm ("After you first resolve a spell
   with this name, you may cast a copy of it from exile without paying
   its mana cost at the beginning of each of your first main phases")
   100% ausente.** Só a 1ª resolução (paga, `{5}{W}{W}`) existia — o
   motor de recorrência GRÁTIS a cada turno seguinte, que é o ponto real
   da carta, nunca disparava. Corrigido com uma flag
   `restoration_seminar_active` + chamada no início de `main_phase()`
   a partir do turno seguinte à 1ª resolução real.
10. **Selvala, Heart of the Wilds — "{G}, {T}: Add X mana..."** o `{T}`
    já era pago (`selvala.tapped=True`), mas o pip `{G}` do próprio
    custo de ativação nunca era debitado — ela rendia X mana LÍQUIDO em
    vez de X-1. Mesma classe de bug do Hei Bai (custo real de uma
    habilidade nunca cobrado). Corrigido debitando 1 de
    `mana_spent_this_turn` ao usá-la.
11. **7 habilidades ativadas com pip colorido no custo nunca checavam a
    COR disponível, só o total genérico de mana** — District Mascot
    (`{1}{G}`), Hopeful Initiate (`{2}{W}`), Maester Seymour
    (`{3}{G}{G}`), Lion Sash (`{W}`), Ozolith activated (`{1}{G}`) e os
    2 níveis do Innkeeper's Talent (`{G}` / `{3}{G}`) — todas ativavam
    mesmo sem nenhuma fonte verde/branca real disponível, desde que
    houvesse mana genérica suficiente. Baixo impacto prático (deck é
    G/W denso em fontes de cor), mas real — corrigido com
    `color_sources(state, "G"/"W")` em cada uma.

**Rishkar, Peema Renegade — 2 correções relacionadas no modelo de
mana** (não contadas nos 11 acima, tratadas junto por serem a mesma
carta): (a) a mana que suas criaturas-com-contador produzem
(`"{T}: Add {G}"`) já era contada no total genérico (`total_mana()`),
mas NUNCA no requisito de cor verde (`color_sources`/`green_sources`) —
um board só com criaturas-Rishkar destapadas (sem land verde nenhuma)
não conseguia pagar um pip `{G}` de verdade mesmo tendo mana verde
disponível de fato; (b) o cálculo original contava TODA criatura com
contador, inclusive as que já têm sua PRÓPRIA habilidade de mana
(Llanowar Elves, Fyndhorn Elves, Avacyn's Pilgrim, Birds, Biophagus,
Delighted Halfling) — um permanente só tem 1 `{T}`, não pode pagar as 2
habilidades ao mesmo tempo, então isso inflava `total_mana()`. Ambas
corrigidas em `rishkar_mana_bonus()` / `green_sources()`.

**Considerado e deliberadamente NÃO implementado (decisão de design
documentada, não gap deixado pra trás):** Lion Sash — Reconfigure `{2}`
+ "Equipped creature gets +1/+1 for each +1/+1 counter on this
Equipment." Reconfigurar só MOVE o mesmo poder total de Lion Sash
(criatura) pra outra criatura (equipada) — neste goldfish sem remoção de
oponente modelada, o dano proxy total de combate é idêntico dos dois
jeitos, mas ficar DESANEXADA mantém Lion Sash como um corpo atacante A
MAIS (nunca pior). Ficar sempre desanexada é a linha estritamente ≥
melhor aqui — documentado inline em `activate_abilities()`.

**Validação:** smoke test (99 nomes no `CARD_DB`, 99 cartas na
`BASE_LIBRARY`, 0 desconhecidas/duplicadas) + 2.000 partidas antes/depois
(mesma seed, ver `goldfish-log.md` pra tabela) + 20.000 partidas de
regressão (2 rodadas, seeds 9.000.000+ e 4.200.000+, turns=10): **0
exceções em ambas**. 20 testes unitários dirigidos (1 arquivo,
`kutzil_fix_tests.py`) confirmaram cada uma das 11 correções
isoladamente — inclusive o caso sutil de que "The Ozolith" e "Ozolith,
the Shattered Spire" são 2 cartas DIFERENTES na lista (a transferência
de contadores é uma, o dobrador estático é a outra), e que Hardened
Scales corretamente NÃO vaza pro artefato "The Ozolith" mas continua
aplicando normal a criaturas.

---

Pedido direto do usuário (2026-09-02): *"Pode começar com o Kutzil"* —
um dos 4 decks desta pasta sem simulador nenhum ainda (construção do
zero, não auditoria de um arquivo existente). Mesma disciplina de
"compile TUDO" aplicada aos outros 13 simuladores desta sessão.

**Fonte de dados:** oráculo real de todas as 92 cartas (91 não-básicas +
comandante) buscado ao vivo via Scryfall (`POST /cards/collection` em 2
lotes + `/cards/named?fuzzy=` pros 4 MDFCs que não resolveram no lote),
não memória nem a `auditoria.md` anterior (que é boa, mas foi escrita
antes desta leitura linha-a-linha e não é a fonte de verdade aqui).

**Arquitetura:** ao contrário da maioria dos simuladores desta sessão
(lista de nomes), este arquivo usa objetos `Permanent` (card + counters
+ tapped + campos extras) — o motor central de +1/+1 counters e o
próprio gatilho de compra da Kutzil ("power greater than its base
power") exigem rastrear poder atual vs. impresso por criatura
específica. Ver docstring do cabeçalho do `.py` pra detalhamento
completo do motor de multiplicadores de contador (`place_counters()`).

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real modelado neste goldfish solo
  (removal/interaction genuinamente dependente de alvo alheio), mesma
  convenção de toda a sessão.
- 🐛 **Achado e corrigido durante a própria construção** — gap que
  passou no primeiro rascunho e foi achado numa varredura automatizada
  de tags órfãs (mesmo método usado nas auditorias dos outros 13 decks),
  aplicada aqui ANTES de considerar o deck pronto.

## 🐛 12 gaps achados e corrigidos durante a construção (varredura de tags órfãs)

Depois do primeiro rascunho completo (regressão de 20.000 partidas já
passando, 0 exceções), rodei a mesma varredura automatizada de "tag
definida em `add()` mas nunca lida em nenhum dispatch" usada nas
auditorias dos outros decks — 13 candidatos apareceram, 12 eram gaps
reais (1 falso positivo: `green_cost_reduce`, aplicado ao custo de
OUTRAS cartas, não a si mesma — já estava correto):

1. **The Great Henge** — *"This spell costs {X} less to cast, where X
   is the greatest power among creatures you control."* Sem essa
   redução, uma carta de 9 mana ficava praticamente incastável numa
   lista de curva baixa. Corrigido em `effective_cost()`.
2. **Managorger Hydra** — *"Whenever a player casts a spell, put a +1/+1
   counter on this creature."* Sem oponente real, mas vale pra QUALQUER
   spell nossa (não só criatura). Corrigido com hook central
   `on_spell_cast()`, chamado em toda conjuração (paga, de graça via
   hideaway, ou Plot).
3. **Walking Ballista** — *"{4}: Put a +1/+1 counter..." + "Remove a
   +1/+1 counter: deals 1 damage to any target."* Corrigido: mana sink
   real + converte contadores excedentes (≥5, mantém piso de 4) em dano
   proxy.
4. **Beast Whisperer** — *"Whenever you cast a creature spell, draw a
   card."* Motor de draw real 100% ausente. Corrigido no mesmo hook
   `on_spell_cast()`.
5. **Goldvein Hydra** — *"When this creature dies, create a number of
   tapped Treasure tokens equal to its power."* Corrigido em
   `leave_battlefield()`.
6. **Puca's Covenant** — *"Whenever a creature you control with a
   counter on it dies, you may return another target permanent card
   with mana value ≤ counters on that creature from your graveyard to
   your hand. Once each turn."* Corrigido em `leave_battlefield()`.
7. **Tale of Katara and Toph** — *"Creatures you control have 'whenever
   this creature becomes tapped for the first time during each of your
   turns, put a +1/+1 counter on it.'"* Corrigido pro caso mais comum e
   valioso (atacar, em `combat_step()`) — outras fontes de tap (dorks
   pra mana, saddle) não re-hookam este gatilho, exigiria envolver todo
   lugar que seta `perm.tapped = True` no arquivo, custo desproporcional
   pra 1 carta — documentado no código, não esquecido.
8. **Abandoned Air Temple** — *"{3}{W}, {T}: Put a +1/+1 counter on each
   creature you control."* Corrigido em `activate_abilities()`.
9. **Ba Sing Se** — *"{2}{G}, {T}: Earthbend 2."* (terreno vira criatura
   0/0 com haste, +2 contadores, ainda é terreno). Aproximado: poe 2
   contadores no melhor alvo, sem construir o motor completo de
   earthbend (land-vira-criatura-morre-volta) usado no
   `toph_goldfish_v1.py` — única carta desta lista com esse texto,
   escopo desproporcional pra 1 carta. Ganho real de contadores
   preservado, só a nuance "ainda é terreno" fica de fora.
10. **Lion Sash** — *"{W}: Exile target card from a graveyard. If
    permanent, put a +1/+1 counter."* Sem cemitério de oponente, exila
    do PRÓPRIO cemitério (a carta de menor mv, preservando os melhores
    alvos de recursão pro Restoration Seminar/Puca's Covenant).
11. **Mosswort Bridge** — Hideaway 4 + *"{G}, {T}: play the exiled card
    free if creatures you control have total power ≥ 10."* Corrigido
    (mesmo padrão do Collector's Cage, já correto desde o rascunho).
12. **Hushwood Verge** — *"{T}: Add {W}. Activate only if you control a
    Forest or a Plains."* Estava tratada como incondicional
    (`produces={"G","W"}` genérico) — corrigido pra checar a condição
    real em `white_sources()`.

Validado com 3 baterias de testes unitários (15 + 6 + 8 = 29 testes
isolados, todos passando) + regressão de 20.000 partidas repetida a
cada rodada de correção (seeds 2000000+, 3000000+, 4000000+, 5000000+,
6000000+, turns=10, 0 exceções em todas). Ver `goldfish-log.md` pra
métricas antes/depois de cada rodada de correção.

## Motor central verificado

- **place_counters()** — 6 multiplicadores reais (Hardened Scales +1,
  Michelangelo +1, Ozolith +1, Branching Evolution x2, The Earth Crystal
  x2, Innkeeper's Talent nível 3 x2), empilhados na ordem que maximiza o
  total real (aditivos primeiro, CR 616) — testado isoladamente
  (base 1 → 16 com os 5 multiplicadores simultâneos).
- **Botanical Brawler / Generous Pup / Mikey & Leo / Terrasymbiosis** —
  os 4 gatilhos reativos a "contador colocado" (1x/turno cada onde a
  carta especifica), testados isoladamente.
- **Kutzil** (comandante) — draw real condicionado a "poder efetivo >
  poder base" em dano de combate, testado.
- **Damning Verdict** — única exceção real a "wipe simétrico sempre 📊"
  desta sessão: destrói de verdade as próprias criaturas sem contador,
  mas só conjurada quando a perda é pequena (heurística testada:
  `should_cast_damning_verdict()`).
- **Rancor** — +2/+0 permanente via `aura_power`, volta pra mão quando a
  criatura enchant morre (testado).

## Estrutural (📊, sem oponente real — não julgamento de valor)

- **Esper Sentinel** — taxa contra spell de OPONENTE.
- **Boseiju, Who Endures / Eiganjo, Seat of the Empire** — Channel exige
  alvo de oponente (artefato/encantamento/terreno alheio; criatura
  atacando/bloqueando de oponente).
- **Path to Exile / Swords to Plowshares / Kabira Takedown / Bridgeworks
  Battle (modo fight) / Requisition Raid (modos destroy) / Witch
  Enchanter ETB / Wakka (modo destroy artifact) / District Mascot e
  Hopeful Initiate (ativadas destroy)** — contam como `interaction_plays`
  (metrica de interação), sem alvo de oponente real pra destruir de
  verdade.
- **Champion of Lambholt (estática "can't block")**, **Sphere Grid
  (unlock reach/trample)**, **Training Regimen/Duskshell Crawler
  (trample grant)**, **Kodama modified-trample**, **Urdnan
  (first/double strike)** — sem bloqueio de oponente modelado; o
  ganho REAL de contador/dano proxy dessas cartas está implementado, só
  o efeito puramente cosmético de combate (que não muda o total sem
  bloqueadores) fica de fora.

---

## Resumo numérico

- **95 cartas únicas** (comandante + 94 de biblioteca, `lista.md`).
- **🐛 12 gaps achados e corrigidos na própria varredura de construção.**
- **✅ ~80 cartas com efeito real implementado e testado.**
- **📊 ~10 cartas/cláusulas estruturais confirmadas** (opponent-dependent
  genuíno, mesma convenção de toda a sessão).
