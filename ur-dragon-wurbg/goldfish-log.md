# Goldfish Log — The Ur-Dragon

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Simulação #1 — goldfish Python completo (`urdragon_goldfish_v1.py`) — 2026-08-23

**Script construído do zero.** A `auditoria.md` deste deck era curta (sem uma seção de motores detalhada como Toph/Vihaan/Maralen/Nekusar), então a varredura mecânica completa (Passo 0, regex "Whenever"/"At the beginning of"/"When ... enters" em todo `oracle_text`) foi feita aqui pela primeira vez, achando um motor de dano-por-Dragão-em-campo genuinamente rico (Scourge of Valkas, Dragon Tempest), geração de token via cópia (Miirym) e via ataque (Lathliss, Utvara Hellkite), e mana no ataque (Klauth, Savage Ventmaw).

**Roaming Throne — tipo escolhido: Dragon.** Óbvio e central pro tema, documentado mesmo assim. Dobra qualquer gatilho de criatura Dragão, incluindo o próprio gatilho de ataque da Ur-Dragon (ela mesma é um Dragão).

**Motor central implementado com fidelidade real:** o gatilho de ataque da comandante (`Whenever one or more Dragons you control attack, draw that many cards, then you may put a permanent card from your hand onto the battlefield`) + a redução de custo empilhável de Dragões (Eminence da própria comandante, Dragonlord's Servant, Dragonspeaker Shaman, Sarkhan Soul Aflame, Herald's Horn, Urza's Incubator — todas somadas em `dragon_discount()`).

**Motor de dano escalável (Scourge of Valkas/Dragon Tempest) implementado como dispatch central**, não decorativo: `dragon_enters()` é chamado toda vez que UM Dragão entra (nomeado ou token), calcula X = número de Dragões que você controla NAQUELE momento (incluindo o que acabou de entrar), e dispara o dano proxy. Como Miirym e Lathliss criam mais Dragões ao ETB, isso realimenta a si mesmo — mas sem risco de loop infinito, porque as duas cartas reais exigem "another NONTOKEN Dragon", e a função corretamente não re-dispara Miirym/Lathliss para os tokens que elas mesmas criam (regra real das cartas, não um teto artificial que eu precisei inventar).

**Bug real encontrado e corrigido no smoke-test** (mesmo padrão já visto nos outros 7 simuladores desta biblioteca): `cast_card()` tentava `state.hand.remove(COMMANDER)` incondicionalmente, mas ela vem da zona de comando, não da mão.

**Teste de robustez:** 20.000 partidas com timeout de 2s via `signal.alarm`, **0 erros, 0 timeouts**.

**Achado real, não um bug — verificado antes de aceitar o número:** a taxa de "comandante nunca conjurada em 8 turnos" saiu muito mais alta que nos outros decks já simulados (71,5%, contra 1,8% no Vihaan, 3,6% no Toph, ~5% na Maralen, 12,8% no Nekusar). Investiguei antes de aceitar como resultado válido: rodei uma amostra separada medindo `total_mana()` no turno 8 — deu **9,72 de mana média**, praticamente empatado com o custo de `{4}{W}{U}{B}{R}{G}` = 9 da comandante. Isso não é bug de implementação (o modelo de mana deste script é genérico/total, nem sequer verifica cor — na vida real, com 5 cores pip a pip, seria ainda mais difícil) — é um dado real sobre a lista: **10 peças de rampa dedicadas (Cultivate, Kodama's Reach, Farseek, Nature's Lore, Three Visits, Skyshroud Claim, Birds of Paradise, Delighted Halfling, Arcane Signet, Sol Ring) em 99 cartas é uma densidade modesta pra sustentar um comandante de 9 mana.**

**n=3000, seed_base=7600000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0,48
Turno medio de conjuracao da Ur-Dragon: 7,07 | mediana: 7,0
Nunca conjurada em 8 turnos: 71,5%
Avg contagem de Dragoes em campo (fim de jogo): 3,16
Avg compras via ataque da Ur-Dragon: 1,28
Avg permanentes gratis via ataque da Ur-Dragon: 0,42
Avg dano proxy total (Scourge of Valkas/Dragon Tempest/Terror of the Peaks): 10,44
Avg eventos de dano-por-Dragao-ETB: 0,94
Avg Treasures criados: 2,03
Avg dobras via Roaming Throne: 0,23
Avg cartas compradas extra (motores de draw): 2,43
Avg tutores usados: 0,32
Avg mao final: 2,56
```

**Leituras principais:**

- **A comandante em si é o gargalo mais claro que esta biblioteca já mediu.** Quando resolve, é bem tarde (T7,07 médio) e ainda assim quase 3 em cada 4 partidas nunca chegam lá em 8 turnos. Isso não invalida o deck — Dragões individuais continuam entrando e gerando valor (3,16 Dragões em campo no fim, mesmo sem a comandante), mas o motor de ataque específico da Ur-Dragon (draw + permanente grátis) só aparece em minoria clara das partidas.
- **O motor de dano-por-ETB (Scourge of Valkas/Dragon Tempest) é discreto em volume médio (0,94 eventos/partida)** porque cada peça é 1 carta em 99 — mas quando alguma delas resolve junto com vários Dragões já em campo, o dano escala rápido (dado real: dano proxy médio de 10,44 mesmo com só ~1 evento/partida em média, mostra que os eventos individuais tendem a ser grandes quando acontecem).
- **Treasures/mana no ataque (Klauth, Savage Ventmaw, Goldspan Dragon, Ancient Copper Dragon, Old Gnawbone) também ficam abaixo do potencial** pela mesma razão — dependem de Dragões específicos resolverem E atacarem, e com a curva pesada deste deck isso raramente acontece cedo.

Resultados salvos em `urdragon_v1_runs.jsonl` (3000 jogos).

**Simplificações documentadas no docstring do script** (não inventadas — omissões explícitas): fetchlands tratadas como terreno genérico (thinning não modelado); Klauth/Savage Ventmaw aproximam poder-dos-atacantes pelo poder do próprio Dragão atacante (não soma o time inteiro); Ramos, Dragon Engine ganha +1 contador fixo por spell (não por número exato de cores); Sylvan Library sempre escolhe não pagar vida (puro card selection, sem draw líquido extra — decisão conservadora); sem combate real contra oponente, sem contramágica/remoção com efeito de combate real modelado (mesma convenção dos outros simuladores desta biblioteca).

---

## Correção #1 — dois bugs reais encontrados por pergunta do usuário — 2026-08-23

O usuário perguntou se eu tinha ignorado, além de rampa e mana dorks, os
redutores de custo de Dragão. Fui conferir com uma varredura real (regex em
`oracle_text` de "costs... less to cast" nas 99 cartas): **os 6 redutores de
Dragão de verdade estavam todos implementados** em `dragon_discount()`
(Eminence da Ur-Dragon, Dragonlord's Servant, Dragonspeaker Shaman, Sarkhan
Soul Aflame, Herald's Horn, Urza's Incubator) — nenhum ficou de fora.

Mas a checagem revelou **dois bugs reais e distintos** no mesmo script: tags
criadas no `CARD_DB` cujo efeito nunca tinha sido de fato ligado no código
(violação da Regra 3 — tag decorativa em vez de implementação real):

1. **Orb of Dragonkind** — só a 2ª habilidade (sacrifício-tutor: olhar 7,
   revelar Dragão, pôr na mão) estava implementada. A 1ª habilidade, `{1},
   {T}: Add two mana in any combination of colors. Spend this mana only to
   cast Dragon spells or activate abilities of Dragons`, nunca tinha sido
   modelada — rampa repetível restrita a Dragão, exatamente a categoria que
   o usuário perguntou. Corrigido com um pool de mana restrito
   (`dragon_mana_pool`) que só pode ser gasto em cartas de Dragão, e uma
   função `do_orb_dragonkind()` que escolhe entre as duas habilidades
   (prioriza a mana se há Dragão na mão pra aproveitar; só sacrifica pelo
   tutor se não há Dragão nenhum na mão) — as duas são mutuamente
   exclusivas no mesmo turno porque a segunda destrói o artefato.
2. **Goldspan Dragon** — a tag `goldspan` existia no `CARD_DB` mas nunca era
   checada em lugar nenhum. Texto real: `Treasures you control have "{T},
   Sacrifice this artifact: Add two mana of any one color."` — com Goldspan
   em campo, todo Treasure do deck (Ancient Copper Dragon, Old Gnawbone, o
   próprio Goldspan atacando) vale 2 mana, não 1. `create_and_use_treasures()`
   sempre convertia 1-pra-1. Corrigido: dobra a mana por Treasure quando
   Goldspan Dragon está em campo.

**Reteste de robustez:** 20.000 partidas com timeout de 2s, **0 erros, 0
timeouts** — as duas correções não introduziram bug novo.

**n=3000, seed_base=7600000, 8 turnos — resultado oficial após a correção:**

```
Avg mulligans: 0,48
Turno medio de conjuracao da Ur-Dragon: 7,07 | mediana: 7,0
Nunca conjurada em 8 turnos: 70,6%
Avg contagem de Dragoes em campo (fim de jogo): 3,31
Avg compras via ataque da Ur-Dragon: 1,36
Avg permanentes gratis via ataque da Ur-Dragon: 0,43
Avg dano proxy total (Scourge of Valkas/Dragon Tempest/Terror of the Peaks): 11,67
Avg eventos de dano-por-Dragao-ETB: 1,00
Avg Treasures criados: 2,12
Avg dobras via Roaming Throne: 0,26
Avg cartas compradas extra (motores de draw): 2,72
Avg tutores usados: 0,23
Avg ativacoes da habilidade de mana da Orb of Dragonkind: 0,45
Avg mao final: 2,48
```

**Leitura honesta do impacto:** pequeno, não estrutural. "Nunca conjurada em
8 turnos" caiu de 71,5% pra 70,6% — quase nada, porque tanto a Orb quanto o
Goldspan são 1 cópia cada em 99 cartas (0,45 ativações médias da mana da Orb
por partida; o Goldspan multiplica o VALOR do Treasure, não a contagem, então
"Treasures criados" nem devia mudar muito e não mudou: 2,03→2,12). O achado
do turno 7,07/71,5% do registro anterior continua válido e não muda de
natureza — a comandante de 9 mana continua sendo o gargalo real do deck,
essas duas peças ajudam, mas são pequenas demais pra resolver isso sozinhas.
Vale como confirmação adicional (não contradição) do achado já registrado
acima sobre a densidade modesta de rampa do deck.

Resultados atualizados em `urdragon_v1_runs.jsonl` (3000 jogos, sobrescrito).

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
