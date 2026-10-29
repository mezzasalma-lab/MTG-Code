import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
# 14) Wave Goodbye: a criatura de oponente que a Master levou volta a MAO DO DONO (oponente), nunca a' minha
sub('''            if p.counters == 0 and not p.is_token and "commander" not in p.card.tags:
                state.battlefield.remove(p)
                state.hand.append(p.card.name)''', '''            if p.counters == 0 and "opp_card" in p.card.tags:
                state.battlefield.remove(p)
                state.opps[max(0, p.owner_idx - 1)].hand_size += 1            # "to its owner's hand": o dono e' o oponente
            elif p.counters == 0 and not p.is_token and "commander" not in p.card.tags:
                state.battlefield.remove(p)
                state.hand.append(p.card.name)''')
# 15) resiliencia: a Master e o Horrigan entram na lista de pecas que a remocao de oponente mira (logo depois da Muldrotha)
sub('''"Kami of Whispered Hopes", "Muldrotha, the Gravetide",
''', '''"Kami of Whispered Hopes", "Muldrotha, the Gravetide", "The Master, Transcendent", "Agent Frank Horrigan",
''')
open(p, "w", encoding="utf-8").write(s)
print("ok2")
