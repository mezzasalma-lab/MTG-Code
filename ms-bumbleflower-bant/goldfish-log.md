# Goldfish Log — Ms. Bumbleflower

## Porte completo do modo de resiliência + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** "Faça agora a Ms. Bumbleflower" — seguindo o porte
concluído no Nekusar, Azula, Beorn e Thranduil. Detalhes completos em
`checklist-oraculo.md`.

**Achado:** deck nasce com CR 903.9a correta desde o início. `state.
battlefield` aqui é lista de objetos `Permanent` (não strings) —
`remove_permanent` envolve a `leave_battlefield` já existente (que já
tratava Ozolith/Chasm Skulker) e só adiciona o tratamento do comandante
(zona de comando). Auditoria dos pontos de sacrifício pré-existentes
(disciplina obrigatória) achou **0 sacrifice outlets neste deck**
(diferente do Beorn/Thranduil) — mas achou 2 bugs reais não
relacionados: (1) taxa de comandante (CR 903.8) tinha o contador
certo, mas o efeito de taxação nunca era lido em `effective_cost`; (2)
`mulligan()` reembaralhava via RNG global em vez do RNG seedado (mesma
classe de bug do Azula — 685/3000 = 22,8% de partidas
não-determinísticas com a mesma seed antes do fix).

**Resultado:** modo padrão com bit-identidade PERFEITA (0/20000
mismatches) contra uma versão anterior patcheada só com o fix de
determinismo — porte 100% estrutural, como esperado (0 sacrifícios
voluntários = comandante nunca sai de campo em modo padrão = taxa
nunca observável fora do modo de resiliência).

**Validação:** regressão de 20.000 partidas em modo de resiliência, 0
exceções, 0 comandantes presos no cemitério, 33,48% das partidas com
recast pagando a taxa CR 903.8 + 22 testes dirigidos.

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no
Megatron/Azula/Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil.
Detalhes carta-a-carta completos em `checklist-oraculo.md` (seção no
topo) — **12 gaps reais** encontrados, mesmo depois da rodada de
construção original já ter corrigido 8 outros + 1 bug crítico (comandante
nunca em campo). Achado principal: Heliod, Sun-Crowned tratado como
criatura o tempo todo, sem o gate real de devoção ao branco (`>=5`),
afetando 5 pontos do motor (combate, contador, mana do Rishkar, Ozolith).
Mais 11 gaps: 2 habilidades de Heliod incompletas/ausentes (gatilho de
vida só via combate, `{1}{W}` de lifelink 100% ausente); Deepglow Skate
só dobrava 1 alvo em vez de "any number"; Jolrael's `{4}{G}{G}` overdrive
100% ausente; Swiftfoot Boots' Equip {1} nunca cobrado (mesma classe do
bug sistêmico do Captain Storm); Slip Out the Back's "phases out" 100%
ignorado (alvo continuava atacando); Tamiyo Seasoned Scholar's −7 100%
ausente; Walking Ballista's "remove counter: 1 dano" 100% ausente; Twenty
-Toed Toad's limite de mão (20, não infinito) misturado com as fontes
verdadeiramente ilimitadas; Flooded Grove subcontada como 0 mana junto
com 3 filter lands que são genuinamente líquido-0 (ela não é, tem `{T}:
Add {C}` de graça); Oakhollow Village esquecia Twenty-Toed Toad (Frog) do
próprio set de tipos elegíveis.

### Métricas antes/depois (2.000 partidas, seed 7.000.000, turns=10, mesma seed)

| Métrica | Antes | Depois |
|---|---|---|
| Dano proxy médio | 187,8 | 199,0 |
| Dano proxy mediano | 126,5 | 133,0 |
| Cartas compradas extra (média) | 24,5 | 25,9 |
| Compras forçadas do oponente (média) | 17,3 | 18,1 |
| Treasures criados (média) | 2,6 | 2,8 |
| Contadores colocados (média) | 72,5 | 79,9 |
| Vida ganha (média) | 2,5 | 17,3 |
| Interação jogada (média) | 3,4 | 3,5 |
| Vitórias via Simic Ascendancy | 419/2000 (21,0%) | 440/2000 (22,0%) |
| Vitórias via Twenty-Toed Toad | 61/2000 (3,1%) | 73/2000 (3,7%) |
| Biblioteca esgotada | 0/2000 | 1/2000 |

**Leitura:** todas as métricas se movem pra CIMA, na direção esperada de
uma rodada que só corrigiu implementações ausentes/parciais (nenhum fix
removeu valor de nenhuma carta). O salto mais chamativo é vida ganha
(2,5→17,3, ~7x) — driver principal é o achado #3 (Heliod's `{1}{W}:
lifelink noutra criatura`, ramo antes 100% ausente): antes, Heliod só
ganhava vida via lifelink de combate nativo (raro nesta lista — só
Mangara tem lifelink impresso); agora, sempre que Heliod está em campo
com mana sobrando, ele ativamente converte o poder do melhor atacante em
vida ganha TODO turno, o que também retrigger o próprio Heliod (mais
contadores) — efeito composto real, não um bug (mana-gated a 1 ativação
por turno, sem loop). Dano proxy subiu ~6% (187,8→199,0) — soma de vários
fixes menores na mesma direção (Deepglow dobrando múltiplos alvos,
Jolrael overdrive, Ballista convertendo contadores em dano no último
turno, Flooded Grove destravando 1 mana extra). Contadores colocados
subiu ~10% (mesma causa: Deepglow multi-alvo + Oakhollow incluindo o Toad
+ fasear ainda coloca o contador do Slip Out). As 2 condições de vitória
alternativa também sobem levemente (mais contadores = growth counters da
Ascendancy sobem mais rápido; Toad se beneficia do próprio ajuste de Frog
no Oakhollow) — nenhuma métrica se moveu de forma inexplicável ou na
direção errada.

**Validação:** smoke test (94 cartas no `CARD_DB`, 99 na `BASE_LIBRARY`,
0 desconhecidas/duplicadas fora das básicas) + 2.000 partidas antes/depois
(tabela acima) + 20.000 partidas de regressão (seed 9.500.000+, turns=10,
**0 exceções**, ~40s) + 23 checagens dirigidas (1 arquivo, uma por gap,
todas passando).

---

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

