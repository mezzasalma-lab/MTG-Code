# 2026-10-10 — Mothman: Underground Sea sem tirar o Bojuka Bog (qual terreno sai no lugar?)

Pedido do usuário (2026-10-10), depois de eu propor Bojuka Bog → Underground Sea: *"Não queria tirar a Bojuka não, tem outra opção?"*. **Nada foi alterado na lista nem no simulador** (`lista.md` e `mothman_goldfish_v1.py` iguais ao commit `af2bbb7`; `codigo/mothman_goldfish_v1_ANTES.py` == o vivo, `cmp` igual no momento da cópia). Tudo aqui é medição e recomendação; a troca só entra com um "sim" do usuário.

## Conclusão (medido × raciocinado)

N = 10.000 por variante e modo, pareado, trocas `no lugar` (`SWAP_IN_PLACE`: a permutação do baralho não muda), sementes 3.000.000+i, 12 turnos; `*` = excede o IC95%. Base = a lista atual (Tropical Island no lugar da Swarmyard): comandante até T4 65,4% / 60,1%, mesa limpa até T8 59,6% / 28,0% (padrão / resiliência). Cada variante troca **um** terreno pelo Underground Sea.

| sai → Underground Sea | comandante até T4 (pad. / res.) | mesa limpa T8 (pad. / res.) | fontes efetivas B / G / U (hoje 16 / 19 / 16) | o que se perde (oráculo) |
|---|---|---|---|---|
| **Bojuka Bog** (a proposta anterior, referência) | +1,28 \* / +1,25 \* | **+1,19 \* / +0,63 \*** | 16 / 19 / 17 | o tira-cemitério |
| **Swamp** (um dos 3) | **+0,73 \* / +0,75 \*** | **+0,74 \* / +0,22** | 16 / 19 / **17** | só o ser terreno **básico** |
| **Strip Mine** | **+1,72 \* / +1,50 \*** | +0,53 \* / +0,59 \* | 17 / 19 / 17 | destruir terreno; sacrificar para o laço Icetill / Gitrog; o crime |
| **Urza's Saga** | **+1,90 \* / +1,76 \*** | +0,38 / +0,24 (ruído) | 17 / 19 / 17 | os Construct e a busca de artefato |
| Minamo | +0,67 \* / +0,61 \* | +0,50 \* / +0,03 | 17 / 19 / 16 | desvirar uma lendária (Great Henge, Zellix, Cauldron) |
| Island (um dos 4) | +0,51 \* / +0,56 \* | +0,43 \* / +0,41 \* | 17 / 19 / 16 | só o ser básico |
| Shifting Woodland | +0,75 \* / +0,69 \* | +0,22 / +0,24 (ruído) | 17 / 18 / 17 | uma fonte de G; a cópia de permanente do cemitério |
| Takenuma | +0,70 \* / +0,57 \* | +0,25 / +0,20 (ruído) | 16 / 19 / 17 | o canal (mila 3 e devolve criatura / planeswalker) |
| Boseiju | +0,87 \* / +0,72 \* | +0,04 / +0,22 (ruído) | 17 / 18 / 17 | o canal (destrói artefato / encantamento / terreno não básico) |
| Zagoth Triome | −0,07 / −0,12 (T4); T5 −0,50 \* / −0,66 \* | +0,90 \* / +0,02 | 16 / 18 / 16 | uma fonte de G; o ciclo |
| Watery Grave | 0,00 / 0,00 | −0,04 / −0,02 (nulo) | 16 / 19 / 16 | **nada** (é o Sea com o imposto de 2 vida) |
| Morphic Pool | +0,02 / +0,01 | +0,06 / +0,01 (nulo) | 16 / 19 / 16 | **nada na mesa de 4** (desvira com 2+ oponentes) |

(`resumos/tabela_u.md`, `tabela_u2.md` (Urza's Saga), `fontes_por_cor.md`; todas as colunas de T3 a T10 e as de atividade estão lá.)

1. **Resposta: sim, tem. Recomendo trocar um Swamp** (o que mais convém sem abrir mão de nenhuma função): o Underground Sea é um Swamp que também dá `{U}` e desvira sempre, então a mana só melhora (fontes efetivas de U 16 → 17; na auditoria de 2026-10-05 G e U eram as cores apertadas, razão fontes / cartas U 0,76, B 1,45, G 0,62; não recontei as razões com a lista de hoje). Medido contra a base: comandante até T4 **+0,73 ± 0,20 \* / +0,75 ± 0,21 \***, T8 +0,74 ± 0,36 \* / +0,22 ± 0,34 (resiliência, ruído). **Contra o Bojuka Bog diretamente**, o Swamp rende menos: −0,55 ± 0,29 \* no comandante até T4 e −0,45 ± 0,44 \* no T8 do modo padrão (`resumos/pares_diretos.md`); no T8 da resiliência a diferença cabe no ruído (−0,41 ± 0,42). Ou seja, **manter o Bog custa cerca de meio ponto**, não mais.
2. **O que o Swamp perde de verdade:** ele é terreno **básico**; o Sea não é (rulings de 2008-10-01: "tem os tipos básicos mas não é básico"). Isso importa contra Wasteland / Blood Moon / Back to Basics no pod, que o simulador **não modela**. O resto não muda: a Prismatic Vista fica com 2 Swamps como alvo, mas a Polluted Delta e a Verdant Catacombs buscam o próprio Sea (tipo Swamp) e a Misty Rainforest também (tipo Island); Nature's Lore, Three Visits e a Shifting Woodland não leem Swamp.
3. **Se a prioridade for ter o comandante em T4:** Strip Mine (+1,72 / +1,50) e Urza's Saga (+1,90 / +1,76) são os que mais aceleram, porque são incolores e o Sea dá duas cores. Mas o T8 deles é menor (Strip Mine +0,53 \* / +0,59 \*; Saga no ruído) e **cada um tira uma função real**: a Strip Mine é o crime do Deepmuck / Freestrider, o laço Icetill + Gitrog (sacrifica, volta pelo cemitério, compra) e a única que destrói QUALQUER terreno (o Boseiju só pega não básico); a Saga é o Construct e a busca de Sol Ring / Lantern. Contra o Swamp, a Strip Mine ganha +0,99 ± 0,33 \* no T4 e empata no T8 (+0,21 pelo Swamp, ruído).
4. **A troca sem perda nenhuma:** Watery Grave → Underground Sea. O Sea é o Watery Grave sem o imposto: mesmo `{U}`/`{B}`, mesmos tipos (Island Swamp), mas **desvira sem pagar 2 de vida**. A mana não muda (por isso o 0,00 de velocidade, esperado e não prova de inutilidade); o que muda é a vida: **vida mínima +0,78 ± 0,02 (padrão) / +0,76 ± 0,02 (resiliência)** por partida (`tabela_u.md`, atividade). É uma melhoria pequena e segura, mas **não acelera nada**. O Morphic Pool é igual na mesa de 4 (desvira com 2+ oponentes; com 1 só oponente restante entra virado, ruling de 2018-06-08), então também dá 0 de velocidade; a vida mínima sobe +0,20.
5. **Não recomendo:** Zagoth Triome (perde G, o comandante em T4/T5 piora), Shifting Woodland (perde G e a cópia), Takenuma, Boseiju (o T8 fica em ruído e perde-se a função), Minamo (T8 da resiliência 0).
6. **Spellbook** (`dados/spellbook_under.json`, `resumos/log_spellbook_under.txt`): 93 nomes resolvidos (não reconhecidos: nenhum), 2 combos na base (Bloodchief Ascension + Mindcrank; Altar of Dementia + The Great Henge); **nenhuma das 12 trocas cria ou derruba combo** (0 novos, 0 perdidos). Tirar a Shifting Woodland derruba um "quase" combo, Shifting Woodland + Time Vault, que não existe na lista (o Time Vault não está nela). Controle positivo (Thassa's Oracle + Demonic Consultation aparece) e de corte (sem o Mindcrank some Ascension + Mindcrank) ok. O Underground Sea não é Game Changer (`game_changer` = false, Scryfall ao vivo).

**Minha recomendação, com o raciocínio:** *Swamp → Underground Sea* se você quer a melhora de mana sem perder nenhuma função (e aceita o risco de ser terreno não básico); *Watery Grave → Underground Sea* se quer só a melhora de vida sem mexer em nada; *Strip Mine → Underground Sea* só se a remoção de terreno e o laço Icetill/Gitrog valem menos para você que o T4 (+1,7). Não foi aplicado nada.

## Escopo verificado e NÃO verificado (Regra #7)

**Verificado, com método:** (a) os 12 candidatos a sair, incluindo todos os terrenos que produzem 2+ cores ou têm função, por A/B pareado de 10.000 × 2 modos; (b) oráculo e rulings ao vivo dos candidatos (`dados/rulings_candidatos.json`: Watery Grave, Morphic Pool, Minamo, Shifting Woodland, Zagoth Triome, Strip Mine, Takenuma, Boseiju, Bojuka Bog, Swamp, Island, Underground Sea); (c) a documentação do deck (`auditoria.md`, `checklist-oraculo.md`, `goldfish-log.md`) lida com grep de "combo", "infinit", "loop" e do nome de cada candidata, e o Spellbook com a lista de cada troca (Regra #4 e adendo); (d) as fontes por cor, contadas por script no `CARD_DB` do simulador congelado.
**NÃO verificado:** Blood Moon / Wasteland / Back to Basics contra o Sea e contra qualquer terreno não básico (estado de oponente, estrutural); o valor da Strip Mine contra uma mesa real (o simulador só conta o crime e o laço; o "destroy target land" é proxy); o Urza's Saga (Construct e busca) e o Boseiju / Takenuma (canal só com alvo) contra oponente real; só uma família de sementes; não medi duas trocas ao mesmo tempo (só há um Underground Sea); as comparações diretas entre candidatos fora das oito de `pares_diretos.md`; Overgrown Tomb, Breeding Pool, Rejuvenating Springs e Undergrowth Stadium (todas perdem a cor G, a mais exigida: 33 cartas com pip de G na análise de 2026-10-08), a Command Tower (dá as três cores), a Plaza of Heroes e a Waterlogged Grove (já tinham piorado a lista em 2026-10-08/09 quando trocadas por básicos), as fetches, o Agadeem e os básicos Forest não foram candidatos neste lote.

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| smoke (99 cartas, 90 distintas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos sem exceção) | ok nas 12 listas | `resumos/smoke_under.txt` |
| replicação cruzada com `../2026-10-09-swarmyard-tropical`: `base` == e1; **`u0_bojuka_bog` == e2 (a mesma lista obtida por dois caminhos)**; base do U2 == base do U | **6/6 séries**, 10.000 partidas cada, 0 divergências | `resumos/replicacao.txt` |
| reprodutibilidade (`orquestracao/verificar_reproducao.sh --tudo`) | **7/7** saídas iguais com `cmp` (as duas tabelas, as comparações diretas, as fontes por cor, a replicação, o índice, e a re-simulação de base, u1, u3 e u8: 1.000 sementes × 2 modos = 8/8 séries 1000/1000) | `resumos/verificacao_reproducao.txt` |

Sem mudança de código nem de lista, não há bit-identidade, regressão de 20.000 nem determinismo novos a rodar: o simulador congelado é o do commit `af2bbb7`, já validado nessas frentes na rodada de `../2026-10-09-swarmyard-tropical`. (Regra #10, item 4: nenhuma verificação é vazia: as séries têm 10.000 partidas, o A/B tem diferenças com IC, o Spellbook tem 2 combos na base e os dois controles.)

## Mapa arquivo → o que é → status → tabela que o usa

| arquivo (`dados/`) | o que é | status | usado em |
|---|---|---|---|
| `raw_under_10000[_resiliencia].json.xz` | lote **U**: base + u0 Bojuka Bog, u1 Watery Grave, u2 Morphic Pool, u3 Swamp, u4 Island, u5 Minamo, u6 Shifting Woodland, u7 Zagoth Triome, u8 Strip Mine, u9 Takenuma, u10 Boseiju (cada um → Underground Sea) × 2 modos | usado | `resumos/tabela_u.md`, `pares_diretos.md` |
| `raw_under2_10000[_resiliencia].json.xz` | lote **U2**: base + u11 Urza's Saga → Underground Sea × 2 modos (candidato que faltou no U; a base repete a do U bit a bit) | usado | `resumos/tabela_u2.md`, `pares_diretos.md` |
| `rulings_candidatos.json` | oráculo + rulings (Scryfall, 2026-10-10) dos 12 terrenos | usado | acima |
| `spellbook_under.json` | Commander Spellbook (93 nomes, 12 trocas, 2 controles) | usado | acima |

Nenhum lote foi superado nem invalidado. Os `*_parcial.json.xz` e `*.done` do driver retomável foram apagados depois de os lotes fecharem.

## Como refazer

```
bash descomprimir.sh                                                  # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 rank_proxy.py under | cmp - ../resumos/tabela_u.md           # idem: under2 -> tabela_u2.md
python3 compara_candidatos.py | cmp - ../resumos/pares_diretos.md
python3 fontes_por_cor.py | cmp - ../resumos/fontes_por_cor.md
python3 confere_replicacao.py | cmp - ../resumos/replicacao.txt
(cd .. && python3 indice_dados.py | cmp - resumos/indice_dados.md)
bash verificar_reproducao.sh --tudo                                    # tudo acima + re-simulação (PYTHONHASHSEED=0; NÃO editar o simulador congelado enquanto roda)
sha256sum -c ../SHA256SUMS
```

Gerado por `orquestracao/`: `lanca_tudo.sh` (lote U), `lanca_u2.sh` (lote U2), `driver_mm.py` (retomável por variante; `LOTES`, `TAG`, `MODOS`), `abgen.py` (harness, formato `colunas-v1`), `gera_config.py` e `gera_config2.py` (`config_u.json`, `config_u2.json`), `csb_under.py` + `csb_stefano.py` (Spellbook), `fontes_por_cor.py`, `compara_candidatos.py`, `confere_replicacao.py`, `resimula_amostra.py`. Sintaxe das variantes: `{"SWAPS": [["saiu","entrou"], …], "SWAP_IN_PLACE": true}`.

## Incidentes

- O Urza's Saga não estava na primeira lista de candidatos do lote U; entrou num lote U2 com a base repetida, e a base do U2 é bit-idêntica à do U (`replicacao.txt`, linha 3), então as duas tabelas comparam as mesmas partidas.
