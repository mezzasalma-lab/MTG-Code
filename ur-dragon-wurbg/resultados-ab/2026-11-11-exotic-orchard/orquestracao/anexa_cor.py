"""Anexa ao LEIAME.md e ao goldfish-log.md do Ur-Dragon a leitura de COR (o efeito do proxy da Exotic Orchard neste deck aparece em `color_screw`, nao no comandante),
lendo os numeros de resumos/ab_10000{,_resiliencia}.txt (nada digitado a mao). Idempotente (aborta se a secao ja' existe).
Uso (raiz do repositorio): python3 -I ur-dragon-wurbg/resultados-ab/2026-11-11-exotic-orchard/orquestracao/anexa_cor.py"""
import os, re
D = "ur-dragon-wurbg/resultados-ab/2026-11-11-exotic-orchard"
def campo(t, nome):
    m = re.search(r"^\s*\*?\s*" + re.escape(nome) + r"\s+([\d.]+)\s+([\d.]+)\s+([+-][\d.]+) ±([\d.]+)", t, re.M)
    assert m, nome
    return [float(x) for x in m.groups()]
def br(x, nd): return f"{x:.{nd}f}".replace(".", ",")
r = {}
for modo, suf in (("padrão", ""), ("resiliência", "_resiliencia")):
    t = open(f"{D}/resumos/ab_10000{suf}.txt", encoding="utf-8").read()
    r[modo] = (campo(t, "color_screw_turns"), campo(t, "first_color_screw_turn__nunca"), campo(t, "first_color_screw_turn__ate_T4"))
def linha(modo):
    cs, nu, t4 = r[modo]
    return (f"{modo}: `color_screw_turns` {br(cs[0],4)} → {br(cs[1],4)} (**{br(cs[2],4)} ±{br(cs[3],4)} turnos com falta de cor por partida**); "
            f"partidas que NUNCA tiveram falta de cor {br(nu[0]*100,2)}% → {br(nu[1]*100,2)}% (**{br(nu[2]*100,2)} ±{br(nu[3]*100,2)} pontos**); falta de cor até o T4 {br(t4[2]*100,2)} ±{br(t4[3]*100,2)} pontos")
texto = ("## Onde o efeito aparece neste deck: a cor, não o comandante\n"
         "O comandante (MV 9) quase nunca sai até o T4 (2,3% das partidas), então a coluna do comandante é pequena por construção. O que o proxy mexe é a **falta de cor** (N = 10.000, pareado, `resumos/ab_10000*.txt`):\n"
         f"- {linha('padrão')}.\n- {linha('resiliência')}.\n"
         "Leitura: a Exotic Orchard em campo deixa de ser terreno sem cor num deck de 5 cores. Em partidas sem ela o resultado é idêntico (bit-identidade).\n")
for arq, marca in ((f"{D}/LEIAME.md", "## Não coberto (Regra #7)"), ("ur-dragon-wurbg/goldfish-log.md", "- **Os números anteriores do deck foram medidos com a Orchard sem cor**")):
    s = open(arq, encoding="utf-8").read()
    assert "Onde o efeito aparece neste deck" not in s, f"{arq}: ja' tem a secao (idempotencia)"
    assert s.count(marca) == 1, (arq, marca, s.count(marca))
    sec = texto if arq.endswith("LEIAME.md") else texto.replace("## Onde", "- **Onde", 1).replace("cor, não o comandante\n", "cor, não o comandante:** ", 1).replace("\n- ", "\n  - ").replace("\nLeitura", "\n  Leitura") + ""
    s = s.replace(marca, sec + ("\n" if arq.endswith("LEIAME.md") else "") + marca, 1)
    open(arq, "w", encoding="utf-8").write(s)
print("anexado")
