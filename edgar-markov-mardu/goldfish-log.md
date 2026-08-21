# Goldfish Log — Edgar Markov

## Simulação #1 — gerada por Claude (RNG real, não é partida sua)

**Método:** embaralhei a lista de 100 cartas de `lista.md` com `random.shuffle` do Python (sem seed fixa, entropia do sistema) em 2026-08-20. On the play, sem compra no T1.

**Mão inicial:** Takenuma Abandoned Mire, Smothering Tithe, Godless Shrine, Arcane Signet, Roaming Throne, Swamp, Swords to Plowshares

**T1:** Joga Takenuma, Abandoned Mire.

**T2:** Compra: Sevinne's Reclamation. Joga Godless Shrine. Conjura Swords to Plowshares (`{W}`) — sem alvo real num goldfish solo (não há criatura de oponente), incluído aqui só como jogada de curva hipotética.

**T3:** Compra: Unholy Annex // Ritual Chamber. Joga Swamp. Conjura Arcane Signet (`{2}`).

**T4:** Compra: Skullclamp. Sem terreno na mão. Conjura Skullclamp (`{1}`).

**T5:** Compra: Phyrexian Altar. Sem terreno na mão (3 terrenos + Arcane Signet = 4 fontes de mana no total).
**Correção em relação a uma primeira passada automática:** meu script inicial tentou conjurar Sevinne's Reclamation aqui, mas isso está errado — Sevinne's Reclamation exige um alvo no cemitério com custo de mana 3 ou menos, e nenhuma criatura morreu ainda nessa simulação, então **não há alvo legal e a mágica não pode ser conjurada**. Corrigindo: com 4 mana disponível, a jogada real é conjurar **Roaming Throne** (`{4}`), escolhendo o tipo Vampire ao entrar (sinergiza com o Eminence do próprio Edgar Markov e com os outros gatilhos de Vampiro da lista).

**T6:** Compra: Edgar Markov. Sem terreno na mão. Mana disponível: 3 terrenos + Arcane Signet = 4. Edgar Markov custa `{3}{R}{W}{B}` = 6 total — **não castável ainda**, faltam 2 fontes de mana. Com os 4 mana disponíveis, a jogada real é conjurar **Smothering Tithe** (`{3}{W}`), usando Godless Shrine/Arcane Signet pro W.

**Board final (fim do T6):** Takenuma Abandoned Mire, Godless Shrine, Swamp, Arcane Signet | Skullclamp, Roaming Throne (tipo Vampire), Smothering Tithe.
**Mão remanescente:** Sevinne's Reclamation (ainda sem alvo), Unholy Annex // Ritual Chamber, Phyrexian Altar, Edgar Markov (o próprio comandante preso na mão por falta de mana).
**Observação honesta:** essa mão específica ficou land-light (só 3 terrenos em 6 turnos) e nunca chegou a resolver o próprio comandante em campo — ele ficou parado na mão do T6 em diante por faltar 2 fontes de mana. Não simulei além do T6.

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
