"""Extrai os trechos das Comprehensive Rules citados na partida manual #3 do Wise Mothman de rules-cache/comprehensive-rules.txt (regra permanente §18).
Uso: python3 -I extrair_cr_trechos.py > resumos/cr_trechos.txt"""
import os
aqui = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(aqui, "..", "..", "..", "..", "rules-cache", "comprehensive-rules.txt"), encoding="utf-8-sig").read().replace("\r", "")
lines = t.split("\n")
def rule(num):
    for i, l in enumerate(lines):
        if l.startswith(num + " ") or (l.startswith(num + ".") and l.split(" ")[0].rstrip(".") == num):
            out = [l]
            for m in lines[i + 1:i + 12]:
                if m.strip() == "":
                    break
                out.append(m)
            return "\n".join(out)
    return "NAO ACHADO"
head = [l for l in lines[:8] if l.strip()]
out = ["# Trechos das Comprehensive Rules citados na partida manual #3 do Wise Mothman (extraidos de rules-cache/comprehensive-rules.txt)", "# " + " | ".join(head[:3]), ""]
for n in ["728.1", "702.81a", "701.17a", "305.2", "122.1i"]:
    out.append(rule(n)); out.append("")
print("\n".join(out), end="")
