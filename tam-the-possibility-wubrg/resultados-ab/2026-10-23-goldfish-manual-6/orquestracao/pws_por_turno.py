"""Planeswalkers em campo no FIM de cada turno do goldfish manual #6, SO' do bruto (dados/goldfish_manual_6_bruto.json), por INTERVALO de presenca de cada permanente (id do playtester):
entra num evento `* -> battlefield`, sai num evento `battlefield -> <outra zona>`, OU quando o mesmo id entra de novo da mao (clique desfeito: o log nao registra desfazer, mas a 2a entrada prova que a 1a
nao ficou). Ficha de Jace = nome "Jace" com token=True. Sem a premissa nenhuma: o que o log permite concluir.
Sobre a ficha de Jace do T4 (id Yap1mo...): NAO tem evento de saida, mas no T8 o Sanctum Lurker (empower Jace 1) cria uma ficha NOVA (outro id): pela regra (so' se cria ficha se nao se controla uma) ela ja'
nao estava em campo no T8. Sem a flag, conto a ficha ate' o T7; `--premissa-fracture` conta a saida no T4 (a Fracture do oponente e' o unico evento de oponente que pode te-la tirado; o usuario nao lembra o alvo).
Este script e' ESPECIFICO deste log (prefixo de id `Yap1mo` e turno de saida 4/8 da ficha de Jace do T4 estao fixos de proposito).
Nota de 2026-10-29: o bloco T11 contem DOIS inicios de turno (o turno extra do Oko, jogado a mao; ver `testes/t_manual6.py`, duvida 6); a contagem "T11" e' a do FIM do bloco, isto e, do fim do turno extra.
Uso: python3 pws_por_turno.py [--premissa-fracture]"""
import json, os, sys, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, DECK)
import tam_goldfish_v1 as T

log = json.load(open(os.path.join(AQUI, "..", "dados", "goldfish_manual_6_bruto.json")))
PREMISSA = "--premissa-fracture" in sys.argv


def eh_pw(e):
    n = e["name"]
    return (e.get("token") and n == "Jace") or (n in T.CARD_DB and "planeswalker" in T.CARD_DB[n].types)


def intervalos():
    """id -> lista de [turno_de_entrada, turno_de_saida (a partir dele NAO esta' em campo; None = segue), nome, lealdade]."""
    iv = collections.defaultdict(list)
    aberto = {}
    for t, blk in enumerate(log, 1):
        for e in blk:
            if not eh_pw(e):
                continue
            i, fz, tz = e["id"], e["fromZone"], e["toZone"]
            if tz == "battlefield" and fz != "battlefield":
                if i in aberto:                        # entrou de novo da mao: a 1a entrada foi DESFEITA (clique), no mesmo turno em que comecou (apoio: aritmetica da mao no fim do turno)
                    aberto[i][1] = aberto[i][0]
                    aberto.pop(i)
                x = [t, None, e["name"], (e.get("counters", {}).get("Loyalty") or {}).get("count")]
                iv[i].append(x); aberto[i] = x
            elif fz == "battlefield" and tz != "battlefield" and i in aberto:
                aberto[i][1] = t
                aberto.pop(i)
            if i in aberto:
                aberto[i][3] = (e.get("counters", {}).get("Loyalty") or {}).get("count", aberto[i][3])
    for i, lst in iv.items():
        if i.startswith("Yap1mo") and lst[-1][1] is None:
            lst[-1][1] = 4 if PREMISSA else 8       # sem evento de saida: no T8 ja' nao existia (o Lurker criou uma ficha NOVA); com a premissa, a Fracture do T4 a tirou
    return iv


def contagem():
    iv = intervalos()
    out = {}
    for t in range(1, len(log) + 1):
        out[t] = sorted(nome for lst in iv.values() for ent, sai, nome, _ in lst if ent <= t and (sai is None or t < sai) and sai != ent)
    return out


if __name__ == "__main__":
    c = contagem()
    print("turno | planeswalkers em campo no fim do turno (so' do bruto" + ("; premissa: Jace Yap1mo saiu no fim do T4" if PREMISSA else "; Jace Yap1mo: sem saida no log, mas ausente no T8") + ")")
    for t, nomes in c.items():
        print(f"T{t:2d} | {len(nomes)} | {', '.join(nomes)}")
