"""Frequencia de cada uma das 3 mudancas de 2026-10-22 (rodada 1), SO' dos brutos arquivados (`dados/raw_ab_10000[_resiliencia].json.xz`, variante `depois`): partidas com >= 1 evento e total por partida.
Uso: python3 resumo_politicas.py"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
CAMPOS = [("m_tam_attacks", "ataques da Tam"), ("m_tamiyo_combat_draws", "compras da Tamiyo por dano de combate"), ("m_aminatou_mana_blinks", "Aminatou -1 desvira permanente de mana"),
          ("m_kitten_mana_blinks", "Kitten desvira permanente de mana"), ("m_saheeli_creature_mana_copies", "Saheeli copia criatura de mana"), ("m_saheeli_trigger_copies", "Saheeli copia Flux Channeler/Kitten"),
          ("m_saheeli_staff_copies", "Saheeli copia o Staff of Compleation")]
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    r = [x[1] for x in A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_10000{suf}"))["depois"]]
    n = len(r)
    print(f"\n== modo {modo}, N={n} (variante `depois`: as 3 chaves ligadas) ==")
    print("   evento                                         partidas com >= 1      total por partida")
    for c, nome in CAMPOS:
        v = [x.get(c, 0) for x in r]
        k = sum(1 for a in v if a > 0)
        print(f"   {nome:46s} {k:6d} ({100 * k / n:6.2f}%)   {sum(v) / n:8.4f}")
