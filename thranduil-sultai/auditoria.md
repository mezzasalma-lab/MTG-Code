# Auditoria — Thranduil, the Elvenking (Sultai — B/G/U)

Auditoria feita via skill `mtg-commander`, dados em tempo real do Scryfall.
Data: 2026-08-20

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

## 4. Ramp — 14 peças ✅ (acima do mínimo de 10–12 do Bracket 3)

Arbor Elf, Bloom Tender, Deathbloom Ritualist, Elves of Deep Shadow, Elvish Archdruid, Elvish Mystic, Gwenna Eyes of Gaea, Incubation Druid, Llanowar Elves, Marwyn the Nurturer, Priest of Titania, Selvala Heart of the Wilds, Sol Ring, Wirewood Channeler.

Ponto forte real do deck: quase todo dork escala com a quantidade de elfos em campo (Priest of Titania, Elvish Archdruid, Wirewood Channeler), então o ramp cresce exponencialmente conforme a estratégia tribal avança.

---

## 5. Card draw — ~9 fontes (na faixa do mínimo recomendado)

Rhystic Study, Beast Whisperer, Champions of the Perfect, Edric Spymaster of Trest, Elrond Moon-Reader, Glissa Sunslayer (modal), Harmonized Crescendo, Underrealm Lich (filtragem), além do próprio Thranduil (draw 2/discard 1 a cada elfo lendário que entra).

Adequado, mas depende bastante de gatilhos (criar criatura, dano de combate) — pouco draw "incondicional" fora do Rhystic Study.

---

## 6. Remoção — corrigido após validação com os 2000 goldfishes

**Correção do original:** esta seção recomendava trocar cartas por "Beast Within, Chaos Warp, Vindicate, Deadly Rollick". Chaos Warp (`{2}{R}`) e Vindicate (`{1}{W}{B}`) **não são Sultai** — nem sequer legais na identidade de cor B/G/U do Thranduil. Erro do texto original, verificado via `color_identity` do Scryfall antes de aplicar qualquer troca.

**Troca real aplicada** (0,52 → **1,11** remoção conjurada em média, confirmado nos 2000 goldfishes):
- **Cortadas:** Agatha's Soul Cauldron, Oversold Cemetery, Harmonized Crescendo — as três eram peças de valor lento/condicional com baixo impacto direto, e duas delas dependiam de volume de criaturas na GY que os próprios goldfishes mostraram ser baixo (~1 Elfo milhado por partida em média — ver seção 10 revisada).
- **Adicionadas** (verificadas via Scryfall, todas legais em B/G/U):
  - **Deadly Rollick** (`{3}{B}`, ou `{1}{B}` se você controla um comandante — quase sempre o caso): `Exile target creature.`
  - **Putrefy** (`{1}{B}{G}`): `Destroy target artifact or creature.` — cobre a lacuna de remoção de artefato.
  - **Feed the Swarm** (`{1}{B}`): `Destroy target creature or enchantment an opponent controls. You lose life equal to that permanent's mana value.` — cobre a lacuna de remoção de encantamento.

| Tipo | Cartas | Qtde |
|---|---|---|
| Remoção pontual | Assassin's Trophy, Awaken the Honored Dead, Trystan's Command (modal), Deadly Rollick, Putrefy, Feed the Swarm | 6 |
| Edict repetível | Ruthless Winnower (stax leve, edict toda upkeep) | 1 |
| Wipe assimétrico | Kindred Dominance (destrói tudo que não é do tipo escolhido), Raise the Palisade (bounce assimétrico) | 2 |

**Total real: 9 efeitos** — agora dentro da faixa recomendada (8–10) pra Bracket 3–4. Ainda não há remoção dedicada de planeswalker, mas artefato e encantamento (as duas lacunas mais gritantes) estão cobertos agora.

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

**Nonbo leve:** Kindred Dominance/Raise the Palisade/Kindred Summons pedem escolha de "tipo de criatura" — funcionam melhor se o board for consistentemente majoritário Elfo, o que geralmente é o caso aqui, então não chega a ser um problema real.

---

## 11. Estimativa de Bracket

**Bracket 3, tendendo a 3.5–4.**

A favor do 4: Sol Ring, tutores de criatura (Fauna Shaman, Vannifar, Finale of Devastation), motor de combo tribal rápido (Elvish Warmaster + anthems + Lathril pode fechar jogo turno 6-8), Rhystic Study como vantagem de cartas de ponta.

Contra o 4: sem fast mana adicional (Mana Crypt/Vault/Chrome Mox), sem tutor de combo de 2 peças "instantâneo", e a remoção abaixo do recomendado deixa o deck mais vulnerável a boards que fujam do seu controle — características mais de Bracket 3 focado.

---

## 12. Sugestões de melhoria (prioridade)

1. ~~Reforçar remoção~~ — **aplicado**: cortadas Agatha's Soul Cauldron/Oversold Cemetery/Harmonized Crescendo, adicionadas Deadly Rollick/Putrefy/Feed the Swarm (ver seção 6 revisada — Chaos Warp e Vindicate da versão original nem eram Sultai).
2. ~~Adicionar um overrun~~ — **corrigido:** o deck já tem Tyvar the Pummeler, Ezuri Renegade Leader e Elvish Warmaster fazendo esse papel (ver seção 8 revisada). Prioridade real é mais rampa que sustente esses custos de ativação (4-7 mana) no mesmo turno que o board fica largo.
3. **Engordar fontes de azul** — pelo menos +1 Island básica ou trocar um utility land por algo como Botanical Sanctum ou Tolarian Terror... (considerar um dual U/x adicional); hoje só ~9 fontes hard de U é abaixo do ideal para um pip crítico no próprio comandante.
4. Opcional: Deadly Rollick / Fierce Guardianship (força-tarefa de proteção com free-cast, sinergiza com a quantidade de mana verde disponível) se o objetivo é empurrar para Bracket 4.

---

## Links

- EDHREC: https://edhrec.com/commanders/thranduil-the-elvenking
- Moxfield (criar/comparar): https://moxfield.com/decks/new
- Tribo Elfo: https://edhrec.com/tribes/elf
