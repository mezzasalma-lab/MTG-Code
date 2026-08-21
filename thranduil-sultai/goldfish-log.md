# Goldfish Log — Thranduil (Sultai)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Simulação estatística v1 — escrita e rodada por Claude (não é dado seu)

**Atribuição:** assim como o simulador do Beorn, este script foi **escrito e executado por mim**, a seu pedido, nos mesmos moldes do `beorn_goldfish_v1.py`. Script completo salvo em `thranduil_goldfish_v1.py` nesta pasta — reproduzível, não é caixa-preta. Metodologia completa (modelo de mana tricolor, proxy estatístico pra "Elfos no cemitério", limitações conhecidas) documentada no docstring do próprio script.

**Resultado (n=2000, 8 turnos, multiplayer — compra sempre no T1 por CR 103.8a):**

```
Avg commander cast turn: 4.00 | por T5: 82,3% | por T6: 86,5%
Avg spells cast: 9.83 | Avg extra draws (gatilhos): 2.86
Avg ramp em campo: 2.31 | Avg remoção conjurada: 0.54
Avg gatilhos "elfo lendário entrou" (Thranduil draw2/discard1): 1.43
Avg cartas milhadas: 2.93 | Avg Elfos milhados pro cemitério (proxy): 0.49
Avg finishers ativados: 2.37 | turno médio do 1º: 4.83 | 53,4% dos jogos até T8
Avg cartas descartadas por limite de mão: 0.08
Avg battlefield final: 14.90 | Avg mão final: 0.68 | Avg terrenos jogados: 6.25
```

Consistente com o teste anterior de n=500 (turno do comandante 4,05→4,00; finisher até T8 55,0%→53,4%; mão final 0,72→0,68) — números estáveis, não é ruído de amostra pequena.

**Duas limitações conhecidas, ainda não corrigidas (mesma transparência que apliquei no Beorn):**
1. **"Elfos no cemitério" é um proxy estatístico**, não contagem real carta-por-carta — assume ~16,5% de chance de qualquer carta milhada ser Elfo, com base na densidade real do deck. Não rastreia identidade individual.
2. **Avg mão final ficou muito baixo (0,68)** — sinal de que o motor de conjuração está esvaziando a mão demais por turno, porque o script (como o do Beorn antes das correções) não rastreia mana já gasta dentro do turno, só um teto por carta individual. Isso provavelmente infla `spells_cast` e `finishers_ativados` de forma otimista. Ainda não corrigi isso — fica pra quando você validar os números, do jeito que fizemos com o Beorn.

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
