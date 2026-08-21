# Auditoria — Thranduil, the Elvenking (Sultai — B/G/U)

Auditoria feita via skill `mtg-commander`, dados em tempo real do Scryfall.
Data: 2026-08-20
Última atualização (rebalanceada de remoção/desenvolvimento, seção 6 e 4): 2026-08-21

---

## 1. Validação formal

| Check | Resultado |
|---|---|
| Total de cartas | **100** (99 + comandante) ✅ |
| Singleton | ✅ nenhuma duplicata (exceto básicas) |
| Identidade de cor (B/G/U) | ✅ nenhuma violação — todas as 91 cartas dentro da identidade |
| Cartas banidas em Commander | ✅ nenhuma |
| Cartas não encontradas/erros de grafia | ✅ nenhuma — todas resolvidas no Scryfall |

**Comandante:** Thranduil, the Elvenking — `{2}{B}{G}{U}` — Legendary Creature Elf Noble.
Identidade de cor confirmada: **B/G/U (Sultai)**.

---

## 2. Base de mana

- **Terrenos: 37** (dentro do ideal de 36–38 para curva normal) ✅
  - Inclui 2 MDFCs contados como terreno (Malakir Rebirth, Revitalizing Repast) — na prática funcionam como ~36 terrenos "puros" + flexibilidade.
- Fixação: Command Tower, Cavern of Souls, Reflecting Pool, Three Tree City, Yavimaya Cradle of Growth, Zagoth Triome, shocklands (Breeding Pool, Overgrown Tomb, Watery Grave) — boa qualidade para Bracket 3–4.

**Distribuição de fontes de cor (aprox.):**

| Cor | Pips no deck | Fontes de terreno | Situação |
|---|---|---|---|
| G (verde) | 57 | ~22 hard + flex | Cor primária, bem suportada |
| B (preto) | 23 | ~15 hard + flex | Cor secundária, adequada |
| U (azul) | 11 | **~9 hard** + flex | ⚠️ **claramente a mais fraca** |

**Ponto de atenção:** azul tem só **1 Island básica** e nenhum fetch/tutor de terreno. Isso é um risco real porque:
- O próprio comandante precisa de `{U}` no turno em que for conjurado.
- Elrond, Moon-Reader tem ativação `{5}{U}{U}` (duplo azul).
- Maralen, Fae Ascendant custa `{2}{B}{G}{U}` (as três cores).
- Rhystic Study precisa de `{U}` cedo para ser eficiente.

**Correção aplicada — 2026-08-21: Llanowar Wastes trocado por Underground River.** Llanowar Wastes (`{T}: Add {C}` / `{T}: Add {B} or {G}. Causa 1 dano a você`) era 1 dos 7 terrenos do deck que só tocavam B/G, cor já bem suprida. Underground River é a mesma painland (sempre destapada, sem condição), só que B/U (`{T}: Add {U} or {B}. Causa 1 dano a você`) — verificado via Scryfall, legal em Commander, `$2,43`. Fontes de U sobem de 10 pra **11**, sem tirar terreno nenhum do total (37 mantido) nem reduzir B (ainda 12 fontes via as outras 6 duais B/G + Underground River). Confirmado nos 2000 goldfishes: blue screw caiu de **11,9% → 8,4%** das partidas, avg turnos com screw caiu de 0,32 → 0,23 (`goldfish-log.md`, seção "Fonte de U — Underground River no lugar de Llanowar Wastes"). Ainda vale considerar mais 1-2 trocas similares (item 3, seção 12) se quiser reduzir mais.

**Segunda correção aplicada — 2026-08-21: Formidable Speaker trocado por Arcane Signet.** Testados 4 candidatos antes de decidir (Arcane Signet, Chromatic Lantern, Urza's Incubator, The World Tree — este último **ilegal** na identidade B/G/U, `color_identity` do Scryfall inclui R/W pelo custo de sacrifício). Arcane Signet (`{2}`, `T: Add one mana of any color in your commander's color identity`, sempre destapado) venceu Chromatic Lantern (mesmo efeito, mas 1 mana mais caro e 1 turno mais lento) e goleou Urza's Incubator (só reduz custo genérico, não ataca o gargalo real de cor — ganho de +0,3pp contra +3,7pp do Signet em T4). Thranduil's Company **não foi considerado** pra corte, vetado permanentemente pelo usuário (ver `references/user-standing-rules.md`, regra 5).

---

## 3. Curva de mana

CMC médio (sem terrenos, sem comandante): **3.32** — dentro do ideal (2.5–3.5) para Bracket 3–4. ✅

| CMC | Qtde |
|---|---|
| 1 | 6 |
| 2 | 13 |
| 3 | 18 |
| 4 | 14 |
| 5 | 6 |
| 6 | 2 |
| 7 | 2 |
| 8 | 1 |

Curva saudável, pico em 3, topo curto (só 3 cartas acima de CMC 6). Bom para um deck que quer jogar sua base de elfos cedo e escalar.

---

## 4. Ramp — 15 peças ✅ (acima do mínimo de 10–12 do Bracket 3)

Arbor Elf, Bloom Tender, Deathbloom Ritualist, **Devoted Druid** (`{1}{G}`, `{T}: Add {G}` + `Put a -1/-1 counter on this creature: Untap this creature` — dork com pseudo-ramp extra em turnos que não precisa atacar, e a habilidade de untap é herdável pelo Thranduil via GY), Elves of Deep Shadow, Elvish Archdruid, Elvish Mystic, Gwenna Eyes of Gaea, Incubation Druid, Llanowar Elves, Marwyn the Nurturer, Priest of Titania, Selvala Heart of the Wilds, Sol Ring, Wirewood Channeler.

Ponto forte real do deck: quase todo dork escala com a quantidade de elfos em campo (Priest of Titania, Elvish Archdruid, Wirewood Channeler), então o ramp cresce exponencialmente conforme a estratégia tribal avança.

---

## 5. Card draw — ~9 fontes (na faixa do mínimo recomendado)

Rhystic Study, Beast Whisperer, Champions of the Perfect, Edric Spymaster of Trest, Elrond Moon-Reader, Glissa Sunslayer (modal), Harmonized Crescendo, Underrealm Lich (filtragem), além do próprio Thranduil (draw 2/discard 1 a cada elfo lendário que entra).

Adequado, mas depende bastante de gatilhos (criar criatura, dano de combate) — pouco draw "incondicional" fora do Rhystic Study.

---

## 6. Remoção — corrigido após validação com os 2000 goldfishes

**Correção do original:** esta seção recomendava trocar cartas por "Beast Within, Chaos Warp, Vindicate, Deadly Rollick". Chaos Warp (`{2}{R}`) e Vindicate (`{1}{W}{B}`) **não são Sultai** — nem sequer legais na identidade de cor B/G/U do Thranduil. Erro do texto original, verificado via `color_identity` do Scryfall antes de aplicar qualquer troca.

**Troca real aplicada, primeira versão** (0,52 → **1,11** remoção conjurada em média, confirmado nos 2000 goldfishes):
- **Cortadas:** Agatha's Soul Cauldron, Oversold Cemetery, Harmonized Crescendo.
- **Adicionadas** (verificadas via Scryfall, todas legais em B/G/U):
  - **Deadly Rollick** (`{3}{B}`, ou `{1}{B}` se você controla um comandante — quase sempre o caso): `Exile target creature.`
  - **Putrefy** (`{1}{B}{G}`): `Destroy target artifact or creature.` — cobre a lacuna de remoção de artefato.
  - **Feed the Swarm** (`{1}{B}`): `Destroy target creature or enchantment an opponent controls. You lose life equal to that permanent's mana value.` — cobre a lacuna de remoção de encantamento.

**Correção — Agatha's Soul Cauldron e Oversold Cemetery voltaram pro deck.** Os dois foram cortados na versão acima com uma leitura errada: ambos dependiam supostamente do volume de *Elfos* na GY (que é baixo, ~0,7-1,0/partida). Isso está errado nos dois casos:
- **Agatha's Soul Cauldron** — `"{T}: Exile target card from a graveyard"` não exige que seja SEU cemitério nem que seja Elfo — é hate de cemitério real contra qualquer oponente, independente da densidade de Elfos.
- **Oversold Cemetery** — `"if you have four or more CREATURE cards in your graveyard"` não exige Elfo, só criaturas (qualquer tipo). Buried Alive sozinho já manda 3 pro cemitério de um golpe.

**Cortes reais que entraram no lugar delas:** Eclipsed Elf (seleção de carta pontual, sem sinergia de GY, sem habilidade herdável pela Thranduil) e Lys Alana Huntmaster (token maker redundante com Elvish Warmaster/Lathril, dominado estritamente por Imperious Perfect — ver seção 12).

**Segunda rebalanceada — 2026-08-21: Feed the Swarm e Putrefy cortados, Devoted Druid/Imperious Perfect/Formidable Speaker entraram no lugar delas + Urza's Incubator.** Pedido direto do usuário, sem correção de leitura errada desta vez — troca deliberada de 2 remoções por 2 peças de desenvolvimento de board e 1 mana dork. Urza's Incubator (artefato redutor de custo, não é remoção) saiu pra abrir a terceira vaga.

| Tipo | Cartas | Qtde |
|---|---|---|
| Remoção pontual | Assassin's Trophy, Awaken the Honored Dead, Trystan's Command (modal) | 3 |
| Edict repetível | Ruthless Winnower (stax leve, edict toda upkeep) | 1 |
| Wipe assimétrico | Kindred Dominance (destrói tudo que não é do tipo escolhido), Raise the Palisade (bounce assimétrico) | 2 |
| GY hate (interação, não remoção de ameaça em campo) | Agatha's Soul Cauldron | 1 |

**Total real: 8 efeitos** — ainda dentro da faixa recomendada (8–10) pra Bracket 3–4, mas agora no piso da faixa, não mais no meio dela. Confirmado nos 2000 goldfishes pós-corte: **1,11 → 0,78** remoção conjurada em média (`goldfish-log.md`, seção "Rebalanceada da lista — 3 cortes / 3 adições"). Sem Feed the Swarm, remoção de encantamento fica só com Glissa Sunslayer (condicional, precisa conectar dano de combate) e Awaken cap. I (`destroy target nonland permanent`, cobre qualquer tipo mas é conjuração única). Sem Putrefy, remoção de artefato fica só com Assassin's Trophy (`destroy target permanent`, não restrito a criatura) — cobertura ainda existe, só não é mais redundante.

**Awaken the Honored Dead ({B}{G}{U}) avaliada e mantida** — é a única peça de remoção do deck que pede as 3 cores simultâneas (nenhuma outra passa de 2 cores). Simulação dedicada (n=3000) mostrou B+G+U disponíveis simultaneamente em campo em 75,2% dos jogos até o turno 3 e 85,1% até o turno 5 (modelo otimista — ignora terreno-entra-tapado, ver ressalva no cabeçalho de `thranduil_goldfish_v1.py`). Por ser Saga de conjuração única, atraso não desperdiça valor. Não foi cortada, mas é a peça de interação mais frágil de cor do deck — ligada ao mesmo problema de azul já sinalizado no item 3 da seção 12 (nunca corrigido).

---

## 7. Proteção — 7 peças ✅

Heroic Intervention, Lightning Greaves, Iron-Shield Elf, Selfless Safewright, Revitalizing Repast, Tyvar the Pummeler, Underrealm Lich (indestructible pago em vida).

Boa cobertura — importante porque o motor de valor (elfos lendários entrando) é alvo óbvio de remoção do oponente.

---

## 8. Win conditions

**Correção (re-varredura de `oracle_text` de todas as 91 cartas, feita depois desta auditoria original):** a versão anterior desta seção dizia que o deck não tinha nenhum efeito de overrun. Isso estava errado — o deck tem **quatro** efeitos de pump em massa repetíveis, só que nenhum é um "Craterhoof" clássico de cast único:

- **Tyvar, the Pummeler** — `{3}{G}{G}: Creatures you control get +X/+X until end of turn, where X is the greatest power among creatures you control.` Overrun repetível de verdade, ativável todo turno que tiver mana.
- **Ezuri, Renegade Leader** — `{2}{G}{G}{G}: Elf creatures you control get +3/+3 and gain trample until end of turn.` Segundo overrun repetível, específico pra Elfos (a maioria do board).
- **Elvish Warmaster** — `{5}{G}{G}: Elves you control get +2/+2 and gain deathtouch until end of turn.` Terceiro pump repetível, deathtouch vira remoção via combate.
- **Jarad, Golgari Lich Lord** — `{1}{B}{G}, Sacrifice another creature: Each opponent loses life equal to the sacrificed creature's power.` Dreno repetível via sacrifício — ótimo pra descartar excesso de tokens de Elfo em dano direto.
- **Lathril, Blade of the Elves** — `{T}, Tap ten untapped Elves you control: Each opponent loses 10 life and you gain 10 life.` — dreno de 10, exige 10 Elfos destapados (alcançável com o motor de tokens).
- **Finale of Devastation** (X≥10) e **Kindred Summons / Bloodline Bidding** — burst de reforço/reanimação em massa (não são dano direto, mas destravam alpha strikes o mesmo turno via os pumps acima).
- Anthems empilhados (Elvish Archdruid, Thranduil Sindarin Liege, contadores da Immaculate Magistrate/Arwen) sustentam o tamanho base do board entre um pump e outro.

**Sugestão de melhoria revisada:** como o deck já tem 3 overruns repetíveis (Tyvar, Ezuri, Warmaster) fazendo o trabalho de um Craterhoof, a recomendação de "adicionar overrun" da versão anterior não é mais prioritária — o gargalo real é chegar em mana suficiente pra ativar essas habilidades (todas custam 4-7 mana) no mesmo turno que o board já está largo, não falta de efeito de fechamento.

---

## 9. Tutores

Fauna Shaman, Buried Alive (setup para reanimação), Finale of Devastation, Prime Speaker Vannifar (pod). Bom toolbox para Bracket 3.

---

## 10. Sinergia com o tema Elfos/Thranduil

Excelente coesão tribal — não é um goodstuff pile:

- **~15 Elfos lendários** no deck (Arwen, Dionus, Eladamri, Elrond, Glissa, High Perfect Morcant, Jarad, Lathril, Marwyn, Maralen, Selvala, Thranduil Sindarin Liege, Trystan, Tyvar Bellicose, Tyvar the Pummeler, Prime Speaker Vannifar) — cada um que entra dispara o "draw 2, discard 1" do comandante. Densidade muito acima da média.
- **Correção (via os 2000 goldfishes com combat_step e draw engines implementados):** esta seção dizia que a habilidade de herdar ativações de Elfos na GY "não é decorativa, é jogável". Os dados não sustentam isso tão bem quanto o texto original sugeria — a simulação mostra **média de ~0,7-1,0 Elfo milhado pro cemitério por partida** (proxy estatístico, não é contagem exata carta-por-carta, mas a ordem de grandeza é clara). As ferramentas de mill existem (Buried Alive, Trystan/Lluwen, Takenuma channel, Silvan Rally), mas o volume real que chega na GY numa partida de 8 turnos é baixo. Não é decorativa, mas também não é um plano B confiável — trate como upside ocasional, não como pilar da estratégia. Não removi as peças de mill (a maioria tem utilidade própria além de encher a GY), mas não priorizaria mais delas em upgrades futuros.
- Ramp, anthems, geração de tokens e payoffs todos reforçam o mesmo plano — sinergia interna muito forte.
- **Adições da rebalanceada 2026-08-21** reforçam o mesmo plano: Imperious Perfect (`{2}{G}`, anthem +1/+1 pra Elfos + gera token de Elfo no ETB) e Formidable Speaker (`{2}{G}`, descarta 1 carta da mão pra buscar qualquer criatura no grimório — alimenta o GY e ainda busca peça, tutor real).

**Nonbo leve:** Kindred Dominance/Raise the Palisade/Kindred Summons pedem escolha de "tipo de criatura" — funcionam melhor se o board for consistentemente majoritário Elfo, o que geralmente é o caso aqui, então não chega a ser um problema real.

---

## 11. Estimativa de Bracket

**Bracket 3, tendendo a 3.5–4.**

A favor do 4: Sol Ring, tutores de criatura (Fauna Shaman, Vannifar, Finale of Devastation), motor de combo tribal rápido (Elvish Warmaster + anthems + Lathril pode fechar jogo turno 6-8), Rhystic Study como vantagem de cartas de ponta.

Contra o 4: sem fast mana adicional (Mana Crypt/Vault/Chrome Mox), sem tutor de combo de 2 peças "instantâneo", e a remoção abaixo do recomendado deixa o deck mais vulnerável a boards que fujam do seu controle — características mais de Bracket 3 focado.

---

## 12. Sugestões de melhoria (prioridade)

1. ~~Reforçar remoção~~ — **aplicado, depois parcialmente revertido**: cortadas Agatha's Soul Cauldron/Oversold Cemetery/Harmonized Crescendo, adicionadas Deadly Rollick/Putrefy/Feed the Swarm (Chaos Warp e Vindicate da versão original nem eram Sultai); Agatha's Soul Cauldron e Oversold Cemetery voltaram depois (leitura errada corrigida); em 2026-08-21, Feed the Swarm e Putrefy foram cortados de novo por decisão direta do usuário, trocados por Devoted Druid/Imperious Perfect/Formidable Speaker — remoção real caiu de 1,11 pra 0,78 conjurada em média, total estático caiu de 9 pra 8 efeitos (ver seção 6 atualizada). Ainda dentro da faixa 8–10, mas no piso.
2. ~~Adicionar um overrun~~ — **corrigido:** o deck já tem Tyvar the Pummeler, Ezuri Renegade Leader e Elvish Warmaster fazendo esse papel (ver seção 8 revisada). Prioridade real é mais rampa que sustente esses custos de ativação (4-7 mana) no mesmo turno que o board fica largo.
3. ~~Engordar fontes de azul~~ — **parcialmente aplicado, 2026-08-21:** Llanowar Wastes (B/G) trocado por Underground River (B/U, mesma painland sempre destapada) — fontes de U sobem de 10 pra 11, blue screw caiu de 11,9% pra 8,4% das partidas (ver seção 2 atualizada). Ainda dá pra ir além: outros 6 terrenos B/G-only continuam no deck (Gilt-Leaf Palace, Nurturing Peatland, Undergrowth Stadium, Wastewood Verge, Deathcap Glade, Overgrown Tomb) — cada um é candidato a virar mais 1 fonte de U se quiser reduzir ainda mais o screw.
4. Opcional: Deadly Rollick / Fierce Guardianship (força-tarefa de proteção com free-cast, sinergiza com a quantidade de mana verde disponível) se o objetivo é empurrar para Bracket 4.

---

## Links

- EDHREC: https://edhrec.com/commanders/thranduil-the-elvenking
- Moxfield (criar/comparar): https://moxfield.com/decks/new
- Tribo Elfo: https://edhrec.com/tribes/elf
