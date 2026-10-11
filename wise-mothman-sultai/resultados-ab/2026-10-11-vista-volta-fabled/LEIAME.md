# 2026-10-11 — Mothman: Prismatic Vista → Fabled Passage (a Fabled volta)

Pedido do usuário (2026-10-11): depois de eu explicar que a Prismatic Vista só acelera os primeiros turnos e custa 1 de vida, *"Quer que eu volte?"* → *"Sim"*. **Lista APLICADA** em `lista.md` e no `DECKLIST_TEXT` do simulador, trocada NO LUGAR (a linha `1 Prismatic Vista` virou `1 Fabled Passage` na mesma posição, que era a da Fabled Passage original). A lista anterior está em `../../lista-anterior-2026-10-11.md`. A Prismatic Vista continua no `CARD_DB` e implementada (volta por `SWAPS=(("Fabled Passage","Prismatic Vista"),)`).

## Conclusão (medido × raciocinado)

N = 10.000 por variante e modo, pareado, `no lugar`, sementes 3.000.000+i, 12 turnos; `*` = excede o IC95%. Base = a lista de antes (com a Vista). **Custo da volta** (`resumos/base_nova.md`, `tabela_w.md`; nova / anterior / diferença pareada; padrão | resiliência):

| | padrão | resiliência |
|---|---|---|
| comandante até T3 | 15,29% / 15,73% / **−0,44 ± 0,18 \*** | 14,24% / 14,65% / **−0,41 ± 0,17 \*** |
| comandante até T4 | 65,96% / 66,17% / −0,21 ± 0,20 \* (no limite) | 60,61% / 60,87% / −0,26 ± 0,21 \* |
| mesa limpa até T8 | 59,95% / 60,31% / **−0,36 ± 0,28 \*** | 28,12% / 28,19% / −0,07 ± 0,27 (ruído) |
| mesa limpa até T10 | 89,08% / 89,25% / −0,17 ± 0,16 \* | 62,70% / 62,89% / −0,19 ± 0,28 (ruído) |
| 1º oponente fora até T6 | 45,42% / 45,93% / −0,51 ± 0,27 \* | 27,55% / 27,93% / −0,38 ± 0,25 \* |
| deck-out | 2,69% / 2,62% / +0,07 (sem efeito) | 1,38% / 1,44% / −0,06 (sem efeito) |
| vida mínima (média) | 32,96 / 32,63 / **+0,32 ± 0,02 \*** | 30,73 / 30,41 / **+0,33 ± 0,03 \*** |

1. **Por que a Fabled custa o que custa:** o texto (Scryfall) diz que o básico entra **virado** e só desvira com 4 ou mais terrenos; a Vista o põe desvirado sempre, mas paga 1 de vida. Nos turnos 1 a 3 a Fabled quase nunca tem as 4 terras, daí o −0,4 no comandante em T3; do T4 em diante as duas rendem o mesmo e a Fabled poupa a vida. O custo é pequeno e fica concentrado no começo, como o §19 já previa (isoladamente a Vista rendia +0,52 em T3 e +0,50 em T8 do padrão).
2. **Ganho:** +0,32 / +0,33 de vida mínima por partida e nenhuma carta a mais para proxiar (a Fabled é a carta original da lista).
3. **Nova linha de base** (padrão / resiliência): comandante até T4 **66,0% / 60,6%**, até T5 78,8% / 73,0%; mesa limpa até T7 18,7% / 7,3%, **T8 60,0% / 28,1%**, T10 89,1% / 62,7%; 1º oponente fora até T6 45,4% / 27,6%; deck-out 2,69% / 1,38%. O simulador vivo com `SWAPS=()` é a lista aplicada (bit-idêntico ao ANTES + w1 `no lugar`: 20.000/20.000, `resumos/bitident_lista.txt`).
4. **Spellbook** (`dados/spellbook_viva.json`, `resumos/log_spellbook_viva.txt`): 92 nomes resolvidos (não reconhecidos: nenhum), a lista viva == a anterior com a troca; antes 2 combos, depois 2 combos: **0 novos, 0 perdidos, 0 "quase" criados ou derrubados**; controle positivo (Thassa's Oracle + Demonic Consultation) e de corte (sem o Mindcrank some Ascension + Mindcrank) ok. A Fabled Passage não é Game Changer; o Bracket não muda.

## O que mudou no simulador

**Nenhuma regra nova.** Só a lista: `DECKLIST_TEXT` (`1 Prismatic Vista` → `1 Fabled Passage`) e `lista.md`. A Fabled Passage já tinha o comportamento do oráculo no simulador (`crack_fetch`: básico virado; com 4+ terrenos, contando o buscado, desvira; sem custo de vida; teste `fabled_passage_desvira_com_4_terrenos`).
Testes (`../../testes/testes_dirigidos.py`, **208/208**): o teste de partidas completas dos terrenos passou a pôr a Vista por `SWAPS` (ela saiu da lista e o teste exige vê-la em jogo); o teste da lista foi atualizado (Bayou e Fabled Passage dentro; Hollow e Vista fora); teste novo `lista_viva_tem_fabled_passage_e_nao_a_vista_e_a_vista_volta_por_swaps` (a Vista volta no mesmo índice da biblioteca).

## Escopo verificado e NÃO verificado (Regra #7)

**Verificado:** a biblioteca viva == a do A/B (bit-identidade em 20.000 comparações); o comportamento da Fabled no código contra o texto do oráculo (ruling de 2020-06-23: o terreno buscado conta para as 4); as etiquetas `fabled_passage` e `vista` lidas só em `crack_fetch` (grep).
**NÃO verificado:** o valor de poupar 1 de vida contra aggro real (a vida só entra no deck-out e na vida mínima); só uma família de sementes.

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| testes dirigidos | **208/208** (1 novo; 2 adaptados) | `../../testes/testes_dirigidos.py` |
| smoke (99 cartas, 91 distintas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos sem exceção) | ok | `resumos/smoke_vista.txt`, `smoke_vivo.txt` |
| bit-identidade: vivo `SWAPS=()` == ANTES congelado + w1 `no lugar` | 20.000/20.000 (4 fatias × 2.500 sementes × 2 modos, sementes 9.600.000+) | `resumos/bitident_lista.txt` |
| replicação cruzada: `base` daqui == `u3_swamp` de `../2026-10-10-underground-sea-sem-bojuka` (a mesma lista por outro caminho) | **2/2 séries**, 10.000 partidas cada | `resumos/replicacao.txt` |
| regressão 20.000 × 2 modos, sementes 5.000.000+i, simulador VIVO | 0 exceções, 0 carta acima do baralho, 0 contador negativo | `resumos/regressao_vivo_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos (vivo; vivo com `COMMANDER_REMOVAL_SHARE=0.5`) | 0 divergências nos 2 casos | `resumos/determinismo.txt` |
| reprodutibilidade (`orquestracao/verificar_reproducao.sh --tudo`) | **5/5** saídas iguais com `cmp` (tabela, base nova, replicação, índice, e a re-simulação de base e w1: 1.000 sementes × 2 modos = 4/4 séries 1000/1000) | `resumos/verificacao_reproducao.txt` |

## Mapa arquivo → o que é → status

| arquivo (`dados/`) | o que é | status |
|---|---|---|
| `raw_vista_10000[_resiliencia].json.xz` | A/B: `base` (lista com a Vista) e `w1_vista_fabled` (a troca) × 2 modos, N = 10.000 | usado em `tabela_w.md`, `base_nova.md` |
| `spellbook_viva.json` | Commander Spellbook da lista exata (antes × depois) | usado |

Nenhum lote foi superado nem invalidado. Os `*_parcial.json.xz` e `*.done` do driver retomável foram apagados.

## Como refazer

```
bash descomprimir.sh                                                  # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 rank_proxy.py vista | cmp - ../resumos/tabela_w.md
python3 base_nova.py | cmp - ../resumos/base_nova.md
python3 confere_replicacao.py | cmp - ../resumos/replicacao.txt
bash verificar_reproducao.sh --tudo                                    # tudo acima + re-simulação (PYTHONHASHSEED=0; NÃO editar o simulador congelado enquanto roda)
sha256sum -c ../SHA256SUMS
```

Gerado por `orquestracao/`: `lanca_ab.sh` (A/B), `lanca_validacao.sh` (smoke, regressão, determinismo), `driver_mm.py`, `abgen.py`, `gera_config.py` (`config_w.json`), `config_vivo.json`, `bitident_lista.py`, `csb_viva.py` + `csb_stefano.py`, `base_nova.py`, `confere_replicacao.py`, `resimula_amostra.py`.
