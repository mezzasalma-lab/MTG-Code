# Goldfish Log — Ms. Bumbleflower

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Partida #1 — AAAA-MM-DD

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

---

## Partida #2 — AAAA-MM-DD

- **Formato do teste:**
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:**
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

<!-- Copie o bloco acima para cada nova partida -->

---

## 2026-09-02 — Simulador goldfish construído do zero (`bumbleflower_goldfish_v1.py`)

Último dos 4 decks sem simulador desta sessão a ser fechado (depois de
Kutzil, Azula e Captain Storm) — a lista foi colada ao vivo pelo usuário
nesta conversa (`lista.md` estava vazio antes disso). Detalhamento
completo carta-a-carta em `checklist-oraculo.md`.

**Metodologia:** oráculo real via Scryfall (line-by-line, "compile
TUDO"), implementação com objetos `Permanent` (o deck de contadores mais
denso da sessão), testes unitários (12 no total, 2 arquivos), 1 bug
crítico (comandante nunca em campo — mesmo bug já visto no Azula) + 8
gaps reais após varredura automatizada de tags órfãs, regressão de
20.000 partidas (0 exceções, ~62s).

**Motor real deste deck:** Ms. Bumbleflower dispara em toda magia
conjurada (força o oponente a comprar + põe contador + no 2º gatilho do
turno compra 2), centralizado junto com TODA outra fonte de contador do
deck (Rishkar, Forgotten Ancient, Managorger/Kalonian Hydra, Deepglow
Skate, Simic Ascendancy, Noble Heritage, Wizard Class, Oakhollow
Village, Ozolith) numa função única `put_counters()` — o que faz Danny
Pink (compra no 1º contador de cada criatura por turno) e Simic
Ascendancy (vitória alternativa com 20+ growth counters) reagirem a
QUALQUER uma dessas fontes automaticamente, sem precisar de código
duplicado em cada carta.

### Achado: 2 vitórias alternativas reais, ambas disparando na prática

- **Simic Ascendancy** (20+ growth counters no upkeep): **4.093/20.000
  partidas (~20.5%)** venceram assim na regressão de 10 turnos — um
  resultado real do quão denso é o pacote de multiplicadores de
  contador (Kalonian Hydra dobra tudo ao atacar, Deepglow Skate dobra na
  ETB, a própria Simic Ascendancy é um mana sink direto pra +1/+1).
- **Twenty-Toed Toad** (20+ contadores nele ou 20+ cartas na mão ao
  atacar): **505/20.000 (~2.5%)**.

Nenhuma das duas foi "decidida" a dar certo — surgiram naturalmente da
implementação fiel de cada carta, exatamente o tipo de achado que a
regressão longa existe pra revelar.

### Métricas (20.000 partidas, seed 5.000.000+, turns=10, 0 exceções)

| Métrica | Média |
|---|---|
| Dano proxy total | 188.7 |
| Cartas compradas extra | 24.8 |
| Compras forçadas do oponente (retrigger Smothering Tithe) | 17.7 |
| Contadores colocados | 72.3 |
| Vida ganha | 2.7 |
| Interação jogada | 3.5 |
| Biblioteca esgotada | 9/20000 |

