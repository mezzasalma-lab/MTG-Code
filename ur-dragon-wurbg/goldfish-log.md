# Goldfish Log — The Ur-Dragon

## Simulação #1 — gerada por Claude (RNG real, não é partida sua)

**Método:** embaralhei a lista de 100 cartas de `lista.md` com `random.shuffle` do Python (sem seed fixa, entropia do sistema) em 2026-08-20. On the play, sem compra no T1. Fetchlands e buscas de biblioteca (Nature's Lore) foram resolvidas removendo a carta buscada da biblioteca simulada e rodando `random.shuffle` de novo nela — igual ao "then shuffle" real das cartas — não escolhi as próximas compras livremente.

**Mão inicial:** Misty Rainforest, Cavern of Souls, Swamp, Orb of Dragonkind, Temple Garden, Bloodstained Mire, Nature's Lore

Mão com 5 terrenos/fontes de mana e nenhum Dragão — jogável, mas sem ameaça na mão de saída.

**T1:** Joga Bloodstained Mire, crackeia na hora buscando Mountain (paga 1 vida, vida 39). Biblioteca reembaralhada.

**T2:** Compra: Rhythm of the Wild. Joga Temple Garden destapado (paga 2 vida, vida 37). Conjura Nature's Lore (`{1}{G}`), busca Forest, coloca destapado em campo. Biblioteca reembaralhada.
Board: Mountain, Temple Garden, Forest — 3 fontes de mana já no T2.

**T3:** Compra: Roaming Throne. Joga Misty Rainforest, crackeia buscando Island (paga 1 vida, vida 36). Biblioteca reembaralhada.
Board: Mountain, Temple Garden, Forest, Island — 4 fontes de mana.

**T4:** Compra: Klauth, Unrivaled Ancient (`{4}{R}{R}` = 6 mana — não castável ainda). Joga Cavern of Souls. Conjura Orb of Dragonkind (`{1}{R}`).

**T5:** Compra: Garruk's Uprising. Joga Swamp. Conjura Rhythm of the Wild.

**T6:** Compra: Swords to Plowshares. Sem terreno na mão pra jogar. Conjura Roaming Throne (`{4}`).

**Board final (fim do T6):** Mountain, Temple Garden, Forest, Island, Cavern of Souls, Swamp (6 terrenos) + Orb of Dragonkind, Rhythm of the Wild, Roaming Throne.
**Mão remanescente:** Klauth Unrivaled Ancient, Garruk's Uprising, Swords to Plowshares.
**Observação honesta:** nenhum Dragão de verdade resolveu em campo nos 6 turnos simulados — Klauth ficou preso na mão por falta de mana (precisa de 6, o deck só tinha 6 fontes em campo no T6 mas gastas em Roaming Throne). Não é uma afirmação sobre a lista em geral, só o que essa mão/sequência específica produziu.

---

## Estudo de evolução V0.5–V1.7.7 — fonte: Google Colab do usuário (não Claude)

**Atribuição:** esta tabela e a análise que a acompanha vêm de simulações estatísticas (1.000 iterações por versão) que o usuário rodou no Google Colab, fora desta sessão, ao longo da evolução do deck. Não foram geradas por mim — não tenho acesso à ferramenta nem posso verificar a lógica interna do simulador. Reproduzo os números e a interpretação como o usuário trouxe, sem validação independente da minha parte.

**Nota de consistência:** as versões v0.5–v1.7.4 mencionam Smuggler's Surprise, Dragon's Hoard e Fellwar Stone — nenhuma das três está no `lista.md` atual registrado aqui. Isso bate com a própria narrativa do usuário (o deck foi mudando com base nesses testes): a lista que temos hoje já reflete o resultado desse processo, não uma versão anterior.

### Tabela comparativa (fonte: Colab do usuário)

| Versão | Mull. | Ramp T2 | Engine T4 | Dragão T6 | Dragão T8 | Tithe T4 | Hand final | BF final | Tesouros | Dano T8 | Infinite |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v0.5 – baseline antigo, T6 | 1,04 | 60,2% | 54,8% | 62,8% | — | 3,8% | 2,90 | 8,37 | — | — | — |
| v1.2 – Oracle, T6 | 1,01 | 58,7% | 57,1% | 63,1% | — | 5,5% | 2,93 | 8,37 | 0,07 | — | — |
| v1.3 – Oracle, T6 | 1,03 | 60,4% | 48,9% | 62,9% | — | 4,8% | 3,28 | 8,72 | 0,08 | — | — |
| v1.5 – T8 + novo mulligan | 0,66 | 56,6% | 45,9% | 67,2% | 83,5% | 6,2% | 3,66 | 11,51 | 0,17 | — | — |
| v1.6.1 – Smuggler modelado | 0,64 | 55,4% | 42,7% | 66,5% | 83,2% | 5,4% | 3,60 | 11,72 | 0,20 | — | — |
| v1.7.4 baseline – combate/tesouros | 0,65 | 57,7% | 46,7% | 68,7% | 86,0% | 5,4% | 3,59 | 14,52 | 4,36 | 23,4 | 0,7% |
| v1.7.5 – Smuggler → Delighted | 0,62 | 67,0% | 44,2% | 69,7% | 84,8% | 6,1% | 3,39 | 14,48 | 5,02 | 22,9 | 0,9% |
| **v1.7.6 – + Birds, −Dragon's Hoard** | 0,59 | 66,8% | 42,5% | 71,3% | 85,3% | 5,5% | 3,48 | 14,97 | 4,89 | 25,2 | 0,6% |
| v1.7.7 experimental – Horn → Fellwar | 0,58 | 70,8% | 41,9% | 72,7% | 87,7% | 5,1% | 3,36 | 14,61 | 4,97 | 24,5 | 0,9% |

**v1.7.6 é a configuração atual** — corresponde ao `lista.md` registrado aqui (Delighted Halfling e Birds of Paradise dentro, Smuggler's Surprise e Dragon's Hoard fora, Herald's Horn mantido). v1.7.7 (Herald's Horn → Fellwar Stone) foi testada mas descartada pelo usuário — fica registrada como teto experimental de velocidade, não como configuração adotada.

### Interpretação do usuário sobre a evolução (reproduzida, não verificada por mim)

- O ganho mais relevante não foi aumentar volume de ramp, foi qualidade: trocar por Delighted Halfling levou Ramp T2 de 57,7% (v1.7.4) para 67,0% (v1.7.5).
- Dragon's Hoard → Birds of Paradise (v1.7.5 → v1.7.6) não subiu mais o Ramp T2 (já saturado), mas subiu Dragão T6 (69,7% → 71,3%) e Dano T8 (22,9 → 25,2).
- Engine T4 caiu de 46,7% (v1.7.4) para 42,5% (v1.7.6) — trade-off aceito pelo usuário em troca do ganho em Dragão T6 e Dano T8.
- v0.5–v1.3 não são comparáveis a v1.5+ (só simulavam 6 turnos, heurísticas diferentes) — o próprio usuário fez essa ressalva metodológica.

---

## Goldfish manual do usuário (case study, não misturar estatisticamente com a tabela acima)

**Fonte:** relatado pelo usuário, partida manual jogada por ele mesmo (não simulação em massa, não simulação minha).

Linha de jogo relatada:
- T1: Command Tower
- T2: Cavern (of Souls) + Farseek → Bayou
- T3: Mountain → Sylvan Library + Firdoch Core
- T4: Lightning Greaves + interação
- T5: Ramos (Dragon Engine) + Greaves
- T6: Haven (of the Spirit Dragon) → Return of the Wildspeaker pra 5 cartas
- T7: desenvolvimento/fetch → Miirym (Sentinel Wyrm)
- T8-ish: Utvara (Hellkite)/Miirym → Ur-Dragon → avalanche de gatilhos/cartas/permanentes

Resultado relatado: ~16 cartas na mão no fim, board considerado vitória virtual pelo usuário.

**Achado do usuário reproduzido aqui:** Sylvan Library + fetchlands + Return of the Wildspeaker resolveram o problema de ficar sem gás; Firdoch Core funcionou no papel híbrido de ramp/fixing que ainda recebe a Eminência do comandante.

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
