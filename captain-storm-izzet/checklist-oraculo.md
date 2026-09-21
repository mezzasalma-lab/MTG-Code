# Checklist cláusula-a-cláusula — Captain Storm, Cosmium Raider (Izzet, U/R)

## Porte completo do modo de resiliência (interação de oponente) + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** *"Então implemente ele tb"* — último dos 18 decks com
simulador desta sessão a receber o porte (depois de Nekusar, Azula,
Beorn, Thranduil, Ms. Bumbleflower e Kutzil). Este deck nunca tinha o
modo de resiliência atual — porte completo do zero, nascendo já com a
correção de CR 903.9a nativa desde a 1ª linha.

**Arquitetura:** `state.battlefield` é lista de objetos `Permanent`
(`uid`, `card`, `counters`...) com `perm.card` como STRING de nome
(diferente do Kutzil, mais parecido com o Beorn/Thranduil).
`remove_permanent` **envolve** a `leave_battlefield` já existente (que
já tratava equipamentos desanexados, transferência de contadores pro
Ozolith, "death_treasure", Tarrian's Soulcleaver e `descended_this_turn`
corretamente) e adiciona só o tratamento do comandante (CR 903.9a —
cemitério de verdade primeiro, CR 700.4/704, só depois removida de lá
pra representar a zona de comando).

## Achado real CRÍTICO: `commander_uid` ficava obsoleto após blink real (Ghostly Flicker/Planar Incision), zerando silenciosamente o rastreio de CR 903.10a — subestimava a win-condition primária do deck em ~2,5 pontos percentuais — 2026-09-21

**Gatilho:** auditoria de pontos de saída-e-retorno de campo
pré-existentes (disciplina obrigatória antes de construir o modo de
resiliência, Regra #6 do CLAUDE.md) — `Ghostly Flicker` ("blink up to 2
target artifacts/creatures/lands, choosing the highest MV first") e
`Planar Incision` (blink do artefato/criatura de maior MV + 1 contador)
são blinks LEGÍTIMOS (exílio-e-retorno na mesma resolução, não é caso de
CR 903.9a — a permanente nunca "morre" de verdade). Mas `enter_
battlefield` sempre cria um `Permanent` **NOVO com `uid` novo**, e
`state.commander_uid` (usado por `combat_step` para rastrear CR 903.10a
— "21+ de dano de combate da MESMA fonte comandante") nunca era
atualizado depois do blink. Se Captain Storm fosse um dos alvos
escolhidos (ela é MV2 — plausível quando o board não tem muita coisa de
MV mais alto), `state.commander_uid` ficava permanentemente apontando
pra um `uid` que não existe mais em `state.battlefield`, e **todo dano
de combate dela dali em diante parava de ser contado**, silenciosamente,
sem nenhum erro/exceção.

**Diferente de todos os achados anteriores desta sessão, este bug não
tinha relação nenhuma com sacrifício/morte — a comandante nunca saía de
campo de verdade, só trocava de identidade (`uid`) no meio de uma
resolução legítima**, e mesmo assim quebrava CR 903.10a de forma
totalmente silenciosa (sem exceção, sem log óbvio — só um número que
parava de subir).

**Corrigido:** nos 2 pontos reais de blink (`ghostly_flicker`/
`planar_incision` em `cast_instant_sorcery`), captura-se `was_commander
= (alvo.uid == state.commander_uid)` antes do `leave_battlefield`, e
depois do `enter_battlefield` recriar o Permanent, `state.commander_uid`
é atualizado pro `uid` NOVO quando `was_commander` for verdadeiro.

**Validação:** bit-identidade em modo padrão (20.000 seeds, seed_base
1000000) contra uma versão do commit anterior patcheada com APENAS o
fix de determinismo (isolando o efeito puro deste fix + o da taxa CR
903.8): **816/20000 mismatches (4,08%)** — a maior divergência de
qualquer deck desta sessão, e legítima: confirmada via trace direto da
seed 1000005 (`commander_uid` registrado=3 mas o Permanent real da
Captain Storm em campo tinha `uid`=7 na versão ANTIGA —
`commander_damage_dealt` travado em 3 pra sempre a partir do blink; na
versão corrigida, `commander_uid` bate com o `uid` real, e o dano
acumulado sobe pra 42, cruzando o threshold de 21 e disparando
`commander_damage_win=True`). Comparação A/B agregada (10.000 seeds)
confirma que NENHUMA outra métrica se move fora de ruído (`proxy_damage_
total`/`counters_placed_total`/`treasures_created_total`/`cards_drawn_
extra`/`etb_doubler_triggers_total` idênticos) — só as métricas
DIRETAMENTE ligadas ao dano da comandante mudam, como esperado: contador
direto de "`commander_uid` obsoleto" cai de **409/10000 (4,09%) pra
0/10000**, e **`commander_damage_win` sobe de 81,70% pra 84,17%** — a
win-condition PRIMÁRIA deste deck estava sendo subestimada em ~2,5
pontos percentuais por um bug silencioso de rastreio de identidade, não
por qualquer limitação real do deck.

## Achado real ADICIONAL: taxa de comandante (CR 903.8) tinha o contador declarado e incrementado, mas nunca era somada ao custo (mesma classe do Bumbleflower/Kutzil) — 2026-09-21

**Gatilho:** `GameState.commander_cast_count` já existia e era
incrementado em `try_cast_commander` — mas só era LIDO em 1 lugar
(`combat_step`, bônus de ataque de Captain Vargus Wrath, um efeito real
de carta sem relação com taxa de comandante). `effective_cost()` nunca
somava a taxa real de CR 903.8.

**Corrigido:** `effective_cost()` agora soma `2 *
state.commander_cast_count` ao MV base quando `name == COMMANDER`.

**Nota de determinismo:** mesma classe de bug já documentada no Azula/
Bumbleflower — `mulligan(state)` reembaralhava via `random.shuffle()`
(módulo GLOBAL) em vez de um RNG seedado. Confirmado empiricamente: 723
de 3.000 partidas (24,1%) davam resultado diferente rodando a MESMA
seed duas vezes. Corrigido adicionando `rng: Optional[random.Random] =
None` ao `GameState` e trocando `mulligan()` pra `state.rng.shuffle`.
0/3.000 partidas não-determinísticas após o fix.

**Resumo da validação completa:** regressão de 20.000 partidas em modo
de resiliência: 0 exceções, 0 comandantes presos no cemitério, 0
`commander_uid` obsoleto, 46,11% das partidas com `commander_cast_count
>= 2` (recast pagando a taxa CR 903.8 depois de removida). 25 testes
dirigidos: `remove_permanent` no comandante (não presa no cemitério,
`commander_in_play`/`commander_uid` resetados), `remove_permanent` em
criatura comum, transferência de contadores pro Ozolith preservada,
taxa de comandante em `effective_cost` (3 casos), `try_cast_commander`
debita taxa e incrementa contador, contra-ataque intercepta o cast
(mana/taxa/gatilho-de-cast já contam, comandante nunca entra em campo),
`try_smart_opponent_wipe` inclui o comandante nos alvos, Ghostly Flicker
mantém `commander_uid` sincronizado após blink (3 casos), mulligan
determinístico (300 amostras).

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn: oráculo real via Scryfall pras 73 cartas + comandante, comparado
cláusula-por-cláusula contra o código já existente.

**Achado principal — sistêmico, afeta as 11 peças de Equipment:**
`try_equip()` nunca cobrava NENHUM custo de Equip, em lugar nenhum do
arquivo — toda peça anexava de graça, tanto ao ser conjurada quanto ao
ser re-anexada depois. O parâmetro `free: bool` da função nem era lido
no corpo dela (dead parameter). Isso inflava sistematicamente a
eficiência de mana do pacote inteiro de Equipment (Equip custa de {0} a
{4} nas 11 peças). Oráculo real: só **Twin Blades** e **Embercleave**
têm "When this Equipment enters, attach it to target creature you
control" — só essas 2 (das 11) genuinamente anexam de graça na primeira
vez. As outras 9 exigem a habilidade de Equip normal (ativada, `{custo}:
Attach to target creature you control. Equip only as a sorcery`) tanto
na primeira vez quanto em qualquer re-anexação.

**Corrigido:** `try_equip()` virou 2 funções — `try_equip_free()` (só
pras Auras Curious Inquiry/Rune of Flight, que anexam ao resolver o
próprio cast sem custo de Equip separado, e pro ETB real de Twin
Blades/Embercleave) e `try_equip_paid()` (as outras 9 peças, cobrando o
`EQUIP_COST` real de cada uma, com o desconto dinâmico do Dragonfire
Blade — "{1} less for each color of the creature it targets" —
calculado contra o alvo já escolhido). `cast_permanent()` só chama o
attach de graça pras 2 exceções reais; as outras 9 ficam desanexadas até
`try_activated_abilities()` pagar o Equip de verdade (mesmo turno, se
sobrar mana, ou num turno futuro).

**Mais 6 gaps reais encontrados e corrigidos:**

1. **Two-Handed Axe // Sweeping Cleave** ("whenever equipped creature
   attacks, double its power") nunca disparava — as 2 comparações no
   combate usavam o nome curto `"Two-Handed Axe"`, mas o `CARD_DB` (e
   `p.card` em qualquer permanente real) usa o nome completo do MDFC
   `"Two-Handed Axe // Sweeping Cleave"` — nunca batiam, dobro de poder
   100% inerte desde a construção original.
2. **Enterprising Scallywag** ("you descended if a permanent card was
   put into your graveyard from ANYWHERE") só checava o descarte por
   limite de mão no fim do turno — ignorava toda sacrifício/morte real
   de carta (Lotus Petal, Izzet Locket, criaturas que morrem), a fonte
   muito mais frequente de "descended" num deck denso em Treasure/
   sacrifício. Corrigido centralizando a flag em `leave_battlefield()`
   (todo permanente REAL, não-token, que vai pro cemitério a partir do
   campo).
3. **Izzet Locket** (sacrifício por 2 cartas) e **Lotus Petal**
   (sacrifício por mana) usavam `battlefield.remove()` cru — nunca iam
   pro cemitério de verdade, nunca disparavam Gleaming Geardrake
   ("whenever you sacrifice an artifact") nem Tarrian's Soulcleaver
   ("...put into a graveyard from the battlefield"). Roteados por
   `leave_battlefield()` + novo helper `on_sacrifice_artifact()`.
4. **Trickster's Talisman** (sacrifício pra copiar a criatura equipada)
   tinha o mesmo problema — mesma correção.
5. **Oaken Siren** ("{T}: Add U, spend only on artifact spell/ability")
   nunca contribuía NENHUMA mana — é o único mana-dork de CRIATURA da
   lista (os outros 7 rocks são artefatos), então também é o único que
   precisa de checagem de doença de invocação, ausente até agora.
   Corrigido como mana genérica (mesma convenção de restrição-não-
   rastreada já usada nesta sessão, ex.: Tablet of Discovery no Azula) —
   não conta como fonte de cor (não seria gasta em não-artefatos na
   restrição real).
6. **Curious Inquiry / Rune of Flight** (Auras "Enchant creature")
   podiam ser conjuradas mesmo sem nenhuma criatura em campo — regra
   601.2c exige alvo legal pra sequer conjurar uma Aura; sem essa
   guarda, o loop guloso podia gastar mana numa Aura que entraria
   desanexada e iria pro cemitério na hora por SBA (704.5n), sem efeito
   algum. Guarda adicionada em `can_cast()`.

**Validação:** smoke test (75 nomes no `CARD_DB`, 98 cartas na
`BASE_LIBRARY`, 0 desconhecidas) + 2.000 partidas antes/depois (mesma
seed) + 20.000 partidas de regressão, 0 exceções em todas. Testes
unitários dirigidos confirmaram cada correção: Equipment comum
(Goldvein Pick) entra desanexado e só anexa depois de `spend_mana`
real; Twin Blades continua anexando de graça no cast; Two-Handed Axe
agora dobra o dano de combate de verdade; "descended" dispara num
sacrifício real (Lotus Petal) sem precisar do descarte por limite de
mão; Geardrake + Soulcleaver disparam ambos, sem duplicar, num único
sacrifício de Treasure.


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
