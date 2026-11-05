"""Extrai, do registro da conversa (transcript .jsonl da sessao), a mensagem do usuario com o JSON do goldfish manual #12 do Tom Bombadil, SEM redigitar:
grava a mensagem inteira (`mensagem_usuario_original.txt`) e o JSON puro (`partida.json`). Uso: python3 -I extrair_json_da_conversa.py <transcript.jsonl> <pasta de saida>"""
import json, sys, os
T, OUT = sys.argv[1], sys.argv[2]
dec = json.JSONDecoder(); last = None
with open(T, "r") as f:
    for line in f:
        try: o = json.loads(line)
        except Exception: continue
        m = o.get("message") or {}
        if m.get("role") != "user": continue
        c = m.get("content"); txt = ""
        if isinstance(c, str): txt = c
        elif isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text": txt += b.get("text", "")
        if "MAIS UM GOLDFISH MANUAL DO TOM BOMBADIL" in txt and "Ketria Triome" in txt and "Karn's Bastion" in txt:
            last = txt
assert last, "mensagem nao encontrada no transcript"
i = last.index("[\n  [")
data, end = dec.raw_decode(last[i:])
open(os.path.join(OUT, "mensagem_usuario_original.txt"), "w", encoding="utf-8").write(last)
json.dump(data, open(os.path.join(OUT, "partida.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("mensagem:", len(last), "caracteres | turnos (elementos):", len(data), "| eventos por turno:", [len(t) for t in data], "| depois do JSON:", repr(last[i + end:].strip()[:80]), "| antes:", repr(last[:i].strip()[:80]))
