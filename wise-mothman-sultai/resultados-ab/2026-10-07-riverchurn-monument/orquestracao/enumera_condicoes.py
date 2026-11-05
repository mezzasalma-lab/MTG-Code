#!/usr/bin/env python3
"""Regra #4 item 4: enumera POR SCRIPT, lendo type_line/oracle_text do cache do Scryfall, quais cartas da lista do Mothman satisfazem cada condicao
que o Riverchurn Monument toca. Nunca de memoria. Uso: python3 enumera_condicoes.py > ../resumos/enumeracao_condicoes.txt"""
import json, re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
cache = json.load(open(os.path.join(ROOT, 'scryfall-cache', 'oracle-cache.json')))
lista = open(os.path.join(ROOT, 'wise-mothman-sultai', 'lista.md'), encoding='utf-8').read().splitlines()
names, comandante = [], None
sec = None
for ln in lista:
    if ln.startswith('## '):
        sec = ln[3:].strip(); continue
    m = re.match(r'^(\d+) (.+)$', ln.strip())
    if m and sec in ('Comandante', 'Deck'):
        n = m.group(2).strip()
        (names.append(n) if sec == 'Deck' else None)
        if sec == 'Comandante': comandante = n
cards = [comandante] + names
print(f'cartas lidas de lista.md: comandante + {len(names)} = {len(cards)}')
miss = [n for n in cards if n not in cache]
print('sem oraculo no cache (deve ser vazio):', miss)
cache['Riverchurn Monument']  # tem de existir
def oracle(n):
    c = cache[n]; return (c.get('oracle_text') or '')
def tl(n): return cache[n].get('type_line') or ''
conds = {
 'artefato (type_line)':               lambda n: 'Artifact' in tl(n),
 'oraculo cita "artifact"':            lambda n: re.search(r'\bartifacts?\b', oracle(n), re.I) is not None,
 'oraculo cita "mill"/"milled"':       lambda n: re.search(r'\bmill', oracle(n), re.I) is not None,
 'oraculo cita "graveyard"':           lambda n: 'graveyard' in oracle(n).lower(),
 'oraculo cita "untap"/"untaps"/"becomes untapped"': lambda n: re.search(r'untap', oracle(n), re.I) is not None,
 'oraculo cita "activate"/"activated"':lambda n: re.search(r'\bactivat', oracle(n), re.I) is not None,
 'oraculo cita "enters" (gatilho de entrada de permanente)': lambda n: re.search(r'permanent[^.]*enters|another permanent', oracle(n), re.I) is not None,
 'devolve ao campo / flicker / blink': lambda n: re.search(r'return (it|that card|them|target[^.]*) to the battlefield|exile[^.]*then return', oracle(n), re.I) is not None,
 'conjura do cemiterio (Muldrotha/Six/Kozilek-like)': lambda n: re.search(r'from your graveyard', oracle(n), re.I) is not None and re.search(r'cast|play', oracle(n), re.I) is not None,
 'conta contadores/rad':               lambda n: re.search(r'\brad\b|counter', oracle(n), re.I) is not None and 'counter target' not in oracle(n).lower(),
}
for k, f in conds.items():
    hit = [n for n in cards if f(n)]
    print(f'\n## {k}  [{len(hit)}]')
    for n in hit: print('  -', n, '|', tl(n))
