"""
Motor de mesa (pod) — Fase 1: esqueleto de turno + combate real,
validado com 2 decks simples (Nekusar-Grixis, Rat King Verminister).

Ver `references/pod-simulator-design.md` (Fase 0) para o design
completo do motor final (4 jogadores, PlayerState/TableState ricos,
adaptador por deck). Este arquivo é deliberadamente mais simples que
aquele schema — Fase 1 só precisa provar 3 coisas:

1. Dois simuladores solo completamente independentes (cada um com seu
   próprio `GameState`, `CARD_DB`, `play_turn`) conseguem alternar
   turnos dentro de uma mesa compartilhada sem conflito.
2. Vida real (40 cada), dano real entre os dois (não mais proxy
   agregado sem alvo), com eliminação real quando vida <= 0.
3. Um combate real mínimo (poder de ataque real, bloqueio real, ainda
   que aproximado) acontece entre os dois boards.

Por isso NÃO existe aqui um `PlayerState`/`TableState` ricos com
`battlefield` unificado em `Permanent` — cada jogador mantém seu
`GameState` nativo intacto (zero risco de regressão nos 2 simuladores
já validados em 20.000 partidas cada), e este arquivo só adiciona por
cima: vida real, turno alternado, e a tradução de "quanto dano este
turno produziu" em dano real contra um oponente de verdade. Essa
tradução completa (schema PlayerState rico, adaptador por carta pra
remoção/contramágica mirando oponente real) é Fase 2+.

======================================================================
Achados de arquitetura reais (não previstos no design da Fase 0,
descobertos lendo o código de verdade dos 2 decks)
======================================================================
- **Nekusar assume NUM_OPPONENTS=3** (mesa de 4) em todo drenar/queimar
  — `proxy_damage_total` dele é a SOMA sobre 3 oponentes hipotéticos,
  não um número por-oponente. Pra rotear como dano real contra 1 único
  oponente (Fase 1 é só 2 jogadores), divide por `NUM_OPPONENTS`.
- **Rat King não tem essa convenção** — `proxy_damage_total` lá já é um
  total agregado simples, sem premissa de contagem de oponente.
  Aplicado direto, sem dividir.
- **Nekusar não tem plano de combate nenhum** (`combat_step` dele é
  literalmente `pass`) — é um deck 100% de drenar via gatilho de
  compra, não de atacar. Confirmado lendo o arquivo, não assumido.
- **Nenhum dos dois rastreia toughness de criatura** — Nekusar nem
  rastreia `power` (`Card` dele não tem esse campo, coerente com não
  ter combate real); Rat King tem `base_power` mas não toughness.
  Bloqueio "de verdade" (quem morre na troca) não é possível com os
  dados que esses 2 simuladores guardam hoje — só decks com objetos
  `Permanent` (Toph, por exemplo) têm isso. A heurística de bloqueio
  aqui é deliberadamente simples (seção `estimate_block_reduction`),
  documentada como aproximação a ser refinada quando decks com P/T
  real entrarem no pod.
"""

import os
import random
import sys
from dataclasses import dataclass, field
from typing import Optional

NEKUSAR_DIR = os.path.join(os.path.dirname(__file__), "..", "nekusar-grixis")
RATKING_DIR = os.path.join(os.path.dirname(__file__), "..", "rat-king-verminister")
sys.path.insert(0, NEKUSAR_DIR)
sys.path.insert(0, RATKING_DIR)

# Achado real: `nekusar_goldfish_v1.py` le' `lista.md` com caminho
# RELATIVO no import (`build_library()`, nivel de modulo), assumindo que
# o cwd e' a propria pasta do deck -- verdade quando ele roda sozinho,
# falso quando importado daqui. Troca de cwd so' durante o import de
# cada um (nao mexe no cwd do resto do processo).
_original_cwd = os.getcwd()
os.chdir(NEKUSAR_DIR)
import nekusar_goldfish_v1 as nekusar  # noqa: E402
os.chdir(_original_cwd)
os.chdir(RATKING_DIR)
import ratking_goldfish_v1 as ratking  # noqa: E402
os.chdir(_original_cwd)

MODULES = {
    "nekusar": nekusar,
    "ratking": ratking,
}

# Nomes de campos de token conhecidos por deck, com um poder estimado
# por token — a maioria dos geradores de token neste par é 1/1, usado
# como piso razoável documentado (não uma leitura de oráculo carta a
# carta, que é o próximo refino real quando a Fase 4 trouxer os 4 decks
# grandes de verdade).
TOKEN_FIELDS = {
    "nekusar": [],
    "ratking": ["rat_tokens", "squirrel_tokens", "mercenary_tokens"],
}


@dataclass
class PlayerState:
    seat: int
    deck_id: str
    module: object
    native_state: object
    life: int = 40
    eliminated: bool = False
    damage_dealt_total: int = 0
    drain_damage_dealt_total: int = 0
    combat_damage_dealt_total: int = 0
    turns_taken: int = 0


@dataclass
class TableState:
    players: list
    turn_number: int = 0
    rng: random.Random = field(default_factory=random.Random)
    log: list = field(default_factory=list)

    def opponents_of(self, seat: int) -> list:
        return [p for p in self.players if p.seat != seat and not p.eliminated]

    def alive_players(self) -> list:
        return [p for p in self.players if not p.eliminated]

    def winner(self) -> Optional["PlayerState"]:
        alive = self.alive_players()
        return alive[0] if len(alive) == 1 else None


def creature_power(module, name: str) -> int:
    card = module.CARD_DB[name]
    return getattr(card, "power", None) or getattr(card, "base_power", 0) or 0


def combat_power_this_turn(player: PlayerState) -> int:
    module, state = player.module, player.native_state
    total = sum(creature_power(module, n) for n in module.ready_creatures(state))
    for field_name in TOKEN_FIELDS.get(player.deck_id, []):
        total += getattr(state, field_name, 0) * 1  # piso de 1 poder por token, ver docstring
    return total


def estimate_block_reduction(defender: PlayerState) -> int:
    """Sem toughness real rastreada, aproxima bloqueio como '1 de dano
    abatido por criatura em campo do defensor' (chump-block genérico) —
    documentado como simplificação real da Fase 1, não combate
    matemático completo (ver docstring do topo)."""
    module, state = defender.module, defender.native_state
    blockers = sum(1 for n in state.battlefield if module.is_creature_card(n))
    for field_name in TOKEN_FIELDS.get(defender.deck_id, []):
        blockers += getattr(state, field_name, 0)
    return blockers


def choose_attack_target(table: TableState, attacker_seat: int) -> Optional[PlayerState]:
    opponents = table.opponents_of(attacker_seat)
    if not opponents:
        return None
    return min(opponents, key=lambda p: p.life)  # mira quem tem menos vida


def take_turn(table: TableState, player: PlayerState, is_first_turn: bool, on_play: bool):
    module, state = player.module, player.native_state

    drain_before = state.proxy_damage_total
    module.play_turn(state, is_first_turn=is_first_turn, on_play=on_play)
    player.turns_taken += 1
    drain_delta = state.proxy_damage_total - drain_before

    num_opponents = getattr(module, "NUM_OPPONENTS", None)
    real_drain = drain_delta // num_opponents if num_opponents else drain_delta

    real_combat = combat_power_this_turn(player)

    target = choose_attack_target(table, player.seat)
    if target is None:
        return

    real_combat = max(0, real_combat - estimate_block_reduction(target))

    total_damage = real_drain + real_combat
    if total_damage <= 0:
        return

    target.life -= total_damage
    player.drain_damage_dealt_total += real_drain
    player.combat_damage_dealt_total += real_combat
    player.damage_dealt_total += total_damage
    if target.life <= 0:
        target.eliminated = True

    table.log.append({
        "turn": table.turn_number,
        "actor": player.deck_id,
        "target": target.deck_id,
        "drain": real_drain,
        "combat": real_combat,
        "total": total_damage,
        "target_life_after": target.life,
        "target_eliminated": target.eliminated,
    })


def run_pod_game(seed: int, deck_ids: tuple, rounds: int = 10, starting_seat: int = 0) -> TableState:
    rng = random.Random(seed)
    players = []
    for seat, deck_id in enumerate(deck_ids):
        module = MODULES[deck_id]
        hand, lib, mulls = module.mulligan(rng)
        native_state = module.GameState(hand=hand, library=lib, mulligans=mulls)
        players.append(PlayerState(seat=seat, deck_id=deck_id, module=module, native_state=native_state))
    table = TableState(players=players, rng=rng)

    for round_num in range(rounds):
        table.turn_number = round_num + 1
        for player in table.players:
            if player.eliminated:
                continue
            if len(table.alive_players()) <= 1:
                return table
            is_first_turn = round_num == 0
            on_play = is_first_turn and player.seat == starting_seat
            take_turn(table, player, is_first_turn=is_first_turn, on_play=on_play)
    return table


def run_batch(n: int, seed_base: int, deck_ids: tuple, rounds: int = 10):
    exceptions = 0
    outcomes = {deck_id: 0 for deck_id in deck_ids}
    draws = 0
    turns_to_win = []
    for i in range(n):
        try:
            starting_seat = i % len(deck_ids)  # alterna quem comeca, evita vies de 1o jogador
            table = run_pod_game(seed_base + i, deck_ids, rounds=rounds, starting_seat=starting_seat)
        except Exception as e:
            exceptions += 1
            if exceptions <= 5:
                print(f"EXCEPTION seed={seed_base + i}: {e}")
            continue
        winner = table.winner()
        if winner is not None:
            outcomes[winner.deck_id] += 1
            turns_to_win.append(table.turn_number)
        else:
            draws += 1

    print(f"Rodadas: {n}, excecoes: {exceptions}")
    for deck_id in deck_ids:
        pct = 100 * outcomes[deck_id] / n
        print(f"Vitorias {deck_id}: {outcomes[deck_id]}/{n} ({pct:.1f}%)")
    print(f"Sem eliminacao em {rounds} rodadas: {draws}/{n} ({100 * draws / n:.1f}%)")
    if turns_to_win:
        print(f"Turno medio de eliminacao (quando houve): {sum(turns_to_win) / len(turns_to_win):.1f}")


if __name__ == "__main__":
    run_batch(2000, seed_base=1_000_000, deck_ids=("nekusar", "ratking"), rounds=10)
