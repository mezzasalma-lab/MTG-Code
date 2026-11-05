"""Extrai os trechos das Comprehensive Rules citados no goldfish manual #12 de rules-cache/comprehensive-rules.txt (já no repositório, regra permanente §18).
Conferência de 2026-11-05: a CR baixada de https://media.wizards.com/2026/downloads/MagicCompRules%2020260925.txt (link da página https://magic.wizards.com/en/rules)
é IDÊNTICA byte a byte (sha256 8d860e45...70ca) ao rules-cache, então a cópia baixada não foi duplicada no repositório.
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
out = ["# Trechos das Comprehensive Rules citados no goldfish manual #12 (extraídos de rules-cache/comprehensive-rules.txt, CR em vigor desde 2026-09-25; idêntica à baixada de media.wizards.com em 2026-11-05)", "# " + " | ".join(head[:3]), ""]
for n in ["714.2b", "714.3c", "714.4", "117.5", "603.2", "603.3", "603.3b", "307.5", "602.5d", "702.62a", "903.8", "701.54a", "701.54c", "302.6"]:
    out.append(rule(n))
    out.append("")
print("\n".join(out), end="")
