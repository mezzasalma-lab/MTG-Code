# Checklist cláusula-a-cláusula — Fire Lord Azula (Grixis, U/B/R)

Pedido direto do usuário (2026-09-01): *"Quais decks faltam para fecharmos?"*
→ *"Pode começar com o Kutzil"* (feito) → continuação natural pros outros 3
decks sem simulador desta pasta. Azula é o segundo (construção do zero,
não auditoria de arquivo existente). Mesma disciplina de "compile TUDO"
desta sessão.

**Fonte de dados:** oráculo real das 84 cartas não-básicas + comandante,
buscado ao vivo via Scryfall (`POST /cards/collection` em 2 lotes +
`/cards/named` pros 2 MDFCs e pra "Seething Song" isolada), não memória
nem só a `auditoria.md` anterior (boa, mas escrita antes desta leitura
linha-a-linha). A `auditoria.md` já tinha documentado a ambiguidade de
nome entre "Seething Song" (clássica, C21) e "Blazing Firesinger //
Seething Song" (MDFC "Prepare", SOS) — confirmado de novo aqui, IDs
diferentes, cartas físicas distintas.

**Arquitetura:** lista de nomes (`state.battlefield` como lista de
strings), igual à maioria dos simuladores desta sessão — não objetos
`Permanent` como Toph/Kutzil, porque este deck **não tem contadores
persistentes em criaturas** (nem +1/+1 counters, nem estado que sobrevive
de um turno pro outro). Como o combate aqui é goldfish (sem bloqueio),
"qual criatura específica recebeu qual bônus" nunca importa pro dano
total — só o poder agregado do ataque importa. Por isso os pumps de
alvo-único usam um dicionário leve `creature_power_mods` (nome →
{"add", "mult"}, resetado a cada turno), em vez de contadores reais.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real modelado neste goldfish solo,
  mesma convenção de toda a sessão.
- 🐛 **Achado e corrigido durante a própria construção** — gap que passou
  no primeiro rascunho e foi achado numa varredura automatizada, aplicada
  ANTES de considerar o deck pronto (mesmo método usado nos outros 14
  simuladores desta sessão, incluindo o Kutzil).

## 🐛 5 gaps achados e corrigidos durante a construção

Depois do primeiro rascunho completo (regressão de 5.000 partidas já
passando, 0 exceções), rodei a mesma varredura de "tag definida em
`add()` mas nunca lida em nenhum dispatch" — a maioria dos "órfãos"
detectados eram falsos positivos (despachados por checagem direta de
NOME em `state.battlefield`, não por tag, ex.: `magecraft_draw`,
`cost_reduce_ur`, `zada_copy_engine`). **5 eram gaps reais**, e um deles
(#1) era o mais grave possível — zerava o motor inteiro do comandante:

1. **🔴 O comandante nunca entrava em campo.** `BASE_LIBRARY` corretamente
   tem só as 99 cartas de deck (Azula fica na zona de comando, não
   embaralhada — mesmo padrão do Kutzil/Megatron), mas eu tinha
   **esquecido de escrever o passo que conjura a partir da zona de
   comando** — `try_cast_permanents()` só varre `state.hand`, e Azula
   nunca está lá. Resultado: em 500 partidas de teste, Azula entrava em
   campo em **0**. Sem Azula em campo, Firebending e o gatilho de cópia
   dela (o motor central do deck) nunca disparavam — `azula_copy_events_total`
   também era 0 em 2.000 partidas seguidas. Corrigido com
   `try_cast_commander()`, chamada explicitamente no início do turno E de
   novo depois dos rituais/rocks (pode destravar depois de mais mana).
   Depois do fix: Azula em campo até o turno 10 em **474/500** partidas
   (~95%), `azula_copy_events_total` média 1.7-1.8.
2. **Blazing Firesinger // Seething Song** — a ETB da frente ("this
   creature enters prepared") nunca setava `state.firesinger_prepared =
   True`. O motor pra *usar* a preparação (`try_cast_nontarget_value()`,
   pagar {2}{R} e conjurar uma cópia de Seething Song por RRRRR) já
   estava escrito desde o rascunho, mas era código morto — a flag nunca
   virava `True`. Corrigido na ETB.
3. **Archmage of Runes** — *"Whenever you cast an instant or sorcery
   spell, draw a card."* Só o Magecraft do Archmage Emeritus (cast OU
   copy) estava no `on_spell_event()`; o gatilho do Archmage of Runes (só
   CAST, diferente do Magecraft) nunca disparava. Corrigido — inclusive
   dobrado pela Veyran (é um triggered ability de um permanente causado
   por conjurar instant/sorcery, mesma lógica documentada no topo do
   arquivo).
4. **Stormcatch Mentor (Prowess)** — *"Whenever you cast a noncreature
   spell, this creature gets +1/+1 until end of turn."* Tag `prowess`
   existia, nunca lida em lugar nenhum. Corrigido com `trigger_prowess()`,
   chamado em todo caminho de conjuração de spell não-criatura (permanente
   e instant/sorcery) — só dobra via Veyran quando o spell é
   instant/sorcery (Prowess dispara pra QUALQUER não-criatura, mas o
   texto da Veyran é específico pra instant/sorcery).
5. **A carta "Flashback"** ({R}, *"target instant/sorcery card in your
   graveyard gains flashback until end of turn, flashback cost = mana
   cost"*) — 100% código morto, gastava mana sem fazer nada. Corrigido:
   concede + conjura de imediato o instant/sorcery de maior mv castável
   no cemitério (única janela real em que a flashback concedida existe).

**Bônus (não veio da varredura, achado por leitura direta ao implementar
#5):** o flashback IMPRESSO do próprio **Bulk Up** ({4}{R}{R}, distinto
do custo impresso {1}{R} e da carta "Flashback" acima) também estava sem
dispatch — corrigido com `try_bulk_up_flashback()`, chamado 1x por turno
no fim do main phase 2 se sobrar mana de verdade.

**Bug real achado DEPOIS de corrigir os gaps acima** (não veio da
varredura de tags, veio de um outlier estatístico numa regressão): a
regra 706.10 do X ("a copy of a spell has the same value of X as the
spell it's copying") não estava sendo respeitada — `resolve_single_target_effect()`
recalculava `remaining_mana(state)` de novo a cada cópia do Lunar Frenzy
via Zada, e como cada cópia também gera Treasures via Storm-Kiln Artist
(efeito colateral do próprio `on_spell_event`), o X ficava cada vez maior
a cada cópia dentro da MESMA conjuração — bola de neve. Corrigido:
`x_value` calculado 1x no cast original, propagado (mesmo valor) pra
todas as cópias da mesma conjuração — teste unitário dedicado
(`test_azula_gaps.py` caso #5... ver `test_azula_core.py` caso #5).

Validado com 2 baterias de testes unitários (7 + 6 = 13 testes isolados,
todos passando) + regressão repetida a cada rodada de correção (seeds
2.000.000+, 3.000.000+, 5.000.000+, turns=10, **0 exceções** em todas —
inclusive uma sweep final de 20.000 partidas, ~18.5s, 0 exceções).

## Motor central verificado

- **Storm real** (`spells_cast_this_turn`) — Grapeshot: dano = 1 +
  magias conjuradas ANTES dela no turno (contador incrementado só em
  CAST, não em COPY — testado).
- **Magecraft dobrado pela Veyran** — Archmage Emeritus (compra),
  Storm-Kiln Artist (Treasure), o próprio pump da Veyran, **e também os
  gatilhos do Zada e da Azula** (ambos são "triggered ability de um
  permanente que controlo, causada por conjurar/copiar instant ou
  sorcery" — a mesma cláusula da Veyran que reconhecidamente dobra o
  próprio Magecraft dela por ruling oficial). Não dobra Storm (habilidade
  da magia, não de um permanente) nem Prowess quando o spell não é
  instant/sorcery. Testado isoladamente (2 fontes de Magecraft + Zada +
  Archmage of Runes).
- **Zada, Hedron Grinder** — magia de alvo único mirando só Zada copia
  pra cada OUTRA criatura (each copy targets a different one) — testado
  com e sem Veyran (Veyran = 2 gatilhos independentes do Zada, cada um
  com seu próprio "different" — as 2 batches de cópias PODEM repetir alvo
  entre si, já que são resoluções separadas — mult=64 documentado como
  consequência real e correta de empilhar 3 magias "double power"
  através do motor Zada+Veyran, não um bug).
- **Fire Lord Azula (comandante)** — Firebending 2 (RR ao atacar) +
  cópia de magia conjurada durante o ataque, ambos testados; achado #1
  acima documenta o bug que zerava isso inteiro.

## Estrutural (📊, sem oponente real — não julgamento de valor)

- **Counterspell / Wash Away / An Offer You Can't Refuse** — precisam de
  spell de oponente pra contar.
- **Chaos Warp / Snap** — remoção/bounce sem alvo de oponente real.
- **Innocent Blood** — Regra 1 da sessão: *"each player sacrifices a
  creature"* é simétrico sem oponente modelado → só conta como
  `interaction_plays`, sem sacrifício real executado (mesmo atingindo a
  nós mesmos também na regra real).
- **Chandra's Ignition** — mesma Regra 1: *"target creature you control
  deals damage... to each OTHER creature and each opponent"* atingiria
  nossas próprias outras criaturas também (sem oponente pra também
  sofrer) — só conta o dano proxy representando "each opponent", sem
  destruir nossas próprias criaturas.
- **Kediss, Emberclaw Familiar** — *"whenever a commander you control
  deals combat damage to an opponent, it deals that much damage to each
  OTHER opponent"* — este arquivo usa dano proxy FLAT (sem contagem de
  N-oponentes, convenção da maioria dos simuladores desta sessão,
  diferente da premissa específica de mesa-de-4 do Megatron) — a
  cláusula de replicação não tem número pra manifestar no modelo flat; o
  corpo 1/1 dele soma poder de ataque normalmente.
- **Exotic Orchard** — leitura literal do oráculo ("mana de uma cor que
  um terreno de OPONENTE poderia produzir"): 0 terrenos de oponente
  modelados → produz 0 mana de verdade. Não é julgamento de valor, é a
  leitura correta da regra com 0 fontes qualificando.
- **Gingerbrute** — `{2},{T},Sacrifice: gain 3 life` não implementado —
  este arquivo não rastreia vida própria (nenhuma outra carta do deck
  depende de limiar de vida), sacrificar um atacante 1/1 haste por um
  recurso não modelado nunca teria valor real pra medir.
- **Baral, Chief of Compliance** — o draw-then-discard ao CONTRAR uma
  mágica precisa de spell de oponente sendo contrada — 📊, só a redução
  de custo dele é real (essa está implementada).

## Aproximações documentadas (reais, não inventadas)

- **Firebender Ascension** (quest counters via "ataque causa uma
  triggered ability disparar") — aproximado: cada permanente com
  Firebending que ataca conta 1 quest counter; ao acumular 4, "copia" um
  desses gatilhos ≈ +2 de dano proxy. Mesmo padrão de aproximação
  documentada do Ba Sing Se no Kutzil.
- **Fists of Flame** (+1/0 por carta comprada este turno) — aproximado
  como +1/0 fixo (o total real varia com quantas cartas já foram
  compradas no turno até aquele ponto, não rastreado por carta
  individual neste modelo agregado).
- **Reiterate / Narset's Reversal** — usados só como finalizador do
  Grapeshot (copiam o storm burn já resolvido uma vez cada, no fim do
  turno) — não generalizados como copiadores de qualquer spell nem com
  loop de buyback recursivo indefinido (decisão de escopo documentada).
- **Opal Palace** (bônus de contadores no comandante recastado da zona de
  comando, proporcional a quantas vezes já foi conjurado) — não
  implementado; exigiria o comandante morrer/voltar pra zona de comando,
  cenário raro sem remoção de oponente neste goldfish solo.

---

## Resumo numérico

- **84 cartas não-básicas + comandante**, 99 na biblioteca real de jogo
  (`lista.md`).
- **🐛 5 gaps achados e corrigidos na própria varredura de construção**
  (+ 1 bug real de regra 706.10 achado por análise de outlier estatístico,
  + 1 achado bônus do flashback do Bulk Up).
- **✅ ~65 cartas/cláusulas com efeito real implementado e testado.**
- **📊 ~8 cartas/cláusulas estruturais confirmadas** (opponent-dependent
  genuíno, mesma convenção de toda a sessão).
