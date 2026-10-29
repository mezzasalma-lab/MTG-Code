"""Extrai por script (sem redigitar) o JSON do Archidekt playtester que o usuario colou na conversa em 2026-10-03
("Assumi algumas mortes em combate para gerar tesouros com o Mahadi ..."). Uso: python3 extrair_json_da_conversa.py saida.json"""
import json, sys
T = '/root/.claude/projects/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f.jsonl'
dec = json.JSONDecoder()
last = None
with open(T, 'r') as f:
    for line in f:
        try:
            o = json.loads(line)
        except Exception:
            continue
        m = o.get('message') or {}
        if m.get('role') != 'user':
            continue
        c = m.get('content')
        txt = c if isinstance(c, str) else ''.join(b.get('text', '') for b in (c or []) if isinstance(b, dict) and b.get('type') == 'text')
        if 'Assumi algumas mortes em combate' in txt and 'Boros Charm' in txt:
            last = txt
print(len(last) if last else None, file=sys.stderr)
i = last.index('[\n  [')
data, end = dec.raw_decode(last[i:])
print(len(data), 'turnos;', sum(len(t) for t in data), 'registros', file=sys.stderr)
json.dump(data, open(sys.argv[1], 'w'), ensure_ascii=False)
