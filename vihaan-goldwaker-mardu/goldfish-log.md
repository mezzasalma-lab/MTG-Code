# Goldfish Log — Vihaan, Goldwaker

> **Dados brutos e como reproduzir as tabelas da seção Correção do simulador: exílio sempre primeiro e farm com Dictate (2026-10-04):** [`resultados-ab/2026-10-04-exilio-sempre-e-dictate/LEIAME.md`](resultados-ab/2026-10-04-exilio-sempre-e-dictate/LEIAME.md) — brutos `.json.xz` por partida, código antes, resumos, comandos, hashes e verificação de reprodutibilidade (Regra #8 do `CLAUDE.md`).

> **Dados brutos e como reproduzir as tabelas da seção Correção do simulador: exílio do Prosper expirando primeiro e Treasure animado com Mahadi (2026-10-03):** [`resultados-ab/2026-10-03-exilio-primeiro-e-mahadi/LEIAME.md`](resultados-ab/2026-10-03-exilio-primeiro-e-mahadi/LEIAME.md) — brutos `.json.xz` por partida, código antes, resumos, comandos, hashes e verificação de reprodutibilidade (Regra #8 do `CLAUDE.md`).

> **Dados brutos e como reproduzir as tabelas da seção Correção do simulador: conjurar/jogar de fora da mão (2026-10-03):** [`resultados-ab/2026-10-03-fora-da-mao/LEIAME.md`](resultados-ab/2026-10-03-fora-da-mao/LEIAME.md) — brutos `.json.xz` por partida, código antes, resumos, comandos, hashes e verificação de reprodutibilidade (Regra #8 do `CLAUDE.md`).

> **Dados brutos e como reproduzir as tabelas da seção Partida manual #1 do Vihaan (2026-10-03):** [`resultados-ab/2026-10-03-partida-manual-1/LEIAME.md`](resultados-ab/2026-10-03-partida-manual-1/LEIAME.md) — o log da partida (`.json.xz`), oráculo e rulings ao vivo, scripts, resumos, comandos, hashes e verificação de reprodutibilidade (Regra #8 do `CLAUDE.md`).

> **Dados brutos e como reproduzir as tabelas da seção Correção do simulador: Sephiroth (2026-10-03):** [`resultados-ab/2026-10-03-sephiroth/LEIAME.md`](resultados-ab/2026-10-03-sephiroth/LEIAME.md) — brutos `.json.xz` por partida, código antes, resumos, comandos, hashes e verificação de reprodutibilidade (Regra #8 do `CLAUDE.md`).

> **Dados brutos e como reproduzir as tabelas da seção Correção do simulador: Treasure animado, mulligan e terreno tapped (2026-10-03):** [`resultados-ab/2026-10-03-treasure-animado-e-mulligan/LEIAME.md`](resultados-ab/2026-10-03-treasure-animado-e-mulligan/LEIAME.md) — brutos `.json.xz` por partida, código antes/depois, resumos, comandos, hashes e verificação de reprodutibilidade (Regra #8 do `CLAUDE.md`).

> **Dados brutos e como reproduzir as tabelas da seção Inevitable Defeat (2026-10-03):** [`resultados-ab/2026-10-03-inevitable-defeat/LEIAME.md`](resultados-ab/2026-10-03-inevitable-defeat/LEIAME.md) — brutos `.json.xz` por partida, resumos, comandos, hashes e verificação de reprodutibilidade (Regra #8 do `CLAUDE.md`).

> **Dados brutos e como reproduzir as tabelas da seção Kingpin, Wilson Fisk (2026-10-03):** [`resultados-ab/2026-10-03-kingpin/LEIAME.md`](resultados-ab/2026-10-03-kingpin/LEIAME.md) — brutos `.json.xz` por partida, resumos, comandos, hashes e verificação de reprodutibilidade (Regra #8 do `CLAUDE.md`).


---

## Correção do simulador: exílio sempre primeiro e farm de Treasure animado também com Dictate — 2026-10-04

**Pedido (3 frases do usuário):** *"T7 foi erro meu. Prefiro sempre jogar o spell exilado para criar mais tesouros. O dictate é mais vantagem, eu sacrifico tesouros animados e todos os oponentes sacrificam criaturas."*
**Veredito:**
1. **T7 foi esquecimento de registro** (Pact Boon do Lotho e Lotho na Tax não anotados): fecha, não é erro de regra nem do simulador.
2. **"Sempre jogar o spell exilado"** virou chave (`IMPULSE_ALL_FIRST_ENABLED`): *toda* carta do exílio (não só as que expiram neste turno) é conjurada antes das da mão, inclusive as que acabaram de ser exiladas no meio do main (Inspired Tinkering). **O efeito é pequeno no simulador, porque a rodada anterior já pegava quase tudo:** as cartas do Prosper expiram no turno em que ficam jogáveis (97,2% → 97,3% das mágicas conjuradas); só as da Inspired Tinkering, que valem por dois turnos, mudam.
3. **Dictate em campo aciona o sacrifício dos Treasures animados** (`TREASURE_FARM_WITH_DICTATE_ENABLED`), **mesmo sem Mahadi/Plunderer**, como você faz. **Sem a reposição isso custa Treasures:** estoque no fim **−0,084 ±0,015 por jogo** (padrão) quando é só o Dictate que justifica; em troca, **+0,087 gatilhos do Dictate por jogo** (0,245 → 0,335), isto é, ~0,26 criaturas de oponente a mais sacrificadas por jogo (×3 oponentes, proxy). O simulador **não dá valor** a essas criaturas de oponente (📊), então na métrica de vitória o efeito é zero (+0,04 ±0,08pp).
Nenhum dos dois move a vitória até o T8 de forma significativa (juntos: +0,23 ±0,20pp padrão, +0,10 ±0,14pp resiliência): são correções de **linha de jogo**, não de número.

### O que mudou no código (2 chaves)
1. **`IMPULSE_ALL_FIRST_ENABLED`**: no início de `main_phase` roda `play_from_impulse` sem o filtro "expira neste turno", e dentro do laço da mão, a cada iteração, a carta do exílio (a mais barata primeiro, maximizando quantas entram e portanto quantos Pact Boon) vai antes de qualquer carta da mão. O comandante continua primeiro. Antes (rodada anterior): só as que expiram neste turno.
2. **`TREASURE_FARM_WITH_DICTATE_ENABLED`**: `farm_animated_treasures` também roda com o Dictate of Erebos em campo. `treasure_farm_dictate_total` conta os animados sacrificados *só por causa do Dictate* (sem Mahadi/Plunderer). **Ordem:** o Dictate é pago antes com terrenos/rocks (o `spend_mana` só gasta Treasure no que falta), e os animados morrem depois, com ele em campo: nenhum gatilho se perde (o contrário da sua T8, em que ele foi pago com os próprios animados).

### Medição (apoio; pareada; base = simulador antes, commit `ba594c8`; N=10.000, sementes 3.000.000+i, 8 turnos; entre parênteses o modo resiliência)
Diferença pareada (variante − antes), IC95%:

| variante | win ≤8 (pp) | Treasures criados | estoque no fim | dano mesa | mortes de criatura |
|---|---|---|---|---|---|
| só "exílio sempre primeiro" | +0,19 ±0,19 n.s. (+0,06 ±0,13 n.s.) | +0,10 ±0,04 (+0,06 ±0,03) | +0,03 ±0,03 n.s. (+0,01 ±0,02 n.s.) | +0,20 ±0,17 (+0,05 ±0,10 n.s.) | +0,03 ±0,03 n.s. (+0,02 ±0,02 n.s.) |
| só "farm também com Dictate" | +0,04 ±0,08 n.s. (+0,05 ±0,05 n.s.) | −0,005 ±0,004 (−0,001 ±0,002 n.s.) | **−0,084 ±0,015** (−0,046 ±0,009) | +0,15 ±0,07 (+0,07 ±0,03) | **+0,09 ±0,02** (+0,06 ±0,01) |
| **as duas** | +0,23 ±0,20 n.s. (+0,10 ±0,14 n.s.) | +0,09 ±0,04 (+0,06 ±0,03) | −0,05 ±0,03 n.s. (−0,03 ±0,02 n.s.) | +0,34 ±0,18 (+0,13 ±0,10) | **+0,11 ±0,03** (+0,08 ±0,03) |

Base: win ≤8 14,3% (3,7%) · Treasures criados 12,87 (7,90) · estoque no fim 3,50 (1,87) · dano mesa 21,04 (9,53) · mortes de criatura 4,16 (5,12).
**Métricas diretas (por jogo, padrão, as duas vs antes):** cartas do exílio conjuradas antes das da mão **pela chave "sempre"** 0 → **1,61**; magias do exílio conjuradas 1,464 → 1,507; chamadas de Pact Boon 0,561 → 0,571; Treasures-criatura sacrificados pelo farm 0,666 → **0,771** (dos quais **0,088 só por causa do Dictate**); gatilhos do Dictate 0,245 → **0,335**, isto é, criaturas de oponente forçadas a sacrificar (×3, proxy) 0,73 → **1,01** por jogo (resiliência 0,44 → 0,59). Só 85,7% das partidas terminam no mesmo estado do antes (89,4% na resiliência).
**Destino das cartas que o Prosper exila** (`resumos/prosper_destino_*.txt`, só as que já tiveram a vez): mágica conjurada **97,2% → 97,3%** (1.943 de 1.999 → 1.955 de 2.009); terreno jogado 97,3% → 97,5%. Praticamente inalterado: o "sempre" é irrelevante para o Prosper porque as cartas dele sempre expiram no turno seguinte.

**Leitura (medido):** (a) os dois ajustes são de **linha de jogo**: o "sempre" só muda a ordem da Inspired Tinkering (+0,10 Treasures criados); (b) o farm com Dictate **gasta** estoque (−0,084 sozinho) para forçar sacrifícios que o simulador não valoriza, então o número de vitória não sobe e o estoque cai um pouco; isso é consistente com o que você disse ("o Dictate é mais vantagem": a vantagem está no oponente, que o simulador não mede); (c) a conta real do Dictate para você é **gatilhos × 3 oponentes**: 0,335 gatilhos por jogo no simulador = ~1 criatura de oponente por jogo até o T8.
**Lido como raciocínio, não medido:** o valor de cada criatura de oponente sacrificada (depende do que sobra no campo dele, estado de oponente 📊); a política "sacrifica **todos** os animados que sobraram" é a que a regra "o Dictate justifica" pede, mas a sua T8 sacrificou **7 dos até 12** Treasures disponíveis, então pode haver uma reserva que eu não consegui inferir do log: se houver um critério (guardar N Treasures para o próximo turno), diga e eu parametrizo.

### Validação (Regra #1) — arquivada em `resultados-ab/2026-10-04-exilio-sempre-e-dictate/`
- **Smoke:** 99 cartas, 93 distintas, 0 desconhecidas, 0 duplicadas não básicas, 35 terrenos; 200 partidas sem exceção.
- **Testes dirigidos:** 16/16: carta do exílio que **não** expira (prazo 8) vai antes da mão; a recém-exilada pela Inspired Tinkering também (com mana pra só uma, entra a do exílio e o Zulaport fica na mão; com a chave desligada, o contrário); o comandante segue primeiro; vários do exílio entram com 1 Pact Boon cada; Dictate sem Mahadi/Plunderer sacrifica os animados (5 mortes, 5 gatilhos = 15 criaturas de oponente no proxy); com a chave desligada não; com Mahadi o contador "só Dictate" fica em 0; sem Dictate/Mahadi/Plunderer não sacrifica; só os animados; **Dictate pago com os 5 terrenos e 6 animados depois morrem com ele em campo = 6 gatilhos**; integração com Zulaport e Sephiroth; sequência real `combat_step` → `main_phase` → farm → `end_step`; invariantes em 3.000 partidas.
- **Bit-identidade com as 2 chaves desligadas:** 20.000/20.000 idênticas ao `ba594c8` no modo padrão e 20.000/20.000 na resiliência.
- **Regressão:** 140.000 partidas (7 configurações/modos × 20.000, sementes 5.000.000+i), **0 exceções**, 0 cartas duplicadas, 0 partidas com mais de 1 jogada de terreno no turno, 0 "animados vivos" ≠ 0 no fim do turno, 0 Treasures < 0, 0 farms inválidos, 0 mágicas paradas no campo, 0 emblemas do Sephiroth inconsistentes.
- **Reprodutibilidade:** `bash orquestracao/verificar_reproducao.sh --tudo` → **10/10 saídas byte a byte iguais** (`cmp`): as 4 tabelas do A/B refeitas dos `.json.xz` e a re-execução do smoke, dos 16 testes, da bit-identidade (20.000 × 2 modos), da regressão (140.000 partidas) e do destino do Prosper (antes e depois). Os arquivos dos lotes anteriores do Vihaan, ajustados para desligar as 2 chaves novas, foram reverificados contra o simulador vivo: `exilio-primeiro-e-mahadi` 10/10, `fora-da-mao` 8/8, `sephiroth` 11/11, `treasure-animado-e-mulligan` 7/7, `kingpin` 11/11, `inevitable-defeat` 6/6, `partida-manual-1` 7/7 (o `prosper_destino.py` de `exilio-primeiro-e-mahadi` carregava o simulador vivo sem passar por `F.flags` e pegou as chaves novas ligadas; ajustado e refeito).

### Escopo verificado e NÃO verificado (Regra #7)
- **Verificado:** o início e o laço de `main_phase` (ordem exílio × mão), `play_from_impulse`, `farm_animated_treasures`; por teste dirigido + A/B + regressão + destino do Prosper.
- **Não verificado / aberto:** (1) o valor dos sacrifícios do Dictate no oponente (📊: só se conta o uso); (2) a quantidade de Treasures que você guarda ao sacrificar com o Dictate (o simulador sacrifica todos os animados que sobram); (3) Lotho/Monologue Tax em 2ª mágica de oponente 📊; (4) o resto do `.py` não foi relido; (5) o contador +1/+1 do Treasure no T7 e a cópia da Sevinne's no T8 continuam sem resposta.

---

## Correção do simulador: exílio do Prosper expirando primeiro e Treasure animado com Mahadi — 2026-10-03

**Pedido:** *"Corrija o efeito do Prosper, a melhor parte dele é jogar terreno do exílio e criar um tesouro! Além disso quando castei o Dictate eu usei tesouros já criaturas para ativar o Machado mais vezes!"* (junto com as respostas da análise da partida; ver §3b da seção "Partida manual #1", mais abaixo). Leio **"Machado" como Mahadi** (autocorretor; não há carta de nome parecido na lista, e sacrificar Treasures já criaturas só faz sentido para as mortes que o Mahadi conta). Se foi o Reaver Cleaver, diga e eu refaço.
**Veredito:**
1. **O terreno do exílio + Treasure já estava corrigido** no commit anterior (`7cd3f55`) e funciona: dos terrenos que o Prosper exila e já tiveram a sua vez, **97,8% foram jogados** (1.074 de 1.098; cada um dispara o Pact Boon). O que ainda estava errado era a **política das mágicas**: só **37%** das mágicas que o Prosper exilava eram conjuradas (744 de 2.005); **63% expiravam** porque a mão ia primeiro. Você sempre jogou o exílio antes (T5 Mire, T6 Sevinne's, T7 Lotho). Agora a carta do exílio que expira neste turno é conjurada antes das da mão: **97,2% conjuradas** (1.943 de 1.999).
2. **Treasure já criatura como saída própria.** O próprio Treasure é saída de sacrifício (habilidade de mana, ativável sem nada pra gastar) e os animados pelo Vihaan são criaturas até o fim do turno. Com **Mahadi** (1 Treasure por criatura morta) ou **Pitiless Plunderer** (1 Treasure por morte), sacrificá-los é de graça. O simulador só fazia isso com Altar/KCI. Agora, no fim da 2ª main, sacrifica os animados que sobraram quando há Mahadi ou Plunderer em campo.
3. **Efeito (padrão, N=10.000, pareado): win até o T8 +2,40 ±0,42pp** (11,9% → 14,3%), estoque de Treasures no fim +0,49 ±0,16, mortes de criatura +0,75 ±0,09; no modo resiliência win +0,63 ±0,25pp.

### O que mudou no código (2 chaves)
1. **Exílio expirando primeiro** (`IMPULSE_EXPIRING_FIRST_ENABLED`). No início de cada `main_phase` (depois do comandante), `play_from_impulse(expiring_only=True)` conjura as cartas do pool com prazo = turno atual (mais barata primeiro), pela esteira de cast da rodada anterior, com Pact Boon. As que podem esperar (prazo > turno) continuam depois da mão. Jogada de terreno do exílio já era a primeira (`play_land`).
2. **Treasure animado como saída própria** (`TREASURE_SELF_OUTLET_FARM_ENABLED`). `farm_animated_treasures` roda no fim da 2ª main: com Mahadi ou Pitiless Plunderer em campo, sacrifica todos os Treasures animados que sobraram (`sacrifice_treasures(for_mana=True)`: mana ability do Treasure; a mana sobra e esvazia), sem exceder os animados. Sem Mahadi/Plunderer custaria 1 Treasure por morte e **não é feito** (isso seria julgamento de valor). Todas as mortes alimentam o resto: Zulaport, Sephiroth (vira na 4ª), Marionette Master, Mirkwood Bats, Agent of the Iron Throne.
3. **Proxy do Dictate** (sem chave; só leitura): `dictate_triggers_total` conta as criaturas minhas que morrem com o Dictate em campo (*each opponent sacrifices a creature*: estado de oponente, 📊, nunca simulado). Antes o Dictate não tinha nem contagem.

### Medição (apoio; pareada; base = simulador antes, commit `7cd3f55`; N=10.000, sementes 3.000.000+i, 8 turnos; entre parênteses o modo resiliência)
Diferença pareada (variante − antes), IC95%:

| variante | win ≤8 (pp) | Treasures criados | estoque no fim | dano mesa | drain | mortes de criatura |
|---|---|---|---|---|---|---|
| só exílio expirando primeiro | **+1,26 ±0,37** (+0,34 ±0,22) | +0,85 ±0,16 (+0,27 ±0,06) | +0,16 ±0,08 (+0,02 ±0,03) | +2,12 ±1,00 (+0,57 ±0,23) | +0,91 ±0,38 (+0,23 ±0,09) | +0,04 ±0,06 (+0,06 ±0,04) |
| só Treasure animado (farm) | **+1,08 ±0,20** (+0,26 ±0,11) | +1,01 ±0,20 (+0,40 ±0,17) | +0,32 ±0,14 (+0,09 ±0,13) | +1,91 ±0,26 (+0,51 ±0,17) | +0,81 ±0,11 (+0,22 ±0,07) | **+0,67 ±0,07** (+0,27 ±0,05) |
| **as duas** | **+2,40 ±0,42** (+0,63 ±0,25) | **+1,92 ±0,26** (+0,68 ±0,18) | **+0,49 ±0,16** (+0,12 ±0,13 n.s.) | **+4,15 ±1,03** (+1,10 ±0,27) | **+1,77 ±0,40** (+0,46 ±0,11) | **+0,75 ±0,09** (+0,35 ±0,06) |

Base: win ≤8 11,9% (3,1%) · Treasures criados 10,95 (7,22) · **estoque no fim 3,01 (1,75)** · dano mesa 16,89 (8,42) · drain 7,58 (3,83) · mortes de criatura 3,40 (4,77).
**Cuidado ao ler "Treasures criados":** com o Mahadi e o Plunderer o Treasure sacrificado volta como um Treasure novo, então "criados" sobe mais do que o estoque. O ganho líquido é a coluna **estoque no fim** (+0,49 ±0,16 no padrão; +0,12 ±0,13, não significativo, na resiliência).
**Métricas diretas (por jogo, padrão, as duas vs antes):** magias do exílio conjuradas 0,77 → **1,46**; chamadas de Pact Boon 0,34 → **0,56**; cartas do exílio conjuradas antes das da mão 0 → **1,37**; cartas do pool que expiram sem uso 1,53 → **1,20**; Treasures-criatura sacrificados pelo farm 0 → **0,67**; Treasures pedidos pelo Mahadi 0,35 → **0,83** e pelo Plunderer 0,37 → **0,77**; gatilhos do Dictate (proxy) **0,24** (antes não contados). Só 54,5% das partidas terminam no mesmo estado do antes (68,5% na resiliência).

**Destino das cartas que o Prosper exila** (`resumos/prosper_destino_*.txt`; só as que já tiveram a sua vez; padrão, N=10.000):
| | antes | depois |
|---|---|---|
| terreno jogado | 97,8% (1.074 de 1.098) | 97,3% (1.110 de 1.141) |
| mágica conjurada | **37,1%** (744 de 2.005) | **97,2%** (1.943 de 1.999) |
| mágica expirou sem uso | **62,9%** (1.261) | **2,8%** (56) |
Jogos com pelo menos 1 exílio do Prosper: 15,5% → 16,1% (o Prosper só entra em campo do T4 em diante).

**Leitura (medido):** (a) o grosso do ganho de vitória vem das duas correções somadas (+2,40pp), cada uma sozinha dá cerca de +1pp; (b) o "farm" faz o que a sua T8 fez: 0,67 Treasures-criatura por jogo viram mortes, o que levanta as mortes de criatura em +0,67 e o Mahadi/Plunderer devolvem o Treasure (o estoque no fim sobe +0,32 só com o farm); (c) o terreno do Prosper já funcionava e continua; a mudança é nas mágicas.
**Lido como raciocínio, não medido:** o farm assume que o Mahadi/Plunderer continuam em campo até o end step (o simulador não tem remoção em resposta aí); e a política "sacrifica tudo que sobrou" desperdiça a mana desses Treasures (esvazia), o que é de graça só porque o Mahadi/Plunderer a repõem. O Dictate do simulador não faz o oponente sacrificar nada (📊): nas suas mãos ele é um motor de remoção por morte que o simulador subestima.

### Validação (Regra #1) — arquivada em `resultados-ab/2026-10-03-exilio-primeiro-e-mahadi/`
- **Smoke:** 99 cartas, 93 distintas, 0 desconhecidas, 0 duplicadas não básicas, 35 terrenos; 200 partidas sem exceção.
- **Testes dirigidos:** 17/17 (`resumos/testes_dirigidos.txt`): carta do exílio que expira vai antes da da mão (e a que não expira espera); comandante continua primeiro; mana pra uma só; farm com Mahadi (net zero no end step), com Plunderer, sem nenhum dos dois (não sacrifica), só os animados (os criados depois do combate ficam); cenário do T8 (Mahadi + Zulaport + Dictate, 7 animados = 7 drains + 7 gatilhos do Dictate); integração com o Sephiroth (vira na 4ª morte); Dictate pago com Treasures já criaturas (3 no custo + 4 sobrando = 7 mortes); invariantes em 3.000 partidas.
- **Bit-identidade com as 2 chaves desligadas:** 20.000/20.000 idênticas ao `7cd3f55` no modo padrão e 20.000/20.000 na resiliência.
- **Regressão:** 140.000 partidas (7 configurações/modos × 20.000, sementes 5.000.000+i), **0 exceções**, 0 cartas duplicadas, 0 partidas com mais de 1 jogada de terreno no turno, 0 com "animados vivos" ≠ 0 ao fim do turno, 0 Treasures < 0, 0 farms inválidos (nunca acima dos animados, nunca sem Mahadi/Plunderer), 0 emblemas do Sephiroth inconsistentes.
- **Reprodutibilidade:** `bash orquestracao/verificar_reproducao.sh --tudo` → **10/10 saídas byte a byte iguais** (`cmp`): as 4 tabelas do A/B refeitas dos `.json.xz` e a re-execução do smoke, dos 17 testes, da bit-identidade (20.000 × 2 modos), da regressão (140.000 partidas) e do destino do Prosper (antes e depois). Os arquivos dos lotes anteriores do Vihaan, ajustados para desligar as 2 chaves novas, foram reverificados contra o simulador vivo: `fora-da-mao` 8/8, `sephiroth` 11/11, `treasure-animado-e-mulligan` 7/7, `kingpin` 11/11, `inevitable-defeat` 6/6, `partida-manual-1` 7/7.

### Escopo verificado e NÃO verificado (Regra #7)
- **Verificado:** o início de `main_phase` (ordem exílio × mão), `play_from_impulse`, o fim da 2ª main (`farm_animated_treasures`), `on_creature_dies` (proxy do Dictate), e o destino medido de cada carta que o Prosper exila; por teste dirigido + A/B + regressão.
- **Não verificado / aberto:** (1) o farm sem Mahadi/Plunderer (custaria 1 Treasure por morte: decisão de valor, não feito); (2) a ordem dentro do turno: o simulador sacrifica no fim da 2ª main, então o Dictate (se estiver em campo) já conta cada morte, o que é igual ou melhor que a sua T8 (onde ele foi pago com os Treasures); (3) o Dictate segue 📊 (o oponente nunca sacrifica nada); (4) Lotho/Monologue Tax em 2ª mágica de oponente 📊; (5) o resto do `.py` não foi relido nesta rodada; (6) a leitura de "Machado" como Mahadi.

---

## Correção do simulador: conjurar/jogar de fora da mão (terreno do exílio, mágica do exílio, "spell cast", Storm, Sevinne's) — 2026-10-03

**Pedido (implícito):** o usuário respondeu *"Quero sim, sempre!"* à oferta de corrigir erros do simulador; estes saíram da análise da partida manual #1 (seção abaixo). Código: `vihaan_goldfish_v1.py` (antes = commit `c04840d`).
**Veredito:** cinco correções, cada uma atrás da sua chave, **todas no sentido esperado**. Juntas, no modo padrão (N=10.000, pareado): **win até o T8 +1,29 ±0,30pp** (10,6% → 11,9%), Treasures criados **+0,48 ±0,08**, dano de combate proxy +1,36 ±0,27, mana do T6 +0,06; no modo resiliência win +0,47 ±0,20pp. O ganho vem sobretudo de **jogar o terreno que o Prosper exila** (win +0,76 ±0,20pp sozinho) e de **resolver a mágica que ele exila** (+0,51 ±0,18pp); a contagem de "spell cast" e a Sevinne's mudam o número pouco e ficam por correção de regra. A mais grave em regra: **a mágica exilada pelo Prosper virava um permanente parado e o efeito nunca resolvia**, e **a Sevinne's Reclamation devolvia uma instantânea/feitiço (muitas vezes ela mesma) 0,14 vezes por jogo** (2.735 devoluções em 20.000 jogos), que também ficava parada no campo.

### O que mudou no código (5 chaves)
1. **Terreno do exílio** (`IMPULSE_LAND_PLAY_ENABLED`). Fontes que dizem *play* (Prosper, Inspired Tinkering, Face-Breaker; oráculo lido ao vivo) mandam o terreno exilado para `impulse_lands`; ele é a jogada de terreno do turno (**antes** do terreno da mão, que não expira; entra untapped primeiro) e dispara o **Pact Boon** (ruling 2021-07-23: qualquer carta jogada do exílio). Grenzo e Laughing Jasper Flint dizem *cast*: terreno exilado por eles continua não jogável.
2. **Mágica do exílio** (`IMPULSE_CAST_PIPELINE_ENABLED`). `play_from_impulse` agora chama `cast_card(..., from_zone="exile")`: cobra o custo, conta como magia, extort, Lotho, **resolve** a instantânea/feitiço e a manda ao cemitério; o Pact Boon dispara no cast, antes de resolver. Antes: `enter_battlefield` direto, sem resolver.
3. **Contagem de "spell cast"** (`SPELL_CAST_COUNT_ALL_PATHS_ENABLED`). Flashback da Sevinne's e a mágica do Cascade contam como magia conjurada (Lotho, extort; Pact Boon no Cascade, que conjura do exílio; Rain of Riches no flashback pago com Treasure). E o **Lotho só dispara se já estava em campo no cast** (foto antes de a magia entrar; ruling 2023-06-16: as conjuradas antes dele contam); antes ele disparava contra si mesmo quando era a 2ª mágica.
4. **Storm** (`STORM_SACRIFICE_PUMP_ENABLED`). *Whenever you sacrifice a Treasure, +1/+0 until end of turn* (ruling 2017-09-29: qualquer sacrifício; os pagos pra conjurar a Storm não contam, `storm_sac_baseline`): entra no poder dela no dano proxy e no "that many" do Cleaver quando ela é o portador.
5. **Alvo da Sevinne's** (`SEVINNE_PERMANENT_TARGET_ENABLED`). *Return target permanent card with MV ≤3* (ruling 2024-06-07: artefato, batalha, criatura, encantamento, **terreno**, planeswalker). O filtro antigo só excluía terreno, então a heurística "maior MV" escolhia com frequência **a própria Sevinne's** (que já está no cemitério ao resolver) ou um feitiço. Agora instantânea/feitiço não é alvo; terreno é (entra tapped se a regra dele manda, não gasta jogada de terreno). *Descoberto pelo invariante de validação da correção 2, não pela análise da partida.*

### Medição (apoio; pareada; base = simulador antes, commit `c04840d`; N=10.000, sementes 3.000.000+i, 8 turnos; entre parênteses o modo resiliência)
Diferença pareada (variante − antes), IC95%:

| variante | win ≤8 (pp) | Treasures | combate | mortes de criatura | recursões | mana T6 |
|---|---|---|---|---|---|---|
| só terreno do exílio | **+0,76 ±0,20** (+0,19 ±0,09) | +0,28 ±0,06 (+0,13 ±0,04) | +0,95 ±0,16 (+0,42 ±0,08) | +0,12 ±0,02 (+0,08 ±0,02) | +0,004 | +0,063 ±0,007 (+0,047) |
| só magia do exílio | **+0,51 ±0,18** (+0,32 ±0,14) | +0,26 ±0,04 (+0,15 ±0,03) | +0,67 ±0,45 (+0,29 ±0,08) | +0,11 ±0,03 (+0,07 ±0,02) | +0,019 | +0,005 |
| só contagem de "spell cast" | −0,12 ±0,14 (−0,09 ±0,09) n.s. | −0,02 ±0,03 n.s. | −0,23 ±0,13 | −0,005 | 0 | −0,007 ±0,004 |
| só Storm | +0,23 ±0,09 (+0,11 ±0,07) | +0,002 | **+0,54 ±0,04** (+0,29 ±0,02) | +0,001 | 0 | 0 |
| só alvo da Sevinne's | −0,01 ±0,08 n.s. (+0,03 ±0,08) | −0,007 ±0,009 | −0,29 ±0,10 (+0,04 ±0,05) | −0,007 | **−0,115 ±0,007** (−0,058) | −0,001 |
| **as cinco** | **+1,29 ±0,30** (+0,47 ±0,20) | **+0,48 ±0,08** (+0,26 ±0,06) | **+1,36 ±0,27** (+0,86 ±0,16) | **+0,23 ±0,04** (+0,12 ±0,03) | −0,105 ±0,008 (−0,043) | **+0,061 ±0,008** (+0,052) |

Base: win ≤8 10,6% (2,6%) · Treasures criados 10,47 (6,95) · combate 50,44 (32,12) · mortes de criatura 3,18 (4,65) · mana T6 6,13 (5,85).
**Métricas diretas (por jogo, padrão, as cinco vs antes):** terrenos do exílio jogados 0 → **0,275**; magias do exílio conjuradas 0 → **0,771**; chamadas de Pact Boon 0,180 → **0,343**; chamadas do Lotho 0,354 → 0,393; bônus da Storm somado 0 → **0,573**; **cartas de instantânea/feitiço paradas no campo no fim 0,359 → 0,000**. Só 39,0% das partidas terminam no mesmo estado do antes (52,6% na resiliência), de modo que a mudança é ampla, mas pequena em magnitude.

**Leitura (medido):** (a) cada contador direto sai de zero e o número de mágicas mortas no campo sai de 0,36 por jogo para 0; é a evidência de que as correções disparam de verdade. (b) Terreno e magia do exílio são os que mexem em vitória e mana. (c) A contagem de "spell cast" quase não muda o total do Lotho (0,354 → 0,334 chamadas sozinha): o auto-disparo que sumiu e as mágicas do exílio/flashback que entraram se compensam; o efeito é de regra, não de número (e é o que o seu T7/T8 exigia). (d) A Sevinne's tira "recursões" **fantasma** (0,115 por jogo: devoluções de feitiço que não faziam nada); o combate −0,29 ±0,10 no padrão **não se repete** na resiliência (+0,04 ±0,05) nem no lote de 2.000 (−0,11 ±0,08): não interpreto.
**Lido como raciocínio, não medido:** a política de jogada continua a de antes: a carta do exílio só é jogada **depois** de tudo que dá pra jogar da mão (`main_phase`), embora ela expire e a da mão não. Medido: **1,5 cartas não-terreno por jogo entram no pool de impulso e expiram sem ser jogadas** (padrão, até o T8; 1,0 na resiliência), inalterado por estas correções. Isso é decisão de ordem de jogo, não de regra, e fica como achado aberto.

### Validação (Regra #1) — arquivada em `resultados-ab/2026-10-03-fora-da-mao/`
- **Smoke:** 99 cartas, 93 distintas, 0 desconhecidas, 0 duplicadas não básicas, 35 terrenos; 200 partidas sem exceção.
- **Testes dirigidos:** 37/37 (`resumos/testes_dirigidos.txt`), incluindo os cenários reais da partida manual (T5: terreno do exílio + Treasure; T6: Sevinne's do exílio devolvendo o Mahadi; T7: Lotho do exílio + Tax = 2 Treasures e −1 de vida; T8: flashback + Dictate dispara o Lotho), invariantes em 3.000 partidas (nenhuma mágica parada no campo, nenhuma carta duplicada) e, para cada correção, o teste com a chave **desligada** reproduzindo o comportamento antigo (no código antigo, 399 de 1.500 jogos terminam com mágica parada no campo).
- **Bit-identidade com as 5 chaves desligadas:** 20.000/20.000 partidas idênticas ao `c04840d` no modo padrão e 20.000/20.000 na resiliência.
- **Regressão:** 180.000 partidas (9 configurações/modos × 20.000, sementes 5.000.000+i), **0 exceções**, 0 cartas duplicadas, 0 partidas com mais de 1 jogada de terreno no turno, 0 com "animados vivos" ≠ 0 ao fim do turno, 0 com Treasures < 0, 0 emblemas do Sephiroth inconsistentes; com as cinco chaves, **0 jogos terminam com instantânea/feitiço parado no campo** (no código antigo: 5.310 de 20.000 jogos no padrão e 3.548 na resiliência).

### Escopo verificado e NÃO verificado (Regra #7)
- **Verificado:** os 5 caminhos que movem carta de fora da mão (`cast_card`, `play_from_impulse`, `play_land`/`play_impulse_land`, `try_sevinne_flashback`, `do_cascade`), o filtro "permanent card" nos 2 pontos da Sevinne's, o contador de Treasures sacrificados e a Storm/Cleaver no combate; por teste dirigido + A/B + regressão.
- **Não verificado / aberto:** (1) política "carta do exílio por último" (1,5 cartas/jogo expiram); (2) Lotho e Monologue Tax em 2ª mágica de **oponente** continuam 📊 (estado de oponente); (3) o resto do `.py` não foi relido nesta rodada; (4) a escolha do alvo da Sevinne's segue "maior MV" (heurística; terreno só quando não há outro alvo); (5) wipes próprios usam o caminho de sacrifício (Mayhem Devil a mais, comandante excluído), Sephiroth só conta mortes minhas, Xorn/Plunderer em lote (achados abertos das rodadas anteriores).

---

## Partida manual #1 do Vihaan (8 turnos, 2026-10-03) — auditoria contra o oráculo + comparação com o simulador

**Pedido:** *"Analise esse Goldfish do Vihaan: Assumi algumas mortes em combate para gerar tesouros com o Mahadi, e um oponente fez 2 spells com Lotho e Tax em campo, gerando 2 tesouros fora do meu turno."* + log do Archidekt (8 turnos).
**Veredito:**
1. **Nenhuma jogada ilegal nos pontos que o log permite checar** (terrenos e se entram tapped, custos pagos, Pact Boon com carta jogada do exílio, gatilho de ataque da Storm, Sevinne's do exílio e depois flashback, Mahadi voltando do cemitério). A conta de mana fecha **exatamente** em T2, T3, T4 e T8.
2. **Treasures: 21 criados (2 / 6 / 7 / 6 em T5–T8). Só T5 fecha sozinho.** T6 e T7 só fecham com duas informações que o log não registra (o dano do equipado com o Reaver Cleaver e quantas mortes você assumiu); abaixo está a conta, com as fórmulas, para você confirmar. **Pelo oráculo, T7 teria no mínimo 6 e até 10 Treasures; o log tem 7.**
3. **Dois pontos de regra que dependem de você:** o contador +1/+1 do Treasure em T7 (se marcava o Cleaver, o equip não podia ter sido naquele momento) e o **The Eldest Reborn do oponente** (o capítulo I aparece, você sacrificou o Zulaport; o capítulo II, "descarte uma carta", não aparece).
4. **Contra o simulador (medido):** 21 Treasures até o T8 está no ~**P90** do simulador (9,8% dos jogos do modo padrão chegam a 21; 3,4% no modo resiliência). Achei **4 lacunas reais no simulador** que esta partida exercita, todas confirmadas por teste direto no código: (a) ele **nunca joga o terreno que o Prosper exila** (você fez isso em T5: Desolate Mire + Treasure do Pact Boon); (b) uma **mágica jogada do exílio vira permanente no campo e o efeito nunca resolve** (o Blood Money exilado não destrói nada; a Sevinne's do exílio de T6 não devolveria o Mahadi); (c) mágica do exílio e **flashback não contam como "spell cast"**, então o Lotho de T7 e T8 não dispararia, e o Lotho conjurado como 2ª mágica **dispara contra si mesmo**; (d) a 3ª cláusula da Storm (*+1/+0 por Treasure sacrificado*) **não existe**; no seu T6, com o Cleaver, vale 1 Treasure.

### 1. Sequência verificada turno a turno (ids do log; só o que o oráculo permite checar)
| T | O que o log mostra | Oráculo / regra | Status |
|---|---|---|---|
| 1 | Dragonskull Summit (tapped) com Mountain na mão | *enters tapped unless you control a Swamp or a Mountain*: sem Mountain em campo, entra tapped; é a jogada "tapped primeiro" | ✅ |
| 2 | Mountain; Mountain + Summit → Arcane Signet | 2 mana, custo 2 | ✅ |
| 3 | Path of Ancestry (tapped); Signet + Summit + Mountain → Vihaan | custo {R}{W}{B}; Signet dá W | ✅ |
| 4 | Forge; Path + Signet + Mountain + Forge → Prosper; Vihaan ataca; Prosper exila Desolate Mire no end step; Wheel do oponente descarta 5 cartas | custo 4; **5 fontes disponíveis, 4 usadas** (Summit sem usar) | ✅ (1 mana sem uso) |
| 5 | **Desolate Mire jogada do exílio → Treasure**; Sol Ring, Rakdos Signet, Zulaport, Storm; Storm ataca → Treasure; Prosper exila Sevinne's | Pact Boon dispara ao **jogar qualquer carta do exílio** (ruling 2021-07-23), terreno inclusive; Storm: *whenever attacks, create a Treasure* | ✅ 2 Treasures = 1 Pact Boon + 1 Storm (**fecha**) |
| 6 | Sevinne's **do exílio** → Mahadi (MV3) volta; Reaver Cleaver; Storm ataca e morre; Eldest Reborn do oponente; Prosper exila Lotho; Zulaport morre | Pact Boon (+1) ao conjurar do exílio; alvo MV ≤3 ✓; Mahadi só conta mortes **do meu turno** (Zulaport morreu no turno do oponente, não conta) | ✅ regras; Treasures: ver §2 |
| 7 | Lotho **do exílio**; Monologue Tax; Prosper exila Blood Money | Pact Boon ao jogar Lotho do exílio; Lotho dispara na **2ª mágica de qualquer jogador** (a Tax foi a minha 2ª) | ⚠️ ver §2 |
| 8 | Swamp; Sevinne's **flashback** → Zulaport; Dictate of Erebos | flashback {4}{W} = 5 ✓, exila depois ✓; Dictate 5 ✓ | ✅ regras; fontes sem Treasure = 10 = 5 + 5 |

### 2. Conta de Treasures (log × oráculo)
Mana por turno (`resumos/ledger_mana.txt`): fontes líquidas sem contar Treasure = gasto em T2 (2), T3 (3), T4 (4 + 1 sem uso), **T8 (10 = Sevinne's 5 + Dictate 5)**; sobras de **+1 em T5** e **+3 em T6 e em T7**, que são exatamente o custo do **Equip {3} do Reaver Cleaver** (o log não registra o equip: é inferência).
Treasures "tapped" que **continuam** no turno seguinte = atacantes marcados (a animação do Vihaan dá vigilância aos outlaws, então o toque é só marcação); os que **somem** = mortos/sacrificados: T6 some 1 (F--PiJszG), T7 somem 2 (olyMYvYre, QaM6nMtBe) — **são as mortes que você disse ter assumido em combate**.

| Turno | Linhas "criada" no log | Fontes pelo oráculo | Fecha? |
|---|---|---|---|
| T5 | 2 | Pact Boon (Mire do exílio) 1 + Storm ataque 1 | ✅ exato |
| T6 | 6 | Pact Boon (Sevinne's do exílio) 1 + Storm ataque 1 = **2 certos**; restam 4 = **Cleaver (dano do Storm equipado: 3, ou 4 se o Treasure F sacrificado deu +1/+0)** + **Mahadi (criaturas mortas no meu turno: Storm, mais as que você assumiu)** | só com c + m = 4 (não dá pra separar pelo log) |
| T7 | 7 | Pact Boon (Lotho do exílio) 1 + Lotho na 2ª mágica (Tax) 1 = **2 certos**; + Mahadi (≥2: olyMYvYre e QaM6nMtBe) + Cleaver (0–4) + as **2 de fora do turno** (Lotho + Tax numa 2ª mágica do oponente) | **6 a 10 esperados × 7 no log** |
| T8 | 6 | **Lotho na 2ª mágica (Dictate; a Sevinne's em flashback foi a 1ª; sem Pact Boon porque saiu do cemitério, não do exílio) = 1 certo** + Mahadi (m mortes assumidas): 1 + m = 6, logo m = 5 se o Lotho foi contado; ou 6 mortes assumidas se ele foi esquecido. Os 7 toques de Treasure em T8 foram **sacrifícios de Treasures já criaturas para pagar o Dictate** (resposta do usuário; a minha inferência anterior, "atacantes marcados", estava errada) | 7 sacrificados como criatura = 7 mortes pro Mahadi, mais o Lotho no Dictate: **8 esperados × 6 no log** se os 7 eram criaturas |

**Onde está o buraco, por turno:** em T7 **nenhuma linha "criada" aparece junto da conjuração do Lotho (Pact Boon) nem da Tax (gatilho do Lotho)**; as 4 linhas antes do end step e as 3 depois comportam duas leituras igualmente possíveis (Cleaver 4 + Mahadi 1 + oponente 2 = 7, ou Mahadi 2 + oponente 2 + 3 outras = 7), e as duas deixam de fora pelo menos 2–3 Treasures que o oráculo pede. Em T6, a Storm morta em combate dá 1 morte; se o Treasure F foi sacrificado com a Storm em campo, ela ganha **+1/+0** (ruling 2017-09-29: qualquer sacrifício) e com o Cleaver isso vira **+1 Treasure**.

### 3. Dúvidas para você (o log não responde)
1. **T6:** de onde vieram as 4 linhas além de Pact Boon e do ataque da Storm? Quanto foi o dano da Storm equipada (3 ou 4)? Quantas mortes você assumiu em T6 (só a Storm, ou o F--PiJszG também)?
2. **T7 e T8:** os Treasures do **Pact Boon do Lotho** e do **Lotho na Tax** (T7) e do **Lotho no Dictate** (T8), com os −1 de vida de cada um, foram criados? Em quais linhas? E os 2 do oponente (Lotho + Tax), em qual bloco?
3. **T7, o contador +1/+1 no Treasure 24DnlO5iG:** era o marcador do Cleaver? Equip só no timing de feitiço, e o Treasure só vira criatura no início do combate; se o equip foi antes, o alvo teria que ser uma criatura de verdade (Lotho tem haste pelo Vihaan; o Mahadi não).
4. **The Eldest Reborn:** capítulo II (cada oponente descarta uma carta) deveria ocorrer no turno seguinte do jogador dele, entre T7 e T8; não há descarte no log. O capítulo III põe uma criatura de **qualquer cemitério** no controle dele depois do T8. Você descartou/vai descartar?
5. **O que ficou na mão sem uso até o T8:** Magda (2 mana, na mão desde T4), Aya of Alexandria (4), Path to Exile (1) e a **Blood Money exilada pelo Prosper em T7, que expirou no fim do T8** (7 mana; em T8 havia **até 12 Treasures**: 15 criados até T7, 3 somem por id, e os que não geraram linha contam como vivos). Foi decisão (goldfish sem alvos, preservar Treasures) ou esquecimento? Não estou dizendo que erraram: cada uma é motor do deck (Magda é sumidouro de Treasures e dá Dragon 4/4; Blood Money com Zulaport + Mahadi + Dictate em campo é morte em massa com payoff), então a resposta muda a leitura.
6. **Sevinne's flashback (T8):** a cópia ("you may copy this spell, new target") não foi usada. No cemitério havia Storm (MV3), Tainted Peak (MV0, terreno também é permanente) e o Zulaport usado. Foi escolha?

### 3b. Respostas do usuário (mesma data) e o que mudam
Transcrição e leitura em `resultados-ab/2026-10-03-partida-manual-1/LEIAME.md` (seção "Respostas do usuário"). Resumo:
| Pergunta | Resposta | Efeito |
|---|---|---|
| T6: mortes assumidas e dano da Storm/Cleaver | **3 mortes** (Mahadi cria 3); o **Cleaver fez 2 de dano** no primeiro ataque | T6 = Pact Boon 1 + ataque da Storm 1 + Cleaver 2 + Mahadi 3 = **7 esperados × 6 linhas "criada"**. Entre o ataque da Storm e a morte dela há **2** linhas onde se esperam 3 (Storm 1 + Cleaver 2): **falta 1 Treasure no combate de T6** (dano 2 = criatura de poder 1 + o +1 do Cleaver: Zulaport ou Prosper; a Storm daria 3) |
| Eldest Reborn | sacrificou o **Zulaport** (capítulo I como no log); **esqueceu** o descarte (capítulo II) | log passa a ✅ no capítulo I; o II não foi registrado (o III reanimaria do cemitério de qualquer jogador depois do T8) |
| Magda, Aya, Path sem uso | foram **descartadas pro Wheel of Fortune** (li como um 2º Wheel depois do T8) | deixa de ser "esquecimento": não há o que cobrar; a Blood Money exilada em T7 que expirou no T8 **continua sem resposta** |
| T8: Dictate | pagou com **Treasures já criaturas** "para ativar o Machado mais vezes" (li **Mahadi**) | os 7 toques de Treasure do T8 são sacrifícios (não atacantes); cada animado sacrificado = 1 criatura morta = 1 Treasure do Mahadi no end step. T8: 7 mortes + Lotho no Dictate = **8 esperados × 6 linhas** se os 7 eram criaturas |
**T7 (resposta do usuário em 2026-10-04): "T7 foi erro meu".** O que faltava no log de T7 (Pact Boon do Lotho jogado do exílio; Lotho na 2ª mágica) foi esquecimento de registro, não erro de regra; **fecha**.
**Ainda sem resposta:** o contador +1/+1 do Treasure em T7, a Sevinne's sem a cópia no T8, a Blood Money que expirou, e quantos dos 7 Treasures do T8 eram criaturas.
**Dois padrões que se repetem:** (1) os gatilhos do **Lotho** (Pact Boon ao jogá-lo do exílio, 2ª mágica) não aparecem como linhas "criada": em T7 o usuário confirmou que foi **erro dele** (T8 provavelmente igual: Lotho no Dictate); (2) em T6 falta 1 Treasure no combate. Ambos subcontam a favor do oráculo (o jogador registrou **menos** Treasures do que as regras davam).

### 4. Comparação com o simulador (medido; N=10.000, sementes 3.000.000+i, 8 turnos; simulador no estado do commit `c04840d`; `resumos/comparacao_simulador_*.txt`)
| | partida | simulador padrão | simulador resiliência |
|---|---|---|---|
| Treasures criados acumulados T5 / T6 / T7 / T8 | 2 / 8 / 15 / 21 | médias 1,94 / 3,96 / 6,79 / 10,42 | 1,58 / 3,01 / 4,80 / 6,83 |
| % dos jogos do simulador com ≥ a partida | — | 52,7 / 13,4 / 8,1 / **9,7** | 43,1 / 7,7 / 3,3 / **3,0** |
| P(≥21 até o T8) | 21 | 9,8% (p90 = 20, p99 = 39) | 3,4% |
| Comandante conjurado até o T3 | T3 | 92,8% | 88,0% |
| Mana total T2 / T3 / T4 | 2 / 3 / 5 | 2,03 / 3,19 / 4,02 | 2,03 / 3,19 / 4,00 |

**Leitura (medido):** a partida está no **topo ~10%** do simulador (não é outlier). Por fonte, o simulador (padrão) gera por jogo até o T8: Storm ataque 0,73, Cleaver 0,65, **Mahadi 0,44**, **Lotho (2ª mágica minha) 0,44**; **Tax e Lotho em 2ª mágica de OPONENTE: 0** (estrutural 📊: *"Whenever an opponent casts their second spell each turn"* / *"Whenever a player casts their second spell each turn"* dependem de mágicas de oponente que o simulador não modela; nunca fabriquei isso). As **mortes assumidas em combate** também não existem no simulador (sem bloqueio, sem remoção em combate), então o Mahadi do simulador é piso (as mortes dele vêm só de sacrifícios próprios e wipes).
**Lacunas reais do simulador achadas aqui (Regra #6: cláusulas operacionais do relato, testadas no código do commit `c04840d`):**
1. **Terreno do exílio.** `play_from_impulse` filtra terreno (`e[0] != "land"` e `ctype != "land"`), então **o terreno exilado pelo Prosper nunca é jogado** e o Pact Boon dele nunca dispara. Medido: **1,78 terrenos entram no pool de impulso por jogo (46% dos jogos têm ≥1)**, **0,38 por jogo com o Prosper em campo na hora** (0,17 na resiliência): cada um é uma jogada de terreno e um Treasure perdidos. É o que a sua T5 fez. (Fontes que dizem *play*: Prosper, Inspired Tinkering, Face-Breaker; Grenzo e Laughing Jasper Flint dizem *cast*, terreno não vale.)
2. **Mágica do exílio.** Teste direto: com o Prosper em campo e o Blood Money no pool, `play_from_impulse` o **põe no campo como permanente** (`"Blood Money" in battlefield = True`, cemitério = False), **sem destruir nenhuma criatura**, sem contar como mágica conjurada; só o Treasure do Pact Boon sai. Vale para toda mágica exilada (feitiço ou instantânea): Blood Money, Sevinne's Reclamation, Big Score, Path to Exile...
3. **Contagem de "spell cast" (Lotho).** `spells_cast_this_turn` só sobe em `cast_card`. Teste direto: Lotho do exílio + Monologue Tax da mão → contador 1 (o Lotho **não** dispara, o seu T7 sim); flashback da Sevinne's → contador 0 (esperado 1; o seu T8 sim). E **Sol Ring depois Lotho (2ª mágica)** → o Lotho cria 1 Treasure e tira 1 de vida **de si mesmo**, porque o teste de "Lotho em campo" roda depois de ele entrar: pelo oráculo ele estava na pilha. O Cascade (Rain of Riches) também não conta a mágica que conjura.
4. **Storm.** *"Whenever you sacrifice a Treasure, Captain Lannery Storm gets +1/+0 until end of turn"* (ruling 2017-09-29: qualquer sacrifício; os pagos para conjurar a própria Storm não contam) não aparece no `.py`: só o gatilho de ataque. Com o Cleaver equipado nela, o "that many" cresce 1 por Treasure sacrificado antes do dano.
**Lido como raciocínio, não medido:** o impacto dessas lacunas no win ≤T8 e no ritmo de mana só sai de um A/B depois do conserto.
**Atualização (mesmo dia):** as quatro lacunas foram corrigidas, com uma quinta achada na validação (alvo da Sevinne's); ver a seção "Correção do simulador: conjurar/jogar de fora da mão", logo acima neste log. Os números desta seção (§4) são do simulador **antes** da correção (commit `c04840d`); para o simulador atual, a coluna de comparação mudaria um pouco.

### Escopo verificado e NÃO verificado (Regra #7)
- **Verificado:** terrenos (tapped/untapped), custos de todas as magias que entraram em campo, Pact Boon em T5/T6/T7, ataque da Storm, Sevinne's (exílio e flashback), identificação dos Treasures que somem (por id), conta de mana por turno (script `ledger_mana.py`), comparação por distribuição com o simulador.
- **NÃO verificado:** o que o log não registra (equips, vida, ordem real de triggers: a ordem das linhas dentro do turno nem sempre é cronológica, como a Prosper do T6 aparecendo depois do Eldest Reborn do oponente); a atribuição exata de cada Treasure de T6/T7/T8 (precisa das suas respostas acima); se alguma carta saiu do turno certo por escolha. **Não** avaliei se as escolhas de jogo foram boas (isso exigiria os motores e o Commander Spellbook: Regra #4).
- **Simulador:** o resto do `.py` não foi relido nesta rodada; só `play_from_impulse`, `play_land`, `cast_card`, `try_sevinne_flashback` (a cópia **está** modelada: original + cópia), `do_cascade`, o gatilho de ataque da Storm / equip / dano do Cleaver e o Lotho/Tax/Mahadi como acima.

---

## Correção do simulador: Sephiroth (emblema acumulável, wipe com mortes simultâneas, contador por turno) — 2026-10-03

**Pedido:** *"Quero sim, corrija os itens 2 e 3."* (itens da lista de lacunas do Sephiroth que eu tinha levantado ao responder se o simulador flipava o Sephiroth com 4 mortes no mesmo turno.)
**Veredito:** as três correções estão no `vihaan_goldfish_v1.py`, cada uma atrás da sua chave (`SEPHIROTH_EMBLEM_STACKING_ENABLED`, `SEPHIROTH_SIMULTANEOUS_DEATH_ENABLED`, `SEPHIROTH_TURN_BOUNDARY_ENABLED`). O efeito é **pequeno em jogo médio e grande na taxa de "Sephiroth virou"**: no modo resiliência (oponente com wipe) a taxa cai de **2,31% para ~0,6%** dos jogos, porque **72% das viradas antigas (167 de 231) vinham de wipes em que o Sephiroth morria junto** e, pela ruling, **não vira**. Drain, dano da mesa e vitória até o T8 não se mexem de forma mensurável.

### O que o oráculo diz (lido ao vivo, 2026-10-03; arquivado em `dados/oraculo_e_rulings.json`)
- Frente: *Whenever another creature dies, target opponent loses 1 life and you gain 1 life. If this is the fourth time this ability has resolved this turn, transform Sephiroth.*
- Verso: *Super Nova — As this creature transforms into Sephiroth, One-Winged Angel, you get an emblem with "Whenever a creature dies, target opponent loses 1 life and you gain 1 life."*
- **Ruling 2025-06-06:** *If Sephiroth, Fabled SOLDIER and one or more other creatures die at the same time, its last ability will trigger for each of those other creatures. (It won't transform, though.)* As outras 9 rulings são sobre faces de carta dupla e não mudam a leitura.

### O que mudou no código (3 correções + 1 achada no caminho)
1. **Emblema + Sephiroth de frente = 2 gatilhos por morte** (`..._EMBLEM_STACKING_ENABLED`). O emblema é objeto independente, então se o Sephiroth volta de frente (reanimado) com um emblema já existente, cada morte dispara o do emblema **e** o da frente; a 4ª resolução da frente vira de novo e dá um **2º emblema**, e emblemas acumulam. O código antigo guardava um sim/não e só disparava o emblema (1 por morte). Passei a contar `super_nova_emblems`.
2. **Wipe com mortes simultâneas** (`..._SIMULTANEOUS_DEATH_ENABLED`). Os wipes próprios (Blood Money, Blasphemous Act) e o do oponente (`try_smart_opponent_wipe`) tiram as criaturas do campo uma a uma, então o resultado dependia da ORDEM de remoção: Sephiroth primeiro na lista = 0 gatilhos; Sephiroth por último = 4 gatilhos **e virava** (contra a ruling). Agora `begin_mass_death`/`end_mass_death` tiram a foto do que ele enxerga antes do lote: dispara para cada outra criatura (fichas incluídas), em qualquer ordem, e **não vira** se ele morre junto.
3. **"4ª vez neste turno"** (`..._TURN_BOUNDARY_ENABLED`) — achado enquanto corrigia: `sephiroth_deaths_this_turn` só zerava no meu turno, então mortes do meu turno vazavam para o turno do oponente (e entre os 3 oponentes). Agora zera em cada turno de oponente, e quando o Sephiroth reentra em campo (objeto novo).
4. **Erro meu pego pelos testes dirigidos** (antes de medir qualquer coisa): na primeira versão do lote, a morte do **próprio** Sephiroth disparava a habilidade da frente (5 gatilhos num wipe com 4 outras criaturas, em vez de 4). A frente diz "another". Agora as vias de permanente nomeado (`sacrifice_named_creature`, `remove_permanent`) informam quem morreu (`dying=`); a morte dele não dispara a frente, mas dispara o emblema ("a creature dies", sem "another") se já houver um.

### Medição (apoio; pareada; base = simulador antes, commit `ba74496`, que já tem Treasure animado/mulligan/tapped)
Diferença pareada (variante − antes), IC95%, N=10.000, sementes 3.000.000+i, 8 turnos. A coluna "virou" é a taxa de jogos com o emblema:

| modo / variante | virou (pp) | emblemas/jogo | drain | dano mesa | win ≤T8 (pp) | jogos com estado final igual ao antes |
|---|---|---|---|---|---|---|
| **padrão** — base | 2,03% | 0,0203 | 7,01 | 15,61 | 10,6% | — |
| padrão — só emblema acumulável | 0 | 0 | 0 | 0 | 0 | 99,68% |
| padrão — só wipe simultâneo | −0,27 ±0,10 | −0,003 ±0,001 | +0,005 ±0,005 | +0,005 ±0,005 | 0 | 99,04% |
| padrão — só contador por turno | 0 | 0 | 0 | 0 | 0 | 100% |
| **padrão — as três** | **−0,27 ±0,10** | −0,003 ±0,001 | +0,005 ±0,005 | +0,005 ±0,005 | 0 | 99,04% |
| **resiliência** — base | 2,31% | 0,0231 | 3,63 | 7,99 | 2,6% | — |
| resiliência — só emblema acumulável | 0 | 0 | 0 | 0 | 0 | 99,89% |
| resiliência — só wipe simultâneo | **−1,67 ±0,25** | −0,017 ±0,003 | +0,002 ±0,007 | +0,002 ±0,007 | 0 | 96,95% |
| resiliência — só contador por turno | −0,69 ±0,16 | −0,007 ±0,002 | −0,030 ±0,008 | −0,030 ±0,008 | 0 | 94,64% |
| **resiliência — as três** | **−1,70 ±0,25** | −0,017 ±0,003 | +0,002 ±0,007 | +0,001 ±0,008 | 0 | 93,07% |

**Leitura (medido):** (a) a virada cai porque o simulador antigo virava o Sephiroth em wipe em que ele morria junto (contra a ruling) e carregava contagem de um turno para outro. Instrumentado no código antigo (`resumos/flips_em_wipe_antes_resiliencia.txt`, resiliência, N=10.000): das **231** viradas, **167 foram em wipe com o Sephiroth morrendo junto** (162 de oponente, 5 meus), 6 em wipe com ele sobrevivendo e 58 fora de wipe. (b) O drain não se mexe: o que se perde de emblemas fantasmas se compensa com os gatilhos que antes se perdiam quando o Sephiroth era removido primeiro. (c) O **emblema acumulável quase nunca acontece**: em 20.000 jogos do modo padrão o "emblema + frente em campo" gerou **4 gatilhos extras** no total; em 10.000 jogos de resiliência, 1 jogo (2 gatilhos extras). Precisa de recursão do Sephiroth depois de virar. É correção de regra, não de número. (d) No modo padrão a variante "contador por turno" não muda nada porque esse modo não tem turno de oponente; os 6 jogos de 2.000 que mudam de estado na variante "emblema" divergem **só** no campo `sephiroth_deaths_this_turn` (zerado na reentrada), sem efeito em métrica (`resumos/explica_diferencas_*.txt`).
**Lido como raciocínio, não medido:** nenhuma dessas correções muda a recomendação do Sephiroth na lista; só a confiança no número dele no modo resiliência (a taxa de emblema era ~3,8× a real: 2,31% contra ~0,61%).

### Validação (Regra #1) — arquivada em `resultados-ab/2026-10-03-sephiroth/`
- **Smoke:** 99 cartas, 93 distintas, 0 desconhecidas, 0 duplicadas não básicas, 35 terrenos; 200 partidas sem exceção.
- **Testes dirigidos:** 28/28 (`resumos/testes_dirigidos.txt`): emblema + frente = 2 gatilhos por morte; 4ª resolução dá o 2º emblema; wipe com o Sephiroth primeiro e último na lista dão o mesmo resultado (4 gatilhos, não vira); o mesmo no wipe do oponente; 5 fichas morrendo juntas com ele vivo (vira na 4ª, 5 gatilhos); emblema + frente morrendo juntos (7 = 4 do emblema + 3 da frente); contador zera no turno do oponente e na reentrada; com as chaves desligadas cada teste reproduz o comportamento antigo documentado.
- **Bit-identidade com as 3 chaves desligadas:** 20.000/20.000 idênticas ao commit `ba74496` no modo padrão e 20.000/20.000 na resiliência.
- **Regressão:** 140.000 partidas (7 configurações/modos × 20.000, sementes 5.000.000+i), **0 exceções**, 0 cartas duplicadas, 0 violações dos invariantes novos (`has_super_nova_emblem == (emblemas>0)`, virou ⇒ ≥1 emblema, nenhum lote de mortes ativo no fim do turno).

### Escopo verificado e NÃO verificado (Regra #7)
- **Verificado:** só os gatilhos de morte do Sephiroth (frente e emblema) em todas as vias que removem criatura nomeada ou ficha em lote (Blood Money, Blasphemous Act, `try_smart_opponent_wipe`, `sacrifice_named_creature`, `remove_permanent`), por teste dirigido + A/B + regressão. A habilidade de entrada/ataque ("sacrifice another creature, draw") **não foi relida** nesta rodada.
- **Continuam abertos (não corrigidos aqui):** (1) os wipes próprios usam o caminho de **sacrifício**, mas "destroy" não é sacrifício: Mayhem Devil dispara a mais e o comandante é excluído; (2) o Sephiroth só conta mortes das minhas criaturas (a frente diz "another creature", de qualquer controlador: mortes de criaturas de oponente não entram, estrutural 📊 por serem estado de oponente); (3) política: o Sephiroth poderia sacrificar Treasures animados como fodder; (4) Xorn/Pitiless Plunderer por lote de evento; (5) 7 outros decks ainda sorteiam as cartas do fundo no mulligan.

---

## Correção do simulador: Treasure animado, mulligan e terreno tapped — 2026-10-03

**Pedido:** *"Quer que eu corrija agora o roteamento do Treasure animado para todos os gatilhos de criatura? Isso move os números de base do Vihaan, então eu rodaria antes e depois."* — *"Quero sim, corrija todos os erros do simulador!"*
**Veredito:** as três correções estão no `vihaan_goldfish_v1.py`, cada uma atrás da sua chave. Efeito no goldfish (N=10.000 pareado, sementes 3.000.000+i, 8 turnos), as três juntas: win até o T8 **+1,83 ±0,36pp**, comandante ≤T3 **+7,77 ±0,57pp** (85,0% → 92,8%), ≤T4 +1,05 ±0,21pp, Treasures criados +0,77, dano de combate proxy +3,01, drain +0,78, mortes de criatura **+1,05** por partida. **Atenção:** a base do simulador mudou. Os números absolutos das rodadas anteriores (Kingpin, Inevitable Defeat, Draconic Visitor etc.) são do simulador antigo; as comparações pareadas dentro de cada rodada continuam válidas, comparar números absolutos entre rodadas, não.

### O que mudou no código
1. **Treasure animado = criatura em todo sacrifício** (`ANIMATED_TREASURE_ROUTING_ENABLED`). Oráculo lido ao vivo: *At the beginning of combat on your turn, you may have Treasures you control become 3/3 Construct Assassin artifact creatures … until end of turn.* Rulings (2024-04-12): mantêm as habilidades. **CR 611.2c:** o conjunto afetado é fixado quando o efeito começa, então só os Treasures que já existiam no início do combate viram criatura. Até aqui só o Ashnod's Altar tratava o animado como criatura; agora **todo** sacrifício depois da animação conta (mana de Treasure na 2ª main phase, Deadly Dispute, Magda, Jan Jansen, Professional Face-Breaker, Lich-Knights' Conquest, Krark-Clan Ironworks, Altar), disparando Zulaport, Pitiless Plunderer, Sephiroth, Agent of the Iron Throne, e o Mahadi no end step.
   Dois erros do código antigo, no mesmo ponto: (a) o **Krark-Clan Ironworks** tratava o animado como "não criatura fora do combate", o que o oráculo do Vihaan nega; (b) o **Ashnod's Altar** ("Sacrifice a **creature**") recebia **todos** os Treasures, inclusive os criados depois da animação, que não são criatura. Agora o Altar só aceita os animados vivos (o mana bonus cai −0,34 por partida: era mana que o oráculo não permite).
2. **Mulligan com escolha** (`MULLIGAN_SMART_BOTTOM_ENABLED`). O London Mulligan do Vihaan **sorteava** as cartas do fundo (`rng.shuffle(hand)`), devolvendo com a mesma chance o Sol Ring e um terreno sobrando. Agora: só devolve terreno quando sobram mais de 4 (primeiro o que entra tapped); fora isso, a carta não-terreno de maior custo, protegendo Sol Ring, Arcane Signet, Smothering Tithe e Big Score.
3. **Terreno tapped em T1/T2** (`TAPPED_LAND_FIRST_ENABLED`). Antes jogava o **primeiro terreno da mão**. Agora, em T1/T2, joga o que entra tapped (Bojuka Bog, Path of Ancestry, checkland sem o básico, fastland depois do T3) **salvo** se isso custar uma jogada de desenvolvimento (Sol Ring, Arcane Signet, 2-drop); só permanentes contam (Path to Exile/Requisition Raid/Shoot the Sheriff sem alvo no goldfish não seguram o terreno). Mesma regra do Megatron.

### Medição (apoio; N=10.000 sementes 3.000.000+i pareadas; base = simulador antes, commit 6e623d3)
Base: win ≤T8 8,8% · revel ≤T8 0,46% · cmd ≤T3 85,0% · ≤T4 95,3% · Treasures criados 9,71 · dano mesa 13,85 · combate 47,43 · drain 6,23 · mortes de criatura 2,13 · mana bonus 2,28. Diferença pareada (variante − base), IC95%:

| variante | win ≤8 (pp) | cmd ≤T3 (pp) | cmd ≤T4 (pp) | Treasures | combate | drain | mortes de criatura | mana bonus |
|---|---|---|---|---|---|---|---|---|
| só Treasure animado | +0,81 ±0,24 | 0 | 0 | +0,42 ±0,17 | +0,71 ±0,22 | +0,42 ±0,08 | **+0,91 ±0,06** | −0,34 ±0,09 |
| só mulligan com escolha | +0,25 ±0,19 | +1,40 ±0,31 | +1,00 ±0,20 | +0,10 ±0,05 | +0,64 ±0,19 | +0,05 ±0,05 | +0,04 ±0,02 | +0,04 ±0,04 |
| só terreno tapped T1/T2 | +0,72 ±0,20 | **+6,39 ±0,52** | +0,03 ±0,05 | +0,23 ±0,05 | +1,50 ±0,21 | +0,28 ±0,09 | +0,07 ±0,02 | +0,11 ±0,04 |
| **as três (o que ficou)** | **+1,83 ±0,36** | **+7,77 ±0,57** | **+1,05 ±0,21** | **+0,77 ±0,18** | **+3,01 ±0,36** | **+0,78 ±0,13** | **+1,05 ±0,07** | −0,21 ±0,10 |
| sensibilidade: tapped cego (sempre o tapped) | +0,53 ±0,22 | +7,67 ±0,52 | +0,03 ±0,05 | +0,19 ±0,06 | +1,11 ±0,21 | +0,22 ±0,08 | +0,06 ±0,03 | +0,08 ±0,04 |
| sensibilidade: tapped até o T4 (+as outras 2) | +2,08 ±0,38 | +8,76 ±0,57 | +1,05 ±0,21 | +0,83 ±0,18 | +3,34 ±0,38 | +0,81 ±0,12 | +1,07 ±0,07 | −0,17 ±0,10 |

**Leitura (medido):** (a) Treasures animados sacrificados **como criatura** por partida: **0,56** (só Altar, antes) → **1,53** (as três). É o que move as mortes de criatura (+1,05), o drain (+0,78) e, pelo Pitiless Plunderer e pelo Mahadi, os Treasures criados (+0,77). (b) O terreno tapped move o **T3** (+6,39pp), com mana +0,08 no T3: o T4 já estava saturado (95,3%). (c) O mulligan com escolha rende +1,40pp no T3. (d) A política cega ganha um pouco mais no T3 (+7,67 contra +6,39pp) mas tem mana no T2 **−0,02** (perde Sol Ring/Arcane Signet); o teste de jogada perdida é o que um jogador faria. O modo resiliência (2.000) e o lote de 2.000 mostram a mesma direção (`resumos/ab_2000.txt`, `resumos/ab_2000_resiliencia.txt`): win +1,50pp e +0,60pp.

### Validação (Regra #1) — arquivada em `resultados-ab/2026-10-03-treasure-animado-e-mulligan/`
- **Smoke:** 99 cartas, 93 distintas, 0 desconhecidas, 0 duplicadas não básicas, 35 terrenos.
- **Bit-identidade com as 3 chaves desligadas:** 20.000/20.000 partidas idênticas ao commit 6e623d3 no modo padrão e 20.000/20.000 na resiliência.
- **Regressão:** 160.000 partidas (8 configurações/modos × 20.000), **0 exceções**, 0 cartas duplicadas, 0 partidas com "Treasures animados vivos" ≠ 0 ao fim do turno, 0 com Treasures < 0.
- **Testes dirigidos:** 42/42, incluindo `play_turn` completo (Vihaan + Krark-Clan Ironworks + Zulaport + Mahadi: os animados morrem como criatura e o Mahadi cria os Treasures no end step; a animação acontece no combate e zera no fim do turno: Regra #6) e a invariante em 2.000 partidas reais "criaturas sacrificadas = mín(n, animados vivos)" em toda chamada.

### Achados laterais (não corrigidos, Regra #1)
- **Sephiroth:** "sacrifique qualquer número de outras criaturas ao atacar" aceita os Treasures animados (são criaturas nesse momento); o simulador só oferece fichas e Constructs como combustível. Política, não oráculo; não modelado nem medido.
- **Xorn / Pitiless Plunderer:** o simulador cria os Treasures em **lote** por evento (`create_treasures(n)`); o Xorn soma +1 por lote, não por criatura que morre (cada morte é um gatilho separado). Pré-existente; não alterado.
- **Mulligan com sorteio das cartas do fundo** em outros 7 decks: Hei Bai, Maralen, Nekusar, Rat King, Toph, Ulalek, Ur-Dragon (varredura por grep de `rng.shuffle(hand)` + `bottom = hand[:penalty]`). Nenhum foi alterado.

### O que NÃO foi verificado (Regra #7)
Só as classes sacrifício/morte de Treasure e "criatura que morre" (`on_permanent_sacrificed`), ordem de fases, mulligan e jogada de terreno foram varridas neste arquivo; não houve auditoria carta a carta do `.py` inteiro. A política "Treasure animado primeiro" e "tapped sempre que não custar jogada" em T3+ (além da sensibilidade até T4) não foram medidas como alternativas.

---

## Kingpin, Wilson Fisk — avaliação como possível inclusão — 2026-10-03

**Pedido:** *"E a inclusão de Kingpin, Wilson Fisk no Vihaan?"* (com foto da carta).
Regras #3/#4/#5 e adendo de 2026-09-28: oráculo e rulings ao vivo (a foto só confirma que a carta existe) → docs do deck → Commander Spellbook antes/depois com controle positivo → enumeração por script → simulador só como apoio. Nenhuma carta foi cortada ou adicionada à lista.

**Oráculo (Scryfall ao vivo, 2026-10-03; salvo no cache):** {3}{B}, Legendary Creature — Human Villain 3/6 (Marvel Super Heroes Commander, 2026-06-26; legal, não é Game Changer, ~US$0,67). *Menace. Whenever you sacrifice Kingpin or another creature, create two Treasure tokens. This ability triggers only once each turn.* **Rulings: nenhum.**
**Rulings que decidem a leitura (Vihaan, 2024-04-12):** os Treasures animados "mantêm as habilidades" enquanto são criaturas; "outlaw" é Assassin/Mercenary/Pirate/Rogue/Warlock. Kingpin é Human Villain: **não é outlaw** (sem vigilância/haste do Vihaan, ataca só no turno seguinte).

### O que a carta toca nos motores reais do Vihaan (`resumos/enumeracao.txt`, varredura por script sobre o oráculo ao vivo)

- **O gatilho exige sacrificar uma CRIATURA, e o Vihaan transforma os próprios Treasures em criaturas.** No início do combate, "Treasures you control become 3/3 Construct Assassin artifact creatures until end of turn". A partir daí qualquer Treasure sacrificado, **por 1 de mana no 2º main, pelo Krark-Clan Ironworks, pelo Ashnod's Altar ou pela Magda**, é uma criatura sacrificada e dispara o Kingpin: **+2 Treasures por turno com 1 Treasure gasto** (+3 com Xorn, +4 com Anointed Procession, +6 com os dois; com Academy Manufactor vêm 2 Clues e 2 Foods juntos).
- **Saídas de sacrifício de criatura na lista (8):** Ashnod's Altar, Deadly Dispute, High Market, Jan Jansen, Krark-Clan Ironworks, Lich-Knights' Conquest (fichas), Phyrexian Tower, Sephiroth. Fora do turno de animação o Kingpin depende delas (ou das fichas que a lista já sacrifica: Constructs do Jan Jansen, ficha da Urabrask's Forge no end step).
- **Limite:** 1 vez por turno; 2 Treasures por disparo, não por criatura. Por isso **empilha, não compete**, com o grupo "criatura morre → Treasure" já na lista: Pitiless Plunderer (+1 por criatura que morre, sem limite), Mahadi (no end step, 1 por criatura morta no turno), Life Insurance (criatura não-ficha que morre) e Revel in Riches (criatura de oponente). Com ≥3 Treasures animados sacrificados no mesmo turno Plunderer + Mahadi já dão mais que o Kingpin; o Kingpin vale quando se sacrifica **um** Treasure só.
- **Gatilhos de ficha que cada disparo aciona:** Mirkwood Bats (criar/sacrificar ficha), Kambal (fichas entrando), Caretaker's Talent (compra 1ª vez no turno), Nadier's Nightblade (ficha saindo). Gatilhos de morte/sacrifício que o Treasure animado sacrificado também aciona: Zulaport, Pitiless Plunderer, Dictate of Erebos, Sephiroth e Captain Lannery Storm (reage a sacrificar Treasure); Life Insurance não conta (só criatura não-ficha).
- **Cor:** o simulador do Vihaan não modela cor; o {B} (cor primária do deck) foi medido à parte: P(≥4 de mana e fonte de B, contando Treasure) por T3/T4/T5/T8 = 16% / 77% / 90% / 97% (`resumos/castabilidade_b_kingpin.txt`; só 2,6% das partidas nunca chegam lá em 8 turnos).
- **Combos (Commander Spellbook, antes e depois de cada troca):** base = 4 combos (Ashnod's Altar + Mahadi + Revel in Riches; Anointed Procession/Goldspan Dragon/Xorn + Gleaming Splendor + Smothering Tithe). **Kingpin sem cortar: 0 combos novos e 0 "quase" novos** (em 29 trocas testadas). Controles positivos ok: cortar Smothering Tithe ou Gleaming Splendor remove 3 combos; cortar Mahadi ou Ashnod's Altar remove 1. **Pitiless Plunderer** (34) e **Ashnod's Altar** (32) são as duas cartas com mais "quase combos" da lista; o limite de 1×/turno do Kingpin impede um loop de Treasure por conta própria.

### Medição no simulador (apoio; N=6.000 sementes 3.000.000+i pareadas, troca posicional; harness sem alterar `vihaan_goldfish_v1.py`)

**Como foi modelado:** o gatilho do Kingpin é ligado em `on_permanent_sacrificed(is_creature=True)`, o ponto central pelo qual o simulador roteia todo sacrifício, e cria 2 Treasures por `create_treasures` (Xorn, Procession e Academy Manufactor valem como para qualquer criação). Três políticas: **`sim`** só o que o simulador já roteia como sacrifício de criatura; **`anim`** + sacrificar um Treasure ANIMADO por qualquer via conta como criatura sacrificada (mana no 2º main, Krark-Clan Ironworks, Magda), só para o Kingpin, mantendo a base intacta (ver achado lateral); **`delib`** + linha deliberada: no end step, se o Kingpin ainda não disparou e há Treasure animado, sacrifica UM por nada para disparar (−1 Treasure, +2). O simulador não escolhe essa linha sozinho.
**Base (8 turnos):** `win_turn` ≤T8 9,0%, Revel in Riches ≤T8 0,48%, comandante ≤T3 85,0%, Treasures criados 9,66. **(12 turnos):** `win_turn` ≤T12 78,1%, Revel ≤T12 7,95%, Treasures criados 50,9. (`win_turn` = 1º turno com dano de mesa+combate proxy ≥120, Revel in Riches ou combo.)
O Kingpin é conjurado em **15,5% das partidas até T8 (26,7% até T12), em média no T6**; por partida conjurada dispara 0,7/1,0/1,5 vez em 8 turnos e 2,1/2,5/3,2 em 12 (`sim`/`anim`/`delib`) e cria 1,5–1,9 / 2,1–2,5 / 3,2–3,8 Treasures (8 turnos) e 5,4–6,0 / 6,6–7,0 / 8,3–8,8 (12 turnos).

**Contra uma carta morta, no mesmo slot e nas mesmas sementes** (a Blank Card inconjurável entra NA MESMA POSIÇÃO: contrafactual exato; o simulador premia não gastar mana, então comparar com a base misturaria os dois efeitos). Diferença Kingpin − Blank, IC95%:

| slot | política | win ≤T8 (pp) | win ≤T12 (pp) | Revel ≤T12 (pp) |
|---|---|---|---|---|
| Academy Manufactor | sim / anim / delib | −0,02 / +0,17 / +0,30 (±0,24) | +0,80 / +0,87 / +1,27 (±0,4) | +0,33 / +0,38 / +0,47 (±0,3) |
| Monologue Tax | sim / anim / delib | −0,15 / +0,03 / +0,25 (±0,25) | +0,67 / +0,67 / +0,92 (±0,4) | +0,30 / +0,47 / +0,57 (±0,34) |
| Back in Town | sim / anim / delib | −0,33 / −0,13 / +0,07 (±0,23) | +0,82 / +0,82 / +1,08 (±0,4) | +0,55 / +0,57 / +0,55 (±0,35) |

**Leitura:** (a) **em 8 turnos o Kingpin não se distingue de uma carta morta** (−0,3 a +0,3pp); (b) **em 12 turnos ganha de uma carta morta: +0,7 a +0,9pp de win (`sim`/`anim`) e +0,9 a +1,3pp (`delib`), e +0,3 a +0,6pp de Revel in Riches** (base 7,95%): efeito pequeno, mas com IC acima de zero nas 9 células de win ≤T12 e em 8 das 9 de Revel ≤T12; (c) **nas partidas em que ele foi conjurado** (n ≈ 920–930, `resumos/condicional_kingpin_vs_blank.txt`, 8 turnos) ele cria **+0,6 a +0,9 (sim), +1,4 a +1,6 (anim) e +2,6 a +3,0 (delib) Treasures a mais que a Blank**, e termina com +0,3 a +0,5 / +0,6 a +0,7 / +1,0 a +1,2 Treasures a mais em campo, sem ganho de win em 8 turnos (±1,5pp com esse n); (d) **dano de mesa e de combate** nessas partidas sobem na linha `delib` (+0,4 a +1,2 e +3,5 a +4,5), dentro de IC largo.
**Custo de cortar outras cartas (referência, `delib`, 8 turnos, win ≤T8, Kingpin − base):** Sol Ring −2,8 ±0,5; Mirkwood Bats −1,7 ±0,4; Orochi Soul-Reaver −1,0 ±0,3; Anointed Procession −0,9 ±0,25; Lotho −0,8 ±0,3; Agent of the Iron Throne −0,5 ±0,3; Xorn −0,45 ±0,3; Nadier's Nightblade −0,35 ±0,3 (os controles Sol Ring e Arcane Signet doem; no 12 turnos Sol Ring −1,0 e Orochi −2,0). As demais 56 linhas estão em `resumos/ab_kingpin_6000_{sim,anim,delib}.txt` e as de 12 turnos em `resumos/ab_kingpin_6000_t12_*_slots.txt`.

### O que a medição NÃO diz (Regra #5)
- **As cartas "baratas de cortar" no simulador são, em grande parte, valor dependente de oponente que o goldfish não vê** (Monologue Tax, Teferi's Protection, Back in Town, Academy Manufactor, Smothering Tithe com 3 combos): custo ~0 no simulador **não** é argumento para cortá-las. A tabela mostra o efeito do Kingpin contra uma carta morta, **não** qual carta deve sair; essa escolha é sua.
- **Blasphemous Act:** nas tabelas de 12 turnos, trocá-la dá +4,2 a +4,5pp de win; isso é o simulador conjurando um wipe contra o próprio campo, não um dado sobre o deck.
- **Oponente real** (remoção do Kingpin, do Vihaan ou dos Treasures animados, bloqueio, contramágica), a linha `delib` em jogo real e o Kingpin como corpo 3/6 menace que bloqueia: 📊 estruturais ou não medidos.

### Achado lateral do simulador (não corrigido nesta rodada, Regra #1)
- **[Corrigido ainda em 2026-10-03, depois desta rodada: ver a seção "Correção do simulador: Treasure animado, mulligan e terreno tapped" no topo deste arquivo.]** **Treasure ANIMADO sacrificado é tratado como não-criatura em dois caminhos para TODOS os gatilhos de criatura:** (a) `spend_mana` (mana do 2º main) chama `sacrifice_treasures(for_mana=True)` com `as_creature=False`; (b) `aggressive_treasure_destruction` só passa `as_creature=True` com o Ashnod's Altar, e cai no Krark-Clan Ironworks com `as_creature=False` ("não é criatura fora do combate"), embora os Treasures sigam sendo criaturas até o fim do turno (oráculo do Vihaan). Zulaport Cutthroat, Nadier's Nightblade, Pitiless Plunderer, Sephiroth, Dictate of Erebos e a Mahadi (end step) **subestimam** esses eventos. Aqui só o Kingpin os enxerga (política `anim`/`delib`), para a base ficar idêntica ao simulador original; corrigir para todos moveria a base do deck.

**Escopo verificado nesta rodada:** oráculo + rulings (Kingpin: nenhum; Vihaan, Xorn, Academy Manufactor, Anointed Procession, Dictate of Erebos, Mirkwood Bats, Goldspan Dragon, Ashnod's Altar, Sephiroth lidos e salvos); leitura de `on_permanent_sacrificed`, `sacrifice_*`, `spend_mana`, `aggressive_treasure_destruction`, `combat_step`, `end_step` e `play_turn` (ordem de fases: animação no início do combate, 2º main depois do combate, end step por último); enumeração por script das 94 entradas distintas de `lista.md`; Spellbook antes/depois em 29 trocas (25 candidatas + 4 controles positivos); A/B pareado do Kingpin contra TODAS as 64 cartas não-terreno em 3 políticas (8 turnos) e contra 14 delas em 12 turnos; Kingpin − Blank no mesmo slot (8 e 12 turnos); condicional nas partidas com Kingpin conjurado; bit-identidade do harness contra o simulador original sem patch (300/300 em 101 campos, nas 3 políticas); 11/11 tabelas refeitas dos `.json.xz` byte a byte.
**Não verificado:** oponente real; a linha deliberada `delib` na mesa; efeito do Kingpin como bloqueador; o simulador mede dano contra um alvo-proxy de 120 (3 oponentes × 40), não vida real; qualquer classe da taxonomia da Regra #1 no `.py` além do roteamento de sacrifício e das fases (a carta não está na lista).

---

## Inevitable Defeat — avaliação como possível inclusão — 2026-10-03

**Pedido:** *"Faça o mesmo para Inevitable Defeat como possível inclusão nos meus dois decks Mardu: Megatron e Vihaan."* (a parte do Megatron está em `megatron-tyrant-mardu/goldfish-log.md`).
Regras #3/#4/#5 e adendo de 2026-09-28: oráculo e ruling ao vivo → docs do deck (`auditoria.md`, `checklist-oraculo.md`, `goldfish-log.md`) → Commander Spellbook antes/depois com controle positivo → enumeração por script → simulador só como apoio.

**Oráculo (Scryfall ao vivo, 2026-10-03; salvo no cache):** {1}{R}{W}{B}, Instant (Tarkir: Dragonstorm, 2025-04-11, legal, não é Game Changer, ~US$0,77). *This spell can't be countered. Exile target nonland permanent. Its controller loses 3 life and you gain 3 life.* **Ruling (2025-04-04):** alvo ilegal na resolução ⇒ nada acontece, ninguém ganha nem perde vida.

### O que a carta toca nos motores reais do Vihaan (`auditoria.md` §3–§6 + `resumos/enumeracao.txt`)

- **Motor central = Treasures (30 fontes) + multiplicadores (Xorn, Academy Manufactor, Anointed Procession) + vitória por Revel in Riches.** A Defeat **não cria Treasure**, não é token, não é artefato, não morre/entra: nenhum multiplicador nem sac outlet a vê. Contraste com as respostas do deck que **alimentam** o motor: **Deadly Derision** (instant: destrói criatura/PW e cria Treasure) e **Blood Money** (wipe em sorcery: cria Treasure por criatura não-token destruída).
- **Crime (único payoff do deck: Magda, the Hoardmaster, "whenever you commit a crime, create a tapped Treasure", 1×/turno):** a Defeat mira um permanente de oponente, então comete crime. Mas já cometem crime, por exemplo, Path to Exile, Shoot the Sheriff, Deadly Derision, Boros Charm, Requisition Raid, Bojuka Bog e o upkeep do Laughing Jasper Flint (miram oponente/permanente/cemitério dele); a Defeat só soma um Treasure da Magda se for o único crime do turno. No simulador a Magda estava em campo em **13% das conjuradas**.
- **Ganho de vida:** payoffs de "você ganhou vida" = **Witch of the Moors** (1 carta; no end step, se você ganhou vida, o oponente sacrifica criatura e você devolve criatura do cemitério). Os 3 de vida da Defeat ligam a Witch **por demanda**, desde que resolvam no meu turno (a condição é "ganhou vida neste turno" no meu end step), mas ela estava em campo em só **~1% das conjuradas**. Outras fontes de ganho (Zulaport, Nadier's, Life Insurance, Sephiroth) disparam por criatura/token que sai de campo, nada a ver com a Defeat.
- **Cobertura de interação (oráculo):** Path/Shoot the Sheriff/Deadly Derision pegam criatura (Derision também PW); Boros Charm 4 de dano a jogador/PW; **Council's Judgment** (sorcery, exila qualquer permanente não-terreno por voto, sem alvo) e **Requisition Raid** (sorcery, artefato e/ou encantamento) são as únicas respostas a encantamento/artefato, **nenhuma em instant**. A Defeat seria a primeira resposta em instant a qualquer permanente não-terreno, sem alvo-restrição de tipo, sem contramágica.
- **Cor:** R+W+B = identidade do comandante. O simulador do Vihaan **não modela cor** (só mana total); medi à parte, lendo o estado dos mesmos jogos: P(R+W+B e ≥4 de mana) por T4/T5/T6/T8 = **62–71% / 81–84% / 89–90% / 96%** (leitura pessimista–otimista; Treasure conta como fonte de qualquer cor; o simulador joga terrenos na ordem da mão sem sequenciar por cor, então a leitura pessimista é piso). Aplicando essa porta de cor, a taxa de conjuração cai ≤0,2pp.
- **Combos (Commander Spellbook, antes e depois):** base = 4 combos (Ashnod's Altar + Mahadi + Revel in Riches; Anointed Procession/Goldspan Dragon/Xorn + Gleaming Splendor + Smothering Tithe). Defeat sem cortar: **0 combos novos, 0 "quase" novos**. Controles positivos ok: cortar Smothering Tithe ou Gleaming Splendor remove 3 combos. **Nenhuma das 13 candidatas testadas pertence a combo** (Academy Manufactor, Blasphemous Act e Teferi's Protection pertencem a "quase combos": 4, 4 e 6).

### Medição no simulador (apoio; N=10.000 sementes 3.000.000+i pareadas, 8 turnos, troca posicional, com a porta de cor pessimista)

Defeat conjurada em ~10,7% das partidas até T8 (o simulador encerra a partida quando a condição do Revel in Riches é cumprida). Base: `win_turn` ≤T8 8,8%, comandante ≤T3 85,0%, dano de mesa 13,85. `win_turn` = 1º turno com dano ≥120, Revel in Riches ou combo; o dreno de 3 da Defeat soma ao dano de mesa.

| Defeat entra no lugar de | win ≤T8 (pp) | cmd ≤T3 (pp) | dano de mesa | Treasures | conjurada |
|---|---|---|---|---|---|
| Monologue Tax | +0,16 ±0,12 | +0,00 ±0,00 | +0,48 ±0,08 | +0,04 ±0,02 | 10,5% |
| Academy Manufactor | +0,41 ±0,16 | +0,00 ±0,00 | +0,73 ±0,10 | +0,19 ±0,03 | 11,1% |
| Back in Town | +0,13 ±0,14 | +0,01 ±0,02 | +0,49 ±0,08 | +0,05 ±0,02 | 11,0% |
| Teferi's Protection | +0,20 ±0,15 | +0,00 ±0,00 | +0,42 ±0,13 | +0,01 ±0,04 | 10,4% |
| Smothering Tithe | +0,17 ±0,12 | +0,07 ±0,21 | +0,42 ±0,08 | +0,04 ±0,03 | 10,7% |
| Council's Judgment | +0,23 ±0,14 | +0,00 ±0,00 | +0,50 ±0,13 | +0,02 ±0,02 | 11,0% |
| Shoot the Sheriff | +0,14 ±0,16 | +0,04 ±0,04 | +0,32 ±0,09 | −0,00 ±0,02 | 10,2% |
| Boros Charm | +0,17 ±0,14 | +0,04 ±0,04 | +0,43 ±0,11 | +0,03 ±0,03 | 10,8% |
| Path to Exile | +0,13 ±0,15 | +0,08 ±0,06 | +0,28 ±0,07 | −0,00 ±0,02 | 10,7% |
| Deadly Derision | −0,21 ±0,13 | +0,00 ±0,00 | +0,13 ±0,10 | −0,16 ±0,02 | 11,1% |
| Requisition Raid | −0,03 ±0,16 | +0,08 ±0,06 | +0,40 ±0,10 | −0,01 ±0,03 | 11,0% |
| Blasphemous Act | +0,39 ±0,16 | +0,00 ±0,00 | +0,36 ±0,25 | +0,09 ±0,03 | 10,2% |
| Life Insurance | +0,28 ±0,15 | +0,00 ±0,00 | +0,05 ±0,10 | +0,07 ±0,03 | 10,9% |
| Mari, the Killing Quill | −0,02 ±0,13 | +0,01 ±0,02 | +0,45 ±0,08 | +0,01 ±0,02 | 10,8% |
| The Reaver Cleaver | −0,14 ±0,19 | +0,00 ±0,00 | −0,00 ±0,13 | −0,45 ±0,06 | 10,4% |
| Laughing Jasper Flint | −0,45 ±0,18 | +0,00 ±0,00 | −0,10 ±0,22 | −0,10 ±0,06 | 11,2% |
| Urabrask's Forge | −0,41 ±0,16 | +0,00 ±0,00 | −0,35 ±0,15 | −0,03 ±0,03 | 10,7% |
| Lotho, Corrupt Shirriff | −1,42 ±0,25 | +0,14 ±0,07 | −0,33 ±0,13 | −0,44 ±0,05 | 10,4% |
| Orochi Soul-Reaver | −1,46 ±0,25 | +0,00 ±0,00 | −0,72 ±0,14 | −0,59 ±0,05 | 10,9% |
| **controle** Arcane Signet | −0,42 ±0,22 | −0,66 ±0,24 | −0,13 ±0,15 | −0,13 ±0,05 | 10,1% |
| **controle** Sol Ring | −3,13 ±0,37 | −1,98 ±0,28 | −1,87 ±0,30 | −0,71 ±0,08 | 9,7% |

**Smothering Tithe aparece na tabela só como leitura do simulador:** cortá-la remove 3 combos no Spellbook (com Gleaming Splendor + Anointed Procession/Goldspan Dragon/Xorn), então não é candidata real. Os controles doem (Sol Ring −3,1pp; Arcane Signet atrasa o comandante −0,7pp). Entre as candidatas há dois grupos: trocas dentro do ruído (+0,1 a +0,4pp; o sinal positivo de Monologue Tax/Academy/Back in Town/Blasphemous Act vem **do simulador premiar não gastar mana**: a Blank Card inconjurável no mesmo slot dá +0,52 / +0,59 / +0,52pp, mais que a Defeat) e trocas que custam (Lotho e Orochi Soul-Reaver, −1,4pp: são geradores de Treasure). **O dreno da própria Defeat explica ~0,32 do dano de mesa (3 × 10,7% por partida);** o resto do +0,3 a +0,7 é o mesmo efeito de "slot livre" que a Blank Card mostra (+0,32 a +0,54). A recursão da Witch não se moveu (±0,004).

### O que a medição NÃO diz (Regra #5)
- **Várias das cartas "baratas de cortar" no simulador são geradoras de valor dependente de oponente**, que o goldfish não vê: Monologue Tax e Gleaming Splendor (Treasure por spell/compra de oponente), Teferi's Protection (proteção), Academy Manufactor/Back in Town (motor/recursão), Smothering Tithe (3 combos no Spellbook). Custo ~0 no simulador **não** é razão para cortá-las (Regra #5). O que o simulador mostra com segurança é só o contrário: cortar Lotho, Orochi Soul-Reaver ou o Sol Ring dói.
- Exílio, contramágica, alvo ilegal (ruling), a Defeat como resposta a encantamento/artefato/PW em instant: 📊 estruturais (sem permanente de oponente no goldfish).
- O primeiro lote usou a "Blank Card" como artefato; nesta rodada isso não mudou nenhum número do Vihaan (idêntico nos dois lotes), mas o lote anterior está em `superado-blank-artefato/` para auditoria.

**Escopo verificado nesta rodada:** oráculo + ruling; `auditoria.md`, `checklist-oraculo.md` e `goldfish-log.md` do deck lidos para motores/combos; enumeração por script sobre as 95 entradas distintas de `lista.md` (crime, alvo de oponente, ganho de vida, perda de vida, exile, gatilho de spell); Spellbook antes/depois em 13 trocas candidatas + 2 controles positivos; castabilidade de cor (2 leituras); A/B pareado de 19 trocas + 2 controles + 3 "Blank" em 3 modos de porta de cor (off/pessimista/otimista, equivalentes em ≤0,2pp de conjuração); bit-identidade do harness contra o simulador original sem patch (300/300 em 101 campos do `GameState`, nos 3 modos); tabelas refeitas dos `.json.xz` byte a byte.
**Não verificado:** comportamento contra oponentes reais; linha deliberada "Defeat em instant no turno do oponente" (Magda daria um 2º Treasure no turno do oponente: o simulador só conjura no meu turno, e a Regra #7.4 manda checar proxy fora do turno: aqui o proxy é **piso**); sequenciamento de terrenos por cor; qualquer classe da taxonomia da Regra #1 no `.py` (a carta não está na lista).

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Draconic Visitor — avaliação como inclusão (vs. Ur-Dragon) + Kambal + Reaver Cleaver — 2026-09-25

**Pedido:** *"A carta Draconic Visitor, avalie ela como possível inclusao
tanto no Ur-Dragon, quanto no Vihan, e me diga aonde ela seria melhor e
pq, ou se não vale incluir em nenhum dos 2!"* Implementação e cláusulas em
`checklist-oraculo.md`.

### Antes/depois das correções (2.000 seeds, 6.000.000+, 8 turnos, mesma seed)

| Métrica | Antes | + Kambal | + Reaver Cleaver |
|---|---|---|---|
| Drain médio (padrão) | 5,77 | 6,13 | 6,34 |
| Drain médio (resiliência) | 2,98 | 3,14 | 3,25 |
| Treasures criados (padrão) | 9,43 | 9,43 | 9,86 |
| Revel in Riches condição (padrão) | 0,30% | 0,30% | 0,60% |
| Vida final (padrão) | 38,03 | 38,39 | 38,42 |
| `win_turn` ≤ T8 (padrão, métrica nova) | — | 9,40% | 10,00% |
| `win_turn` ≤ T8 (resiliência) | — | 2,45% | 2,55% |

Tudo o mais ficou bit-idêntico no passo do Kambal (turno do comandante,
Treasures, mortes, compras). A métrica de combate e o `win_turn` são só
leitura. The Reaver Cleaver fica equipada em 7,6% das partidas e cria 0,51
Treasure por partida em média.

### A/B pareado — Visitor no lugar de 6 candidatas + controle (N=5.000, troca posicional)

Diferença pareada (Visitor − base) com IC95%. Controle: Arcane Signet (ramp
de 2; cortá-lo deve atrasar o comandante, e atrasa).

**Padrão** (base: win ≤T8 8,8%, Treasures 9,77, dano de mesa 13,94, combate 46,77)

| Sai | win_turn | win ≤T8 | combo | turno cmd | Treasures | dano mesa | combate |
|---|---|---|---|---|---|---|---|
| Mari, the Killing Quill | −0,003 ±0,003 | +0,2pp ±0,3 | +0,3pp ±0,1 | 0,000 | −0,39 ±0,13 | −0,31 ±0,52 | −0,51 ±0,64 |
| The Reaver Cleaver | −0,002 ±0,003 | +0,2pp ±0,3 | +0,1pp ±0,1 | 0,000 | −0,85 ±0,12 | −0,67 ±0,26 | +1,37 ±0,27 |
| Urabrask's Forge | −0,001 ±0,003 | +0,1pp ±0,3 | +0,1pp ±0,1 | 0,000 | −0,37 ±0,07 | −0,58 ±0,33 | +0,24 ±0,46 |
| Lotho, Corrupt Shirriff | +0,016 ±0,004 | −1,4pp ±0,4 | +0,1pp ±0,1 | −0,002 | −0,83 ±0,15 | −1,04 ±0,77 | −2,60 ±0,72 |
| Laughing Jasper Flint | +0,001 ±0,003 | −0,1pp ±0,3 | +0,2pp ±0,1 | 0,000 | −0,45 ±0,10 | −0,29 ±0,40 | −0,02 ±0,94 |
| Orochi Soul-Reaver | +0,021 ±0,005 | −1,8pp ±0,4 | +0,1pp ±0,1 | 0,000 | −0,95 ±0,11 | −1,10 ±0,40 | −2,96 ±0,34 |
| Arcane Signet (controle) | +0,003 ±0,004 | −0,3pp ±0,3 | +0,1pp ±0,1 | +0,027 ±0,008 | −0,53 ±0,15 | −0,84 ±0,64 | −0,59 ±0,66 |

**Resiliência** (base: win ≤T8 2,1%): Mari/Cleaver/Forge +0,1pp ±0,2;
Lotho −0,4pp ±0,2; Orochi −0,2pp ±0,2; Signet 0,0pp e turno do comandante
+0,025.

**Leitura do incondicional:** a Visitor só resolve em 8% das partidas até
o T8 (média no T7,2). O efeito médio fica diluído. Contra as 3 candidatas
fracas é neutro; contra Lotho e Orochi é pior.

### Condicional — só as partidas em que a Visitor resolveu

Mesmo slot (Mari), 10 turnos pra dar tempo de a carta agir (N=5.000):

| | Padrão (resolveu em 15,1%, T8,4) | Resiliência (6,4%, T8,6) |
|---|---|---|
| win ≤T10 | 60,3% → **+5,3pp ±2,7** | 22,4% → **+10,9pp ±4,1** |
| Treasures | 29,1 → −15,3 | 14,9 → −5,5 |
| Dano de mesa (drain) | 98,8 → −37,0 | 28,2 → −6,4 |
| Combate | 146,5 → +34,6 | 75,0 → +24,1 |
| Dragões criados | +16,7 | +7,1 |
| Combo (Plunderer + Altar) | +5,8pp | +1,2pp |

**Decomposição — o TEXTO da Visitor vale alguma coisa aqui?** Visitor ×
um 5/5 voador genérico de mesmo custo no mesmo slot (só no harness). Nas
partidas em que resolveu, até T10:
- padrão: win +7,4pp ±2,4;
- resiliência: +11,5pp ±3,7.

O texto troca −15 Treasures e −35 de drain por +33 de combate, e sai
positivo. Trocar cada Treasure (1 mana, 3/3 só no meu combate) por um 5/5
voador permanente acelera o relógio mais do que a perda de mana e de
drain custa, nesta janela.

### Combo novo — probabilidade (Regra 7)

Visitor + Pitiless Plunderer + Ashnod's Altar, com ≥1 dos 7 pagadores.
Hipergeométrica em 99 cartas, sem tutor:

| Cartas vistas | 3 peças | 3 peças + pagador |
|---|---|---|
| 15 (T8, sem compra extra) | 0,29% | 0,18% |
| 21 (T8, +6 extras) | 0,85% | 0,66% |
| 25 (T12, +6 extras) | 1,47% | 1,24% |

No simulador: 0,1–0,3% das partidas até o T8, e 0,9% até o T10. Combo de 3
peças sem tutor nenhum, abaixo de 1,5% até o T12. Isso é compatível com o
Bracket 3 (`commander-rules.md`: combos de 3 peças são aceitáveis).

### Conclusão pra este deck

Ver a comparação com o Ur-Dragon em `ur-dragon-wurbg/goldfish-log.md`
(mesma data). Aqui a Visitor é uma **troca de modo**:
- desliga o comandante (animar Treasures), a Revel in Riches e ~14 cartas
  que consomem Treasure;
- transforma as ~30 fontes de Treasure/Construct da lista em Dragões 5/5
  voadores, multiplicados por Anointed/Manufactor/Xorn;
- adiciona um infinito de 3 peças.

Quando resolve, o simulador mostra ganho real (+5 a +11pp de vitória até o
T10). O texto em si é positivo contra um 5/5 genérico. Corte sugerido:
**The Reaver Cleaver**, pelos motivos do deck:
- custa 6 mana no total pra fazer algo;
- disputa o mesmo papel de fim de jogo;
- com a Visitor em campo, o "that many Treasure" dela vira Dragão também,
  ou seja, faz a mesma coisa pior;
- no A/B é neutro (+0,2pp ±0,3).

Mari não é cortada com base no simulador porque o valor real dela é
📊 dependente de oponente. Ela dá deathtouch aos Treasures animados, que
são Construct *Assassin*, e o simulador não modela bloqueio. Pela Regra 5,
isso não é motivo pra corte. `lista.md` não muda até o usuário decidir.

---

## Porte completo do modo de resiliência + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** "Ainda bem que vimos isso antes de implementar o Vihaan,
que tb tem muito sacrifício de artefatos!" seguido de "Vamos fazer o
Vihaan agora." Detalhes completos em `checklist-oraculo.md` e
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Achado:** 1º deck desta sessão a nascer com CR 903.9a já correta
desde o início (`remove_permanent`, Mayhem Devil excluído via
`on_permanent_destroyed`). Mesmo assim, a regressão de 20k achou 2
bugs REAIS pré-existentes do próprio motor (não de CR 903.9a): `sacrifice_
named_creature` nunca tratava o comandante, e o fallback do Deadly
Dispute podia escolhê-lo sem preferência — 319/20000 seeds (1,6%) com
o comandante preso no cemitério antes do fix.

**Resultado:** modo padrão diverge em 3,3% das seeds (657/20000) após
o fix do Deadly Dispute — mudança real e intencional (RNG ripple
esperado). A/B (10k seeds): `treasures_created_total`/`creature_deaths_
total`/etc. dentro de margem pequena; "comandante nunca conjurado"
idêntico nos 2 lados (0,79%/0,79%).

**Validação:** regressão de 20.000 partidas nos 2 modos, 0 exceções, 0
comandantes presos no cemitério (era 319/20000 antes) + 7 testes
dirigidos.

---

### Auditoria oráculo-por-oráculo completa — 2026-09-14

Última das 16 decks desta campanha. Releitura clause-by-clause do oráculo
real (Scryfall, todas as 91 cartas) achou **16 gaps reais** — detalhe
completo em `checklist-oraculo.md`. Resumo dos principais:

- 9 tags `outlaw`/`haste` erradas (7 faltando, 2 sobrando) verificadas
  via `type_line` real, afetando Back in Town, Olivia, Laughing Jasper
  Flint.
- **2ª habilidade real do próprio Vihaan** ("Other outlaws you control
  have vigilance and haste") nunca propagada — outlaws sem haste impressa
  perdiam o ataque no turno em que entravam mesmo com o comandante em
  campo.
- **Laughing Jasper Flint** disparava na fase errada (end_step em vez de
  upkeep) — 0% de valor gerado desde sempre, mesma classe de bug já
  documentada pro Mahadi na criação do arquivo.
- **Urabrask's Forge** criava o token DEPOIS do snapshot de atacantes do
  combate — nunca contava como atacante no próprio combate, apesar de
  ter haste real.
- **Magda, the Hoardmaster** (Scorpion Dragon) e **Professional
  Face-Breaker** (2ª habilidade) — 100% ausentes, nunca implementadas.
- **Agent of the Iron Throne** só cobria metade artefato do "artifact OR
  CREATURE" real.
- **Extort** (Life Insurance) e **Flashback** (Sevinne's Reclamation) —
  habilidades reais 100% ausentes.
- **Back in Town** — MV errado no CARD_DB (6 em vez do real 3) + custo X
  nunca pago.
- **Lich-Knights' Conquest** — fodder ignorava Treasures/other_tokens (o
  maior reservatório do deck).
- **The Reaver Cleaver** — Equip {3} nunca pago, bônus de combate de
  graça.
- Aya of Alexandria / Grenzo, Havoc Raiser — gatilhos "por criatura"
  (sem "one or more" no oráculo) achatados pra 1 fixo.

**Validação:** smoke test (CARD_DB 94, BASE_LIBRARY 99, 0 desconhecidas,
0 duplicatas) + 38 testes unitários isolados (1 por correção) + regressão
de 20.000 partidas (seed 9500000+, turns=10, 0 exceções) + antes/depois
via `git stash` (2.000 jogos, seed 7500000, turns=8):

| Métrica | Antes | Depois |
|---|---|---|
| Avg Treasures em campo no fim | 2,60 | 2,06 |
| Avg Treasures sacrificados (total) | 4,83 | 5,37 |
| Avg outros tokens criados | 0,83 | 1,61 |
| Avg mortes de artefato | 5,05 | 5,57 |
| Avg drain/dano agregado (proxy) | 3,34 | 3,93 |
| Avg vida ganha | 1,09 | 1,33 |
| Avg combates com ≥1 atacante | 4,04 | 4,31 |
| RECURSION avg/jogo | 0,13 | 0,14 |
| Avg Scorpion Dragons da Magda (novo) | — | 0,09 |
| Avg impulsos Face-Breaker (novo) | — | 0,37 |
| Avg Extort pago (novo) | — | 0,17 |
| Avg flashbacks Sevinne's (novo) | — | 0,01 |

Todas as métricas se moveram na direção esperada (mais atacantes hasty
contando combates, mais sinks reais de Treasure drenando o pool mais
rápido, mais drain/vida via Extort+Agent of the Iron Throne+escala real
da Aya/Grenzo), nenhuma explodiu. `lista.md` não mudou — auditoria
implementation-only, nenhuma carta adicionada/removida.

---

### Auditoria linha-a-linha "compile TUDO" — 2026-09-01

**Gatilho:** pedido direto do usuário ("AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha") — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King, Thranduil, Ulalek e Ur-Dragon. Ver `checklist-oraculo.md`
pra detalhamento completo.

**Método:** detecção automatizada de tags órfãs (37 candidatas) + nomes
de carta com poucas ocorrências. A esmagadora maioria eram falsos
positivos (dispatch por nome dentro de funções centralizadas como
`on_permanent_sacrificed()`/`on_creature_dies()`/`on_token_leaves()` —
este arquivo já tem uma arquitetura de aristocratas bem centralizada).
**3 gaps reais confirmados:**

1. **High Market** (`sac_outlet_life`) e **Phyrexian Tower**
   (`sac_outlet_bb`) — 2 terrenos com habilidade real de sacrifício
   (`{T}, Sacrifice a creature: gain 1 life` / `Add {B}{B}`) nunca
   implementados. Corrigidos com `try_sac_land_outlets()`, chamado no
   início do `end_step()` — só sacrifica TOKENS descartáveis
   (Constructs/other_tokens), nunca uma criatura nomeada real (trocar um
   corpo de verdade por 1 vida ou 1 mana extra é claramente mau negócio).
   Reusa `sacrifice_constructs()`/`sacrifice_other_tokens()`, que já
   disparam todos os gatilhos reais de morte (Zulaport Cutthroat,
   Pitiless Plunderer, Mahadi, Sephiroth, Mayhem Devil) — sem duplicar
   lógica.
2. **Sentinel Sarah Lyons** (`anthem_artifact`) — 2 habilidades reais: o
   anthem "+2/+2 se um artefato entrou este turno" é genuinamente 📊
   (sem P/T por criatura neste modelo, consistente com o resto do
   arquivo), mas o **Battalion** ("ela e mais 2 criaturas atacam: dano =
   artefatos que você controla") era um gatilho real e quantificável
   (proxy de dano, mesma convenção do Smaug the Magnificent) nunca
   implementado. Corrigido em `combat_step()`, com novo helper
   `artifacts_in_play()` (conta permanentes nomeados + Treasures +
   Constructs).

**Reclassificação verificada, não alterada:** o próprio docstring do
cabeçalho já documentava, de forma transparente, que Grenzo/Laughing
Jasper Flint "exilam da biblioteca do OPONENTE" na regra real, mas usam a
PRÓPRIA biblioteca como fonte substituta aproximada — uma decisão
deliberada e já documentada (não uma omissão silenciosa disfarçada). Não
alterado nesta rodada por ser uma escolha de design já revisada, não um
gap novo encontrado.

**Validação:** 9 testes unitários isolados (todos passando) + regressão
de 20.000 partidas (seed 8000000+, turns=10, 0 exceções) + `run_batch`
antes/depois via `importlib` (3000 jogos, seed 9000000, turns=10):

| Métrica | Antes | Depois |
|---|---|---|
| Drain/dano agregado (proxy) | 9.91 | 11.74 |
| Vida ganha | 2.78 | 3.32 |
| Mana bônus via sac outlets pós-combate | 5.71 | 6.10 |
| Revel in Riches (10+ Treasures) | 3.0% | 3.1% |

Todas as métricas relevantes subiram na direção esperada, sem nenhuma
outra métrica se mover de forma inexplicável. `vihaan_v1_runs.jsonl`
regenerado (3000 jogos, seed_base=6000000, turns=8, mesmos parâmetros já
estabelecidos no `__main__` do arquivo).

---

## Simulação #1 — goldfish Python completo (`vihaan_goldfish_v1.py`) — 2026-08-22

**Contexto:** o usuário trouxe um script pronto gerado por ChatGPT pra essa mesma decklist, com resultado de n=500 já rodado. Antes de reaproveitar, revisei o código inteiro e encontrei **5 problemas reais que invalidavam a maior parte dos números reportados**:

1. **Mana nunca era gasta de verdade.** `pay_mana()` só descontava Treasure (via sacrifício); terreno e rock eram recalculados do zero a cada carta conjurada, sem nunca subtrair o que já tinha sido gasto naquele turno. Com 5 terrenos, o script conseguia conjurar cinco mágicas de 5 manas diferentes no mesmo turno — mana efetivamente infinita disfarçada. Isso explica os números inflados do relatório original (battlefield médio 14,34, dano de combate médio 79,23 por turno).
2. **Um "combo" que não existe** — `combo_check()` tratava Jan Jansen + Ashnod's Altar + Pitiless Plunderer como um loop infinito e, quando "montava" (0,4% dos jogos), zerava a vida dos 3 oponentes fictícios na hora. Conferi o oráculo real: as duas habilidades da Jan Jansen custam `{T}` sem nenhuma forma de destapar — no máximo 1 ativação de cada por turno, sem loop possível. Isso já tinha sido conferido (e não encontrado) na varredura de combo da auditoria (seção 9).
3. **Combate contra 3 oponentes fictícios de 40 de vida que nunca bloqueiam nem interagem** — o script reportava "39,6% mata pelo menos 1 oponente, 33,6% mata os 3" até o turno 8, simulando dano sempre desbloqueado contra alvos indefesos. Nenhum outro simulador desta biblioteca faz isso — combate real de oponente nunca é modelado, só os gatilhos de ataque/dano que geram recurso pro próprio jogador.
4. **Gatilhos reais e rastreáveis viraram sorteio de moeda** — Lotho (real: "quando um jogador conjura a 2ª mágica do turno", condição rastreável) usava `random() < 0.45`; mesmo problema no Orochi Soul-Reaver.
5. **Mahadi com timing errado** — o gatilho real é em lote no final do turno ("para cada criatura que morreu ESTE turno"), o script disparava por morte individual, na hora.

Dado isso, reconstruí a lógica de jogo do zero (mantendo só a decklist, que já batia com a auditoria), seguindo a arquitetura já estabelecida nos outros 4 simuladores deste repositório: mana rastreada de verdade turno a turno, sem vida de oponente fictícia, gatilhos implementados a partir do oráculo real.

**Passo 0** (varredura mecânica no oráculo completo): 40 cartas com gatilho real. Todas conferidas contra a lógica implementada; as opponent-dependentes (Smothering Tithe, Monologue Tax, Mari, Revel in Riches morte-de-criatura-do-oponente, Grenzo goad) documentadas como tal, não fingidas.

**3 bugs reais encontrados e corrigidos durante o build** (achados rodando 20-30 mil partidas com timeout antes do batch oficial, não em teste manual):

1. **Treasure Vault (terreno) sendo conjurado como se fosse mágica** — mesmo bug clássico já visto no Toph e no Edgar Markov: o loop genérico de conjuração não excluía terrenos (mv=0, sempre "pagável"). Corrigido filtrando `n not in LAND_NAMES` no loop de castables.
2. **Cascade descartando a própria carta que estava sendo conjurada** — quando o Rain of Riches dá cascade num spell com custo adicional de descarte (Big Score/Unexpected Windfall), o cascade acontecia ANTES da carta original sair da mão, então o "descarte uma carta" do spell cascadeado podia acabar descartando a própria carta original (ainda presa na mão), causando `ValueError` no `.remove()` seguinte. Corrigido reordenando `cast_card()`: a carta sai da mão (ou vai a campo) antes de qualquer efeito colateral (cascade, Lotho) rodar.
3. **Métrica "cartas compradas extra" inflada pela compra normal do turno** — a compra obrigatória de cada turno usava a mesma função `draw_cards()` das compras-bônus dos motores, contando as duas juntas (média reportada de 8,17). Corrigido usando compra direta (`state.hand.append(...)`) pra compra normal, reservando `draw_cards()`/o contador pra compras de motor de verdade — a média real caiu pra 1,17.

**n=2000, seed_base=5000000, 8 turnos — resultado final:**

```
Avg mulligans: 0,59
Turno medio de conjuracao do Vihaan: 3,17 | mediana: 3
Nunca conjurado em 8 turnos: 1,8%
Avg Treasures criados (total no jogo): 4,01
Avg Treasures em campo no fim: 2,51
Avg Treasures sacrificados (total): 1,49
Avg Constructs criados: 0,37
Avg outros tokens criados: 0,73
Avg mortes de criatura: 0,58
Avg mortes de artefato: 1,55
Avg drain/dano agregado (proxy, NAO vida real de oponente): 1,10
Avg vida ganha: 0,47
Avg cartas compradas extra: 1,17
Avg cascades via Rain of Riches: 0,04
Avg combates com pelo menos 1 atacante: 3,89
Revel in Riches (10+ Treasures) — condicao satisfeita: 0,1% dos jogos | turno medio: 7,67
```

**Comparação com o relatório original (n=500) — pra deixar claro o tamanho da distorção:**

| Métrica | Script original (com os bugs) | Este script (corrigido) |
|---|---|---|
| Treasures em campo no fim | 6,49 | 2,51 |
| Battlefield count médio | 14,34 | não comparável diretamente (contagem diferente) |
| Revel in Riches condição batida | 4,8% | **0,1%** |
| "Combo" ligado | 0,4% (inexistente) | 0% (não existe, confirmado) |
| Mata pelo menos 1 oponente | 39,6% | não medido (sem oponente fictício) |

O motor de Treasure é real e funciona, mas em volume bem mais modesto do que o relatório original sugeria — 23 fontes em 99 cartas não significa "todas ativam toda partida"; a maioria das fontes é uma criatura/spell específica que precisa ser comprada E resolvida E (nos casos de combate) sobreviver até atacar. **0,1% de Revel in Riches é o número honesto** — é um wincon real mas de baixíssima frequência num jogo de 8 turnos, não os 4,8% fictícios do script original.

**Simplificações documentadas no docstring do script:** sem oponente real (nenhum permanente/spell/vida adversária de verdade — Smothering Tithe, Monologue Tax, Mari, Revel in Riches contra criatura do oponente, e o modo "goad" do Grenzo ficam sem efeito numérico solo); drain/dano são contadores agregados, nunca vida real de oponente; combate sem bloqueio (mesma convenção de todos os outros simuladores desta biblioteca); Grenzo e Laughing Jasper Flint (que exilariam da biblioteca do oponente) aproximados puxando da própria biblioteca, documentado no código.

---

---

### Política "maximizar criação e destruição de Treasure" — 2026-08-22

**Pedido do usuário:** priorizar a criação E destruição de Treasures como mecânica principal do goldfish (confirmando antes que Mirkwood Bats está no deck — está — e que "Marionette Apprentice" **não** está — a carta real na lista é **Marionette Master**, diferente: Fabricate 3 em vez de Fabricate 1, drain = poder da criatura em vez de fixo 1).

**Implementação — `TREASURE_MAXIMIZE_POLICY`, duas partes:**
1. **Criação:** cartas com tag de geração de Treasure ganham prioridade de conjuração sobre outras de mesmo custo (`is_treasure_source()`).
2. **Destruição — o achado central desta sessão:** se o Vihaan animou os Treasures em criaturas 3/3 outlaw no combate (`At the beginning of combat... Treasures you control become 3/3 Construct Assassin`), sacrificá-los pro **Ashnod's Altar** enquanto ainda são criaturas dispara **três categorias de gatilho ao mesmo tempo** — morte de criatura (Zulaport, Sephiroth, Pitiless Plunderer), morte de artefato (Marionette Master, Agent of the Iron Throne) e token saindo (Nadier's Nightblade, Mirkwood Bats) — porque um Treasure animado É simultaneamente artefato, criatura e token. Sacrificar direto pro Krark-Clan Ironworks (sem animar) só pega artefato+token, perde a categoria de morte de criatura inteira. Implementado em `aggressive_treasure_destruction()`, chamada no fim do `combat_step`; a mana gerada (`{C}{C}` por Treasure, sempre — não só quando o Goldspan Dragon está fora) entra num `bonus_mana_pool` disponível numa segunda passada de main phase pós-combate (adicionada pra aproveitar essa mana ainda no mesmo turno).

**Bug real encontrado e corrigido no processo:** o cálculo de drain da Marionette Master usava um poder chutado de "4" sem checar a carta real — o poder base real dela (Scryfall) é **1/3**, e como a implementação sempre escolhe o modo "3 Servos" do Fabricate 3 (não contadores), o poder nunca sai de 1. Corrigido pra usar o valor real.

Testado em 30.000 partidas com timeout antes do batch oficial (0 erros).

**n=2000, mesmas seeds, baseline (só sacrifica Treasure pra pagar mana) vs política nova:**

| Métrica | Baseline | Maximize | Δ |
|---|---|---|---|
| Avg Treasures criados (total) | 4,245 | 6,432 | +51,5% |
| Avg Treasures sacrificados (total) | 2,179 | 4,123 | +89,3% |
| Avg mortes de criatura | 0,667 | 1,264 | +89,5% |
| Avg mortes de artefato | 2,268 | 4,268 | +88,2% |
| Avg drain/dano agregado (proxy) | 1,327 | 1,764 | +32,9% |
| Avg vida ganha | 0,558 | 0,718 | +28,7% |
| Avg cartas compradas extra | 1,198 | 1,371 | +14,4% |
| Avg mana bonus gerada pós-combate | 0 | 1,323 | (mecânica nova) |
| Turno médio de conjuração do Vihaan | 3,171 | 3,17 | ~igual |
| Revel in Riches (10+ Treasures) | 0,25% | 0,25%¹ | ~igual |

¹ No batch de reporte final (seed diferente) saiu 0,2%/0,25% — dentro do ruído normal de amostra, não uma mudança real.

**Leitura:** a política quase **dobra** os gatilhos de aristocratas (mortes de criatura e de artefato) e aumenta drain em quase um terço, **sem custo medido na curva da comandante** — a mana gerada pelos sac outlets no combate compensa a mana que teria vindo dos Treasures se eles tivessem sido só guardados. É um ganho real de valor incremental por turno.

**Ressalva honesta — tensão real com o Revel in Riches:** essa política **compete diretamente** com o wincon alternativo de acumular 10+ Treasures simultâneos (Revel in Riches), porque ela ativamente esvazia o estoque de Treasure toda vez que anima e sacrifica. Nos dados, a taxa de Revel in Riches ficou estatisticamente igual nas duas políticas (a carta já é rara o suficiente — 1 cópia em 99 — que o efeito não apareceu de forma clara na amostra), mas conceitualmente são dois planos de jogo em tensão: se o objetivo prioritário for fechar o jogo via Revel in Riches, "maximizar destruição" não é a política certa — seria o oposto (acumular sem sacrificar). Como o usuário pediu explicitamente "criação e destruição como mecânica principal" (não o wincon do Revel in Riches), mantive `TREASURE_MAXIMIZE_POLICY = True` como default.

---

## Simulação #2 — re-run pós-troca de cartas (Rakdos Signet → Gleaming Splendor, Insatiable Avarice → Smaug the Magnificent) — 2026-08-22

**Mudanças no `CARD_DB` e no motor:**
- Removido `add("Rakdos Signet", ...)` e sua entrada em `GOOD_KEEP` (não contava mana em `rocks_mana()` de qualquer forma — era filtro, mana líquida 0 — então a remoção não altera a matemática de mana, só a fixação de cor real que a carta dava no jogo físico, registrado na auditoria).
- Removido `add("Insatiable Avarice", ...)` e seu bloco em `resolve_instant_sorcery`.
- Adicionado `Gleaming Splendor` com tag `opponent_dependent` — mesma convenção já usada pra Smothering Tithe/Monologue Tax/Mari (gatilho depende de ação real do oponente, não modelado numericamente aqui; carta fica "disponível" mas sem efeito solo na simulação, documentado desde o topo do arquivo).
- Adicionado `Smaug the Magnificent` com dois gatilhos reais implementados:
  - Upkeep — `create_treasures(state, 1, ...)` logo no início de `play_turn`, condicionado a já estar em campo (não dispara no turno em que é conjurado, igual à regra real).
  - Ataque — `drain(state, state.treasures)` no bloco de gatilhos de "ataca" do `combat_step` (mesmo padrão do Captain Lannery Storm/Goldspan Dragon/Kellogg), usando o contador agregado `drain_damage_total` como proxy de "dano igual ao número de Treasures", nunca vida real de oponente.
  - Tag `upkeep_treasure` adicionada a `TREASURE_SOURCE_TAGS` pra a política de priorização de conjuração (`TREASURE_MAXIMIZE_POLICY`) reconhecer a carta como fonte de Treasure.

**Bug real encontrado e corrigido nesta passada (não relacionado à troca de cartas, achado ao revisar `play_turn` pra decidir onde encaixar o upkeep do Smaug):** o gatilho da Magda (`Whenever you commit a crime, create a tapped Treasure token`) estava sendo checado **logo depois do reset de `commits_crime_this_turn = False`**, ou seja, sempre lia `False` — nenhuma magia do turno atual tinha sido conjurada ainda naquele ponto do código. Resultado: **o gatilho da Magda nunca disparava em nenhuma partida simulada**, apesar da carta estar corretamente implementada em todo o resto (tag `crime_treasure`, contada como fonte na seção 3 da auditoria). Corrigido movendo a checagem pra depois das duas chamadas de `main_phase()` (onde as magias que cometem crime — Path to Exile, Council's Judgment, Deadly Derision, Requisition Raid, Boros Charm, Teferi's Protection — são de fato conjuradas), antes do `end_step()`.

**Teste de robustez** (prática obrigatória documentada em `references/goldfish-sim-card-rules.md`): 15.000 partidas com timeout de 2s/partida via `signal.alarm`, **0 erros, 0 timeouts**.

**Batch oficial: n=3000, seed_base=6000000, turns=8** (substitui o batch anterior de n=2000/seed=5000000):

| Métrica | v1 (n=2000, lista antiga) | v2 (n=3000, lista nova + fix Magda) | Δ |
|---|---|---|---|
| Avg Treasures criados (total no jogo) | 6,43 | 6,62 | +3,0% |
| Avg Treasures em campo no fim | 2,31 | 2,39 | +3,5% |
| Avg mortes de criatura | 1,26 | 1,13 | −10,3% |
| Avg drain/dano agregado (proxy) | 1,76 | 2,27 | +28,7% |
| Avg cartas compradas extra | 1,37 | 0,99 | −27,7% |
| Revel in Riches (10+ Treasures) | 0,25% | 0,4% | +0,15pp |

**Leitura honesta, sem inventar causa única — a troca mistura vários efeitos ao mesmo tempo, então a leitura é qualitativa:**
- **Drain/dano subiu bastante (+28,7%)** — soma de dois efeitos reais: o novo gatilho de ataque do Smaug (`dano = Treasures controlados`) e, principalmente, o fix do bug da Magda (mais Treasures reais criados por crime → mais material pro resto da cadeia de aristocratas/drain).
- **Cartas compradas extra caiu (−27,7%)** — efeito direto e esperado da perda do Insatiable Avarice, que era uma fonte de draw puro (draw 3) e não foi substituída por nada equivalente. Bate com o que já estava registrado na auditoria (seção 6: 8→7 fontes de draw).
- **Treasures criados subiu só um pouco (+3,0%)**, apesar de ter ganho uma fonte nova (Smaug upkeep) e corrigido o bug da Magda — porque perdeu a fixação de mana do Rakdos Signet (efeito indireto: menos consistência de curva pode atrasar levemente o motor), e porque Gleaming Splendor não contribui numericamente na simulação (opponent-dependent, sem oponente real modelado — na mesa física ela deve contribuir mais do que aparece aqui).
- **Mortes de criatura caíram (−10,3%)** — dentro do ruído esperado de amostra a amostra (dois seeds diferentes, n diferentes), não atribuo isso a nenhuma das trocas especificamente.

Resultados salvos em `vihaan_v1_runs.jsonl` (sobrescrito com os 3000 jogos novos — o nome do arquivo ficou "v1" porque é a mesma versão do simulador, só re-rodado com a lista atualizada).

---

## Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks — última rodada da varredura completa dos 10
decks com simulador Python. Landfall N/A (0 cartas), dorks N/A (0 mana
dorks criatura na lista).

**Bugs reais achados (fixing lands + 3 cartas com tag e nenhum gatilho):**

- **Desolate Mire / Shadowblood Ridge**: são *filter lands* — real:
  `{1},{T}: Add {W}{B}` / `{1},{T}: Add {B}{R}`, **sem NENHUMA habilidade de
  mana grátis**. `lands_in_play()` contava as duas como +1 incondicional,
  igual qualquer terreno normal, mesmo sem nenhuma outra fonte de mana em
  campo pra "semear" o filtro. Corrigido: só contribuem se houver pelo
  menos 1 outra fonte de mana real presente (mesmo padrão do Fetid
  Heath/Rugged Prairie corrigido no Edgar Markov nesta sessão).
- **Bojuka Bog / Path of Ancestry / Clifftop Retreat / Dragonskull Summit /
  Isolated Chapel / Blackcleave Cliffs**: tags `etb_tapped`/`checkland_*`/
  `fastland` existiam no `CARD_DB`, nunca lidas em lugar nenhum — todo
  terreno produzia mana no próprio turno em que era jogado, mesmo os que
  entram tapped de verdade (incondicional, ou condicionado a controlar um
  básico do tipo certo, ou condicionado a ter 2 ou menos outros terrenos).
  Nova infraestrutura `tapped_lands_this_turn` (mesmo padrão de outros
  decks desta sessão). Blood Crypt (shockland) segue sempre entrando
  destapada — este arquivo rastreia vida de verdade, mas a convenção já
  estabelecida é assumir que o custo de vida sempre é pago.
- **Black Market Connections**: só existia a entrada no `CARD_DB` — **zero
  gatilho em lugar nenhum**. "At the beginning of your first main phase,
  choose one or more" (Treasure -1 vida / compra -2 vida / token 3/2 -3
  vida) — implementado escolhendo os 3 modos todo turno (IA agressiva,
  vida própria só perdida por fontes auto-infligidas neste sim solo).
- **Mirkwood Bats**: "Whenever you create **or sacrifice** a token" — só a
  metade "create" disparava (via `on_tokens_created`); a metade "sacrifice"
  nunca era checada em `on_token_leaves()`, apesar de ser o motor central
  de sacrifício do deck (`aggressive_treasure_destruction` dispara isso o
  jogo inteiro).
- **Sephiroth, Fabled SOLDIER**: só a metade passiva ("whenever another
  creature dies, opponent loses 1/you gain 1") estava modelada — a metade
  ETB/ataque ("you may sacrifice another creature. If you do, draw a
  card") 100% ausente. Implementada nos dois gatilhos reais (ETB via
  `resolve_permanent_etb`, ataque via `combat_step`), sacrificando só
  fodder barato (token genérico ou Construct), nunca uma criatura nomeada.

**Não corrigido (decisão de escopo, não bug):** Demolition Field's
habilidade paga exige "target nonbasic land an opponent controls" — sem
alvo legal possível num goldfish solo sem oponente real, a ativação não
pode acontecer de verdade (Regra 1 — não inventar estado alheio). Diferente
de Sephiroth/Black Market Connections, que não dependem de alvo do
oponente.

**Resultado (n=2000, seed_base=5500000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg Treasures criados (total) | 6,57 | **7,89** |
| Avg drain/dano agregado (proxy) | 2,54 | **3,63** |
| Avg vida ganha | 0,73 | **1,00** |
| Avg cartas compradas extra | 1,03 | **2,00** |
| Avg mortes de criatura | 1,16 | **1,43** |

Salto grande em quase toda métrica — Black Market Connections e Mirkwood
Bats eram motores centrais 100%/50% ausentes, então a correção teve
impacto real e substancial, não marginal.

**Robustez:** sweep de 20.000 jogos (seeds 5500000–5519999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

`lista.md` não mudou. `vihaan_v1_runs.jsonl` sobrescrito (3000 jogos).

---

## Correção — rodada ampliada da checklist obrigatória (categorias 10-13) — 2026-08-31

**Contexto:** pedido explícito do usuário pra completar a rodada ampliada do
`references/goldfish-sim-card-rules.md#checklist-obrigatória-de-categorias-de-mecânica`
(categorias 10 a 13 — métricas básicas, multi-face, planeswalker, Classes/Sagas)
neste deck, que só tinha recebido a checklist original (1-9) em 2026-08-28.

**Categoria 12 (planeswalker) — N/A confirmado independentemente:** varredura
programática de `type_line` no cache pra todas as 94 cartas únicas da lista
(comandante incluso). Zero cartas com `Planeswalker` no `type_line`. 0
planeswalkers na lista, categoria N/A.

**Categoria 13 (Classes/Sagas) — 1 carta na lista:** mesma varredura achou
só `Caretaker's Talent` (`Enchantment — Class`). 0 Sagas.

**Categoria 11 (multi-face) — 2 cartas na lista** (varredura de "//" em
`lista.md`, confirmado via API real que nenhuma outra carta tem layout
multi-face): `Brightclimb Pathway // Grimclimb Pathway` e `Sephiroth, Fabled
SOLDIER // Sephiroth, One-Winged Angel`.

### Bugs reais corrigidos

1. **Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel — o achado
   central desta rodada.** `layout` real (API Scryfall) = `transform`.
   `state.sephiroth_transformed` já existia e era SETADO na 4ª morte do
   turno (linha ~508 antiga), mas **nunca era LIDO em lugar nenhum** — uma
   tag de estado morta. Oráculo real completo:
   ```
   Frente ({2}{B}): Whenever Sephiroth enters or attacks, you may sacrifice
   another creature. If you do, draw a card.
   Whenever another creature dies, target opponent loses 1 life and you
   gain 1 life. If this is the fourth time this ability has resolved this
   turn, transform Sephiroth.
   Verso: Flying
   Super Nova — As this creature transforms into Sephiroth, One-Winged
   Angel, you get an emblem with "Whenever a creature dies, target
   opponent loses 1 life and you gain 1 life."
   Whenever Sephiroth attacks, you may sacrifice any number of other
   creatures. If you do, draw that many cards.
   ```
   3 correções reais:
   - **Emblem Super Nova** (`state.has_super_nova_emblem`, novo campo) é uma
     2ª fonte INDEPENDENTE de drain 1/vida 1 por morte — não substitui a
     habilidade da frente, ela deixa de existir junto com a transformação (o
     verso não tem mais "whenever another creature dies", só o emblem tem).
     O emblem drena em QUALQUER morte de criatura (texto "a creature", sem
     "another" — inclui a morte do próprio Sephiroth) e SEM limite de 4x por
     turno, permanente pro resto da partida mesmo se Sephiroth sair de campo
     depois. `on_creature_dies()` reescrita pra checar o emblem primeiro,
     caindo pra habilidade da frente só antes da transformação.
   - **Ataque muda de escala:** `try_sephiroth_sac_draw()` sempre usava
     "sacrifica 1, compra 1" (correto pra frente). Depois de transformado, o
     verso sacrifica QUALQUER NÚMERO de outras criaturas e compra essa
     quantidade — corrigido pra sacrificar TODO o fodder disponível
     (tokens + constructs) de uma vez quando `sephiroth_transformed`.
   - **Edge case adicional encontrado:** se Sephiroth já transformado morre
     e é recuperado via Sevinne's Reclamation (mv≤3, alcança ele), a nova
     cópia física reentra pela FRENTE (transform é do objeto físico, não do
     jogador) — `enter_battlefield()` agora reseta `sephiroth_transformed`
     nesse caso (o emblem, sendo independente, NÃO reseta).

2. **Caretaker's Talent — nível 1 só (nível 2/3 ausentes).** Oráculo real:
   ```
   Nivel 1: Whenever one or more tokens you control enter, draw a card.
   This ability triggers only once each turn.
   {W}: Level 2 — When this Class becomes level 2, create a token that's a
   copy of target token you control.
   {3}{W}: Level 3 — Creature tokens you control get +2/+2.
   ```
   Implementada `try_level_caretakers_talent()`: sobe de nível pagando como
   sorcery (mana sobrando depois de conjurar tudo da mão + Phyrexian
   Reclamation, heurística documentada no código — prioridade baixa em
   relação a desenvolver board novo, alta em relação a deixar mana parada),
   nível 2 cria cópia do token de maior valor controlado (Treasure >
   Construct > outro), nível 3 é cumulativo com 1/2. **O anthem do nível 3
   não tem onde se aplicar numericamente neste simulador** — nenhum efeito
   do deck (nem antes, nem depois desta correção) depende de poder de
   criatura-token; Marionette Master usa o próprio poder DELA, não de
   token. Decisão de arquitetura honesta (documentada no código, não
   inventado): reportado como métrica PROXY (tokens em campo × anthem
   implicado), nunca dano real calculado — mesma convenção já usada pra
   drain/vida no resto do arquivo.

3. **Brightclimb Pathway // Grimclimb Pathway — sem bug, decisão de
   arquitetura documentada.** `layout` real = `modal_dfc`. Confirmado: o
   motor de mana inteiro deste simulador (`lands_in_play`/`rocks_mana`/
   `total_mana`) nunca rastreou cor por fonte individual em NENHUM dos 35
   terrenos, antes ou depois desta rodada — só soma mana total agregada.
   Tratar a Pathway como land genérico de 1 mana é consistente com o resto
   do arquivo, não uma simplificação nova só pra esta carta. Comentário
   adicionado no `CARD_DB` explicando a decisão, sem inventar rastreamento
   de cor pra 1 carta só (nenhuma métrica reportada depende de cor).

4. **Achado extra (fora da lista original do pedido) — Phyrexian
   Reclamation sem NENHUMA lógica de ativação.** Categoria 7 (ativadas
   repetíveis) + categoria 10 (métrica RECURSION): só existia a entrada no
   `CARD_DB` (tag `recursion_repeat`), zero código em qualquer lugar.
   Oráculo real: `{1}{B}, Pay 2 life: Return target creature card from your
   graveyard to your hand.` Sem "activate only as sorcery" — repetível
   livremente. Implementada `try_phyrexian_reclamation()`, ativa quantas
   vezes mana+cemitério permitirem no main phase, priorizando devolver a
   criatura de maior mv (heurística documentada).

5. **Achado extra — Witch of the Moors com condição errada.** Oráculo real:
   "if you gained life THIS TURN" — o código checava
   `state.life_gained_total` (acumulado do JOGO INTEIRO), então depois de
   qualquer 1 ponto de vida ganho em qualquer turno anterior, a condição
   ficava permanentemente satisfeita pro resto da partida (recursão de
   graça todo turno sem depender de ganhar vida de novo). Corrigido com
   contador per-turno novo (`life_gained_this_turn`, resetado em
   `play_turn()`), mesmo padrão já usado noutros flags per-turno do
   arquivo.

6. **Achado extra — Black Market Connections disparando 2x por turno.**
   Oráculo real: "At the beginning of your **first** main phase" — só 1x
   por turno. `main_phase()` é chamada 2x por turno (pré e pós-combate,
   pra usar a mana bonus dos sac outlets — mecânica adicionada em
   2026-08-22) e `try_black_market_connections()` não tinha guarda contra a
   2ª chamada desde a correção de 2026-08-28 que implementou essa carta —
   dobrando Treasure/draw/token/perda de vida todo turno. Corrigido com
   flag per-turno (`black_market_connections_triggered_this_turn`), mesmo
   padrão de `caretaker_drawn_this_turn`/`kambal_drawn_this_turn`.

### Categoria 10 — métricas básicas obrigatórias, agora com linha formal

Antes desta rodada não havia linha "RECURSION"/"INTERACTION" formal no
relatório (`run_batch`), apesar do deck ter cartas reais de cada categoria.
Adicionadas 5 linhas explícitas no relatório: `RAMP`, `DRAW`, `INTERACTION`,
`RECURSION`, `FINISHER/LETHALITY` — cada uma citando as cartas que a
compõem, não só um número solto.

### Robustez

20.000 partidas (seeds 7000000–7019999, timeout 2s/partida via
`signal.alarm`) — **0 erros, 0 timeouts**.

### Resultado — batch oficial (n=3000, seed_base=6000000, turns=8), antes vs. depois

**Nota honesta:** a maioria das métricas CAIU, não subiu — o achado extra
#6 (Black Market Connections disparando 2x/turno desde 2026-08-28) estava
inflando quase toda métrica de Treasure/draw/drain por um fator real, e sua
correção domina o delta total mais do que os efeitos NOVOS (Sephiroth
transform, Caretaker nível 2/3, Phyrexian Reclamation), que são raros o
suficiente (peças únicas, condições específicas) pra não compensar a queda.

| Métrica | Antes (com bug do BMC 2x) | Depois (corrigido) | Δ |
|---|---|---|---|
| Avg Treasures criados (total) | 8,33 | 7,63 | −8,4% |
| Avg Treasures sacrificados (total) | 5,61 | 5,11 | −8,9% |
| Avg mortes de criatura | 1,52 | 1,36 | −10,5% |
| Avg mortes de artefato | 5,76 | 5,26 | −8,7% |
| Avg drain/dano agregado (proxy) | 3,54 | 3,09 | −12,7% |
| Avg vida ganha | 1,04 | 0,94 | −9,6% |
| Avg cartas compradas extra | 2,02 | 1,63 | −19,3% |
| Revel in Riches (10+ Treasures) | 0,5% | 0,4% | −0,1pp |

**Métricas novas (sem baseline "antes", efeitos recém-implementados):**

| Métrica nova | Valor |
|---|---|
| Sephiroth transformado (emblem Super Nova ativo) — % de jogos | 0,5% |
| Avg cartas compradas via sac do Sephiroth (as 2 faces) | 0,09 |
| Caretaker's Talent nível 2 alcançado — % de jogos | 10,0% |
| Caretaker's Talent nível 3 alcançado — % de jogos | 5,4% |
| RECURSION — avg cartas recuperadas do cemitério/jogo | 0,14 |
| ...das quais via Phyrexian Reclamation (repetível) | 0,03 |
| INTERACTION — avg remoção/wipe conjurados/jogo | 0,71 |

**Leitura:** o efeito líquido desta rodada é uma correção pra BAIXO nas
métricas centrais (o bug do BMC 2x era o maior distorcedor não descoberto
até agora), compensada só parcialmente pelos efeitos novos genuínos — mas
raros o suficiente numa lista de 99 cartas singleton (Sephiroth transforma
em 0,5% dos jogos porque exigir 4 mortes de criatura NO MESMO turno é um
board state avançado; Caretaker nível 3 exige {2}+{W}+{3}{W}=6 mana extra
sobrando além de tudo mais que o turno já gastou). Os números "depois" são
os honestos — nenhuma métrica estava inflada por efeito novo desta rodada,
só corrigida de uma distorção antiga (dobra do BMC).

`lista.md` não mudou. `vihaan_v1_runs.jsonl` sobrescrito (3000 jogos, mesma
seed_base=6000000 — script principal não mudou de seed).

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
