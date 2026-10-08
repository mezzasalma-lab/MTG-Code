# 2026-10-08 — pacote Horrigan + Branching Evolution, qual interação cortar, remoções (Drown in the Loch, Atomize...)

Pedido do usuário (2026-10-08): *"Ainda não fizemos nenhuma mudança no deck, o que vc me sugere? Abrir mão de interação por Remoção?"* e, depois, *"Termine o trabalho por favor"*.
**Nada foi cortado nem adicionado na lista do usuário** (`lista.md` intacta); o simulador **não foi alterado** (`codigo/` é uma cópia congelada do vivo de 2026-10-07, `cmp` igual a `../2026-10-07-candidatas-stefano-2/codigo/mothman_goldfish_v1_C2.py`).

## Conclusão (o que o A/B mede; o resto é raciocinado e está marcado)

Base: mesa limpa até T8 **51,3% (padrão) / 24,0% (resiliência)**, T10 85,0% / 58,1%, deck-out 3,25% / 1,56%. N = 10.000 por variante e modo, pareado, `no lugar` (`SWAP_IN_PLACE`), sementes 3.000.000+i, 12 turnos. `*` = excede o IC95% pareado.

| pacote (entra ← sai) | T8 padrão | T8 resiliência | T10 padrão / resil. | deck-out padrão |
|---|---|---|---|---|
| Horrigan ← Offer (sozinho) | +2,37 ± 0,37 * | +0,99 ± 0,30 * | +0,85 * / +0,67 * | −0,47 * |
| Branching ← Negate (sozinho) | +1,88 ± 0,38 * | +0,93 ± 0,31 * | +0,48 / +0,40 * | −0,17 |
| **p1: Horrigan ← Offer + Branching ← Negate** | **+4,02 ± 0,50 \*** | **+1,85 ± 0,42 \*** | +1,09 \* / +1,02 \* | −0,41 \* |
| p2: Horrigan ← Offer + Branching ← Didn't Say Please | +4,10 ± 0,49 * | +1,90 ± 0,40 * | +1,38 * / +1,50 * | −0,52 * |
| p3: Horrigan ← Offer + Branching ← Wave Goodbye | +3,48 ± 0,49 * | +1,98 ± 0,41 * | +0,88 * / +1,34 * | −0,38 * |
| p4: … + Branching ← Toxic Deluge | +3,45 ± 0,49 * | +1,91 ± 0,40 * | +0,74 * / +1,38 * | −0,27 |
| p5: … + Branching ← Tear Asunder | +3,54 ± 0,49 * | +1,92 ± 0,40 * | +0,86 * / +1,27 * | −0,42 * |
| p6: … + Branching ← Arcane Denial | +3,60 ± 0,49 * | +1,60 ± 0,42 * | +0,88 * / +1,07 * | −0,59 * |

- **Os dois ganhos quase se somam:** p1 = +4,02 / +1,85 contra a soma dos individuais +4,25 / +1,92 (diferente das seis candidatas da rodada anterior, que juntas davam 72% da soma). Leitura (raciocinada, não medida por decomposição): o Horrigan (proliferate ×2) põe contadores que o Branching Evolution dobra, então um reforça o outro em vez de disputar o mesmo recurso.
- **O 2º corte quase não muda a velocidade** (`resumos/pacotes_entre_si.md`, diferença direta pareada): no padrão, cortar Negate (p1) ou Didn't Say Please (p2) rende ≈ +0,5 ponto a mais que cortar Wave Goodbye, Deluge ou Tear Asunder (p1−p3 +0,54 ± 0,46 *, p1−p4 +0,57 *, p1−p5 +0,48 *; p1−p6 +0,42 e p1−p2 −0,08 dentro do IC); na resiliência as seis variantes empatam (|dif| ≤ 0,25, dentro do IC).
- **O que a interação "custa" no simulador** (modo resiliência, média por partida; base: 0,689 contramágicas conjuradas, 0,182 proteções usadas, 0,838 peças do meu motor removidas por remoção pontual do oponente, 0,654 wipes que pegaram): p1 = −0,25 contramágicas, −0,05 proteções, **+0,04 peças removidas**, −0,01 wipes. p3 (cortar Wave Goodbye em vez de Negate) = −0,15 / −0,03 / +0,02. Ou seja, cortar duas contramágicas custa ≈ 4 peças de motor a cada 100 partidas nesse modelo. O oponente é o proxy do repositório (7 categorias, 1/3 de atenção por turno): **apoio, não árbitro**.
- **Cemitério do oponente** (`resumos/gy_oponentes.md`; relevante para Drown in the Loch, que conta o cemitério do CONTROLADOR do alvo): só com o que o MEU mill põe lá, mediana de cartas por oponente vivo no fim do meu turno, padrão: T4 1, T5 2, T6 4, T7 6, T8 7; com ≥ 5 cartas: T4 10%, T5 23%, T6 44%, T7 60%; o oponente mais cheio da mesa tem ≥ 5 em T5 33%, T6 60%. Resiliência é um pouco menor (T6 39% com ≥ 5). É **piso**: os oponentes do simulador são passivos (nenhuma magia, nenhuma criatura morta), o cemitério real tem também o que eles mesmos jogam; e a partir de T7 a amostra é de oponentes que ainda estão vivos. Leitura (raciocinada): Drown seria resposta de T6+ neste deck, não de T3/T4.
- **Spellbook** (99 nomes reconhecidos, 0 não reconhecidos; controle positivo e de corte OK): base = 2 combos (Ascension + Mindcrank; Altar of Dementia + Great Henge [+ Glen Elendra]); o pacote exato (−Offer −Negate +Horrigan +Branching) não cria nem derruba combo; Drown in the Loch, Assassin's Trophy, Putrefy, Beast Within, Deadly Rollick, Atomize e Casualties of War também não criam. "Quase" novo com o pacote: **Branching Evolution + Walking Ballista + (Vigor ou Rite of Passage)**; nenhuma das duas está na lista (oráculos no `scryfall-cache`).

## O que NÃO foi verificado (Regra #7)
- O valor de interação contra oponente real (remoção sobre o permanente do oponente é estrutural no goldfish: "Destroy target creature…" depende de alvo no tabuleiro dele). Drown in the Loch, Atomize, Assassin's Trophy, Putrefy, Beast Within, Deadly Rollick e Casualties of War **não estão implementados** no simulador: o que se diz delas vem do oráculo, das rulings (`dados/rulings_remocoes.json`), do Spellbook e do cemitério acima, não de A/B.
- Nenhuma terceira troca, nenhum pacote com Loading Zone/Earth Crystal/Fractured/Tide/Scorchbeast junto com Horrigan + Branching, e o pacote com o Master, Transcendent (Horrigan + Master já foi medido na rodada do Stefano: +2,65). Só os 9 cenários acima.
- Uma única família de sementes (3.000.000+i) por variante; as prioridades de conjuração (Horrigan 71, Branching 70) continuam sem sensibilidade (rodada anterior).
- O cemitério do oponente real (as magias que ele joga, criaturas que morrem), a MV dos alvos reais e a ordem humana de jogo.

## Validação desta rodada
- Smoke (`resumos/smoke_pacote.txt`): 9 variantes, 99 cartas, 0 desconhecidas, 0 duplicadas, 0 exceções em 200 partidas × 2 modos.
- Testes dirigidos do simulador vivo: 194/194 (nenhum código mudou).
- **Replicação (`resumos/replicacao.txt`): 4/4 séries bit-idênticas** (a `base` e a `Branching ← Negate` daqui == as de `candidatas-stefano-2`, 10.000 partidas × 2 modos, fingerprint + todos os campos): o simulador congelado é o mesmo e o harness retomável não mudou nada.
- Regressão (`resumos/regressao_pacote_20000.txt`): 20.000 partidas × 2 modos × 2 pacotes (p1, p3), sementes 5.000.000+i: **0 exceções**, 0 carta acima do baralho, 0 campo negativo.
- Determinismo (`resumos/determinismo.txt`): p1, 3 `PYTHONHASHSEED` (11/22/33) × 1.500 sementes × 2 modos: **0 divergências**.
- **Reprodutibilidade (`resumos/verificacao_reproducao.txt`): 6/6 iguais** (as cinco saídas refeitas só dos brutos batem no `cmp`; base e p1, 1.000 sementes × 2 modos, re-simuladas com o simulador congelado: 4.000/4.000 partidas idênticas ao bruto).

## Incidentes (para quem audita)
- O worker reiniciou **duas vezes** durante a rodada (≈ 00:40 UTC e ≈ 13:36 UTC): derrubou o 1º lote do A/B, a 1ª medição de cemitério e a 1ª verificação da rodada anterior. O `driver_mm.py` desta pasta ganhou **retomada por variante** (parcial por variante; cada variante é independente, mesmas sementes, então reaproveitar é exato; os arquivos `*_parcial` foram apagados depois que o bruto final foi gravado, e o `replicacao.txt` prova que o resultado não mudou).
- Bug meu em `gy_opp.py`: o caminho de saída relativo era resolvido depois do `chdir` que o `abgen.carrega` faz para a pasta do deck (o 1º lote de cemitério morreu ao gravar); corrigido com `os.path.abspath` antes do `carrega`.
- Bug meu em `resimula_amostra.py` (2 iterações): o bruto guarda só 12 caracteres do fingerprint e preenche com 0,0 os campos ausentes numa partida; a 1ª comparação (0/1000) e a 2ª (42/1000) eram falsos negativos do comparador, não do simulador; a versão final compara o prefixo de 12 caracteres e os campos preenchidos (1000/1000 nas 4 séries).

## Mapa arquivo → o que é → status → saída
| arquivo | o que é | status | alimenta |
|---|---|---|---|
| `dados/raw_pacote_10000.json.xz`, `dados/raw_pacote_10000_resiliencia.json.xz` | bruto por partida (colunas-v1, 313 campos numéricos): 9 variantes × 10.000, modo padrão / resiliência | usado | `resumos/tabela_pacote.md`, `pacotes_entre_si.md`, `replicacao.txt` |
| `dados/gy_oponentes_padrao.json.xz`, `dados/gy_oponentes_resiliencia.json.xz` | cemitério de cada oponente no fim de cada turno meu, 10.000 partidas por modo | usado | `resumos/gy_oponentes.md` |
| `dados/spellbook_pacote.json`, `resumos/log_spellbook_pacote.txt` | Commander Spellbook com resolução de nomes e controles | usado | seção "Spellbook" acima |
| `dados/rulings_remocoes.json` | oráculo + rulings ao vivo (Scryfall) de Drown in the Loch, Atomize, Deadly Rollick, Assassin's Trophy (15 rulings) | usado | goldfish-log §16, checklist §15 |
| `codigo/mothman_goldfish_v1_estado_2026-10-08.py` | simulador congelado (== vivo de 2026-10-07) | usado | todas as séries |
| `resumos/*` | `tabela_pacote.md`, `pacotes_entre_si.md`, `gy_oponentes.md`, `replicacao.txt`, `compacto_pacote_10000[_resiliencia].txt`, `pacote_10000[_resiliencia].txt` (saída do driver), `smoke_pacote.txt`, `regressao_pacote_20000.txt`, `determinismo.txt`, `verificacao_reproducao.txt`, `indice_dados.md`, logs | usado | — |
| `orquestracao/*` | `gera_config.py` → `config_pacote.json`; `lanca_tudo.sh`, `lanca_gy.sh`, `lanca_reg.sh`; `driver_mm.py` (retomável), `abgen.py`; `gy_opp.py`, `rank_pacote.py`, `compara_pares.py`, `resumo_gy.py`, `confere_replicacao.py`, `csb_pacote.py`, `csb_stefano.py`, `resimula_amostra.py`, `verificar_reproducao.sh` | usado | — |
| `indice_dados.py`, `descomprimir.sh` | índice dos dados e descompressão | usado | `resumos/indice_dados.md` |

## Como refazer cada tabela
Dentro de `orquestracao/` (nada precisa do simulador, só dos `.json.xz`): `python3 rank_pacote.py > ../resumos/tabela_pacote.md` · `python3 compara_pares.py > ../resumos/pacotes_entre_si.md` · `python3 resumo_gy.py > ../resumos/gy_oponentes.md` · `python3 confere_replicacao.py > ../resumos/replicacao.txt` · de dentro da pasta: `python3 indice_dados.py > resumos/indice_dados.md` · tudo + a re-simulação de amostra: `bash orquestracao/verificar_reproducao.sh --tudo`.
Refazer os brutos: `python3 gera_config.py && bash lanca_tudo.sh && bash lanca_gy.sh` (≈ 1 h de CPU em 4 núcleos; `PYTHONHASHSEED=0` é fixado pelo driver). Spellbook: `python3 csb_pacote.py ../../../lista.md ../dados/spellbook_pacote.json`.
