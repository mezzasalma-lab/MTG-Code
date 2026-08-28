# Goldfish Log — Nekusar, the Mindrazer

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Simulação #1 — goldfish Python completo (`nekusar_goldfish_v1.py`) — 2026-08-23

**Script construído do zero**, reaproveitando a varredura mecânica já feita na auditoria (`auditoria.md` seções 5 e 6, que já tinha catalogado os 9 payoffs reais de dano-por-compra e as 15 fontes de wheel/draw em massa carta a carta com oracle_text exato) em vez de refazer o Passo 0 do zero — a auditoria já tinha esse trabalho pronto e correto.

**Sem oponente real num goldfish solo**, e este é o deck mais dependente disso de todos os já simulados nesta biblioteca (é literalmente um deck de "dano por compra do oponente"): `NUM_OPPONENTS = 3` é uma premissa declarada de mesa (4 jogadores), e todo dano/perda-de-vida gerado é um contador **proxy agregado** (`proxy_damage_total`), nunca vida real de ninguém — reportado sempre com esse aviso, nunca como "matou a mesa".

**Motor central implementado com fidelidade real:** `damage_per_opponent_draw()` soma os 8 payoffs de dano-por-compra ativos (comandante, Orcish Bowmasters, Sheoldred, Underworld Dreams, Spiteful Visions, Phyrexian Tyranny, Razorkin Needlehead, Scrawling Crawler), e cada evento de wheel (`wheel_event()`) multiplica isso pelo número de compras de cada oponente-proxy. Os gatilhos simétricos "each player's draw step, +1 draw" (comandante, Spiteful Visions) são tratados à parte no `draw_step()`, afetando tanto minha mão real quanto o dano proxy gerado nos oponentes.

**Combo de storm/recursão (Underworld Breach + Past in Flames + rituais) implementado como loop real**, não decorativo — `work_breach_or_flames_recast()` respeita os custos reais de cada mecânica: escape (Underworld Breach) exige exilar 3 outras cartas do cemitério a cada recast (auto-limitante, o cemitério encolhe 3 por iteração); flashback (Past in Flames) exila a própria carta recastada ao resolver (regra real, CR 702.32a).

**2 bugs reais encontrados e corrigidos no smoke-test/robustez, antes do batch oficial:**

1. **Comandante nunca saía da mão** — mesmo bug já visto em todos os outros 5 simuladores desta biblioteca: `cast_card()` tentava `state.hand.remove(COMMANDER)` incondicionalmente, mas ela vem da zona de comando, não da mão. Corrigido excluindo a comandante dessa remoção.
2. **Loop do Past in Flames nunca convergia** — a primeira versão devolvia a carta recastada via flashback de volta pro cemitério (copiando a lógica do escape do Underworld Breach), mas flashback de verdade **exila** a carta ao resolver, não devolve. Sem isso, o loop batia no teto defensivo de 40 iterações repetidamente (visto em 3 das primeiras 30 seeds testadas manualmente, com `storm_count` grudado em 40-50). Corrigido: só o modo "escape" devolve a carta pro cemitério; o modo "flashback" a exila de verdade.
3. **Sem descarte por limite de mão (CR 514.3)** — achado rodando uma amostra maior: mãos chegando a **74 cartas** depois de 8 turnos, porque nada descartava o excesso no cleanup. Esperado nesse deck especificamente, já que ele compra em volume absurdo (Nekusar + Spiteful Visions dão +1 compra simétrica por turno, fora os wheels completos). Corrigido com `cleanup_discard()`: descarta até 7 no fim do turno, priorizando manter as cartas de maior CMC (mais impactantes) e descartando o excedente mais barato primeiro — incluindo terrenos excedentes quando já há mana suficiente em campo, uma escolha real de jogo, documentada.

**Teste de robustez** (antes e depois dos 2 bugs de loop/mão): 20.000 partidas com timeout de 2s via `signal.alarm`, **0 erros, 0 timeouts** em ambas as rodadas — a segunda rodada (pós-fix do cleanup) confirmou a correção (mão máxima voltou a 7, contra 74 antes).

**n=3000, seed_base=7300000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0,61
Turno medio de conjuracao do Nekusar: 5,14 | mediana: 5,0
Nunca conjurado em 8 turnos: 12,8%
Avg eventos de wheel (full+parcial): 1,19
Avg wheels completos (descarta mao, compra 7): 1,19
Avg dano/perda-de-vida proxy total (3 oponentes hipoteticos, NUNCA vida real): 81,51
Avg vida ganha (Sheoldred, proxy Bloodchief): 1,91
Avg cartas compradas extra: 16,60
Avg tutores usados: 0,78
Avg recasts via Underworld Breach/Past in Flames: 0,51
Partidas com pelo menos 1 loop de Breach/Flames (2+ recasts no mesmo evento): 26,7%
Avg storm count maximo no turno: 4,03
Avg mill proxy total (Mindcrank + Brain Freeze): 9,66
Avg reanimados (Animate Dead/Reanimate): 0,01
Avg mao final: 3,38
```

**Leituras principais:**

- **Comandante mais lento que os outros decks já simulados** (T5,14 médio, 12,8% nunca resolve em 8 turnos) — coerente com o custo `{2}{U}{B}{R}` (3 cores + genérico) e uma base de mana que prioriza fetches/duais sobre rampa dedicada (só 3 rocks reais: Sol Ring, Arcane Signet, os 2 Talismãs).
- **O combo de storm (Breach/Flames) é real e aparece em parcela relevante das partidas (26,7% com pelo menos 1 loop de 2+ recasts)**, mas o volume médio de recasts é modesto (0,51/partida) — bate com a leitura qualitativa da auditoria ("não é um combo de 2 peças isolado, é uma cadeia que pode explodir quando as peças se alinham"): quando liga, gera valor real (storm médio de 4,03, alguns jogos passam disso), mas não é a maioria das partidas.
- **Dano proxy médio de 81,51 por partida** é alto mesmo sem o cenário extremo de "todos os 8 payoffs em campo simultâneo" que a auditoria descreveu como matemática de mesa — confirma que o motor de wheel-damage é genuinamente forte mesmo em jogos parciais, não só no caso hipotético ideal.
- **Reanimados praticamente zero (0,01/partida)** — esperado: só 9 criaturas em 99 cartas, e nada no deck sacrifica/descarta criaturas de propósito (os wheels descartam a mão inteira aleatoriamente, então às vezes pegam uma criatura, raramente).

Resultados salvos em `nekusar_v1_runs.jsonl` (3000 jogos).

**Simplificações documentadas no docstring do script** (não inventadas — omissões explícitas): sem oponente real, todo dano/vida é proxy agregado (`NUM_OPPONENTS=3`); contramágicas/proteção conjuradas quando há mana sobrando, sem efeito de combate real modelado; fetchlands tratadas como terreno genérico (thinning não modelado); Brain Freeze e Mindcrank registram mill como proxy, nunca aplicado a biblioteca real de ninguém; Wheel of Misfortune modelado como wheel completo padrão, sem a metade condicional de dano-por-número-escolhido; sem combate real (deck não é de ataque).

---

## Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks. Achado grave nesta rodada: o próprio docstring
do script afirmava "9 payoffs... 15 fontes de wheel/draw... **todos** com
efeito real implementado" — falso. **11 das ~15 fontes catalogadas tinham só
a tag, nenhum gatilho real**:

- **Waste Not / Liliana's Caress** (tag `discard_payoff`): gatilhos por carta
  DESCARTADA por oponente (evento distinto de "compra", que `wheel_event()`
  já cobria) — nunca disparavam. Nova função `discard_payoff_total()`,
  chamada de dentro de `wheel_event()` com um parâmetro de descartes por
  oponente (premissa documentada: na maioria dos wheels simétricos
  "descarta a mão, compra N" o descarte tem a mesma ordem de grandeza do
  redraw). Waste Not modelado com a composição real da decklist (22
  terrenos/10 criaturas/67 outras de 99) pra dividir entre as 3 cláusulas.
- **Jace's Archivist / Magus of the Wheel**: wheels reais ({U},{T} repetível
  1x/turno; sacrifício de um tiro só) — 100% ausentes, implementadas como
  eventos de wheel de verdade.
- **Faerie Mastermind**: as DUAS metades ausentes — passiva ("whenever an
  opponent draws their second card each turn, you draw a card", dispara
  quando o próprio estático do Nekusar está ativo) e ativada ("{3}{U}: each
  player draws a card", repetível, teto de 10/turno).
- **Resonating Lute**: metade "{T}: Draw a card. Activate only if 7+ cards
  in hand" implementada; a estática de campo (lands ganham mana extra
  restrita a instant/sorcery) fica de fora — esse motor não restringe mana
  por tipo de spell, baixo valor pro escopo.
- **Sensei's Divining Top**: achado extra — o gate usava `ready_creatures()`
  (lista só de criaturas), mas o Top é um Artifact, nunca aparecia lá.
  Condição morta por construção, nunca disparava. Corrigido (artefato não
  tem doença de invocação).
- **Teferi's Puzzle Box**: tag `wheel_passive` só era lida pra ordenar
  prioridade de cast, nunca disparava o efeito real ("at the beginning of
  each player's draw step..."). Implementado 1x por meu turno (premissa:
  tamanho médio de mão do oponente = 5, representa o ciclo dos 3 turnos-
  proxy dos oponentes desde meu último turno).
- **Mikokoro / Geier Reach Sanitarium / Cephalid Coliseum**: 3 terrenos
  wheel, 100% ausentes — implementados como ativações reais ({2},{T} pra
  Mikokoro/Geier Reach; Cephalid Coliseum com o gate real de Threshold,
  7+ cartas no cemitério, sacrifício de um tiro só).

**Resultado (n=2000, seed_base=4000000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg eventos de wheel | 1,19 | **3,45** |
| Avg dano/vida proxy total | 81,05 | **404,75** |
| Avg cartas compradas extra | 16,54 | **25,70** |
| Avg storm count máximo | 4,06 | **7,33** |
| Avg recasts via Breach/Flames | 0,53 | **1,18** |
| Avg vida ganha (Sheoldred) | 1,91 | **9,92** |

Salto grande (5x no dano proxy) — o deck estava significativamente
subsimulado: quase todo o "motor de wheel secundário" (fora os 4-5 payoffs
principais já implementados desde a Simulação #1) não existia de verdade.
Mais cartas compradas por turno também alimenta mais recasts via Underworld
Breach (fica com mais spells no cemitério pra reciclar), explicando o
aumento composto em storm count e recasts.

**Robustez:** sweep de 20.000 jogos (seeds 4000000–4019999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

Docstring do script corrigido (a frase "todos com efeito real implementado"
era falsa — substituída por uma nota explícita desta correção).

`lista.md` não mudou. `nekusar_v1_runs.jsonl` sobrescrito.

---

## Partida #1 — AAAA-MM-DD

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

---

## Partida #2 — AAAA-MM-DD

- **Formato do teste:**
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:**
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

<!-- Copie o bloco acima para cada nova partida -->
