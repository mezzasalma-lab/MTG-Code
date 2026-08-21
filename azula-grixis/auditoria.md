# Auditoria — Fire Lord Azula (Grixis — U/B/R)

Fontes: Scryfall REST API (`cards/collection`, `cards/named`, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `cmc`), consultada em 2026-08-20. Definições de Bracket: `references/commander-rules.md#brackets` do skill mtg-commander.
Data da auditoria: 2026-08-20

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | 100 (99 + comandante) | contagem sobre o texto colado (parsing de set/coletor/foil removido) |
| Singleton | Sem duplicatas reais | ver nota abaixo |
| Identidade de cor (Grixis) | Sem violação | `color_identity` |
| Cartas banidas em Commander | Nenhuma | `legalities.commander` |

**Comandante:** Fire Lord Azula — `{1}{U}{B}{R}` — Legendary Creature Human Noble. Texto (Scryfall): *"Firebending 2 (Whenever this creature attacks, add {R}{R}. This mana lasts until end of combat.) Whenever you cast a spell while Fire Lord Azula is attacking, copy that spell."*

**Nota — segundo caso do mesmo tipo de ambiguidade de nome nesta sessão:** a lista tem **Seething Song** (clássica, `{2}{R}`, `C21`) e **Blazing Firesinger // Seething Song** (MDFC, `{X}{R}` na frente, `SOS`, cujo verso reimprime o nome "Seething Song"). Minha primeira consulta em lote ao Scryfall resolveu incorretamente as duas linhas pro mesmo card ID (a mesma falha que já tinha acontecido com Demonic Tutor/Emeritus of Woe no deck do Verminister). Conferido manualmente: **IDs diferentes**, são duas cartas físicas distintas, sua lista está correta.

**Nota formal:** Kediss, Emberclaw Familiar tem a habilidade **Partner** (`oracle_text` confirmado), mas você só declarou Fire Lord Azula como comandante — Kediss está jogando como carta normal no 99, o que é legal. Se quiser usar Kediss como segundo comandante no futuro, ele precisaria sair da lista principal pra zona de comando.

---

## 2. Terrenos e curva

- Terrenos: **37** (`type_line`).
- CMC médio, não-terrenos, sem comandante: **2.35** — muito baixo, consistente com um deck de spellslinger que quer resolver muitos spells baratos por turno.

| CMC | Qtde |
|---|---|
| 1 | 16 |
| 2 | 25 |
| 3 | 9 |
| 4 | 8 |
| 5 | 3 |
| 6 | 1 |

41 das 62 cartas não-terreno custam 1-2 mana — curva extremamente baixa, o oposto do perfil que vimos nos decks verdes (Beorn, Thranduil, Ur-Dragon).

---

## 3. Categorização por função (via `oracle_text`)

**Ramp:** Sol Ring, Arcane Signet, Talisman of Dominance, mais um pacote pesado de geração de Treasure (Big Score, Unexpected Windfall, Ancestors' Aid, An Offer You Can't Refuse, Storm-Kiln Artist) — a fonte de aceleração principal do deck não são rocks, é Treasure via spells.

**Card draw:** extremamente denso. Praticamente todo instant barato do deck compra carta junto com seu efeito principal — Leap, Expedite, Shadow Rift, Crimson Wisps, Fists of Flame, Thought Scour (cantrips de 1 mana com upside), mais Frantic Search, Thrill of Possibility, Demand Answers, Big Score, Unexpected Windfall, Abandon Attachments, Archmage Emeritus (Magecraft: compra a cada instant/sorcery conjurado ou copiado), Archmage of Runes (compra a cada instant/sorcery conjurado). Esse é, de longe, o motor de draw mais denso que já vi entre os decks auditados.

**Redução de custo (instant/sorcery):** Baral Chief of Compliance (-1), Goblin Electromancer (-1), Archmage of Runes (-1), Nightscape Familiar (-1 pra spells azuis/vermelhos), Stormcatch Mentor (-1). Com 2-3 desses simultâneos, spells de 1-2 mana ficam efetivamente grátis ou quase.

**Remoção/interação:** Chaos Warp (versátil, não-permanente), Innocent Blood (edict simétrico), Chandra's Ignition (dano em massa via poder de uma criatura sua), Snap (bounce + desonera 2 terrenos), 4 contramágicas (Counterspell, An Offer You Can't Refuse, Wash Away, Narset's Reversal — essa última também copia e devolve o spell alvo à mão do dono, é interação e cópia ao mesmo tempo). Não há remoção dedicada de artefato/encantamento nem de planeswalker.

**Win conditions:** Grapeshot com Storm de verdade (`oracle_text` confirma a keyword Storm), Chandra's Ignition (dano em massa escalando com poder), Giggling Skitterspike (reflete dano recebido em interação pra cada oponente), Zada Hedron Grinder (copia qualquer instant/sorcery que alveje só ela pra cada outra criatura seguar — o deck tem vários combat tricks de 1 mana com draw embutido que servem exatamente pra isso: Titan's Strength, Brute Force, Temur Battle Rage, Run Amok, Unleash Fury, Lunar Frenzy, Invigorated Rampage), e o próprio motor do comandante (copiar spells enquanto ataca).

**Proteção:** ponto fraco real — não encontrei hexproof/indestructible dedicados na varredura. A "proteção" do deck é indireta, via contramágica (4 peças) segurando respostas do oponente, não via proteção do próprio board.

---

## 4. Game Changers e estruturas restritas

**Game Changers: 0** — confirmado via `cards/search?q=is:gamechanger` (lista de 53 cartas), nenhuma presente na lista.

Varredura de `oracle_text` das 100 cartas:
- **Mass land denial:** nenhuma encontrada.
- **Turnos extras:** nenhum efeito encontrado.
- **Combo de 2 peças:** não identifiquei um combo infinito de 2 cartas na varredura que fiz. O motor central (Zada + combat tricks, Veyran/Storm-Kiln/Archmage + Magecraft, Grapeshot com Storm real, redutores de custo empilhados) é uma sinergia forte de "muitas cartas empilhando", não um loop de 2 peças fechado — não achei nenhum par de cartas que gere mana ou dano infinito sozinho.

---

## 5. Classificação de Bracket

**Bracket 2 (Core).**

Aplicando a mesma correção metodológica que já apliquei no deck do Verminister nesta sessão: **0 Game Changers + sem combo de 2 peças + sem mass land denial + sem turnos extras** classifica o deck como Bracket 2, **independente de quão bem construída a sinergia interna seja**. Esse deck tem um motor genuinamente denso (redução de custo empilhada, Magecraft triplo, Storm de verdade no Grapeshot, Zada com vários habilitadores) — mas densidade de sinergia e eficiência de carta, por si só, não empurram um deck pra Bracket 3 segundo o critério oficial (gráfico de Rachel Weeks/painel de Brackets, atualização de outubro/2025) — só Game Changers e as três estruturas proibidas fazem isso.

Vale registrar: esse é o deck mais "abaixo do teto" que já vi na sua coleção nesse critério específico — nem chega perto do limite de 3 Game Changers que Kutzil, Hei Bai, Prismatic Bridge e Ur-Dragon batem exatamente.

---

## 6. Sugestões de melhoria

Não consultei o EDHREC nesta auditoria — não vou especular cortes/inclusões sem esse cruzamento. Se quiser, faço a consulta específica igual fiz pro Beorn.

Um ponto estrutural que a varredura já deixa claro, independente de EDHREC: **proteção é o gap mais visível** — o deck não tem hexproof/indestructible pra proteger Azula (peça central do motor) ou Zada de remoção pontual, dependendo só de contramágica reativa.

---

## Links

- EDHREC: https://edhrec.com/commanders/fire-lord-azula
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
