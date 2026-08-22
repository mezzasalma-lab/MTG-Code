# Goldfish Log — Esika, God of the Tree // The Prismatic Bridge

## Simulação #1 — gerada por Claude (RNG real, não é partida sua)

**Método:** embaralhei a lista de 100 cartas de `lista.md` com `random.shuffle` do Python (sem seed fixa, usa entropia do sistema operacional) em 2026-08-20. Mão inicial = 7 cartas do topo pós-embaralhamento. Convenção: jogador na ponta ("on the play"), sem compra no turno 1, compra 1 carta a partir do turno 2. Efeitos de "olhe o topo N" (ex: Oath of Nissa) foram resolvidos consultando a ordem real da biblioteca simulada, não escolhidos livremente. Este é um teste solo sem oponente — anotei explicitamente onde isso limita alguma carta (ex: Exotic Orchard).

**Mão inicial:** Oath of Nissa, Plateau, Command Tower, Sphinx of the Second Sun, Exotic Orchard, Bayou, Tamiyo, Field Researcher

**T1:** Joga Command Tower. Conjura Oath of Nissa (`{G}`). Resolve olhando o topo 3 da biblioteca simulada: Arena Rector, City of Brass, Savannah. Escolha: Arena Rector (criatura — já tinha 3 terrenos na mão, land não era prioridade). City of Brass e Savannah vão pro fundo.
Mão pós-T1: Plateau, Sphinx of the Second Sun, Exotic Orchard, Bayou, Tamiyo Field Researcher, Arena Rector.

**T2:** Compra: Badlands. Joga Bayou. Nenhum spell de 2 custa esse valor na mão — passa.

**T3:** Compra: Swords to Plowshares. Joga Plateau. 3 fontes de mana (Command Tower/Bayou/Plateau). Tamiyo, Field Researcher custa `{1}{G}{W}{U}` = 4 total, falta 1 — não castável ainda. Passa.

**T4:** Compra: The Peregrine Dynamo. Joga Exotic Orchard — **nota:** em goldfish solo sem oponente, Exotic Orchard não tem fonte confiável (não há terreno alheio pra copiar), tratado como mana morto neste teste. Com Command Tower + Bayou + Plateau (3 mana úteis), conjura The Peregrine Dynamo (`{3}`).

**T5:** Compra: Sol Ring. Conjura Sol Ring. Com Sol Ring + os 3 lands úteis, monta `{1}{G}{W}{U}` e conjura Tamiyo, Field Researcher.

**T6:** Compra: Teferi, Time Raveler. Conjura Teferi, Time Raveler (`{1}{W}{U}`).

**Board final (fim do T6):** Command Tower, Bayou, Plateau, Exotic Orchard (morto), Sol Ring | Oath of Nissa, The Peregrine Dynamo, Tamiyo Field Researcher, Teferi Time Raveler.
**Mão remanescente:** Sphinx of the Second Sun, Arena Rector, Badlands, Swords to Plowshares.
**Sem compra ainda:** nenhuma das Game Changers da lista (Farewell, Narset Parter of Veils, Rhystic Study) apareceu nesses 6 turnos — dado real dessa simulação, não uma afirmação sobre a lista em geral.

---

## Simulação #2 — goldfish Python focado (Greater Auramancy?) — 2026-08-21

**Script:** `prismatic_bridge_goldfish_v1.py` — construído do zero pra essa pergunta específica (não é o goldfish completo de curva geral, escopo documentado no docstring do arquivo). CARD_DB gerado via Scryfall `cards/collection` (99 cartas) com tags derivadas de `oracle_text` real. Simula só a face "The Prismatic Bridge" do comandante (a frente Esika não foi modelada — limitação documentada).

**Objetivo:** decidir se vale incluir Greater Auramancy, testando o deck atual vs. uma versão com Greater Auramancy no lugar de The Peregrine Dynamo (única criatura sem nenhuma tag de sinergia).

**Premissa não validada** (usuário não tem dado real, deck nunca jogado — citação: *"3 oponentes, não joguei com o deck ainda"*): taxa de tentativa de remoção por oponente por turno mirando a Bridge/protetores. Testado em 3 cenários (12%, 25%, 40% por oponente por turno) pra checar se a conclusão muda com a taxa.

**n=2000 por cenário, 10 turnos:**

| Taxa de remoção assumida | Bridge removida (méd/partida) sem GA | com GA | % Bridge em campo no fim, sem GA | com GA |
|---|---|---|---|---|
| 12%/oponente/turno | 1,18 | 1,14 | 63,3% | 64,5% |
| 25%/oponente/turno | 1,59 | 1,58 | 39,4% | 40,0% |
| 40%/oponente/turno | 1,72 | 1,73 | 28,4% | 28,4% |

**Achado principal — por que o efeito é tão pequeno em qualquer cenário:** instrumentei quantas partidas (de 2000, mesma seed base, deck com Greater Auramancy) chegam a ter cada protetor em campo em algum momento dos 10 turnos:

```
Sterling Grove chegou a estar em campo: 14,7%
Greater Auramancy chegou a estar em campo: 16,4%
Os 2 chegaram a estar em campo (mesmo que não simultâneo): 2,4%
```

**A redundância de shroud só importa nos jogos em que os DOIS protetores entram em campo — e isso acontece em só 2,4% das partidas.** O gargalo real não é "1 protetor não é redundante o suficiente", é "a chance de sequer conjurar 1 protetor de 2 mana num deck de 99 cartas em 10 turnos já é baixa (~15%)". Greater Auramancy não ataca esse problema — ela é mais uma carta de baixa densidade competindo pelo mesmo espaço, não uma solução pra reliability.

**Outros números de referência (taxa 12%, sem Greater Auramancy):**
```
Turno médio da 1ª conjuração da Bridge: 4,50 | mediana: 4,0
Bridge nunca conjurada em 10 turnos: 5,9%
Conjurada via flash (end step do turno anterior): 3,5% das partidas
Avg gatilhos de upkeep: 2,94 | acertos: 2305 criatura / 3581 planeswalker
```

**Conclusão:** sob qualquer uma das 3 premissas de remoção testadas, Greater Auramancy melhora a sobrevivência da Bridge em menos de 1,5 ponto percentual — efeito real mas pequeno, e consistente (não muda de ordem de grandeza mesmo triplicando a taxa de remoção assumida). Não é uma troca de alto impacto pra esse objetivo específico. Se a prioridade é proteção da Bridge, o gargalo real (~15% de chance de ter QUALQUER protetor em campo) provavelmente pede outra solução (ex: um tutor de encantamento, ou simplesmente aceitar que a proteção robusta contra remoção pontual não é o forte desse build — os counterspells da seção 5 da auditoria seguem sendo a defesa mais confiável).

---

<!-- Para novas partidas (reais ou novas simulações), use o formato abaixo -->

## Partida #N — AAAA-MM-DD

- **Formato do teste:** goldfish / playtest com amigos / mesa competitiva
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:** vitória / derrota / sem resolução
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**
