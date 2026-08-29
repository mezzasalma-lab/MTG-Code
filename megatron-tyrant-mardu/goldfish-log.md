# Goldfish Log — Megatron, Tyrant

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

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

<!-- Copie o bloco acima para cada nova partida -->
