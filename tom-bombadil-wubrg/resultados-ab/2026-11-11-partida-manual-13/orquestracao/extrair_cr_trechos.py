"""Extrai os trechos das Comprehensive Rules citados no goldfish manual #13 de rules-cache/comprehensive-rules.txt (já no repositório, regra permanente §18).
Fonte: rules-cache/comprehensive-rules.txt (já no repositório, regra permanente §18; NADA foi baixado nesta rodada). A identidade desse arquivo com a CR oficial (media.wizards.com, 2026-09-25, sha256 8d860e45...70ca) foi conferida em 2026-11-05, na partida #12.
Uso: python3 -I extrair_cr_trechos.py > resumos/cr_2026-09-25_trechos.txt"""
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
out = ["# Trechos das Comprehensive Rules citados no goldfish manual #13 (extraídos de rules-cache/comprehensive-rules.txt, CR em vigor desde 2026-09-25; sem download nesta rodada)", "# " + " | ".join(head[:3]), ""]
for n in ["714.2b", "714.2d", "714.2e", "714.3c", "714.4", "704.3", "117.5", "603.2", "603.3b", "302.6", "305.2"]:
    out.append(rule(n))
    out.append("")
print("\n".join(out), end="")
