"""Extrai, do registro da conversa (transcript .jsonl da sessao), a mensagem do usuario com o JSON do goldfish manual #13 do Tom Bombadil, SEM redigitar:
grava a mensagem inteira (`mensagem_usuario_original.txt`) e o JSON puro (`partida.json`). A mensagem tambem traz respostas sobre o Mothman #3 (texto antes do JSON).
Uso: python3 -I extrair_json_da_conversa.py <transcript.jsonl> <pasta de saida>"""
import json, sys, os
T, OUT = sys.argv[1], sys.argv[2]
dec = json.JSONDecoder(); last = None
def textos(o):
    m = o.get("message") or {}
    if m.get("role") == "user":
        c = m.get("content")
        yield c if isinstance(c, str) else "".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text") if isinstance(c, list) else ""
    a = o.get("attachment")
    if isinstance(a, dict):
        p = a.get("prompt")
        yield p if isinstance(p, str) else "".join(b.get("text", "") for b in p if isinstance(b, dict) and b.get("type") == "text") if isinstance(p, list) else ""
with open(T, "r") as f:
    for line in f:
        try: o = json.loads(line)
        except Exception: continue
        for txt in textos(o):
            if "Tom Bombad" in txt and "Wooded Foothills" in txt and "Satsuki, the Living Lore" in txt and "[\n  [" in txt:
                last = txt
assert last, "mensagem nao encontrada no transcript"
i = last.index("[\n  [")
data, end = dec.raw_decode(last[i:])
assert len(data) > 0 and all(isinstance(t, list) and t for t in data)
open(os.path.join(OUT, "mensagem_usuario_original.txt"), "w", encoding="utf-8").write(last)
json.dump(data, open(os.path.join(OUT, "partida.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("mensagem:", len(last), "caracteres | turnos (elementos):", len(data), "| registros:", sum(len(t) for t in data), "| eventos por turno:", [len(t) for t in data], "| depois do JSON:", repr(last[i + end:].strip()[:80]))
print("antes do JSON (ultimos 400 caracteres):", repr(last[max(0, i - 400):i]))
