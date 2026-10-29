"""Extrai por script (sem redigitar) o JSON do Archidekt playtester que o usuario colou na conversa (registro .jsonl da sessao).
A mensagem chegou no MEIO de um turno do assistente, e o registro a guarda como `attachment` (nao como mensagem `user`): por isso o script olha as duas formas.
Uso: python3 extrair_json_da_conversa.py <saida.json> [<transcript.jsonl>]   (a ultima mensagem com 'Mais um goldfish' e 'Freestrider Lookout')."""
import json, sys
T = sys.argv[2] if len(sys.argv) > 2 else "/root/.claude/projects/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f.jsonl"
dec = json.JSONDecoder()
last = None
def textos(o):
    m = o.get("message") or {}
    if m.get("role") == "user":
        c = m.get("content")
        yield c if isinstance(c, str) else "".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text") if isinstance(c, list) else ""
    a = o.get("attachment")
    if isinstance(a, dict):
        p = a.get("prompt")
        yield p if isinstance(p, str) else "".join(b.get("text", "") for b in p if isinstance(b, dict) and b.get("type") == "text") if isinstance(p, list) else ""
with open(T) as f:
    for line in f:
        try:
            o = json.loads(line)
        except Exception:
            continue
        for txt in textos(o):
            if "Mais um goldfish" in txt and "Freestrider Lookout" in txt and "[\n  [" in txt:
                last = txt
assert last, "mensagem nao encontrada"
i = last.index("[\n  [")
data, end = dec.raw_decode(last[i:])
assert len(data) > 0 and all(isinstance(t, list) and t for t in data)
print(len(data), "turnos;", sum(len(t) for t in data), "registros;", "texto antes do JSON:", repr(last[max(0, i - 300):i]), "| texto apos o JSON:", repr(last[i + end:i + end + 300]), file=sys.stderr)
json.dump(data, open(sys.argv[1], "w"), ensure_ascii=False, indent=2)
