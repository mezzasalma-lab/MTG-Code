"""Extrai por script (sem redigitar) o JSON do Archidekt playtester que o usuario colou na conversa (registro .jsonl da sessao).
A mensagem pode estar guardada como mensagem `user` ou como `attachment` (quando chega no meio de um turno do assistente): o script olha as duas formas.
Uso: python3 -I extrair_json_da_conversa.py <transcript.jsonl> <pasta_saida>
Grava <pasta_saida>/partida.json e <pasta_saida>/mensagem_usuario_original.txt (a ultima mensagem com 'Wise Mothman', 'Altar of the Brood' e 'Zagoth Triome')."""
import json, os, sys
T, OUT = sys.argv[1], sys.argv[2]
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
            if "Wise Mothman" in txt and "Altar of the Brood" in txt and "Zagoth Triome" in txt and "[\n  [" in txt:
                last = txt
assert last, "mensagem nao encontrada"
i = last.index("[\n  [")
data, end = dec.raw_decode(last[i:])
assert len(data) > 0 and all(isinstance(t, list) and t for t in data)
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "mensagem_usuario_original.txt"), "w", encoding="utf-8").write(last)
json.dump(data, open(os.path.join(OUT, "partida.json"), "w"), ensure_ascii=False, indent=2)
print(len(data), "turnos;", sum(len(t) for t in data), "registros; eventos por turno:", [len(t) for t in data])
print("texto antes do JSON:", repr(last[max(0, i - 300):i]))
print("texto apos o JSON:", repr(last[i + end:i + end + 300]))
