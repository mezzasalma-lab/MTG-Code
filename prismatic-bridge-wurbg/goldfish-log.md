# Goldfish Log — Esika, God of the Tree // The Prismatic Bridge

## Simulação #1 — gerada por Claude (RNG real, não é partida sua)

**Método:** embaralhei a lista de 100 cartas de `lista.md` com `random.shuffle` do Python (sem seed fixa, usa entropia do sistema operacional) em 2026-08-20. Mão inicial = 7 cartas do topo pós-embaralhamento. Convenção: jogador na ponta ("on the play"), sem compra no turno 1, compra 1 carta a partir do turno 2. Efeitos de "olhe o topo N" (ex: Oath of Nissa) foram resolvidos consultando a ordem real da biblioteca simulada, não escolhidos livremente. Este é um teste solo sem oponente — anotei explicitamente onde isso limita alguma carta (ex: Exotic Orchard).

**Mão inicial:** Oath of Nissa, Plateau, Command Tower, Sphinx of the Second Sun, Exotic Orchard, Bayou, Tamiyo, Field Researcher

**T1:** Joga Command Tower. Conjura Oath of Nissa (`{G}`). Resolve olhando o topo 3 da biblioteca simulada: Arena Rector, City of Brass, Savannah. Escolha: Arena Rector (criatura — já tinha 3 terrenos na mão, land não era prioridade). City of Brass e Savannah vão pro fundo.
Mão pós-T1: Plateau, Sphinx of the Second Sun, Exotic Orchard, Bayou, Tamiyo Field Researcher, Arena Rector.

**T2:** Compra: Badlands. Joga Bayou. Nenhum spell de 2 custa esse valor na mão — passa.

**T3:** Compra: Swords to Plowshares. Joga Plateau. 3 fontes de mana (Command Tower/Bayou/Plateau). Tamiyo, Field Researcher custa `{1}{G}{W}{U}` = 4 total, falta 1 — não castável ainda. Passa.

**T4:** Compra: The Peregrine Dynamo. Joga Exotic Orchard — **nota:** em goldfish solo sem oponente, Exotic Orchard não tem fonte confiável (não há terreno alheio pra copiar), tratado como mana morto neste teste. Com Command Tower + Bayou + Plateau (3 mana úteis), conjura The Peregrine Dynamo (`{3}`).

**T5:** Compra: Sol Ring. Conjura Sol Ring. Com Sol Ring + os 3 lands úteis, monta `{1}{G}{W}{U}` e conjura Tamiyo, Field Researcher.

**T6:** Compra: Teferi, Time Raveler. Conjura Teferi, Time Raveler (`{1}{W}{U}`).

**Board final (fim do T6):** Command Tower, Bayou, Plateau, Exotic Orchard (morto), Sol Ring | Oath of Nissa, The Peregrine Dynamo, Tamiyo Field Researcher, Teferi Time Raveler.
**Mão remanescente:** Sphinx of the Second Sun, Arena Rector, Badlands, Swords to Plowshares.
**Sem compra ainda:** nenhuma das Game Changers da lista (Farewell, Narset Parter of Veils, Rhystic Study) apareceu nesses 6 turnos — dado real dessa simulação, não uma afirmação sobre a lista em geral.

---

<!-- Para novas partidas (reais ou novas simulações), use o formato abaixo -->

## Partida #N — AAAA-MM-DD

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
