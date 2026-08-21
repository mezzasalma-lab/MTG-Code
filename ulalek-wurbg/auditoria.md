# Auditoria — Ulalek, Fused Atrocity (5 cores — WUBRG, Eldrazi)

Fontes: Scryfall REST API (`cards/collection`, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `cmc`), consultada em 2026-08-20. Definições de Bracket: `references/commander-rules.md#brackets` do skill mtg-commander (fonte primária: anúncios oficiais da Wizards, "Introducing Commander Brackets Beta" e atualização de outubro/2025). Dados de goldfish citados na seção 8: fonte externa do usuário (ferramenta própria, Google Colab), não gerados por mim.

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | 100 (99 + comandante) | contagem sobre o texto colado |
| Singleton | Sem duplicatas | `uniq -d` |
| Identidade de cor (5 cores) | Sem violação | `color_identity` |
| Cartas banidas em Commander | Nenhuma | `legalities.commander` |

**Comandante:** Ulalek, Fused Atrocity — `{C/W}{C/U}{C/B}{C/R}{C/G}` (5 mana, cada pip híbrido incolor/cor) — Legendary Creature Eldrazi. Texto (Scryfall): *"Devoid. Whenever you cast an Eldrazi spell, you may pay {C}{C}. If you do, copy all spells you control, then copy all other activated and triggered abilities you control. You may choose new targets for the copies."*

Nota: o comandante não menciona "flash" no próprio texto — as métricas de "flash windows"/"flash lines" do goldfish (seção 8) se referem a peças do deck que dão flash a outras cartas (Vedalken Orrery, Liberator Urza's Battlethopter, Skittering Cicada), permitindo conjurar um Eldrazi no fim do turno do oponente e copiar o que estiver na pilha.

---

## 2. Terrenos e curva

- Terrenos: **37** (`type_line`).
- CMC médio, não-terrenos, sem comandante: **4.45** (`cmc`) — alto, esperado num deck com múltiplos Eldrazi de CMC 9-13 (Kozilek x3, Ulamog x2, Emrakul, Void Winnower, Flayer of Loyalties).
- Mana base: contém os 10 duais ABUR completos (Badlands, Bayou, Plateau, Savannah, Scrubland, Taiga, Tropical Island, Tundra, Underground Sea, Volcanic Island — confirmado por nome na lista), além de pain lands, City of Brass, Mana Confluence, Exotic Orchard, Reflecting Pool, e terrenos Eldrazi-específicos (Eldrazi Temple, Cavern of Souls, Eye of Ugin, Sanctum of Ugin, Urza's Cave, Cascading Cataracts, Shrine of the Forsaken Gods).

---

## 3. Categorização por função (via `oracle_text`)

**Ramp:** Sol Ring, Arcane Signet, Talisman of Dominance/Impulse/Resilience, Thran Dynamo, Farseek, Nature's Lore, Three Visits, Expedition Map, Sowing Mycospawn (busca terreno ao conjurar), Forsaken Monument (mana extra por permanente incolor tapado), Spawning Bed (land, sacrifica por 3 tokens de mana) — mais os geradores de token de mana incidentais (Writhing Chrysalis, Chittering Dispatcher, Glaring Fleshraker, Warping Wail, Eldrazi Confluence).

**Card draw:** Rhystic Study (Game Changer), The One Ring (Game Changer), Anticausal Vestige (draw ao sair do campo), Sire of Stagnation (compra 2 por terreno que oponente joga), Kozilek's Unsealing (compra 3 ao conjurar criatura CMC 7+), Nulldrifter (compra 2 ao conjurar).

**Remoção:** Swords to Plowshares, Beast Within, Toxic Deluge, Ugin's Binding (bounce, depois exílio em massa condicional pelo cemitério), Ugin the Ineffable (-3: destrói permanente CMC 3+), Warping Wail (modal, inclui exílio de criatura pequena), World Breaker (exila artefato/encantamento/terreno ao conjurar), Null Elemental Blast (hate multicolor, estreito).

**Wipe relevante para esse deck especificamente:** **All Is Dust** — destrói todos os permanentes coloridos. Como praticamente todas as criaturas Eldrazi do deck são Devoid (incolor, confirmado por `oracle_text` — "This card has no color"), esse wipe tende a ser assimétrico a favor de quem o conjura, mantendo o próprio board.

**Proteção:** Heroic Intervention, Lightning Greaves, Eldritch Immunity (proteção de todas as cores, overload pro time todo), Void Grafter (hexproof), Swan Song, An Offer You Can't Refuse.

**Habilitadores de flash (ligados às métricas de goldfish):** Vedalken Orrery, Liberator Urza's Battlethopter, Skittering Cicada — todos dão flash a spells incolores/artefatos, permitindo conjurar Eldrazi fora do seu turno.

**Multiplicadores de valor:** Echoes of Eternity (copia spell incolor ao conjurar + duplica gatilhos de permanente incolor), Zhulodok Void Gorger (cascade-cascade em spells incolores CMC 7+), Roaming Throne (duplica gatilho de criatura do tipo escolhido), Conduit of Ruin (desconto + tutor pro topo de um Eldrazi CMC 7+).

---

## 4. Game Changers e estruturas restritas

**Game Changers: 3** — Ancient Tomb, Rhystic Study, The One Ring (confirmado via `cards/search?q=is:gamechanger`). Teto exato do Bracket 3.

Varredura de `oracle_text` das 100 cartas:
- **Mass land denial:** não encontrada. World Breaker e Sowing Mycospawn (kicker) exilam **um** terreno-alvo cada, não é efeito em massa.
- **Turnos extras:** não encontrado nenhum efeito desse tipo no texto de nenhuma carta.
- **Combo de 2 peças:** não identifiquei nenhum via varredura de texto (busquei por padrões de untap/copy/recast livre e combinações "infinite"-adjacentes). Isso não é prova formal de ausência, só que não achei um com os padrões que apliquei.

---

## 5. Classificação de Bracket

**Bracket 3 (Upgraded), no teto de Game Changers (3 de 3).**

Base: 3 Game Changers, sem negação de terras em massa, sem turno extra, sem combo de 2 peças identificado na varredura de texto. Mesmo perfil dos outros decks WUBRG que já auditei (Hei Bai, Prismatic Bridge, Ur-Dragon) — todos batem exatamente no teto de 3.

---

## 6. Sinergia com o tema Eldrazi/cópia

O comandante copia todos os spells e habilidades ativadas/disparadas que você controla ao conjurar um Eldrazi (pagando {C}{C}). O deck reforça isso em duas direções:

1. **Habilitadores de flash** (Vedalken Orrery, Liberator, Skittering Cicada) permitem conjurar um Eldrazi barato no fim do turno do oponente pra copiar o que já estiver na pilha, incluindo coisas conjuradas fora do seu turno.
2. **Peças redundantes de cópia** (Echoes of Eternity, Zhulodok) empilham valor adicional sobre spells incolores independente do gatilho do comandante.

Isso é consistente com as métricas do goldfish externo (seção 8): "Avg Ulalek paid triggers" e "Avg flash lines taken" aparecem como métricas dedicadas no simulador do usuário, o que indica que essas linhas foram modeladas explicitamente.

---

## 7. Sugestões — nenhuma recomendação de troca de carta

Não vou sugerir cortes/inclusões específicas para esse deck sem consultar o EDHREC ao vivo (não fiz essa consulta nesta auditoria). Recomendações genéricas de "adicione mais remoção" sem checar o que já está na lista contra dados reais de uso seriam especulação — o que essa auditoria evita, conforme pedido.

---

## 8. Cruzamento com goldfish — fonte externa, não verificada por mim

Dados do simulador do usuário (Google Colab), reproduzidos de `goldfish-log.md`, versão mais recente (v2.2, 500 jogos, 8 turnos, on the play):

- Comandante conjurado até o turno 4: 65,4% | até o turno 5: 83,8%
- Turno médio de conjurar o comandante: 4,25
- Eldrazi conjurados em média: 3,64
- Gatilhos pagos de Ulalek em média: 2,89
- Battlefield final médio: 14,63 permanentes
- Mão final média: 3,26 cartas

Esses números são consistentes com o land count (37) e o pacote de ramp (item 3) permitindo uma curva de comandante em torno do turno 4-5, compatível com o custo de 5 mana dele. Não tenho como verificar a lógica interna do simulador que gerou esses números — reporto como o usuário forneceu.

---

## Links

- EDHREC: https://edhrec.com/commanders/ulalek-fused-atrocity
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
