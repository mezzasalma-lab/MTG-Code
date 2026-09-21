# Goldfish Log — Fire Lord Azula

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Porte completo do modo de resiliência + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** "Agora o deck da Azula" — seguindo o porte concluído no
Vihaan e no Nekusar. Detalhes completos em `checklist-oraculo.md` e
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Achado:** 3º deck desta sessão a nascer com CR 903.9a correta desde o
início. Sem impacto numérico (0 cartas "creature dies" — deck
spellslinger/magecraft/storm, não aristocrata). 1 token agregado real
(Treasures) tratado no wipe de artefato.

**Resultado:** modo padrão idêntico ao commit anterior (0/20000
mismatches, isolando o fix de determinismo abaixo).

**Validação:** regressão de 20.000 partidas em modo de resiliência, 0
exceções, 0 comandantes presos no cemitério + 6 testes dirigidos.

---

## Achado adicional: `mulligan()` não era determinística — bug pré-existente sério, não relacionado ao comandante — 2026-09-21

**Gatilho:** validação de bit-identidade do porte acima revelou que
`mulligan()` reembaralhava a biblioteca com o módulo `random` GLOBAL
(sem seed própria) sempre que um 2º+ mulligan acontecia — `simulate_
one(seed)` **não era determinística**: 953/5.000 seeds (19,1%)
retornavam resultado diferente rodando a MESMA seed 2 vezes. Qualquer
`run_batch`/goldfishing anterior deste deck pode ter tido resultados
não totalmente reproduzíveis.

**Corrigido:** `state.rng` (mesmo padrão dos outros 11 decks) agora
alimenta TODA aleatoriedade do jogo, incluindo o reembaralhamento de
mulligan.

**Validação:** 0/N resultados diferentes depois do fix (era 953/5000
antes), confirmado via teste dirigido.

---

## Achado adicional: `state.life` nunca existiu neste arquivo — 2026-09-21

**Gatilho:** ao implementar a categoria "ataque de oponente" do modo
de resiliência, achei que este deck nunca rastreou a própria vida (nem
fetches/shock lands descontam) — diferente de todos os outros 11
decks. Simplificação pré-existente real, não um bug introduzido por
mim.

**Corrigido:** adicionado `life: int = 40` ao `GameState` (aditivo, só
usado pela nova categoria de ataque — não muda nenhum comportamento
pré-existente, confirmado pela bit-identidade 0/20000 acima).

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

---

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Megatron: oráculo
real via Scryfall pras 63 cartas + 20 terrenos + comandante, comparação
cláusula-por-cláusula contra o código, 9 gaps reais corrigidos (detalhes
completos em `checklist-oraculo.md`, seção no topo): mana colorida das 3
rocks (Signet/Talisman/Tablet) não contava pra checagem de cor; Grixis
Panorama crackeava de graça (devia custar `{1}`); 5 mágicas com "discard
a card" como custo adicional obrigatório podiam ser conjuradas com a mão
vazia; Fists of Flame tinha o pump fixo em +1/0 em vez de escalar com
cartas compradas no turno; Frantic Search não passava seus draws por
`draw_cards()` (undercounting de métricas) e descartava as cartas
ERRADAS (maior custo, não menor); o token do Firebender Ascension nunca
gerava o próprio mana de Firebending 1 ao atacar; Sazacap's Brew recusava
o gift sem necessidade (sem desvantagem real modelada pra dar o token ao
oponente); e Lunar Frenzy calculava o pump de X mas nunca gastava esse
mana de verdade (bug de mana fantasma reaproveitável).

### Métricas antes/depois (20.000 partidas, seed 5.000.000, turns=10, 0 exceções)

| Métrica | Antes | Depois |
|---|---|---|
| Dano proxy médio | 1586.2 | 2931.9 |
| Dano proxy mediano | 70.0 | 75.0 |
| Cartas compradas extra (média) | 28.0 | 30.4 |
| Treasures criados (média) | 12.4 | 15.8 |
| Cópias via Azula atacando (média) | 1.7 | 1.8 |
| Dobras via Veyran (média) | 8.9 | 10.7 |
| Biblioteca esgotada | 2695/20000 (13.5%) | 3207/20000 (16.0%) |

A mediana subiu pouco (~7%, o jogo "típico" mudou pouco) — a média subiu
bem mais porque os gaps corrigidos (mais mana colorida real disponível
via rocks, X realmente pago, Fists escalando de verdade) alimentam ainda
mais a cauda extrema do combo Zada+Veyran+Storm-Kiln Artist já documentado
acima, não porque o comportamento típico do deck mudou de categoria.

