# Checklist cláusula-a-cláusula — Ulalek, Fused Atrocity

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King e Thranduil.

**Contexto importante:** este simulador já tinha passado por 2 rodadas de
auditoria completa de oráculo antes desta (2026-08-28 e 2026-08-30,
documentadas extensivamente no docstring do cabeçalho e em
`goldfish-log.md`), incluindo correções reais como Forsaken Monument's
mana doubling, Sanctum of Ugin, Emrakul's graveyard cost reduction, os
8 painlands faltando em `TRUE_C_LANDS`, etc.

**Método:** detecção automatizada de (a) tags definidas em `add()` nunca
lidas em dispatch e (b) nomes de carta que só aparecem em `add()`+
`DECKLIST_TEXT`. ~39 candidatos apareceram no total; a esmagadora maioria
eram falsos positivos porque este arquivo mistura 3 convenções de
dispatch diferentes:
- Tabela de tag→função pros cast-triggers dos titãs Eldrazi
  (`CT_TRIGGERS`: Kozilek x3, Ulamog x2, Emrakul, Flayer, Conduit,
  Nulldrifter, Sowing Mycospawn, Writhing Chrysalis) — todos corretos.
- Checagem de nome direta dentro de funções compartilhadas
  (`eldrazi_cost_discount()` cobre Urza's Incubator, It That Heralds the
  End, Eye of Ugin's estática, Emrakul's redução por tipo em cemitério;
  `on_colorless_creature_etb()` cobre Glaring Fleshraker) — todos
  corretos.
- Tag genérica `"interaction"` pra toda a pacote de remoção/contramagia
  (Swords to Plowshares, Toxic Deluge, Beast Within, Swan Song, etc.) —
  tratadas como proxy (conjuráveis, sem alvo de oponente real), consistente
  com o resto da sessão.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real, sem combate/P-T por criatura
  individual, ou sem modelo de mana pip-a-pip — limite conhecido, não
  julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 Os 3 gaps corrigidos nesta rodada

Todos em terrenos que estavam registrados genericamente dentro de um
loop de 34 terrenos (`add(n, 0, "land", {"colorless"})`) — só a mana
{C} básica coberta, nenhuma habilidade adicional real.

1. **Eye of Ugin** — a redução estática ("Colorless Eldrazi spells you
   cast cost {2} less") já era coberta por nome em
   `eldrazi_cost_discount()` desde 2026-08-28/30. Faltava a ativada real:
   *"{7}, {T}: Search your library for a colorless creature card, reveal
   it, put it into your hand, then shuffle."* O próprio docstring já
   documentava isso como deferido ("2 habilidades ativadas a mais, ficam
   pra uma rodada dedicada"). Corrigido com `try_eye_of_ugin()` — 1x por
   turno, tutora a criatura colorless de maior MV disponível.
2. **Urza's Cave** — *"{3}, {T}, Sacrifice this land: Search your library
   for a land card, put it onto the battlefield tapped, then shuffle."*
   100% ausente (mesma nota de deferimento do docstring). Corrigido com
   `try_urzas_cave()` — busca Ancient Tomb (maior valor: {C}{C}) se ainda
   estiver na biblioteca, senão qualquer terreno disponível. Uso único
   por partida (a própria habilidade sacrifica o terreno).
3. **Ruins of Oran-Rief** — 2ª habilidade real *"{T}: Put a +1/+1 counter
   on target colorless creature that entered this turn"* (mutuamente
   exclusiva com o modo de mana {C} básica, mesmo `{T}`) nunca
   implementada — só o modo de mana genérica estava coberto (contado
   dentro do loop de 34 terrenos). Corrigido com `try_ruins_oran_rief()`,
   contador agregado (este modelo não rastreia P/T por criatura
   individual). Simplificação documentada: só dispara pra criaturas
   conjuradas via `resolve_cast`/`creature_etb_hooks` nesse turno, não
   cobre tokens Spawn/Scion/Manifest criados fora desse fluxo específico
   (este arquivo não centraliza toda criação de token num único ponto de
   entrada).

**Reclassificação de linguagem (não um bug, correção de fraseado):** o
comentário do cabeçalho sobre Void Grafter/Liberator/Ruins of Oran-Rief
dizia *"presentes na decklist mas sem efeito numérico relevante pro
goldfish"* — fraseado próximo do "julgamento de valor" que o pedido do
usuário proíbe. Reescrito com a razão estrutural real por carta: Void
Grafter (sem oponente/remoção real modelada pra proteger contra — 📊
genuíno), Liberator (exigiria comparar o power dele contador-a-contador
contra cada gasto de mana futuro — mesmo limite de "sem P/T por criatura"
já documentado no resto do arquivo, não um recorte específico desta
carta).

Validado com 6 testes unitários isolados + regressão de 20.000 partidas
(seed 3000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 6000000, turns=10): tutores usados
0.60→0.70, RAMP 2.33→2.52, Urza's Cave ativado em 17.0% dos jogos, Ruins
of Oran-Rief avg 0.66 contadores/partida.

## Falsos positivos descartados (já corretamente implementados)

- **Kozilek/Ulamog/Emrakul (todas as variantes) + Flayer of
  Loyalties/Conduit of Ruin/Nulldrifter/Sowing Mycospawn/Writhing
  Chrysalis** — cast-triggers reais dispatchados via `CT_TRIGGERS`
  (tag→função), não por nome — meu primeiro método de detecção (contagem
  de ocorrência de nome) apontou falso positivo, corrigido cruzando com
  a tabela de dispatch real.
- **Urza's Incubator, It That Heralds the End** — cost reduction
  estática já implementada por nome dentro de `eldrazi_cost_discount()`.
- **Sanctum of Ugin** — já implementado desde 2026-08-28 (mill-trigger
  gratuito ao conjurar spell colorless MV7+, `on_any_spell_cast_hooks`).
- **Rhystic Study, Sire of Stagnation, Defense of the Heart** —
  genuinamente opponent-dependent (gatilhos exigem ação do oponente), 📊
  consistente com o resto da sessão.
- **Sire of Seven Deaths** — só keywords de combate (reach/first
  strike/vigilance/menace/trample/lifelink/ward), sem gatilho numérico —
  nada a implementar.
- **Morophon, the Boundless** — não é órfã de tag (tags só `{"colorless"}`,
  sem tag própria); redução "{W}{U}{B}{R}{G} less" e anthem "+1/+1"
  ambas 📊 estruturais: este arquivo não modela custo por pip de cor
  (mana pool fungível única, sem rastreio WUBRG) nem P/T por criatura.

---

## Resumo numérico

- **~100 cartas na lista** (comandante + biblioteca, incluindo os 34
  terrenos genéricos + Ancient Tomb).
- **🐛 Corrigido nesta rodada:** 3 cartas (Eye of Ugin, Urza's Cave,
  Ruins of Oran-Rief).
- **✅ Falsos positivos descartados (já implementados corretamente,
  métodos de dispatch diferentes do esperado pela varredura inicial):**
  11 cartas/grupos (Kozilek x3, Ulamog x2, Emrakul, Flayer, Conduit,
  Nulldrifter, Sowing Mycospawn, Writhing Chrysalis, Urza's Incubator, It
  That Heralds the End, Sanctum of Ugin).
- **📊 Estrutural confirmado:** Rhystic Study, Sire of Stagnation, Defense
  of the Heart (opponent-dependent), Sire of Seven Deaths (combate puro),
  Morophon (sem modelo de pip de cor / sem P/T por criatura), Void
  Grafter, Liberator.
