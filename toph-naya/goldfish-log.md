# Goldfish Log — Toph (Naya)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Simulação #1 — goldfish Python completo (`toph_goldfish_v1.py`) — 2026-08-22

**Script construído do zero**, cobrindo as **16 mecânicas/motores documentados na seção 4 da `auditoria.md`**, não só 1 ou 2 (pedido explícito do usuário). Passo 0 (regra de `references/goldfish-sim-card-rules.md`, aplicada de forma mais ampla que só Roaming Throne — esse deck não tem Roaming Throne, mas o princípio de "varredura mecânica antes de codar" vale igual): regex em todo o oráculo achou **43 cartas com gatilho real** ("Whenever"/"At the beginning of"/"When"). Todas as 43 foram checadas contra a lógica implementada; 34 têm efeito real em código, 9 são genuinamente dependentes de oponente/combate (Esper Sentinel, Skullclamp, Sword of Feast and Famine, Talon Gates of Madara, Krang, Haywire Mite como remoção, Council's Judgment, Lightning Greaves, Heroic Intervention) e foram documentadas como tal em vez de fingir um efeito numérico solo.

**Arquitetura:** `Card`/`Permanent`/`GameState` dataclasses. O núcleo é tratar earthbend + "artefato/criatura vira terreno" (Toph e Ashaya) como **um sistema só**, não dois separados — `is_land()` é dinâmico (depende de `commander_in_play`/`ashaya_in_play`/`mycosynth_in_play`), e `leave_battlefield()` é o ponto central onde o **Motor #16** (earthbend torna recorrente qualquer artefato-terreno com gatilho/custo de morte) e o Ozolith (recicla contadores) vivem.

**Bugs reais encontrados e corrigidos durante o build (documentados, não escondidos):**
1. **A própria comandante nunca era conjurada** — `build_library()` só lê a seção "Lista completa" do `lista.md` (99 cartas), a Toph fica na "zona de comando" à parte e a lógica de casting só olhava `state.hand`. Resultado: em 8 turnos de teste inicial, earthbend do end step nunca disparava porque `commander_in_play` ficava `False` o jogo inteiro. Corrigido com `can_cast_commander()`/tax de `+2` por recast, sempre tentada primeiro no `main_phase`.
2. **Loop infinito por mutar `state.battlefield` durante a iteração** — o clone da Scute Swarm era anexado à própria lista que o `landfall_trigger` estava percorrendo com `for p in state.battlefield`, fazendo o loop visitar os clones novos indefinidamente. Corrigido iterando sobre `list(state.battlefield)` (snapshot).
3. **`ValueError` em sacrifícios em lote** — Planar Engineering sacrifica 2 terrenos de uma lista pré-computada; se processar o primeiro disparava uma cadeia de landfall que fazia um bounce land (Gruul Turf/Selesnya Sanctuary) devolver o segundo terreno da lista pra mão antes dele ser processado. Corrigido com uma checagem defensiva em `leave_battlefield()`.
4. **`RecursionError` — Ultron copiando token indefinidamente** — o token criado pela cópia do Ultron reentrava em `enter_battlefield()` e disparava o próprio gatilho do Ultron de novo (a checagem não excluía tokens, e a regra real é "outro artefato **não-token**"). Corrigido com a flag `is_token` no `Permanent`, que também corrige `is_land()` pra não deixar token virar terreno via Toph/Ashaya (a regra real também é "não-token" ali).
5. **`RecursionError` — auto-recursão dentro de `create_token()`** — um `replace_all` de refatoração (trocar `state.tokens_created += 1` espalhado por `create_token(state, log)`) acabou reescrevendo a própria linha *dentro* da definição de `create_token`, fazendo a função chamar a si mesma. Corrigido revertendo essa linha específica pra incremento direto.

Todos os 5 bugs foram achados rodando **20.000 partidas com timeout de 2s por partida via `signal.alarm`** antes do batch oficial — zero erros/travamentos nas 20.000 depois da correção do 5º bug.

**n=2000, seed_base=9000000, 8 turnos:**

```
Avg mulligans: 0,77
Turno medio de conjuracao da Toph: 2,61 | mediana: 2
Nunca conjurada em 8 turnos: 3,6%
Avg terrenos em campo (turno 8, contando artefato/criatura-terreno): 10,22
Avg aplicacoes de earthbend: 7,92
Avg recorrencias via Motor#16: 0,20 | % de jogos com pelo menos 1: 11,1%
Avg gatilhos de landfall disparados: 9,55
Avg tokens de Field of the Dead: 3,90 | % de jogos que ligou: 84,6%
Avg cartas compradas extra (motores de draw): 1,43
Avg mana extra gerado (Lotus Cobra/Nissa por landfall): 1,15
Avg cheats do Kodama of the East Tree: 0,01
Avg copias via Strionic Resonator: 0,50
Avg dobras via Bristly Bill (ativada): 0,23
Avg realocacoes de contador via The Ozolith: 0,03
Avg tokens totais criados: 9,52
% de jogos com Ashaya em campo: 10,3%
Avg vida ganha (Inventors' Fair/Haywire Mite/Sylvan Library liquido): 0,23

Earthbend por fonte (soma das 2000 partidas):
  Toph, the First Metalbender (end step): 12317 (6,16/jogo)
  Ba Sing Se (ativada): 998 (0,50/jogo)
  Toph Earthbending Master (ataque, X=experiencia): 464 (0,23/jogo)
  Badgermole Cub (ETB): 291 (0,15/jogo)
  Avatar Kyoshi (combate): 290 (0,14/jogo)
  Earthbending Student (ETB): 271 (0,14/jogo)
  Earth Kingdom General (ETB): 262 (0,13/jogo)
  Earthbender Ascension (ETB): 253 (0,13/jogo)
  Earthshape (instant): 249 (0,12/jogo)
  Toph Greatest Earthbender (ETB, X=mana gasto): 225 (0,11/jogo)
  Bumi (ETB): 211 (0,11/jogo)
```

**Achados reais que a auditoria qualitativa não tinha número pra sustentar:**

- **Field of the Dead liga em 84,6% dos jogos até o turno 8** — confirma com dado real a hipótese da seção 3/4 da auditoria (artefato virando terreno via Toph conta como nome distinto pra contagem de "7+ terrenos com nomes diferentes"). É um dos motores mais consistentes do deck, não um "às vezes".
- **Motor #16 (earthbend torna artefato-morte recorrente) ativa em 11,1% dos jogos** — real, mas depende de uma combinação específica (earthbendar um Stasis Coffin/Ichor Wellspring/Unstable Obelisk especificamente, e depois ele efetivamente morrer/ser sacrificado) — não é algo que acontece toda partida, mas quando acontece é uma virada de valor real.
- **Scute Swarm é genuinamente explosivo quando resolve com 6+ terrenos em campo** — precisei implementar um **cap defensivo de 200 permanentes em campo** pra simulação não travar (a regra real do card é copiar a si mesma a cada landfall subsequente, inclusive as cópias copiando de novo — crescimento geométrico real, não um bug da minha implementação). Scute Swarm chegou em campo em ~14% das 1000 partidas de uma amostra separada; nessas partidas o cap foi atingido em média **~32 vezes por jogo** (8875 atingidos em só 2000 partidas totais, a maioria concentrada nas ~14% que tinham a carta). Isso é uma leitura real sobre o card, não um artefato de simulação — em mesa, Scute Swarm com Toph em campo (mais terrenos-artefato entrando) tende a sair de controle rápido uma vez montado.
- **Kodama of the East Tree quase nunca encontra o próprio gatilho (0,01/jogo)** — não é bug (conferido manualmente): ele só entra em ~9,6% dos jogos (6 mana, cópia única em 99 cartas) e, quando entra, a política gananciosa do simulador (conjura tudo que dá pra pagar, mais barato primeiro) já costuma ter esvaziado a mão de cartas baratas o bastante pra ele aproveitar. Achado honesto de baixo valor prático dentro do perfil de jogo modelado.
- **Comandante conjurada em média no turno 2,61** (mediana 2) e só 3,6% dos jogos nunca resolvem ela em 8 turnos — a curva de 3 mana da Toph é rápida de bater mesmo sem ramp dedicado a ela especificamente.

**Simplificações documentadas no docstring do script** (não inventadas, omissões explícitas): sem combate real contra oponente (nenhuma criatura adversária, nenhum bloqueio — "atacar" só dispara gatilhos de ataque, não há dano/vida de oponente real); Esper Sentinel/Skullclamp/Sword of Feast and Famine/Talon Gates/Krang/Council's Judgment/Lightning Greaves/Heroic Intervention não têm efeito numérico solo simulado (dependem de oponente real); modelo de mana genérico (mana total, não pip a pip — o deck tem fixing extenso e documentado); habilidades de lealdade do Wrenn and Realmbreaker além da estática de fixing não são ativadas automaticamente.

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
