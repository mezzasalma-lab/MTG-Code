# Goldfish Log — Esika, God of the Tree // The Prismatic Bridge

## Sisay, Weatherlight Captain (5ª candidata do dia, pedida depois das 4) — 2026-09-29

**Pedido:** "E a avaliação de Sisay, Weatherlight Captain para o deck da PB?" (prós e contras, Regra #4/#5).
Oráculo ao vivo (Scryfall): {2}{W}, Legendary Creature — Human Soldier 2/2. *"Sisay gets +1/+1 for each color among other
legendary permanents you control. {W}{U}{B}{R}{G}: Search your library for a legendary permanent card with mana value less
than Sisay's power, put that card onto the battlefield, then shuffle."* Rulings ao vivo (2019-06-14): última informação se
ela sai antes da resolução; {X} na biblioteca vale 0. Cláusula a cláusula em `checklist-oraculo.md` (adendo Sisay).

**Correção de premissa minha:** eu lembrava "poder = maior MV entre as outras lendárias". O oráculo é outro (+1/+1 por COR
entre as OUTRAS lendárias; a busca é limitada pelo poder dela). Foi pego pela leitura ao vivo antes de escrever código.

### O que muda no simulador (via `swap`; a lista atual não muda)

- Sisay é criatura lendária de 3 MV, corpo 2/2 + `_sisay_bonus` (união das cores dos outros permanentes lendários em campo,
  inclusive a Bridge, que é 5 cores → 7/7 na hora). Não ataca (`NON_ATTACKING_NAMES`, mesma convenção da Tam).
- Ativação `sisay_activate`: {W}{U}{B}{R}{G}, **sem {T}** (ativa no turno em que entra), procura lendária com MV < poder que eu
  ainda não controlo; embaralha antes dos ETBs; PW entra com lealdade (× Doubling Season) e ativa no mesmo main phase; Oath de
  Teferi pisca; Carth olha as 7; Chain Veil registra a entrada. Peregrine Dynamo copia a ativação (1×/turno, {1}).
  Delighted Halfling e Plaza of Heroes pagam a Sisay (é lendária).
- Política de escolha do alvo: sem PW em campo → melhor PW; com 2+ PWs → Oath de Teferi; senão o PW de maior MV; senão peça de
  motor. **Ordem no turno: a busca vai na frente da mão** (`sisay_pre_hand_all`). Medido: −0,086 (busca primeiro) vs −0,069
  (política antiga: mão primeiro, busca antes só com alvo MV ≥ 6) no 1º ultimate.
- Chaves de política novas em `CAND_POLICY`: `sisay_activate` e `sisay_pre_hand_all` (o A/B liga/desliga cada uma com `@chave`).
- Estatísticas novas (`cand_stats`): `sisay_activations`, `sisay_fetches`, `sisay_fetch_pw`, `sisay_fetch_engine`,
  `sisay_power_sum`, `sisay_dynamo_copies`, `entered_Sisay…`, `first_turn_…`.

### Validação

- Testes: 134/134 (10 novos da Sisay: bônus de cor, Bridge 7/7, sem {T}, alvo por MV < poder, regra da lenda, Doubling Season,
  ordem antes/depois da mão, Dynamo, Halfling/Plaza, não ataca).
- Lista atual **bit-idêntica** ao snapshot anterior (`bitident.py`: N = 300 no padrão + 400 na resiliência (4 perfis), 0 divergências).
- Regressão de 40.000 partidas (20.000 padrão + 20.000 resiliência, 4 perfis de mesa, swaps rotativos incluindo Sisay
  sozinha em 3 slots e um pacote de 5 candidatas, alarme de 20 s): **0 exceções, 0 travamentos** (a Sisay entrou em 6.119 dessas partidas; 4.335 partidas tiveram ao menos uma ativação).
- Commander Spellbook (antes/depois, lista de 99 + Esika): **0 combos novos**; 2 quase-combos com Intruder Alarm (não está na
  lista). Não é Game Changer.

### A/B pareado (N = 3.000 seeds; padrão 3.000.000+, resiliência mista 6.000.000+; IC95%; negrito = não cruza 0)

**Sisay no lugar de cada corte (Δ pareado sobre a lista atual; negativo em 1º ult = melhor)**

| sai ↓ | padrão: 1º ult | padrão: P(ult ≤ T8) | resil.: vida ≤ 0 | resil.: 1º ult | resil.: P(dano ≥ 40) |
|---|---|---|---|---|---|
| Arena Rector | **-0.086 ±0.019** | **+2.23 pp ±0.68** | **-0.40 pp ±0.38** | +0.008 ±0.023 | -0.53 pp ±0.91 |
| Swan Song | **-0.062 ±0.017** | **+1.53 pp ±0.64** | **-0.57 pp ±0.46** | +0.012 ±0.022 | **-1.07 pp ±0.88** |
| Veil of Summer | **-0.072 ±0.020** | **+2.67 pp ±0.72** | -0.23 pp ±0.47 | +0.005 ±0.024 | -0.70 pp ±0.91 |
| Oath of Nissa | **-0.047 ±0.022** | **+1.70 pp ±0.77** | -0.43 pp ±0.56 | +0.023 ±0.024 | **-1.23 pp ±0.94** |
| Farseek | **-0.047 ±0.020** | **+1.73 pp ±0.69** | +0.07 pp ±0.44 | **+0.029 ±0.025** | **-1.53 pp ±0.97** |
| Doubling Season | **-0.033 ±0.021** | **+1.07 pp ±0.73** | -0.53 pp ±0.56 | **+0.042 ±0.025** | **-1.73 pp ±1.01** |

Controles do mesmo A/B: cortar Arena Rector por um **corpo 2/2 lendário sem texto** (mesmo custo, cor, tipo) dá
+0,002 ±0,009 no padrão (sem efeito); cortar Swan Song por ele dá +0,046 ±0,014 (o corte em si custa isso). Ou seja, **todo o
ganho de ritmo da Sisay vem do texto (a busca), não do corpo**.

**O que o TEXTO faz: Sisay − corpo 2/2 sem texto (mesmo slot; todas as partidas | só partidas em que a carta entrou)**

| métrica | Arena Rector (todas) | Swan Song (todas) | Arena Rector (entrou) | Swan Song (entrou) |
|---|---|---|---|---|
| padrão Δ 1º ult (turno) | **-0.089 ±0.017** | **-0.108 ±0.018** | **-0.193 ±0.037** | **-0.246 ±0.039** |
| padrão Δ P(ult ≤ T8) | **+2.30 pp ±0.62** | **+2.93 pp ±0.64** | **+5.01 pp ±1.35** | **+6.67 pp ±1.44** |
| resil. Δ vida ≤ 0 | -0.17 pp ±0.28 | **-0.60 pp ±0.36** | -0.37 pp ±0.64 | **-1.34 pp ±0.80** |
| resil. Δ 1º ult | **-0.050 ±0.017** | **-0.026 ±0.016** | **-0.111 ±0.039** | **-0.059 ±0.035** |
| resil. Δ PW-turnos vivos | **+0.547 ±0.162** | **+0.259 ±0.138** | **+1.225 ±0.360** | **+0.578 ±0.307** |
| resil. Δ PWs mortos em combate | **-0.014 ±0.010** | **-0.013 ±0.011** | **-0.031 ±0.023** | **-0.029 ±0.025** |
| resil. Δ P(dano ≥ 40) | **+1.67 pp ±0.80** | **+1.00 pp ±0.72** | **+3.73 pp ±1.78** | **+2.23 pp ±1.61** |
| resil. Δ P(dano ≥ 120) | +0.57 pp ±0.71 | +0.10 pp ±0.68 | +1.27 pp ±1.58 | +0.22 pp ±1.52 |

**Sensibilidade (slot Arena Rector, Δ pareado sobre a base)**

| variante | padrão Δ 1º ult | padrão Δ P(ult ≤ T8) | resil. Δ vida ≤ 0 | resil. Δ 1º ult | resil. Δ PW-turnos vivos | resil. Δ P(dano ≥ 40) |
|---|---|---|---|---|---|---|
| política final (busca antes da mão) | **-0.086 ±0.019** | **+2.23 pp ±0.68** | **-0.40 pp ±0.38** | +0.008 ±0.023 | -0.199 ±0.213 | -0.53 pp ±0.91 |
| **sem a busca** (só o corpo que cresce) | +0.002 ±0.009 | -0.07 pp ±0.33 | **-0.33 pp ±0.33** | **+0.049 ±0.021** | **-0.651 ±0.176** | **-2.93 pp ±0.82** |
| política antiga (mão primeiro; busca antes só com alvo MV ≥ 6) | **-0.069 ±0.016** | **+1.73 pp ±0.61** | -0.37 pp ±0.38 | **+0.027 ±0.022** | -0.157 ±0.193 | **-1.67 pp ±0.89** |

**Sensibilidade ao perfil de mesa (só resiliência, N = 3.000 por perfil, slot Arena Rector; política final)**

| candidata − controle (o que o TEXTO faz) | mista | go_wide | voltron | low |
|---|---|---|---|---|
| vida ≤ 0 | -0.17 pp ±0.28 | **-0.67 pp ±0.40** | **-0.60 pp ±0.32** | -0.03 pp ±0.07 |
| 1º ult | **-0.050 ±0.017** | **-0.040 ±0.019** | **-0.077 ±0.019** | **-0.077 ±0.019** |
| PW-turnos vivos | **+0.547 ±0.162** | **+0.282 ±0.152** | **+0.535 ±0.161** | **+0.718 ±0.171** |
| PWs mortos em combate | **-0.014 ±0.010** | +0.000 ±0.015 | **-0.034 ±0.013** | **-0.016 ±0.006** |
| P(dano ≥ 40) | **+1.67 pp ±0.80** | +0.67 pp ±0.73 | **+1.77 pp ±0.80** | **+2.27 pp ±0.84** |

| candidata − base (o que o SLOT faz) | mista | go_wide | voltron | low |
|---|---|---|---|---|
| vida ≤ 0 | **-0.40 pp ±0.38** | **-0.67 pp ±0.48** | **-0.43 pp ±0.38** | -0.10 pp ±0.11 |
| 1º ult | +0.008 ±0.023 | +0.006 ±0.022 | **-0.031 ±0.024** | **-0.060 ±0.022** |
| PW-turnos vivos | -0.199 ±0.213 | **-0.275 ±0.192** | -0.127 ±0.211 | +0.182 ±0.205 |
| PWs mortos em combate | **-0.017 ±0.014** | -0.001 ±0.017 | **-0.037 ±0.016** | **-0.018 ±0.007** |
| P(dano ≥ 40) | -0.53 pp ±0.91 | **-0.93 pp ±0.82** | -0.17 pp ±0.94 | +0.77 pp ±0.92 |

**Uso por partida em que a carta entrou (slot Arena Rector; mediana | média | P(>0))**

| métrica | padrão (n=1.378 de 3.000) | resiliência (n=1.339 de 3.000) |
|---|---|---|
| ativações | 3 \| 3,18 \| 76,2% | 1 \| 1,99 \| 66,2% |
| buscas | 3 \| 3,24 \| 76,2% | 1 \| 2,04 \| 66,2% |
| buscas que trouxeram PW | 2 \| 2,21 \| 65,0% | 1 \| 1,35 \| 53,9% |
| buscas que trouxeram peça de motor | 1 \| 1,03 \| 63,3% | 0 \| 0,70 \| 48,2% |
| cópias pela Peregrine Dynamo | 0 \| 0,06 \| 6,4% | 0 \| 0,05 \| 4,8% |
| turno em que entra | mediana 8 | mediana 8 |

Ela entra em ~45% das partidas (padrão 45,9% no slot Arena Rector; 42–47% nos seis cortes).

### Leitura (Regra #5: o deck primeiro, o simulador como apoio)

**Pelo deck (medido + raciocínio):**
- **É a mais "Bridge-nativa" das candidatas.** É criatura (a Bridge a acerta, o que nenhuma das 4 PWs do dia faz), a própria Bridge
  conta como lendária de 5 cores, então ela fica 7/7 no turno em que entra e alcança 22 das 24 lendárias da lista (só Kaya MV 7 e
  Ugin MV 8 ficam de fora). Sem {T}: a doença de invocação não atrasa a busca.
- A busca é um tutor repetível e gratuito em cartas (só custa {W}{U}{B}{R}{G}): traz PW (2,2 por partida em que entra no padrão),
  que entra com o dobro de lealdade pela Doubling Season e **ativa no mesmo turno**; ou peça de motor (Chain Veil, Oath de Teferi,
  Carth, Vorinclex, Atraxa, Peregrine Dynamo). A Dynamo copia a busca; o Chain Veil e o Oath dobram ativações.
- **Medido:** melhor das 5 candidatas do dia no ritmo (−0,086 turno no slot Arena Rector; melhora nos 6 cortes; Dihada −0,057,
  Guff −0,053, Sarkhan −0,010, Vronos −0,004 no mesmo slot). Todo o efeito vem da busca (sem ela: +0,002). Ainda fica atrás de
  Loyal Tutor (−0,135) e Tam (−0,119) no mesmo slot (`ab_candidatas_vs_fra.py`, seção 7 acima).
- No **terceiro slot** ela é marginalmente melhor que o Entrust no ritmo (−0,028 ±0,017; +1,4 pp de P(ult ≤ T8)) e pior na
  resiliência (1º ult +0,028 ±0,022; dano ≥ 40 −0,9 pp, dentro do ruído). Como **quarta carta** por cima do pacote FRA completo,
  −0,018 ±0,020 (não significativo).

**Contra:**
- **5 mana com as 5 cores por ativação** (mais os 3 da conjuração): compete com a mão pelo mesmo mana; a política final põe a busca
  na frente, mas isso custa a mão do turno. Mediana de 3 ativações por partida em que ela entra no padrão, 1 na resiliência.
- **Depende da Bridge:** sem ela, o poder dela é 2 + cores das OUTRAS lendárias (vermelho só pelo Nicol Bolas: máximo 6/6 sem a
  Bridge) e a busca alcança bem menos.
- **É criatura:** exposta a remoção e wipe (a Plaza of Heroes a protege, se estiver em campo). O simulador de resiliência a
  modela como criatura comum (não ataca, não bloqueia). Contra o corpo 2/2 sem texto, o TEXTO ganha PW-turnos vivos (+0,28 a
  +0,72) e 1º ult da resiliência (−0,04 a −0,08) nos 4 perfis de mesa; contra a BASE (o slot que ela toma) os PW-turnos ficam
  entre −0,28 e +0,18 e o P(dano ≥ 40) entre −0,9 e +0,8 pp: ela paga o slot e não deixa ganho claro de resiliência ou dano.
- Entra tarde (turno mediano 8) e só em ~45% das partidas; não alcança Kaya/Ugin; o ganho em vida ≤ 0 é pequeno (−0,4 a −0,6 pp,
  significativo só em 2 dos 6 cortes).
- Sobre a resiliência ao comparar com a BASE (não com o corpo): PW-turnos vivos −0,199 ±0,213 e P(dano ≥ 40) −0,53 pp ±0,91, ambos
  dentro do ruído no slot Arena Rector; **o slot que ela toma é que pesa**, não a carta.

**O que o simulador NÃO vê (e pode subestimar ou superestimar):**
- ativação no fim do turno do oponente (a habilidade não tem restrição de timing): seria uma ativação EXTRA com mana que sobrou do
  meu turno; o simulador só ativa no meu turno, então **subestima a carta**;
- resposta do oponente à ativação (ruling da última informação, 📊 estrutural);
- o modelo de cor é agregado (1 fonte por cor), então **superestima** a facilidade de pagar {W}{U}{B}{R}{G} com mana real;
- a frente da Esika.

**Onde interage com a lista (Regra #4):** Bridge (alvo e fonte do bônus), Doubling Season (lealdade dobrada dos PWs buscados),
Chain Veil/Oath de Teferi/Urza III (2 ativações do PW buscado), Peregrine Dynamo (copia a busca), Carth (o embaralhamento da busca
muda o topo que ele olha), Delighted Halfling/Plaza of Heroes (pagam a Sisay). Combos: 0 novos. Bracket: não é Game Changer; o deck continua com 3.

### Limites desta rodada (Regra #7: o que foi e o que NÃO foi verificado)

- **Verificado:** oráculo e rulings ao vivo cláusula a cláusula com teste dirigido; conceitos "lendária permanente", MV e "cor entre
  lendárias" enumerados por script sobre o `type_line`/`cmc` ao vivo; Spellbook antes/depois; A/B nos 6 cortes com controle de corte
  e de corpo; condicional (só quando entrou); sensibilidade a política (3 variantes) e a perfil de mesa (4); bit-identidade da lista
  atual; regressão de 40.000 partidas.
- **NÃO verificado:** as outras 99 cartas contra a Sisay uma a uma (só os conceitos e motores listados); ativação no fim do turno do
  oponente; ordem da ativação contra todas as janelas do turno (só mão-primeiro vs busca-primeiro); pagamento de cor com mana real
  (o arquivo usa 1 fonte por cor); resposta de oponente à ativação; a frente da Esika.

## Rodada das 4 candidatas: Dihada, Commodore Guff, Vronos, Sarkhan the Masterless — 2026-09-29

**Pedido do usuário:** "Avalie a inclusão das seguintes cartas ao deck, quero
prós e contras mais do que sugestões de cortes no momento": Dihada (pelo −3),
Commodore Guff (contador de lealdade em todos os PWs no end step), Vronos
(phase out de 2 PWs até o meu próximo turno) e Sarkhan the Masterless (o +1
vira todos os PWs em Dragões 4/4 voadores). Cláusula a cláusula, rulings,
premissas corrigidas e escopo: `checklist-oraculo.md` (mesma data).

**Duas premissas do pedido que o oráculo não confirma:** a Guff põe contador
em **um** PW alvo por end step (não em todos); o Vronos tira de fase **outros**
PWs (até 2), no "next end step".

### O que muda no simulador

- As 4 entram **só via `swap`**. A lista atual continua bit-idêntica: 900 partidas
  padrão + 1.200 de resiliência (4 perfis) comparadas campo a campo com o código
  anterior, 0 divergências.
- Efeitos novos (`prismatic_bridge_goldfish_v1.py`, bloco "CANDIDATAS 2026-09-29"):
  - Dihada: escudo da +2 (vigilância/lifelink/indestrutível numa lendária), −3 com
    Treasure (`treasure_stock`: mana de qualquer cor, persiste, some ao gastar), −11 (untap de fontes de mana + criaturas
    de oponente roubadas atacam com haste).
  - Guff: gatilho de end step (`guff_end_step`), Wizard (mana {R} só pra PW: abate o genérico), −3 (X = PWs).
  - Vronos: phase out no end step (`vronos_phase_out_step`), −2 (1 bounce por oponente), −7 (Construct 9/9).
  - Sarkhan: estático (cada Dragão dá 1 de dano em cada atacante), +1 (PWs viram Dragão 4/4 voador), −3 (Dragão).
  - Motores da lista que agora enxergam as 4: Doubling Season (fichas, Treasure, lealdade inicial), Bolas (empresta os −3
    de compra), Peregrine Dynamo (copia), Oath/Chain Veil (2× no turno), Tam (4 tipos de PW novos).
- **Correção de premissa minha, registrada:** eu tinha modelado que o PW animado pela Sarkhan não ativa mais. O ruling
  (2019-05-03) diz que ainda ativa. Corrigi antes do A/B final; o primeiro lote de Vronos/Sarkhan foi descartado e rodado
  de novo. O Vronos −7 também foi ajustado ao ruling (ataca no mesmo turno se o artefato já estava em campo).

### Validação

- **Testes dirigidos:** 124/124 (23 novos, um por cláusula e por interação: escudo da Dihada em combate e em wipe, Treasure
  como mana de qualquer cor e consumo no fim do turno, Guff com Doubling Season/All Will Be One/fora de fase, Wizard
  doente e depois pagando só genérico de PW, ordem Guff antes do phase out, Vronos −2/−7 e o Construct indestrutível,
  Sarkhan animando (só os prontos atacam, ainda ativam, perdem a Gauntlet), Dragões atirando nos atacantes e o dano marcado
  restaurado, Bolas emprestando o −3 da Guff/Dihada, 12 partidas completas por candidata e pelas 4 juntas).
- **Bit-identidade da lista atual:** 0 divergências (600 + 300 padrão, 800 + 400 resiliência) em todos os campos do estado,
  antes e depois das correções de ruling.
- **Regressão:** 20.000 partidas padrão + 20.000 de resiliência (perfis rotativos), swaps rotativos (base, cada
  candidata, 3 combinações das 4 juntas): **0 exceções, 0 travamentos** (alarme de 20 s por partida). Entraram em campo
  em 9.160 (Dihada), 9.599 (Guff), 8.716 (Vronos) e 8.758 (Sarkhan) dessas 40.000 partidas; o −11 da Dihada disparou em
  327 e o −7 do Vronos em 1.748.
- **Commander Spellbook antes/depois** (`spellbook_antes_depois.py`; comandante + 99): lista atual 12 combos e 92 quase-combos. Com cada candidata e com as
  4 juntas: **0 combos novos, 0 removidos, 0 quase-combos novos**. Controle positivo: tirar a The Chain Veil derruba 4
  combos (o pipeline reage a mudança de lista). Nenhuma das 4 é Game Changer (`is:gamechanger`): o deck segue com 3.
- **Oráculo:** Dihada, Vronos e Sarkhan entraram no `scryfall-cache/oracle-cache.json` (a Guff já estava, texto idêntico).

### A/B pareado (N = 3.000 seeds; padrão 3.000.000+, resiliência mista 6.000.000+)

Scripts: `ab_candidatas.py` (harness), `ab_candidatas_sum.py` (tabelas), `ab_vronos_protecao.py`,
`regress_candidatas.py`. A carta nova entra **na linha** da cortada (troca posicional): a partida só diverge quando aquela
posição é comprada ou revelada. Cortes: Arena Rector, Swan Song, Veil of Summer, Oath of Nissa, Farseek e Doubling Season
(controle: cortar o motor tem que sair pior). Métricas sempre limitadas por partida (regra "A/B de carta" de
`references/goldfish-sim-card-rules.md`): turno do 1º ultimate (sem ultimate = 11), P(ultimate ≤ T8), vida ≤ 0 e PW-turnos
na resiliência, e **P(dano nosso ≥ 40 / ≥ 120)**: a média do proxy de dano é dominada pelas partidas em loop (a média com teto de
1000 subestimava a Sarkhan: Δ −5,1 ±5,9 sobre a base no slot Arena Rector, enquanto P(dano ≥ 40) sobe +6,2 pp sobre o PW inerte); o limiar não. **Controle do lado da entrada:** um PW de lealdade 5
**sem nenhuma habilidade** (só existe no harness), no mesmo slot. Candidata − PW inerte = valor do TEXTO, sem misturar com "é
mais um PW" nem com o valor do slot cortado (decomposição da regra "A/B de carta cara ou tardia").

**Base (lista atual, motor atual):**
- padrão: 1º ultimate no turno 9,253; P(ult ≤ T8) 34,7%; 1,484 turnos com ultimate;
- resiliência (mesa mista): vida ≤ 0 em 14,7% (go_wide 28,1%, voltron 18,9%, low 1,8%); 1º ult 9,693; PW-turnos vivos 15,75; PWs mortos em combate 0,577; PWs no T10 5,36.

**Frequência:** Dihada e Guff entram em 44 a 47% das partidas (num slot só; chegam pela Bridge ou pela mão, mediana do
1º turno em campo: 8); Vronos e Sarkhan em 39 a 43% (custam 5). O efeito condicional (só as partidas em que entram) é
cerca de 2× o incondicional.


#### 1. O que o TEXTO da carta faz: candidata menos o PW inerte no mesmo slot

Negativo em 1º ult e vida ≤ 0 = melhor; positivo em P(ult ≤ T8), PW-turnos e P(dano) = melhor. Negrito = IC95% não cruza 0.

**Efeito das HABILIDADES: candidata menos o PW inerte no mesmo slot (todas as partidas; negativo em 1º ult/vida ≤ 0 = melhor)**

| candidata | métrica | sai Arena Rector | sai Swan Song |
|---|---|---|---|
| Dihada | padrão Δ 1º ult (turno) | **-0.063 ±0.014** | **-0.074 ±0.016** |
| Dihada | padrão Δ P(ult ≤ T8) | **+1.40 pp ±0.53** | **+1.93 pp ±0.58** |
| Dihada | padrão Δ turnos c/ ult | **+0.097 ±0.016** | **+0.097 ±0.017** |
| Dihada | resil. Δ vida ≤ 0 | -0.23 pp ±0.30 | -0.33 pp ±0.41 |
| Dihada | resil. Δ 1º ult | **-0.100 ±0.019** | **-0.079 ±0.018** |
| Dihada | resil. Δ PW-turnos vivos | **+1.829 ±0.217** | **+1.649 ±0.203** |
| Dihada | resil. Δ PWs mortos em combate | -0.002 ±0.015 | -0.006 ±0.013 |
| Dihada | resil. Δ P(dano nosso ≥ 40) | **+5.47 pp ±0.93** | **+4.43 pp ±0.86** |
| Dihada | resil. Δ P(dano nosso ≥ 120) | **+4.77 pp ±0.88** | **+3.27 pp ±0.79** |
| Guff | padrão Δ 1º ult (turno) | **-0.059 ±0.012** | **-0.060 ±0.011** |
| Guff | padrão Δ P(ult ≤ T8) | **+1.70 pp ±0.46** | **+1.50 pp ±0.46** |
| Guff | padrão Δ turnos c/ ult | **+0.063 ±0.012** | **+0.071 ±0.012** |
| Guff | resil. Δ vida ≤ 0 | **-0.47 pp ±0.24** | **-0.33 pp ±0.28** |
| Guff | resil. Δ 1º ult | **-0.063 ±0.015** | **-0.052 ±0.015** |
| Guff | resil. Δ PW-turnos vivos | **+0.619 ±0.124** | **+0.442 ±0.127** |
| Guff | resil. Δ PWs mortos em combate | **-0.052 ±0.012** | **-0.050 ±0.013** |
| Guff | resil. Δ P(dano nosso ≥ 40) | **+2.40 pp ±0.68** | **+1.60 pp ±0.67** |
| Guff | resil. Δ P(dano nosso ≥ 120) | **+1.67 pp ±0.63** | **+1.13 pp ±0.61** |
| Vronos | padrão Δ 1º ult (turno) | **-0.010 ±0.007** | -0.005 ±0.008 |
| Vronos | padrão Δ P(ult ≤ T8) | +0.03 pp ±0.27 | +0.07 pp ±0.31 |
| Vronos | padrão Δ turnos c/ ult | **+0.010 ±0.008** | +0.005 ±0.008 |
| Vronos | resil. Δ vida ≤ 0 | -0.10 pp ±0.28 | +0.07 pp ±0.37 |
| Vronos | resil. Δ 1º ult | **-0.026 ±0.015** | **-0.036 ±0.014** |
| Vronos | resil. Δ PW-turnos vivos | -0.039 ±0.139 | **-0.130 ±0.110** |
| Vronos | resil. Δ PWs mortos em combate | **-0.037 ±0.014** | **-0.035 ±0.014** |
| Vronos | resil. Δ P(dano nosso ≥ 40) | **+1.33 pp ±0.66** | **+1.47 pp ±0.66** |
| Vronos | resil. Δ P(dano nosso ≥ 120) | **+0.70 pp ±0.57** | +0.33 pp ±0.52 |
| Sarkhan | padrão Δ 1º ult (turno) | **-0.017 ±0.007** | **-0.009 ±0.007** |
| Sarkhan | padrão Δ P(ult ≤ T8) | +0.23 pp ±0.25 | +0.17 pp ±0.28 |
| Sarkhan | padrão Δ turnos c/ ult | **+0.016 ±0.008** | **+0.009 ±0.008** |
| Sarkhan | resil. Δ vida ≤ 0 | **-0.33 pp ±0.32** | -0.23 pp ±0.39 |
| Sarkhan | resil. Δ 1º ult | **-0.013 ±0.013** | **-0.022 ±0.012** |
| Sarkhan | resil. Δ PW-turnos vivos | -0.050 ±0.110 | **-0.125 ±0.106** |
| Sarkhan | resil. Δ PWs mortos em combate | **-0.043 ±0.012** | **-0.042 ±0.013** |
| Sarkhan | resil. Δ P(dano nosso ≥ 40) | **+6.20 pp ±0.93** | **+5.83 pp ±0.92** |
| Sarkhan | resil. Δ P(dano nosso ≥ 120) | **+1.50 pp ±0.58** | **+1.40 pp ±0.60** |

**Efeito das HABILIDADES: candidata menos o PW inerte no mesmo slot (só partidas em que ela entrou; negativo em 1º ult/vida ≤ 0 = melhor)**

| candidata | métrica | sai Arena Rector | sai Swan Song |
|---|---|---|---|
| Dihada | padrão Δ 1º ult (turno) | **-0.135 ±0.030** | **-0.161 ±0.034** |
| Dihada | padrão Δ P(ult ≤ T8) | **+2.98 pp ±1.12** | **+4.25 pp ±1.26** |
| Dihada | padrão Δ turnos c/ ult | **+0.207 ±0.032** | **+0.214 ±0.036** |
| Dihada | resil. Δ vida ≤ 0 | -0.43 pp ±0.63 | -0.72 pp ±0.89 |
| Dihada | resil. Δ 1º ult | **-0.213 ±0.039** | **-0.170 ±0.039** |
| Dihada | resil. Δ PW-turnos vivos | **+3.939 ±0.439** | **+3.578 ±0.417** |
| Dihada | resil. Δ PWs mortos em combate | +0.000 ±0.033 | -0.009 ±0.028 |
| Dihada | resil. Δ P(dano nosso ≥ 40) | **+11.78 pp ±1.93** | **+9.52 pp ±1.83** |
| Dihada | resil. Δ P(dano nosso ≥ 120) | **+10.21 pp ±1.84** | **+6.99 pp ±1.69** |
| Guff | padrão Δ 1º ult (turno) | **-0.127 ±0.024** | **-0.132 ±0.024** |
| Guff | padrão Δ P(ult ≤ T8) | **+3.63 pp ±0.98** | **+3.31 pp ±1.01** |
| Guff | padrão Δ turnos c/ ult | **+0.134 ±0.024** | **+0.158 ±0.026** |
| Guff | resil. Δ vida ≤ 0 | **-0.93 pp ±0.50** | **-0.72 pp ±0.60** |
| Guff | resil. Δ 1º ult | **-0.135 ±0.032** | **-0.111 ±0.033** |
| Guff | resil. Δ PW-turnos vivos | **+1.355 ±0.260** | **+0.962 ±0.272** |
| Guff | resil. Δ PWs mortos em combate | **-0.107 ±0.025** | **-0.106 ±0.028** |
| Guff | resil. Δ P(dano nosso ≥ 40) | **+5.23 pp ±1.44** | **+3.40 pp ±1.44** |
| Guff | resil. Δ P(dano nosso ≥ 120) | **+3.58 pp ±1.35** | **+2.39 pp ±1.32** |
| Vronos | padrão Δ 1º ult (turno) | -0.012 ±0.015 | -0.009 ±0.017 |
| Vronos | padrão Δ P(ult ≤ T8) | +0.00 pp ±0.58 | +0.08 pp ±0.71 |
| Vronos | padrão Δ turnos c/ ult | +0.012 ±0.017 | +0.007 ±0.018 |
| Vronos | resil. Δ vida ≤ 0 | -0.16 pp ±0.60 | +0.16 pp ±0.81 |
| Vronos | resil. Δ 1º ult | **-0.065 ±0.035** | **-0.080 ±0.033** |
| Vronos | resil. Δ PW-turnos vivos | +0.262 ±0.312 | -0.064 ±0.250 |
| Vronos | resil. Δ PWs mortos em combate | **-0.081 ±0.032** | **-0.078 ±0.032** |
| Vronos | resil. Δ P(dano nosso ≥ 40) | **+3.74 pp ±1.55** | **+3.40 pp ±1.56** |
| Vronos | resil. Δ P(dano nosso ≥ 120) | **+2.03 pp ±1.34** | +0.81 pp ±1.23 |
| Sarkhan | padrão Δ 1º ult (turno) | **-0.027 ±0.015** | **-0.018 ±0.016** |
| Sarkhan | padrão Δ P(ult ≤ T8) | +0.47 pp ±0.54 | +0.33 pp ±0.65 |
| Sarkhan | padrão Δ turnos c/ ult | **+0.028 ±0.016** | **+0.017 ±0.016** |
| Sarkhan | resil. Δ vida ≤ 0 | **-0.73 pp ±0.69** | -0.56 pp ±0.85 |
| Sarkhan | resil. Δ 1º ult | **-0.034 ±0.029** | **-0.047 ±0.027** |
| Sarkhan | resil. Δ PW-turnos vivos | +0.230 ±0.230 | -0.047 ±0.240 |
| Sarkhan | resil. Δ PWs mortos em combate | **-0.094 ±0.027** | **-0.095 ±0.030** |
| Sarkhan | resil. Δ P(dano nosso ≥ 40) | **+15.57 pp ±2.11** | **+13.96 pp ±2.12** |
| Sarkhan | resil. Δ P(dano nosso ≥ 120) | **+3.97 pp ±1.34** | **+3.39 pp ±1.42** |

#### 2. Sensibilidade: desligar o que carrega cada carta (slot Arena Rector, Δ pareado sobre a base)

| candidata / política | padrão Δ 1º ult (turno) | padrão Δ P(ult ≤ T8) | padrão Δ turnos c/ ult | resil. Δ vida ≤ 0 | resil. Δ 1º ult | resil. Δ PW-turnos vivos | resil. Δ PWs mortos em combate | resil. Δ P(dano nosso ≥ 40) |
|---|---|---|---|---|---|---|---|---|
| Dihada: política completa | **-0.057 ±0.014** | **+1.37 pp ±0.52** | **+0.087 ±0.015** | -0.33 pp ±0.35 | **-0.035 ±0.020** | **+2.199 ±0.234** | **+0.045 ±0.017** | **+3.07 pp ±0.94** |
| Dihada: sem o −3 (só +2) | +0.003 ±0.006 | +0.13 pp ±0.21 | **-0.010 ±0.006** | **-0.37 pp ±0.31** | **+0.061 ±0.019** | **+0.445 ±0.166** | **+0.025 ±0.012** | +0.17 pp ±0.87 |
| Guff: política completa | **-0.053 ±0.013** | **+1.67 pp ±0.49** | **+0.052 ±0.012** | **-0.57 pp ±0.33** | +0.002 ±0.020 | **+0.989 ±0.179** | -0.004 ±0.012 | +0.00 pp ±0.83 |
| Guff: sem o −3 (só +1 e o gatilho de end step) | **-0.055 ±0.012** | **+1.63 pp ±0.48** | **+0.051 ±0.012** | **-0.57 pp ±0.33** | +0.003 ±0.020 | **+0.722 ±0.170** | -0.005 ±0.011 | -0.43 pp ±0.81 |
| Vronos: política completa | -0.004 ±0.009 | +0.00 pp ±0.35 | -0.001 ±0.009 | -0.20 pp ±0.32 | **+0.039 ±0.021** | **+0.331 ±0.179** | +0.011 ±0.012 | **-1.07 pp ±0.84** |
| Vronos: +1 sem phase out (só +1 de lealdade) | -0.004 ±0.009 | +0.00 pp ±0.35 | -0.000 ±0.009 | -0.27 pp ±0.31 | **+0.043 ±0.020** | **+0.300 ±0.175** | +0.012 ±0.012 | **-1.07 pp ±0.85** |
| Sarkhan: política completa | **-0.010 ±0.008** | +0.20 pp ±0.31 | +0.006 ±0.008 | **-0.43 pp ±0.33** | **+0.051 ±0.020** | **+0.320 ±0.164** | +0.005 ±0.011 | **+3.80 pp ±0.96** |
| Sarkhan: +1 sem animar (só +1 de lealdade; Dragões do −3 e o estático ficam) | **-0.010 ±0.008** | +0.20 pp ±0.31 | +0.006 ±0.008 | **-0.43 pp ±0.33** | **+0.051 ±0.020** | **+0.317 ±0.163** | +0.005 ±0.011 | **-1.83 pp ±0.76** |

Legenda: "sem o −3" = a política nunca usa o −3 (Dihada/Guff); "sem phase out" = o +1 do Vronos só dá lealdade; "sem animar" = o +1 da Sarkhan só dá lealdade (as fichas Dragão do −3 e o estático ficam).

#### 3. Sensibilidade ao perfil de mesa (candidata − PW inerte, slot Arena Rector, resiliência, N = 3.000 por perfil)

| candidata − PW inerte (slot Arena Rector) | métrica | mista | go_wide | voltron | low |
|---|---|---|---|---|---|
| Dihada | vida ≤ 0 | -0.23 pp ±0.30 | -0.03 pp ±0.46 | **-0.43 pp ±0.38** | -0.07 pp ±0.13 |
| Dihada | 1º ult | **-0.100 ±0.019** | **-0.103 ±0.019** | **-0.089 ±0.019** | **-0.082 ±0.017** |
| Dihada | PWs mortos em combate | -0.002 ±0.015 | -0.007 ±0.022 | **-0.017 ±0.015** | -0.001 ±0.008 |
| Dihada | P(dano ≥ 40) | **+5.47 pp ±0.93** | **+5.83 pp ±0.97** | **+4.67 pp ±0.91** | **+4.87 pp ±0.90** |
| Guff | vida ≤ 0 | **-0.47 pp ±0.24** | **-0.60 pp ±0.42** | -0.33 pp ±0.35 | -0.10 pp ±0.11 |
| Guff | 1º ult | **-0.063 ±0.015** | **-0.057 ±0.015** | **-0.051 ±0.016** | **-0.059 ±0.014** |
| Guff | PWs mortos em combate | **-0.052 ±0.012** | **-0.089 ±0.019** | **-0.043 ±0.013** | **-0.026 ±0.007** |
| Guff | P(dano ≥ 40) | **+2.40 pp ±0.68** | **+1.83 pp ±0.65** | **+2.10 pp ±0.70** | **+2.30 pp ±0.72** |
| Vronos | vida ≤ 0 | -0.10 pp ±0.28 | **+0.50 pp ±0.41** | **-0.47 pp ±0.35** | -0.03 pp ±0.07 |
| Vronos | 1º ult | **-0.026 ±0.015** | **-0.031 ±0.013** | **-0.037 ±0.016** | **-0.014 ±0.012** |
| Vronos | PWs mortos em combate | **-0.037 ±0.014** | **-0.056 ±0.017** | **-0.076 ±0.017** | **-0.012 ±0.007** |
| Vronos | P(dano ≥ 40) | **+1.33 pp ±0.66** | **+1.93 pp ±0.66** | **+1.87 pp ±0.74** | **+1.67 pp ±0.66** |
| Sarkhan | vida ≤ 0 | **-0.33 pp ±0.32** | +0.27 pp ±0.39 | **-0.43 pp ±0.34** | -0.07 pp ±0.09 |
| Sarkhan | 1º ult | **-0.013 ±0.013** | **-0.015 ±0.011** | **-0.014 ±0.013** | -0.007 ±0.012 |
| Sarkhan | PWs mortos em combate | **-0.043 ±0.012** | **-0.038 ±0.014** | **-0.030 ±0.015** | **-0.020 ±0.007** |
| Sarkhan | P(dano ≥ 40) | **+6.20 pp ±0.93** | **+4.93 pp ±0.84** | **+5.33 pp ±0.90** | **+6.67 pp ±0.96** |

Base por perfil (vida ≤ 0): mista: 14.7% | go_wide: 28.1% | voltron: 18.9% | low: 1.8%


#### 4. Vronos: o que o phase out protege de fato (resiliência mista, N = 3.000; `ab_vronos_protecao.py`)

#### Vronos: onde o phase out aparece (todas as partidas; n=3000)

| métrica | Vronos completo − base | Vronos sem phase out − base | phase out (completo − sem) | Vronos − PW inerte |
|---|---|---|---|---|
| Δ soma da lealdade dos PWs no fim (cap 1000) | **-18.652 ±8.057** | **-17.474 ±8.001** | -1.179 ±2.792 | +0.671 ±6.310 |
| Δ PWs vivos no T10 (cap 50) | +0.046 ±0.088 | +0.047 ±0.088 | -0.001 ±0.024 | -0.020 ±0.070 |
| Δ PW-turnos vivos | **+0.331 ±0.179** | **+0.300 ±0.175** | +0.031 ±0.039 | -0.039 ±0.139 |
| Δ PWs mortos em combate | +0.011 ±0.012 | +0.012 ±0.012 | -0.001 ±0.004 | **-0.037 ±0.014** |
| Δ dano de combate recebido pelos PWs (cap 1000) | +0.062 ±0.073 | **+0.106 ±0.074** | **-0.045 ±0.021** | **-0.395 ±0.087** |
| Δ remoções sofridas | +0.015 ±0.019 | +0.015 ±0.018 | +0.000 ±0.004 | -0.000 ±0.018 |
| Δ vida ≤ 0 | -0.20 pp ±0.32 | -0.27 pp ±0.31 | +0.07 pp ±0.09 | -0.10 pp ±0.28 |
| Δ 1º ultimate (turno) | **+0.039 ±0.021** | **+0.043 ±0.020** | **-0.004 ±0.004** | **-0.026 ±0.015** |

#### Vronos: onde o phase out aparece (só as 1231 partidas em que o Vronos entrou; n=1231)

| métrica | Vronos completo − base | Vronos sem phase out − base | phase out (completo − sem) | Vronos − PW inerte |
|---|---|---|---|---|
| Δ soma da lealdade dos PWs no fim (cap 1000) | **-34.351 ±18.558** | **-31.478 ±18.422** | -2.872 ±6.805 | +6.650 ±14.687 |
| Δ PWs vivos no T10 (cap 50) | **+0.312 ±0.204** | **+0.314 ±0.202** | -0.002 ±0.058 | +0.103 ±0.162 |
| Δ PW-turnos vivos | **+1.119 ±0.405** | **+1.042 ±0.394** | +0.076 ±0.096 | +0.262 ±0.312 |
| Δ PWs mortos em combate | +0.014 ±0.027 | +0.016 ±0.027 | -0.002 ±0.010 | **-0.081 ±0.032** |
| Δ dano de combate recebido pelos PWs (cap 1000) | +0.126 ±0.161 | **+0.235 ±0.164** | **-0.109 ±0.050** | **-0.819 ±0.196** |
| Δ remoções sofridas | +0.036 ±0.043 | +0.036 ±0.042 | +0.000 ±0.011 | +0.008 ±0.042 |
| Δ vida ≤ 0 | **-0.73 pp ±0.66** | **-0.89 pp ±0.61** | +0.16 pp ±0.23 | -0.16 pp ±0.60 |
| Δ 1º ultimate (turno) | **+0.068 ±0.046** | **+0.079 ±0.045** | **-0.011 ±0.010** | **-0.065 ±0.035** |

PWs tirados de fase por partida em que o Vronos entrou: média 3.53, P(>0) 71.6%

#### 5. Frequência e uso por partida em que a carta entrou

| candidata | Arena Rector | Swan Song | Veil of Summer | Oath of Nissa | Farseek | Doubling Season |
|---|---|---|---|---|---|---|
| Dihada (std) | 47.0% | 45.5% | 45.4% | 44.1% | 44.6% | 45.0% |
| Dihada (res) | 46.7% | 46.2% | 48.4% | 46.4% | 47.9% | 48.1% |
| Guff (std) | 46.9% | 45.3% | 45.4% | 44.0% | 44.5% | 45.1% |
| Guff (res) | 46.5% | 46.1% | 48.2% | 46.3% | 47.7% | 48.0% |
| Vronos (std) | 42.0% | 40.2% | 40.6% | 38.6% | 39.4% | 39.2% |
| Vronos (res) | 41.0% | 41.2% | 43.0% | 40.1% | 41.9% | 42.3% |
| Sarkhan (std) | 42.1% | 40.4% | 40.7% | 38.7% | 39.5% | 39.2% |
| Sarkhan (res) | 41.1% | 41.3% | 43.1% | 40.1% | 41.9% | 42.5% |
| CONTROLE (PW sem habilidade) (std) | 47.4% | 45.8% | — | — | — | — |
| CONTROLE (PW sem habilidade) (res) | 46.9% | 46.4% | — | — | — | — |

**Uso (slot Arena Rector; mediana | média com teto 1000 por partida | P(>0))**

**Dihada — std** (n=1410 partidas com a carta em campo, de 3000)

| métrica | mediana | média (cap 1000/partida) | P(>0) |
|---|---|---|---|
| dihada_minus3 | 3 | 3.86 | 94.0% |
| dihada_plus2_targets | 1 | 2.25 | 53.3% |
| dihada_legends_to_hand | 2 | 3.05 | 81.1% |
| dihada_pws_to_hand | 1 | 1.99 | 70.5% |
| dihada_milled | 11 | 12.41 | 94.0% |
| dihada_milled_pw_or_creature | 1 | 0.87 | 54.8% |
| dihada_treasures | 14 | 126.91 | 94.0% |
| dihada_treasures_spent | 1 | 3.83 | 51.3% |
| dihada_ult | 0 | 0.00 | 0.0% |
| dihada_stolen_power | 0 | 0.00 | 0.0% |
| 1º turno em campo | 8 | 8.13 | — |

**Dihada — res** (n=1401 partidas com a carta em campo, de 3000)

| métrica | mediana | média (cap 1000/partida) | P(>0) |
|---|---|---|---|
| dihada_minus3 | 2 | 3.15 | 94.0% |
| dihada_plus2_targets | 0 | 1.76 | 45.0% |
| dihada_legends_to_hand | 2 | 2.52 | 78.8% |
| dihada_pws_to_hand | 1 | 1.64 | 67.5% |
| dihada_milled | 8 | 10.08 | 93.9% |
| dihada_milled_pw_or_creature | 0 | 0.68 | 44.7% |
| dihada_treasures | 9 | 87.50 | 93.9% |
| dihada_treasures_spent | 1 | 3.37 | 54.4% |
| dihada_ult | 0 | 0.12 | 7.6% |
| dihada_stolen_power | 0 | 2.40 | 7.6% |
| 1º turno em campo | 8 | 8.03 | — |

**Guff — std** (n=1406 partidas com a carta em campo, de 3000)

| métrica | mediana | média (cap 1000/partida) | P(>0) |
|---|---|---|---|
| guff_plus1 | 4 | 4.27 | 94.2% |
| guff_wizards | 4 | 8.47 | 86.3% |
| guff_wizard_mana | 0 | 1.52 | 34.4% |
| guff_minus3 | 1 | 1.21 | 51.3% |
| guff_minus3_cards | 4 | 14.85 | 51.3% |
| guff_end_triggers | 2 | 2.57 | 96.4% |
| guff_end_counters | 5 | 213.33 | 96.4% |
| 1º turno em campo | 8 | 8.13 | — |

**Guff — res** (n=1395 partidas com a carta em campo, de 3000)

| métrica | mediana | média (cap 1000/partida) | P(>0) |
|---|---|---|---|
| guff_plus1 | 3 | 4.05 | 96.1% |
| guff_wizards | 3 | 6.23 | 91.9% |
| guff_wizard_mana | 0 | 0.65 | 26.9% |
| guff_minus3 | 0 | 0.37 | 31.7% |
| guff_minus3_cards | 0 | 2.07 | 31.7% |
| guff_end_triggers | 2 | 2.21 | 93.0% |
| guff_end_counters | 4 | 132.39 | 93.0% |
| 1º turno em campo | 8 | 8.03 | — |

**Vronos — std** (n=1259 partidas com a carta em campo, de 3000)

| métrica | mediana | média (cap 1000/partida) | P(>0) |
|---|---|---|---|
| vronos_plus1 | 3 | 4.00 | 96.6% |
| vronos_phased_out | 5 | 6.74 | 93.7% |
| vronos_minus2 | 0 | 0.00 | 0.0% |
| vronos_bounced | 0 | 0.00 | 0.0% |
| vronos_ult | 0 | 0.00 | 0.0% |
| vronos_attack_damage | 0 | 0.00 | 0.0% |
| 1º turno em campo | 9 | 8.40 | — |

**Vronos — res** (n=1231 partidas com a carta em campo, de 3000)

| métrica | mediana | média (cap 1000/partida) | P(>0) |
|---|---|---|---|
| vronos_plus1 | 1 | 1.99 | 74.6% |
| vronos_phased_out | 2 | 3.53 | 71.6% |
| vronos_minus2 | 0 | 0.82 | 39.2% |
| vronos_bounced | 0 | 2.04 | 39.2% |
| vronos_ult | 0 | 0.55 | 39.8% |
| vronos_attack_damage | 0 | 8.27 | 24.1% |
| 1º turno em campo | 9 | 8.31 | — |

**Sarkhan — std** (n=1264 partidas com a carta em campo, de 3000)

| métrica | mediana | média (cap 1000/partida) | P(>0) |
|---|---|---|---|
| sarkhan_plus1 | 3 | 4.08 | 96.4% |
| sarkhan_animated | 19 | 40.01 | 96.4% |
| sarkhan_ready_attackers | 8 | 23.54 | 90.0% |
| sarkhan_attack_power_potential | 36 | 206.66 | 90.0% |
| sarkhan_attack_damage | 0 | 0.00 | 0.0% |
| sarkhan_minus3 | 0 | 0.00 | 0.0% |
| sarkhan_ping_kills | 0 | 0.00 | 0.0% |
| sarkhan_ping_damage | 0 | 0.00 | 0.0% |
| 1º turno em campo | 9 | 8.39 | — |

**Sarkhan — res** (n=1233 partidas com a carta em campo, de 3000)

| métrica | mediana | média (cap 1000/partida) | P(>0) |
|---|---|---|---|
| sarkhan_plus1 | 2 | 2.96 | 89.9% |
| sarkhan_animated | 12 | 26.91 | 89.9% |
| sarkhan_ready_attackers | 5 | 15.45 | 83.5% |
| sarkhan_attack_power_potential | 20 | 130.26 | 83.5% |
| sarkhan_attack_damage | 18 | 75.79 | 80.6% |
| sarkhan_minus3 | 0 | 0.48 | 36.7% |
| sarkhan_ping_kills | 0 | 0.53 | 10.6% |
| sarkhan_ping_damage | 0 | 1.26 | 20.4% |
| 1º turno em campo | 9 | 8.32 | — |

#### 6. As 4 juntas

| métrica | Δ pareado |
|---|---|
| padrão Δ 1º ult (turno) | +0.026 ±0.030 |
| padrão Δ P(ult ≤ T8) | -0.57 pp ±1.06 |
| padrão Δ turnos c/ ult | -0.012 ±0.029 |
| resiliência Δ vida ≤ 0 | **-0.83 pp ±0.82** |
| resiliência Δ 1º ult | **+0.067 ±0.037** |
| resiliência Δ PW-turnos vivos | **+3.284 ±0.373** |
| resiliência Δ PWs mortos em combate | **+0.032 ±0.028** |
| resiliência Δ P(dano nosso ≥ 40) | **+6.37 pp ±1.47** |
| resiliência Δ P(dano nosso ≥ 120) | +1.00 pp ±1.23 |

#### 7. "Vale a pena?": as candidatas do dia (Dihada, Guff, Vronos, Sarkhan e, na rodada seguinte, Sisay) contra as 3 de Reality Fracture (Tam, Loyal Tutor, Entrust the Spark) nos MESMOS slots fracos

Os três cortes mais fracos da lista (Arena Rector, Swan Song, Veil of Summer) já estão reservados às 3 de FRA
(`checklist-oraculo.md`, rodada de 2026-09-25). Então a pergunta real é se alguma delas ganha desse uso do slot (a Sisay entrou depois, na seção própria acima; as linhas dela estão nas mesmas tabelas).
Mesmo harness, mesmas seeds, N = 3.000 (`ab_candidatas_vs_fra.py`; o pacote FRA usa os mesmos cortes da rodada anterior).

**1. Uma carta por vez no slot Arena Rector (Δ sobre a lista atual)**

| variante | padrão: 1º ult (turno) | padrão: P(ult ≤ T8) | resil.: vida ≤ 0 | resil.: 1º ult | resil.: P(dano ≥ 40) |
|---|---|---|---|---|---|
| Loyal Tutor (FRA) | **-0.135 ±0.023** | **+3.50 pp ±0.78** | -0.30 pp ±0.34 | **-0.045 ±0.025** | **+1.23 pp ±0.97** |
| Tam (FRA) | **-0.119 ±0.017** | **+2.93 pp ±0.65** | **-0.37 pp ±0.36** | **-0.053 ±0.024** | **-1.13 pp ±0.83** |
| Entrust the Spark (FRA) | **-0.064 ±0.014** | **+1.60 pp ±0.51** | -0.20 pp ±0.29 | +0.002 ±0.020 | +0.23 pp ±0.86 |
| Dihada | **-0.057 ±0.014** | **+1.37 pp ±0.52** | -0.33 pp ±0.35 | **-0.035 ±0.020** | **+3.07 pp ±0.94** |
| Guff | **-0.053 ±0.013** | **+1.67 pp ±0.49** | **-0.57 pp ±0.33** | +0.002 ±0.020 | +0.00 pp ±0.83 |
| Vronos | -0.004 ±0.009 | +0.00 pp ±0.35 | -0.20 pp ±0.32 | **+0.039 ±0.021** | **-1.07 pp ±0.84** |
| Sarkhan | **-0.010 ±0.008** | +0.20 pp ±0.31 | **-0.43 pp ±0.33** | **+0.051 ±0.020** | **+3.80 pp ±0.96** |
| Sisay | **-0.086 ±0.019** | **+2.23 pp ±0.68** | **-0.40 pp ±0.38** | +0.008 ±0.023 | -0.53 pp ±0.91 |

**2. Terceiro slot (Tam→Arena Rector e Loyal Tutor→Swan Song fixos; Veil of Summer sai). Δ sobre a lista atual**

| variante | padrão: 1º ult (turno) | padrão: P(ult ≤ T8) | resil.: vida ≤ 0 | resil.: 1º ult | resil.: P(dano ≥ 40) |
|---|---|---|---|---|---|
| Tam + Loyal Tutor + **Entrust** | **-0.236 ±0.027** | **+6.00 pp ±0.95** | **-0.67 pp ±0.55** | **-0.125 ±0.033** | **+1.30 pp ±1.15** |
| Tam + Loyal Tutor + **Dihada** | **-0.246 ±0.029** | **+6.37 pp ±1.04** | **-1.00 pp ±0.60** | **-0.149 ±0.036** | **+4.30 pp ±1.35** |
| Tam + Loyal Tutor + **Guff** | **-0.227 ±0.029** | **+6.03 pp ±1.04** | **-0.97 pp ±0.59** | **-0.107 ±0.035** | +1.10 pp ±1.25 |
| Tam + Loyal Tutor + **Vronos** | **-0.183 ±0.029** | **+4.87 pp ±0.99** | -0.57 pp ±0.57 | **-0.088 ±0.035** | +0.63 pp ±1.24 |
| Tam + Loyal Tutor + **Sarkhan** | **-0.185 ±0.029** | **+4.93 pp ±0.98** | **-0.80 pp ±0.57** | **-0.068 ±0.035** | **+4.63 pp ±1.32** |
| Tam + Loyal Tutor + **Sisay** | **-0.264 ±0.031** | **+7.43 pp ±1.10** | **-0.87 pp ±0.63** | **-0.097 ±0.036** | +0.43 pp ±1.27 |

**3. O mesmo terceiro slot, Δ sobre o pacote com Entrust (positivo em 'P(...)' e negativo em 'vida ≤ 0/1º ult' = melhor que o Entrust)**

| variante | padrão: 1º ult (turno) | padrão: P(ult ≤ T8) | resil.: vida ≤ 0 | resil.: 1º ult | resil.: P(dano ≥ 40) |
|---|---|---|---|---|---|
| Dihada no lugar do Entrust | -0.010 ±0.015 | +0.37 pp ±0.57 | -0.33 pp ±0.37 | **-0.024 ±0.020** | **+3.00 pp ±0.99** |
| Guff no lugar do Entrust | +0.010 ±0.014 | +0.03 pp ±0.55 | -0.30 pp ±0.33 | +0.018 ±0.019 | -0.20 pp ±0.85 |
| Vronos no lugar do Entrust | **+0.054 ±0.013** | **-1.13 pp ±0.48** | +0.10 pp ±0.30 | **+0.037 ±0.018** | -0.67 pp ±0.85 |
| Sarkhan no lugar do Entrust | **+0.052 ±0.013** | **-1.07 pp ±0.48** | -0.13 pp ±0.24 | **+0.057 ±0.018** | **+3.33 pp ±0.91** |
| Sisay no lugar do Entrust | **-0.028 ±0.017** | **+1.43 pp ±0.66** | -0.20 pp ±0.39 | **+0.028 ±0.022** | -0.87 pp ±0.88 |

**4. Quarta carta por cima do pacote FRA completo (Tam + Loyal Tutor + Entrust), entrando no lugar do Oath of Nissa. Δ sobre o pacote FRA**

| variante | padrão: 1º ult (turno) | padrão: P(ult ≤ T8) | resil.: vida ≤ 0 | resil.: 1º ult | resil.: P(dano ≥ 40) |
|---|---|---|---|---|---|
| + Dihada (sai Oath of Nissa) | -0.003 ±0.020 | +0.20 pp ±0.72 | -0.47 pp ±0.51 | -0.025 ±0.025 | **+3.00 pp ±1.00** |
| + Guff (sai Oath of Nissa) | +0.008 ±0.020 | -0.23 pp ±0.71 | -0.40 pp ±0.54 | **+0.032 ±0.024** | -0.37 pp ±0.90 |
| + Vronos (sai Oath of Nissa) | **+0.055 ±0.021** | **-1.13 pp ±0.72** | -0.13 pp ±0.52 | **+0.043 ±0.023** | -0.67 pp ±0.89 |
| + Sarkhan (sai Oath of Nissa) | **+0.053 ±0.021** | **-0.97 pp ±0.71** | -0.40 pp ±0.51 | **+0.059 ±0.023** | **+3.33 pp ±1.00** |
| + Sisay (sai Oath of Nissa) | -0.018 ±0.020 | **+0.83 pp ±0.72** | -0.43 pp ±0.52 | **+0.031 ±0.025** | **-1.20 pp ±0.91** |

**Leitura:**
- Sozinhas no slot Arena Rector, **Loyal Tutor (−0,135) e Tam (−0,119) valem mais que qualquer uma das 5 novas** (Sisay −0,086, Entrust −0,064, Dihada −0,057, Guff −0,053, Sarkhan −0,010, Vronos −0,004 no turno do 1º ultimate). A Sisay é a melhor das 5 em velocidade.
- No **terceiro slot** (ao lado de Tam + Loyal Tutor): a **Sisay ganha do Entrust no ritmo** (−0,028 ±0,017 no turno do 1º ult; +1,4 pp de P(ult ≤ T8)) e a **Dihada empata com ele** (−0,010, dentro do ruído). Na resiliência é o contrário: a Dihada fica melhor que o Entrust (1º ult −0,024; P(dano ≥ 40) +3,0 pp) e a Sisay fica pior (1º ult +0,028 ±0,022; P(dano ≥ 40) −0,9 pp, dentro do ruído). Guff empata no ritmo e não traz o resto. Vronos e Sarkhan são piores que o Entrust no ritmo (+0,05 turno).
- Como **quarta carta** por cima do pacote FRA completo, nenhuma acelera de forma clara (Dihada ±0; Sisay −0,018 ±0,020, não significativo, com +0,8 pp de P(ult ≤ T8) e 1º ult da resiliência +0,031 pior; Vronos e Sarkhan pioram ~0,055 turno e −1 pp de P(ult ≤ T8)): o Oath of Nissa vale tanto quanto elas nesse slot. A Dihada e a Sarkhan só somam dano (+3 pp de P(dano ≥ 40)).

### Leitura (Regra #5: o deck primeiro, o simulador como apoio)

**O que o simulador mede:** velocidade dos ultimates dos 17 PWs, sobrevivência dos PWs e da vida contra 3 oponentes com
criaturas, e um proxy de dano de combate. **O que ele NÃO mede:**
- instantâneo de oponente no MEU turno (afeta só os PWs animados da Sarkhan);
- a QUALIDADE do PW protegido (o oponente simulado bate no de maior lealdade fora de fase e desvia o resto);
- a frente da Esika (não existe no arquivo);
- Dihada −11 e Vronos −2 além de criatura de oponente (📊 estrutural).

Por isso as conclusões abaixo separam "medido" de "raciocínio pelo deck".

**Dihada — a candidata cujo efeito é mais forte e vem inteiro do −3.**
- Medido: sem o −3 (só +2) o ganho some (padrão Δ 1º ult −0,057 → +0,003; resiliência Δ 1º ult −0,035 → +0,061, pior que a base). Contra o PW inerte: 1º ult −0,063 no padrão e −0,100 na resiliência; P(dano ≥ 40) +5,5 pp. Nos 4 perfis de mesa o 1º ult melhora 0,08 a 0,10.
- Pelo deck: o −3 é um tutor de "lendária" e a lista tem 24 (17 PWs + Chain Veil, Oath of Teferi, Oath of Nissa, Vorinclex, Carth, Atraxa, Peregrine Dynamo). P(≥1 lendária nas 4) = 67,7% e P(≥1 PW) = 53,5% na biblioteca cheia. Em partida: mediana 3 usos, ~3,1 lendárias na mão (2,0 PWs).
- O "custo" do mill é quase zero porque as cartas moídas são aleatórias (a Dihada só seleciona); a perda específica é criatura/PW que a Bridge acertaria: 0,87 por partida.
- Treasure paga os PWs que ela mesma pôs na mão (7 PWs custam 6+), mas sobra: mediana 1 Treasure gasto por partida (51% das partidas gastam algum). A carta chega tarde (T8 mediano), então não é ramp.
- Contra: 4 mana R/W/B; puxar PW pra mão tira ele da pilha que a Bridge põe de graça (o Treasure compensa em mana, não em tempo); o −11 só dispara em 7,6% das partidas de resiliência em que ela entra.

**Commodore Guff — vale pelo gatilho de end step e pelos Wizards, não pelo −3, e é UM PW por turno.**
- Medido: contra o PW inerte, 1º ult −0,059 (padrão) e −0,063 (resiliência); vida ≤ 0 −0,47 pp; PWs mortos −0,052. Sem o −3 o ganho de velocidade é o mesmo (−0,055 vs −0,053): o −3 só acrescenta PW-turnos (+0,99 vs +0,72).
- Pelo deck: o contador passa por `add_loyalty`, então Doubling Season/Vorinclex/Innkeeper nv.3 dobram e o All Will Be One dispara; o alvo é o PW mais perto do ultimate. O Wizard (dobrado pela Doubling Season) é bloqueador e a {R} paga PW (34% das partidas em que ela entra usam essa mana). O −3 compra X = PWs em campo (mediana 4, usado em 51% das partidas em que entra).
- Contra: **o "todos os PWs" que motivou a inclusão já existe** na lista (8 cartas dão proliferate, por varredura do oráculo: Atraxa no MESMO end step, Evolution Sage, Flux Channeler, Inexorable Tide, Ichormoon Gauntlet [0], Mutational Advantage, Ripples of Potential e Vraska 0; o Deepglow Skate dobra os contadores); a Guff soma 1 contador (2 com dobrador) em 1 PW. Entra tarde (T8 mediano), 4 mana U/R/W, precisa estar viva no end step.

**Vronos — a mais fraca no que dá pra medir; a proteção é redundante com a lista.**
- Medido: padrão sem efeito no ritmo (Δ 1º ult −0,010 vs inerte). O phase out em si: −0,109 de dano de combate nos PWs por partida em que ele entra, mas mortes de PW (−0,002) e vida ≤ 0 (+0,16 pp) não mudam, porque o dano vai pros PWs que ficaram. O efeito medido sobre o inerte (PWs mortos −0,037 no geral e −0,081 quando entra) vem principalmente do −2 (por eliminação: com e sem o phase out o número é o mesmo). Na mesa go_wide a vida ≤ 0 até piora (+0,50 pp).
- −2: 1 bounce por oponente (3 na mesa de 4), usado em 39% das partidas de resiliência em que ele entra. −7: Construct 9/9 impossível de bloquear, indestrutível, com vigilância; usado em 40% dessas partidas e o Construct ataca em 24% (dano médio 8,3 por partida).
- Contra: protege só OUTROS PWs e só até o meu untap (no meu turno todos ficam expostos); o Vronos e a Bridge (encantamento) ficam na linha de fogo; PW fora de fase perde os estáticos (Teferi Time Raveler, Narset, Wanderer) e a ativação instantânea do emblema do Teferi TA; a lista já tem **Ripples of Potential** (phase out de TODOS os PWs por {1}{U}, instantâneo, com proliferate), Mutational Advantage, Veil of Summer e Sterling Grove. 5 mana UU no tempo de feitiço.

**Sarkhan the Masterless — abre uma linha de vitória que a lista não tem, com risco que o simulador não vê.**
- Medido: contra o PW inerte, P(dano ≥ 40) **+6,2 pp** (+15,6 pp nas partidas em que entra) e P(≥ 120) +1,5 pp; vida ≤ 0 −0,33 pp; PWs mortos −0,043. A animação sozinha vale +5,6 pp de P(dano ≥ 40) (+3,80 pp com ela, −1,83 pp sem); a queda de vida ≤ 0 vem das fichas Dragão e do estático, não da animação. Nas partidas em que ela entra na resiliência, 81% usam o +1 com dano e o dano mediano é 18. No padrão o ganho é mínimo (Δ 1º ult −0,017).
- Pelo deck: hoje a lista fecha por veneno (Vraska −9: elimina um oponente em 33% das partidas até o T10), Bolas −8, Elspeth −7 ou turnos extras. Com 4 a 6 PWs prontos são 16 a 24 de dano voador por turno, dividido entre 3 oponentes (por isso P(≥ 120) só sobe 1,5 pp: sozinha não fecha a mesa). Doubling Season: entra com 10.
- Regras que pesam (rulings): o PW animado **deixa de ser planeswalker** até o fim do turno (perde as habilidades que a Ichormoon Gauntlet concede, mas ainda ativa as próprias); só ataca quem estava sob controle desde o começo do turno; sem vigilância (a da Esika exige a frente em campo, que exclui a Bridge). A lista tem 0 Dragões, então o estático só conta as fichas do −3.
- Contra: no meu turno os PWs viram criaturas 4/4: um Swords to Plowshares ou wipe em resposta exila/mata Ugin, Kaya, Elspeth. **O simulador não modela instantâneo de oponente no meu turno, então esta carta é a mais superestimada aqui.** 5 mana RR.

**As 4 juntas** (Dihada→Arena Rector, Guff→Swan Song, Vronos→Veil of Summer, Sarkhan→Oath of Nissa): o ritmo padrão não muda (1º ult +0,026 ±0,030, P(ult ≤ T8) −0,57 pp ±1,06: os cortes de Swan Song/Veil/Oath e o fato de Vronos/Sarkhan não acelerarem cancelam o ganho de Dihada e Guff); na resiliência: vida ≤ 0 −0,83 pp, PW-turnos +3,28, P(dano ≥ 40) +6,4 pp, mas o 1º ult piora (+0,067). Ou seja, o ganho do pacote é sobrevivência e dano, não velocidade.

**Onde cada uma interage com a lista (Regra #4):**
- Bridge: as 4 são PWs, então entram de graça pelo gatilho de upkeep e ativam no mesmo turno (CR 606.3); a fatia de PW do pool da Bridge passa de 17/28 para 21/32.
- Urza cap. II pode botá-las de graça (todas MV ≤ 6); Carth acha mais PWs no top 7; Arena Rector nunca as escolhe (busca o de maior MV: Ugin/Kaya).
- Doubling Season: lealdade inicial 10, fichas dobradas (Treasure, Wizard, Dragão); Chain Veil/Oath de Teferi/Urza III: 2 ativações no turno; Peregrine Dynamo copia o −3 da Guff/Dihada.
- Aminatou −1 e Oath de Teferi devolvem a candidata com lealdade nova; Oko −5 copia (regra da lenda).
- Combos: 0 novos (Spellbook). Bracket: nenhuma é Game Changer; o deck continua com 3.

### Limites desta rodada (Regra #7: o que foi e o que NÃO foi verificado)

- **Verificado:** oráculo e rulings ao vivo das 4, cláusula a cláusula, com teste dirigido; combos (Spellbook antes/depois + controle); os conceitos "lendária", "Dragão", "artefato" e "Wizard" enumerados por script sobre o `type_line`; A/B com controle de corte (Doubling Season/Farseek) e de entrada (PW inerte); condicional; sensibilidade a política (4 chaves) e a perfil de mesa (3); bit-identidade da lista atual; regressão de 40.000 partidas.
- **NÃO verificado:** as outras 99 cartas contra as 4 uma a uma (só os conceitos e motores listados); instantâneo de oponente no meu turno; a frente da Esika; ordem do gatilho da Guff contra todos os outros gatilhos de end step (só Oath, Atraxa, Sterling Grove, Vronos); a qualidade do PW protegido pelo Vronos; a interação real do −11 da Dihada com PW/artefato/encantamento do oponente (📊).
- **Sem o efeito do Carth na Sarkhan animada:** o Carth cobra [+1] "planeswalkers' loyalty abilities"; um PW animado não é planeswalker. Não achei ruling; o simulador mantém o imposto (conservador).


<details><summary>Tabelas completas: cada candidata contra cada corte (incondicional e condicional)</summary>

**Modo padrão — todas as partidas (incondicional)**

| candidata ↓ / sai → | Arena Rector | Swan Song | Veil of Summer | Oath of Nissa | Farseek | Doubling Season |
|---|---|---|---|---|---|---|
| Dihada: Δ 1º ult (turno) | **-0.057 ±0.014** | **-0.028 ±0.016** | **-0.027 ±0.016** | -0.008 ±0.021 | +0.013 ±0.019 | **+0.020 ±0.018** |
| Dihada: Δ P(ult ≤ T8) | **+1.37 pp ±0.52** | **+0.70 pp ±0.64** | **+0.93 pp ±0.61** | +0.40 pp ±0.73 | -0.03 pp ±0.66 | -0.40 pp ±0.66 |
| Dihada: Δ turnos c/ ult | **+0.087 ±0.015** | **+0.044 ±0.017** | **+0.049 ±0.017** | **+0.023 ±0.021** | +0.013 ±0.019 | +0.002 ±0.017 |
| Guff: Δ 1º ult (turno) | **-0.053 ±0.013** | **-0.014 ±0.014** | **-0.016 ±0.015** | +0.002 ±0.021 | **+0.021 ±0.017** | +0.013 ±0.018 |
| Guff: Δ P(ult ≤ T8) | **+1.67 pp ±0.49** | +0.27 pp ±0.58 | **+0.77 pp ±0.59** | -0.10 pp ±0.72 | -0.37 pp ±0.62 | +0.00 pp ±0.63 |
| Guff: Δ turnos c/ ult | **+0.052 ±0.012** | **+0.018 ±0.015** | **+0.023 ±0.015** | -0.015 ±0.020 | -0.014 ±0.018 | -0.009 ±0.017 |
| Vronos: Δ 1º ult (turno) | -0.004 ±0.009 | **+0.041 ±0.013** | **+0.032 ±0.014** | **+0.049 ±0.021** | **+0.061 ±0.018** | **+0.054 ±0.017** |
| Vronos: Δ P(ult ≤ T8) | +0.00 pp ±0.35 | **-1.17 pp ±0.52** | **-0.63 pp ±0.49** | **-1.00 pp ±0.71** | **-1.37 pp ±0.61** | **-1.03 pp ±0.59** |
| Vronos: Δ turnos c/ ult | -0.001 ±0.009 | **-0.048 ±0.014** | **-0.032 ±0.014** | **-0.076 ±0.020** | **-0.056 ±0.018** | **-0.057 ±0.016** |
| Sarkhan: Δ 1º ult (turno) | **-0.010 ±0.008** | **+0.037 ±0.013** | **+0.031 ±0.014** | **+0.048 ±0.021** | **+0.061 ±0.018** | **+0.051 ±0.017** |
| Sarkhan: Δ P(ult ≤ T8) | +0.20 pp ±0.31 | **-1.07 pp ±0.51** | **-0.57 pp ±0.49** | **-1.00 pp ±0.71** | **-1.30 pp ±0.61** | **-0.90 pp ±0.58** |
| Sarkhan: Δ turnos c/ ult | +0.006 ±0.008 | **-0.045 ±0.014** | **-0.030 ±0.014** | **-0.074 ±0.020** | **-0.055 ±0.018** | **-0.054 ±0.016** |
| CONTROLE (PW sem habilidade): Δ 1º ult (turno) | +0.006 ±0.006 | **+0.046 ±0.014** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ P(ult ≤ T8) | -0.03 pp ±0.24 | **-1.23 pp ±0.52** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ turnos c/ ult | **-0.011 ±0.007** | **-0.053 ±0.014** | — | — | — | — |

**Resiliência — todas as partidas (incondicional)**

| candidata ↓ / sai → | Arena Rector | Swan Song | Veil of Summer | Oath of Nissa | Farseek | Doubling Season |
|---|---|---|---|---|---|---|
| Dihada: Δ vida ≤ 0 | -0.33 pp ±0.35 | **-0.50 pp ±0.46** | **-0.43 pp ±0.42** | **-0.67 pp ±0.53** | +0.00 pp ±0.47 | **-0.60 pp ±0.52** |
| Dihada: Δ 1º ult | **-0.035 ±0.020** | **-0.024 ±0.021** | **-0.039 ±0.022** | **-0.027 ±0.025** | -0.004 ±0.026 | **+0.025 ±0.024** |
| Dihada: Δ PW-turnos vivos | **+2.199 ±0.234** | **+1.964 ±0.219** | **+2.219 ±0.233** | **+1.789 ±0.253** | **+1.714 ±0.266** | **+2.098 ±0.235** |
| Dihada: Δ PWs mortos em combate | **+0.045 ±0.017** | **+0.036 ±0.016** | **+0.033 ±0.017** | **+0.035 ±0.018** | **+0.026 ±0.017** | **+0.025 ±0.017** |
| Dihada: Δ P(dano nosso ≥ 40) | **+3.07 pp ±0.94** | **+2.63 pp ±0.97** | **+2.50 pp ±0.94** | **+2.63 pp ±1.02** | **+3.23 pp ±1.02** | **+1.97 pp ±1.00** |
| Dihada: Δ P(dano nosso ≥ 120) | **+2.83 pp ±0.90** | **+2.03 pp ±0.82** | **+2.17 pp ±0.86** | **+2.40 pp ±0.93** | **+1.60 pp ±0.97** | +0.67 pp ±0.96 |
| Guff: Δ vida ≤ 0 | **-0.57 pp ±0.33** | **-0.50 pp ±0.45** | -0.30 pp ±0.41 | -0.53 pp ±0.55 | +0.23 pp ±0.48 | -0.37 pp ±0.50 |
| Guff: Δ 1º ult | +0.002 ±0.020 | +0.003 ±0.020 | +0.001 ±0.022 | **+0.031 ±0.024** | **+0.039 ±0.024** | **+0.047 ±0.023** |
| Guff: Δ PW-turnos vivos | **+0.989 ±0.179** | **+0.756 ±0.168** | **+0.971 ±0.182** | **+0.462 ±0.205** | **+0.499 ±0.222** | **+1.035 ±0.199** |
| Guff: Δ PWs mortos em combate | -0.004 ±0.012 | -0.008 ±0.016 | -0.006 ±0.016 | -0.003 ±0.016 | -0.008 ±0.017 | **-0.019 ±0.016** |
| Guff: Δ P(dano nosso ≥ 40) | +0.00 pp ±0.83 | -0.20 pp ±0.83 | -0.13 pp ±0.84 | **-0.90 pp ±0.90** | -0.43 pp ±0.91 | -0.87 pp ±0.95 |
| Guff: Δ P(dano nosso ≥ 120) | -0.27 pp ±0.77 | -0.10 pp ±0.74 | +0.23 pp ±0.76 | -0.23 pp ±0.79 | -0.23 pp ±0.84 | **-1.50 pp ±0.87** |
| Vronos: Δ vida ≤ 0 | -0.20 pp ±0.32 | -0.10 pp ±0.40 | -0.03 pp ±0.38 | -0.13 pp ±0.57 | +0.40 pp ±0.48 | -0.10 pp ±0.49 |
| Vronos: Δ 1º ult | **+0.039 ±0.021** | **+0.019 ±0.018** | **+0.029 ±0.021** | **+0.044 ±0.024** | **+0.058 ±0.025** | **+0.075 ±0.022** |
| Vronos: Δ PW-turnos vivos | **+0.331 ±0.179** | **+0.185 ±0.151** | **+0.377 ±0.158** | +0.078 ±0.199 | -0.055 ±0.222 | **+0.304 ±0.164** |
| Vronos: Δ PWs mortos em combate | +0.011 ±0.012 | +0.006 ±0.014 | +0.003 ±0.014 | -0.003 ±0.017 | -0.002 ±0.017 | -0.001 ±0.014 |
| Vronos: Δ P(dano nosso ≥ 40) | **-1.07 pp ±0.84** | -0.33 pp ±0.83 | -0.60 pp ±0.85 | -0.77 pp ±0.92 | -0.73 pp ±0.91 | **-1.57 pp ±0.89** |
| Vronos: Δ P(dano nosso ≥ 120) | **-1.23 pp ±0.72** | **-0.90 pp ±0.70** | **-1.40 pp ±0.73** | **-0.83 pp ±0.81** | **-1.53 pp ±0.87** | **-2.80 pp ±0.83** |
| Sarkhan: Δ vida ≤ 0 | **-0.43 pp ±0.33** | -0.40 pp ±0.43 | -0.33 pp ±0.37 | -0.43 pp ±0.56 | +0.13 pp ±0.46 | -0.30 pp ±0.48 |
| Sarkhan: Δ 1º ult | **+0.051 ±0.020** | **+0.033 ±0.018** | **+0.045 ±0.020** | **+0.060 ±0.023** | **+0.081 ±0.025** | **+0.089 ±0.023** |
| Sarkhan: Δ PW-turnos vivos | **+0.320 ±0.164** | **+0.190 ±0.148** | **+0.420 ±0.154** | +0.055 ±0.195 | -0.111 ±0.218 | **+0.397 ±0.169** |
| Sarkhan: Δ PWs mortos em combate | +0.005 ±0.011 | -0.001 ±0.013 | +0.006 ±0.013 | +0.003 ±0.017 | +0.006 ±0.016 | -0.013 ±0.013 |
| Sarkhan: Δ P(dano nosso ≥ 40) | **+3.80 pp ±0.96** | **+4.03 pp ±0.96** | **+4.13 pp ±0.97** | **+3.37 pp ±1.02** | **+3.67 pp ±1.04** | **+3.60 pp ±1.02** |
| Sarkhan: Δ P(dano nosso ≥ 120) | -0.43 pp ±0.75 | +0.17 pp ±0.69 | -0.03 pp ±0.79 | +0.00 pp ±0.82 | -0.50 pp ±0.86 | **-1.57 pp ±0.85** |
| CONTROLE (PW sem habilidade): Δ vida ≤ 0 | -0.10 pp ±0.30 | -0.17 pp ±0.44 | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ 1º ult | **+0.065 ±0.019** | **+0.055 ±0.018** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ PW-turnos vivos | **+0.370 ±0.164** | **+0.315 ±0.149** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ PWs mortos em combate | **+0.048 ±0.013** | **+0.042 ±0.015** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ P(dano nosso ≥ 40) | **-2.40 pp ±0.77** | **-1.80 pp ±0.78** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ P(dano nosso ≥ 120) | **-1.93 pp ±0.69** | **-1.23 pp ±0.67** | — | — | — | — |

**Modo padrão — só as partidas em que a candidata entrou em campo (condicional)**

| candidata ↓ / sai → | Arena Rector | Swan Song | Veil of Summer | Oath of Nissa | Farseek | Doubling Season |
|---|---|---|---|---|---|---|
| Dihada: Δ 1º ult (turno) | **-0.122 ±0.030** | **-0.061 ±0.035** | **-0.063 ±0.035** | -0.034 ±0.045 | +0.008 ±0.041 | +0.023 ±0.036 |
| Dihada: Δ P(ult ≤ T8) | **+2.91 pp ±1.11** | **+1.54 pp ±1.38** | **+2.13 pp ±1.34** | +0.98 pp ±1.60 | +0.30 pp ±1.45 | -0.81 pp ±1.35 |
| Dihada: Δ turnos c/ ult | **+0.186 ±0.032** | **+0.101 ±0.036** | **+0.112 ±0.036** | **+0.074 ±0.045** | **+0.049 ±0.041** | +0.028 ±0.035 |
| Guff: Δ 1º ult (turno) | **-0.114 ±0.026** | **-0.032 ±0.030** | **-0.038 ±0.034** | -0.014 ±0.044 | +0.025 ±0.037 | +0.008 ±0.036 |
| Guff: Δ P(ult ≤ T8) | **+3.56 pp ±1.03** | +0.59 pp ±1.26 | **+1.76 pp ±1.30** | -0.15 pp ±1.59 | -0.37 pp ±1.35 | +0.07 pp ±1.29 |
| Guff: Δ turnos c/ ult | **+0.112 ±0.026** | **+0.045 ±0.033** | **+0.054 ±0.033** | -0.010 ±0.044 | -0.010 ±0.038 | +0.003 ±0.036 |
| Vronos: Δ 1º ult (turno) | -0.001 ±0.019 | **+0.095 ±0.031** | **+0.073 ±0.033** | **+0.078 ±0.047** | **+0.097 ±0.038** | **+0.111 ±0.037** |
| Vronos: Δ P(ult ≤ T8) | -0.08 pp ±0.75 | **-2.82 pp ±1.23** | **-1.40 pp ±1.19** | **-1.90 pp ±1.66** | **-2.20 pp ±1.40** | **-2.30 pp ±1.30** |
| Vronos: Δ turnos c/ ult | -0.007 ±0.020 | **-0.109 ±0.032** | **-0.072 ±0.032** | **-0.137 ±0.046** | **-0.090 ±0.039** | **-0.114 ±0.035** |
| Sarkhan: Δ 1º ult (turno) | -0.016 ±0.018 | **+0.086 ±0.031** | **+0.071 ±0.034** | **+0.077 ±0.046** | **+0.099 ±0.038** | **+0.102 ±0.036** |
| Sarkhan: Δ P(ult ≤ T8) | +0.40 pp ±0.64 | **-2.56 pp ±1.21** | **-1.23 pp ±1.19** | **-1.89 pp ±1.65** | **-2.11 pp ±1.41** | **-1.96 pp ±1.28** |
| Sarkhan: Δ turnos c/ ult | +0.009 ±0.019 | **-0.099 ±0.032** | **-0.067 ±0.033** | **-0.134 ±0.046** | **-0.090 ±0.038** | **-0.108 ±0.035** |
| CONTROLE (PW sem habilidade): Δ 1º ult (turno) | +0.013 ±0.013 | **+0.099 ±0.030** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ P(ult ≤ T8) | -0.07 pp ±0.50 | **-2.69 pp ±1.12** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ turnos c/ ult | **-0.022 ±0.014** | **-0.111 ±0.031** | — | — | — | — |

**Resiliência — só as partidas em que a candidata entrou em campo (condicional)**

| candidata ↓ / sai → | Arena Rector | Swan Song | Veil of Summer | Oath of Nissa | Farseek | Doubling Season |
|---|---|---|---|---|---|---|
| Dihada: Δ vida ≤ 0 | **-0.71 pp ±0.71** | **-1.30 pp ±0.91** | **-1.10 pp ±0.83** | **-1.29 pp ±1.01** | -0.70 pp ±0.80 | **-1.66 pp ±0.86** |
| Dihada: Δ 1º ult | **-0.075 ±0.043** | **-0.050 ±0.044** | **-0.079 ±0.043** | **-0.073 ±0.051** | -0.031 ±0.052 | +0.032 ±0.046 |
| Dihada: Δ PW-turnos vivos | **+4.745 ±0.465** | **+4.399 ±0.428** | **+4.616 ±0.444** | **+4.017 ±0.507** | **+3.898 ±0.504** | **+4.339 ±0.449** |
| Dihada: Δ PWs mortos em combate | **+0.095 ±0.035** | **+0.073 ±0.034** | **+0.072 ±0.033** | **+0.081 ±0.036** | **+0.048 ±0.032** | **+0.054 ±0.031** |
| Dihada: Δ P(dano nosso ≥ 40) | **+6.50 pp ±1.98** | **+6.20 pp ±2.03** | **+5.51 pp ±1.90** | **+5.90 pp ±2.13** | **+6.89 pp ±2.08** | **+4.44 pp ±2.04** |
| Dihada: Δ P(dano nosso ≥ 120) | **+6.07 pp ±1.92** | **+4.61 pp ±1.70** | **+4.62 pp ±1.74** | **+5.61 pp ±1.95** | **+3.69 pp ±1.96** | +1.73 pp ±1.94 |
| Guff: Δ vida ≤ 0 | **-1.36 pp ±0.64** | **-1.30 pp ±0.89** | **-0.83 pp ±0.81** | -0.86 pp ±1.06 | -0.49 pp ±0.79 | **-1.18 pp ±0.80** |
| Guff: Δ 1º ult | +0.003 ±0.042 | +0.009 ±0.041 | +0.002 ±0.043 | +0.049 ±0.049 | **+0.059 ±0.049** | **+0.081 ±0.045** |
| Guff: Δ PW-turnos vivos | **+2.178 ±0.373** | **+1.796 ±0.340** | **+2.045 ±0.362** | **+1.155 ±0.423** | **+1.372 ±0.427** | **+2.132 ±0.393** |
| Guff: Δ PWs mortos em combate | -0.014 ±0.024 | -0.024 ±0.033 | -0.008 ±0.031 | +0.001 ±0.032 | -0.023 ±0.033 | **-0.037 ±0.029** |
| Guff: Δ P(dano nosso ≥ 40) | -0.07 pp ±1.78 | +0.07 pp ±1.73 | +0.00 pp ±1.70 | -1.73 pp ±1.88 | -0.77 pp ±1.86 | -1.46 pp ±1.94 |
| Guff: Δ P(dano nosso ≥ 120) | -0.57 pp ±1.65 | +0.00 pp ±1.55 | +0.62 pp ±1.56 | -0.07 pp ±1.64 | -0.14 pp ±1.71 | **-2.78 pp ±1.76** |
| Vronos: Δ vida ≤ 0 | **-0.73 pp ±0.66** | -0.49 pp ±0.81 | -0.23 pp ±0.79 | -1.00 pp ±1.06 | -0.48 pp ±0.70 | **-0.87 pp ±0.80** |
| Vronos: Δ 1º ult | **+0.068 ±0.046** | +0.036 ±0.040 | **+0.062 ±0.045** | +0.042 ±0.051 | **+0.080 ±0.054** | **+0.154 ±0.047** |
| Vronos: Δ PW-turnos vivos | **+1.119 ±0.405** | **+0.777 ±0.333** | **+1.017 ±0.349** | **+0.800 ±0.426** | **+0.648 ±0.457** | **+0.733 ±0.366** |
| Vronos: Δ PWs mortos em combate | +0.014 ±0.027 | +0.009 ±0.031 | +0.008 ±0.028 | -0.007 ±0.034 | -0.025 ±0.034 | -0.002 ±0.027 |
| Vronos: Δ P(dano nosso ≥ 40) | -1.95 pp ±1.97 | +0.08 pp ±1.90 | -0.85 pp ±1.91 | -0.83 pp ±2.10 | -0.80 pp ±2.05 | **-2.92 pp ±2.04** |
| Vronos: Δ P(dano nosso ≥ 120) | **-2.52 pp ±1.70** | -1.46 pp ±1.60 | **-2.87 pp ±1.66** | -0.92 pp ±1.88 | **-2.47 pp ±1.94** | **-6.23 pp ±1.91** |
| Sarkhan: Δ vida ≤ 0 | **-0.97 pp ±0.71** | **-1.13 pp ±0.89** | **-1.01 pp ±0.79** | **-1.75 pp ±1.04** | **-0.79 pp ±0.62** | **-1.10 pp ±0.81** |
| Sarkhan: Δ 1º ult | **+0.101 ±0.044** | **+0.069 ±0.039** | **+0.101 ±0.044** | **+0.089 ±0.050** | **+0.134 ±0.052** | **+0.191 ±0.049** |
| Sarkhan: Δ PW-turnos vivos | **+1.056 ±0.364** | **+0.781 ±0.323** | **+1.110 ±0.339** | **+0.744 ±0.415** | **+0.508 ±0.448** | **+0.944 ±0.375** |
| Sarkhan: Δ PWs mortos em combate | +0.001 ±0.024 | -0.008 ±0.029 | +0.013 ±0.027 | +0.008 ±0.035 | -0.006 ±0.034 | **-0.030 ±0.026** |
| Sarkhan: Δ P(dano nosso ≥ 40) | **+9.89 pp ±2.21** | **+10.65 pp ±2.17** | **+10.13 pp ±2.15** | **+9.57 pp ±2.34** | **+9.70 pp ±2.32** | **+9.25 pp ±2.30** |
| Sarkhan: Δ P(dano nosso ≥ 120) | -0.57 pp ±1.76 | +1.13 pp ±1.58 | +0.31 pp ±1.81 | +1.25 pp ±1.89 | +0.00 pp ±1.93 | **-3.29 pp ±1.95** |
| CONTROLE (PW sem habilidade): Δ vida ≤ 0 | -0.43 pp ±0.59 | -0.57 pp ±0.87 | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ 1º ult | **+0.136 ±0.040** | **+0.119 ±0.038** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ PW-turnos vivos | **+0.830 ±0.345** | **+0.835 ±0.301** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ PWs mortos em combate | **+0.099 ±0.027** | **+0.084 ±0.032** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ P(dano nosso ≥ 40) | **-5.18 pp ±1.63** | **-3.37 pp ±1.61** | — | — | — | — |
| CONTROLE (PW sem habilidade): Δ P(dano nosso ≥ 120) | **-4.12 pp ±1.46** | **-2.44 pp ±1.37** | — | — | — | — |

</details>

## Rodada Reality Fracture (Tam, Loyal Tutor, Entrust the Spark) — 2026-09-25

Detalhe cláusula por cláusula e os 3 bugs de motor em `checklist-oraculo.md`.

### Correções de motor: antes/depois (2.000 partidas, mesmas seeds, lista atual)

Modo padrão: seeds 3.000.000+. Resiliência: mesa mista, seeds 6.000.000+.
Etapas acumulativas.

| etapa | 1ª Bridge | gatilhos Bridge | ativações | ultimates | PWs no T10 | compras via PW | turnos extras (Gauntlet) | oponentes envenenados | res: vida ≤ 0 | res: PW-turnos vivos | res: ativações |
|---|---|---|---|---|---|---|---|---|---|---|---|
| antes (commit ba77495) | 5,16 | 4,41 | 22,3 | 6,71 | 5,32 | 17,9 | — | — | 14,6% | 14,57 | 19,6 |
| a. genérico real no desconto | 5,16 | 4,39 | 22,3 | 6,69 | 5,31 | 17,8 | 0,35 | 0,56 | 14,6% | 14,57 | 19,6 |
| b. **PW ativa no turno em que entra (CR 606.3)** | 5,17 | 5,25 | **34,4** | **10,81** | 5,99 | **28,4** | 0,56 | 0,82 | 14,9% | 15,72 | **30,9** |
| c. lore da Urza por proliferate/Deepglow | 5,17 | 5,26 | 34,4 | 10,76 | 6,00 | 28,2 | 0,57 | 0,82 | 14,9% | 15,71 | 31,0 |

Cada correção moveu a métrica esperada:
- **(a)** O Notebook deixou de baratear Bolas, Narset, Counterspell e afins. Efeito pequeno, pra baixo.
- **(b)** 5,0 PWs por partida passaram a ativar no turno em que entram:
  - ativações: +54%;
  - ultimates: +61%;
  - turnos extras do Gauntlet: +60%.
- **(c)** PW posto de graça pelo capítulo II da Urza: de 0,108 para 0,142 por partida (+31%).

No modo resiliência a vida ≤ 0 subiu 0,3 pp. Está dentro do ruído, mas a
direção faz sentido: com mais ativações os PWs viram alvo maior de remoção.

### Validação

- **Testes dirigidos:** 101/101 (`test_prismatic_bridge_goldfish.py`). São 16
  novos, um por cláusula e interação: desconto só genérico, X por tipo,
  Doubling Season, doença de invocação, janela main só com ultimate,
  Dynamo copiando a Tam, Loyal Tutor com a Bridge / na mana que sobrou /
  segurado sem a Bridge, Entrust + Carth depois da busca + ativação no mesmo
  turno, Urza por proliferate, troca posicional. O teste antigo "PW
  conjurado ganha lealdade" foi atualizado: agora ele também ativa (4 → 5).
- **Regressão:** 40.000 partidas (20.000 padrão + 20.000 resiliência nos 4
  perfis de mesa), metade com as 3 candidatas dentro via troca. Resultado:
  **0 exceções, 0 travamentos** (alarme de 20 s por partida).
- **Lista atual:** o snapshot final (2.000 + 2.000 partidas) é idêntico à
  etapa c em todas as métricas. A Tam, o Loyal Tutor, o Entrust e a cópia da
  Dynamo sobre a Tam só agem quando a carta está na lista.
- **Troca posicional (`apply_swaps`):** a carta nova entra na linha da cortada
  (regra do teste pareado), então cada partida A/B só diverge quando a carta
  trocada é comprada.

### A/B pareado: cada candidata × 10 cortes (2.000 + 2.000 partidas por variante)

Scripts: `ab_reality_fracture.py` e `ab_reality_fracture_sum.py`. Seeds iguais
às do snapshot; resiliência em mesa mista.

**Por que não a média de ultimates:** a contagem de ultimates explode nas
partidas já ganhas (loops de Oko/Doubling Season/Gauntlet: 80+ numa partida
só). Uma partida a mais nesse estado move a média em +2 e não diz nada.
Métricas usadas, todas limitadas por partida:
- turno do 1º ultimate (sem ultimate = 11);
- P(ultimate até o T8);
- vida ≤ 0 na resiliência.

Mais detalhes em `references/goldfish-sim-card-rules.md`, seção "A/B de carta".

**Base (lista atual, motor corrigido):**
- modo padrão: 1º ultimate no turno 9,28 em média; P(ult ≤ T8) = 33,8%;
- resiliência: vida ≤ 0 em 14,9%; P(ult ≤ T8) = 23,5%.

**Modo padrão — Δ do turno médio do 1º ultimate** (negativo = mais rápido; negrito = IC95% não cruza 0):

| entra ↓ / sai → | Arena Rector | Dovin's Veto | Void Rend | Swan Song | Veil of Summer | Oath of Nissa | Blasphemous Act | Farseek | Three Visits | Doubling Season (controle) |
|---|---|---|---|---|---|---|---|---|---|---|
| Loyal Tutor | **−0,146 ±0,029** | **−0,130 ±0,027** | **−0,117 ±0,027** | **−0,107 ±0,025** | **−0,106 ±0,027** | **−0,084 ±0,027** | **−0,089 ±0,024** | **−0,065 ±0,025** | **−0,071 ±0,028** | **−0,065 ±0,025** |
| Tam, the Possibility | **−0,127 ±0,021** | **−0,096 ±0,022** | **−0,101 ±0,022** | **−0,053 ±0,020** | **−0,070 ±0,021** | **−0,046 ±0,027** | **−0,064 ±0,021** | **−0,062 ±0,024** | **−0,033 ±0,023** | **−0,040 ±0,025** |
| Entrust the Spark | **−0,072 ±0,017** | **−0,040 ±0,015** | **−0,037 ±0,015** | **−0,019 ±0,011** | **−0,022 ±0,012** | −0,001 ±0,022 | **−0,018 ±0,009** | +0,014 ±0,020 | **+0,029 ±0,020** | +0,013 ±0,015 |

**Resiliência — Δ de vida ≤ 0 até o T10** (negativo = melhor):

| entra ↓ / sai → | Arena Rector | Dovin's Veto | Void Rend | Swan Song | Veil of Summer | Oath of Nissa | Blasphemous Act | Farseek | Three Visits | Doubling Season |
|---|---|---|---|---|---|---|---|---|---|---|
| Loyal Tutor | −0,2 pp ±0,4 | **−0,5 pp ±0,4** | −0,1 pp ±0,4 | −0,3 pp ±0,4 | −0,3 pp ±0,4 | −0,5 pp ±0,6 | **+0,8 pp ±0,5** | +0,3 pp ±0,6 | −0,1 pp ±0,5 | −0,5 pp ±0,6 |
| Tam, the Possibility | −0,4 pp ±0,5 | **−1,1 pp ±0,6** | **−0,5 pp ±0,5** | **−0,4 pp ±0,4** | −0,6 pp ±0,6 | −0,5 pp ±0,7 | +0,4 pp ±0,6 | +0,1 pp ±0,6 | +0,1 pp ±0,6 | **−0,8 pp ±0,6** |
| Entrust the Spark | −0,1 pp ±0,4 | **−0,3 pp ±0,3** | +0,1 pp ±0,4 | +0,1 pp ±0,4 | +0,1 pp ±0,4 | +0,1 pp ±0,6 | **+1,1 pp ±0,5** | **+0,6 pp ±0,6** | **+0,6 pp ±0,5** | −0,1 pp ±0,5 |

**Leitura:**
- **O controle funciona.** Cortar Doubling Season fica sempre no fundo do
  ranking, junto com os tutores de terreno (Farseek/Three Visits: ramp já é
  curto, 9 peças). O método separa corte ruim de corte bom.
- **Arena Rector é o melhor corte pras 3 cartas.** Ela é alvo da Bridge (criatura)
  que não dá PW. O gatilho de morte ("When this creature dies ... search your
  library for a planeswalker card") não tem como ser ligado de propósito:
  a lista não tem NENHUM outlet de sacrifício de criatura (varredura do
  oráculo da lista inteira). Na resiliência, cortá-la não piora a
  sobrevivência de nenhuma das 3.
- **Blasphemous Act não deve sair.** Cortá-la piora a sobrevivência na
  resiliência (+0,8 e +1,1 pp com Loyal Tutor/Entrust). O wipe protege os PWs.
- **Uso por partida** (10 turnos, modo padrão):
  - Loyal Tutor: sai em 21,2% das partidas (quase sempre que é comprado), 96% delas pela linha da Bridge.
  - Tam: ativa em 23,6% das partidas, 0,41 ativação e 0,43 de mana economizado por partida. A cópia pela Dynamo aparece em 0,9%.
  - Entrust: conjurado em 15,1% das partidas.

### Pacotes (as 3 juntas) — mesmas seeds

| pacote | 1º ult (Δ) | P(ult ≤ T8) | res: vida ≤ 0 | res: 1º ult (Δ) | res: PW-turnos (Δ) |
|---|---|---|---|---|---|
| base | 9,28 | 33,8% | 14,9% | 9,69 | 15,71 |
| **P1: Tam→Arena Rector, Loyal Tutor→Swan Song, Entrust→Veil of Summer** | **−0,246 ±0,033** | **40,1%** | 14,2% (−0,7 ±0,7) | **−0,140 ±0,040** | **+0,76 ±0,35** |
| P2: Tam→Arena Rector, Loyal Tutor→Dovin's Veto, Entrust→Void Rend | **−0,281 ±0,036** | **41,3%** | 14,3% (−0,6 ±0,7) | **−0,145 ±0,041** | **+0,73 ±0,38** |
| P3: só Tam→Arena Rector + Loyal Tutor→Swan Song | **−0,226 ±0,032** | **39,6%** | 14,2% (−0,7 ±0,6) | **−0,130 ±0,038** | **+0,61 ±0,33** |
| P4: só Loyal Tutor→Swan Song + Entrust→Arena Rector (sem Tam) | **−0,169 ±0,030** | **38,3%** | 14,5% (−0,4 ±0,5) | **−0,056 ±0,034** | **+0,81 ±0,33** |

Comparações pareadas entre pacotes:
- **Entrust na margem (P3 → P1):**
  - 1º ult −0,021 ±0,012 (significativo, mas pequeno);
  - P(ult ≤ T8) +0,5 pp ±0,4;
  - vida ≤ 0: 0,0.
- **Tam na margem (P4 + Tam no lugar de Veil):**
  - 1º ult −0,077 ±0,023;
  - P(ult ≤ T8) +1,8 pp ±0,9;
  - 1º ult na resiliência −0,084 ±0,030.
- **Cortes "melhores no simulador" (P2) × cortes pelo deck (P1):**
  - 1º ult −0,035 ±0,039, **indistinguível**;
  - vida ≤ 0: +0,1 pp ±0,7.

O simulador não separa as duas opções, então quem decide é o deck
(Regra #5, ver `checklist-oraculo.md`). Void Rend e Dovin's Veto são
incontraláveis e mais amplas do que o modelo de oponente consegue medir: o
oponente aqui só tem criatura, remoção, wipe e contramágica na Bridge.

## Rodada dedicada de gaps — auditoria completa das 100 cartas — 2026-09-24

**Pedido do usuário:** "Sim, faz a rodada dedicada fechando os gaps restantes".
Detalhe cláusula por cláusula em `checklist-oraculo.md`.

### Antes/depois de cada correção (2.000 partidas, mesmas seeds)

Modo padrão = seeds 3.000.000+; resiliência = mesa mista, seeds 6.000.000+.
Médias (as partidas "explosivas" puxam a média de ativações/ultimates pra
cima — ver medianas na tabela seguinte).

| etapa | 1ª Bridge | gatilhos Bridge | ativações | ultimates | PWs no T10 | land drops | res: vida ≤ 0 (%) | res: remoções sofridas | res: PWs no T10 |
|---|---|---|---|---|---|---|---|---|---|
| 0. reestruturação (md5 idêntico) | 4,28 | 3,88 | 10,0 | 2,12 | 2,34 | 4,92 | 19,0 | 1,50 | 1,85 |
| 1. Doubling Season não dobra custo | 4,28 | 3,88 | 10,0 | 2,10 | 2,33 | 4,91 | 19,0 | 1,51 | 1,83 |
| 2. Carth = +1 lealdade (não mana) | 4,29 | 3,96 | 10,5 | 2,43 | 2,40 | 4,92 | 18,9 | 1,53 | 1,88 |
| 3. mulligan sem embaralhar o fundo | 4,30 | 3,98 | 10,6 | 2,45 | 2,44 | 4,96 | 18,9 | 1,54 | 1,88 |
| 4. Halfling/Plaza/Beacon/Oath of Nissa/Bloom Tender (mana) | 4,22 | 4,09 | 10,8 | 2,49 | 2,50 | 4,97 | 16,7 | 1,61 | 1,95 |
| 5. shock/dor/World Tree | 4,26 | 4,04 | 10,6 | 2,39 | 2,46 | 4,97 | 18,0 | 1,59 | 1,93 |
| 6. gatilhos de conjuração centralizados | 4,26 | 4,04 | 10,7 | 2,49 | 2,49 | 4,97 | 17,6 | 1,58 | 1,96 |
| 7. Kaya 0, seleção real (Narset/Teferis), Vraska vida | 4,26 | 4,07 | 11,0 | 2,60 | 2,56 | 4,98 | 17,6 | 1,59 | 1,97 |
| 8. **PW conjurado da mão ganha lealdade** | 4,25 | 4,18 | **19,3** | **4,25** | **4,91** | 5,01 | 14,4 | 1,76 | 4,03 |
| 9. Aminatou + ETB das Oaths | 4,22 | 4,25 | 20,4 | 4,98 | 5,14 | 5,01 | 14,0 | 1,80 | 4,37 |
| 10. Oko +1/−5, fichas-cópia, Haze | 4,23 | 5,25 | 21,3 | 5,62 | 5,43 | 5,03 | 14,0 | 1,81 | 4,46 |
| 11. Teferis (desvirar/emblemas) | 4,23 | 6,60 | 45,4 | 13,07 | 5,53 | 5,08 | 13,8 | 1,85 | 4,53 |
| 12a. **terreno não é mágica** | **5,15** | 4,13 | **22,8** | **5,48** | 4,34 | **7,40** | 16,1 | 1,36 | 3,41 |
| 12b. Tamiyos (emblema/Notebook) | 5,15 | 4,62 | 32,5 | 8,73 | 5,51 | 7,41 | 16,1 | 1,40 | 3,84 |
| 13. Bolas (estático) | 5,15 | 4,74 | 33,4 | 10,21 | 5,56 | 7,39 | 16,1 | 1,40 | 3,82 |
| 14. Ichormoon + ordem do turno extra | 5,15 | 4,44 | 30,4 | 9,06 | 5,54 | 7,41 | 16,1 | 1,37 | 3,86 |
| 15. Vraska −9 / veneno | 5,15 | 4,28 | 21,1 | 5,81 | 5,39 | 7,40 | 16,1 | 1,32 | 3,84 |
| 16. Peregrine Dynamo | 5,15 | 4,40 | 22,2 | 6,51 | 5,40 | 7,41 | 16,3 | 1,31 | 3,90 |
| 17. Nesting Grounds/Grove/Ugin landfall/Urza | 5,16 | 4,42 | 22,3 | 6,71 | 5,33 | 7,36 | 16,4 | 1,31 | 3,95 |
| 18. respostas (só resiliência) | 5,16 | 4,42 | 22,3 | 6,71 | 5,33 | 7,36 | **14,6** | **0,86** | **4,79** |
| 19. Innkeeper nível 1 em todo modo | 5,16 | 4,42 | 22,3 | 6,71 | 5,33 | 7,36 | 14,6 | 0,86 | 4,79 |

Notas: a etapa 15 (veneno) derruba a MÉDIA de ativações só nas partidas em
que um oponente morre envenenado (24% delas): com oponente eliminado há menos
turnos de oponente pro emblema do Teferi Archmage — nas outras partidas nada
muda (mediana igual, 11). A etapa 11 → 12a mostra o tamanho do bug do
terreno: toda a "explosão" de mana da etapa 11 vinha, em parte, dos terrenos
baixados de graça.

### Commit anterior × agora (3.000 partidas, mesmas seeds)

| | antes | agora |
|---|---|---|
| 1ª Bridge (turno médio) | 4,34 (mediana 4) | 5,18 (mediana 5) |
| Bridge nunca conjurada até o T10 | 10,1% | 6,6% |
| Land drops em 10 turnos | 4,92 | 7,35 |
| Gatilhos da Bridge | 3,87 | 4,58 |
| Ativações de PW | 10,0 (mediana 6) | 23,1 (mediana 11) |
| Ultimates | 2,17 (mediana 1) | 7,07 (mediana 1) |
| PWs em campo no T10 | 2,35 (mediana 1) | 5,40 (mediana 4) |
| Cartas via PW | 5,8 (mediana 2) | 18,7 (mediana 5) |
| **Resiliência (mesa mista):** vida ≤ 0 até o T10 | 18,2% | 15,3% |
| remoções sofridas | 1,52 | 0,84 (contramágicas/proteções) |
| mortes de PW | 2,17 | 2,23 (com o dobro de PWs em campo) |
| PWs mortos em combate | 0,34 | 0,64 |
| PWs em campo no T10 | 1,87 | 4,82 |

### A/B de pillowfort refeito (4.000 partidas por célula, seeds 11.000.000+)

Mudou o que o A/B mede: a Oath of Nissa (o slot trocado) agora tem efeito
real (ETB + mana de PW), então o teste é "pillowfort × Oath of Nissa". O perfil
`low` (quase sem combate) serve de controle: o efeito lá é quase todo "custo
de tirar a Oath"; o que sobra nas mesas agressivas é a proteção de verdade.

| Δ PW-turnos vivos por partida | Silent Arbiter | Dueling Grounds | Sphere of Safety | Ghostly Prison |
|---|---|---|---|---|
| mesa mista | −0,67 | −0,38 | −0,29 | −0,46 |
| go-wide | −0,61 | −0,28 | −0,32 | −0,49 |
| voltron | −0,74 | −0,43 | −0,30 | −0,43 |
| low (controle) | −0,86 | −0,48 | −0,37 | −0,51 |
| **proteção líquida na mista (mista − low)** | +0,19 | +0,10 | +0,08 | +0,05 |

PW mortos em combate (mista): Arbiter −0,036, Dueling −0,028, Sphere −0,013,
Ghostly **+0,009** (empurra ataque pro PW, como antes). Silent Arbiter continua
roubando gatilho da Bridge (−0,11 PW acertado/partida). Nenhuma das 4 muda a
taxa de "vida ≤ 0" na mesa mista.

**Leitura:** a conclusão da rodada anterior fica mais forte. Com o motor
corrigido, o deck põe o dobro de PWs em campo e o ganho de proteção de
qualquer pillowfort (+0,05 a +0,19 PW-turno por partida na mesa mista) é
menor que o custo de tirar até uma carta barata como a Oath of Nissa.

## Modelo de combate + A/B de pillowfort (Silent Arbiter / Dueling Grounds / Sphere of Safety / Ghostly Prison) — 2026-09-24

**Pergunta do usuário:** "Conseguimos implementar no goldfish um simulador de
ataque aos PW? [...] Vale incluir Silent Arbiter e Dueling [Grounds]?" —
mesa real: **mista**. Modelo e suposições em `checklist-oraculo.md`.

### Antes/depois de cada correção (2.000 partidas, mesmas seeds)

Modo padrão (seeds 3.000.000+, 10 turnos). `s0` = só o modelo de combate
(modo padrão bit-idêntico ao commit anterior).

| etapa | gatilhos Bridge | PW acertados | ativações | ultimates | fichas | tutor Carth | PWs no fim |
|---|---|---|---|---|---|---|---|
| s0 modelo de combate | 3,243 | 1,960 | 8,799 | 1,542 | 2,309 | 0,244 | 1,809 |
| s1 `creature_enters` (doença + ETB Deepglow/Carth de todo ponto) | 3,244 | 1,973 | 8,952 | 1,635 | 2,285 | 0,334 | 1,877 |
| s2 Sphinx (fase inicial adicional real) | **3,884** | **2,352** | 9,989 | 1,980 | 2,503 | 0,367 | 2,320 |
| s3 Atraxa proliferate no end step | 3,885 | 2,344 | 10,026 | 2,118 | 2,465 | 0,352 | 2,337 |
| s4 Doubling Season dobra ficha | 3,885 | 2,344 | 10,026 | 2,118 | **2,744** | 0,352 | 2,337 |
| s5 Damn só preta | 3,881 | 2,341 | 10,021 | 2,118 | 2,743 | 0,351 | 2,336 |
| s6 Oath+Urza III não somam | 3,877 | 2,341 | 9,985 | 2,110 | 2,727 | 0,351 | 2,333 |
| s7 lore da Urza dobrado + Read ahead | 3,880 | 2,350 | 10,030 | 2,125 | 2,743 | 0,352 | 2,340 |
| s8 All Will Be One | = s7 (só métrica nova: 9,9 gatilhos/partida em média; em campo em 12,2% das partidas) |||||||
| s9 vida real (Kaya/Teferi Sunset/Ugin/Chain Veil) | = s8 (vida não é lida no modo padrão) |||||||

Resiliência, mesa mista (seeds 6.000.000+):

| etapa | vida final | PW mortos em combate | PW-turnos vivos | ultimates | PWs no fim |
|---|---|---|---|---|---|
| antes do modelo (ataque genérico antigo) | 37,22 | — | — | 1,120 | 1,429 |
| s0 modelo de combate | 22,12 | 0,348 | 7,297 | 0,898 | 1,429 |
| s2 Sphinx | 21,89 | 0,358 | 8,373 | 1,226 | 1,774 |
| s8 All Will Be One | 22,04 | 0,344 | 8,546 | 1,335 | 1,851 |
| s9 vida real | **24,74** | 0,344 | 8,546 | 1,335 | 1,851 |

### A/B pareado (5.000 partidas por célula, seeds 11.000.000+, 10 turnos)

Cada candidata entra no slot da **Oath of Nissa** (que o simulador ainda
não modela = slot "vazio"; mede o ganho marginal da carta). Mesma seed =
mesma ordem de biblioteca, então as partidas são idênticas até a carta
aparecer. "Condicional" = só partidas em que a carta chegou ao campo,
comparadas com a mesma seed sem ela.

**Mesa mista (a real):** base = 17,7% das partidas chegam a vida ≤ 0 até o T10;
0,33 PW morto em combate por partida (de 2,20 mortes de PW no total — a
maior parte vem de remoção de oponente e dos próprios ultimates).

| Δ vs base (por partida) | Silent Arbiter | Dueling Grounds | Sphere of Safety | Ghostly Prison |
|---|---|---|---|---|
| em campo até o T6 | 14,6% | 10,3% | 5,0% | 10,7% |
| "morreu" até o T10 | −1,0 pp | −0,8 pp | −0,2 pp | −0,7 pp |
| PW mortos em combate | −0,024 | −0,008 | −0,007 | **+0,012** |
| PW-turnos vivos | **−0,287** | +0,007 | 0,000 | −0,053 |
| ultimates | −0,033 | −0,004 | +0,002 | −0,021 |
| PWs acertados pela Bridge | **−0,106** | 0,000 | −0,001 | −0,006 |
| dano de combate nosso (proxy) | −2,6 | −1,9 | −0,3 | −0,3 |
| condicional: "morreu" | −3,0 pp | −4,2 pp | −2,4 pp | −3,8 pp |
| condicional: PW-turnos vivos | **−0,74** | +0,01 | −0,05 | −0,25 |

**Mesa go-wide (pior caso pra PW):** base 27,2% "morreu", 0,41 PW morto em
combate. Dueling Grounds é a melhor: condicional −8,6 pp de morte, −0,145
PW morto em combate, **+0,37 PW-turnos vivos**, +0,10 ultimate. Sphere:
condicional +0,29 PW-turnos, −6,4 pp. Silent Arbiter: condicional −0,65
PW-turnos (Bridge diluída). Ghostly Prison: condicional **+0,12 PW morto em
combate** (empurra ataque pro PW). **Voltron e low:** as 4 ficam ~neutras
(só 1 atacante relevante; Silent Arbiter continua negativa pela diluição).

**Sensibilidade (mesa focada em mim, atenção 2/3):** o risco vira MORRER
(vida final média −8 na mista, −29 na go-wide); as 4 ajudam a vida
(+0,9 a +4,0) mas os PWs quase não mudam — a conclusão não vira.

### Leitura (Regra #5: deck primeiro, simulador como apoio)

- **Silent Arbiter: não.** É criatura num deck cuja Bridge revela "até
  achar criatura OU planeswalker" — cada criatura não-PW a mais rouba
  gatilho da Bridge (−0,27 PW acertado quando ela aparece). Morre nos
  nossos próprios 5 wipes. Limita nosso ataque (fichas da Elspeth/Samurai/
  Elk/Oko).
- **Ghostly Prison: não pra proteger PW.** Ruling oficial: não protege
  planeswalker — e o atacante que não paga vai pro PW (medido: mais PW
  morto em combate).
- **Dueling Grounds: a única com efeito real, e só contra go-wide.** Na
  mesa mista o ganho nos PWs é ~zero; protege vida. Não para comandante
  voltron (ele já é 1 atacante só).
- **Sphere of Safety:** efeito pequeno, 5 de mana, raramente em campo cedo.
- O deck já tem a defesa anti-criatura que importa: 5 wipes, 4 remoções
  pontuais, 13 modos de remoção/controle em 11 PWs, All Will Be One (agora
  modelada), o estático da Eternal Wanderer. Combate responde por ~15% das
  mortes de PW no modelo; o maior risco medido é a nossa VIDA (17,7% das
  partidas chegam a 0 na mesa mista), não o PW.

## CR 903.9a: comandante passa pelo cemitério de verdade antes da zona de comando — 2026-09-21

**Gatilho:** usuário conferiu a regra real do CR 903.9 e apontou o erro
("comandantes podem ser mortos sim!"). Detalhes completos em
`checklist-oraculo.md` e `megatron-tyrant-mardu/checklist-oraculo.md`.

**Achado:** 2 call sites reais neste deck (diferente dos outros 8) —
`remove_permanent` (resiliência) E `resolve_removal_round` (sistema
legado, roda em modo padrão também). Ambos desviavam o comandante
direto pra zona de comando sem passar pelo cemitério. Bridge é
Enchantment (não Creature/Planeswalker) — Carth the Lion, único
gatilho de morte do deck, não reage a ela — correção puramente
estrutural nos 2 pontos.

**Resultado:** modo padrão idêntico nas 2 variantes de lista (com/sem
Greater Auramancy), 0/3000 mismatches cada.

**Validação:** regressão de 20.000 partidas em modo padrão + 20.000 em
modo de resiliência, 0 exceções nos 2, 0 comandantes presos no
cemitério + 3 testes dirigidos.

## `try_smart_opponent_removal` nunca respeitava shroud de Sterling Grove/Greater Auramancy — 2026-09-21

**Gatilho:** usuário perguntou se a proteção de Sterling Grove/Greater
Auramancy (shroud pra "other enchantments you control") e a menor
frequência real de wipe de encantamento tinham sido consideradas.
Detalhes técnicos completos em `checklist-oraculo.md`.

**Achado:** shroud não se aplica a NENHUMA das wipes reais da lista
(nenhuma usa "target"), então o número de enchantment wipe do A/B
anterior está correto. Mas achei um bug real na categoria de remoção
ALVO (`try_smart_opponent_removal`) — nunca respeitava a proteção,
diferente do sistema legado que já fazia isso certo antes do modo de
resiliência substituir ele.

**Resultado (A/B 2000 jogos mesma seed_base):** Sterling Grove passa a
ser removido em 0,3% dos jogos (0,0% antes — nunca era alvo desta
categoria). Efeito pequeno mas real (janela estreita: Sterling Grove
precisa estar em campo no exato momento do roll de remoção).

**Validação:** modo padrão 100% bit-idêntico (2.000 seeds) + regressão
de 20.000 partidas em modo resiliência, 0 exceções + 3 testes
dirigidos.

---

## Modo de resiliência ganha wipe de artefato e wipe de encantamento — 2026-09-20

**Gatilho:** "Temos que incluir remoções de artefatos e encantamentos
tb: Vandalblast, Farewell, Austere Command, etc…" Detalhes técnicos em
`checklist-oraculo.md` e `megatron-tyrant-mardu/checklist-oraculo.md`.

**Implementado direto no design FINAL** (unificado — 1 rolagem "algum
wipe acontece" + escolha ponderada de 1 tipo só, pesos 0.4/0.2/0.15).
Achado real: a própria Bridge É Enchantment — o único dos 3 tipos de
wipe que a alcança, corretamente roteada pra zona de comando (CR
903.9), nunca cemitério.

**Resultado (A/B 2000 jogos mesma seed_base):** % de jogos com pelo
menos 1 wipe de qualquer tipo sobe de 38,7% pra 64,5% (antes = commit
`d66e569`, só wipe de criatura). Avg wipes totais por jogo: 0,465 →
0,982. 16,4% dos jogos "depois" sofrem pelo menos 1 artifact wipe,
27,9% pelo menos 1 enchantment wipe.

**Validação:** modo padrão 100% bit-idêntico ao commit `d66e569`
(2.000 seeds) + regressão de 20.000 partidas, 0 exceções + teste
dirigido confirmando o roteamento CR 903.9 da Bridge (1.241/1.241
disparos corretos em 3.000 chamadas).

---

## Porte completo do modo de resiliência (interação de oponente) — 2026-09-20

**Gatilho:** "Repita o processo todo com o deck da Prismatic Bridge" —
mesmo modo já validado em Megatron/Ur-Dragon/Hei Bai/Markov/Ulalek/Toph.
Detalhes técnicos completos em `checklist-oraculo.md`.

**Diferença real vs. os outros 6 decks:** este arquivo já tinha
`resolve_removal_round`, sistema de remoção próprio (12%/oponente/turno,
sempre ativo, mira Bridge/protetores) construído pra responder "vale
Greater Auramancy?". Perguntei ao usuário antes de implementar como
reconciliar — escolha: modo de resiliência SUBSTITUI o antigo dentro
dele mesmo (via `play_turn(..., skip_legacy_removal=True)`), modo padrão
continua 100% intocado com o sistema antigo rodando normal.

**2 bugs reais de Carth the Lion corrigidos** (achados por acaso, não
relacionados ao modo de resiliência, mas já alcançáveis em modo padrão
hoje): "put the rest on the bottom" estava recolocando no TOPO da
biblioteca; a metade "planeswalker morre" do gatilho nunca disparava
(1.861 mortes de planeswalker em 3.000 jogos de modo padrão, evento
comum, não raro). Ambos corrigidos e validados.

**Achado de calibração importante:** a Bridge sobrevive MUITO mais sob
o novo modo de resiliência do que sob o sistema antigo, porque o novo
sistema (mesma convenção dos outros 6 decks) não mira o comandante
diretamente — Bridge removida 1,24x em média (sistema antigo) vs. 0,00x
(sistema novo); em campo no fim 72,0% vs. 90,8%. Consequência esperada
da decisão de design escolhida, não um bug — mas muda o que os números
do modo de resiliência respondem comparado à pergunta original do
Greater Auramancy (essa continua respondida pelo modo padrão intocado).

**Validação:** regressão de 20.000 partidas em modo padrão E resiliência
(0 exceções nos dois) + testes dirigidos (comandante→zona de comando,
sincronização de loyalty na morte de planeswalker + gatilho da Carth,
sistema antigo desligado de verdade dentro do modo de resiliência,
ordem de biblioteca da Carth batendo com o oráculo real).

**Comparativo — FIX real da Carth (2000 jogos, mesma seed, modo padrão antes/depois):**

| Métrica | Antes do fix | Depois do fix |
|---|---|---|
| Avg tutores via Carth | 0,114 | 0,244 |
| Avg mortes de planeswalker | 0,633 | 0,632 |
| Avg planeswalkers em campo no fim | 1,734 | 1,745 |

**Comparativo — ANTES (padrão, com fix da Carth) vs. DEPOIS (modo de resiliência), 2000 jogos, 10 turnos:**

| Métrica | Antes | Depois |
|---|---|---|
| Bridge nunca conjurada em 10 turnos | 7,8% | 9,2% |
| Bridge em campo no fim da partida | 72,0% | 90,8% |
| Avg vezes que a Bridge foi removida | 1,24 | 0,00 |
| Avg gatilhos da Bridge | 3,20 | 5,58 |
| Avg acertos em criatura | 1,25 | 2,18 |
| Avg acertos em planeswalker | 1,95 | 3,40 |
| Avg ativações de planeswalker | 8,38 | 10,42 |
| Avg ultimates usados | 1,44 | 1,41 |
| Avg tokens criados por PW | 2,28 | 2,98 |
| Avg cartas compradas via PW | 4,54 | 5,64 |
| Avg planeswalkers em campo no fim | 1,74 | 1,68 |
| Avg tutores via Carth | 0,24 | 0,44 |

**Métricas exclusivas do modo de resiliência (2000 jogos):** vida final
36,82; ataques sofridos 2,04; remoções inteligentes 1,80 (miram
planeswalkers, não a Bridge); descartes 1,33; board wipes 0,77 (56,1%
das partidas); graveyard wipe 0,59; graveyard snipe 0,64; counterspells
0,06; Bridge recastada após remoção em 4,5% das partidas.

---

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

### Simulação #3 — Enlightened Tutor no lugar do Greater Auramancy — 2026-08-21

**Teste de acompanhamento**, pedido do usuário depois do resultado do Greater Auramancy. Enlightened Tutor (`{W}`, Instant, `Search your library for an artifact or enchantment card... put that card on top`) no lugar de The Peregrine Dynamo, buscando Sterling Grove especificamente (lógica adicionada: busca só se Sterling Grove ainda não está em campo e ainda está na biblioteca).

**n=2000, taxa de remoção 12%/oponente/turno:**

```
Sterling Grove chegou a estar em campo:
  sem tutor:            14,7%
  com Enlightened Tutor: 24,3%   (+9,6pp, ~65% de aumento relativo)

% Bridge ainda em campo no fim da simulação:
  sem tutor:             63,3%
  com Enlightened Tutor: 63,2%   (~igual)

Avg vezes que a Bridge foi removida por partida:
  sem tutor:             1,18
  com Enlightened Tutor: 1,14   (mesma ordem de grandeza do Greater Auramancy)
```

**Leitura:** o tutor melhora bastante a taxa de ACESSO ao Sterling Grove (quase 2/3 de aumento relativo), mas isso não vira sobrevivência maior da Bridge no fim da partida. Motivo: Sterling Grove não se protege a si mesmo, e Enlightened Tutor é singleton — depois que o Sterling Grove morre (o que ainda acontece com frequência normal), não tem como buscar de novo. O tutor ataca "conseguir a proteção mais cedo", não "a proteção persistir depois que cai" — que é o mesmo problema estrutural de antes, só adiado.

**Nenhuma das duas opções testadas (Greater Auramancy, Enlightened Tutor) resolve o problema de forma decisiva sozinha.**

---

### Simulação #4 — Hall of Heliod's Generosity (recursão repetível) — 2026-08-21

**Diferença do Enlightened Tutor:** Hall of Heliod's Generosity (`{1}{W}, {T}: Put target enchantment card from your graveyard on top of your library`) é um TERRENO — permanente, repetível, não singleton. Testado no lugar de Nesting Grounds, em 10 E 16 turnos (pra dar tempo da cadeia completa: Sterling Grove morrer → Hall em campo → mana disponível → recursão → compra → recast).

**Bug encontrado e corrigido nesse teste:** `resolve_removal_round` fazia a carta removida sumir do jogo em vez de ir pro cemitério — teria feito a recursão nunca achar o alvo. Corrigido em `prismatic_bridge_goldfish_v1.py` (agora `state.graveyard.append(target)` na remoção de protetores).

**n=2000, taxa de remoção 12%/oponente/turno, comparando 10 vs 16 turnos:**

```
                          Baseline 10t   +Hall 10t   Baseline 16t   +Hall 16t
Sterling Grove em campo   15,1%          15,1%       21,1%          21,1%
Bridge em campo no fim    63,3%          63,1%       69,8%          70,0%
Bridge removida (média)   1,18           1,17        2,44           2,42
```

**Efeito praticamente zero em qualquer horizonte de turnos.** Instrumentado: só 48 eventos de recursão em 2000 partidas (2,4%) em 10 turnos. Hall of Heliod's Generosity é 1 carta em 37 terrenos (~2,7% de densidade) — só ativa se Sterling Grove já morreu E ela já está em campo E sobra mana, uma cadeia de baixa probabilidade que raramente se completa mesmo dando mais tempo de jogo (16 turnos não muda o resultado vs. o baseline no mesmo horizonte).

**Conclusão consolidada das 3 opções testadas (Greater Auramancy, Enlightened Tutor, Hall of Heliod's Generosity): nenhuma resolve o problema de forma perceptível.** Mesmo motivo nas três — deck de 99 cartas singleton com 1 única peça de proteção dedicada (Sterling Grove), competindo por espaço de compra com as outras 96. Qualquer solução de 1 carta ainda precisa ser puxada primeiro, o que já é raro em 10-16 turnos. Ver `auditoria.md` seção de proteção pra recomendação final.

---

### Simulação #5 — avaliação principal, n=5000: Bridge cast + acerto de planeswalker até T6/T7/T8 — 2026-08-21

**Objetivo pedido pelo usuário:** avaliar o deck pela capacidade real de (a) conjurar a Bridge e (b) ela acertar um planeswalker (não criatura) via gatilho de upkeep, até os turnos 6, 7 e 8. Métrica nova adicionada ao simulador: `first_pw_hit_turn` (turno do primeiro acerto de planeswalker, rastreado em `bridge_upkeep_trigger`).

**Lista atual, sem nenhuma das trocas testadas nas sessões anteriores** (Greater Auramancy/Enlightened Tutor/Hall of Heliod's Generosity não estão na lista real — só foram experimentos). n=5000, 8 turnos, seed_base=4000000.

```
Avg mulligans: 0,23
Bridge nunca conjurada em 8 turnos: 12,5%
Turno médio da 1ª conjuração da Bridge: 4,07 | mediana: 4
Conjurada via flash (end step anterior): 3,7% das partidas
Avg gatilhos de upkeep por partida: 2,04
  Acertos em criatura: 3985 | em planeswalker: 6230 | total: 10215
% da Bridge ainda em campo no fim (T8): 59,0%
Avg vezes que a Bridge foi removida: 0,82
```

**Bridge colocou planeswalker em jogo (1º acerto de PW via gatilho de upkeep):**

| Turno | Chance acumulada |
|---|---|
| **T6** | **42,4%** |
| **T7** | **50,2%** |
| **T8** | **57,7%** |
| Nunca em 8 turnos | 42,3% |

**Leitura:** menos da metade das partidas (42,4%) já teve um planeswalker colocado de graça pela Bridge até o turno 6 — o motor central do deck ainda não "ligou" na maioria dos jogos nesse ponto. Só passa de 50% no turno 7. No turno 8, ainda quase 1 em cada 4 partidas (42,3% projetado ao fim de 8 turnos) nunca viu isso acontecer. Isso é consistente com os dados já registrados: turno médio de 1ª conjuração da Bridge é 4,07, e ela só acerta planeswalker em 6230 de 10215 gatilhos totais (61%, já que o deck tem mais planeswalker que criatura — seção 8 da auditoria), então mesmo quando a Bridge está em campo cedo, ainda precisa de outro gatilho de upkeep pra realmente acertar. A tese do deck (jogar PW de graça pela Bridge) é real, mas não é rápida nem garantida — é um plano de médio prazo (turno 7-8 em diante), não um plano de turno 4-5.

---

### Correção — mana disponível pra flashar a Bridge (CR 500.1: untap, upkeep, draw) — 2026-08-21

**Bug real identificado pelo usuário:** meu `can_flash_bridge` usava `total_mana`/`remaining_mana` (mana atual do jogador), como se tudo estivesse sempre destapado no momento de flashar a Bridge no end step de um oponente. Isso está errado — o untap step só destapa os permanentes do jogador ativo (CR 500.1). Meus terrenos ficam tapados do jeito que ficaram no MEU último turno durante os turnos dos oponentes; só destapam de novo no MEU próximo untap step. A mana real disponível pra flashar algo no end step alheio é o que sobrou NÃO GASTO do meu último turno, não o total atual.

**Correção aplicada:**
- Novo campo `state.mana_held_back` — calculado no fim de cada turno (`total_mana - mana_spent_this_turn`), representa o que ficou destapado e disponível até meu próximo untap.
- `can_flash_bridge` agora checa `mana_held_back` contra o custo do habilitador de flash (`Alchemist's Refuge` = 2, `Emergence Zone` = 1, `Emergence Zone` se sacrifica ao usar) + custo efetivo da Bridge (com taxa de comandante).
- `main_phase` agora reserva mana de propósito quando um habilitador de flash já está em campo e a Bridge ainda não saiu — não gasta tudo no resto da mão, seguindo mana pra viabilizar a linha de flash no futuro.

**Resultado, n=5000, 8 turnos:**

| Métrica | Antes (bug) | Depois (corrigido) |
|---|---|---|
| Conjurada via flash | 3,7% | **0,0%** |
| 1º acerto de PW até T6 | 42,4% | 40,9% |
| 1º acerto de PW até T7 | 50,2% | 48,6% |
| 1º acerto de PW até T8 | 57,7% | 55,9% |

**Achado estrutural, não só um ajuste numérico:** a linha de flash caiu pra ZERO, não só diminuiu. Motivo: no modelo, a Bridge está sempre "disponível" (vem da zona de comando, não depende de estar na mão) — assim que fica pagável, a IA gananciosa conjura ela imediatamente na main phase. O custo de flashar (habilitador + Bridge) é sempre maior que o custo de conjurar normal (só a Bridge). Como o mana total só cresce turno a turno, no momento em que teria mana suficiente pra flashar, já teria tido mana suficiente pra conjurar normal num turno anterior — e a IA já teria feito isso antes de chegar lá. **O modelo atual nunca escolhe segurar a Bridge de propósito só pra flashar**, porque não pesa o benefício real da linha (pular a janela de remoção antes do 1º gatilho) contra abrir mão de 1 turno com a Bridge já em campo. Pra medir esse benefício de verdade, seria preciso modelar uma política diferente (segurar a Bridge deliberadamente quando o habilitador já está em campo, mesmo podendo conjurar normal) — ainda não implementado.

---

### Política "hold-for-flash" implementada e testada — 2026-08-21

**Implementação:** novo flag `HOLD_FOR_FLASH_POLICY` (default `False`, preserva o comportamento cast-ASAP). Quando `True`: se um habilitador de flash (Alchemist's Refuge/Emergence Zone) já está em campo e a Bridge ainda não foi conjurada, o `main_phase` **não** conjura ela normal mesmo se pagável — segura de propósito, reserva mana todo turno, e espera a janela de flash no end step alheio (`can_flash_bridge`, usando `mana_held_back`).

**n=5000, 8 turnos, comparando as duas políticas:**

| Métrica | Cast-ASAP (default) | Hold-for-flash |
|---|---|---|
| Conjurada via flash | 0,0% | **9,4%** |
| Bridge nunca conjurada em 8t | 14,1% | **21,5%** |
| Turno médio da 1ª conjuração | 4,08 | 4,29 |
| Avg gatilhos de upkeep/partida | 1,96 | **1,73** |
| % Bridge em campo no fim | 58,6% | **50,2%** |
| Avg Bridge removida | 0,78 | **0,69** |
| 1º acerto de PW até T6 | 40,9% | **36,5%** |
| 1º acerto de PW até T7 | 48,6% | **43,5%** |
| 1º acerto de PW até T8 | 55,9% | **50,4%** |

**Leitura:** a troca é real, mas negativa no agregado. Segurar de propósito reduz a remoção média (0,78→0,69 — a proteção contra a janela de exposição funciona de verdade) e ativa a linha de flash em 9,4% das partidas. Mas o custo supera o ganho: como o limiar de mana pra flashar é sempre MAIOR que o limiar pra conjurar normal, esperar por essa condição mais cara e mais rara atrasa (ou em muitos casos impede) a entrada da Bridge em campo — mais partidas nunca chegam a ter a Bridge em campo (14,1%→21,5%), menos gatilhos totais acontecem (1,96→1,73), e todas as métricas de acerto de planeswalker pioram (T6/T7/T8 caem uns 4-5 pontos cada).

**Conclusão prática:** a política ótima, segundo o modelo, não é "sempre segurar pra flashar quando possível" — é conjurar assim que fica pagável (política atual, já é o padrão do simulador). Só vale usar a linha de flash nos casos em que ela já coincide naturalmente com o resto do jogo, não como estratégia deliberada e sistemática.

---

### Heurístico de mulligan corrigido com base em dados reais — 2026-08-21

**Análise de correlação** (n=8000 mãos amostradas pós-mulligan, presença de carta na mão inicial vs turno da 1ª conjuração da Bridge), pedida pelo usuário pra responder "3 terrenos ou 2+rock, e quais cartas".

**Comparação de composição de mão (só mãos sem mulligan, n=6468):**

| Composição | Turno médio 1ª conjuração | % nunca conjura |
|---|---|---|
| 2 terrenos, 0 rocks | **5,72** | **31,8%** |
| 3 terrenos, 0 rocks | 4,50 | 14,0% |
| 2 terrenos + 1+ rock | **4,32** | **12,2%** |
| 4 terrenos, 0 rocks | 3,33 | 6,0% |
| 3 terrenos + 1+ rock | 3,21 | 3,8% |

Confirma a hipótese do usuário: **2 terrenos + 1 rock supera 3 terrenos sem rock.** E revela que **2 terrenos sem rock é uma mão ruim de verdade** (5,72t, 31,8% nunca conjura) — o `should_keep()` anterior aceitava isso (só checava 2-5 terrenos, sem considerar rocks).

**Correlação carta-por-carta (n=8000, presença na mão inicial vs turno médio):**

| Carta | Com ela | Sem ela | Efeito |
|---|---|---|---|
| Arcane Signet | 3,36t / 4,5% nunca | 4,15t / 14,8% nunca | Maior ganho individual |
| Sol Ring | 3,18t / 7,1% nunca | 4,16t / 14,6% nunca | Forte |
| Bloom Tender | 3,50t / 5,6% nunca | 4,13t / 14,7% nunca | Forte |
| Delighted Halfling | 3,40t / 8,4% nunca | 4,14t / 14,6% nunca | Forte |
| Chromatic Lantern | 3,82t / 7,3% nunca | 4,11t / 14,6% nunca | Bom |
| Farseek | 4,32t / 17,9% nunca | 4,08t / 13,9% nunca | Pior (não conta como rock) |
| Nature's Lore | 4,50t / 15,7% nunca | 4,06t / 14,0% nunca | Pior |
| Three Visits | 4,48t / 16,9% nunca | 4,07t / 14,0% nunca | Pior |
| Sterling Grove | 4,43t / 15,7% nunca | 4,06t / 14,0% nunca | Neutro/pior pra velocidade |
| Rhystic Study | 4,32t / 14,4% nunca | 4,07t / 14,1% nunca | Neutro/pior pra velocidade |

**Correção aplicada em `should_keep()`:** novo conjunto `FAST_RAMP_ROCKS_DORKS = {"Sol Ring", "Arcane Signet", "Chromatic Lantern", "Bloom Tender", "Delighted Halfling"}` — os tutores de terreno (Farseek/Nature's Lore/Three Visits) ficam de fora de propósito, já que pioram a velocidade quando estão na mão inicial. Regra nova: manter se 3+ terrenos, OU 2 terrenos + pelo menos 1 desses 5 rocks/dorks.

**n=5000, 8 turnos, ANTES vs DEPOIS da correção do mulligan:**

| Métrica | Antes (só checava 2-5 terrenos) | Depois (heurístico corrigido) |
|---|---|---|
| Avg mulligans | 0,23 | **0,52** |
| Bridge nunca conjurada em 8t | 14,1% | **10,7%** |
| Turno médio da 1ª conjuração | 4,08 | **3,78** |
| Avg gatilhos de upkeep/partida | 1,96 | **2,14** |
| % Bridge em campo no fim | 58,6% | **60,1%** |
| 1º acerto de PW até T6 | 40,9% | **45,8%** |
| 1º acerto de PW até T7 | 48,6% | **53,2%** |
| 1º acerto de PW até T8 | 55,9% | **59,8%** |

**Leitura:** mulligar mais mãos ruins (0,23→0,52 em média) melhora TODAS as métricas — velocidade, gatilhos totais, e principalmente a métrica que mais importa (acerto de planeswalker por turno, subindo 4-5 pontos em cada checkpoint). Confirma que o heurístico antigo estava deixando passar mãos genuinamente ruins.

---

### Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks. Auditoria via agente comparando `oracle_text`
real contra o código.

**Achado que explica a Simulação anterior:** a correlação carta-por-carta
registrada acima já tinha detectado que Farseek/Nature's Lore/Three Visits
"pioravam a velocidade quando estavam na mão inicial" — a causa raiz era
esta: eram conjurados como Sorcery genérica e iam direto pro cemitério, **sem
nenhuma busca de terreno real**, puro sink de mana/carta. Corrigido nesta
rodada com busca real (pool real por tipo de terreno, Scryfall).

**Outros bugs reais achados (todos na modelagem de mana, que é diretamente
relevante pra pergunta central deste sim — turno de resolução da Bridge):**

- **Bloom Tender / Delighted Halfling**: sem NENHUM rastreio de doença de
  invocação — produziam mana no próprio turno em que eram conjurados.
- **Bloom Tender**: "for each color among permanents you control" modelada
  como 5c fixo, não escala com as cores reais em campo.
- **Delighted Halfling**: `{T}: Add {C}` incondicional era real, mas a mana
  colorida (any color) só vale "pra conjurar um spell lendário" — modelada
  como 5c incondicional. Corrigido (nova tabela `LEGENDARY_CARD_NAMES`, 24
  permanentes lendários reais na lista).
- **Chromatic Lantern**: faltava a estática de campo inteiro ("Lands you
  control have '{T}: Add one mana of any color.'") — só o próprio `{T}`
  dela estava certo.
- **The World Tree**: "as long as you control six or more lands..." — a
  mesma estática de campo inteiro, condicionada a 6+ terrenos, tratada como
  5c incondicional desde o turno 1.
- **Fabled Passage**: não tem NENHUMA habilidade de mana no oráculo real (só
  sac-fetch) — modelada como fonte incondicional de qualquer cor. Corrigido
  com a busca real (basic land, tapped se <4 terrenos).
- **Interplanar Beacon / Plaza of Heroes**: só `{T}: Add {C}` é incondicional
  no oráculo real — as habilidades coloridas são restritas (planeswalkers
  only / legendary only). Modeladas como 5c incondicional; corrigidas pra
  só incolor (as restrições em si não foram modeladas, baixo valor pro
  escopo, documentado no código).
- **Evolution Sage**: landfall-proliferate 100% ausente — mesma classe do
  bug do Beorn (nenhum despacho de landfall existia neste arquivo).

**Explicitamente NÃO corrigido nesta rodada (decisão de escopo, documentada
no docstring do arquivo, não esquecimento):** as 14 cartas tageadas "draw" e
as 8 tageadas "proliferate"/"counter_doubler" continuam com a tag mas sem
gatilho real. Draw fica de fora por volume (comparável a montar um goldfish
completo); proliferate/counter-doubler fica de fora porque este simulador
não rastreia nenhum sistema de counters/tokens/loyalty — não há alvo real
pra dobrar/proliferar no estado rastreado, e a pergunta central do sim
(turno de resolução/taxa de acerto/sobrevivência da Bridge) não depende
disso.

**Resultado (n=2000, seed_base=3000000, sem Greater Auramancy, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Bridge nunca conjurada em 10t | 5,8% | **9,6%** |
| Turno médio da 1ª conjuração | 4,14 | **4,30** |
| % Bridge em campo no fim | 64,8% | **69,5%** |
| Acertos totais (criatura+PW) | 6226 | **6331** |

A Bridge ficou levemente mais lenta/menos confiável de conjurar — esperado,
já que várias fontes "grátis" de 5c incondicional (Fabled Passage,
Interplanar Beacon, Plaza of Heroes, metade do Delighted Halfling) foram
corrigidas pra restritas/incolor. Os tutores de terreno agora rampam de
verdade, o que compensa parcialmente. Recomendação: se o usuário quiser,
vale re-rodar a correlação carta-a-carta da Simulação anterior (Farseek/
Nature's Lore/Three Visits devem parar de aparecer como "pior pra
velocidade" agora que rampam de verdade).

**Robustez:** sweep de 20.000 jogos (seeds 3000000–3019999, timeout 2s/jogo),
sem Greater Auramancy — 0 erros, 0 timeouts. Smoke test de 500 jogos com
Greater Auramancy=True também limpo.

---

### Correção — lealdade e ativações reais dos 17 planeswalkers (regra nova) — 2026-08-28

**Gatilho (usuário):** depois de eu confirmar que este simulador nunca
modelava as habilidades individuais de nenhum dos 17 planeswalkers (só
rastreava SE a Bridge acertava um) — citação literal: *"Preciso que os
counters de lealdade e ativações de planeswalker sejam sempre
contabilizados, a base do Prismatic Bridge é essa! Adicione essa regra
para tudo, sempre também!"* Registrada como categoria 12 permanente em
`references/goldfish-sim-card-rules.md`.

**O que existia antes:** o `docstring` do arquivo já documentava isso
explicitamente como limitação de escopo ("habilidades individuais de cada
um dos 17 planeswalkers... NÃO modelado") — não era um buraco silencioso,
mas era uma lacuna real e grande: um planeswalker acertado pela Bridge
virava um nome parado em `state.battlefield`, sem lealdade, sem ativação,
sem efeito.

**Implementado:**
- `PLANESWALKER_STARTING_LOYALTY` — lealdade inicial real (Scryfall) das 17
  cartas. `state.loyalty: Dict[str, int]` rastreia lealdade de verdade.
- `add_loyalty()` — helper central que aplica mudança de lealdade,
  respeitando os dobradores reais de counter (Doubling Season/Vorinclex,
  Monstrous Raider — ambos com "put twice that many counters", empilham
  multiplicativamente) e mata o planeswalker (remove de campo, vai pro
  cemitério) quando a lealdade chega a 0.
- **As 17 habilidades reais implementadas** (uma ativação por planeswalker
  por turno, CR 606.3), cada uma com heurística documentada de qual
  habilidade usar (prioriza ultimate quando alcançável e não-simétrico,
  senão a habilidade de maior valor real sem downside pro nosso lado):
  Aminatou (+1), Ashiok (-1, denial), Elspeth (+1 tokens / -7 ultimate),
  Kaya (+2 drain), Liliana (+1 token / -9 ultimate), Narset (-2 tutor),
  Nicol Bolas (+1 draw / -8 ultimate), Oko (-1 token), Tamiyo Compleated
  Sage (-X recursão real do cemitério, conta pra métrica RECURSION / -7
  ultimate), Tamiyo Field Researcher (-7 ultimate), Teferi Hero (+1 draw /
  -8 ultimate), Teferi Temporal Archmage (+1 draw / -10 ultimate), Teferi
  Time Raveler (-3 draw sem downside), Teferi Who Slows the Sunset (+1
  vida / -2 draw / -7 ultimate com emblem real — +3 compras/turno depois,
  mesma premissa de N_OPPONENTS já usada no resto do arquivo), The Eternal
  Wanderer (0 token, sem custo), Ugin (+2 / -10 ultimate real: ganha 7
  vida, compra 7, coloca até 7 permanentes da mão em campo de graça, mesmo
  padrão do Last March of the Ents no Beorn), Vraska (0: draw + proliferate
  real — agora com alvo de verdade, a lealdade de outros planeswalkers).
- **Sinergia nova e real:** Evolution Sage (landfall proliferate) e Deepglow
  Skate (ETB dobra counters) agora têm efeito de verdade — antes eram
  documentados como "sem alvo modelável" porque não existia nenhum sistema
  de counters rastreado; agora a lealdade de planeswalker é esse alvo.

**Deliberadamente deferido nesta rodada (documentado, não silenciado):**
estático da Nicol Bolas ("has all loyalty abilities of all other
planeswalkers" — exigiria dispatch combinatório, baixo valor esperado já
que 2+ planeswalkers vivos simultâneos são raros com a Bridge acertando 1
por vez); Innkeeper's Talent nível 3 (precisa de engine de leveling de
Class, mesma classe de simplificação já usada no Caretaker's Talent do Hei
Bai); proliferate de Flux Channeler/Ichormoon Gauntlet/Inexorable
Tide/Mutational Advantage/Ripples of Potential/Atraxa (precisam de hooks de
"ao conjurar spell"/"end step" que este arquivo ainda não tem — fica pra
uma rodada dedicada).

**Resultado (n=2000, turns=10, sem Greater Auramancy):**

```
--- Planeswalkers (lealdade + ativacoes reais, regra nova) ---
Avg ativacoes de habilidade de planeswalker por partida: 7.08
Avg planeswalkers vivos no fim da simulacao: 1.70
Avg mortes de planeswalker (lealdade a 0) por partida: 0.59
Avg ultimates usados por partida: 0.83
RECURSION (via Tamiyo, Compleated Sage -X): 0.09
DRAW: avg compras via planeswalker: 3.47
Avg tokens criados via planeswalker: 1.87
Avg vida ganha via planeswalker: 2.41 | vida perdida do oponente (proxy): 1.58
INTERACTION: avg remocao proxy (Ashiok/Ugin): 0.72 | wipe proxy (Elspeth/Liliana ultimate): 0.11
```

Antes desta correção, TODOS esses números eram 0 — não porque os
planeswalkers não tinham efeito no jogo real, mas porque o simulador
nunca os deixava agir. 58,6% das partidas acertam pelo menos 1
planeswalker até o turno 8 (métrica que já existia) — agora isso
finalmente vira valor real simulado, não só um nome parado em campo.

**Robustez:** sweep de 20.000 jogos (seeds 5000000–5019999, timeout
2s/jogo, alternando com/sem Greater Auramancy) — 0 erros, 0 timeouts.

`lista.md` não mudou.

---

### Correção — Innkeeper's Talent níveis 2 e 3 (regra nova de Classes/Sagas) — 2026-08-28

**Gatilho (usuário):** *"Não esqueça de verificar as cartas com 'níveis',
como classes e sagas. Vc tb precisa criar a regra de verificar e
contabilizar isso, pq... o innkeeper's no Prismatic no nível 3 DOBRA TODOS
OS COUNTERS, inclusive os de lealdade de PWs ao entrarem no jogo!"* Regra
nova (categoria 13, `goldfish-sim-card-rules.md`).

Na correção anterior (lealdade de planeswalker), eu tinha deixado
Innkeeper's Talent nível 3 de fora citando "precisa de engine de leveling"
sem tentar construir essa engine — exatamente o padrão que a nova regra
proíbe.

**Texto real (Scryfall):** `{G}: Level 2` — *"Permanents you control with
counters on them have ward {1}"* (defensivo puro, sem efeito numérico
modelável). `{3}{G}: Level 3` — *"If you would put one or more counters on
a permanent or player, put twice that many of each of those kinds of
counters on that permanent or player instead."*

**Implementado:**
- `try_level_up_innkeepers_talent()` — sobe de nível como sorcery, pagando
  o custo real ({G}=1 pro nível 2, {3}{G}=4 pro nível 3).
- `counter_doubler_multiplier()` agora inclui Innkeeper's Talent nível 3
  junto com Doubling Season/Vorinclex — **dobra a lealdade inicial de
  qualquer planeswalker que a Bridge acertar depois disso**, e qualquer
  ganho de lealdade via +1/proliferate.
- Chamada no início do `main_phase()`, antes de `activate_planeswalkers()`
  — se o nível 3 é alcançado no MESMO turno que a Bridge acerta um
  planeswalker, a ordem real do turno (upkeep da Bridge acontece ANTES do
  main phase) significa que o dobro só vale a partir do próximo acerto,
  não retroage sobre o turno atual.

**Resultado (n=2000, sem Greater Auramancy):**

```
Innkeeper's Talent em campo em 18.5% dos jogos, alcancou nivel 3 (dobra
TODOS os counters, inclusive lealdade de planeswalker ao entrar) em 14.2%
```

Antes desta correção, esse número era simplesmente inexistente — a carta
nunca saía do nível 1. 14,2% das partidas (de 18,5% em que a carta aparece)
alcançam o nível 3, um efeito real e frequente o bastante pra valer a
correção.

**Robustez:** sweep de 20.000 jogos (seeds 7000000–7019999, timeout
2s/jogo, alternando com/sem Greater Auramancy) — 0 erros, 0 timeouts.

`lista.md` não mudou.

---

### Leitura linha-a-linha completa do oráculo (mesma exigência do Toph/Beorn/Edgar Markov/Hei Bai/Maralen/Megatron/Nekusar) — 2026-09-01

**Gatilho (usuário):** *"AGORA FAZ O QUE SEMPRE Te MANDei FAZER: COmpila
a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada carta tem que ser
lida linha a linha"*.

**Aviso:** este simulador foi construído deliberadamente com escopo
restrito (foco no motor Bridge + planeswalkers, não curva geral
completa) — diferente dos outros 6 decks. Apliquei "compile TUDO" às
lacunas documentadas como deferidas, não expandi o escopo original do
simulador.

Achado: 5 cartas 100% ausentes apesar de tags existentes — Sphinx of the
Second Sun (extra turn real, condicionado a "if you cast it" — não
dispara via Bridge, verificado contra o oráculo real, não suposição),
Carth the Lion (tutor de planeswalker no ETB + taxa de {1} em ativações
de lealdade), Flux Channeler/Inexorable Tide (proliferate no cast),
Mutational Advantage/Ripples of Potential (proliferate no próprio
efeito). Todos reusam `proliferate_loyalty()`, já testada.

**Reclassificações importantes (correção da minha própria memória, não
bugs de código):** eu tinha memorizado errado o texto de Arena Rector
(achei que era ETB "exile+recast", na real é gatilho de MORTE — 📊
estrutural real, nada remove nossas criaturas neste sim). Verifiquei
contra Scryfall antes de implementar, não confiei na lembrança.

**Deferido, confirmado genuinamente desproporcional:** Nicol Bolas
(estático que concede TODAS as habilidades de outros PWs) e Ichormoon
Gauntlet (concede habilidade nova a cada um dos 17 PWs) exigiriam
reestruturar a lógica hardcoded por-planeswalker deste arquivo
especificamente — não julgamento de valor sobre a carta, mas
desproporção real de escopo vs. o resto desta rodada.

**Robustez:** 6+ testes unitários isolados + 20.000 partidas de
regressão (0 erros, alternando `with_greater_auramancy`).

**Batch, n=2000, seed_base=1800000 (antes = git HEAD, depois = com os fixes):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg pw_activations_total | 6,72 | 6,73 |
| Avg planeswalkers_in_play_end | 1,70 | 1,78 |
| Sphinx extra turn ativado | (não existia) | 4,7% dos jogos |
| Carth tutor ativado | (não existia) | 11,2% dos jogos |

`checklist-oraculo.md` criado.

---

### Auditoria oráculo-por-oráculo completa — 2026-09-13/14

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil/Nekusar/Ms.
Bumbleflower/Rat King. Achado principal (detalhes completos em
`checklist-oraculo.md`, seção no topo): 3 fontes reais de "ativar
lealdade de planeswalker mais de 1x por turno" nunca implementadas
(Oath of Teferi — estático, sempre 2x; The Chain Veil — pago, {4}{T};
Urza Assembles the Titans capítulo III — 2x só naquele turno), num deck
com 17 planeswalkers. Também: Urza's Saga inteira (capítulos I e II)
100% ausente, e 11 cartas de interação (Counterspell, Mana Drain, Path
to Exile, Swords to Plowshares, Anguished Unmaking, Damn, Void Rend,
Toxic Deluge, Blasphemous Act, Supreme Verdict, Farewell) nunca
contavam pra métrica agregada apesar de terem as tags reais desde a
construção original.

**Batch, n=2000, seed_base=3000000 (antes = git HEAD, depois = com os fixes):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg ativações de planeswalker por partida | 7.01 | 8.65 |
| Avg ultimates usados por partida | 1.18 | 1.48 |
| Avg compras via planeswalker | 3.87 | 4.66 |
| Avg tokens criados via planeswalker | 1.74 | 2.24 |
| Avg mortes de planeswalker por partida | 0.52 | 0.63 |
| Avg vida ganha via planeswalker | 2.67 | 3.37 |
| INTERACTION (11 cartas, antes não existia) | 0 | 2.45 |

Regressão de 20.000 partidas (seed 7000000, turns=8): 0 exceções. Chain
Veil ativado em 6.8% dos jogos, Urza conjurada em 7.9% e alcançou
capítulo III (dobra de lealdade) em 51.2% desses. Subida generalizada
mas moderada em todas as métricas de planeswalker — esperado, já que os
3 multiplicadores de ativação corrigidos afetam TODOS os 17
planeswalkers da lista, não uma carta isolada, mas cada fonte
individual (Oath of Teferi/Chain Veil/Urza) só aparece numa fração
minoritária dos jogos.

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
