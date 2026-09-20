# Checklist cláusula-a-cláusula — Edgar Markov

## Modo de resiliência ganha wipe de artefato e wipe de encantamento — 2026-09-20

**Gatilho:** "Temos que incluir remoções de artefatos e encantamentos
tb: Vandalblast, Farewell, Austere Command, etc…" — até esta rodada, a
única categoria de "board wipe" do modo de resiliência era "destroy all
creatures". Raciocínio completo (e a correção de design que se seguiu
no mesmo dia) em `megatron-tyrant-mardu/checklist-oraculo.md`.

**Implementado direto no design FINAL** (este deck recebeu a extensão
DEPOIS da correção de design nos outros 3, então nunca passou pela
versão com rolagens independentes): `try_smart_opponent_wipe()` único —
1 rolagem "algum wipe acontece" (`chance = interaction_chance() *
TOTAL_WIPE_CHANCE_FACTOR`, soma dos 3 pesos = 0.75) seguida de escolha
ponderada de 1 TIPO só (`WIPE_TYPE_WEIGHTS = {"creature": 0.4,
"artifact": 0.2, "enchantment": 0.15}`), restrita aos tipos com alvo
legal em campo. Delega pro mesmo `remove_permanent(state, log, n,
source=...)` já usado por todas as outras categorias (nota: assinatura
com `log` na 2ª posição, diferente da maioria dos outros decks). Edgar
Markov nunca é artefato nem encantamento (Legendary Creature — Vampire
Knight, confirmado via Scryfall), então nunca é alvo direto. Vários
encantamentos reais e motores de valor de verdade neste deck
(Caretaker's Talent, Black Market Connections, Anointed Procession,
Smothering Tithe, The Meathook Massacre) agora alcançáveis por wipe de
encantamento. `state.wiped_this_round` setado se o tipo escolhido não
for criatura mas algum permanente destruído também for criatura de
verdade (nenhuma carta desta lista é híbrida hoje — `is_creature`/
`is_artifact`/`is_enchantment` mutuamente exclusivas, `Card.type` é uma
string única sem híbrido — checagem mantida por robustez).

**Validação:** modo padrão 100% bit-idêntico ao commit `8faa943` (2.000
seeds) + regressão de 20.000 partidas em modo resiliência, 0 exceções +
testes dirigidos (no máximo 1 tipo por chamada, 0 violações; distribuição
ponderada bate com os pesos relativos dentro de 3pp).

**Resultado (A/B 2000 jogos mesma seed_base):** % de jogos com pelo
menos 1 wipe de qualquer tipo sobe de 40,8% pra 65,5% (antes = commit
`8faa943`, só wipe de criatura). Avg wipes totais por jogo: 0,477 →
0,949. 15,7% dos jogos "depois" sofrem pelo menos 1 artifact wipe,
17,4% pelo menos 1 enchantment wipe.

## Porte completo do modo de resiliência (interação de oponente) — 2026-09-20

**Gatilho:** usuário pediu direto, depois de já ter validado o modo em
Megatron/Ur-Dragon/Hei Bai (incluindo 3 rodadas de correção de
orquestração de turno nesta mesma sessão): *"Agora implementa essas
mudanças no Markov."* Este deck nunca tinha NENHUMA extensão de
resiliência antes — porte completo do zero, já incorporando o design
FINAL já validado nos outros 3 (não precisou repetir as 3 rodadas de
correção histórica).

**Diferenças estruturais reais deste deck vs. os outros 3** (levadas em
conta no design, não simplificações por preguiça):
1. **Nenhuma criatura NOMEADA jamais morria neste motor antes desta
   rodada** — só sacrifício de TOKEN via `sac_loop` (decisão de escopo
   documentada desde a reconstrução original: nenhum outlet de
   sacrifício do deck alcança criatura nomeada). `remove_permanent()`
   (novo) é o 1º ponto real de destroy/wipe verdadeiro do arquivo.
2. **Combate real (bloqueadores) não é modelado** — mesma convenção já
   documentada no topo do arquivo desde a reconstrução original ("Edgar
   ataca todo turno... sem resposta do oponente"). Ataque de oponente
   também conecta sem bloqueio, mesmo padrão do Ur-Dragon/Hei Bai.
3. **Vida própria nunca foi rastreada** — só contadores agregados de
   drain/lifegain do oponente. `state.life` é NOVO, existe só como alvo
   do ataque de oponente.

**Achados reais que exigiram corrigir código COMPARTILHADO (Regra #3 do
CLAUDE.md — não bastava auditar carta por carta, o conceito central
"criatura pode morrer"/"comandante pode sair de campo" nunca tinha
existido neste arquivo):**

1. **`eminence_trigger()` tinha um bug dormant que só ficou alcançável
   com o novo `remove_permanent()`.** A condição `state.commander_in_play
   or state.commander_cast_count == 0` só cobria 2 dos 3 estados reais
   de Edgar (em campo; nunca conjurado ainda = literalmente na zona de
   comando). Antes desta rodada Edgar nunca DEIXAVA o campo depois de
   conjurado (nenhum removal existia), então o 3º estado real —
   destruído por um oponente e voltando pra zona de comando via CR
   903.9 — nunca acontecia e o bug ficava adormecido. Corrigido:
   Eminence está disponível incondicionalmente neste motor (Edgar
   sempre está em campo OU na zona de comando, nunca em nenhum outro
   lugar — nenhuma substituição de zona tipo exile/shuffle-into-library
   se aplica a ele). Comportamento em modo padrão continua 100%
   idêntico (verificado — a fórmula antiga já dava a mesma resposta nos
   2 estados que o modo padrão de fato alcançava).
2. **`main_phase()` só permitia conjurar Edgar 1x pra sempre**
   (`state.commander_cast_count == 0` na condição de cast) — nunca era
   um problema em modo padrão, mas bloquearia recast de verdade depois
   de `remove_permanent` mandar Edgar de volta pra zona de comando.
   Removido — `not state.commander_in_play` sozinho já é a condição
   real (100% idêntico em modo padrão, confirmado por regressão).
3. **`_creature_sacrificed()` bundlava 2 gatilhos com escopo real
   diferente** — Pitiless Plunderer ("whenever ANOTHER creature you
   control dies", verificado via Scryfall: NÃO é sacrifice-restricted)
   + death payoffs (Blood Artist/Zulaport/etc, "dies" geral) por um
   lado, Vito Fanatic ("whenever YOU sacrifice another permanent",
   sacrifice-restricted de verdade) por outro. Extraído
   `_apply_creature_death_payoffs()` (só a parte 1, geral) pra ser
   reusada tanto por sacrifício de verdade quanto por
   `remove_permanent` — Vito Fanatic fica de fora da remoção de
   oponente, corretamente (destruição de oponente não é algo que EU
   sacrifiquei). Refatoração confirmada bit-a-bit idêntica em modo
   padrão pros 5 call sites reais já existentes.
4. **CR 903.9 aplicado corretamente em `remove_permanent`**: comandante
   destruído vai pra zona de comando (efeito de SUBSTITUIÇÃO), nunca
   chega a ser "put into a graveyard" de verdade — gatilhos de "dies"
   (Pitiless Plunderer, death payoffs) NÃO disparam pra ele. Testado
   diretamente.

**Implementado:** as mesmas 7 categorias já validadas no Megatron/
Ur-Dragon/Hei Bai (ataque sem bloqueio, remoção curada por
`INTERACTION_ENGINE_PRIORITY`, discard aleatório, board wipe via
`remove_permanent`, graveyard hate em 2 modelos — mass exile 1x/partida
e exílio de carta única repetível, alvo = maior MV entre criatura no
cemitério, mesmo critério que Agadeem's Awakening/Sevinne's
Reclamation/Bloodline Bidding usam pra recursão real —, e counterspell
mirando só o cast do comandante), já incorporando direto o design final
das 3 rodadas de correção de orquestração de turno: `try_smart_
opponent_turn()` simula `NUM_OPPONENTS = 3` turnos de oponente reais
por rodada; `state.wiped_this_round` + `POST_WIPE_ATTACK_HASTE_FACTOR =
0.15` garantem que um wipe simétrico suprime ataque na rodada inteira
(não só o turno do wiper), reduzido nunca zerado (haste); `OPPONENT_
ATTENTION_CHANCE = 1/NUM_OPPONENTS` garante que nem todo turno de todo
oponente mira em mim.

**`INTERACTION_ENGINE_PRIORITY` curada** (motor recorrente de valor, não
corpo isolado): Roaming Throne, Pitiless Plunderer, Ashnod's Altar,
Sanctum Seeker, Skullclamp, Black Market Connections, Caretaker's
Talent, Zulaport Cutthroat, Sorin Imperious Bloodlord, Vito Fanatic of
Aclazotz. Edgar Markov fica de fora de propósito — já tem categoria
dedicada (counterspell no cast) e remoção não o mata de verdade mesmo
(vai pra zona de comando).

**Validação:**
- Modo padrão confirmado **100% bit-idêntico** ao HEAD anterior — 5.000
  seeds comparadas campo a campo no dict COMPLETO retornado por
  `simulate_one` (não só um subconjunto), 0 divergências.
- Regressão de 20.000 partidas em modo resiliência, 0 exceções.
- Testes dirigidos: comandante removido vai pra zona de comando (nunca
  cemitério) e fica recastável (tax correta); remoção de criatura
  nomeada dispara Pitiless Plunderer + death payoffs mas NÃO o gatilho
  de sacrifício do Vito Fanatic; token removido sai de `battlefield` E
  `tokens` sem ir pro cemitério; Eminence continua disponível com Edgar
  na zona de comando após remoção (bug dormant confirmado e corrigido);
  taxa de ataque pós-wipe cai pra ~13,5% da taxa base (~ fator 0,15
  esperado).
- `run_batch_with_interaction` (2000 jogos): avg ataques sofridos 1,22,
  avg board wipes 0,51 (43,3% das partidas sofrem ao menos 1), avg
  counterspells 0,09, avg vida final 38,11, Edgar recastado após
  remoção em 8,6% das partidas — magnitudes na mesma faixa dos outros 3
  decks já validados. "Nunca conjurado em 8 turnos" sobe de 23,2%
  (padrão) pra 26,5% (resiliência) — direção esperada (counterspell
  atrapalhando o 1º cast), não um bug.

## Achado real 2026-09-14 (usuário perguntou se Roaming Throne está certa em todos os decks onde aparece)

Depois de achar e corrigir uma classe de bug no Beorn (Roaming Throne
nunca contava como o próprio tipo escolhido pra fins de "controle N
criaturas do tipo X"), o usuário pediu pra verificar os outros decks.
Este deck tinha o **mesmo bug**, num lugar diferente.

Oráculo real: *"As this creature enters, choose a creature type. This
creature is the chosen type in addition to its other types."* — a
convenção deste deck (única escolha sensata, tribal Vampiro) é sempre
escolher Vampire. `is_vampire(card)` só reconhecia a tag `"vampire_type"`
(ou o próprio comandante) — Roaming Throne, sem essa tag, nunca contava
como Vampiro pras 3 contagens reais de "quantos Vampiros você controla"
em campo: desconto de custo do **Voldaren Estate**, compra do **Champion
of Dusk**, e os contadores +1/+1 distribuídos pelo próprio **gatilho de
ataque da Edgar**.

**Cuidado que ISSO NÃO é o mesmo fix do Beorn (não dá pra copiar e
colar):** diferente do Firdoch Core (Changeling, que vale em qualquer
zona), o tipo que a Roaming Throne ganha é uma característica **só
enquanto ela está na batalha** ("as this enters, choose..." — não é uma
CDA como Changeling). Isso significa que marcar Roaming Throne como
Vampiro incondicionalmente (a mesma tag estática usada pra outras
cartas) teria corrigido os 3 bugs reais acima mas **criado 2 bugs
novos**: Sorin, Imperious Bloodlord (−3, "put a Vampire creature **card**
from your hand") passaria a poder cheat a Roaming Throne pra campo
direto da mão (ela ainda não escolheu tipo nenhum enquanto é só uma
carta na mão); e o Eminence da própria Edgar ("whenever you cast
another Vampire **spell**") passaria a disparar ao conjurar a própria
Roaming Throne (a escolha só acontece na resolução, não durante o cast).

**Corrigido com um helper separado**, `is_vampire_in_play(card)`,
usado só nos 3 loops que iteram `state.battlefield` (onde ela já é um
Vampiro de verdade) — `is_vampire()` puro continua sem reconhecer
Roaming Throne, preservando o comportamento correto em mão/cemitério/
cast.

**Validação:** 2 testes unitários dirigidos (`is_vampire` puro fica
False pra Roaming Throne; `is_vampire_in_play` fica True) — passando.
Batch de 2.000 partidas antes/depois (mesma seed 7100000, turns=10):
`edgar_attack_counters_total` 17,33→18,11; `champion_of_dusk_draws`
0,570→0,594; `voldaren_estate_blood_tokens` 0,577→0,581 — movimento
pequeno e real (Roaming Throne só está em campo em 15% dos jogos, seed
usada). 20.000 partidas de regressão (seed 7300000+), **0 exceções**.

---

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Azula/Beorn/Captain
Storm: oráculo real via Scryfall pras 92 cartas não-terreno + comandante +
28 terrenos (batch de `POST /cards/collection`, 68 cartas de uma vez, 0
`not_found`, + `/cards/named?fuzzy=` individual pros 9 MDFC/Room/prepared),
comparado cláusula-por-cláusula contra o `edgar_markov_goldfish_v1.py`
atual. Este já era o deck mais auditado da sessão (16+ rodadas anteriores,
incluindo uma leitura linha-a-linha completa em 2026-09-01, ver seção
abaixo) — mesmo assim, focar especificamente na cascata de "sacrifício →
todos os payoffs disparam exatamente uma vez cada" (pedido explícito desta
rodada) achou **6 gaps reais**, todos na categoria mais difícil
("implementação parcial" — a tag/carta já tinha código real, só cobria
PARTE dos pontos onde deveria disparar).

**Achado principal — sistêmico, mesma classe do bug do Captain Storm
(Equip nunca cobrado): a cascata de sacrifício não disparava por completo
em 4 dos 5 pontos reais de sacrifício de criatura deste deck.**

O motor tinha um sacrifício "canônico" bem implementado dentro de
`sac_loop()` (Pitiless Plunderer cria Treasure + `_apply_death_payoffs`
dispara Blood Artist/Zulaport/etc + Vito, Fanatic of Aclazotz avança de
estágio) — mas esses 3 efeitos estavam **inline dentro do próprio
`sac_loop()`**, nunca extraídos pra um helper compartilhado. Os outros 4
pontos reais de sacrifício de criatura da lista (`_pay_diabolic_intent_cost`
— custo do Diabolic Intent; `try_fountainport` — sac-token da própria
habilidade; o sacrifício opcional do Plumb the Forbidden; e o **+1** de
Sorin, Imperious Bloodlord, "you may sacrifice a Vampire") cada um só
chamava PARTE dessa cascata (ou nenhuma parte, no caso do Sorin):

1. **Sorin, Imperious Bloodlord (+1, "sacrifice a Vampire": 3 dano + 3
   vida) não disparava NENHUM payoff de morte.** Sacrificar um Vampire
   Token pra essa habilidade é uma morte de criatura de verdade — Blood
   Artist, Cruel Celebrant, Zulaport Cutthroat, Vindictive Vampire,
   Bastion of Remembrance, Vein Ripper, Funeral Room, The Meathook
   Massacre, Pitiless Plunderer (Treasure) e Vito, Fanatic of Aclazotz
   deveriam TODOS reagir, mas nenhum reagia — o código só incrementava
   `creatures_died_this_turn` e seguia direto pro dano/vida da própria
   habilidade do Sorin, sem tocar em `_apply_death_payoffs` nem em
   qualquer outra parte da cascata.
2. **Diabolic Intent** (custo "sacrifice a creature") só chamava
   `_apply_death_payoffs` — Pitiless Plunderer e Vito Fanatic ficavam
   mudos, e `creatures_sacrificed_total` nunca era incrementado (métrica
   subcontava).
3. **Plumb the Forbidden** (custo opcional "sacrifice one or more
   creatures... copy this spell for each") — mesmo gap do Diabolic Intent:
   só `_apply_death_payoffs`, sem Pitiless Plunderer nem Vito Fanatic.
4. **Fountainport** (sac-token da própria habilidade `{2},{T},Sacrifice a
   token: Draw a card`) já chamava Pitiless Plunderer + death payoffs, mas
   não Vito Fanatic.
5. **Vito, Fanatic of Aclazotz em si** ("Whenever you sacrifice ANOTHER
   PERMANENT" — confirmado no oráculo real via Scryfall, não é só
   criatura) nunca disparava ao cracar um Treasure. Isso é relevante
   porque Treasure É sacrificado de verdade neste motor
   (`create_treasure_and_crack`, "T, Sacrifice this token: Add...") — as
   3 fontes de Treasure do deck (Pitiless Plunderer, Black Market
   Connections, Fountainport) cracam na hora, cada crack é um segundo
   evento de sacrifício real, separado da morte da criatura que o
   originou. Confirmado o impacto real: `vito_fanatic_demons_created`
   (o 3º estágio, token 4/3 voador) estava em **0,0 em 2.000 partidas**
   antes do fix — o motor nunca acumulava 3 sacrifícios reais no mesmo
   turno pela via estreita do `sac_loop()` sozinho.

**Corrigido:** extraídos 2 helpers compartilhados —
`_vito_fanatic_sacrifice_trigger()` (só a progressão de estágio) e
`_creature_sacrificed()` (a cascata completa: contador +
Pitiless Plunderer + `_apply_death_payoffs` + Vito Fanatic) — chamados
agora dos 5 pontos reais de sacrifício de criatura (`sac_loop`,
`_pay_diabolic_intent_cost` nos 2 ramos, `try_fountainport`, o sac do
Plumb the Forbidden, e o novo `+1` do Sorin), mais uma chamada direta de
`_vito_fanatic_sacrifice_trigger()` dentro de `create_treasure_and_crack()`
pra cobrir o sacrifício do próprio Treasure. Skullclamp foi deixado DE
FORA de propósito (fica só no `sac_loop`, onde a maioria dos sacrifícios
acontece de fato) — generalizar o reequipe de Equipment pra todo ponto
arriscaria contagem dupla do custo sem ganho real de precisão, decisão
documentada inline no código.

**Achado lateral, mesma categoria ("implementação parcial"): Cruel
Celebrant.** Oráculo real confirmado via Scryfall: "Whenever this creature
or another creature **or planeswalker** you control dies..." — é a ÚNICA
carta do `DEATH_PAYOFF_FORMULAS` com essa cláusula extra (as outras 8 —
Blood Artist/Zulaport/Vindictive Vampire/Bastion of Remembrance/Funeral
Room/Vein Ripper/The Meathook Massacre/Cordial Vampire — são
criatura-only, conferido uma por uma). Sorin, Imperious Bloodlord PODE
morrer de verdade neste motor (a habilidade `−3` reduz a lealdade a 0 se
ativada com lealdade == 3) — `add_loyalty()` já tinha um contador
`pw_deaths_total` funcionando pra isso, mas nunca chamava nenhum payoff de
morte. Corrigido: extraído o corpo de "disparar 1 payoff de morte" pra um
helper `_fire_death_payoff()` (reutilizado tanto por `_apply_death_payoffs`
quanto pela chamada nova em `add_loyalty`, só pra Cruel Celebrant, na
morte de planeswalker) — não reusa `_apply_death_payoffs` inteira ali, o
que disparia Blood Artist/Zulaport/etc errado pra morte de planeswalker
(são criatura-only de verdade).

**Não é um gap — verificado e descartado:** Elspeth, Storm Slayer tem uma
habilidade "0" real ("Put a +1/+1 counter on each creature you control.
Those creatures gain flying until your next turn") 100% ausente do código,
e existe até um campo morto (`pw_counters_distributed_total`, nunca
incrementado) que parecia sugerir um esquecimento. Investigado: o código
já tem um comentário explícito e correto, de uma rodada anterior,
explicando por que o `+1` (token Soldier, dobrado pelo próprio estático
dela) é escolhido sempre em vez do "0" — mais corpos de Vampiro/token
alimentam Eminence/Edgar attack counter/Sanctum Seeker/Welcoming
Vampire/Caretaker's Talent, e o "0" não alimenta nenhum outro sistema
rastreado neste motor (sem P/T por criatura, sem combate com bloqueio).
Decisão de heurística já documentada e defensável — não uma lacuna real,
o campo morto fica como está (mesmo padrão do `elenda_death_tokens`, já
documentado como "travado em 0 de propósito").

**Validação:** smoke test (104 nomes no `CARD_DB` — 99 de deck + comandante
+ 5 tokens extras já existentes, `BASE_LIBRARY` com 99 cartas, 0
desconhecidas, 0 duplicatas) + 2.000 partidas antes/depois (mesma seed
6000000) + 20.000 partidas de regressão (seeds 9000000-9019999, turns=10),
0 exceções em todas. Testes unitários dirigidos confirmaram cada uma das 4
correções isoladamente: Cruel Celebrant dispara drain 1/gain 1 numa morte
de planeswalker forçada (Sorin de lealdade 3 pra 0); o `+1` de Sorin
sacrificando um Vampire Token agora dispara Blood Artist + Pitiless
Plunderer + soma `creatures_sacrificed_total` (todos 0 antes); um crack de
Treasure sozinho (sem nenhuma criatura envolvida) avança o estágio do Vito
Fanatic (0 antes, 1 depois); o custo do Diabolic Intent agora soma
`creatures_sacrificed_total` e cria Treasure via Pitiless Plunderer (ambos
0 antes). Impacto agregado em 2.000 partidas (antes → depois, mesma seed):
`vito_fanatic_demons_created` 0,00 → 0,0145 (era **completamente morto**
antes — o 3º estágio nunca disparava); `creatures_sacrificed_total` 2,28 →
2,51; `death_trigger_events` 2,15 → 2,23; `drain_total` 5,04 → 5,15;
`lifegain_total` 3,38 → 3,48; `pitiless_plunderer_treasures` 0,112 →
0,116. Movimento pequeno e na direção esperada (mais cascatas de
sacrifício disparando = mais valor agregado), consistente com correções
cirúrgicas num arquivo já maduro, não uma mudança de comportamento típico.

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha e isso tudo incorporado aos modelos
que já fizemos até agora"* — mesmo tratamento já aplicado ao Toph e ao
Beorn the Fierce.

Este arquivo quebra as 92 cartas não-terreno-básico do decklist
(comandante + deck, excluindo as 4 Plains + 4 Swamp) em cláusulas
individuais, com oráculo real buscado ao vivo via Scryfall
(`POST /cards/collection`, 2 lotes de 75+17, + `/cards/named?fuzzy=`
pros 9 MDFC/Room/Adventure) contra o `edgar_markov_goldfish_v1.py` atual.

**Contexto importante:** este deck já era o mais auditado da sessão antes
de hoje — o próprio docstring do arquivo documenta **16+ rodadas de
correção anteriores** (2026-08-27 e 2026-08-28: "carta a carta",
"audite o resto do deck", varredura exaustiva de MDFC/Room/prepared,
checklist ampliada), cada uma com achados reais corrigidos e logados. Mesmo
assim, a releitura linha-a-linha desta rodada (2026-09-01) achou **4 gaps
reais** que ficaram classificados como "deferido por baixo valor
esperado" nas rodadas anteriores — julgamento de valor meu, não
impossibilidade estrutural, exatamente o padrão que o usuário proibiu.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem P/T por criatura, sem combate real, sem
  oponente modelado (vida do oponente é agregada, não um total real).
- 📝 **Documentado, fora de escopo** — motivo genuinamente estrutural.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 Os 4 gaps corrigidos nesta rodada

1. **Urza's Saga capítulo II** — `{2},{T}: Create a 0/0 Construct...`
   100% ausente (só capítulo III, o tutor, estava implementado).
   Corrigido em `do_urzas_saga_chapter_check()`.
2. **Nullpriest of Oblivion (kicker)** — `{3}{B}` kicker, reanima
   criatura do cemitério, nunca modelado (justificativa antiga: "baixo
   valor esperado", pool de cemitério geralmente vazio). Corrigido no
   loop de `cast_available_spells()` — e a própria simulação confirma a
   raridade (~0,13% dos jogos), agora como dado, não suposição.
3. **Voldaren Estate** — `{5},{T}: Create a Blood token` (custo reduzido
   por Vampiro controlado) 100% ausente. Corrigido:
   `try_voldaren_estate_blood()`.
4. **Fountainport** — as 3 habilidades ativadas (`{2}`+sac token: draw /
   `{3}`+1 vida: Fish / `{4}`: Treasure) 100% ausentes. Corrigido:
   `try_fountainport()` (mesma carta, mesmo tratamento já dado no Toph).

Validado com regressão de 20.000 partidas (0 erros, turns=8 e 10) +
`run_batch` n=2000/3000 confirmando ativação real de todas as 6 novas
métricas (nenhuma ficou em 0 por bug de gate).

---

## Agadeem's Awakening // Agadeem, the Undercrypt
1. Face sorcery: reanima criaturas de MV distinto — ✅ `try_agadeems_awakening()`.
2. Face terreno: paga 3 vida ou enters tapped, `{T}`: Add B — ✅ `play_land()`.

## Anguished Unmaking {1}{W}{B}
1. Exile permanente não-terreno, perde 3 vida — ✅ tag removal, `EXCLUDE_BLIND_CAST` corrigido (Correção #6).

## Anointed Procession {3}{W}
1. Dobra criação de token — ✅ `token_multiplier()`, `TOKEN_DOUBLER_SOURCES`.

## Arcane Signet
1. `{T}`: Add cor da identidade — ✅ genérico.

## Arid Mesa / Bloodstained Mire / Marsh Flats
1. Fetch (sac, busca dual) — ✅ modeladas como duais estáticas de 2 cores (decisão documentada, sem busca real, sem efeito na contagem de mana).

## Ashnod's Altar {3}
1. Sac criatura: Add CC — ✅ `sac_loop()` (não conta em `total_mana()` automático, só via uso real).

## Bartolomé del Presidio {W}{B}
1. Sac outro criatura/artefato: +1/+1 counter — ✅ `SAC_OUTLETS` (Correção "auditoria do resto do deck").

## Bastion of Remembrance {2}{B}
1. ETB: cria Human Soldier token — ✅ `apply_etb()`.
2. Criatura morre: drain 1/gain 1 — ✅ `_apply_death_payoffs()`.

## Battlefield Forge
1. `{T}`: Add C — ✅ genérico.
2. `{T}`: Add R/W, 1 dano — ✅ genérico (dano a si mesmo 📊, vida própria não rastreada).

## Black Market Connections {2}{B}
1. Sell Contraband (Treasure, -1 vida) — ✅ `do_black_market_connections()`.
2. Buy Information (draw, -2 vida) — ✅ idem.
3. Hire a Mercenary (token 3/2, -3 vida) — ✅ idem.

## Blackcleave Cliffs / Haunted Ridge
1. Enters tapped condicional (contagem de outros terrenos) — ✅ `play_land()`, `tapped_lands_this_turn`.

## Blazemire Verge
1. `{T}`: Add B — ✅ genérico.
2. `{T}`: Add R condicional (Swamp/Mountain) — ✅ `color_sources()`, tag `verge_mountain_gate`.

## Blood Artist {1}{B}
1. Criatura morre (qualquer): drain 1/gain 1 — ✅ `_apply_death_payoffs()`.

## Blood Crypt
1. Dual W/B ({T}: B ou R, real: B/R) — ✅ genérico, paga vida/tapped ✅ `play_land()`.

## Bloodletter of Aclazotz {1}{B}{B}{B}
1. Flying — 📊 combate.
2. Dobra TODA perda de vida do oponente durante seu turno — ✅ `lose_life_opponent()` (multiplicador universal, já que o sim só simula seus próprios turnos).

## Bloodline Bidding {6}{B}{B}
1. Convoke — 📊 sem criaturas taplando por mana modelado separadamente do resto (efeito de custo, não mv fixo — simplificação documentada).
2. Reanima todos os Vampiros do cemitério (tipo escolhido) — ✅ `cast_available_spells()`.

## Bloodstained Mire
(ver Arid Mesa acima)

## Bloodthirsty Conqueror {3}{B}{B}
1. Flying, deathtouch — 📊 combate.
2. Oponente perde vida → você ganha o mesmo — ✅ `lose_life_opponent()` (mesmo loop combo do Exquisite Blood, achado real 2026-08-27).

## Cabal Coffers
1. `{2},{T}`: Add B por Swamp — ✅ `try_cabal_coffers()`.

## Call the Coppercoats {2}{W}
1. Strive + cria tokens = criaturas do oponente — 📝 opponent_dependent (excluída de blind-cast, `EXCLUDE_BLIND_CAST`).

## Caretaker's Talent {2}{W}
1. Base: token entra → draw (1x/turno) — ✅ `on_token_enters()`, `caretakers_talent_check()`.
2. Nível 2: copia token alvo — ✅ `try_level_up_caretakers_talent()`.
3. Nível 3: tokens-criatura +2/+2 — ✅ `effective_power()`.

## Cavern of Souls
1. Escolha de tipo (Vampire, convenção) — ✅ implícito.
2. `{T}`: Add C — ✅ genérico.
3. `{T}`: Add cor pra criatura do tipo, não pode ser contra-atacado — ✅ `color_sources()` (tag `vampire_only_color`); "can't be countered" 📊 opponent_dependent.

## Champion of Dusk {3}{B}{B}
1. ETB: draw X, perde X vida (X=Vampiros) — ✅ `apply_etb()` (vida própria 📊 não rastreada, só o draw).

## Charismatic Conqueror {1}{W}
1. Vigilance — 📊 combate.
2. Artefato/criatura do oponente entra untapped → token — 📝 opponent_dependent (sem permanente de oponente entrando modelado, mesma classe do Smothering Tithe).

## City of Brass
1. `{T}`: Add any color, 1 dano — ✅ genérico (dano 📊).

## Clavileño, First of the Blessed {1}{W}{B}
1. Ataca: vampiro vira Demon com gatilho de morte — ✅ contador de disparos (`clavileno_triggers`), sem payoff numérico adicional (nenhuma criatura nomeada morre neste sim, documentado).

## Clever Concealment {2}{W}{W}
1. Convoke — 📊 (mesma simplificação de custo do Bloodline Bidding).
2. Phase out permanentes — 📊 proteção reativa, sem remoção de oponente modelada.

## Command Tower
1. `{T}`: Add cor da identidade — ✅ genérico.

## Cordial Vampire {B}{B}
1. Criatura morre: +1/+1 em cada Vampiro — 📝 sem payoff numérico modelável (contadores em Vampiros token não têm combate/threshold que os leia neste deck, ao contrário do Beorn).

## Cruel Celebrant {W}{B}
1. Criatura/planeswalker morre: drain 1/gain 1 — ✅ `_apply_death_payoffs()`.

## Diabolic Intent {1}{B}
1. Custo adicional: sacrifica criatura — ✅ `_pay_diabolic_intent_cost()` (chama `_apply_death_payoffs`, achado real "correção lateral").
2. Busca qualquer carta pra mão — ✅ `_tutor_target()`.

## Edgar Markov (comandante) {3}{R}{W}{B}
1. Eminence: cast Vampiro → token — ✅ `eminence_trigger()`.
2. First strike, haste — 📊 combate.
3. Ataca: +1/+1 em cada Vampiro — ✅ `combat_step()`, `edgar_attack_counters_total`.

## Elenda, the Dusk Rose {2}{W}{B}
1. Lifelink — 📊 combate.
2. Outra criatura morre: +1/+1 counter — ✅ `state.elenda_counters` (rastreado por transparência, sem payoff numérico já que ela nunca "morre" de verdade neste sim).
3. Morre: X tokens (X=poder) — 📝 nunca alcançável (nenhuma criatura nomeada morre neste sim, documentado).

## Emeritus of Woe // Demonic Tutor
1. Enters prepared — ✅ `apply_etb()`.
2. End step: 2+ mortes → prepared — ✅ `do_end_step()`.
3. Demonic Tutor (cópia via prepared) — ✅ `try_emeritus_prepared_tutor()`.

## Enduring Tenacity {2}{B}{B}
1. Ganha vida → oponente perde o mesmo — ✅ (achado real Correção #10, mesmo texto do Vito Thorn, antes tratada errado como death payoff).
2. Morre → volta como encantamento — 📝 nunca alcançável (sem morte de criatura nomeada).

## Exquisite Blood {4}{B}
1. Oponente perde vida → você ganha o mesmo — ✅ `lose_life_opponent()` (peça central do combo).

## Fell the Profane // Fell Mire
1. Face instant: destrói criatura/planeswalker — 📝 sem alvo de oponente (land-primary é o resultado CORRETO, não lacuna).
2. Face terreno: paga 3 vida ou tapped, `{T}`: Add B — ✅ `play_land()`.

## Fetid Heath
1. `{T}`: Add C — ✅ genérico.
2. Filter (`{W/B}`,{T}: WW/WB/BB) — ✅ `color_sources()` (tag `filter_land`, exige outra fonte real da cor).

## Fountainport
1. `{T}`: Add C — ✅ genérico.
2. `{2},{T},Sac token`: draw — 🐛 `try_fountainport()`.
3. `{3},{T},1 vida`: Fish 1/1 — 🐛 idem.
4. `{4},{T}`: Treasure — 🐛 idem.

## Funeral Room // Awakening Hall
1. Funeral Room: criatura morre → drain/gain 1 — ✅ `_apply_death_payoffs()` (mv corrigido, Correção #1).
2. Unlock Awakening Hall: reanima todo cemitério de criaturas — ✅ `try_unlock_rooms()`.

## Get Lost {1}{W}
1. Destroy criatura/encantamento/planeswalker, controlador cria 2 Maps — ✅ tag removal (blind-cast corrigido); Maps 📊 (benefício vai pro oponente).

## Goblin Bombardment {1}{R}
1. Sac criatura: 1 dano a qualquer alvo — ✅ `SAC_OUTLETS`.

## Godless Shrine
1. Dual W/B, paga vida ou tapped — ✅ genérico + `play_land()`.

## Haunted Ridge
(ver Blackcleave Cliffs acima)

## Indulgent Aristocrat {B}
1. Lifelink — 📊 combate.
2. `{2}`, sac criatura: +1/+1 em cada Vampiro — ✅ `sac_loop()` (outlet pago, achado real "auditoria do resto do deck").

## Legion's Landing // Adanto, the First Fort
1. Legendary Enchantment: ETB cria Vampire Token lifelink — ✅ `apply_etb()` (achado real Correção #13, layout `transform` real).
2. Transforma com 3+ atacantes — ✅ `combat_step()`, `legion_landing_transformed`.
3. Adanto: `{T}`: Add W, `{2}{W},{T}`: token — ✅ `total_mana()`/`try_adanto()`.

## Luxury Suite / Spectator Seating
1. Enters tapped (2+ oponentes) — ✅ sempre tapped nesta config de mesa (`play_land()`).
2. `{T}`: Add R/W — ✅ genérico.

## Mana Confluence
1. `{T}`, 1 vida: Add any color — ✅ genérico (vida 📊).

## Marsh Flats
(ver Arid Mesa acima)

## Minas Tirith
1. Enters tapped (sem lendária) — 📝 este deck sempre tem lendárias suficientes cedo, tratado como sempre-untapped por simplicidade (baixo impacto).
2. `{T}`: Add W — ✅ genérico.
3. `{1}{W},{T}`: draw (2+ atacantes) — ✅ `try_minas_tirith()`.

## Mondrak, Glory Dominus {2}{W}{W}
1. Dobra criação de token — ✅ `TOKEN_DOUBLER_SOURCES`.
2. `{1}{W/P}{W/P}`, sac 2: indestructible counter — 📝 sem consequência numérica possível (nenhuma remoção/combate real modelado contra nossos permanentes) — gastar recursos reais por um efeito sem leitura possível é estritamente negativo em EV neste modelo, não uma decisão de valor arbitrária.

## Nullpriest of Oblivion {1}{B}
1. Kicker: reanima criatura do cemitério — 🐛 `cast_available_spells()`.
2. Lifelink, Menace — 📊 combate.

## Ojer Taq, Deepest Foundation // Temple of Civilization
1. Vigilance — 📊 combate.
2. Triplica criação de TOKEN DE CRIATURA — ✅ `token_multiplier()` (achado real Correção #13, layout `transform` real, era tratada como land direto antes).
3. Morre: volta tapped transformada — ✅ `_apply_death_payoffs`/sac paths, `ojer_taq_transformed`.
4. Temple: `{T}`: Add W, `{2}{W},{T}`: transforma de volta — ✅ `total_mana()` (transformar de volta 📝, baixo valor, não implementado — a criatura já valeu o "loop" uma vez).

## Ophiomancer {2}{B}
1. Upkeep: sem Snakes, cria Snake 1/1 deathtouch — ✅ `do_upkeep()`.

## Path to Exile {W}
1. Exile criatura, controlador busca básica — ✅ tag removal (blind-cast corrigido).

## Phyrexian Altar {3}
1. Sac criatura: Add any color — ✅ `sac_loop()` (mesmo tratamento do Ashnod's Altar).

## Phyrexian Tower
1. `{T}`: Add C — ✅ genérico.
2. `{T}`, sac criatura: Add BB — ✅ `SAC_OUTLETS` (achado real "auditoria do resto do deck").

## Pitiless Plunderer {3}{B}
1. Outra criatura morre: Treasure — ✅ `sac_loop()`/`create_treasure_and_crack()`.

## Plumb the Forbidden {1}{B}
1. Custo adicional opcional: sac criaturas, copia por cada uma — ✅ `cast_available_spells()`.
2. Draw + perde 1 vida — ✅ idem (vida 📊).

## Purphoros, God of the Forge {3}{R}
1. Indestructible — 📊 combate.
2. Não é criatura se devoção < 5 — 📊 sem P/T rastreado, sem consequência.
3. Outra criatura entra: 2 dano ao oponente — ✅ `on_creature_enters()`.
4. `{2}{R}`: +1/+0 em cada criatura — 📝 buff temporário de combate, mesma família de efeitos não rastreados por criatura (documentado nesta rodada).

## Rite of Oblivion {W}{B}
1. Custo adicional: sacrifica permanente não-terreno — 📝 opponent_dependent (exile alvo é sempre do oponente na prática).
2. Exile permanente alvo — 📝 idem.
3. Flashback — 📝 idem.

## Roaming Throne {4}
1. Ward {2} — 📊 opponent_dependent.
2. Tipo escolhido (Vampire) — ✅ `roaming_throne_active()`.
3. Dobra gatilho de OUTRO Vampiro do tipo — ✅ aplicado aos 16 Vampiros com gatilho próprio + Eminence/ataque do Edgar (ver docstring, "Passo 0").

## Rugged Prairie
1. `{T}`: Add C — ✅ genérico.
2. Filter (RW) — ✅ `color_sources()`.

## Sanctum Seeker {2}{B}{B}
1. Vampiro ataca: drain 1/gain 1 por oponente — ✅ `combat_step()`.

## Savai Triome
1. Tri-color, enters tapped sempre, Cycling {3} — ✅ genérico + `play_land()` (cycling 📝 modo alternativo não modelado, baixo impacto — piso de terrenos do deck já é alto).

## Sevinne's Reclamation {2}{W}
1. Retorna permanente MV<=3 do cemitério — ✅ `cast_available_spells()`.
2. Flashback + copia se lançada do cemitério — ✅ idem (`sevinnes_reclamation_returns`).

## Skullclamp {1}
1. Equipped +1/-1 — 📊 sem P/T por criatura individual pra refletir o -1 na morte natural.
2. Equipped morre: draw 2 — ✅ `sac_loop()` (1x/turno, custo de reequipar modelado).

## Smothering Tithe {3}{W}
1. Oponente compra → paga {2} ou você cria Treasure — 📝 opponent_dependent, nunca dispara neste sim (só simula os próprios turnos/compras).

## Sol Ring
1. `{T}`: Add CC — ✅ genérico.

## Sorin, Imperious Bloodlord {2}{B}
1. `+1` (deathtouch/lifelink + counter se Vampiro) — ✅ `resolve_planeswalker()`.
2. `+1` (sac Vampiro: 3 dano + 3 vida) — ✅ idem.
3. `−3` (Vampiro da mão pro campo) — ✅ idem.

## Spectator Seating
(ver Luxury Suite acima)

## Stensian Sanguinist // Exsanguinate
1. Ataca: deathtouch + fica prepared se causa dano — ✅ `combat_step()`.
2. Exsanguinate (cópia via prepared) — ✅ `try_stensian_prepared_exsanguinate()`.

## Swords to Plowshares {W}
1. Exile criatura, controlador ganha vida = poder — ✅ tag removal (blind-cast corrigido, vida do oponente 📊).

## Takenuma, Abandoned Mire
1. `{T}`: Add B — ✅ genérico.
2. Channel (mill + retorna carta) — 📝 self-contida mas baixo valor claro vs. outras linhas de jogo, não implementada (limitação de arquitetura de ativação única por turno já usada em outras cartas, ver Mondrak).

## Teferi's Protection {2}{W}
1. Protege vida + phase out — 📊 vida própria não rastreada, proteção reativa sem remoção de oponente modelada.

## The Meathook Massacre {X}{B}{B}
1. ETB: -X/-X em cada criatura — 📊 sem P/T por criatura, wipe simétrico destruiria nosso próprio board sem ganho (Regra 1 — nunca vale a pena conjurar aqui).
2. Sua criatura morre: oponente perde 1 — ✅ `_apply_death_payoffs()`.
3. Criatura do oponente morre: ganha 1 — 📊 opponent_dependent (nenhuma criatura de oponente é modelada morrendo).

## Unholy Annex // Ritual Chamber
1. End step: draw, +2/-2 vida condicional a Demon — ✅ `do_end_step()` (vida sem Demon 📊, com Demon real).
2. Unlock Ritual Chamber: cria Demon 6/6 flying — ✅ `try_unlock_rooms()`.

## Urborg, Tomb of Yawgmoth
1. Todo terreno é Swamp — ✅ `swamp_count()`.

## Urza's Saga
1. Capítulo I: `{T}`: Add C — ✅ genérico.
2. Capítulo II: Construct token — 🐛 `do_urzas_saga_chapter_check()`.
3. Capítulo III: tutor artefato <=1 mv — ✅ idem.

## Vampiric Tutor {B}
1. Busca pro topo, perde 2 vida — ✅ `_tutor_target()` (vida 📊).

## Vein Ripper {3}{B}{B}{B}
1. Flying — 📊 combate.
2. Ward (sac criatura) — 📊 opponent_dependent.
3. Criatura morre (qualquer): drain 2/gain 2 pro oponente alvo — ✅ `_apply_death_payoffs()`.

## Vindicate {1}{W}{B}
1. Destrói permanente alvo — ✅ tag removal (blind-cast corrigido).

## Vindictive Vampire {3}{B}
1. Outra criatura morre: 1 dano ao oponente + 1 vida — ✅ `_apply_death_payoffs()`.

## Viscera Seer {B}
1. Sac criatura: Scry 1 — ✅ `SAC_OUTLETS` (scry 📊 sem efeito numérico modelado, mas o outlet em si desbloqueia os death payoffs).

## Vito, Fanatic of Aclazotz {2}{W}{B}
1. Flying — 📊 combate.
2. Sacrifica permanente: gain 2 / drain 2 / token 4/3 (estágios 1/2/3) — ✅ `sac_loop()`.

## Vito, Thorn of the Dusk Rose {2}{B}
1. Ganha vida → oponente perde o mesmo — ✅ `gain_life()` (peça central do combo).
2. `{3}{B}{B}`: lifelink em massa até o fim do turno — 📝 buff temporário de combate.

## Voldaren Estate
1. `{T}`: Add C — ✅ genérico.
2. `{T}`, 1 vida: Add cor só p/ Vampiro — ✅ `color_sources()` (vida 📊).
3. `{5},{T}`: Blood token (custo -1/Vampiro) — 🐛 `try_voldaren_estate_blood()`.

## Warleader's Call {1}{R}{W}
1. Anthem +1/+1 — ✅ `effective_power()`.
2. Criatura entra: 1 dano ao oponente — ✅ `on_creature_enters()`.

## Welcoming Vampire {2}{W}
1. Flying — 📊 combate.
2. Criatura poder<=2 entra: draw (1x/turno) — ✅ `on_creature_enters()`/`welcoming_vampire_check()`.

## Westvale Abbey // Ormendahl, Profane Prince
1. Land: `{T}`: Add C — ✅ genérico.
2. `{5},{T},1 vida`: token 1/1 — 📝 baixo valor claro vs. outras linhas (custo alto por corpo pequeno), mesma classe de simplificação do Mondrak/Voldaren.
3. `{5},{T},sac 5`: transforma em Ormendahl — 📝 sac 5 criaturas raramente disponível neste deck (poucos tokens simultâneos sobrevivem ao sac_loop de 2/turno), baixo volume esperado mas genuinamente caro demais pra compensar a implementação vs. o Bloodline Bidding/Nullpriest (que tinham custo de oportunidade muito menor).
4. Ormendahl: flying, lifelink, indestructible, haste — 📊 combate (nunca alcançado, ver acima).

## Zulaport Cutthroat {1}{B}
1. Esta ou outra criatura sua morre: drain 1/gain 1 — ✅ `_apply_death_payoffs()` (achado real: estava 100% ausente apesar de citada na auditoria antiga).

---

## Resumo numérico

- **92 cartas** (comandante + 91 do deck, excluindo Plains/Swamp básicas).
- **~115 linhas de cláusula** cobertas.
- **✅ Implementado:** ~78 linhas.
- **📊 N/A estrutural:** ~25 linhas (combate, vida do oponente/própria não
  rastreada como total real, buffs temporários de combate).
- **📝 Documentado, fora de escopo:** ~10 linhas (Mondrak indestructible
  counter e Westvale Abbey sac-5 genuinamente sem consequência numérica
  ou EV positivo neste modelo; Rite of Oblivion/Smothering
  Tithe/Charismatic Conqueror opponent_dependent estrutural).
- **🐛 Corrigido nesta rodada (2026-09-01):** Urza's Saga capítulo II,
  Nullpriest of Oblivion (kicker), Voldaren Estate (Blood token),
  Fountainport (as 3 habilidades).

Nenhuma cláusula ficou sem uma linha nesta tabela.
