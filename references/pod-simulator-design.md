# Design do motor de mesa (pod de 4 jogadores) — Fase 0

Pedido do usuário (2026-09-02): simular uma mesa real de 4 jogadores,
cada um pilotando um deck diferente, pra análise — não mais goldfish
solo. Combinado explicitamente que isso seria construído **em fases**,
cada uma entregando algo testável sozinho, pra não queimar orçamento
numa coisa grande que não termina em nada usável.

**Mesa alvo (confirmada 2026-09-02):** Edgar Markov vs Ur-Dragon vs Toph
vs Maralen. São os 4 simuladores mais complexos do repositório inteiro
(Toph 2.724 linhas, Edgar Markov 2.575, Ur-Dragon 2.207, Maralen 1.528 —
maiores que qualquer um dos exemplos usados nas seções abaixo), o que
torna a Fase 4 (plugar esses 4 de verdade) a etapa mais trabalhosa do
projeto. Por isso a Fase 1 (prova de conceito do encanamento) usa 2
decks bem mais simples só pra validar a arquitetura barato antes de
investir nos 4 grandes — ver seção 8.

Este documento é só a **Fase 0**: o contrato de estado e as decisões de
arquitetura. Nenhum motor de turno é escrito aqui — isso é Fase 1.

---

## 1. Por que isso não é "estender os 17 simuladores"

Os simuladores atuais (`*_goldfish_v1.py`, um por deck) são **solo**:
não existe vida, mão ou board de oponente real. Toda carta que depende
de oponente (remoção, contramágica, Rhystic Study, Smothering Tithe...)
está marcada 📊 e nunca executa de verdade — não porque a carta não
importa, mas porque não há pra quem apontar.

Um motor de mesa real precisa de:
1. Estado de vida/mão/board **real** pra 4 jogadores simultâneos.
2. Ordem de turno real entre eles.
3. Decisão real de alvo (quem cada remoção/contramágica mira), de
   bloqueio (o defensor decide) e de reação (contramágica/instant em
   resposta).

Isso é maior que qualquer deck individual já construído nesta sessão —
por isso a divisão em fases.

---

## 2. Decisão central: **adaptador**, não reescrita

Os 17 decks já têm toda a lógica de carta escrita (`CARD_DB`, ETBs,
combate, ativadas) — mas em **duas arquiteturas diferentes**:

- **Objetos `Permanent`** (Toph, Kutzil, Captain Storm, Ms. Bumbleflower)
  — contadores +1/+1 persistentes e equipamentos anexados exigem
  rastrear estado por permanente específico. Da mesa alvo, só a **Toph**
  usa esse padrão.
- **Lista de nomes** (Edgar Markov, Ur-Dragon, Maralen, Azula, Megatron,
  a maioria dos outros) — mais simples, suficiente quando não há
  contador persistente pra rastrear. Os outros 3 da mesa alvo (Edgar
  Markov, Ur-Dragon, Maralen) usam esse padrão.

Reescrever os 4 decks pedidos (Edgar Markov, Ur-Dragon, Toph, Maralen —
juntos, ~9.400 linhas) num motor unificado do zero jogaria fora toda a
lógica de carta já testada e validada em 20.000 partidas cada. Em vez
disso, a
Fase 0 define um **adaptador fino**: cada deck continua com seu próprio
arquivo, `CARD_DB` e funções internas — só ganha uma casca pequena que
traduz chamadas do motor de mesa ("é sua vez", "escolha um alvo entre
estes", "você quer bloquear/reagir?") pras funções que o deck já tem,
substituindo os pontos que hoje são 📊 por decisões reais.

```
DeckAdapter (protocolo, um por deck):
    card_db: dict                      # CARD_DB do arquivo original, sem mudança
    take_turn(table, seat) -> None      # chama a logica de turno que ja existe,
                                         # mas lendo/escrevendo table.players[seat]
                                         # em vez de um GameState solo
    choose_attack_target(table, seat) -> int          # qual oponente atacar
    choose_block(table, seat, attacker_info) -> perm|None
    choose_removal_target(table, seat, candidates) -> perm|None
    react_with_counterspell(table, seat, spell_info) -> bool
```

Cada deck "vira adaptador" na Fase 4, um de cada vez — o trabalho por
deck é **religar os pontos 📊 existentes**, não recriar a carta do zero
(a leitura de oráculo, os testes unitários e a lógica em si já existem
e já foram validados).

---

## 3. Estado compartilhado

### `PlayerState`

```python
@dataclass
class PlayerState:
    seat: int                       # 0-3
    deck_id: str                    # "edgar_markov" | "ur_dragon" | "toph" | "maralen"
    life: int = 40
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)   # list[Permanent] -- ver secao 4
    graveyard: list = field(default_factory=list)
    library: list = field(default_factory=list)
    exile: list = field(default_factory=list)

    commander_in_play: bool = False
    commander_uid: Optional[int] = None
    commander_cast_count: int = 0

    lands_played_this_turn: int = 0
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0

    eliminated: bool = False        # vida <= 0
    extra: dict = field(default_factory=dict)   # campos especificos do deck
                                                  # (ex: state.tokens do Edgar Markov)
                                                  # -- evita um GameState gigante com
                                                  # campo de TODO deck existente
    metrics: dict = field(default_factory=dict)  # contadores que hoje sao atributos soltos
                                                   # em cada GameState viram entradas aqui
```

`extra` e `metrics` como dicts (em vez de dataclass fields fixos) é
deliberado: cada deck tem 15-30 campos únicos hoje no seu `GameState`
solo (ex.: o Edgar Markov já rastreia `tokens: List[str]` à parte pros
Vampiros 1/1 da Eminence) — forçar todos num `PlayerState` único infla
o schema compartilhado com campos que só 1 dos 4 decks usa. O adaptador
de cada deck lê/escreve seu próprio namespace dentro de `extra`/`metrics`,
e campos genuinamente específicos (como esse `tokens` do Edgar Markov)
continuam existindo do jeito que já existem, só dentro de `extra`.

### `TableState`

```python
@dataclass
class TableState:
    players: list          # 4x PlayerState, indice = seat
    turn_player: int = 0
    turn_number: int = 0
    rng: random.Random = field(default_factory=random.Random)
    log: list = field(default_factory=list)

    def opponents_of(self, seat: int) -> list[int]:
        return [p.seat for p in self.players if p.seat != seat and not p.eliminated]

    def alive_players(self) -> list[int]:
        return [p.seat for p in self.players if not p.eliminated]
```

---

## 4. Unificando `Permanent` entre os dois padrões

Da mesa alvo, 3 decks (Edgar Markov, Ur-Dragon, Maralen) tratam o campo
como `list[str]`; só a Toph usa objeto (`Permanent(card, uid, tapped,
counters, ...)`). Pra Fase 4 não exigir reescrever os 3 de lista-de-nomes
inteiros, a decisão é: **todo `battlefield` do motor de mesa usa
`Permanent`**, e o adaptador de cada deck de lista-de-nomes ganha uma
camada de tradução mínima (nome↔uid) só nos pontos onde ele precisa
saber "quem é esse permanente" pra decidir alvo/bloqueio — o resto da
lógica interna de cada um (cast, combate, ETBs) continua igual, olhando
só pros próprios nomes.

---

## 5. Modelo de prioridade — simplificado de propósito

Não vamos simular passar prioridade item a item como o Magic real (isso
sozinho é um motor à parte). Em vez disso, pontos de decisão **fixos**:

1. **No turno de um jogador**: só ele age (compra, joga terreno,
   conjura, ativa, ataca) — os outros 3 não têm janela de resposta
   espontânea.
2. **Bloqueio**: quando alguém é atacado, o defensor decide bloqueio via
   `choose_block()` — heurística, não busca no espaço de jogo.
3. **Reação a mágica**: antes de uma mágica resolver, cada oponente com
   contramágica disponível é perguntado via `react_with_counterspell()`
   — heurística simples (ex.: "tenho mana + o alvo é uma ameaça real? conto
   como sim"), não blefe nem sequenciamento ótimo.

Isso é uma simplificação deliberada, documentada — não "IA perfeita",
mas decisão real o suficiente pra interação genuína acontecer (ao
contrário de hoje, onde ela simplesmente não acontece).

---

## 6. Heurísticas de decisão (assinatura, não implementação ainda)

```python
def choose_target(table: TableState, acting_seat: int, candidates: list,
                   criterion: str = "best_value") -> object:
    """criterion: 'best_value' (maior ameaca), 'lowest_life' (jogador
    com menos vida), 'largest_board' (mais permanentes)."""

def should_block(table: TableState, defending_seat: int, attacker,
                  potential_blockers: list) -> Optional[object]:
    """Bloqueia se algum bloqueador mata o atacante sem perder mais
    valor do que ganharia deixando passar; senao None (leva o dano)."""

def should_react(table: TableState, seat: int, reaction_options: list) -> Optional[object]:
    """Usa a reacao disponivel (contramagica/instant) se o alvo/gatilho
    for avaliado como ameaca real (heuristica de 'valor' generica,
    reaproveitando o mesmo `creature_power`-like scoring que cada deck
    ja usa internamente pra escolher alvo proprio)."""
```

---

## 7. O que fica **fora** desta primeira versão (documentado, não esquecido)

- Blefe / informação oculta real (todo estado é visível pro motor, já
  que é simulação, não um jogo real entre pessoas).
- Pilha (stack) completa com respostas encadeadas — só o ponto de
  reação fixo da seção 5.
- Escolha de bloqueio múltiplo/otimizada (assume 1 bloqueador por
  atacante, o "melhor" disponível).
- Mana pool compartilhado entre passos — cada jogador só gasta na
  própria janela de ação.

Cada um desses pode virar uma fase futura se a análise pedir mais
fidelidade depois que a Fase 1-5 estiver rodando.

---

## 8. Fase 1 — ✅ concluída (2026-09-02)

Esqueleto de turno + combate real escrito em `pod-simulator/pod_engine_v1.py`,
validado com Nekusar-Grixis vs Rat King Verminister (os 2 simuladores
mais simples do repositório, nenhum dos dois faz parte da mesa alvo).
20.000 partidas, 0 exceções, ~46s. Resultados e limitações completas em
`pod-simulator/fase1-log.md` — resumo: a arquitetura funciona (vida
real, turno alternado, dano real com eliminação), mas **nenhum dos 2
decks de teste rastreia poder/toughness de criatura de forma
completa**, então o placar de "quem venceria" ali não deve ser lido
como sinal de força real — só como prova de que o encanamento roda.
Isso muda na Fase 4, quando decks com combate/P/T real entrarem
(Toph, que já rastreia toughness em objetos `Permanent`).

**Fase 1 foi deliberadamente mais simples que o schema `PlayerState`/
`TableState` rico descrito nas seções 3-6**: cada jogador manteve seu
`GameState` nativo intacto (zero risco de regressão), e o motor só
somou por cima vida real + roteamento de dano. O schema rico completo
(battlefield unificado em `Permanent`, adaptador por carta pra
remoção/contramágica mirando oponente real) é trabalho da Fase 2+.

## 9. Próximo passo (Fase 2)

Interação real (remoção, contramágica) entre os mesmos 2 decks de
teste — reconectar os pontos hoje 📊 pra mirar o oponente de verdade
usando o motor da Fase 1 como base. Escrito depois de confirmação do
usuário.
