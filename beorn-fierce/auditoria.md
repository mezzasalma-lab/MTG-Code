# Auditoria — Beorn the Fierce (Mono-Verde)

Auditoria feita via skill `mtg-commander`, dados em tempo real do Scryfall. Cruzada com os 5 goldfishes já registrados em `goldfish-log.md`.
Data: 2026-08-20

---

## 1. Validação formal

| Check | Resultado |
|---|---|
| Total de cartas | **100** (99 + comandante) ✅ |
| Singleton | ✅ nenhuma duplicata |
| Identidade de cor (mono-G) | ✅ nenhuma violação |
| Cartas banidas em Commander | ✅ nenhuma |
| Erros de grafia/cartas não encontradas | ✅ nenhuma |

**Comandante:** Beorn the Fierce — `{3}{G}{G}` — Legendary Creature Bear Shapeshifter Warrior.
Trample; dá +2/+2 a outros Ursos; a cada combate converte uma criatura sua em Urso com contador de trample; compra 2 cartas se você controla 3+ Ursos.

---

## 2. Base de mana

- **Terrenos: 38** (33 Forest + Nykthos, Yavimaya Cradle of Growth, War Room, Scavenger Grounds, Bala Ged Recovery//Sanctuary) — no topo do ideal (36-38), levemente alto, mas coerente com a curva pesada do deck.
- Sendo mono-verde, fixação de cor é praticamente um não-problema. Yavimaya, Cradle of Growth transforma todo terreno em Forest, o que é redundante para cor mas ajuda devoção e sinergias de "Forest entering" (Necklace of Girion).
- **Nykthos, Shrine to Nyx** é uma inclusão inteligente — o deck tem bastante pip pesado de verde (Archdruid's Charm `{G}{G}{G}`, Ayula's Influence `{G}{G}{G}`, Ezuri's Predation `{G}{G}{G}`, Tribute to the World Tree `{G}{G}{G}`, Unnatural Growth `{G}{G}{G}{G}`), então devoção alta é realista.
- War Room e Scavenger Grounds trocam uma fonte de mana por utilidade (draw genérico e graveyard hate) — aceitável em mono-cor.

---

## 3. Curva de mana

CMC médio (sem terrenos, sem comandante): **3.82** — acima do ideal recomendado (2.5–3.5), puxado pelo topo pesado.

| CMC | Qtde |
|---|---|
| 1 | 5 |
| 2 | 11 |
| 3 | 17 |
| 4 | 10 |
| 5 | 9 |
| 6 | 3 |
| 7 | 1 |
| 8 | 3 (Craterhoof Behemoth, Ezuri's Predation, Last March of the Ents) |
| 9 | 1 (The Great Henge — custo nominal, mas reduz via maior poder em campo) |
| 12 | 1 (Ghalta, Primal Hunger — reduz {X} pelo poder total do seu board, frequentemente jogável por poucos manas) |

**Leitura real:** a curva nominal é mais pesada que o ideal, mas boa parte do topo (Great Henge, Ghalta, Defiler of Vigor reduzindo spells verdes, Goreclaw reduzindo criaturas poder 4+, Radagast, Emerald Medallion) tem redução de custo condicional — bate com o que os goldfishes mostraram: Craterhoof e companhia normalmente resolvem antes do CMC nominal sugerir. Ainda assim, vale considerar 1-2 cortes no topo se a mesa for mais rápida que Bracket 3.

---

## 4. Ramp — MUITO acima do necessário (~15 peças)

**Mana direto:** Birds of Paradise, Llanowar Elves, Sol Ring, Lotus Cobra, Selvala Heart of the Wilds, Herd Heirloom, Firdoch Core, Necklace of Girion, Patchwork Banner (9)
**Busca/rampa de terreno:** Cultivate, Sakura-Tribe Elder, Three Visits, Solemn Simulacrum (4)
**Redução de custo:** Emerald Medallion, Radagast of Rhosgobel, Defiler of Vigor, Goreclaw (4, parcial/condicional)

Isso é bem acima do teto recomendado até para Bracket 4 (12+). Combinado com 38 terrenos, o deck tem excesso de mana disponível — dá pra considerar cortar 1-2 peças de ramp redundante (ex: Necklace of Girion, que é lento e faz pouco além de +1/+1 counters) por mais interação.

---

## 5. Card draw — MUITO acima do necessário (~13-14 fontes)

Beast Whisperer, Garruk's Uprising, Ohran Frostfang, Toski Bearer of Secrets, Return of the Wildspeaker, Shamanic Revelation, Selvala (condicional), The Great Henge, Herd Heirloom (condicional), Tireless Tracker, Chronicle of Victory, Solemn Simulacrum, Last March of the Ents, além do próprio Beorn (draw 2 com 3+ Ursos).

Excelente resiliência a mão vazia — bate com os goldfishes, que mostraram o deck raramente travando por falta de gás.

---

## 6. Remoção — ⚠️ PONTO CRÍTICO (confirma exatamente o que você observou nos goldfishes)

| Carta | Função |
|---|---|
| Beast Within | Destrói qualquer permanente (dá 3/3 ao oponente) |
| Song of the Dryads | Transforma permanente em Forest (pseudo-remoção) |
| Archdruid's Charm | Modal — um dos modos é fight |
| Ezuri's Predation | Fight em massa contra todas as criaturas oponentes (mini-wipe) |
| Haywire Mite | Só artefato/encantamento não-criatura |

**Total real: 5 cartas**, e nenhuma é um wipe "limpo" — dependem de combate/fight (arriscado se seu board for mais fraco que o do alvo) ou dão um corpo de volta ao oponente (Beast Within). **Não há:**
- Remoção instantânea "exile" clássica (Swords to Plowshares, Path to Exile, Beast Within à parte)
- Wipe de verdade (Wrath-like)
- Remoção dedicada de planeswalker

Isso é **bem abaixo** do recomendado (8-10 remoção pontual + 2-3 wipes) e é o maior gap estrutural do deck. Seus próprios goldfishes nunca testaram essas 5 cartas contra ameaças reais porque, jogando sozinho, não há o que remover — mas numa mesa real isso vai aparecer rápido como o ponto fraco.

---

## 7. Proteção — 7 peças ✅

Heroic Intervention, Lightning Greaves, Chameleon Colossus (proteção de preto), Toski (indestructible), Obscuring Haze (fog grátis com comandante em campo), Gigantic Big Bear (hexproof), Allosaurus Shepherd (seus feitiços verdes não podem ser contra-atacados).

Boa cobertura para proteger o board de wipes/remoção alheia enquanto ele cresce.

---

## 8. Win conditions — muito bem resolvidas

- **Craterhoof Behemoth** — confirmado no Jogo 5 como fechador real (85+ poder disponível).
- **Unnatural Growth** — dobra poder/resistência a cada combate; com o board que esse deck monta, provavelmente mata em 1-2 combates.
- **Ghalta, Primal Hunger** — ameaça de 12 mana virando praticamente grátis com o board cheio de poder.
- **Genji Glove** — combate extra + double strike; **nunca testado nos goldfishes**. Combinado com um Urso grande (via Beorn/Ayula) ou com Toski (draw por dano de combate), essa é provavelmente a linha de fechamento mais explosiva do deck e vale simular especificamente.
- **The Great Henge** — motor de valor que também vira quase grátis com um creature grande em campo.
- **Titania's Command / Last March of the Ents** — geram board/pressão adicional.

---

## 9. Sinergia com o tema Urso / +1+1 counters

Construção tribal muito bem pensada em um "tipo de criatura" que normalmente não existe como tema real:

- **Beorn the Fierce** é o motor central: converte 1 criatura por combate em Urso (ganhando trample) e dá +2/+2 a todos os outros Ursos.
- **Ayula, Queen Among Bears** e **Little Bear** têm gatilhos que só disparam com Ursos — recompensando diretamente o que Beorn cria.
- **Habilitadores universais de tipo** (Maskwood Nexus, Chameleon Colossus, Firdoch Core, Springleaf Parade) fazem qualquer criatura — inclusive tokens — contar como Urso, multiplicando os gatilhos de Ayula/Beorn mesmo sem Ursos "de verdade" no deck.
- **Patchwork Banner, Chronicle of Victory e Roaming Throne** podem escolher "Bear" como tipo, empilhando anthem + card draw + gatilhos duplicados especificamente na sua sinergia central.
- **Contadores de +1/+1** têm um segundo eixo de sinergia (Forgotten Ancient, Germination Practicum, Tribute to the World Tree, Titania's Command, Necklace of Girion) que se conecta ao primeiro porque Little Bear e Beorn's Hospitality colocam contadores especificamente em Ursos.

Isso não é um goodstuff pile — é um deck tribal real com um payoff (Beorn) muito bem casado com os habilitadores.

---

## 10. Cruzamento com os goldfishes

| Padrão observado | Confirmado pela auditoria? |
|---|---|
| Beorn chega turnos 4-7 de forma consistente | ✅ CMC 5 do comandante + ~15 peças de ramp tornam isso esperado |
| Craterhoof fecha jogo quando resolve | ✅ é literalmente a win condition mais direta do deck |
| Pouco teste de remoção | ✅ confirmado estruturalmente — só 5 cartas de remoção no deck todo, é normal que apareçam pouco em goldfish solo |
| Genji Glove nunca testado | ⚠️ vale simular — é a única linha "combo-ish" do deck e pode ser um fechador mais rápido que esperar por Craterhoof |

---

## 11. Estimativa de Bracket

**Bracket 3.**

A favor de poder alto: Sol Ring, Craterhoof, The Great Henge, Ghalta praticamente de graça, motor de ramp/draw muito acima da média.
Contra Bracket 4/cEDH: nenhum fast mana além do Sol Ring, sem tutores de combo, e principalmente — **quase nenhuma interação**. Um deck Bracket 4 real precisa conseguir responder a ameaças alheias tão rápido quanto desenvolve as próprias; aqui, o plano é puramente "eu monto meu board e ataco", o que é ótimo em mesas mais lentas/casuais (Bracket 3) mas se torna uma fraqueza clara contra decks que interagem ou contra board wipes.

---

## 12. Sugestões de melhoria (prioridade)

1. **Adicionar remoção real** — trocar 2-3 peças de ramp redundante (ex: Necklace of Girion) por: Beast Within *(já tem)*, Ranger's Guile-like proteção não conta; sugerir **Pounce**, **Rabid Bite**, **Return to Nature**, ou (se orçamento permitir) **Vindicate**/**Krosan Grip** para artefato/encantamento dedicado.
2. **Um wipe assimétrico** ajudaria muito — algo como **Roiling Vortex** não é verde; considerar **Beast Within** já cobre parcialmente, mas um efeito tipo **Return of the Wildspeaker**-adjacent que limpe o board sem te prejudicar (ex: **Aftershock**, **Pyroclasm** não são verdes — em mono-verde a opção realista é **Fungal Plots**/**Wrath of the Skies** não existem; a melhor rota mono-verde é dobrar em fight-based removal: **Prey Upon**, **Ram Through**, ou cartas de "destroy target creature with power X or less" via combate).
3. **Testar a linha do Genji Glove** especificamente — parece a forma mais rápida de fechar jogo via dano de combate dobrado, e está sem dados nos seus goldfishes.
4. **Considerar cortar 1 terreno** (38→37) já que o ramp é muito denso; útil para encaixar uma peça extra de remoção sem desidratar a curva.

---

## Links

- EDHREC: https://edhrec.com/commanders/beorn-the-fierce
- Tribo Urso: https://edhrec.com/tribes/bear
- Moxfield (criar/comparar): https://moxfield.com/decks/new
