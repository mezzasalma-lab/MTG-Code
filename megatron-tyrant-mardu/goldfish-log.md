# Goldfish Log — Megatron, Tyrant

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Reconstrução completa: shell de weld/cheat/sacrifice — 2026-09-02

**Gatilho:** o usuário conseguiu com o dono real do deck (o oponente
citado nas partidas presenciadas) a lista inicial dele. Comparando com o
que tínhamos (montado por frequência entre decklists públicas + primer),
ficou claro que o plano de jogo real é outro: solda/recupera artefato
(Goblin Welder/Trash for Treasure/Scrap Welder/Scrap Trawler/Daretti x2)
+ cheat pra campo (Sneak Attack/Anrakyr the Traveller/Feldon of the
Third Path) + Warstorm Surge como motor de dano — não "Megatron
sacrifica combustível barato todo turno".

**Decisão da lista final** (ver `lista.md` pro detalhamento completo):
lista real do dono (100 cartas, já vinha pronta) menos 8 cortes fracos/
redundantes (Sojourner's Companion, Frogmyr Enforcer, Psychotic Fury,
Temur Battle Rage, Seize the Spotlight, Cathartic Reunion, Evendo
Brushrazer, Coveted Jewel) mais 8 adições confirmadas pelo usuário
(Rakdos the Muscle, Summon: Bahamut, Osgir the Reconstructor, Wheel of
Fortune, Phyrexian Triniform, Blasphemous Act — vistas ao vivo, ausentes
dessa lista "inicial" — mais Shields Up! e Blacksmith's Skill, pedidas à
parte). Terrenos rebalanceados por peso real de pips (R 59,6%/B 28,8%/
W 11,5% dos símbolos coloridos — branco é a cor mais leve, nenhum custo
duplo-branco na lista inteira) e upgradados pra base premium ABUR
(Plateau/Scrubland/Badlands no lugar das 3 painlands, budget liberado
pra proxy) + Adagia, Windswept Bastion (Planet land que duplica
artefato) no lugar de 1 Plains.

**`megatron_goldfish_v1.py` reescrito do zero.** Oráculo das 76 cartas
não-terrenas confirmado via Scryfall antes de qualquer código. Motor
novo: `creature_enters()` como ponto único de ETB de criatura (dispara
Warstorm Surge sempre, real poder dinâmico via `get_power()` pro Daretti
Rocketeer Engineer), `sacrifice()` como ponto único de sacrifício
(dispara Scrap Trawler/toolbox/Triniform/Rakdos automaticamente), fodder
escolhido via `best_weld_fodder()`/`best_payoff_fodder()` (nunca
sacrifica board real por payoff puro — só fodder temporário "grátis").

**4 classes de bug real achadas e corrigidas durante os testes** (não
hipotéticas — cada uma reproduzida e confirmada antes do fix):
1. `cast_megatron` checava "está na mão", mas o comandante corretamente
   nunca entra na mão (zona de comando) — Megatron nunca era conjurado
   em partida NENHUMA (100% de 2.000 jogos testados antes do fix).
2. Heurística de "pior carta pra descartar" usava só menor MV, então
   Looting/Laughing Mad descartavam os próprios terrenos da mão antes de
   conseguirem ser jogados — travava o desenvolvimento de mana da
   partida inteira. Corrigido com `worst_discard_target()` (protege
   terrenos até 6 em campo).
3. Recursão infinita real: Mirrorworks/Skitterbeam Battalion copiando a
   si mesmos via token, porque a checagem "if you cast it"/"nontoken"
   real do oráculo não excluía tokens — corrigido propagando um
   parâmetro `token` por `creature_enters`/`resolve_etb`/`artifact_etb_hooks`.
4. `ValueError` real em 5 pontos de solda: escolher alvo no cemitério
   ANTES de sacrificar o fodder cria uma janela onde o próprio
   sacrifício (gatilho de morte do toolbox) pode consumir o mesmo alvo —
   corrigido com guardas defensivas em Goblin Welder/Scrap Welder/Trash
   for Treasure/Goblin Engineer/Daretti/Metalwork Colossus.

**Validação:** 11 testes unitários isolados + 3 rodadas de 20.000
partidas (seeds 1M/2M, turns=10, **0 exceções, 0 timeouts**) +
comparação turns=8 vs turns=14 (3.000 jogos cada) confirmando que o
motor escala de forma real com mais turnos (Daretti chega ao -10 em
3,4%→11,7%, Ayara transforma em 1,5%→10,9%, artefatos sacrificados
2,78→8,90) — consistente com um motor de valor que precisa de tempo pra
montar, não um bug. Turno médio de conjuração do Megatron: 4,27-5,02.
Dano proxy médio: 26,5 (turns=8) / 83,3 (turns=14).

Detalhamento completo carta a carta em `checklist-oraculo.md`.

---

### Reauditoria linha-a-linha completa das 99 cartas — 2026-09-02

**Gatilho:** o usuário perguntou sobre Stensian Sanguinist e eu respondi
errado (disse MDFC — na real é a keyword **"prepared"**, mecânica
diferente). Ele corrigiu e cobrou: *"Eu não mandei vc auditar TODAS as
cartas linha por linha e uma por uma?"* — sinal de que a rodada de
2026-09-01 (ver entrada mais abaixo) não tinha sido tão completa quanto
o checklist afirmava.

Refiz a varredura inteira: oráculo real via Scryfall pras 93 cartas
não-terreno-básico, cruzado carta por carta contra o código. Achado mais
grave: **Starscream, Power Hungry** — segundo DFC `transform` da lista,
paralelo ao Megatron com mecânica própria de monarquia — existia só como
nome no `CARD_DB` (tag genérica, poder 0), mecânica 100% ausente, apesar
do checklist anterior ter afirmado (errado) que estava "implementada
análoga ao Megatron". Mais 10 gaps reais achados e corrigidos na mesma
rodada: Excalibur (custo/equip), Night's Whisper (carta inteira não
fazia nada), Rakdos the Muscle (gatilho de sacrifício), Atraxa's
Skitterfang (oil counters), Etched Familiar (dreno de morte), Steel
Seraph (grant de keyword), Chromatic Orrery (2ª habilidade), Marsh Flats
(estava sendo tratada como dual estático em vez de fetchland de
verdade — e ao corrigir isso achei que `crack_fetch()` também não
filtrava pelos tipos básicos certos por fetch), Cursed Mirror (ETB de
clone) e Vandalblast (custo errado — bug meu desta sessão, `{1}{R}` em
vez do `{R}` real). Mais 12 valores de poder impressos incorretos
(cosmético — `.power` não é lido em lugar nenhum dentro deste arquivo
solo, só importaria se plugado no motor de mesa externo).

**Validação:** 11 testes unitários isolados (1 por mecânica nova) + 3
rodadas de regressão de 20.000 partidas (seeds 9M/12M/14M, turns=10, **0
exceções, 0 timeouts**) + `run_batch` de 5.000 jogos confirmando sinal
real de cada mecânica (Starscream monarquia ~13-14% dos jogos, Excalibur
conjurada ~11-12%, Cursed Mirror copia o Megatron ~9%). Dano proxy médio
subiu de ~31 pra ~38-39, vida ganha de ~0,5 pra ~3,6-3,8 — mudança real e
grande, não ruído, coerente com corrigir uma dúzia de mecânicas que
antes não faziam nada. Detalhamento completo (carta a carta) em
`checklist-oraculo.md`.

---

### Bracket 2 — remoção dos 3 Game Changers + troca Rakdos Charm → Phyrexian Triniform — 2026-09-02

**Parte 1 — Phyrexian Triniform:** discutindo Portal to Phyrexia, o
usuário identificou que a carta real com "9/9, quando morre gera 3
artefatos 3/3" era **Phyrexian Triniform** — já citada no docstring do
arquivo como "vista ao vivo num oponente real", mas nunca de fato
incluída nas 99 cartas. Adicionada no lugar de Rakdos Charm (peça de
interação mais redundante — já havia 7 outras). Gatilho de morte real
implementado em `toolbox_recur_death_trigger()` (3 tokens 3/3, também
elegíveis como combustível do Megatron).

**Parte 2 — Bracket 2:** pedido direto do usuário — *"Pode tirar o One
Ring e o Smothering Tithe" / "Pode tirar os 3 GCs, quero ele B2"*. Os 3
Game Changers da lista (cross-reference contra `is:gamechanger` do
Scryfall, feito antes nesta sessão): Smothering Tithe, The One Ring,
Teferi's Protection — todos removidos.

**Achado ao remover:** o campo `the_one_ring_burden` só era checado no
upkeep (`self_damage`), **nunca incrementado em lugar nenhum** — The One
Ring nunca causou autodano de verdade neste simulador, apesar de listado
como "implementado" numa rodada anterior deste log. Removê-lo não perde
nenhum dado real de simulação.

Substituídas por Mind Stone (rock + fuel), Sword of the Animist (+1/+1 e
busca terreno básico a cada ataque do Megatron, implementado de verdade
em `megatron_combat()`) e Vandalblast (remoção de artefato, tag
`interaction`) — nenhuma delas é Game Changer.

**Validação:** import + `len(BASE_LIBRARY) == 99` após as duas trocas +
regressão de 5.000 partidas (seed 7000000, turns=8, 0 exceções). Dano
proxy médio 31,40 (era 30,61 só com a troca do Triniform, 28,18 na
baseline original de 2026-08-29) — consistente com uma troca
aproximadamente neutra em poder bruto, dentro do ruído normal entre
seeds.

Detalhamento completo em `checklist-oraculo.md`.

---

### Correção — Plaza of Heroes / infraestrutura "legendary" morta — 2026-09-02

**Gatilho:** usuário lembrou "The Ten Rings" (já correta — max hand size
10 + draw-to-10 no end step). Ao reconferir, achei `is_legendary()`/
`LEGENDARY_NAMES` (13 permanentes legendários da lista) definidos mas
nunca chamados em lugar nenhum, o que apontou pra Plaza of Heroes: só o
modo incolor genérico dela estava implementado — o modo mais valioso
("Add one mana of any color. Spend this mana only to cast a legendary
spell") 100% ausente.

Corrigido: `color_sources(state, color, spell_name=name)` agora conta
Plaza como fonte de qualquer cor faltante quando o spell sendo
conjurado é legendário. Os outros 2 modos (fixar cor pra ativar
habilidade de legendário / hexproof+indestructible) ficam de fora por
razão estrutural real (sem framework genérico de ativação paga / sem
oponente real modelado), não por julgamento de valor.

**Validação:** 4 testes unitários isolados + regressão de 20.000
partidas (0 exceções) + `run_batch` antes/depois (3000 jogos): turno
médio do Megatron 5.02→4.97, "nunca conjurado em 10 turnos" 11.6%→10.8%.
Ver `checklist-oraculo.md` pra detalhamento completo.

**Achado incidental não corrigido nesta rodada:** Talon Gates of Madara
também tem 2 modos reais além do incolor genérico já coberto — *"{1},
{T}: Add one mana of any color"* (filtro pago, não fixação estática
como a Plaza — exigiria rastrear tap-state por terreno individual, que
este arquivo não modela em lugar nenhum) e *"{4}: Put this card from
your hand onto the battlefield"* (hardcast alternativo, bypassa o land
drop). O 2º modo é limpo de implementar com a infraestrutura atual; não
implementado ainda porque surgiu como achado incidental fora do escopo
da pergunta desta rodada, não por decisão de que "não vale a pena" —
fica marcado aqui pra não ser esquecido.

---

## Simulação #1 — goldfish Python completo (`megatron_goldfish_v1.py`) — 2026-08-29

**Contexto:** deck montado do zero nesta sessão a partir de (1) um primer
real de Megatron encontrado pelo usuário — que argumenta explicitamente
contra o "EDHREC Effect" (pegar só as cartas mais populares sem entender
o motor real do comandante) —, (2) 5 decklists reais adicionais
(Moxfield/Archidekt) cruzadas por frequência de inclusão, e (3) cartas
confirmadas pelo usuário como vistas ao vivo num oponente real. Todo o
processo de montagem (avaliação de troca por troca, curva, sinergia)
está registrado na conversa que originou este deck — este log cobre só a
implementação do simulador.

**Passo 0 (checklist de `references/goldfish-sim-card-rules.md`):**
varredura mecânica completa das 99 cartas + comandante via Scryfall real,
nenhum efeito assumido de memória. Achado central que motivou toda a
arquitetura do arquivo: **Megatron é um DFC `transform` de verdade**, e o
oráculo real revela uma interação sutil que o próprio primer usa mas não
deixa 100% explícita — a face da frente (Tyrant) e a face de trás
(Destructive Force) têm habilidades DIFERENTES e complementares:

- **Destructive Force (verso, Vehicle 4/5)**: "Whenever Megatron attacks,
  you may sacrifice another artifact. When you do, Megatron deals damage
  equal to the sacrificed artifact's mana value to target creature. If
  excess damage would be dealt to that creature this way, instead that
  damage is dealt to that creature's controller and you **convert
  Megatron**." — a conversão acontece **no meio do combate**, antes do
  dano de combate.
- **Tyrant (frente, criatura 7/5)**: "At the beginning of each of your
  postcombat main phases, you may convert Megatron. If you do, add {C}
  for each 1 life your opponents have lost this turn."

Isso significa que, num único turno, o Megatron pode: atacar como
Destructive Force (4/5) → sacrificar combustível → causar dano/perda de
vida real → **converter pra Tyrant no meio do combate** → o dano de
combate desse MESMO ataque já sai como Tyrant (poder 7, não 4) → na main
phase pós-combate, converte de volta gerando mana incolor = toda vida que
os oponentes perderam no turno inteiro. Isso reconcilia a matemática do
próprio primer ("Megatron gets through, deals 7 damage" — não faria
sentido se ele estivesse preso como o Vehicle 4/5 o jogo inteiro).
Implementado em `megatron_combat()`/`megatron_postcombat()`, com a
escolha de combustível (`best_fuel_artifact()`) documentada: prioriza o
artefato de maior custo de mana entre as peças do "pacote de combustível"
(tag `fuel_*`) ou o toolbox de recursão, nunca sacrifica rocks/terrenos
de valor contínuo.

**Toolbox de recursão real** (achado durante a conversa de montagem,
confirmado pelo usuário como visto no oponente): Myr Retriever, Workshop
Assistant e Junk Diver têm o mesmo texto ("when this creature dies,
return another target artifact card from your graveyard to your hand"),
formando um loop real quando combinado com Goblin Engineer como sac
outlet repetível (`{R},{T},Sacrifice an artifact: Return target artifact
card with mana value 3 or less from your graveyard to the battlefield`).
Implementado em `toolbox_recur_death_trigger()` +
`try_goblin_engineer_activation()`.

**Achado real de autodano não documentado no primer:** Flame Rift (4 a
CADA jogador, incluindo eu), Damnable Pact (pago vida real pra comprar),
Descent into Avernus (dano simétrico crescente por contador — mas também
gera Treasures reais pra mim), e The One Ring (fardo de vida no upkeep)
são todos implementados com o autodano real aplicado, não só o benefício
— mesmo princípio já usado nesta sessão pro Nekusar (Spiteful
Visions/Phyrexian Tyranny).

**Achado real de efeito simétrico que também mata minhas próprias
criaturas:** Crystalline Entity ("if you cast it, destroy all nonartifact
creatures") destruiria Rakdos the Muscle, Treasure Nabber, Solemn
Simulacrum's... não, Solemn é artefato — mas Losheel/Stensian
Sanguinist/Mishra Tamer of Mak Fawa/Esper Sentinel (nenhuma delas tem o
tipo Artifact) morreriam junto. Implementado sem exceção pro meu lado.

**2 bugs reais corrigidos no smoke-test, antes da varredura de
robustez:**
1. `AttributeError: 'frozenset' object has no attribute 'pop'` — Dauntless
   Scrapbot tentava escolher terreno via `.pop()` num frozenset de cores.
   Corrigido pra usar `min()` com uma função de score sem mutar o set.
2. `ValueError: x not in list` no Goblin Engineer — a lista de artefatos
   elegíveis pra retornar do cemitério era calculada ANTES do sacrifício
   (que pode disparar o toolbox de recursão e remover uma carta do
   cemitério antes do Goblin Engineer conseguir usá-la). Corrigido:
   recalcula a lista depois do sacrifício e do gatilho do toolbox
   resolverem.
3. `KeyError` em qualquer checagem de `CARD_DB` pra token-cópias do Osgir/
   Nexus of Becoming (nome com sufixo " (copia)" nunca cadastrado no
   CARD_DB). Corrigido com `make_token_copy_name()`, que registra um
   alias no CARD_DB apontando pro `Card` real antes de pôr a cópia em
   campo.

**Teste de robustez:** 20.000 partidas com timeout de 3s via
`signal.alarm` (seeds 0–19999) — **0 erros, 0 timeouts**.

**n=3000, seed_base=9100000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0,99
Turno medio de conjuracao do Megatron: 4,67 | mediana: 4,0
Nunca conjurado em 8 turnos: 20,9%
Avg conversoes do Megatron (Tyrant<->Destructive Force): 2,59
Avg mana gerada pela conversao do Megatron: 14,99
Avg combustivel (artefatos) sacrificado pro Megatron: 1,30
Avg dano/perda-de-vida proxy total: 28,18
Avg vida ganha (drenagem): 0,44
Avg cartas compradas extra: 9,44
Avg wheels conjurados: 0,20
Avg tutores usados: 0,23
Avg eventos de recursao/valor: 0,50
Avg vida final: 38,29
Partidas com autodano fatal: 0,2%
Avg mao final: 4,38
```

**Leituras principais:**

- **Turno médio de conjuração 4,67, mediana 4** — bate com o plano real
  do primer (conjurar via More Than Meets the Eye por {1}{R}{W}{B} no
  turno 4). 20,9% nunca conjura em 8 turnos — esperado pra um custo que
  exige as 3 cores (R/W/B) simultaneamente sem rampa verde dedicada.
- **1,30 combustível sacrificado em média** é mais baixo do que o "1
  artefato de 3 mana por turno" que o primer descreve como ideal — reflete
  que, num goldfish real (mão aleatória, sem escolher a mão), nem sempre
  as peças de combustível certas são compradas a tempo. Ainda assim, 14,99
  de mana gerada pela conversão do Megatron confirma que o motor real
  funciona quando consegue rodar.
- **0,2% de autodano fatal** confirma que os efeitos simétricos (Flame
  Rift, Descent into Avernus, The One Ring) são um risco real mas raro
  dentro de 8 turnos — não um problema estrutural do deck.

Resultados salvos em `megatron_v1_runs.jsonl` (3000 jogos).

**Simplificações documentadas no docstring do script** (não inventadas —
omissões explícitas): sem oponente real, todo dano/vida é proxy agregado
(`NUM_OPPONENTS=3`); "opponents can't cast spells during combat" (Tyrant)
sem alvo real pra modelar; Annihilator 4 (Kozilek/Ulamog) não modelado
numericamente; remoção genérica sem alvo real conjurada só quando há mana
sobrando (convenção "interaction" já usada em todos os outros
simuladores desta sessão); Price of Progress usa minha própria contagem
de terrenos não-básicos como proxy da de oponentes; MDFCs com verso de
terreno (Shatterskull Smashing, Sundering Eruption) registradas só pela
face de feitiçaria.

---

## Partida #1 — AAAA-MM-DD

- **Formato do teste:**
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:**
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

### Leitura linha-a-linha completa do oráculo (mesma exigência do Toph/Beorn/Edgar Markov/Hei Bai/Maralen) — 2026-09-01

**Gatilho (usuário):** *"AGORA FAZ O QUE SEMPRE Te MANDei FAZER: COmpila
a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada carta tem que ser
lida linha a linha"*.

Diferente dos outros decks (todos já tinham 1+ rodada de correção
anterior), Megatron foi construído do zero em 2026-08-29 sem nenhuma
reanálise prévia — a releitura linha-a-linha achou **6 tags mortas**
(definidas, nunca lidas em lugar nenhum do dispatch): Scion of Draco
(`domain_reduce`), Summon: Bahamut (`saga_bahamut`), Cryptolith Fragment
(`fuel_mana_drain`), Cityscape Leveler (`cast_removal_attack_removal`),
Retributive Wand (`fuel_ping_death_burst`), Pumpkin Bombs
(`fuel_fuse_burn`). Todas lacunas puras, sem nenhuma documentação
explicando a ausência — diferente do padrão dos outros decks desta
sessão, onde os gaps eram deferidos com justificativa (às vezes válida,
às vezes julgamento de valor proibido).

**Destaque:** Summon: Bahamut é um finisher de dano REAL (Mega Flare =
MV total de outros permanentes controlados) que estava inteiramente
ausente — uma Saga de {9} mana virando efetivamente um vanilla sem
nenhum dos 4 capítulos.

Implementado: novo `effective_cost()` (Scion of Draco, domínio real
deste deck sem Forest/Island é máximo 3, não 5); `try_bahamut_saga()`
(capítulos II/III/IV, chamada no upkeep); `try_cryptolith_fragment()` +
`try_aurora_of_emrakul_attack()` (mana real + transform aproximado via
`40 - proxy_damage_total`); `try_cityscape_leveler_attack()`; 
`try_retributive_wand_ping()`; `try_pumpkin_bombs()` (ativação única
real — o oráculo tira o artefato do seu controle após o 1º uso, não é
julgamento de valor meu).

**Robustez:** 6 testes unitários isolados + 20.000 partidas de regressão
(0 erros).

**Batch, n=3000, seed_base=1400000 (antes = git HEAD, depois = com os 6 fixes):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg proxy_damage_total | 29,10 | 30,33 |
| Avg cartas compradas extra | 9,51 | 9,84 |
| Avg interaction_spells_cast_total | 0,00 | 0,03 |
| Scion of Draco conjurado | 0% (custo fixo {12}) | 2,2% dos jogos |

**Leitura:** tudo sobe, na direção esperada. `interaction_spells_cast_total`
saindo de 0,00 fixo pra um valor real é o sinal mais claro — antes
Cityscape Leveler e Summon: Bahamut (capítulos I/II) nunca contribuíam
NADA pra essa métrica, apesar de serem cartas de interação reais na
lista. Bahamut chega ao Mega Flare (dano real ~63-133) em partidas mais
longas (14 turnos: 3,2% dos jogos) — dentro de 8 turnos raramente há
tempo pra uma Saga de {9} completar 4 capítulos, o que é esperado e
correto, não um bug.

`checklist-oraculo.md` criado (93 cartas).

---

<!-- Copie o bloco acima para cada nova partida -->
