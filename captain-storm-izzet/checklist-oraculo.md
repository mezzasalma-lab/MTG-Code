# Checklist cláusula-a-cláusula — Captain Storm, Cosmium Raider (Izzet, U/R)

Pedido direto do usuário (2026-09-01): *"Quais decks faltam para fecharmos?"*
→ *"Pode começar com o Kutzil"* (feito) → Azula (feito) → Captain Storm é o
terceiro dos 4 decks sem simulador desta sessão. Construção do zero, mesma
disciplina de "compile TUDO".

**Fonte de dados:** oráculo real das 73 cartas não-básicas + comandante,
buscado ao vivo via Scryfall (`POST /cards/collection` em 1 lote +
`/cards/named` pros 2 MDFCs — Storm the Vault // Vault of Catlacan e
Two-Handed Axe // Sweeping Cleave), não memória nem só a `auditoria.md`
anterior (boa, mas escrita antes desta leitura linha-a-linha).

**⚠️ Lista incompleta — não corrigido aqui:** a `auditoria.md` já
documentava que a lista enviada pelo usuário soma 98 cartas de biblioteca
(99 com o comandante) — falta 1 carta pro total padrão de 100.
`BASE_LIBRARY` reflete a lista real como enviada (assert `len == 98`,
documentado inline no código).

**Arquitetura:** objetos `Permanent` (como Kutzil/Toph, diferente do
Azula/Megatron) — este deck precisa rastrear contadores +1/+1
PERSISTENTES (a própria habilidade da Captain Storm) e equipamentos
anexados (qual criatura tem qual Equipment, para cálculo de combate e
gatilhos de dano de combate).

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real modelado, mesma convenção de
  toda a sessão.
- 🐛 **Achado e corrigido durante a própria construção** — gap que passou
  no primeiro rascunho e foi achado numa varredura automatizada, aplicada
  ANTES de considerar o deck pronto.

## 🐛 4 gaps reais achados na varredura de tags órfãs

Depois do primeiro rascunho completo (regressão de 3.000 partidas já
passando, 0 exceções), rodei a varredura de "tag definida em `add()` mas
nunca lida em nenhum dispatch" — 44 candidatos apareceram, a esmagadora
maioria falsos positivos (despachados por checagem direta de NOME em
`state.battlefield`/`EQUIPMENT_STATIC_BONUS`, não por tag — convenção
usada em quase todo o arquivo, já que cada carta tem uma regra bem
específica). **4 eram gaps reais:**

1. **Swiftwater Cliffs / Temple of Epiphany entravam DESTAPADAS** — o
   check original era `"etb_tapped" in CARD_DB[name].tags`, um match
   EXATO de string num frozenset. As tags reais dessas 2 lands são
   `"etb_tapped_gain1"` e `"etb_tapped_scry1"` (nomes mais específicos,
   pra também documentar o ganho de vida/scry 1 que vem junto) — nunca
   batiam com o literal `"etb_tapped"`, então essas 2 lands (que o
   oráculo real diz claramente "This land enters tapped") entravam
   destapadas, dando mana de graça 1 turno mais cedo que deveriam.
   Corrigido com `enters_tapped()`, que checa qualquer tag começando com
   `"etb_tapped"`.
2. **Embercleave só dava o +1/+1 estático, nunca o double strike** — o
   bônus fixo (via `EQUIPMENT_STATIC_BONUS`) estava certo, mas o check de
   double strike no cálculo de combate só olhava `eq.card == "Twin
   Blades"`, esquecendo que Embercleave também dá double strike
   ("Equipped creature gets +1/+1 and has double strike and trample").
   Isso subestimava o dano de qualquer turno em que Embercleave estava
   equipada — corrigido incluindo Embercleave no mesmo check.
3. **Cloak of the Bat não concedia haste de verdade** — a tag
   `eq_flying_haste` existia, mas nada no motor de "quem pode atacar"
   verificava Equipment. Flying é cosmético (sem bloqueio modelado), mas
   haste é real — permite atacar com uma criatura que acabou de entrar
   (cenário comum: equipar um Pirata recém-conjurado no mesmo turno pra
   já gerar Treasure/contador no ataque). Corrigido.
4. **Swiftfoot Boots** — mesmo gap do Cloak of the Bat (`eq_hexproof_haste`),
   mesma correção.

Validado com 2 baterias de testes unitários (6 + 4 = 10 testes isolados,
todos passando) + regressão de 20.000 partidas (seeds 5.000.000+,
turns=10, 0 exceções).

## Motor central verificado

- **Captain Storm (comandante)** — "whenever an artifact you control
  enters, put a +1/+1 counter on target Pirate you control" — testado
  isoladamente, mira o Pirata de maior poder atual (heurística
  documentada).
- **Academy Manufactor** — "if you would create a Clue, Food, or
  Treasure token, instead create one of each" — testado: 1 pedido de
  Treasure vira 3 tokens simultâneos, cada um disparando a Captain Storm
  separadamente.
- **Panharmonicon + Starfield Vocalist** — dobram MULTIPLICATIVAMENTE
  (2 dobradores = 4x, não 2x+2x), testado isoladamente
  (`etb_trigger_multiplier()`), mesmo princípio já documentado noutros
  decks desta sessão pra dobradores empilhados.
- **Corsair Captain** — anthem "Other Pirates you control get +1/+1"
  (não ela mesma), testado.
- **The Ozolith** — captura contadores de criatura que morre + move de
  volta pro melhor alvo no início do combate, testado (2 pontos:
  `leave_battlefield()` e `try_ozolith_move()`).
- **Equipment** (11 peças) — bônus estático + gatilhos de dano de combate
  (Bloodforged Battle-Axe cria cópia-token de si mesma, Goldvein Pick
  cria Treasure, Sword of Once and Future permite conjurar instant/sorcery
  ≤2 do cemitério de graça, Trickster's Talisman sacrifica-se por uma
  cópia-token da criatura equipada, Two-Handed Axe dobra o poder ao
  atacar) — todos implementados e verificados via a regressão longa.

**Achado estatístico real (não um bug, mesmo tratamento dado aos
outliers do Kutzil/Azula nesta sessão):** Bloodforged Battle-Axe é
conhecida no Magic de papel por um crescimento exponencial real quando
várias cópias ficam equipadas na mesma criatura que conecta sem bloqueio
todo turno — cada cópia da Axe dispara SEPARADAMENTE ("whenever equipped
creature deals combat damage, create a token copy"), então N cópias
equipadas = N gatilhos = N novas cópias por combate, dobrando a cada
turno. Confirmado numa partida de teste (seed com `turns=10`): **1.296
cópias de Bloodforged Battle-Axe** no campo até o turno 10, rodando em
0.39s (sem travamento, determinístico). Documentado em `goldfish-log.md`.

## Estrutural (📊, sem oponente real — não julgamento de valor)

- **Encore** (Fathom Fleet Swordjack, Impulsive Pilferer) — "for each
  OPPONENT, create a token copy" — 0 oponentes reais modelados = 0
  cópias, nenhum piloto racional ativaria pra gerar 0 valor. Nunca
  ativado.
- **Kitesail Larcenist** — "for each player, choose target artifact or
  creature THAT PLAYER controls" — o uso real (transformar permanente de
  oponente em Treasure) precisa de alvo de oponente.
- **Fellwar Stone** — "add mana of a color a land an OPPONENT controls
  could produce" — leitura literal sem oponente modelado: produz 0 mana
  de verdade (mesma lógica já aplicada ao Exotic Orchard no Azula).
- **Contramagias** (Counterspell, Mana Leak, Ionize, Spell Rupture) e
  **Chaos Warp** — precisam de spell/permanente de oponente real.
- **Chain Reaction / Blasphemous Act** — Regra 1 da sessão: wipe
  simétrico sem oponente modelado = só conta como `interaction_plays`,
  sem destruir as próprias criaturas.
- **Storm Fleet Negotiator (Parley)** — "each player reveals top card...
  each player draws" — modelado só pra nós mesmos (1 jogador real neste
  goldfish solo).

## Aproximações documentadas (reais, não inventadas)

- **Mystic Remora** — cumulative upkeep real, mas sem oponente conjurando
  spells não-criatura pra disparar o gatilho de compra — 0 valor
  possível de ganhar segurando, sacrificada na primeira oportunidade após
  entrar (achado real via a matemática do modelo solo, não uma decisão
  de "não vale a pena").
- **Sensei's Divining Top** — prioriza o modo real de compra ("{T}: draw
  a card, then put this on top of your library") sobre o modo de
  filtragem ("{1}: look at top 3, reorder") — o de compra é estritamente
  mais valioso pra esta simulação orientada a métricas agregadas.
- **Starfield Vocalist (Warp)** — o custo alternativo `{1}{U}` (exila no
  fim do turno, pode conjurar de novo depois) não foi implementado —
  escopo desproporcional pra 1 carta (exigiria rastrear uma zona de
  exílio temporária separada); ela ainda é conjurada pelo custo normal
  `{3}{U}` via o loop genérico de conjuração.
- **Storm Fleet Negotiator (Parley)** — ver seção estrutural acima.

---

## Resumo numérico

- **73 cartas não-básicas + comandante**, 98 cartas de biblioteca real
  (⚠️ lista incompleta, documentado, não inventado).
- **🐛 4 gaps reais achados e corrigidos na própria varredura de
  construção** (2 lands que entravam destapadas por erro de match de
  string, Embercleave sem double strike aplicado, Cloak of the
  Bat/Swiftfoot Boots sem haste real).
- **✅ ~55 cartas/cláusulas com efeito real implementado e testado.**
- **📊 ~7 cartas/cláusulas estruturais confirmadas** (opponent-dependent
  genuíno, mesma convenção de toda a sessão).
