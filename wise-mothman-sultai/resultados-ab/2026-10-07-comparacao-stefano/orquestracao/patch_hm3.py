import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
# 16) sensibilidade: quantas vezes o Horrigan prolifera (2 = oraculo; 0 = so' o corpo 8/6 trample, para separar corpo de proliferate)
sub('''MASTER_OPP_TURN = True ''', '''HORRIGAN_PROLIF_TIMES = 2    # "proliferate twice" (oraculo). 0 = sensibilidade: so' o corpo (8/6 trample, indestrutivel ao atacar), sem proliferate
MASTER_OPP_TURN = True ''')
sub('''        state.horrigan_etb_prolifs += 1
        proliferate(state, "horrigan_etb", times=2)''', '''        state.horrigan_etb_prolifs += 1
        if HORRIGAN_PROLIF_TIMES > 0:
            proliferate(state, "horrigan_etb", times=HORRIGAN_PROLIF_TIMES)''')
sub('''            proliferate(state, "horrigan_attack", times=2)''', '''            if HORRIGAN_PROLIF_TIMES > 0:
                proliferate(state, "horrigan_attack", times=HORRIGAN_PROLIF_TIMES)''')
open(p, "w", encoding="utf-8").write(s)
print("ok3")
