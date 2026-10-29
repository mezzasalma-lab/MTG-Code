# Ledger da partida manual #2 do Mothman (2026-10-06)

Leitura minha do trace (`resumos/trace.md`); contadores finais por turno conferidos por `assert`. **Limites:** o log nao registra vida, rad, mana flutuante, nem a ordem da pilha.

## 1. Contadores +1/+1, evento a evento (base = o que o log mostrava antes do evento)

Colocacao de `n` contadores num permanente seu com Kami e/ou Constrictor em campo = `n + (#Kami) + (#Constrictor)` (todas aditivas, CR 616.1; rulings do Kami e do Hardened Scales/Constrictor).

| T | evento | n | Kami/Constr. em campo | esperado | no log | diferenca |
|---|---|---|---|---|---|---|
| T3 | Mothman entra: Gyre Sage evolve (o log so' mostra o contador no T4) | 1 | 0/0 | 1 | 1 | ok |
| T4 | Cankerbloom milado pelo rad (nao-terreno, X=1): gatilho do Mothman, alvo Mothman | 1 | 0/0 | 1 | 1 | ok |
| T4 | Basking Broodscale entra: Henge poe 1 contador (e deveria comprar) | 1 | 0/0 | 1 | 1 | ok |
| T5 | Winding Constrictor entra: Henge poe 1 contador nele (o Constrictor ja' vale para si) | 1 | 0/1 | 2 | 1 | **-1** |
| T5 | Kami entra: Henge poe 1 contador nele (Kami e Constrictor ja' valem) | 1 | 1/1 | 3 | 2 | **-1** |
| T5 | Mindcrank milado (X=1): gatilho do Mothman, alvo Mothman | 1 | 1/1 | 3 | 3 | ok |
| T6 | Ouroboroid entra: Henge poe 1 contador nele | 1 | 1/1 | 3 | 2 | **-1** |
| T6 | Fierce Guardianship milada (X=1): gatilho do Mothman, alvo Ouroboroid | 1 | 1/1 | 3 | 2 | **-1** |
| T6 | combate: Ouroboroid (poder 5 = 1 + 4 contadores) poe X em CADA criatura | 5 | 1/1 | 7 por criatura | +6 (Ouroboroid, Mothman, Gyre Sage, Constrictor, Kami) e +5 (Broodscale) | **-1** (-2 na Broodscale) |
| T6 | o mesmo gatilho nas fichas Eldrazi Spawn (0/1, criatura): ja' havia 1 em campo | | | 7 na ficha | 0 | **-7** |
| T7 | combate: Ouroboroid (poder 11) poe X em cada criatura (so' o Ouroboroid foi registrado) | 11 | 1/1 | 13 | +13 (10 -> 23) | ok |

No T7 o log mostra **as duas substituicoes** (11 + 1 + 1 = 13); no T6 mostra so' **uma** (5 + 1 = 6) e nenhuma ficha recebeu contador. Colocacoes com a conta errada (so' as que o log permite provar): T5 Constrictor (-1), T5 Kami (-1), T6 Ouroboroid entrando (-1), T6 gatilho do Mothman (-1) e T6 combate (-1 em 5 criaturas, -2 na Broodscale, -7 na ficha). O gatilho do Mothman do T5 (+3 no Mothman) esta CERTO.
**Fonte declarada pelo usuario (2026-10-07):** a Gyre Sage ganhou +2 no T5 (1 -> 3). A evolve nao dispara com o Constrictor (2/3) nem com o Kami (1/1) entrando (a condicao 'if' e' checada na entrada, antes dos contadores do Henge), e no meu ledger so' ha 1 gatilho do Mothman, no Mothman. O usuario respondeu que os +2 vieram **do mill do rad e do Mothman** (gatilhos 'whenever one or more nonland cards are milled'). O Mothman da rad a CADA jogador ('each player gets a rad counter'), entao o mill do rad dos oponentes, que acontece nos turnos deles e que o log nao registra, tambem dispara o Mothman: e' a explicacao compativel, mas **de quem foi o mill nao consta no log** (inferencia, nao prova). O achado anterior 'sem fonte' esta RETIRADO.

### Como o erro se compoe (replay estrito, mesmas escolhas de alvo do usuario, base = fim do T4 do log)

- fim do T6 pelas regras: Mothman 13, Gyre Sage 12 (com o +2 declarado pelo usuario no T5), Broodscale 10, Constrictor 11, Kami 12, Ouroboroid 15, ficha Spawn 9; no log: Mothman 10, Gyre Sage 9, Broodscale 6, Constrictor 7, Kami 8, Ouroboroid 10, ficha 0.
- gatilho do T7 pelas regras: X = poder do Ouroboroid = 1 + 15 = 16, cada criatura +18 (o log: X = 11, +13).

## 2. Compras do The Great Henge ("whenever a nontoken creature you control enters, put a +1/+1 counter on it and draw a card")

| T | criaturas nao-ficha que entraram com o Henge em campo | compras esperadas (alem da compra do turno) | compras no log (library -> mao fora do passo de compra) |
|---|---|---|---|
| T4 | Basking Broodscale | 1 | 0 | **faltou 1** |
| T5 | Winding Constrictor, Kami of Whispered Hopes | 2 | 2 | ok |
| T6 | Ouroboroid | 1 | 1 | ok |

O T5 (2 compras) e o T6 (1) batem; **no T4 a Broodscale entrou com o Henge em campo e nao ha compra no log** (1 compra a menos).

## 3. Rad (CR 728.1) e o Winding Constrictor ("if you would get one or more counters, you get that many plus one")

| T | mills meus no log | rad esperado no inicio da fase principal 1 (minimo) | cartas milladas no log | diferenca |
|---|---|---|---|---|
| T4 | Cankerbloom | 1 (ETB do Mothman no T3) | 1 | ok |
| T5 | Overgrown Tomb, Mindcrank | 1 (ataque do T4: +1; o rad do T4 foi consumido por um nao-terreno) | 2 | ok (sobra 1 sem fonte) |
| T6 | Fierce Guardianship | 2 ou mais (ataque do T5 com o Constrictor em campo: +1 +1 extra = +2) | 1 | **faltam >= 1** |
| T7 | Misty Rainforest | 2 ou mais (ataque do T6 com o Constrictor: +2) | 1 | **faltam >= 1** |

O Constrictor so' entrou no T5, mas o Mothman atacou depois dele no T5 e no T6: cada ataque deu **2** rad counters a voce, nao 1. Os mills do T6 e do T7 ficam **pelo menos 1 abaixo** do exigido (limite inferior firme); o T5 tem 1 mill a mais do que a fonte conhecida (Overgrown Tomb e Mindcrank; so' havia 1 rad).

## 4. Jogadas de terreno (1 por turno; a Takenuma estava na mao desde a abertura)

| T | terreno jogado | outros terrenos na mao na hora |
|---|---|---|
| T1 | Zagoth Triome (virada) | Island, Takenuma |
| T2 | Island | Takenuma |
| T3 | Swarmyard | Takenuma |
| T4 | **nenhum** | Takenuma |
| T5 | Strip Mine | Takenuma |
| T6 | Undergrowth Stadium | Takenuma, Overgrown Tomb, Watery Grave |
| T7 | Forest | Takenuma, Overgrown Tomb, Watery Grave |

O T4 e' a unica rodada sem jogada de terreno, com a Takenuma na mao: era o que faltava para o Henge (T4) caber no mana (5 = 4 fontes + 1 terreno).
