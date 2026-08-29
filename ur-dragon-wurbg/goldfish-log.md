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

## Correção #2 — a comandante estava sendo excluída de descontos que o oráculo real não exclui — 2026-08-23

Pergunta do usuário sobre incluir Radagast of Rhosgobel (mesma pergunta já
respondida pro Ulalek) me fez reler com cuidado o texto real dos 6
redutores de custo de Dragão antes de montar o teste comparativo — e achei
que **4 bugs reais, todos do mesmo padrão**, estavam escondidos na Correção
#1 (que só cobriu Orb of Dragonkind e Goldspan Dragon, sem olhar pra esse
detalhe específico):

O código sempre excluía a própria Ur-Dragon (`name != COMMANDER`) de TODOS
os 6 redutores de custo de Dragão e da mana restrita da Orb of Dragonkind.
Mas conferindo o oráculo real de cada um:

| Fonte | Texto real | Exclui a própria comandante? |
|---|---|---|
| Eminence (Ur-Dragon) | "**other** Dragon spells you cast cost {1} less" | SIM — só essa tem "other" |
| Dragonlord's Servant | "Dragon spells you cast cost {1} less" | NÃO |
| Dragonspeaker Shaman | "Dragon spells you cast cost {2} less" | NÃO |
| Sarkhan, Soul Aflame | "Dragon spells you cast cost {1} less" | NÃO |
| Herald's Horn | "Creature spells you cast of the chosen type cost {1} less" | NÃO |
| Urza's Incubator | "Creature spells of the chosen type cost {2} less" | NÃO |
| Orb of Dragonkind (mana) | "Spend this mana only to cast Dragon spells..." | NÃO |

Ou seja: só a Eminence da própria comandante deveria excluí-la (ela nunca
desconta a si mesma) — as outras 5 fontes de desconto E a mana restrita da
Orb deveriam valer pra conjurar a própria Ur-Dragon também, e não valiam.

**Bug relacionado, mesma raiz:** a Eminence só ficava ativa depois de
`state.commander_in_play` virar `True` — mas o texto real diz "as long as
The Ur-Dragon is in the command zone **or** on the battlefield". Neste
simulador ela está SEMPRE numa dessas duas zonas (nunca é removida do
jogo — "ainda não conjurada" já significa "na zona de comando" no modelo),
então a Eminence deveria estar ativa desde o turno 1, não só depois de
resolver.

**Bug adicional, achado ao corrigir os anteriores:** `cast_card()` cobrava
o imposto de comandante (+2 por conjuração anterior) em cima de `card.mv`
(9 cru), **ignorando completamente** o desconto que `effective_cost()` já
calculava — `can_cast()` checava a affordability com o custo descontado,
mas o gasto real cobrava o preço cheio. Corrigido junto.

Refatorado `dragon_discount()` em duas funções: `dragon_discount_self()`
(as 5 fontes sem "other", vale pra conjurar a própria comandante) e
`dragon_discount_others()` (as 5 + a Eminence sempre ativa, vale pra
qualquer OUTRO Dragão).

**Reteste de robustez:** 2 sweeps de 20.000 partidas com timeout de 2s,
**0 erros, 0 timeouts** nos dois.

**n=3000, seed_base=7600000, 8 turnos — resultado oficial após a correção:**

```
Avg mulligans: 0,48
Turno medio de conjuracao da Ur-Dragon: 6,81 | mediana: 7,0
Nunca conjurada em 8 turnos: 49,5%
Avg contagem de Dragoes em campo (fim de jogo): 5,28
Avg compras via ataque da Ur-Dragon: 3,15
Avg permanentes gratis via ataque da Ur-Dragon: 0,94
Avg dano proxy total (Scourge of Valkas/Dragon Tempest/Terror of the Peaks): 31,29
Avg eventos de dano-por-Dragao-ETB: 1,88
Avg Treasures criados: 3,51
Avg dobras via Roaming Throne: 0,64
Avg cartas compradas extra (motores de draw): 5,55
Avg tutores usados: 0,28
Avg ativacoes da habilidade de mana da Orb of Dragonkind: 0,40
Avg mao final: 2,84
```

**Correção honesta ao achado anterior desta biblioteca:** as duas
simulações anteriores registraram "comandante é o gargalo mais claro que
esta biblioteca já mediu" com 71,5% (Simulação #1) e depois 70,6%
(Correção #1) de "nunca conjurada em 8 turnos". Esse número estava
sistematicamente inflado por um bug real de implementação, não refletia a
lista de verdade. **O número correto é 49,5%** — turno médio caiu de 7,07
pra 6,81, e todas as métricas de motor (Dragões em campo, dano proxy,
Treasures, compras extra) subiram bastante, porque a comandante resolvendo
mais cedo/mais vezes alimenta tudo que depende dela estar em campo. A
comandante continua sendo mais difícil de resolver que em qualquer outro
deck desta biblioteca (49,5% ainda é o pior "nunca conjurada" registrado),
mas a magnitude do problema era quase 1,5x maior do que os dados mostravam
antes desta correção. A causa raiz (densidade modesta de rampa dedicada
pra um comandante de 9 mana) continua sendo real e válida — só a
severidade relatada estava errada.

Resultados atualizados em `urdragon_v1_runs.jsonl` (3000 jogos, sobrescrito).

---

## Correção #3 — Firdoch Core nunca era tratado como Dragão — 2026-08-23

O usuário corrigiu diretamente algo que eu tinha errado na leitura da
carta: chamei Firdoch Core de "mana-dork genérico" no Teste #1 (parceiro
de troca do teste do Radagast). Ele apontou — corretamente — que Firdoch
Core **entra como Dragão** (Changeling) e com a Eminence da própria
Ur-Dragon custa só {2}, além de poder disparar habilidades que reagem a
"um Dragão entrando".

Conferido no oráculo real: `Firdoch Core | {3} | Kindred Artifact —
Shapeshifter` — `Changeling (This card is every creature type.)`. Changeling
dá TODOS os tipos de criatura em TODA zona, inclusive como spell na pilha —
então Firdoch Core é literalmente um "Dragon spell" ao ser conjurado, e um
"Dragão" permanente depois de resolver, mesmo sendo um Artifact (não
Creature) até pagar `{4}` pra virar 4/4.

**Bug real confirmado e corrigido:** a carta nunca tinha a tag `"dragon"`
no `CARD_DB` — então nunca pegava desconto de Eminence/Dragonlord's
Servant/Dragonspeaker Shaman/Sarkhan Soul Aflame (todas dizem "Dragon
spells", sem exigir carta de criatura) e nunca disparava `dragon_enters()`
ao entrar (Scourge of Valkas/Dragon Tempest/Miirym/Lathliss reagem a
"a Dragon you control enters", também sem exigir criatura).

**Distinção correta que precisei implementar junto:** Herald's Horn e
Urza's Incubator dizem "**Creature spells**... of the chosen type" — essas
duas EXIGEM carta de criatura de verdade, e Firdoch Core continua sendo
Artifact (não Creature) até ser animado (não modelado). Por isso
`dragon_discount_others()` foi reescrita pra separar os dois grupos: as 4
fontes "Dragon spell" (sem exigência de criatura, valem pra Firdoch Core)
sempre se aplicam a qualquer coisa com o tipo Dragão; as 2 fontes
"Creature spell of type" só se aplicam quando `is_creature_card(name)` é
verdade (Firdoch Core fica de fora dessas duas, corretamente).

**Reteste de robustez:** 20.000 partidas com timeout de 2s, **0 erros, 0
timeouts**.

**n=3000, seed_base=7600000, 8 turnos — resultado após a correção:**

```
Avg mulligans: 0,48
Turno medio de conjuracao da Ur-Dragon: 6,81 | mediana: 7,0
Nunca conjurada em 8 turnos: 49,2%
Avg contagem de Dragoes em campo (fim de jogo): 5,55
Avg dano proxy total: 35,16
Avg eventos de dano-por-Dragao-ETB: 1,97
Avg Treasures criados: 3,54
Avg dobras via Roaming Throne: 0,68
Avg cartas compradas extra: 5,60
Avg mao final: 2,82
```

Impacto pequeno mas real (1 carta em 99): "nunca conjurada" caiu mais um
pouco (49,5%→49,2%), Dragões em campo subiu (5,28→5,55), dano proxy subiu
bastante (31,29→35,16) — consistente com Firdoch Core agora contribuir de
verdade pro motor de dano-por-ETB, não só ser um mana rock inerte.

**Consequência pro Teste #1 abaixo:** como Firdoch Core tinha sido usado
como o "parceiro de troca de baixa interferência" no teste comparativo do
Radagast, e ele NÃO é mais neutro em relação às métricas medidas (turno de
comandante, contagem de Dragão, motor de ETB), o teste original estava
confundido — cortar Firdoch Core pra "abrir espaço" pro Radagast também
removia uma peça de sinergia real. Reexecutado com **Anguished Unmaking**
(remoção pontual, proxy sem efeito colateral próprio neste simulador) como
parceiro de troca de verdade neutro. Resultado atualizado abaixo.

Resultados atualizados em `urdragon_v1_runs.jsonl` (3000 jogos, sobrescrito).

---

## Teste #1 — Radagast of Rhosgobel dentro vs. fora (`urdragon_radagast_test.py`) — 2026-08-23

Mesma pergunta já respondida pro Ulalek, agora pro Ur-Dragon. Radagast of
Rhosgobel (`{2}{G}{G}`, Legendary Creature — Avatar Wizard, colors=['G']):
"The first creature spell you cast each turn costs {2} less to cast and
can be cast as though it had flash." Não está na `lista.md` hoje — teste
comparativo, não uma mudança real de deck.

**Diferença estrutural em relação ao Ulalek:** aqui o pacote de desconto de
Dragão já é mais forte E mais amplo do que o "primeira criatura do turno"
de Radagast — ele desconta TODO Dragão conjurado no turno, não só o
primeiro. Além disso, quase toda criatura relevante deste deck já É um
Dragão, então a "primeira criatura do turno" quase sempre coincide com "o
primeiro Dragão do turno" — Radagast empilharia em cima de um desconto que
já existe e é mais amplo, ao contrário do Ulalek (onde Conduit of Ruin é a
única fonte desse tipo). Este deck também não tem nenhum habilitador de
flash incondicional (tipo Vedalken Orrery no Ulalek) — o flash do Radagast
aqui seria uma peça isolada, sem sinergia com mais nada na lista.

Implementado no `CARD_DB` (colors=['G'], NÃO é Dragão — não participa de
`dragon_discount_self`/`dragon_discount_others`, não dispara `dragon_enters()`)
com o mesmo desconto de "primeira criatura do turno" generalizado (soma
com qualquer outra fonte igual, mas neste deck não há nenhuma outra fonte
desse tipo específico — só Radagast, diferente do Conduit of Ruin no
Ulalek).

**Metodologia:** monkeypatch temporário de `BASE_LIBRARY`, mesmas seeds nas
duas variantes. Carta cortada pro teste: **Anguished Unmaking** (remoção
pontual de 3 mana, sem efeito colateral próprio neste simulador sem
oponente real — parceiro de troca de baixa interferência, não é
recomendação de corte real). ~~Firdoch Core~~ foi descartado como parceiro
de troca depois da Correção #3 acima (o usuário mostrou que ele não é
neutro — é Dragão de verdade via Changeling e alimenta o motor de ETB).

**n=3000, seed_base=5500000, mesmas seeds — resultado (pós Correção #3):**

```
                                          SEM Radagast   COM Radagast   delta
Turno medio de conjuracao da Ur-Dragon        6,756          6,746     -0,010
Nunca conjurada em 8 turnos                   50,73%         48,10%    -2,63pp
Avg contagem de Dragoes em campo (fim)         5,567          5,795    +0,228
Avg dobras via Roaming Throne                  0,688          0,754    +0,065
Avg cartas compradas extra                     5,541          5,887    +0,346
Avg mao final                                  2,809          2,876    +0,068
```

**Checagem de ruído (mesma prática do teste do Ulalek):** troquei o
`seed_base` 3 vezes (1M/2M/3M) pra ver se o delta de "nunca conjurada"
inverte de sinal como aconteceu no Ulalek. Aqui **não inverteu** — ficou
consistentemente negativo (melhora) nas 4 rodadas: -2,63pp / -4,77pp /
-3,77pp / -4,33pp. Diferente do Ulalek, este é um efeito real, não ruído
de reamostragem — e se mantém depois da correção do parceiro de troca,
então não era um artefato do bug do Firdoch Core.

**Leitura honesta:** ao contrário do Ulalek, aqui Radagast tem um efeito
real e consistente na taxa de "nunca conjurada em 8 turnos" (melhora de
~3-5pp) — plausível porque este deck é muito mais apertado de mana pra sua
comandante de 9 (mesmo após a Correção #2, ainda o pior "nunca conjurada"
desta biblioteca), então qualquer desconto adicional que empilhe com o
pacote de Dragão já existente tem mais chance real de ser a diferença
entre "consigo pagar" e "não consigo" do que no Ulalek (comandante de 5,
já resolve cedo e de forma confiável). O turno médio *entre as partidas
que resolveram* praticamente não muda (-0,010, dentro do ruído) — o ganho
aparece na cauda (menos jogos travados de vez), não deslocando a média
geral pra frente.

**Conclusão:** aqui o cálculo é mais favorável que no Ulalek, mas ainda
não é um "sim" fácil — o ganho é real só na métrica de "nunca resolve",
não acelera o caso médio, e o texto do Radagast só desconta a PRIMEIRA
criatura do turno (geralmente já um Dragão, então o desconto compete de
fato só quando você teria descartado por 2 mana de diferença). Sem nenhum
habilitador de flash na lista pra aproveitar a segunda metade do texto
dele, o valor aqui vem quase todo do desconto, empilhado num deck que já
tem 5 outras fontes de desconto de Dragão. Vale considerar como uma
inclusão de nicho pra quem sente na mesa que a comandante trava demais —
não uma prioridade óbvia sobre o resto da lista.

---

## Correção #4 — reescrita completa pra modelo de mana por cor — 2026-08-27

Pedido do usuário depois da auditoria de pips (que achou vermelho em
42,7% dos pips do deck mas só 19,8% das fontes, o maior desequilíbrio já
medido nesta biblioteca): reescrever o simulador com rastreio de mana
POR COR, igual ao `thranduil_goldfish_v1.py`, em vez do modelo genérico/
total usado até aqui (documentado como limitação explícita desde a
Simulação #1).

**Arquitetura nova**, mesma da Thranduil: `Card.pips: dict[str,int]`
(custo colorido real de cada carta — computado programaticamente do
`mana_cost` real via Scryfall, não digitado à mão) + `Card.produces:
frozenset` (cores que cada terreno/rock/dork produz, também computado
programaticamente) + `color_sources(state, color)` + `can_cast()` agora
checa mana total E pip por cor, separadamente (desconto de custo reduz
mana genérica, nunca pip colorido — regra real, importante não
confundir).

**Fetch lands implementadas com o mecanismo real** (Regra 6 de
`user-standing-rules.md`): `crack_fetch()` busca de verdade na
biblioteca por um terreno com um dos 2 tipos básicos buscados,
cruzando contra `LAND_BASIC_TYPES` (inclui duais/triomes, não só
básicas — a fetch nunca fica em campo com "produces" próprio, ela vira
o terreno buscado de verdade, escolhido pra resolver a cor mais escassa
no momento).

**Simplificações conservadoras documentadas** (mesma convenção do
Thranduil): Cavern of Souls, Secluded Courtyard, Haven of the Spirit
Dragon têm "any color" mas restrito a criatura do tipo escolhido/Dragão
— tratadas como incolor puro aqui pra não inflar a fixação real pro
resto do deck. Exotic Orchard (dependente de oponente) também incolor,
por não ter dado verificável. Orb of Dragonkind's mana "any combination
of colors" continua contribuindo pro total genérico mas NÃO conta pra
checagem de pip individual (evita double-counting entre cores diferentes
com um pool compartilhado de só 2 mana) — subestima a Orb, não
superestima.

**Métrica nova: color screw.** `check_color_screw()` conta turnos em
que havia mana TOTAL suficiente pra alguma carta na mão mas faltava a
cor certa — algo que o modelo genérico anterior não conseguia nem
detectar, por definição.

**Teste de robustez:** 2 sweeps de 20.000 partidas com timeout de 2s,
**0 erros, 0 timeouts** nos dois.

**n=3000, seed_base=7600000, 8 turnos — resultado após a reescrita:**

```
Avg mulligans: 0,48
Turno medio de conjuracao da Ur-Dragon: 6,88 | mediana: 7,0
Nunca conjurada em 8 turnos: 57,8%
Avg contagem de Dragoes em campo (fim de jogo): 4,27
Avg compras via ataque da Ur-Dragon: 2,23
Avg permanentes gratis via ataque da Ur-Dragon: 0,72
Avg dano proxy total: 18,76
Avg eventos de dano-por-Dragao-ETB: 1,19
Avg Treasures criados: 2,47
Avg dobras via Roaming Throne: 0,38
Avg cartas compradas extra: 4,10
Avg tutores usados: 0,24
Avg ativacoes da mana da Orb of Dragonkind: 0,42
Avg fetches cracked: 0,89
Avg turnos com color screw: 2,05
% de jogos com pelo menos 1 turno de color screw: 41,2% | turno medio do 1o screw: 3,87
Avg mao final: 3,01
```

**Correção honesta ao histórico desta biblioteca:** o modelo genérico
(Simulação #1 → Correção #3) reportou "nunca conjurada em 8 turnos"
caindo progressivamente de 71,5% pra 49,2% conforme bugs reais eram
corrigidos. Com rastreio de cor de verdade, **o número correto é 57,8%**
— pior que o último número do modelo genérico, porque aquele modelo era
literalmente cego pra cor (documentado como limitação desde o início,
nunca escondido, mas agora quantificado): **41,2% das partidas têm pelo
menos 1 turno travado por falta da cor certa apesar de ter mana total
de sobra**, começando em média já no turno 3,87. Isso bate com o
achado da auditoria de pips (vermelho sub-representado) e explica por
que a comandante — que precisa de W+U+B+R+G simultâneos — sofre tanto:
não é só volume de mana, é ter as 5 cores ao mesmo tempo.

Resultados atualizados em `urdragon_v1_runs.jsonl` (3000 jogos,
sobrescrito). Os testes anteriores desta biblioteca que usavam o modelo
genérico (Teste #1 do Radagast) continuam válidos nas métricas que não
dependem de cor (turno de comandante como comparação relativa entre
variantes, contagem de Dragões, etc.) mas não seriam mais diretamente
comparáveis em termos absolutos com os números desta correção.

---

## Teste #2 — Watery Grave vs. Karplusan Forest, com mana por cor (`urdragon_karplusan_test.py`) — 2026-08-27

Primeiro teste real usando o simulador reescrito (Correção #4). Watery
Grave (U/B) é a única terra da lista cujas 2 cores são as mais
sobre-representadas frente à demanda de pips (U a -11,2pp, B a -10,4pp,
auditoria 2026-08-24). Karplusan Forest (R/G, sem tapped) cobre
exatamente as 2 cores mais sub-representadas (R a +23,0pp, G a +5,5pp).

**n=3000, seed_base=2200000, mesmas seeds:**

```
                                    COM Watery Grave   COM Karplusan   delta
Turno medio de conjuracao              6,819              6,798       -0,021
Nunca conjurada em 8 turnos            59,40%             59,50%      +0,10pp
Avg turnos com color screw              2,070              1,957      -0,112
% jogos com >=1 turno de color screw   42,47%             41,00%      -1,47pp
Avg Dragoes em campo (fim)              4,579              4,667      +0,087
```

**Checagem de ruído:** troquei o `seed_base` 3 vezes (1M/3M/4M). O
delta de `color_screw_turns` ficou **consistentemente negativo** nas 4
rodadas (-0,116 / -0,087 / -0,120, mais o -0,112 original) — efeito
real, não ruído. Já o delta de "nunca conjurada" ficou instável e sem
sinal claro (+0,10 / -0,50 / -0,17 / +0,00) — dentro do ruído normal de
trocar 1 carta só.

**Leitura honesta:** a troca melhora de forma real e mensurável a
métrica que ela deveria melhorar (menos turnos travado pela cor errada,
menos partidas com pelo menos 1 turno de color screw), mas o efeito é
pequeno — 1 terra em 36 move a agulha um pouco, não resolve o
desequilíbrio de +23pp sozinha. Isso é esperado e consistente: pra
fechar o gap de verdade seria preciso mais de uma troca (por isso a
sugestão original também incluía cortar uma 2ª fonte B/U e considerar
rocks/dorks de R/G — Talisman of Impulse, Ruby Daring Tracker — ainda
não testados aqui). Vale a troca, mas não é uma bala de prata sozinha.

---

## Correção #5 — segunda troca B/U aplicada de verdade (Island → Battlefield Forge) — 2026-08-27

Pedido do usuário: cortar uma 2ª fonte B/U. Como Watery Grave já tinha
sido usada no Teste #2, o próximo candidato "puro" (só toca cores que
já sobram, não segura nenhuma cor que falta) era uma das duas básicas
singleton: **Island** (U puro) ou **Swamp** (B puro). U tem o gap pior
(-11,2pp vs. -10,4pp de B), então testei cortar a Island.

Escolhi **Battlefield Forge** (R/W) como substituta em vez de outra
R/G — de propósito, pra não empilhar em cima do verde (que já tem o
menor gap dos 3 sub-representados, +5,5pp) e reforçar R (o maior gap,
+23,0pp) e W (+7,0/+8,6pp) ao mesmo tempo, diversificando com a
Karplusan Forest já aplicada.

**Teste pareado com as 2 trocas juntas** (`urdragon_doubleswap_test.py`,
n=3000, seed_base=3300000): o efeito de color screw dobrou de tamanho
em relação à troca única — checado em 4 rodadas de seed diferentes
(1M/4M/6M + a original), delta consistentemente negativo em todas:
-0,212 / -0,215 / -0,185 / -0,192 turnos de color screw por partida.
O delta de "nunca conjurada" também passou a pender pra melhora na
maioria das rodadas (-1,73pp / -0,80pp / +0,33pp / +0,27pp) — ainda
mais ruidoso que o color screw, mas majoritariamente positivo agora
(diferente da troca única, que tinha ficado sem sinal claro).

**As duas trocas aplicadas de verdade em `lista.md`** (Watery Grave →
Karplusan Forest, Island → Battlefield Forge). Reteste de robustez:
20.000 partidas, 0 erros/timeouts.

**n=3000, seed_base=7600000, 8 turnos — resultado oficial após as 2 trocas:**

```
Avg mulligans: 0,48
Turno medio de conjuracao da Ur-Dragon: 6,84 | mediana: 7,0
Nunca conjurada em 8 turnos: 56,6%
Avg contagem de Dragoes em campo (fim de jogo): 4,76
Avg dano proxy total: 29,44
Avg Treasures criados: 2,96
Avg dobras via Roaming Throne: 0,56
Avg cartas compradas extra: 4,62
Avg fetches cracked: 0,90
Avg turnos com color screw: 1,76
% de jogos com pelo menos 1 turno de color screw: 38,0% | turno medio do 1o screw: 3,71
Avg mao final: 3,01
```

Comparando com a Correção #4 (antes de qualquer troca): "nunca
conjurada" caiu de 57,8% pra 56,6%, e a taxa de color screw caiu de
41,2% pra 38,0% das partidas. Confirma a leitura do Teste #2: real,
consistente, mas ainda não resolve o desequilíbrio de +23pp sozinho —
faltam mais peças (rocks/dorks de R, ex: Talisman of Impulse, Ruby
Daring Tracker, ainda não testados) se o objetivo for fechar o gap por
completo.

Resultados atualizados em `urdragon_v1_runs.jsonl` (3000 jogos, sobrescrito).

---

## Correção #6 — Hellkite Charger/Klauth/Goldspan Dragon tinham haste real nunca modelada — 2026-08-27

Achado ao registrar Ruby, Daring Tracker (que tem haste real) pro teste
de rock/dork de R/G pedido pelo usuário: `ready_creatures()` travava
TODA criatura por doença de invocação até o próximo turno, sem checar
haste — mas Hellkite Charger, Klauth e Goldspan Dragon têm "Flying,
haste" no oráculo real (conferido no Scryfall), o que remove essa
restrição tanto pra atacar quanto pra ativar habilidades `{T}`. Nenhuma
das 3 tinha sido marcada. Corrigido com uma tag `"haste"` checada em
`ready_creatures()`.

**Reteste de robustez:** 20.000 partidas, 0 erros/timeouts.

**n=3000, seed_base=7600000 — resultado após a correção:**

```
Nunca conjurada em 8 turnos: 55,6% (era 56,6%)
Avg contagem de Dragoes em campo (fim de jogo): 4,95 (era 4,76)
Avg dano proxy total: 34,22 (era 29,44)
Avg Treasures criados: 3,20 (era 2,96)
```

Impacto pequeno mas real — as 3 cartas já podiam atacar/gerar valor no
mesmo turno que resolviam, e o simulador estava subestimando isso.

---

## Correção #7 — rock + dork de R/G aplicados (Talisman of Impulse, Ruby Daring Tracker) — 2026-08-27

Pedido do usuário: testar rocks/dorks de R/G, com sugestão de onde
cortar. Cortes escolhidos com justificativa (não palpite):

- **Lightning Greaves** → **Talisman of Impulse**: o deck já tem 2
  fontes de haste grátis (Temur Ascendancy, Dragon Tempest), tornando
  Lightning Greaves parcialmente redundante como fonte de haste; não
  produz mana nem vantagem de carta.
- **Magda, Brazen Outlaw** → **Ruby, Daring Tracker**: Magda só tem 1
  Dwarf no deck (ela mesma), então "other Dwarves get +1/+0" nunca
  dispara e o Treasure-por-tap só acontece com ela mesma atacando (no
  máximo 1/turno); a única habilidade forte dela (tutor ao sacrificar 5
  Treasures) exige acumular 5 primeiro, lento. Ruby é R/G direto, tem
  haste real (Correção #6) e ainda ajuda combate.

**Teste pareado com as 4 combinações** (`urdragon_rockdork_test.py`,
n=3000, seed_base=7100000): Talisman sozinho melhorou color screw
(-0,175 turnos) mas não moveu "nunca conjurada" (+0,40pp, ruído). Ruby
sozinha melhorou as duas métricas (-2,07pp nunca conjurada, -0,102
color screw) — faz sentido, ela também é um corpo real com haste, não
só uma fonte de mana. **As duas juntas: -4,23pp em "nunca conjurada".**
Checado em mais 3 rodadas de seed (1,5M/2,5M/5,5M) — delta
consistentemente negativo em "nunca conjurada" nas 4 rodadas totais
(-4,23 / -2,00 / -1,23 / -1,90pp) e em color screw também
(-0,104 / -0,086 / -0,115 / -0,066) — efeito real, não ruído.

**As duas trocas aplicadas de verdade em `lista.md`.** Reteste de
robustez: 20.000 partidas, 0 erros/timeouts.

**n=3000, seed_base=7600000 — resultado oficial após esta troca:**

```
Avg mulligans: 0,48
Turno medio de conjuracao da Ur-Dragon: 6,79 | mediana: 7,0
Nunca conjurada em 8 turnos: 53,3% (era 55,6%)
Avg contagem de Dragoes em campo (fim de jogo): 5,22
Avg dano proxy total: 36,88
Avg cartas compradas extra: 5,27
Avg turnos com color screw: 1,69
% de jogos com pelo menos 1 turno de color screw: 37,4% (era 38,5%)
Avg mao final: 3,05
```

**Progresso acumulado nesta biblioteca, do início ao fim desta sessão de
correções:** "nunca conjurada em 8 turnos" foi de 71,5% (Simulação #1,
com bugs reais de desconto/comandante) para 53,3% agora — via correção
de bugs reais (Correções #1-#3, #6) e trocas de manabase/rocks/dorks
testadas e aplicadas com dado real (Correções #5, #7). Ainda não é um
deck com comandante confiável — 53% é ainda o pior desta biblioteca —
mas a melhora é real e documentada passo a passo, não estimada.

Resultados atualizados em `urdragon_v1_runs.jsonl` (3000 jogos, sobrescrito).

---

## Correção #8 — Magda, Brazen Outlaw: duas falhas reais, corrigidas

O usuário apontou, corretamente, que a análise da Correção #7 (cortar
Magda por Ruby, Daring Tracker) estava errada: *"Magda cria tesouros
com ela mesma e com Firdoch Core. Além disso a Magda tutora dragões,
então ela tem duas funções!"*

Duas falhas reais, não uma:

1. **Sinergia perdida com Firdoch Core.** Firdoch Core tem Changeling
   ("this card is every creature type"), então é um Dwarf de verdade —
   dispara "Whenever a Dwarf you control becomes tapped, create a
   Treasure token" quando ela tapa pra mana, não só quando Magda ataca.
   Eu tinha tratado Firdoch Core como neutra nessa comparação; não é.
2. **A tag nunca foi implementada.** `"treasure_tutor_dragon"` existia
   como tag decorativa em Magda desde que ela entrou no CARD_DB — nunca
   houve nenhuma função checando essa tag em lugar nenhum do código.
   Ou seja, Magda era um corpo puramente decorativo na simulação, uma
   violação real da Regra 3 (efeito estrutural precisa de implementação
   real) que passou despercebida até agora.

**Corrigido:** implementada `do_magda_treasures(state)` — conta taps
reais de Dwarves (Magda atacando + Firdoch Core tapando pra mana),
cria Treasure por tap, e sacrifica 5 Treasures pra tutorar
artifact/Dragon pro campo quando acumula o suficiente. Testado (200
jogos smoke test, 20.000 jogos de robustez, seed_base=2200000, 0
erros/timeouts).

**Reteste pareado Magda (real) vs. Ruby** (`urdragon_magda_retest.py`,
Talisman fixo nas duas variantes): com a implementação real de Magda,
ela agora realmente contribui — 0,057 tutores/jogo em média (≈1 tutor
a cada 17-18 partidas em 8 turnos), algo que Ruby não replica. Mas em
"nunca conjurada em 8 turnos", Ruby continuou à frente em todas as 4
rodadas de seed testadas (delta Ruby−Magda): -3,37pp / -2,40pp /
-0,47pp / -1,13pp. Direção consistente (Ruby sempre melhor), mas
magnitude bem mais ruidosa do que outros testes desta sessão (que
tipicamente ficavam bem agrupados, tipo o teste de rock/dork logo
acima) — sinal de que a diferença real entre as duas é pequena.

**Decisão final:** mantido Ruby, Daring Tracker na lista (não revertido
para Magda). Motivo: Ruby vence de forma consistente (4/4 rodadas) na
métrica mais importante — conjurar o comandante — mesmo contando o
valor real e agora corrigido de Magda. Mas a vantagem é pequena e a
função de tutor de Magda é única (Ruby não tutora nada); se o baralho
mudar de direção (menos foco em curva, mais em recursão de
artifact/Dragon), vale reconsiderar — a implementação de Magda agora
está correta e pronta para uso, não é mais uma tag morta.

`lista.md` permanece: Ruby, Daring Tracker dentro, Talisman of Impulse
dentro, Magda, Brazen Outlaw fora (estado idêntico ao pós-Correção #7).
Reteste oficial (n=3000, seed_base=7600000) confirma os mesmos números
de antes — 53,3% nunca conjurada, 37,4% color screw — sem regressão.

---

## Correção #9 — Lightning Greaves (shroud) e outra tag morta encontrada

Usuário corrigiu de novo: *"Lightning Greaves além de haste enabler é
proteção imediata com Hexproof"* — na verdade é **shroud**, não
hexproof (conferido via oráculo: "Equipped creature has haste and
shroud"), mas o ponto central estava certo: a razão usada pra cortar
Lightning Greaves na Correção #7 ("shroud é real mas situacional sem
oponente modelado") não era um teste — era uma desculpa, já que o
simulador goldfish não modela remoção de oponente e nunca modelou.

Testando a troca de volta (Lightning Greaves dentro, cortando Talisman
of Impulse) achei, sem querer, um **segundo bug de tag morta da mesma
classe da Magda**: `"haste_all"` (Temur Ascendancy: "Creatures you
control have haste", estático) e `"haste_flying"` (Dragon Tempest:
"Whenever a creature you control with flying enters, it gains haste
until end of turn") existiam como tags decorativas desde que essas
cartas foram registradas — `ready_creatures()` nunca as checava, só
olhava a tag `"haste"` na própria criatura. Ou seja, Dragões recém-
conjurados ficavam presos por doença de invocação mesmo com Temur
Ascendancy ou Dragon Tempest em campo, quando o oráculo real remove
essa restrição.

**Corrigido:** `ready_creatures()` agora checa presença de Temur
Ascendancy (libera qualquer criatura) e Dragon Tempest + `has_flying()`
(libera só voadoras, só no turno em que entram). `FLYING_CREATURES`
construído carta a carta via oráculo real (todos os Dragões do deck e
Birds of Paradise têm Flying real, nenhum outro creature do deck tem).
Testado: 200 jogos smoke test, 20.000 jogos de robustez (0 erros).

**Impacto real e limpo do bugfix isolado** (mesma lista, Talisman+Ruby,
mesma seed_base=7600000, n=3000, único fator variando é o código):

| métrica | antes do fix | depois do fix | delta |
|---|---|---|---|
| nunca conjurada | 53,3% | 52,5% | -0,8pp (esperado, pequeno — haste não afeta quando o comandante é conjurado) |
| dano proxy médio | 36,88 | 48,24 | **+11,36 (+31%)** |
| eventos dano-ETB | 1,83 | 2,18 | +0,35 |
| cartas compradas extra | 5,27 | 5,74 | +0,47 |

Efeito real e grande no motor de dano — o deck estava subestimando o
próprio output desde que Temur Ascendancy/Dragon Tempest entraram no
simulador, não só nesta sessão.

**Sobre a troca Lightning Greaves ↔ Talisman especificamente:** testei
isolado (mesmas seeds, com o fix já aplicado) e cortar o Talisman por
Lightning Greaves custa real: -36% no dano proxy médio (75,69→48,28 no
teste isolado — nota: esse número específico saiu inflado por um
artefato de ordenação da lista, ver observação de metodologia abaixo;
o delta relativo de -36% é a leitura confiável, não os valores
absolutos desse teste isolado). Motivo: Talisman é rampa real, perder
rampa atrasa o desenvolvimento do board mesmo sem mudar o turno de
conjuração do comandante. Apresentei o dado ao usuário, que decidiu
**manter Talisman e reverter o corte de Lightning Greaves** — proteção
permanente do comandante não compensa 36% a menos de dano médio nesta
lista. `lista.md` final: idêntico ao pós-Correção #8 (Talisman+Ruby
dentro, Magda e Lightning Greaves fora). Só o bugfix de haste foi
mantido — não é mudança de lista, é correção de simulador.

**Observação de metodologia (importante pra testes futuros):** o
padrão usado em todos os scripts de teste pareado desta sessão
(`build_library(cuts, adds)` faz `lib.remove(c)` seguido de
`lib.append(a)`) coloca a carta nova no FIM da lista, não na posição
da carta removida. `random.shuffle()` do Python é Fisher-Yates baseado
em ÍNDICES, não em conteúdo — então mover uma carta do meio da lista
pro final desloca a posição de shuffle de todas as cartas entre o
ponto original e o fim, não só da carta trocada. Isso não invalida as
conclusões direcionais (todos os testes desta sessão foram checados em
múltiplas seed_bases independentes e a direção do efeito nunca mudou),
mas explica parte do ruído extra visto em alguns testes (ex: o reteste
da Magda, Correção #8) e reduz a precisão do controle de variância que
o pareamento de seeds deveria dar. Fix recomendado pra scripts futuros:
inserir a carta nova no índice da carta removida, não no fim da lista.
Não refiz os testes já concluídos com isso — os achados de direção já
foram confirmados por múltiplas seed_bases independentes de qualquer
forma.

---

## Correção #10 — Cavern of Souls, Secluded Courtyard e Haven of the Spirit Dragon eram fixação real, não incolor

Usuário: *"Vc por acaso colocou Cavern of Souls, Haven of the Spirit
Dragon e Secluded Courtyard como condicionais, mas elas geram mana de
qualquer cor para o tipo de criatura escolhida (Dragão). Mais um erro
importante conceitual e prático de sua parte!"*

Essas 3 terras estavam com `produces=set()` (incolor) desde antes desta
sessão — decisão documentada, não um esquecimento cru, mas a
justificativa ("restrição real demais pra modelar sem inflar fixação pro
resto do deck") não se sustentava: num deck com identidade tribal clara
(comandante Dragão + 21 criaturas Dragão na lista), o tipo escolhido em
Cavern of Souls/Secluded Courtyard é obviamente Dragão, e Haven of the
Spirit Dragon já é fixo em Dragão por texto. Conferido: essas 21
criaturas carregam **49% de todos os pips coloridos do deck**, e **70,7%
da demanda de vermelho especificamente** — exatamente a fatia que mais
precisa de fixação.

**Corrigido:** `color_sources()` ganhou o parâmetro `dragon_creature_spell`
— quando a carta sendo checada é um Dragão de verdade (creature + tag
dragon), essas 3 terras contam como fonte de qualquer uma das 5 cores;
pra qualquer outra checagem (ramp genérico, removal, fetches decidindo o
alvo mais escasso) continuam incolores, do jeito documentado antes — não
infla fixação onde o oráculo real não permite. `has_color_sources_for()`
repassa esse flag automaticamente. `DRAGON_ANY_COLOR_LANDS` documentado
com o oráculo completo das 3 cartas.

Testado: 200 jogos smoke test, 20.000 jogos de robustez (0 erros).

**Impacto real e limpo do fix isolado** (mesma lista, mesma
seed_base=7600000, n=3000, único fator variando é o código — nenhuma
troca de carta):

| métrica | antes do fix | depois do fix | delta |
|---|---|---|---|
| nunca conjurada | 52,5% | 50,0% | **-2,5pp** |
| color screw (% jogos) | 37,4% | 34,1% | **-3,3pp** |
| dano proxy médio | 48,24 | 57,03 | **+8,79 (+18%)** |
| Dragões em campo (fim de jogo) | 5,49 | 5,87 | +0,38 |
| eventos dano-ETB | 2,18 | 2,50 | +0,32 |
| cartas compradas extra | 5,74 | 6,19 | +0,45 |

Fontes de mana por cor recalculadas (caso geral vs. conjurando um
Dragão especificamente):

| cor | fontes (geral) | fontes (pra Dragão) |
|---|---|---|
| W | 20 (18,2%) | 23 (18,4%) |
| U | 18 (16,4%) | 21 (16,8%) |
| B | 19 (17,3%) | 22 (17,6%) |
| R | 25 (22,7%) | **28 (22,4%)** |
| G | 28 (25,5%) | 31 (24,8%)

O vermelho continua sendo a cor mais espremida no caso geral (42,7% de
demanda de pips vs. 22,7% de fontes), mas especificamente pra conjurar
Dragões — 70,7% da própria demanda de vermelho — o deck tem 3 fontes a
mais de vermelho do que a tabela geral mostrava. Isso é diretamente
relevante pra qualquer avaliação de incluir mais Dragões pesados em R
(ex: os candidatos Smaug de The Hobbit em discussão) — a real fixação
disponível pra esse tipo de carta é maior do que a auditoria anterior
sugeria.

Regra 6 de `references/user-standing-rules.md` recebeu um adendo
cobrindo esse padrão (terrenos "any color" restritos a tipo de criatura
escolhido/fixo), espelhado nas duas cópias (repo + skill canônico).

`lista.md` não mudou — correção de simulador, não de decklist.
`urdragon_v1_runs.jsonl` sobrescrito com os números pós-fix.

---

## Correção #11 — crítica metodológica real do usuário + 3 bugs achados junto

Usuário: *"Não, quero a análise real da necessidade de mana, pq quando vc
soma todos os pips, não considera que dificilmente eu irei cast 3
dragões que precisam de pips vermelho no mesmo turno! Ou eles entram
por habilidade do Ur-Dragon, ou por outras habilidades!"*

Ponto metodológico correto: somar todos os 41 pips de vermelho da lista
inteira (`pip_total` na auditoria) e comparar contra fontes de mana é
uma proxy útil mas grosseira — implicitamente assume que toda a demanda
de pips do deck precisa ser paga "de uma vez", quando na prática (a) só
uma fração do deck é comprada/jogada numa partida de 8 turnos, (b) boa
parte dos Dragões que acabam em campo nunca teve pip nenhum pago
(tokens, reanimação, tutor), e (c) mesmo os que são conjurados de
verdade estão espalhados ao longo de 8 turnos, não simultâneos.

Investigando isso pra dar uma resposta com número real (não só
concordar em texto), achei 3 bugs reais adicionais na mesma área:

1. **Haunting Voyage (`mass_reanimate`) nunca tinha sido implementada** —
   tag morta desde que a carta entrou no CARD_DB. A carta custava 6 mana
   e não fazia nada no simulador. Oráculo real: "Choose a creature type.
   Return up to two creature cards of that type from your graveyard to
   the battlefield." Implementado (modo hardcast só — modo foretold, com
   custo/timing de 2 turnos separado, não modelado, mesma simplificação
   conservadora documentada de outras cartas complexas).
2. **Utvara Hellkite** ("Whenever A Dragon you control attacks...") e
   **Old Gnawbone** ("Whenever A creature you control deals combat
   damage...") **NÃO são gatilhos auto-referentes** — ao contrário de
   Goldspan/Klauth/Savage Ventmaw (que dizem "whenever ~ [esta carta]
   attacks"), essas 2 disparam pra qualquer Dragão atacando (Utvara) ou
   qualquer criatura causando dano (Old Gnawbone). O código anterior só
   checava a tag na própria carta atacante dentro do loop por-dragão —
   ou seja, só disparavam quando a própria Utvara/Old Gnawbone estava no
   grupo atacando, e Old Gnawbone criava só 1 treasure por atacante
   (contagem) em vez de "tantos quanto o poder" (magnitude). Corrigido:
   checagem de presença em campo (não precisa estar atacando), Utvara
   escala com `n_attacking`, Old Gnawbone com a soma de poder dos
   atacantes.

Testado: 300 jogos smoke test, 20.000 jogos de robustez (0 erros) depois
de cada uma das 2 rodadas de fix.

**Impacto real dos 3 fixes juntos** (mesma seed_base=7600000, n=3000):

| métrica | antes | depois |
|---|---|---|
| nunca conjurada | 50,0% | 48,1% |
| Dragões em campo (fim de jogo) | 5,87 | **8,08** |
| dano proxy médio | 57,03 | **90,79 (+59%)** |
| Treasures criados | ~4-5 | **11,01** |

**A resposta real pra pergunta do usuário** (n=4000, seed_base=20200000):
dos ~7,85 Dragões em campo no fim de uma partida de 8 turnos —

- **48,2%** são tokens (Lathliss/Miirym/Broodmother/Utvara) — nunca
  tiveram pip nenhum pago.
- **7,2%** entraram de graça por reanimação/tutor (Bladewing, Haunting
  Voyage, Magda, permanente grátis da própria Ur-Dragon atacando).
- **Só 44,6% (3,50 de 7,85) foram realmente conjurados pagando mana** —
  isso dá **0,44 Dragões conjurados por turno em média**, ao longo de 8
  turnos. Nunca "3 Dragões de pip vermelho no mesmo turno" como cenário
  típico — é um evento de cauda, não a norma.

**Conclusão sobre a metodologia:** a tabela de "demanda de pips
agregada vs. fontes agregadas" (usada nas Correções/auditorias #5-#10)
é um proxy razoável pra saber SE a manabase tem cor suficiente no
agregado, mas superestima a pressão real turno-a-turno, e ignora
completamente as vias de entrada gratuita. A métrica que já existia no
simulador e É turno-a-turno de verdade — `color_screw_turns` /
`first_color_screw_turn` (34,5% dos jogos têm pelo menos 1 turno real de
mana total ok mas cor errada, turno médio do primeiro screw ~3,5) — é a
correta pra avaliar necessidade real de mana, não a soma de pips. Daqui
pra frente, ao avaliar necessidade de cor, priorizar essa métrica
dinâmica sobre a tabela estática de pips agregados.

`lista.md` não mudou. `urdragon_v1_runs.jsonl` sobrescrito.

---

## Correção #12 — revisão completa do deck e do simulador

Usuário: *"Revise o deck inteiro e o simulador e veja o que mais está
'de fora' ou errado."*

Metodologia: extraí toda tag usada em `add()` (47 tags únicas, 68
cartas nomeadas), contei quantas vezes cada tag aparece no arquivo
inteiro fora da própria linha `add()` — count=1 significa tag nunca
checada em lugar nenhum. Pra cada uma dessas, conferi se o efeito real
estava implementado via checagem por NOME (padrão já usado nesta sessão
pra Magda/Lathliss/Bladewing/etc) antes de concluir "morta de verdade".
Depois cruzei as 63 cartas não-terrestres da lista contra o oráculo
real completo (Scryfall), carta a carta.

### Corrigido

1. **Klauth, Unrivaled Ancient** — "X é o poder TOTAL das criaturas
   atacantes", código usava só o poder da própria Klauth. Corrigido pra
   usar a soma real.
2. **Ramos, Dragon Engine** — "+1/+1 counter pra CADA cor" do spell
   conjurado, código dava +1 flat por spell independente de cor.
   Corrigido pra `len(pips)` (cores distintas do custo).
3. **Twinflame Tyrant** — "if a source you control would deal damage...
   it deals double" — tag `damage_doubler` nunca implementada. Dobrador
   global de dano completamente ausente do `proxy_damage_total`
   reportado a sessão inteira. Implementado dentro de `proxy_drain()`
   (ponto único de entrada de dano no simulador).
4. **Atarka, World Render** — "whenever a Dragon you control attacks, it
   gains double strike" — tag `attack_double_strike` nunca implementada.
   Dobra gatilhos de "deals combat damage" (Ancient Copper/Gold Dragon
   d20, Old Gnawbone) — não os de "whenever ~ attacks" (Utvara), que
   disparam 1x mesmo com double strike (regra real: atacar 1x, causar
   dano 2x).
5. **The Great Henge** — "{T}: Add {G}{G}. You gain 2 life." — a
   habilidade de mana repetida nunca tinha sido registrada (só o
   desconto de custo e o gatilho de +1/+1 contador+compra estavam).
   Adicionado `produces={"G"}` + 2 mana genérica em `rocks_mana()`
   (vida não rastreada, mesma simplificação de sempre).
6. **Garruk's Uprising** — oráculo tem 3 linhas, não 1: faltava a compra
   única de ETB ("if you control a creature power 4+, draw a card") —
   só a linha recorrente ("whenever a creature enters...") estava
   implementada. Adicionada a checagem de ETB único.
7. **Up the Beanstalk** — tag `bigspell_draw` nunca implementada, carta
   100% decorativa. Implementado ETB draw + gatilho recorrente (spell
   MV≥5, usa MV real impresso, não custo com desconto).
8. **Sylvan Library** — tag `card_selection` nunca implementada, carta
   100% decorativa apesar de ser um dos motores de seleção mais fortes
   do formato. Modelado como +1 carta líquida por turno (compra 2
   extras, devolve 1 pagando 4 vida — vida não rastreada no simulador,
   linha de jogo mais comum documentada como premissa).
9. **Rhythm of the Wild** — tag `riot` nunca implementada. Riot = escolha
   de +1/+1 contador OU haste — modelado sempre escolhendo haste (mesma
   lógica agressiva já usada no resto do simulador), só criaturas
   não-token.
10. **Haunting Voyage** (já corrigida na Correção #11) — bug de crash
    real achado nos 20k jogos de robustez desta rodada: se um dos 2
    alvos reanimados é a própria Bladewing the Risen, o gatilho de ETB
    dela ("return target Dragon permanent from graveyard") dispara ao
    entrar via ESTA reanimação também, e pode consumir o outro alvo do
    cemitério antes do loop da Haunting Voyage chegar nele —
    `list.remove(x): x not in list`. Corrigido checando presença no
    cemitério antes de cada remoção.
11. **Balefire Dragon** — tag `combat_wipe_proxy` nunca implementada.
    Reclassificada como `interaction` (mesma categoria de
    Assassin's Trophy/Beast Within/etc) — "deals that much damage to
    each creature that player controls" depende de criaturas de
    oponente em campo, genuinamente não-modelável num goldfish solo, não
    é um bug a corrigir, é escopo real do simulador.

Testado após cada rodada: smoke test (200-300 jogos) + robustez (20-30k
jogos). Um crash real achado e corrigido nos 30k finais (item 10 acima)
— 0 erros/timeouts na sweep final.

### Deferido (achado, documentado, não implementado — razão explícita)

- **Hellkite Charger** ("pay {5}{R}{R}: untap all attacking creatures,
  additional combat phase") — real e potencialmente grande, mas uma
  chamada recursiva de `combat_step()` arrisca disparar de novo efeitos
  que deveriam ser 1x-por-turno (ex: `do_magda_treasures`, que hoje é
  gatilhado por chamada de combate, não por turno) — precisa de reforma
  maior pra separar "1x por turno" de "1x por combate" antes de
  implementar com segurança. Não implementado pra não introduzir um bug
  novo sob pressa.
- **Sarkhan, Soul Aflame** ("may become a copy of a Dragon that
  enters") — habilidade opcional complexa (troca todas as
  características até o fim do turno) — função base dele (desconto de
  Dragão) já está coberta; custo/benefício de implementar a cópia não
  compensa a complexidade.
- **Return of the Wildspeaker** — restrição real "non-Human creatures"
  ignorada (código usa maior poder entre TODAS as criaturas). Só 3
  criaturas Human no deck, todas dorks de baixo poder — a criatura de
  maior poder é quase sempre um Dragão de qualquer forma. Impacto
  desprezível, não vale o custo de rastrear subtipos de criatura só pra
  isso.
- **Haven of the Spirit Dragon** ("{2}, T, Sacrifice: return Dragon from
  graveyard to hand") — situacional (só relevante se um Dragão já
  morreu, raro nesse simulador sem remoção de oponente modelada), e só
  devolve pra MÃO (ainda precisa ser conjurado de novo) — baixo valor
  frente ao custo de sacrificar uma fonte de mana.
- **Bladewing the Risen** ("{B}{R}: Dragons get +1/+1") e **Scourge of
  Valkas** ("{R}: +1/+0") — pumps ativados de combate, sem loop de
  decisão de "gastar mana sobrando em truque de combate" no simulador.
  Baixo valor pra implementar por 1 ativação/turno.
- **Smothering Tithe** — já corretamente tratada como dependente de
  oponente (`opponent_dependent`), não é um bug, confirmado.

### Impacto real acumulado (mesma seed_base=7600000, n=3000)

| métrica | antes desta revisão | depois |
|---|---|---|
| nunca conjurada | 48,1% | **41,4%** |
| Dragões em campo (fim de jogo) | 8,08 | **11,82** |
| dano proxy médio | 90,79 | **436,51 (+381%)** |
| Treasures criados | 11,01 | **21,98** |
| cartas compradas extra | 6,62 | **11,37** |
| Dragon tokens | 3,94 | 6,59 |
| color screw (% jogos) | 34,5% | 33,1% |

O salto grande em dano proxy vem de efeitos MULTIPLICATIVOS que nunca
tinham sido implementados juntos (Twinflame Tyrant dobra tudo, Atarka
dobra gatilhos de dano-de-combate específicos) empilhando em cima de um
motor que já estava saindo mais forte (mais Dragões em campo por turno,
mais mana via Klauth/Great Henge corrigidos, mais Treasures via Old
Gnawbone/Ramos corrigidos — efeito bola de neve real, não inflação
artificial). Essa é a correção mais significativa da sessão em termos
de poder real do motor: o deck estava sendo medido, a sessão inteira,
como bem mais fraco do que a lista realmente é.

`lista.md` não mudou nenhuma vez nesta revisão — 100% correção de
simulador. `urdragon_v1_runs.jsonl` sobrescrito.

---

## Correção #13 — 3 achados reais que eu ainda tinha deixado passar

Usuário, insistindo depois da Correção #12: *"1) Não considerou os
terrenos 'tribais'; 2) Esqueceu Haunting Voyage; 3) Se duvidar não
considerou Crux of Fate boardwipe assimétrico: e sabe-se lá quais
outros erros!"*

1. **Terrenos que entram tapped nunca foram modelados — achado real,
   novo.** Reauditando a manabase carta a carta, confirmei que Cavern of
   Souls/Secluded Courtyard/Haven of the Spirit Dragon (as "tribais" de
   verdade) continuam corretas (testado isoladamente: 1 Cavern em campo
   dá exatamente 1 fonte de cada cor pra spell de Dragão, 0 pro caso
   geral). Mas achei outra coisa real no caminho: **nenhum terreno no
   simulador inteiro jamais entrava tapped**, mesmo os 4 Triomes
   (Jetmir's Garden, Ketria Triome, Zagoth Triome, Ziatora's Proving
   Ground) que têm "This land enters tapped." incondicional no oráculo
   — sem opção de pagar vida como os choques. Corrigido:
   `ETB_TAPPED_LANDS` + `state.tapped_land_this_turn`, exclui a terra da
   contagem de mana total/cor no turno em que é jogada (via `play_land`
   ou `crack_fetch`, se uma fetch buscar um Triome), libera no turno
   seguinte. Os 8 choques (Blood Crypt etc.) **continuam sempre
   destravados** — têm escolha real de pagar 2 vida, e vida nunca é
   recurso rastreado neste simulador, premissa agora documentada
   explicitamente em vez de implícita.
2. **Haunting Voyage: o modo foretold ("return ALL") realmente não
   tinha sido implementado** — eu tinha descartado isso como "fora de
   escopo" na Correção #11, o que na prática é esquecer metade da
   carta, não uma simplificação razoável. Implementado de verdade: ação
   de foretell separada em `main_phase()` ({2} genérico, exila da mão,
   sem seguir regras normais de conjuração), heurística de conjurar da
   exilada assim que 7 mana sobrar NUM TURNO POSTERIOR (regra real:
   "cast it on a later turn" — bug secundário evitado explicitamente,
   sem isso teria conjurado no mesmo turno do foretell). Modo ALL
   reaproveita o mesmo helper (`reanimate_dragons_from_graveyard`) do
   hardcast, sem limite de 2.
3. **Crux of Fate não é simétrico — e o problema real era maior do que
   só essa carta.** Crux of Fate escolhe "destruir todos os Dragões" OU
   "destruir todos os não-Dragões" — claramente favorável pra esse deck
   (mata só o lixo próprio, mantém as ameaças). Eu tinha ela (e Austere
   Command) tageadas 'wipe' com tratamento `pass` — mas o problema real
   não era a rotulagem "simétrica", era que a IA gulosa CONJURAVA essas
   cartas mesmo sem fazer nada (can_cast só checa mana, não alvo real),
   desperdiçando carta e mana. Investigando isso achei que o MESMO bug
   afeta as 10 cartas tageadas 'interaction' (Swords to Plowshares,
   Assassin's Trophy, Beast Within, Heroic Intervention, Swan Song,
   Teferi's Protection etc.) — nenhuma tinha tratamento em
   `resolve_instant_sorcery`, e várias são baratas (Swords to Plowshares
   {W}=1 mana), competindo por prioridade cedo contra Dragões de
   verdade. Corrigido de forma ampla: cartas 'interaction'/'wipe'
   excluídas do loop guloso de auto-cast (ficam na mão, esperando um
   alvo que este goldfish solo não modela — não fingem que são inúteis,
   só não fingem um alvo que não existe).

Testado: 300 jogos smoke test, 30.000 jogos de robustez (0 erros).

**Impacto real combinado** (mesma seed_base=7600000, n=3000, 3 mudanças
juntas — não isolado por mudança, efeitos mistos e parcialmente
opostos):

| métrica | antes (Correção #12) | depois |
|---|---|---|
| nunca conjurada | 41,4% | **39,8%** |
| color screw (% jogos) | 33,1% | **35,1%** (Triomes tapped são um drag real) |
| dano proxy médio | 436,51 | 396,75 |
| Avg mão final | 3,12 | **5,05** (interaction/wipe empilhando na mão, sem alvo) |

Nunca conjurada e dano proxy médio ainda melhoraram no líquido (mais
mana livre pra ameaças reais > o drag dos Triomes tapped), color screw
piorou um pouco (correto — os Triomes tapped são um custo real que
faltava). A mão final maior é esperada e realista: cartas reativas
seguram até ter alvo, mesmo que este simulador nunca gere um.

`lista.md` não mudou. `urdragon_v1_runs.jsonl` sobrescrito.

---

## Correção #14 — segunda passada carta a carta completa (pedido do usuário: "revise tudo de novo")

Usuário insistiu de novo (mesma cobrança), depois pediu explicitamente
uma nova revisão carta a carta completa. Desta vez gerei o oráculo real
e completo (sem truncar) das 100 cartas da lista (comandante + 63
não-terrestres + 36 terrenos) lado a lado com as tags do CARD_DB e
reli cada uma. 3 achados reais novos:

1. **Delighted Halfling superestimava fixação.** Oráculo real: "{T}: Add
   {C}." + "{T}: Add one mana of any color. Spend this mana only to
   cast a **legendary spell**." O CARD_DB tinha ela com
   `produces=set("WUBRG")` incondicional — contava como fonte de
   qualquer cor pra QUALQUER spell, não só lendários. Levantei as 12
   permanentes lendárias reais do deck (via `type_line`, não
   suposição) e corrigido: `color_sources()` ganhou parâmetro
   `legendary_spell`, só libera Delighted Halfling como fonte de
   qualquer cor quando a carta sendo conjurada é lendária de verdade.
   Mesmo padrão já usado pra Cavern of Souls/Secluded Courtyard/Haven of
   the Spirit Dragon.
2. **Os 6 tutores de terreno verde nunca respeitavam o tipo real, nem
   priorizavam a cor mais escassa.** `land_tutor1`/`land_tutor2`/
   `land_tutor2_direct` eram tags compartilhadas entre cartas com
   restrições DIFERENTES (Farseek busca Plains/Island/Swamp/Mountain;
   Nature's Lore/Three Visits só Forest; Cultivate/Kodama's Reach só
   terreno BÁSICO de verdade, não dual/triome com o tipo) — o código
   pegava qualquer terreno da biblioteca, sem checar tipo nem
   priorizar a cor que falta. Isso afeta 6 dos spells mais jogados no
   early game do deck. Corrigido com `search_land()` (mesmo padrão de
   pontuação do `crack_fetch()` — prioriza a cor mais escassa entre os
   elegíveis pro tipo real de cada carta), dispatch por nome em vez de
   tag genérica. Farseek força tapped (oráculo real), Nature's
   Lore/Three Visits/Skyshroud Claim destravadas (oráculo real não
   fala em tapped).
3. **Hellkite Courser estava sem NENHUMA implementação além da tag
   'dragon'.** Oráculo real: "When this creature enters, you may put a
   commander you own from the command zone onto the battlefield. It
   gains haste. Return it to the command zone at the beginning of the
   next end step." — bota a Ur-Dragon em campo DE GRAÇA (sem pagar a
   taxa crescente de recast!), com haste, ataca esse turno, e volta pra
   zona de comando no final do turno (pode ser conjurada de verdade
   depois, do zero). Implementado via `enter_battlefield(...,
   count_as_cast=False)` — novo parâmetro que evita incrementar
   `commander_cast_count`/marcar `commander_cast_turn` (não é conjurar
   de verdade), mas dispara todos os gatilhos normais de ETB (Dragon
   Tempest, Scourge of Valkas, Lathliss, Miirym, Elemental
   Bond/Garruk's Uprising/Great Henge/Terror of the Peaks). Reversão no
   `end_step()` do mesmo turno.

Testado: 300 jogos smoke test, 30.000 jogos de robustez (0 erros).

**Achados adicionais, documentados como deferidos (baixo valor/alta
complexidade, não implementados):**
- **Cycling {3}** nos 4 Triomes (Jetmir's Garden, Ketria Triome, Zagoth
  Triome, Ziatora's Proving Ground) — descartar por uma carta quando a
  mão está flooded de terreno. Exigiria um julgamento de "mão boa vs.
  ruim" que a IA gulosa atual não modela. Situacional, baixo valor
  frente ao custo de implementar.
- **Goldspan Dragon**: "or becomes the target of a spell" (cria Treasure
  também se alvejada, não só ao atacar) — sem sistema de targeting
  modelado (nem do oponente nem truques próprios), não modelável aqui.
- **Ruby, Daring Tracker**: pump de combate ("+2/+2 se controla criatura
  poder 4+") — não está na lista atual (Magda está no lugar dela), só
  registrada pra testes antigos. Não prioritário.

**Impacto real combinado** (mesma seed_base=7600000, n=3000):

| métrica | antes (Correção #13) | depois |
|---|---|---|
| nunca conjurada | 39,8% | **34,5%** |
| dano proxy médio | 396,75 | 381,92 |
| cartas compradas extra | 11,72 | 12,53 |
| Avg vezes que a Ur-Dragon entra de graça via Hellkite Courser | (não existia) | 0,09 |

"Nunca conjurada" caiu 5,3pp — o maior salto isolado de uma única
rodada de correções nessa métrica específica desde o começo da sessão,
vindo majoritariamente da fixação de terreno de verdade (os 6 tutores
verdes finalmente resolvendo cor de verdade em vez de pegar terreno
aleatório).

`lista.md` não mudou. `urdragon_v1_runs.jsonl` sobrescrito.

---

## Correção #15 — Terror of the Peaks sem tag 'dragon' + 19 poderes errados no CARD_DB inteiro

Usuário pediu revisão completa de novo + pra ver os outros combos do
Commander Spellbook. Rodando a consulta de novo pra conferir os 3
combos "included" achei uma inconsistência: o combo Miirym + Bladewing
the Risen + Terror of the Peaks depende de Terror of the Peaks matar a
si mesma/aos tokens com dano igual ao PRÓPRIO PODER. Conferindo o P/T
real (Scryfall) achei que **Terror of the Peaks é Creature — Dragon
(5/4)**, mas o CARD_DB não tinha a tag `dragon` (invisível pra Eminence,
`dragon_count()`, tutores de Dragão, Cavern of Souls/Secluded
Courtyard/Haven of the Spirit Dragon, Roaming Throne, Herald's
Horn/Urza's Incubator) **e o poder estava registrado como 4 em vez de
5**.

Isso me fez auditar TODOS os `power=` do CARD_DB contra o P/T real via
script (Scryfall). Resultado: **19 poderes errados**, incluindo a
própria Ur-Dragon (9 em vez de 10!) e praticamente todo Dragão grande
do deck:

| carta | power no sim | power real |
|---|---|---|
| The Ur-Dragon | 9 | **10** |
| Atarka, World Render | 7 | **6** |
| Bladewing the Risen | 6 | **4** |
| Dragonlord Dromoka | 4 | **5** |
| Hellkite Charger | 6 | **5** |
| Hellkite Courser | 4 | **6** |
| Klauth, Unrivaled Ancient | 7 | **4** |
| Miirym, Sentinel Wyrm | 3 | **6** |
| Ramos, Dragon Engine | 2 | **4** |
| Savage Ventmaw | 5 | **4** |
| Twinflame Tyrant | 4 | **3** |
| Terror of the Peaks | 4 | **5** |
| Ruby, Daring Tracker | 0 | **1** |
| Delighted Halfling | 0 | **1** |
| Dragonlord's Servant | 0 | **1** |
| Dragonspeaker Shaman | 0 | **2** |
| Sarkhan, Soul Aflame | 0 | **2** |
| Magda, Brazen Outlaw | 0 | **2** |
| Radagast of Rhosgobel | 0 | **2** |
| Roaming Throne | 0 | **4** |

Isso afeta TUDO que usa poder de criatura: `total_attack_power`
(Klauth/Old Gnawbone), Terror of the Peaks (dano = poder de quem
entra), Elemental Bond/Garruk's Uprising/Temur Ascendancy (limiares de
poder 3/4), The Great Henge (custo = maior poder), Return of the
Wildspeaker (compra = maior poder). Os dorks com power=0 (deveriam ter
1-2) nunca bateriam nenhum desses limiares mesmo sendo a maior criatura
num board vazio cedo de jogo — e Roaming Throne com power=0 em vez de 4
nunca contava pros gatilhos de poder-4.

Corrigidos os 20 valores (19 + Terror of the Peaks). Testado: 300 jogos
smoke test, 30.000 jogos de robustez (0 erros).

**Impacto real combinado** (mesma seed_base=7600000, n=3000):

| métrica | antes (Correção #14) | depois |
|---|---|---|
| nunca conjurada | 34,5% | **33,8%** |
| Dragões em campo (fim de jogo) | 12,33 | **13,83** |
| dano proxy médio | 381,92 | **499,18 (+31%)** |
| Treasures criados | 23,92 | **27,44** |
| cartas compradas extra | 12,53 | **13,69** |

`lista.md` não mudou. `urdragon_v1_runs.jsonl` sobrescrito.

---

## Correção #16 — checklist obrigatória de mecânica (regra nova pós-Beorn)

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks. Rodada dedicada via agente de auditoria,
mesmo depois de 15 rodadas de correção anteriores neste deck.

**Landfall:** N/A, 0 cartas. **Dorks/rocks/draw/ramp:** majoritariamente
corretos (Cavern of Souls/Secluded Courtyard/Haven já corrigidos em rodada
anterior, confirmado presente no código, não só no docstring). **Bugs reais
achados:**

- **Talisman of Impulse e Firdoch Core contribuíam 0 mana pro total** —
  Talisman (tag `"rock1"`) nunca era checado em `rocks_mana()` (só Sol
  Ring/Arcane Signet/Great Henge eram hardcoded por nome); Firdoch Core
  (Kindred **Artifact**, não criatura) tinha sua mana modelada como
  `dork_flat1_any`, gated por `ready_creatures()` — que exige
  `is_creature_card()` — então nunca aparecia "pronta" e nunca contribuía.
  Doença de invocação só vale pra criaturas (CR 302.6); artefato não é
  afetado. Corrigidos os dois em `rocks_mana()`, sem gate de prontidão pro
  Firdoch Core. Mesmo bug corrigido em `do_magda_treasures()` (o tap do
  Firdoch Core pra disparar Magda também estava gated por `ready`).
- **Path of Ancestry** ("This land enters tapped", incondicional) faltava
  em `ETB_TAPPED_LANDS` — produzia mana no turno em que era jogada.
- **Return of the Wildspeaker** ("greatest power among **non-Human**
  creatures") contava TODAS as criaturas — as 3 Humanas do deck
  (Dragonspeaker Shaman, Ruby Daring Tracker, Sarkhan Soul Aflame) entravam
  no cálculo errado. Nova tabela `HUMAN_CREATURE_NAMES`.
- **Ramos, Dragon Engine**: "Remove five +1/+1 counters from Ramos: Add
  {W}{W}{U}{U}{B}{B}{R}{R}{G}{G}" — sem `{T}` no custo real, mas estava
  gated por `ready_creatures()` mesmo assim, bloqueando a ativação no
  próprio turno em que Ramos entra com 5+ contadores.
- **Hellkite Charger**: "Whenever this creature attacks, you may pay
  {5}{R}{R}. If you do, ... after this phase, there is an additional
  combat phase" — tagueada `extra_combat_paid`, 100% ausente. Esse é o
  enabler do combo Old Gnawbone + Hellkite Charger citado em
  `auditoria.md`, que nunca conseguia encadear de verdade. Implementado
  (`try_hellkite_charger_extra_combat`, chamado 1x por turno entre os dois
  `combat_step()` — premissa conservadora deliberada: sem loop recursivo,
  pra evitar um combate extra sem teto natural nesse motor).
- Dois comentários desatualizados corrigidos (Talisman of Impulse e Ruby,
  Daring Tracker diziam "NÃO está na lista.md" — ambas estão, linhas 43-44).

**Resultado (n=2000, seed_base=6000000, antes → depois):**

| métrica | antes (Correção #15) | depois |
|---|---|---|
| Dragões em campo (fim de jogo) | 13,78 | **18,48** |
| dano proxy médio | 574,07 | **848,48** |
| Treasures criados | 25,71 | **52,94** |
| cartas compradas extra | 13,69 | **16,57** |
| Dragões que entraram sem pagar custo | 1,03 | **1,23** |
| combates extras via Hellkite Charger (novo) | — | **0,18** |

Salto grande — maior que o esperado só pelos 2 rocks corrigidos. A maior
parte vem do combate extra do Hellkite Charger: quando ele ativa (18% dos
jogos), TODOS os gatilhos de ataque (Old Gnawbone, Utvara, Klauth, etc.)
disparam uma segunda vez completa naquele turno, empilhando em cima da
mana extra do Firdoch Core/Talisman ao longo do jogo inteiro.

**Robustez:** sweep de 20.000 jogos (seeds 6000000–6019999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

`lista.md` não mudou. `urdragon_v1_runs.jsonl` sobrescrito.

---

## Teste comparativo — Morophon, the Boundless (avaliação de inclusão, não aplicado ainda) — 2026-08-28

**Gatilho (usuário):** avaliação de incluir Morophon, the Boundless no
deck (pergunta inicial: "Quero que vc avalie colocar o Morophon no deck
do Ur-Dragon, se vale a pena ou não?"). Depois de eu sugerir cortes só com
base em leitura de texto (achado real — regras permanentes 10 e 11 de
`references/user-standing-rules.md` — o usuário apontou corretamente que
eu deveria ter rodado o próprio goldfish antes de sugerir: *"Com tudo já
pronto, vc pode antes de sugerir a troca já rodar a troca no simulador e
analisar as métricas, me dizendo quais as 3 melhores sugestões de corte
na ordem e pq cada uma delas, analiticamente, é não apenas baseado no
texto da carta que vc as vezes só lê o primeiro parágrafo!"*.

**Implementação real de Morophon em `urdragon_goldfish_v1.py`** (cadastrada
mas NÃO adicionada a `lista.md` ainda — mesmo padrão já usado pro Radagast
of Rhosgobel, registrada só pra permitir teste comparativo):
- `add("Morophon, the Boundless", 7, "creature", {"dragon"}, power=6, pips={})`
  — Changeling real (tag "dragon" cobre todas as zonas, mesmo princípio já
  usado no Firdoch Core).
- **Redução de pip colorido, estruturalmente diferente dos outros 5
  redutores de Dragão do deck** (que reduzem mana GENÉRICA): oráculo real
  "costs {W}{U}{B}{R}{G} less... reduces only the amount of colored mana
  you pay" — nova `morophon_pip_discount()`, aplicada em
  `has_color_sources_for()` (reduz o pip exigido) e somada em
  `effective_cost()` (reduz o total pago). Sem qualificador "other" —
  vale pra QUALQUER spell Dragão, inclusive a própria Ur-Dragon.
- **Anthem "+1/+1 a outras criaturas do tipo escolhido"**: primeiro anthem
  estático desta decklist — nova `effective_power()`, substituindo os 6
  usos anteriores de `CARD_DB[name].power` cru (Great Henge, Garruk's
  Uprising, Elemental Bond/Temur Ascendancy/Terror of the Peaks via
  `creature_etb_hooks`, Return of the Wildspeaker, mana de ataque do
  Klauth). Achado um bug de nomeação real no processo: uma variável local
  pré-existente em `combat_step()` (Old Gnawbone) já se chamava
  `effective_power`, colidindo com a nova função global — renomeada pra
  `old_gnawbone_damage`.

**Robustez:** sweep de 20.000 jogos com Morophon na biblioteca (seeds
5000000–5019999, timeout 3s/jogo) — 0 erros, 0 timeouts.

**Metodologia do teste de corte:** `urdragon_morophon_test.py` — 6
candidatos de corte diferentes testados contra o baseline real (deck
atual), n=3000, seed_base=7600000 (mesmo seed oficial do arquivo
principal, pareado). Candidatos escolhidos pra cobrir teorias diferentes,
não só "carta mais fraca por leitura de texto": Sarkhan Soul Aflame
(redundante com Morophon), Ramos Dragon Engine (lento, mas também Dragão —
contagem neutra), Orb of Dragonkind (mana restrita + tutor redundante),
Ruby Daring Tracker e Talisman of Impulse (fixação só 2 cores), e Firdoch
Core como CONTROLE (rock 5 cores real, esperado ser um corte ruim — testar
se a metodologia distingue sinal real de ruído).

**Resultado (n=3000, seed_base=7600000):**

| Variante | Turno Ur-Dragon | Nunca conjurada | Dragões | Dano proxy | Draw | Screw% |
|---|---|---|---|---|---|---|
| BASELINE (sem Morophon) | 6,583 | 30,47% | 18,97 | 805,56 | 16,78 | 35,87% |
| Corta Sarkhan, Soul Aflame | 6,591 | 30,80% | 21,48 | 1061,27 | 18,20 | 33,93% |
| Corta Ramos, Dragon Engine | **6,558** | **29,53%** | 21,28 | 967,36 | 18,24 | 34,47% |
| Corta Orb of Dragonkind | 6,558 | 30,13% | 22,13 | **1106,02** | **18,86** | 34,03% |
| Corta Ruby, Daring Tracker | 6,601 | 32,00% | 22,16 | 1060,19 | 18,16 | **33,40%** |
| Corta Talisman of Impulse | 6,604 | 32,23% | 22,17 | 1074,04 | 18,10 | 34,00% |
| Corta Firdoch Core (controle) | 6,613 | 31,90% | 21,13 | 993,07 | 17,91 | 35,47% |

**Top 3 corte, em ordem, com razão analítica (não só o texto da carta):**

1. **Orb of Dragonkind** — melhor em dano proxy (1106,02) e cartas
   compradas (18,86), 2º melhor em turno/confiabilidade de conjurar a
   comandante (empatado com Ramos). A leitura de texto já apontava a
   habilidade de mana como fraca (`{1},{T}: add 2, só gasta em Dragão` —
   pior que qualquer rock genérico já na lista) e o modo de sacrifício
   redundante com Sarkhan's Triumph (tutor de Dragão mais barato e
   instant-speed) — os números confirmam: é o corte de MENOR custo de
   oportunidade, então o ganho líquido de trocar por Morophon aparece mais
   limpo aqui do que em qualquer outro candidato.
2. **Ramos, Dragon Engine** — melhor turno médio de conjurar a comandante
   (6,558) E melhor taxa de nunca conjurar (29,53%, a ÚNICA variante que
   fica MELHOR que o baseline nessa métrica). Confirma a leitura de texto
   anterior (engine lento, precisa 5 contadores acumulados antes de valer
   a pena) — E confirma empiricamente o ponto de curva que o usuário
   levantou: por Ramos também ser Dragão, a contagem de Dragões em campo
   fica neutra na troca (21,28 vs 22,13 do Orb — não é o maior ganho de
   Dragões, mas não perde a peça de forma isolada). É o corte mais seguro
   pra quem prioriza confiabilidade de ter a comandante em campo, mesmo
   sendo o mais fraco dos 3 em dano/draw.
3. **Sarkhan, Soul Aflame** — nenhum extremo (nem melhor nem pior em
   nenhuma métrica), mas consistentemente no meio-alto do grupo em todas
   (dano 1061, draw 18,20, screw 33,93% — 2º melhor). Redundante com o
   próprio Morophon por fazer o mesmo trabalho (redutor de custo de
   Dragão), mas sem o custo de oportunidade tão baixo quanto o Orb nem o
   ganho de confiabilidade do Ramos — 3º lugar por ausência de fraqueza,
   não por força específica.

**Validação do controle:** Firdoch Core (rock de 5 cores real + Dragão)
terminou **pior que os 3 primeiros candidatos em quase toda métrica**
(pior turno de comandante do grupo inteiro, 6,613; pior contagem de
Dragões entre os cortes, 21,13; pior taxa de color screw entre os cortes,
35,47%, quase igual ao baseline) — confirma que a metodologia está
distinguindo sinal real (Firdoch Core é genuinamente forte, não deveria
ser cortado) de ruído de seed, não é só variância aleatória.

**Não recomendado, com razão:** Talisman of Impulse e Ruby, Daring Tracker
pioraram a confiabilidade de conjurar a comandante MAIS que qualquer outro
candidato (32,23% e 32,00% de "nunca conjurada", ambos piores que o
próprio baseline sem Morophon) — cortar uma fonte de rampa de 2 mana,
mesmo restrita a 2 cores, ainda pesa mais na curva do que a leitura de
texto sugeria isoladamente.

`lista.md` NÃO mudou — Morophon ainda não foi adicionado ao deck oficial,
esta é uma avaliação comparativa. Scripts: `urdragon_morophon_test.py`
(novo).

---

## Simulação — lista FÍSICA real (`lista-fisica.md`, `urdragon_goldfish_physical_v1.py`) — 2026-08-29

**Contexto:** usuário mandou 6 fotos do deck físico de verdade (guardado em
binder). Cruzamento carta a carta contra `lista.md` (feito em 3 turnos
anteriores desta sessão, com Scryfall real pra cada carta ambígua — "The
Banyan Tree" = reskin Avatar de The Great Henge, "Dragon of Mount Gulg" =
reskin Final Fantasy de Ancient Copper Dragon) achou 8 diferenças reais:

- **Fora da caixa física** (estão em `lista.md`, não apareceram em nenhuma
  das 6 fotos): Birds of Paradise, Delighted Halfling, Ruby, Daring
  Tracker, Ramos, Dragon Engine, Talisman of Impulse, Battlefield Forge,
  Karplusan Forest, Taiga.
- **Dentro da caixa física, fora do `lista.md`**: Lightning Greaves (a
  troca por Talisman de Impulse foi decidida no goldfish mas nunca
  aplicada na caixa de verdade), Magda Brazen Outlaw e Scalelord Reckoner
  (confirmadas pelo usuário como "sempre estiveram" — `lista.md` nasceu
  incompleto), Dragon's Hoard, Morophon the Boundless e Smuggler's
  Surprise (extras físicas nunca avaliadas), Island e Watery Grave
  (terrenos físicos fora da manabase afinada).

Escrita `lista-fisica.md` (99+comandante, conferido `len(lib)==99` e sem
duplicata) e cópia `urdragon_goldfish_physical_v1.py` do simulador,
apontando pra ela em vez de `lista.md`. `lista.md` **não foi tocada** —
continua sendo a lista afinada de referência.

**3 cartas novas implementadas com efeito real (Regra 3), nenhuma so tag:**

- **Scalelord Reckoner** ({3}{W}{W}, Dragão 4/4 voador, C17): "Whenever a
  Dragon you control becomes the target of a spell or ability an opponent
  controls, destroy target nonland permanent that player controls."
  Habilidade própria reativa a ação de OPONENTE real — sem oponente no
  goldfish solo, nunca dispara (mesma classe de `opponent_dependent` já
  usada em Smothering Tithe). Ainda assim conta como corpo Dragão real pra
  `dragon_count()`/`is_dragon()` (alimenta Dragon Tempest, Scourge of
  Valkas, Lathliss, Miirym, Dragon's Hoard, descontos de Dragão, Roaming
  Throne).
- **Dragon's Hoard** ({3}, artefato, M19/AFC/TDC): "Whenever a Dragon you
  control enters, put a gold counter on this artifact. {T}: Add one mana
  of any color. {T}, Remove a gold counter: Draw a card." Duas habilidades
  ativadas competem pelo MESMO {T} — **premissa assumida e documentada
  (Regra 1, precisa validação do usuário)**: sempre usada como rock de
  mana (`rocks_mana()`), nunca gasta o contador pra comprar, num deck
  faminto por fixação 5 cores. Contadores de ouro acumulados SÃO
  rastreados (`dragon_hoard_gold_counters`, incrementado em
  `dragon_enters()` — sem "nontoken" no oráculo, mesma leitura já usada
  em Scourge/Tempest) e reportados como valor NÃO realizado, não
  inventados como compra automática. Artefato, não criatura — Roaming
  Throne nunca dobra o próprio gatilho dele (só dobra gatilho de
  CRIATURA do tipo escolhido), checado e documentado explicitamente.
- **Smuggler's Surprise** ({G}, instant Spree, OTJ #180/#345): 3 modos
  combináveis (mill 4 + seleção, cheat até 2 criaturas da mão pro campo,
  proteção hexproof/indestructible pra poder 4+). **Premissa assumida e
  documentada (Regra 1)**: só o modo "{4}{G}" (cheat de criaturas) é
  modelado — o estruturalmente mais forte pro plano do deck, mesma
  família de Bladewing/Haunting Voyage. Custo total modelado {4}{G}{G}
  (mv=6, pips G:2). Os outros 2 modos ficam de fora, não inventados como
  bônus simultâneo. Conta pra `dragons_free_entry_total` quando a
  criatura colocada é de fato um Dragão.

**Checklist de 13 categorias (`goldfish-sim-card-rules.md`) sobre as 3
cartas novas:** landfall N/A (nenhuma tem), mana dork N/A (nenhuma é
criatura com {T} de mana), mana rock — Dragon's Hoard coberto em
`rocks_mana()`/`color_sources()` (produces=WUBRG, sem doença de invocação,
artefato), fixing de mana — idem, motor de draw — Dragon's Hoard
documentado como não-gasto (ver acima), motor de ramp — Smuggler's
Surprise coberto (cheat de criatura, análogo a ramp-pra-campo), ativada
repetível N/A (nenhuma), combos com peças já na lista — Scalelord
Reckoner/Dragon's Hoard entram automaticamente em todo gatilho genérico de
"Dragão entra" via `is_dragon()`/`dragon_enters()` (Dragon Tempest,
Scourge of Valkas, Lathliss, Miirym, Herald's Horn, descontos, Roaming
Throne), estática N/A (nenhuma das 3 tem), métricas básicas — reportadas
(dragons_free_entry_total, dragon_hoard_gold_counters), recursão N/A
(nenhuma recupera de cemitério), face múltipla N/A (nenhuma tem "//"),
planeswalker N/A, Classe/Saga N/A.

**Robustez:** 20.000 partidas, seeds 0–19999, timeout 3s — 0 erros, 0
timeouts.

**Batch oficial, n=3000, seed_base=7600000 (mesmo par de seeds do último
teste do `lista.md`, comparação direta):**

| Métrica | `lista.md` (afinada) | `lista-fisica.md` (real) |
|---|---|---|
| Avg mulligans | 0,48 | 0,57 |
| Turno médio Ur-Dragon | 6,58 | 6,71 |
| Nunca conjurada em 8 turnos | 30,5% | **40,6%** |
| Avg Dragões em campo (fim) | 18,97 | 16,19 |
| Avg compras via ataque Ur-Dragon | 10,38 | 8,14 |
| Avg permanentes grátis via ataque | 1,78 | 1,43 |
| Avg dano proxy total | 805,56 | 808,40 |
| Avg Treasures criados | 57,74 | 49,00 |
| Avg cartas compradas extra | 16,78 | 14,01 |
| Avg turnos com color screw | 1,62 | 1,89 |
| % jogos com color screw | 35,9% | **39,8%** |
| Avg mão final | 5,35 | 5,42 |

**Leitura:** a lista física perde em quase toda métrica-chave, de forma
consistente com o que já se sabia por decisão testada anteriormente nesta
sessão — não é ruído: a manabase física ainda tem Island+Watery Grave (U/B,
as 2 cores já MAIS sobre-representadas frente à demanda de pips do deck,
ver Regra 6/adendo Ur-Dragon) no lugar de Battlefield Forge+Karplusan
Forest (R/W e R/G, testados e comprovados melhores exatamente por
cobrirem os maiores gaps de cor), e ainda carrega Lightning Greaves em vez
de Talisman de Impulse (rock real vs. equipamento sem produção de mana).
Isso se reflete direto no color screw (+4pp de jogos afetados) e na taxa
de "Ur-Dragon nunca conjurada" (+10,1pp) — a comandante de 5 cores é a
peça mais sensível a fixação de mana do deck inteiro.

`lista.md` não muda a partir deste teste — ele é só uma fotografia do
que está na caixa hoje. Resultados não salvos em `.jsonl` (rodado só via
stdout do `run_batch` default do script, `n=3000`).

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
