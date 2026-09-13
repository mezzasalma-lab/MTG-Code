# Goldfish Log — Captain Storm, Cosmium Raider

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

## 2026-09-02 — Simulador goldfish construído do zero (`captainstorm_goldfish_v1.py`)

Terceiro dos 4 decks sem simulador desta sessão a ser fechado (depois de
Kutzil e Azula). Detalhamento completo carta-a-carta em
`checklist-oraculo.md`.

**Metodologia:** oráculo real via Scryfall (line-by-line, "compile
TUDO"), implementação com objetos `Permanent` (contadores +1/+1
persistentes + Equipment anexado), testes unitários (10 no total, 2
arquivos), 1 rodada de correção após varredura automatizada de tags
órfãs (4 gaps reais confirmados), regressão de 20.000 partidas (0
exceções, ~154s).

**⚠️ Nota herdada da auditoria:** a lista enviada pelo usuário tem 98
cartas de biblioteca (99 com o comandante), falta 1 carta pro total
padrão de 100 — não corrigido/inventado aqui, `BASE_LIBRARY` reflete a
lista real.

**Motor real deste deck:** Captain Storm ("+1/+1 num Pirata quando um
artefato entra") combinado com um pacote denso de geração de
Treasure/Clue/Food, Academy Manufactor (triplica cada criação) e
Panharmonicon+Starfield Vocalist (dobram multiplicativamente qualquer
gatilho de ETB) — três camadas que se retroalimentam.

### Achado estatístico (Bloodforged Battle-Axe)

Confirmado num teste de estresse (seed fixa, turns=10): quando várias
cópias de Bloodforged Battle-Axe acabam equipadas na mesma criatura que
conecta sem bloqueio todo turno, cada cópia dispara SEPARADAMENTE
("whenever equipped creature deals combat damage, create a token copy
of this Equipment") — N cópias = N gatilhos = N novas cópias por
combate, dobrando a cada turno que conecta. Resultado observado: **1.296
cópias de Bloodforged Battle-Axe** em campo até o turno 10, simulação
rodando em 0.39s (determinístico, sem travamento). Esta é uma interação
real e conhecida de Magic de papel (não um bug de implementação) —
documentada, não suprimida, mesmo tratamento dado aos outliers do
Ouroboroid (Kutzil) e do combo Zada+Veyran+Storm-Kiln Artist (Azula)
nesta sessão.

### Métricas (20.000 partidas, seed 5.000.000+, turns=10, 0 exceções)

| Métrica | Média | Mediana |
|---|---|---|
| Dano proxy total | 325.9 | 163.0 |
| Cartas compradas extra | 21.4 | — |
| Treasures criados | 5.4 | — |
| Clues criados | 2.7 | — |
| Food criado | 1.1 | — |
| Contadores colocados pela Captain Storm | 62.8 | — |
| Gatilhos extra via dobradores de ETB | 16.3 | — |
| Equip/attach ativados | 15.6 | — |
| Biblioteca esgotada | 999/20000 (5.0%) | — |

A diferença entre média (325.9) e mediana (163.0) segue o mesmo padrão
documentado no Azula: um motor genuinamente explosivo e raro (Academy
Manufactor + os 2 dobradores de ETB + Bloodforged Battle-Axe
simultâneos) puxa a média pra cima em poucas partidas muito boas, sem
mudar o "jogo típico" (mediana).

---

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Achado principal (detalhes completos em `checklist-oraculo.md`, seção no
topo): `try_equip()` nunca cobrava NENHUM custo de Equip em nenhuma das
11 peças de Equipment — todas anexavam de graça sempre, quando o
oráculo real só concede isso de graça (ETB) pras 2 com essa cláusula
explícita (Twin Blades, Embercleave); as outras 9 exigem pagar o Equip
normal. Mais 6 gaps: Two-Handed Axe nunca dobrava poder de combate (bug
de nome — comparava contra "Two-Handed Axe" mas o card real se chama
"Two-Handed Axe // Sweeping Cleave"); Enterprising Scallywag só
detectava "descended" pelo descarte de limite de mão, ignorando
sacrifícios reais; Izzet Locket/Lotus Petal/Trickster's Talisman
sacrificavam sem passar pelo cemitério nem disparar Geardrake/
Soulcleaver; Oaken Siren (único mana-dork de criatura da lista) nunca
contribuía mana nenhuma; Auras podiam ser conjuradas sem criatura em
campo pra enfeitiçar.

### Métricas antes/depois (20.000 partidas, seed 5.000.000, turns=10, 0 exceções)

| Métrica | Antes | Depois |
|---|---|---|
| Dano proxy médio | 325.9 | 201.3 |
| Dano proxy mediano | 163.0 | 158.0 |
| Cartas compradas extra (média) | 21.4 | 20.7 |
| Treasures criados (média) | 5.4 | 5.3 |
| Contadores colocados pela Captain Storm (média) | 62.8 | 28.2 |
| Gatilhos extra via dobradores de ETB (média) | 16.3 | 6.7 |
| Equip/attach ativados (média) | 15.6 | 3.6 |
| Biblioteca esgotada | 999/20000 (5.0%) | 681/20000 (3.4%) |

A queda grande em "Equip/attach ativados" (15.6→3.6) e nos "Contadores
da Captain Storm" (62.8→28.2) é exatamente o efeito esperado de corrigir
o bug do Equip de graça: antes, toda peça de Equipment conjurada também
"ativava" instantaneamente sem custo, inflando a contagem de ativações
e, indiretamente, o ritmo geral do motor (mais mana livre = mais
artefatos conjurados = mais contadores da Captain Storm). A mediana caiu
pouco (163→158, ~3%) porque o "jogo típico" não dependia tanto do
Equipment quanto a cauda explosiva dependia — a média caiu bem mais
(325.9→201.3) porque a correção do Equip atinge justamente os jogos em
que múltiplas peças caras (Embercleave, Sword of Once and Future,
Dragonfire Blade) estavam sendo empilhadas de graça.

