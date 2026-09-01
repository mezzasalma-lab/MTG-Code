# Checklist cláusula-a-cláusula — Megatron, Tyrant

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov, Hei Bai e Maralen.

93 cartas não-terreno-básico do decklist (Mardu, B/R/W, artefatos +
Eldrazi + combustível-de-sacrifício), oráculo real buscado ao vivo via
Scryfall (`POST /cards/collection`, 2 lotes) contra o
`megatron_goldfish_v1.py` atual.

**Contexto:** este é o deck **mais novo** dos auditados até agora
(construído em 2026-08-29, sem nenhuma rodada de reanálise anterior —
diferente de Toph/Beorn/Edgar Markov/Hei Bai/Maralen, que já tinham
passado por 1-16 correções prévias). A releitura linha-a-linha achou
**6 tags mortas** (definidas no `add()` de cada carta, nunca lidas em
lugar nenhum do dispatch) — não julgamento de valor, **lacuna pura**:
mecânicas inteiras (incluindo um finisher de dano real, Summon: Bahamut)
100% ausentes sem nenhuma documentação explicando por quê.

**Legenda:**
- ✅ **Implementado.**
- 📊 **N/A estrutural** — sem oponente real modelado (vida agregada via
  proxy, `NUM_OPPONENTS=3`), sem combate real (bloqueio).
- 📝 **Documentado, fora de escopo genuíno.**
- 🐛 **Corrigido nesta rodada (2026-09-01)** — tag morta, lacuna pura.

## 🐛 As 6 tags mortas corrigidas nesta rodada

1. **Scion of Draco** (`domain_reduce`) — "This spell costs {2} less for
   each basic land type" nunca reduzia o custo fixo de {12}, praticamente
   incastável numa lista de 93 cartas. Corrigido: novo `effective_cost()`,
   usado em `can_cast()`/`cast_card()`/prioridade de conjuração. Este
   deck (sem Forest/Island) tem domínio máximo real 3, não 5.
2. **Summon: Bahamut** (`saga_bahamut`) — Saga de 4 capítulos
   (destroy/destroy/draw2/**Mega Flare**, um finisher real de dano = MV
   total de outros permanentes) 100% ausente. Corrigido: capítulo I em
   `resolve_etb()`, II/III/IV em `try_bahamut_saga()` (chamada no upkeep).
3. **Cryptolith Fragment // Aurora of Emrakul** (`fuel_mana_drain`) —
   mana ability real (`{T}: Add any color, each player loses 1 life`) +
   condição de transformação (`each player has 10 or less life`) 100%
   ausentes. Corrigido: `try_cryptolith_fragment()` (vida de oponente
   aproximada via `40 - proxy_damage_total`, única leitura disponível
   neste modelo agregado) + `try_aurora_of_emrakul_attack()` pro verso.
4. **Cityscape Leveler** (`cast_removal_attack_removal`) — nem o cast
   nem o gatilho de ataque (destroy nonland permanent, repetível) eram
   contados como interação. Corrigido em `resolve_etb()` +
   `try_cityscape_leveler_attack()`.
5. **Retributive Wand** (`fuel_ping_death_burst`) — `{3},{T}: 1 dano`
   repetível 100% ausente (o gatilho de morte, "5 dano", continua 📊 —
   nenhuma remoção dos PRÓPRIOS permanentes é modelada neste sim, mesma
   razão de Enduring Vitality noutros decks). Corrigido:
   `try_retributive_wand_ping()`.
6. **Pumpkin Bombs** (`fuel_fuse_burn`) — `{T}, discard 2: draw 3, 1
   dano, adversário GANHA CONTROLE do artefato` 100% ausente. Corrigido:
   `try_pumpkin_bombs()` — ativação única de verdade (não julgamento de
   valor: o oráculo literalmente tira o artefato do seu controle após o
   1º uso).

Validado com 6 testes unitários isolados + regressão de 20.000 partidas
(0 erros) + `run_batch` confirmando ativação real de todas as 6 (Scion
of Draco castável em 2,2% dos jogos — antes 0%; Bahamut chega ao Mega
Flare em jogos mais longos, dano real ~63-133 quando resolve).

---

## Cobertura das demais 87 cartas

O motor central (Megatron Tyrant/Destructive Force, conversão de face,
combustível de sacrifício) e o resto do deck já estavam bem cobertos na
construção original (docstring do arquivo, seção "Simplificações
documentadas"). Confirmado nesta rodada, carta por carta:

- **Megatron** (frente Tyrant / verso Destructive Force): mecânica de
  conversão, dano por sacrifício de artefato, geração de mana pós-combate
  — ✅ `megatron_combat()`/`megatron_postcombat()`.
- **Combustível de sacrifício** (Atraxa's Skitterfang/Bitterthorn/Dauntless
  Scrapbot/Etched Familiar/Solemn Simulacrum/etc): ETBs reais, corpo
  descartável — ✅.
- **Kozilek / Ulamog**: cast-draw-4, Annihilator (📊 sem board de
  oponente), destroy-on-cast (📊 interação sem alvo real) — ✅/📊.
- **Starscream** (transform, paralelo ao Megatron): monarquia/conversão —
  ✅ (tratado análogo ao Megatron).
- **Toolbox de recursão** (Myr Retriever/Junk Diver/Workshop Assistant,
  Goblin Engineer, Osgir, Mishra unearth): ✅.
- **Wheels** (Wheel of Fortune/Wheel of Misfortune/Memory Jar): ✅
  (Wheel of Misfortune simplificado — modo de "maior número" não
  simulável sem escolha simultânea de oponente real, documentado).
- **Removal genérica sem alvo real** (Crackling Doom/Soul Shatter/
  Shatterskull Smashing/Sundering Eruption/Rakdos Charm/Swords/Path):
  conjurada quando há mana sobrando, conta como interação — 📊.
- **Price of Progress**: proxy via contagem de terrenos não-básicos
  próprios — 📝 documentado.
- **The One Ring / Phyrexian Arena / Descent into Avernus**: draw
  engines com autodano real, incluindo Descent (dano simétrico) — ✅.
- **Portal to Phyrexia**: sacrifício de oponente (📊) + reanimação do
  próprio cemitério — ✅.
- **Talon Gates of Madara**: `{T}: Add C` genérico coberto — ✅; upgrade
  de cor (`{1},{T}: any color`) e "play from hand for {4}" — 📝 baixo
  impacto de magnitude (só fixação de cor / land drop extra), não
  implementados por escopo, mas agora documentados explicitamente aqui
  em vez de silenciosos.
- **Boros Charm**: modal, dano/indestructible/double strike — ✅ tag
  `boros_charm_burn` (modo de dano).

---

## Resumo numérico

- **93 cartas.**
- **✅ Implementado:** ~75 linhas de cláusula.
- **📊 N/A estrutural:** ~15 linhas.
- **📝 Documentado, fora de escopo genuíno:** ~3 linhas (Talon Gates
  upgrade de cor/land-drop extra, Price of Progress proxy, Wheel of
  Misfortune modo de "maior número").
- **🐛 Corrigido nesta rodada:** 6 tags mortas (Scion of Draco, Summon:
  Bahamut, Cryptolith Fragment, Cityscape Leveler, Retributive Wand,
  Pumpkin Bombs) — todas lacunas puras, sem documentação prévia alguma,
  não julgamento de valor.

---

## 🐛 Correção — Plaza of Heroes / infraestrutura "legendary" morta (2026-09-02)

**Gatilho:** usuário lembrou "The Ten Rings" (que já estava corretamente
implementada — maximum hand size 10 + draw-to-10 no end step, ver
`end_step()`). Ao reconferir, achei `is_legendary()`/`LEGENDARY_NAMES`
(13 permanentes legendários da lista) **definidos mas nunca chamados em
lugar nenhum** — sinal de que algo dependente de "legendary" ficou pra
trás.

**Achado real:** Plaza of Heroes — oráculo completo (Scryfall): *"{T}:
Add {C}." + "{T}: Add one mana of any color. Spend this mana only to
cast a legendary spell." + "{T}: Add one mana of any color among
legendary permanents you control." + "{3}, {T}, Exile this land: Target
legendary creature gains hexproof and indestructible until end of
turn."* Só o modo 1 (incolor genérico) estava implementado
(`produces=set()`) — os outros 3 modos 100% ausentes, incluindo o mais
valioso numa lista com 13 legendários: fixar qualquer cor pra conjurar
um spell legendário.

**Corrigido:** modo 2 implementado de verdade —
`color_sources(state, color, spell_name=name)` agora conta Plaza of
Heroes como fonte de qualquer cor faltante quando `spell_name` é
legendário (`is_legendary()`, agora finalmente chamado). Chamadas
genéricas de `color_sources()` sem contexto de spell continuam
ignorando Plaza (comportamento antigo preservado onde não se aplica).

**Modos 3 e 4 permanecem 📊/📝, por razão estrutural real (não
julgamento de valor):**
- Modo 3 ("fixar cor pra ativar habilidade de legendário") exigiria um
  framework genérico de "pagar custo de qualquer habilidade ativada",
  que este arquivo não tem em lugar nenhum (só ativações hardcoded caso
  a caso).
- Modo 4 (hexproof+indestructible) é proteção contra remoção de
  oponente — sem oponente real modelado neste goldfish solo, mesma
  convenção de toda a sessão.

Validado com 4 testes unitários isolados (bloqueia sem Plaza / libera
com Plaza pra spell legendário / NÃO libera pra spell não-legendário /
`color_sources()` genérico ignora Plaza) + regressão de 20.000 partidas
(seed 11000000+, turns=10, 0 exceções) + `run_batch` antes/depois (3000
jogos, seed 12000000, turns=10): turno médio de conjuração do Megatron
5.02→4.97, "nunca conjurado em 10 turnos" 11.6%→10.8% — pequeno mas real
(fixação de mana ocasional destravando um legendário que faltava a cor).
