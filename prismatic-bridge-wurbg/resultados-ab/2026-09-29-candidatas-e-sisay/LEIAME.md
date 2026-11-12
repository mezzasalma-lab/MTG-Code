# Resultados brutos — candidatas do Prismatic Bridge e Sisay (2026-09-29 e 2026-09-30)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck
Esika // The Prismatic Bridge. As conclusões e tabelas legíveis estão em
`prismatic-bridge-wurbg/goldfish-log.md` (seções datadas 2026-09-29/30) e
`prismatic-bridge-wurbg/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (as seções mais novas ficam no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.md` por tabela; mapa abaixo) |
| refazer uma tabela a partir dos dados | `bash descomprimir.sh` e rodar o comando da coluna "comando" do mapa |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |
| saber que partidas existem em cada arquivo | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## Como os dados foram gerados

- **Simulador:** `prismatic-bridge-wurbg/prismatic_bridge_goldfish_v1.py` (modo padrão = goldfish sem oponente; modo
  resiliência = 3 oponentes simulados com perfil de mesa `mixed`, salvo nos lotes `prof_*`/`sprof*_*`).
- **Sementes:** padrão `3_000_000 + i`; resiliência `6_000_000 + i`; regressão `+100_000`. **Pareado:** todas as variantes de um lote usam as
  mesmas sementes, então a diferença entre duas variantes é por partida (IC95% = 1,96·dp/√N da diferença). N = 3.000 por modo (regressão: 20.000
  por modo).
- **Variante:** `ENTRA|SAI[+ENTRA2|SAI2][@chave1,chave2]`. A troca é **posicional** (a carta nova entra NA LINHA da cortada). `@chave` inverte o
  padrão da chave de `CAND_POLICY` só naquela variante (sensibilidade).
- **Arquivo `<prefixo>_<n>.json.xz`:** parte `n` de um lote rodado em paralelo (o resumo junta `<prefixo>_*.json`). Conteúdo:
  `{variante: {"std": [métricas por partida], "res": [...]}}`; campos em `ab_candidatas.py` (`std_metrics`, `res_metrics`). Os lotes
  `motor_*`, `usoar*_*` e `reg*_*` têm formato próprio (ver o script que os gerou).
- **Scripts de orquestração** (como rodaram; têm caminhos absolutos da pasta temporária da sessão, ajuste `SC`/`AB` para rodar de novo): `orquestracao/`.

## Mapa: arquivo → o que é → onde foi usado

O "código" é o commit do simulador com que o lote foi gerado. Onde o lote rodou com código ainda não commitado, o commit é o primeiro que o
contém; o simulador só mudou entre eles nas chaves indicadas em "obs.".

| prefixo | o que é (variantes) | código | status | tabelas que usam |
|---|---|---|---|---|
| `main`, `main2` | 4 candidatas (Dihada, Guff, Vronos, Sarkhan) × 6 cortes + controle "PW inerte" + pacote das 4 (std + res) | `4493c19` | usado | log: "Rodada das 4 candidatas"; base de todos os merges abaixo |
| `sens` | sensibilidade por chave de política das 4 + PW inerte (`@dihada_minus3`, `@guff_minus3`, `@vronos_phase`, `@sarkhan_animate`) | `4493c19` | usado | idem |
| `prof_go_wide`, `prof_voltron`, `prof_low` | 4 candidatas + inerte por perfil de mesa (res) | `4493c19` | usado | log: "Sensibilidade ao perfil de mesa" |
| `vp` | proteção do Vronos (com/sem phase out; res) | `4493c19` | usado | log: "Vronos: onde o phase out aparece" |
| `csb_*` | respostas do Commander Spellbook (`find-my-combos`), base e cada candidata | `4493c19` | usado | log: Spellbook das 4 candidatas |
| `fra` | as 4 candidatas contra o trio de Reality Fracture (Tam, Loyal Tutor, Entrust) nos mesmos slots (12 variantes) | `eca8aba` | usado | log: seção 7 "Vale a pena?" |
| `sisay` | Sisay em 6 cortes, política antiga da mão. **Única fonte dos controles "Control Body" (corpo 2/2 lendário sem texto)**; as demais chaves foram superadas por `sis2` | intermediário (antes de `40158b6`) | usado só p/ Control Body | log: Sisay, tabela "texto − corpo" |
| `sisp` | **INVÁLIDO:** rodou com harness em que `@sisay_pre_hand_all` tinha semântica invertida | intermediário | **não usar** | nenhuma |
| `sis2` | Sisay, política final de ordem (busca antes da mão), Liliana antiga (11 variantes, std + res) | `40158b6` | std usado; res superado por `lil`/`lil2` | log: Sisay (padrão) |
| `sprof`, `sprof2_*` | perfis de mesa da Sisay/corpo, políticas anteriores | intermediário / `40158b6` | superado por `sprof3_*` | nenhuma final |
| `sprof3_go_wide`, `_voltron`, `_low` | Sisay e corpo 2/2 por perfil, política final | `9376786`* | usado | log: Sisay, perfis |
| `lil` | Sisay em 6 cortes, política final da Liliana (res) + pares + variante `@liliana_spares_sisay` (Liliana antiga) | `9376786`* | usado (res) | log: Sisay; Sisay × Arena Rector |
| `lil2` | sensibilidades da Sisay (`@sisay_activate`, `@sisay_pre_hand_all`), terceiro/quarto slot com a Sisay (res) | `9376786`* | usado (res) | log: Sisay, seção 7 |
| `pair`, `pair3` | pares Sisay+Loyal Tutor, Sisay+Tam (`pair`, std) e Tam+Loyal Tutor (`pair3`, std + res) | `40158b6` (`pair`), qualquer (`pair3`, sem Sisay) | usado (`pair`: só std; res vem de `lil`) | log: Sisay × Arena Rector |
| `usoar` | instrumentação de uso da Arena Rector/Sisay, Liliana antiga | `40158b6` | superado por `usoar2` (a Arena Rector é idêntica) | — |
| `usoar2` | idem, política final da Liliana | `9376786`* | usado | log: Sisay × Arena Rector, "o que a Arena Rector entrega" |
| `outlet` | linha deliberada Damn/Void Rend na própria Arena Rector (2 prioridades) | `9376786` | usado | log: Sisay × Arena Rector |
| `rend` | Sisay com a janela de fim de rodada (`@sisay_round_end`; 6 variantes, std + res) | `ff19dd6` | usado | log: "Sisay com a janela de fim de rodada" |
| `motor` | fonte de cada PW que entra em campo (5 variantes, std + res) | `ff19dd6` | usado | log: "Sisay como redundância do motor de PW de graça" |
| `reg`, `reg2`…`reg6` | regressões de 40.000 partidas (20.000 por modo), 0 exceções, 0 travamentos; `reg6` é a final | `4493c19`, interm., `40158b6`, `9376786`*, `9376786`, `ff19dd6` | `reg6` final; demais históricos | log: Validação de cada seção; `resumos/sum_regressao.md` |
| `scryfall_carta_sisay` | JSON da carta Sisay no Scryfall (oráculo lido ao vivo) | — | referência | checklist: Sisay |

\* Estado com o −4 da Liliana corrigido e a chave `arena_rector_outlet` ainda inexistente/desligada: comportamento idêntico ao de `9376786` com as
chaves padrão (a chave nova nasce desligada).

## Mapa: tabela → resumo salvo → comando que a reproduz

Depois de `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git), a partir de `prismatic-bridge-wurbg/` e com `J=resultados-ab/2026-09-29-candidatas-e-sisay/dados_json`:

| resumo salvo (`resumos/`) | comando |
|---|---|
| `sum_final2.md` (Sisay + 4 candidatas, por corte, condicional, sensibilidade, uso) | `python3 ab_candidatas_sum.py $J/main $J/main2 $J/sens $J/sisay $J/sis2 $J/lil $J/lil2` |
| `sec7_final2.md` (seção 7, contra o trio FRA) | `python3 ab_candidatas_vs_fra.py $J/main $J/main2 $J/fra $J/sisay $J/sis2 $J/lil $J/lil2` |
| `sum_pares_final.md` (Sisay por corte e pares) | `python3 ab_pares_sum.py $J/main $J/main2 $J/fra $J/sisay $J/sis2 -- $J/pair $J/pair3 $J/lil $J/lil2` |
| `sum_prof_final2.md` (perfis de mesa) | `python3 ab_perfis_sum.py "Sisay, Weatherlight Captain\|Arena Rector" "Control Body (2/2 lendaria sem texto)\|Arena Rector" mista=$J/main,$J/main2,$J/sens,$J/sisay,$J/sis2,$J/lil,$J/lil2 go_wide=$J/sprof3_go_wide voltron=$J/sprof3_voltron low=$J/sprof3_low` (sem a barra invertida antes do `\|`) |
| `sum_rend.md` (janela de fim de rodada) | `python3 ab_sisay_rend_sum.py $J/main $J/main2 $J/fra $J/sisay $J/sis2 $J/lil $J/lil2 $J/pair $J/pair3 $J/rend` |
| `sum_outlet.md` (linha deliberada da Arena Rector) | `python3 ab_arena_outlet_sum.py $J/main $J/main2 $J/sens $J/sisay $J/sis2 $J/lil $J/lil2 $J/outlet` |
| `sum_usoar2.md` | `python3 arena_uso_sum.py $J/usoar2` |
| `sum_motor.md` (redundância do motor) | `python3 motor_pw_gratis.py sum $J/motor` |
| `sum_regressao.md`, `bitident_*.txt`, `spellbook_*.txt` | saídas dos lotes `reg*`, de `orquestracao/bitident.py` e de `spellbook_antes_depois.py` (com e sem o argumento `sisay`) |

**Ordem dos prefixos importa:** o prefixo posterior sobrescreve a mesma variante no mesmo modo (`std`/`res` se juntam entre lotes).

## Verificações feitas ao arquivar (2026-09-30)

- **Reprodutibilidade:** a partir dos `.json.xz` arquivados, as 7 tabelas `sum_final2`, `sec7_final2`, `sum_pares_final`, `sum_prof_final2`, `sum_rend`, `sum_usoar2`, `sum_motor`
  saíram **byte a byte iguais** às salvas (`cmp` sem diferença). `sum_outlet.md` e `sum_regressao.md` foram gerados da mesma fonte na hora de arquivar.
- **Bit-identidade da lista atual:** `orquestracao/bitident.py 300` compara o módulo atual com o módulo de `1934abf` (último commit antes das
  candidatas: `git show 1934abf:prismatic-bridge-wurbg/prismatic_bridge_goldfish_v1.py > pb_before.py`). Resultado nos `resumos/bitident_*.txt`:
  0 divergências em 300 partidas padrão + 400 de resiliência (4 perfis). `bitident_lil.txt` registra uma execução que **falhou por erro de sintaxe**
  no meio de uma edição (não é resultado; a execução válida é `bitident_final2/3.txt`).
- **Hashes:** `SHA256SUMS` cobre `dados/`, `resumos/`, `orquestracao/`, `indice_dados.py` e `descomprimir.sh`.

## Resumo das conclusões (números completos no log)

- **Sisay no slot da Arena Rector:** −0,086 turno no 1º ultimate (+2,2 pp de P(ult ≤ T8)); resiliência: vida ≤ 0 −0,4 pp, PW-turnos e dano ≥ 40 empatam,
  dano ≥ 120 −1,2 pp. A Arena Rector entrega Ugin/Kaya em 83% dos disparos (resiliência); a Sisay alcança só MV ≤ 6.
- **Contra Tam e Loyal Tutor no mesmo slot** a Sisay perde no ritmo (Loyal Tutor −0,135, Tam −0,119, Sisay −0,086). Como 3ª carta (no lugar do Veil of
  Summer) sobre Tam + Loyal Tutor ela acelera mais que Entrust e Dihada (−0,055), mas não soma resiliência.
- **Janela de fim de rodada da Sisay** (`sisay_round_end`, desligada por padrão): ≤ 0,005 turno no padrão; +0,19 PW-turnos na resiliência.
- **Como redundância do motor de PW de graça:** segundo motor repetível (1,21 PW/partida fora da Bridge até o T10 quando a Bridge sai), mas entra tarde
  (T8) e falha junto com a Bridge (mesmo mana de 5 cores): 12,9% → 14,7% de ter PW de graça até o T8 quando a Bridge não sai até o T6.
- **Correções de premissa minhas registradas:** "a lista não tem outlet de sacrifício" (falso: Liliana −4, Wanderer −4, wipes, Damn, Void Rend, Bolas −3, Ugin +2);
  meu oráculo de memória da Sisay estava errado; o −4 da Liliana sacrificava a Sisay (corrigido).

## Limites conhecidos (Regra #7: escopo do que foi e do que NÃO foi verificado)

- **Só o Prismatic Bridge.** Rodadas anteriores (2026-09-25 e antes) não têm dados brutos preservados (a pasta temporária de cada sessão foi perdida); só as
  tabelas nos logs.
- **Na resiliência o simulador nunca remove a Bridge** (0 de 3.000 partidas); a remoção legada só existe no modo padrão (72% das partidas, parâmetro antigo não validado).
- **Não modelado:** busca da Sisay em resposta a remoção; Bolas −3 e Ugin +2 na própria Arena Rector; chump block deliberado; pagamento real das 5 cores (o arquivo
  usa 1 fonte por cor); combos (o simulador só executa o loop da Vraska).
- **Comparações de "melhor/pior" são pelo simulador (apoio), não pelo jogo real** (Regra #5 do CLAUDE.md).

## Rulings e oráculos lidos ao vivo (Scryfall, 2026-09-29)

- **Sisay, Weatherlight Captain** ({2}{W}, 2/2): *"Sisay gets +1/+1 for each color among other legendary permanents you control. {W}{U}{B}{R}{G}: Search your library for a
  legendary permanent card with mana value less than Sisay's power, put that card onto the battlefield, then shuffle."* Rulings 2019-06-14: (1) se ela sai depois da
  ativação e antes da resolução, usa-se a última informação; (2) {X} de carta na biblioteca vale 0.
- **Arena Rector** ({3}{W}, 1/2): *"When this creature dies, you may exile it. If you do, search your library for a planeswalker card, put it onto the battlefield, then shuffle."*
  Ruling 2018-06-08: se ela sai do cemitério antes de resolver (ficha), não exila e não busca.
- Oráculo de todas as cartas mencionadas: `scryfall-cache/oracle-cache.json` (raiz do repositório).
