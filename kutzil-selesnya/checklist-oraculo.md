# Checklist cláusula-a-cláusula — Kutzil, Malamet Exemplar

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
