"""
Teste comparativo pareado (mesmas seeds), n=10.000 por variante — Radagast
of Rhosgobel dentro vs. fora do deck da Ulalek, Fused Atrocity.

Pergunta do usuario (2026-08-30): "Considerando o efeito do Ulalek que
custa 2 incoloras e duplica spells do tipo Eldrazi, o radagst seria uma
otima inclusao?" — a premissa merece uma correcao antes do teste: Radagast
of Rhosgobel e Legendary Creature — Avatar Wizard, NAO e Eldrazi. Conjura-lo
NUNCA dispara o gatilho de copia da Ulalek ("Whenever you cast an Eldrazi
spell..."), e a propria habilidade dele (desconto + flash pra 1a criatura
do turno) tambem nunca e copiada por nada do motor de duplicacao do deck
(Ulalek/Echoes of Eternity so copiam spells/gatilhos Eldrazi ou colorless
— Radagast e nenhum dos dois). Ja confirmado no teste pareado anterior
(`ulalek_radagast_test.py`, 2026-08-23) e reconfirmado no oraculo fresco
(2026-08-30): Radagast NAO alimenta o motor central da comandante. Este
teste mede o valor real dele (desconto de custo + flash pra 1a criatura)
isoladamente, sem essa suposicao errada.

======================================================================
Metodologia — substituicao POSICIONAL, nao list.remove()+append()
======================================================================
Regra obrigatoria deste repositorio desde o achado do Ur-Dragon/Magda
(2026-08-29, ver `references/goldfish-sim-card-rules.md`): construir cada
variante via `str.replace()` na linha exata da carta cortada dentro do
TEXTO de `lista.md`, reparseando do zero com a mesma logica de
`build_library()` — nunca `list.remove(); list.append()` (isso quebra o
pareamento de seed porque `rng.shuffle()` depende da posicao de cada carta
na lista original, nao so do conteudo). O teste anterior desta sessao
(2026-08-23) usava o metodo antigo (`.remove()+.append()`) porque foi
escrito ANTES dessa regra existir — refeito aqui com o metodo correto.

======================================================================
3 candidatas a corte pra abrir espaco pro Radagast, em ordem de importancia
======================================================================
1. **Null Elemental Blast** ({C} instant — "Counter target multicolored
   spell. / Destroy target multicolored permanent.") — a carta mais
   estreita de toda a lista de 99: so tem alvo legal contra spells/
   permanentes MULTICOLORIDOS especificamente. Contra um oponente mono ou
   bicolor "errado", e literalmente uma carta morta na mao o jogo inteiro.
   Nenhuma outra carta do deck depende dela pra funcionar. Corte mais
   seguro.
2. **Defense of the Heart** (4 mana, enchantment — "At the beginning of
   your upkeep, if an opponent controls three or more creatures,
   sacrifice this enchantment, search your library for up to two creature
   cards, put those cards onto the battlefield, then shuffle.") — depende
   de uma condicao real do OPONENTE (3+ criaturas em campo dele) que pode
   nunca acontecer, especialmente contra mesas com poucas criaturas
   (control, spellslinger) ou cedo no jogo. Quando dispara e' excelente
   (2 Eldrazi grandes de graca), mas e' uma aposta condicional de 4 mana,
   nao um efeito garantido — ao contrario do Radagast, que e' valor toda
   vez que resolve.
3. **Morophon, the Boundless** (7 mana, Legendary Creature — Shapeshifter)
   — o desconto real ("Spells of the chosen type cost {W}{U}{B}{R}{G}
   less... reduz so' mana colorida") so' ajuda cartas com pips coloridos
   de verdade: neste deck, isso e' Chittering Dispatcher {2}{G}, Sowing
   Mycospawn {3}{G}, Void Grafter {1}{G}{U}, World Breaker {6}{G},
   Writhing Chrysalis {2}{R}{G} — 5 cartas ja baratas (3-7 mana). As
   bombas de custo alto do deck (Kozilek x3, Ulamog x2, Emrakul, Void
   Winnower, Sire of Seven/Stagnation) sao TODAS custo generico puro, sem
   pip colorido nenhum pra Morophon reduzir. 7 mana por um upside
   concentrado em cartas que ja sao as mais baratas da lista e' o corte
   mais debatavel dos 3, mas ainda assim o de menor retorno-por-mana.
"""

import re
import statistics

import ulalek_goldfish_v1 as sim


def build_library_from_text(text: str) -> list:
    """Mesma logica de sim.build_library(), mas recebendo o texto direto
    (permite reparsear uma versao editada de lista.md sem tocar o arquivo
    em disco)."""
    lib = []
    for l in text.splitlines():
        l = l.strip()
        if not l or l.startswith("#"):
            continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if not m:
            continue
        qty, name = int(m.group(1)), m.group(2).strip()
        if name == sim.COMMANDER:
            continue
        assert name in sim.CARD_DB, f"faltando no CARD_DB: {name}"
        for _ in range(qty):
            lib.append(name)
    assert len(lib) == 99, len(lib)
    return lib


def build_variant_library(base_text: str, cut_name: str, add_name: str) -> list:
    old_line = f"1 {cut_name}"
    new_line = f"1 {add_name}"
    assert base_text.count(old_line) == 1, f"linha nao encontrada 1x: {old_line!r}"
    new_text = base_text.replace(old_line, new_line, 1)
    return build_library_from_text(new_text)


def run_variant(seed_base: int, n: int, library: list, turns: int = 8):
    original = sim.BASE_LIBRARY
    sim.BASE_LIBRARY = library
    try:
        states = [sim.simulate_one(seed_base + i, turns=turns) for i in range(n)]
    finally:
        sim.BASE_LIBRARY = original
    return states


def avg(vals):
    return sum(vals) / len(vals) if vals else 0.0


METRICS = [
    ("cmd_turn_avg", "Turno medio de conjuracao da Ulalek",
     lambda ss, n: avg([s.commander_cast_turn for s in ss if s.commander_cast_turn is not None])),
    ("never_cast_pct", "Nunca conjurada em 8 turnos (%)",
     lambda ss, n: 100 * sum(1 for s in ss if s.commander_cast_turn is None) / n),
    ("ulalek_copies_avg", "Avg copias pagas da Ulalek (CC)",
     lambda ss, n: avg([s.ulalek_copies_total for s in ss])),
    ("spell_copies_avg", "Avg tokens-copia de permanentes",
     lambda ss, n: avg([s.spell_token_copies_total for s in ss])),
    ("cast_trigger_extra_avg", "Avg resolucoes extras de cast-trigger",
     lambda ss, n: avg([s.cast_trigger_extra_resolutions_total for s in ss])),
    ("draw_avg", "Avg cartas compradas extra",
     lambda ss, n: avg([s.cards_drawn_extra for s in ss])),
    ("cascade_avg", "Avg cascade cascade (Zhulodok)",
     lambda ss, n: avg([s.cascades_total for s in ss])),
    ("flash_online_avg", "Avg turnos com flash online (qualquer fonte)",
     lambda ss, n: avg([s.flash_online_turns for s in ss])),
    ("first_creature_discount_avg", "Avg descontos 'primeira criatura do turno'",
     lambda ss, n: avg([s.first_creature_discount_events_total for s in ss])),
    ("radagast_flash_grants_avg", "Avg flash concedido pelo Radagast",
     lambda ss, n: avg([s.radagast_flash_grants_total for s in ss])),
    ("interaction_avg", "Avg spells de interacao conjurados (proxy)",
     lambda ss, n: avg([s.interaction_spells_cast_total for s in ss])),
    ("fleshraker_dmg_avg", "Avg dano proxy via Glaring Fleshraker",
     lambda ss, n: avg([s.glaring_fleshraker_damage_total for s in ss])),
    ("all_is_dust_pct", "% de jogos que conjuraram All Is Dust",
     lambda ss, n: 100 * sum(1 for s in ss if s.all_is_dust_cast) / n),
    ("all_is_dust_self_sac_avg", "Avg permanentes proprios sacrificados por All Is Dust (nesses jogos)",
     lambda ss, n: avg([s.all_is_dust_self_sacrificed for s in ss if s.all_is_dust_cast])),
    ("final_hand_avg", "Avg mao final",
     lambda ss, n: avg([len(s.hand) for s in ss])),
]


def summarize(label, states, n):
    print(f"--- {label} (n={n}) ---")
    result = {}
    for key, desc, fn in METRICS:
        val = fn(states, n)
        result[key] = val
        print(f"{desc}: {val:.3f}")
    print()
    return result


def compare(cut_name: str, base_text: str, seed_base: int, n: int, baseline_result: dict, states_baseline):
    lib_with = build_variant_library(base_text, cut_name, "Radagast of Rhosgobel")
    states_with = run_variant(seed_base, n, lib_with)
    r_with = summarize(f"COM Radagast (corta 1x '{cut_name}')", states_with, n)

    print(f"=== Delta (COM Radagast via corte de '{cut_name}') — (COM - SEM) ===")
    for key, desc, _ in METRICS:
        d = r_with[key] - baseline_result[key]
        print(f"{desc}: {d:+.3f}")
    print()
    print("=" * 78)
    print()
    return r_with


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    N = 10000
    SEED_BASE = 5500000
    base_text = open("lista.md").read()

    print(f"n={N} por variante, seed_base={SEED_BASE}, turns=8 (mesmas seeds em todas as variantes)")
    print()

    lib_baseline = build_library_from_text(base_text)
    assert lib_baseline == sim.BASE_LIBRARY, "lista.md mudou desde o import do modulo"
    states_baseline = run_variant(SEED_BASE, N, lib_baseline)
    r_baseline = summarize("SEM Radagast (baseline, lista.md atual)", states_baseline, N)

    print("=" * 78)
    print()

    CANDIDATES = ["Null Elemental Blast", "Defense of the Heart", "Morophon, the Boundless"]
    results = {}
    for cand in CANDIDATES:
        results[cand] = compare(cand, base_text, SEED_BASE, N, r_baseline, states_baseline)
