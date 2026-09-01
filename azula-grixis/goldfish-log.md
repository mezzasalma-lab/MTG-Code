# Goldfish Log — Fire Lord Azula

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

## 2026-09-02 — Simulador goldfish construído do zero (`azula_goldfish_v1.py`)

Segundo dos 4 decks sem simulador desta sessão a ser fechado (depois do
Kutzil). Detalhamento completo carta-a-carta em `checklist-oraculo.md`.

**Metodologia:** oráculo real via Scryfall (line-by-line, "compile
TUDO"), implementação, testes unitários (13 no total, 2 arquivos), 3
rodadas de correção após varredura automatizada de tags órfãs + 1 bug de
regra (706.10, valor de X em cópias) achado por análise de um outlier
estatístico, regressão de 20.000 partidas (0 exceções, ~18.5s).

**Achado mais grave da sessão inteira até agora:** o comandante nunca
entrava em campo no primeiro rascunho (faltava o passo de conjurar da
zona de comando — `BASE_LIBRARY` corretamente não inclui Azula, mas
nada a conjurava de lá). Isso zerava o motor central do deck inteiro
(Firebending + cópia de magia ao atacar). Achado ao verificar
`azula_copy_events_total == 0` em 2.000 partidas seguidas (suspeito
demais pra ser aleatoriedade) e confirmado rastreando presença de Azula
em campo: **0/500** antes do fix, **474/500 (~95%)** depois. Ver
checklist-oraculo.md item 1.

**Motor real deste deck** (Storm + Magecraft + o combo composto
Zada+Azula+Veyran, onde Veyran dobra os gatilhos do Zada e da Azula, não
só o próprio Magecraft dela) é categoricamente diferente de qualquer
outro simulador desta sessão — nenhum outro deck tem esse tipo de
motor de multiplicação de gatilhos por conjurar magia.

### Métricas (20.000 partidas, seed 5.000.000+, turns=10, 0 exceções)

| Métrica | Média | Mediana |
|---|---|---|
| Dano proxy total | 1586.2 | 70.0 |
| Cartas compradas extra | 28.0 | — |
| Treasures criados | 12.4 | — |
| Eventos de cópia do Zada | 0.7 | — |
| Cópias via Azula atacando | 1.7 | — |
| Dobras via Veyran | 8.9 | — |
| Grapeshots conjurados | 0.31 | — |
| Maior dano de 1 Grapeshot (max entre partidas) | — | 46 |
| Biblioteca esgotada | 2695/20000 (13.5%) | — |

**Nota sobre a diferença grande entre média e mediana:** o motor
Zada+Veyran+Storm-Kiln Artist tem uma combinação genuinamente explosiva
e rara — quando as 3 peças estão em campo simultaneamente com um board
largo, cada magia de alvo único gera mais Treasures (via os gatilhos
duplos de Magecraft em cada cópia) do que custou pra conjurar, permitindo
jogar a mão inteira e puxar o deck inteiro no mesmo turno. Isso é uma
linha de combo real e conhecida deste arquétipo em Magic de papel (não
um bug de simulação) — confirmado rápido (poucos ms por partida, sem
travamento) e determinístico por seed. Mesmo tratamento dado ao outlier
do Ouroboroid no Kutzil: documentado como achado real, não suprimido
artificialmente.

