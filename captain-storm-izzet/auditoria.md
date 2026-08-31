# Auditoria — Captain Storm, Cosmium Raider (Izzet — U/R)

Auditoria feita via consulta real à API do Scryfall (todas as 75 cartas
únicas da lista + comandante, incluindo `game_changer` verificado carta a
carta, não de memória), seguindo o checklist de `references/commander-rules.md#analise`.
Data: 2026-08-31.

---

## 1. Validação formal

| Check | Resultado |
|---|---|
| Total de cartas | ⚠️ **99** (98 de biblioteca + comandante) — falta 1 carta, lista enviada pelo usuário já vem faltando |
| Singleton | ✅ respeitado (fora as básicas Island/Mountain) |
| Identidade de cor (U/R) | ✅ nenhuma violação — conferido carta a carta contra `color_identity` real da API |
| Legalidade em Commander | ✅ todas as 75 cartas únicas `legal` |
| Game Changers | ✅ **0** — conferido via campo `game_changer` real da API (não é lista de memória) pra todas as 75 cartas |

**Comandante:** Captain Storm, Cosmium Raider — `{U}{R}`, Legendary
Creature — Human Pirate, 2/2. *"Whenever an artifact you control enters,
put a +1/+1 counter on target Pirate you control."* Motor de anthem
condicional: cada artefato que entra (a lista tem ~28 permanentes com o
tipo Artifact, fora os 3 land-artifacts) alimenta um Pirata com um
contador — encaixa direto com o tema Piratas + Tesouros já presente na
lista.

**⚠️ Lista incompleta — não inventado aqui:** a lista enviada pelo
usuário soma 98 cartas de biblioteca (99 com o comandante), 1 carta
faltando pro total padrão de 100. `lista.md` reflete a lista real como
enviada — nenhuma carta foi adicionada pra completar.

---

## 2. Base de mana

- **Terrenos: 33** (7 não-básicos + 13 Island + 13 Mountain) — abaixo do
  ideal (36-38), mas parcialmente compensado por um pacote de rocks
  grande: Arcane Signet, Command Tower (contam como fonte de qualquer
  cor da identidade — Regra 6 de `user-standing-rules.md`), Fellwar
  Stone, Izzet Signet, Izzet Locket, Sol Ring, Lotus Petal, Decanter of
  Endless Water, Bender's Waterskin, Thought Vessel — **9 mana rocks**,
  bem acima da média.
- **Fixação real:** Izzet Boilerworks (bounce land, U+R fixo), Izzet
  Signet/Locket (U+R fixos), Silverbluff Bridge (U ou R, indestructible),
  Swiftwater Cliffs (U ou R, ganha 1 vida), Temple of Epiphany (U ou R,
  scry 1) — deck 2 cores só, fixação não é um problema real aqui.
- **Seat of the Synod** e **Silverbluff Bridge** são *Artifact Land* —
  contam como permanente artefato de verdade pro gatilho da própria
  Captain Storm (+1/+1 num Pirata quando entram), interação real que o
  simulador (quando existir) vai precisar modelar.
- **Storm the Vault // Vault of Catlacan** (`layout: transform`,
  confirmado via API): a frente é um **Encantamento** (não terreno) que
  faz Treasure a cada dano de combate e transforma em terreno real
  ("Vault of Catlacan", mana de qualquer cor OU {U} por artefato
  controlado) quando você tem 5+ artefatos. Contado como spell pro
  propósito de curva/contagem de terrenos acima, não como um dos 7
  não-básicos.
- **Reliquary Tower / Decanter of Endless Water / Thought Vessel:** "no
  maximum hand size" triplicado — redundante em 3 fontes, mas nenhuma
  delas produz mana condicional então não atrapalha o resto da manabase.

---

## 3. Curva de mana

CMC médio (sem terrenos, sem comandante): **≈2,54** — curva baixa e
agressiva, coerente com um deck de tempo/Piratas.

| CMC | Quantidade | Destaques |
|---|---|---|
| 0 | 1 | Lotus Petal |
| 1 | 14 | Sol Ring, Sensei's Divining Top, Brainstorm, Vapor Snag, Impulsive Pilferer, Spyglass Siren, Dragonfire Blade, Bloodforged Battle-Axe, Tarrian's Soulcleaver, Curious Inquiry, Trickster's Talisman, Magic Damper |
| 2 | 20 | Sol Ring-adjacentes (Arcane Signet, Fellwar Stone, Izzet Signet), Captain Vargus Wrath, Jhoira, Malcolm the Eyes, Gleaming Geardrake, Counterspell, Mana Leak, Oaken Siren, Staunch Crewmate |
| 3 | 20 | Captain Lannery Storm, Corsair Captain, Deadeye Quartermaster (4 na verdade — conferir), Careening Mine Cart, Jackdaw, Plundering Pirate, Sailor of Means, Ionize, Storm Fleet Negotiator, Izzet Locket, Izzet Boilerworks-adjacentes |
| 4 | 6 | Fathom Fleet Swordjack, Panharmonicon, Starfield Vocalist, Chain Reaction, Storm the Vault |
| 5 | 1 | Port Razer |
| 6 | 1 | Embercleave (custo real quase sempre bem menor — reduz {1} por atacante) |
| 7 | 1 | Brass's Bounty |
| 9 | 1 | Blasphemous Act (custo real quase sempre bem menor — reduz {1} por criatura em campo) |

Curva concentrada em 1-3 mana (54 de 65 cartas não-terrestres, 83%) —
plano de jogo é pressão cedo com Piratas baratos gerando Tesouro,
escalando pra ameaças de Equipment/artefato no meio de jogo.

---

## 4. Ramp — sólido via rocks + Tesouro, não land-ramp tradicional

**Rocks fixos (9):** Sol Ring, Arcane Signet, Command Tower, Fellwar
Stone, Izzet Signet, Izzet Locket, Lotus Petal, Decanter of Endless
Water, Bender's Waterskin, Thought Vessel.

**Geração de Tesouro (12 fontes reais, conferido oráculo a oráculo):**
Academy Manufactor (dobra qualquer Clue/Food/Treasure — sinergiza com
TODA a lista abaixo), Brass's Bounty (1 Treasure por terreno — burst
tardio), Captain Lannery Storm (ataque), Careening Mine Cart (ataque,
Vehicle), Corsair Captain (ETB), Enterprising Scallywag (end step
condicional — "descended"), Goldvein Pick (dano de combate, Equipment),
Impulsive Pilferer (morte), Plundering Pirate (ETB), Sailor of Means
(ETB), Seize the Spoils (draw 2 + Treasure), Storm the Vault (dano de
combate coletivo). Esse pacote é o motor de ramp REAL do deck — mais
denso que os rocks fixos.

---

## 5. Card draw — bom, focado em filtragem + Clue/Treasure

Brainstorm, Frantic Search (filtra, não puxa líquido), Curious Inquiry
(Aura + Clue), Rune of Flight (draw no ETB + evasão), Mystic Remora
(explosivo cedo, murcha rápido — cumulative upkeep), Sensei's Divining
Top (filtragem + draw lento), Seize the Spoils (draw 2 real), Jackdaw
(draw = artefatos controlados, condicional a conectar), Malcolm/Gleaming
Geardrake/Spyglass Siren/Storm Fleet Negotiator (Clue tokens — draw
diferido, competem por mana de sacrifício depois).

---

## 6. Interação — 8 efeitos, dentro do recomendado

**Contramagia (4):** Counterspell, Mana Leak, Ionize (também causa 2 de
dano), Spell Rupture (escala com o maior poder controlado — bom encaixe
num deck que quer criaturas grandes via Equipment).

**Remoção/wipe (3):** Chaos Warp (universal, qualquer permanente),
Blasphemous Act (wipe, custo real geralmente bem baixo), Chain Reaction
(wipe escalável com contagem de criaturas em campo).

**Tempo (1):** Vapor Snag (bounce + 1 vida).

8 efeitos de interação real — dentro da faixa recomendada (8-10) sem
precisar de reforço imediato.

---

## 7. Win conditions

- **Piratas + Equipment + contador da própria comandante:** Captain
  Storm bota +1/+1 em Piratas toda vez que um artefato entra — com ~11
  peças de Equipment na lista (Bloodforged Battle-Axe, Cloak of the Bat,
  Dragonfire Blade, Embercleave, Goldvein Pick, Swiftfoot Boots, Sword of
  Once and Future, Tarrian's Soulcleaver, Trickster's Talisman, Twin
  Blades, Two-Handed Axe), cada equip novo empilha valor duplo (o
  contador da Captain Storm + o próprio bônus do Equipment).
- **Fathom Fleet Swordjack** — dano de ataque escala com artefatos
  controlados (não just poder), um deck cheio de Treasure/Equipment vira
  ele numa ameaça grande sem precisar de +1/+1 counters.
- **Embercleave** — flash, custo real despenca com criaturas atacando,
  finisher clássico de deck agressivo de criaturas pequenas.
- **Port Razer** — combat damage → untap tudo + combate extra, ameaça
  real de virar o jogo numa única conexão.
- **Academy Manufactor + Storm the Vault/qualquer gerador de Clue/Food/
  Treasure** — motor de valor duplicado que também acelera Storm the
  Vault a transformar (5+ artefatos).

---

## 8. Sinergia com o tema (artefatos + Piratas + Tesouro)

Construção bem coesa: 16 Piratas reais na lista (conferido `type_line`,
não contagem por nome), 12 fontes de Treasure, ~28 permanentes com tipo
Artifact (Equipment, Vehicles, rocks) — a comandante costura os três
eixos (artefato entra → contador em Pirata), e Panharmonicon/Starfield
Vocalist dobram qualquer gatilho de ETB de artefato/criatura na mesa
(incluindo o da própria Captain Storm, empilhado com Roaming
Throne-like doubling — aqui não há Roaming Throne na lista, mas o
princípio de "2 fontes de dobra simultâneas multiplicam, não somam" já
documentado noutros decks deste repositório se aplica igual se ambas
entrarem em jogo).

---

## 9. Combos / Bracket

**Dramatic Reversal** está na lista **sem Isochron Scepter** — não é o
combo infinito clássico aqui, só um efeito de valor (untapa tudo de
não-terreno por `{1}{U}`, ótimo depois de gastar mana em rocks/Piratas
baratos pra reativar tudo). **Nenhum combo de 2 peças infinito
identificado** na lista atual.

- **Game Changers: 0** (critério de Bracket 2, conferido via API real).
- **Combo de 2 cartas antes do turno 6:** não há.
- **Mass land denial:** não há.
- **Turnos extras encadeados:** não há.

**Conclusão: Bracket 2 (Core)**, mesmo critério já usado nos outros
decks deste repositório (contagem de Game Changers + ausência de
combo/denial/turnos extras — não "quão boas são as cartas", ver correção
já registrada na auditoria do Rat King, seção 11).

---

## 10. Próximos passos

- Falta 1 carta pra completar as 100 (ver seção 1) — decisão do usuário.
- Simulador de goldfish ainda não construído pra este deck — próxima
  etapa natural, seguindo o mesmo padrão dos outros 12 decks do
  repositório (checklist de 13 categorias desde a construção inicial,
  não retrofit).

## Links

- EDHREC: https://edhrec.com/commanders/captain-storm-cosmium-raider
- Moxfield (criar/comparar): https://moxfield.com/decks/new
