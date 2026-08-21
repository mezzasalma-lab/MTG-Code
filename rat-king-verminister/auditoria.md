# Auditoria — Rat King, Verminister (Mono-Preto)

Auditoria feita via skill `mtg-commander`, dados em tempo real do Scryfall, usando o sistema oficial de Brackets/Game Changers corrigido.
Data: 2026-08-20

---

## 1. Validação formal

| Check | Resultado |
|---|---|
| Total de cartas | ⚠️ **99** (98 + comandante) — falta 1 carta, ver seção 2 |
| Singleton | ✅ respeitado — **Rat Colony (24 cópias)** é a exceção oficial, a própria carta diz "A deck can have any number of cards named Rat Colony" |
| Identidade de cor (mono-B) | ✅ nenhuma violação |
| Cartas banidas em Commander | ✅ nenhuma |
| Erros de grafia | 1 encontrado e corrigido (ver nota abaixo) |

**Comandante:** Rat King, Verminister — `{1}{B}` — Legendary Creature Rat Avatar.
Cria um Rat token e ganha um contador +1/+1 no fim do turno se um permanente seu saiu do campo de batalha nesse turno; pode sacrificar 3 Rats pra reanimar uma criatura E todas as cópias dela do cemitério.

---

## 2. Correção — Emeritus of Woe e Demonic Tutor são a MESMA carta

Eu errei isso na primeira versão desta auditoria. Concluí que `Emeritus of Woe` e `Demonic Tutor` eram duas cartas físicas distintas — mas você corrigiu: **"Demonic Tutor" aqui não é uma carta jogável separada, é o efeito de cópia do Emeritus of Woe via a habilidade "prepared"**.

Texto real da carta (conferido no Scryfall):
> **Emeritus of Woe** — Creature Vampire Warlock `{3}{B}` — "This creature enters prepared. (While it's prepared, you may cast a copy of its spell.)" / "At the beginning of your end step, if two or more creatures died this turn, this creature becomes prepared."
> **Demonic Tutor** (verso) — Sorcery `{1}{B}` — "Search your library for a card, put that card into your hand, then shuffle."

Ou seja: você não tem duas cartas na mão pra jogar — tem UM Emeritus of Woe em campo, que, quando "prepared" (2+ criaturas morreram no seu turno), permite conjurar uma CÓPIA do lado Demonic Tutor. É um efeito condicional acessório de uma única carta, não um tutor irrestrito adicional na lista.

**Correção aplicada:** removi a linha duplicada "Demonic Tutor" do `lista.md`. Isso deixa a lista em **99/100** — você optou por completar depois. Quando tiver a carta 100, é só me passar que eu atualizo lista, curva e o resto da auditoria.

---

## 3. Base de mana

- **Terrenos: 35** — levemente abaixo do ideal (36-38), mas compensado por um pacote de ramp mono-preto de altíssima qualidade (ver seção 5).
- **Cabal Coffers + Urborg, Tomb of Yawgmoth + Crypt Ghast** — o combo clássico mono-preto de "swamps geram mais mana". Com 24 Swamp básicos + Urborg transformando todo terreno em Swamp, Cabal Coffers pode gerar uma quantidade de mana absurda no mid/late game, e Crypt Ghast dobra a produção de todo Swamp que você tap.
- **Nykthos, Shrine to Nyx** — bom encaixe, o deck tem bastante pip preto pesado (Ayara `{B}{B}{B}`, Kindred Dominance `{5}{B}{B}`, vários `{B}{B}`).
- Mono-cor, então fixação não é problema — os terrenos não-básicos aqui são todos utilidade (Castle Locthwain draw, Crypt of Agadeem, Swarmyard proteção, Bojuka Bog graveyard hate, Three Tree City, Big Apple 3 a.m.).

---

## 4. Curva de mana

CMC médio (sem terrenos, sem comandante): **2.76** — dentro do ideal, puxado pra baixo pelas 24 cópias de Rat Colony em CMC 2.

| CMC | Destaques |
|---|---|
| 1 | Sol Ring, Skullclamp, Dark Ritual, Reanimate, Culling the Weak |
| 2 | Rat Colony x24, Deadly Dispute, Priest of Forgotten Gods |
| 3 | Lord Skitter, Karumonix, Ayara, Ninja Teen |
| 4 | Ashcoat, Species Specialist, Crypt Ghast, Deadly Rollick |
| 5 | Marrow-Gnawer, Gray Merchant, Syr Konrad, Thrumming Stone |
| 6-7 | Ratcatcher, Kindred Dominance, Plague of Vermin |

Curva agressiva e baixa — as 24 Rat Colony sozinhas garantem jogadas de 2 manas em praticamente qualquer mão.

---

## 5. Ramp — sólido e mono-preto de verdade

Sol Ring, Jet Medallion, Bontu's Monument (redução de custo pra criaturas pretas), Dark Ritual, Culling the Weak (ambos burst mana), Crypt Ghast, Cabal Coffers, Nykthos Shrine to Nyx.

Sem os mana dorks verdes clássicos (óbvio, mono-preto), mas o pacote Crypt Ghast/Cabal Coffers/Urborg é um dos ramps de mono-preto mais eficientes que existem no formato.

---

## 6. Card draw — 🟢 excelente, com Skullclamp fazendo o trabalho pesado

- **Skullclamp** — com Lord Skitter, Marrow-Gnawer, Piper of the Swarm e Plague of Vermin todos fazendo tokens de Rat 1/1, equipar Skullclamp num token e deixá-lo morrer (+1/-1 = 2/0) compra 2 cartas por token. Esse deck faz MUITOS tokens — Skullclamp aqui é um motor de draw quase sem fim.
- Deadly Dispute, Priest of Forgotten Gods, Ayara (sac: draw), Species Specialist, Black Market Connections, Ripples of Undeath, Secret Salvage.

Motor de draw muito bem conectado ao plano de sacrifício/tokens do deck, não é genérico.

---

## 7. Remoção — 6 efeitos, um pouco abaixo do recomendado

Withering Torment, Deadly Rollick (geralmente de graça com comandante em campo), Fell the Profane (também joga como terreno), Kindred Dominance (wipe assimétrico — mata tudo que não é do tipo escolhido, ótimo com o board cheio de Rats), Dictate of Erebos (edict a cada morte sua), Swarmyard Massacre (-1/-1 em massa pra tudo que não é Insect/Rat/Spider/Squirrel).

**6 efeitos** é abaixo do recomendado (8-10) pra Bracket 3, mas o deck compensa parcialmente com o pacote de aristocrats/drain (seção 9) — controla o jogo por atrito e dreno em vez de só remoção pontual.

---

## 8. Win conditions

- **Skullclamp + geradores de token** — motor de draw que também é, indiretamente, vantagem de recursos suficiente pra vencer por atrito.
- **Gray Merchant of Asphodel** — drena igual à devoção ao preto, que costuma ser alta com tantas criaturas de pips pesados.
- **Marrow-Gnawer** — dá fear pra todos os Rats (evasão total) e pode gerar um exército instantâneo sacrificando um Rat.
- **Thrumming Stone + Rat Colony** — a peça mais explosiva do deck. Ripple 4 ao conjurar qualquer Rat Colony revela as 4 cartas do topo e permite conjurar de graça toda cópia adicional de Rat Colony revelada — com 24 cópias no deck, isso pode virar um "storm" de Rat Colonies numa única jogada, inflando um Rat Colony existente (que ganha +1/+0 por outro Rat controlado) para um tamanho absurdo.
- **Pacote de dreno/aristocrats** (Zulaport Cutthroat, Ayara, Priest of Forgotten Gods, Ninja Teen, Dictate of Erebos, Pitiless Plunderer) — dano incremental que se acumula partida afora.

---

## 9. Tutores

Nenhum tutor irrestrito de verdade na lista. O que existe é bem mais condicional do que eu tinha avaliado antes:
- **Emeritus of Woe** — só libera a cópia do Demonic Tutor quando "prepared" (precisa 2+ criaturas suas morrerem no turno) — sinergiza bem com o plano de sacrifício/aristocrats do deck, mas está longe de ser um tutor de mão livre.
- **Ratcatcher** (repetível, só Rat), **Karumonix** (uma vez, só Rat), **Secret Salvage** (busca todas as cópias de um nome específico — sinergiza direto com Rat Colony).

Isso é genuinamente "tutores raros" — dentro do que a regra oficial pede até pra Bracket 1-2, não só Bracket 3.

---

## 10. Sinergia com o tema Rat / aristocrats

Construção coesa: Lord Skitter, Marrow-Gnawer, Piper of the Swarm e Plague of Vermin geram Rats; Karumonix e Ratcatcher os buscam; Cover of Darkness e Marrow-Gnawer dão evasão; Skullclamp e o pacote de dreno convertem a morte deles em recurso; e as 24 Rat Colony + Thrumming Stone dão o teto de explosividade. O comandante amarra tudo: cada permanente seu que sai do campo gera um Rat extra e cresce o Rat King, então o próprio sacrifício constante do deck alimenta o comandante.

---

## 11. Contagem de Game Changers e Estimativa de Bracket — CORRIGIDA de novo

**Game Changers no deck: 0** (correção — a versão anterior contava Demonic Tutor por engano; ver seção 2).

> **Segunda correção nesta seção — a primeira versão errou de novo, dessa vez na lógica do bracket.** Eu tinha argumentado "Skullclamp/Sol Ring/Cabal Coffers são staples eficientes demais pra ser Bracket 2, então isso empurra pra Bracket 3 mesmo sem Game Changers". Isso está **errado** e reproduz um mito comum: **Bracket 2 não é "nível de precon" nem "sem staples boas"**. A Wizards removeu oficialmente essa associação na atualização de outubro/2025 (gráfico de Rachel Weeks, painel de Brackets), justamente porque precons têm níveis de poder muito variados. A diferença real entre Bracket 2 (Core) e Bracket 3 (Upgraded) é **exclusivamente**: contagem de Game Changers (0 vs. até 3) e ausência/presença de combo de 2 peças antes do turno 6, mass land denial, ou turnos extras encadeados. Um deck pode ter Sol Ring, Skullclamp, mana base ótima e sinergia bem fechada **e ainda ser Bracket 2**, contanto que não rode Game Changers nem essas estruturas proibidas.

Reavaliando com o critério certo:
- **Game Changers: 0** ✅ (critério de Bracket 2)
- **Combo de 2 peças antes do turno 6:** não há — Thrumming Stone + Rat Colony é uma sinergia forte de valor, mas depende de ter as duas peças em mão/campo simultaneamente e de já ter Rat Colonies suficientes reveladas; não é um combo de 2 cartas garantido e replicável cedo, é um teto de explosividade condicional
- **Mass land denial:** não há
- **Turnos extras encadeados:** não há
- **Duração esperada:** o plano principal (tribal + aristocrats + Skullclamp) é de vitória **incremental e disruptível** — exatamente a descrição oficial de Bracket 2 ("vitórias incrementais, telegrafadas no tabuleiro, disruptíveis"), não uma vitória rápida e consistente turno 4-6 como se espera de Bracket 3+

**Conclusão corrigida: Bracket 2 (Core).** Você estava certo desde o início. Isso não é um rebaixamento nem um insulto ao deck — só reflete que ele não roda nenhuma Game Changer nem estrutura de combo/denial proibida, mesmo tendo staples de alta qualidade (que, pelo critério atual, não contam pra cima sozinhas).

---

## 12. Necropotence ou outra carta? — resposta direta

**Necropotence é Game Changer** (confirmado na lista oficial de 53). Adicioná-la tira o deck do Bracket 2 (que exige 0 Game Changers) e o coloca em Bracket 3 — dentro do teto (1 de 3), mas já não é mais "Core puro". Se a intenção é manter Bracket 2 como você mesmo definiu, **não adicione Necropotence** — troque por uma carta forte que não seja Game Changer. Se não tiver problema em virar Bracket 3 (ainda bem confortável, só 1 de 3 GC), Necropotence é uma inclusão excelente pra esse deck (skip do draw step de qualquer forma combina bem com Ratcatcher/Karumonix que já filtram a mão, e o motor de vida do deck via Gray Merchant/dreno ajuda a pagar o custo de vida dela).

### Sugestões verificadas no EDHREC que preservam Bracket 2 (nenhuma é Game Changer)

Cruzei as cartas mais recomendadas pra esse comandante no EDHREC contra a sua lista atual e contra a lista oficial de Game Changers — essas são reais gaps, não estão na sua lista, e não mudam o bracket:

**Remoção pontual (prioridade — é o gap real da seção 7):**
- **Go for the Throat** (`{1}{B}`, instant, destrói criatura não-artefato) — recomendação de alto uso no EDHREC pra esse comandante
- **Infernal Grasp** (`{1}{B}`, instant, destrói qualquer criatura, perde 2 de vida) — mesma faixa
- **Damnation** (`{2}{B}{B}`, wipe total "limpo") — cobre o buraco de "wipe simétrico de verdade" que Kindred Dominance/Swarmyard Massacre não cobrem (os dois são assimétricos, poupam seus próprios Rats — ótimo quando você está na frente, ruim se você precisar resetar o board inteiro)
- **Toxic Deluge** (`{1}{B}`, wipe escalável pagando vida) — alternativa mais barata e flexível ao Damnation

**Card draw incremental (menor prioridade, o deck já tem Skullclamp fazendo esse trabalho):**
- **Phyrexian Arena**, **Sign in Blood**, **Night's Whisper** — draw eficiente clássico mono-preto, nenhum é Game Changer

**Terreno de utilidade:**
- **Cavern of Souls** — protege suas criaturas Rat de contramágica (torna a mágica incontável), útil já que o deck depende de resolver ameaças-chave como Marrow-Gnawer/Karumonix

### Sugestões finais (prioridade)

1. **Escolher uma resposta pontual da lista acima** (Go for the Throat ou Infernal Grasp) pra cobrir o gap de remoção sem sair do Bracket 2.
2. **Adicionar Damnation ou Toxic Deluge** como wipe simétrico de verdade — hoje os dois wipes do deck poupam seus Rats, o que é ótimo ofensivamente mas deixa o deck sem resposta se PRECISAR resetar tudo.
3. **Considerar +1-2 terrenos** (35→36-37).
4. Sobre Necropotence: sua chamada — dentro do Bracket 2 como está hoje, ou aceitar subir pra Bracket 3 (ainda bem dentro do teto) e ganhar um dos motores de card advantage mais fortes do formato.

---

## Links

- EDHREC: https://edhrec.com/commanders/rat-king-verminister
- Tribo Rat: https://edhrec.com/tribes/rat
- Moxfield (criar/comparar): https://moxfield.com/decks/new
