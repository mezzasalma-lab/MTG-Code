# Goldfish Log — Hei-Bai, Forest Guardian

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Simulação #1 — goldfish Python completo (`heibai_goldfish_v1.py`) — 2026-08-24

**Script construído do zero.** A `auditoria.md` já tinha uma boa categorização
das 17 Shrines, mas não um catálogo carta-a-carta de todo gatilho real —
varredura mecânica completa feita aqui pela primeira vez (94 cartas
únicas, ver `/tmp/heibai_full.txt` gerado durante o processo).

**Motor central implementado com fidelidade real:** cada Shrine tem, em
geral, DOIS gatilhos distintos — um "when THIS Shrine enters" (X = Shrines
controladas naquele momento) e um "whenever ANOTHER Shrine you control
enters" (efeito fixo de 1 unidade, disparado por toda Shrine já em campo).
Implementado via `shrine_enters()`, dispatch central chamado toda vez que
QUALQUER Shrine entra — nomeada, token (inclusive os tokens-Shrine
criados por Go-Shintai of Life's Origin), ou **reentrada via blink**.

**Três dobradores de gatilho distintos, implementados sem confundir um
com o outro** (a diferença real importa e muda o resultado):
- **Elesh Norn** — incondicional, cobre QUALQUER gatilho causado por algo
  entrando (Shrine ETB, reação de outra Shrine, e também o gatilho da
  Purphoros — que dispara quando OUTRA criatura entra, também "causado
  por permanente entrando").
- **Sanctum of All** — condicional (6+ Shrines), escopado só a "outra
  Shrine" (não pega Purphoros), mas cobre tanto ETB quanto as habilidades
  pagas de end step dos Go-Shintai (que também são "triggered ability of
  another Shrine").
- **Annie Joins Up** — nem ETB nem Shrine, é sobre a fonte ser uma
  criatura LENDÁRIA: cobre o ETB da própria Hei Bai, os 5 Go-Shintai, e o
  gatilho de conjuração da Sythis (que é `Legendary Enchantment Creature`,
  ao contrário de Argothian Enchantress/Enchantress's Presence — essas
  duas nunca são dobradas por nada neste deck).

As três empilham de forma independente quando aplicáveis simultaneamente,
via `resolve_times()` — testado manualmente com Elesh Norn + Sanctum of
All + 6 Shrines: um "when this enters" de Shrine dispara 3 vezes.

**Motor de blink implementado com efeito real** (não decorativo): repiscar
uma Shrine já em campo dispara o "when THIS enters" dela de novo — uma
entrada nova de verdade, não a reação "another Shrine enters". Deadeye
Navigator (soulbond + `{1}{U}` repetível), Ephemerate (com rebound = 2
usos reais), Thassa/Teleportation Circle/Mind Stone harnessed (end step),
Waterbender's Restoration — todos escolhem greedy a Shrine de maior valor
disponível (`best_shrine_to_reblink()`).

**Bug real encontrado e corrigido no smoke-test:** a primeira versão do
ETB da própria Hei Bai ("reveal until Shrine... **then shuffle**") mandava
as cartas reveladas que não eram Shrine pro cemitério — mas o oráculo real
diz "then shuffle", não "then discard"/"then mill". Corrigido pra devolver
essas cartas à biblioteca (sem RNG real de reembaralhar, mesma convenção
já usada nesta biblioteca pra qualquer "search... then shuffle" —
devolvidas deterministicamente, documentado). O bug também tinha uma
condição de loop frágil (`reveal_count < len(state.library)` comparando
contra um comprimento que encolhia a cada iteração), reescrita como um
`while state.library:` limpo.

**Teste de robustez:** 2 sweeps de 20.000 partidas com timeout de 2s via
`signal.alarm`, **0 erros, 0 timeouts** nos dois.

**n=3000, seed_base=9100000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0,58
Turno medio de conjuracao da Hei Bai: 3,79 | mediana: 4,0
Nunca conjurada em 8 turnos: 3,0%
Avg contagem de Shrines em campo (fim de jogo): 4,54
Avg cartas compradas extra: 8,90
Avg drain proxy total: 8,78
Avg dano proxy total (Purphoros/Go-Shintai Ancient Wars): 9,67
Avg tokens criados: 7,67
Avg dobras via Elesh Norn: 1,45
Avg dobras via Sanctum of All (6+ Shrines): 2,63
Avg dobras via Annie Joins Up: 0,34
Avg blinks totais: 1,06 | dos quais em Shrine: 0,79
Avg tutores usados: 0,85
Avg vida ganha proxy: 1,97
Avg spells de interacao conjurados (proxy): 2,53
Avg mao final: 3,17
```

Resultados salvos em `heibai_v1_runs.jsonl` (3000 jogos).

**Leituras principais:**

- **A comandante em si é a mais confiável desta biblioteca até agora**
  (turno médio 3,79, só 3,0% nunca conjurada em 8 turnos) — CMC 4 baixo +
  14 peças de rampa + o próprio ETB da Hei Bai não depende de ter mana
  sobrando pra funcionar, é parte do próprio cast.
- **O achado da auditoria ("motor de draw mais forte desta biblioteca")
  se confirma numericamente**: 8,90 cartas extra em média — mais que o
  dobro do próximo melhor motor de draw já medido nesta biblioteca
  (Nekusar, com wheels dedicados).
- **Os dois dobradores de Shrine (Elesh Norn + Sanctum of All) realmente
  compõem**: 1,45 + 2,63 = mais de 4 eventos de dobra por partida em
  média, confirmando que o achado da auditoria (Sanctum of All como
  multiplicador extra, corrigido em 24/08) não era só teórico — acontece
  de verdade em boa parte das partidas.
- **O motor de blink entrega valor real mas modesto** (0,79 reentradas de
  Shrine em média) — a maioria das fontes de blink (Thassa, Teleportation
  Circle, Mind Stone) só ativa 1x por turno no end step e compete entre si
  pelo mesmo alvo prioritário, então o ganho não escala tão rápido quanto
  o motor de Shrine-ETB em si.

**Simplificações documentadas no docstring do script** (não inventadas —
omissões explícitas): modelo de mana genérico/total; devoção a
vermelho/azul (Purphoros/Thassa) não rastreada (nenhuma das duas depende
disso pra sua habilidade disparada/ativada funcionar); Skybind implementado
com valor modesto (nenhuma criatura não-Shrine deste deck tem ETB de peso
pra repiscar com ele); Weaver of Harmony só o buff estático (a habilidade
de copiar gatilho/ativada de fonte de encantamento não é modelada,
genérica demais pra um efeito determinístico); Destiny Spinner só o
"can't be countered"; Sanctum Weaver e Bloom Tender com mana aproximada
(não pip-a-pip); removal/contramágica proxy sem alvo real, mesma convenção
dos outros 9 simuladores desta biblioteca.

---

## Partida #1 — AAAA-MM-DD

- **Formato do teste:** goldfish / playtest com amigos / mesa competitiva
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:** vitória / derrota / sem resolução
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

## Partida #2 — AAAA-MM-DD

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
