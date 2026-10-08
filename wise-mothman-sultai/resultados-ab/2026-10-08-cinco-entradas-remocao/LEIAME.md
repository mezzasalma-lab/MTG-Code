# 2026-10-08 — Frank + Branching + Atomize + Casualties of War + Assassin's Trophy: implementação, A/B dos 5 cortes, Spellbook

Pedido do usuário (2026-10-08): *"Quero Frank e Branching no deck, bem como atomize, casualties of war e mais uma remoção de permanente"*.
**A lista do usuário (`lista.md`) NÃO foi alterada.** Os cinco cortes são recomendação; a lista proposta está em `lista_proposta_s4.md` (gerada por `orquestracao/gera_lista_proposta.py`, 99 + comandante, legalidade e identidade de cor conferidas no cache) e só vira a lista oficial se o usuário confirmar os cortes.
A "mais uma remoção de permanente" foi escolha minha: **Assassin's Trophy** `{B}{G}` instantâneo, "destroy target permanent an opponent controls" (alternativas lidas ao vivo e descartadas: Beast Within dá um 3/3 ao oponente; Putrefy só pega artefato ou criatura; Abrupt Decay só MV ≤ 3; Maelstrom Pulse é feitiço e não pega terreno; Vraska's Contempt só criatura ou planeswalker).

## O que mudou no simulador (`codigo/mothman_goldfish_v1_ANTES.py` → `mothman_goldfish_v1_DEPOIS.py`; patch em `orquestracao/patch_remocoes.py`)
Atomize, Casualties of War e Assassin's Trophy entram por `SWAPS` (com `SWAPS=()` o arquivo é bit-idêntico ao ANTES). Cláusula a cláusula e rulings: `checklist-oraculo.md` §16. Em resumo: o "destroy" sobre permanente de oponente é estrutural (crime + métrica `interaction_plays` quando `target_available`); o **proliferate do Atomize é real**; a **busca do Trophy é real** no que o simulador rastreia (−1 terreno na biblioteca do oponente-alvo, +1 terreno dele em campo); o custo `{2}{B}{B}{G}{G}` do Casualties vem dos pips. As três entram em `act_removal_proxy` (uma remoção por turno, com mana sobrando e alvo disponível).

## Resultado (mesa limpa até T8, pontos percentuais, N = 10.000 pareado, `no lugar`, sementes 3.000.000+i, 12 turnos; base 51,3% padrão / 24,0% resiliência; `*` = excede o IC95%)
Em todos os conjuntos saem Offer e Negate; as 3 vagas variáveis entre parênteses.

| conjunto (saem também) | T8 padrão | T8 resiliência | T10 padrão / resil. | deck-out padrão / resil. |
|---|---|---|---|---|
| só Frank + Branching (p1) | +4,02 ± 0,50 * | +1,85 ± 0,42 * | +1,09 * / +1,02 * | −0,41 * / −0,07 |
| só as 3 remoções, sem o par (V.A.T.S., Wave Goodbye, Toxic Deluge saem) | +0,23 ± 0,16 * | +0,15 ± 0,14 * | +0,08 / +0,11 | −0,02 / +0,03 |
| s1: V.A.T.S., Wave Goodbye, Toxic Deluge | +4,33 ± 0,52 * | +2,07 ± 0,44 * | +1,15 * / +1,17 * | −0,47 * / −0,09 |
| s2: V.A.T.S., Arcane Denial, Didn't Say Please | +4,94 ± 0,58 * | +1,89 ± 0,50 * | +1,52 * / +1,22 * | −0,37 * / +0,02 |
| s3: V.A.T.S., Wave Goodbye, Arcane Denial | +4,21 ± 0,55 * | +1,78 ± 0,47 * | +1,17 * / +0,63 * | −0,42 * / −0,05 |
| **s4: V.A.T.S., Wave Goodbye, Didn't Say Please** | **+4,64 ± 0,55 \*** | **+2,01 ± 0,46 \*** | +1,56 * / +1,62 * | −0,39 * / −0,10 |
| s5: V.A.T.S., Toxic Deluge, Arcane Denial | +4,39 ± 0,55 * | +1,83 ± 0,48 * | +1,20 * / +0,69 * | −0,39 * / +0,05 |
| s6: V.A.T.S., Toxic Deluge, Didn't Say Please | +4,82 ± 0,55 * | +2,06 ± 0,47 * | +1,61 * / +1,65 * | −0,38 * / +0,00 |
| s7: Tear Asunder, Wave Goodbye, Toxic Deluge | +4,38 ± 0,53 * | +2,24 ± 0,45 * | +1,02 * / +1,30 * | −0,43 * / −0,13 |

- **O ganho vem do par de motor; as três remoções não custam velocidade.** As remoções sozinhas (no lugar de V.A.T.S., Wave Goodbye e Deluge) dão +0,23 / +0,15 (o proliferate do Atomize), e o conjunto inteiro ≈ p1 + 0,3 a 0,9 no padrão.
- **O conjunto de cortes importa pouco para a velocidade** (diferença direta pareada em `resumos/conjuntos_entre_si.md`): s4 − s1 +0,31 ± 0,27 *, s4 − s3 +0,43 ± 0,35 *, s4 − s6 −0,18 ± 0,14 *, s4 − s2 −0,30 ± 0,29 *, s4 − s7 +0,26 ± 0,31; na resiliência todas as diferenças de T8 ficam dentro do IC (|dif| ≤ 0,23). A escolha entre eles é de função no deck, não de velocidade.
- **Custo de interação no simulador** (resiliência, por partida; base: 0,689 contramágicas conjuradas, 0,182 proteções usadas, 0,838 peças do meu motor removidas pelo oponente): s4 = −0,34 contramágicas, −0,06 proteções, **+0,04 peças removidas**; s2 (corta as duas contramágicas universais) = −0,46 / −0,07 / +0,04; s1 e s7 = −0,25 / −0,05 / +0,03. Proxy do repositório (7 categorias, 1/3 de atenção): apoio, não árbitro.
- **As remoções são pouco conjuradas pela convenção do simulador, não pelas cartas** (`resumos/castabilidade.md`, s4, padrão | resiliência): vistas até T8 em ≈ 37% | 29% das partidas; conjuradas em 4,4% | 6,3% (Atomize), 3,2% | 4,1% (Casualties), 7,9% | 9,8% (Trophy). A política é "uma remoção por turno, só com mana sobrando e `target_available` (0,7)"; um jogador real as usa sempre que há alvo. **Não usar esse número para julgar as cartas.**
- **O mana sustenta as cores?** (só terrenos em campo, sem pedras: piso) BB + GG com ≥ 6 terrenos: T6 47,7%, T7 65,6%, T8 75,3% (padrão; resiliência 41,3%, 58,0%, 68,8%). BG com 2 terrenos: T4 83,9%, T5 88,3% (Atomize e Trophy). O Casualties é carta de T7+ neste mana.
- **Spellbook** (95 nomes reconhecidos, 0 não reconhecidos; controle positivo e de corte OK): base = 2 combos (Ascension + Mindcrank; Altar of Dementia + Great Henge [+ Glen Elendra]); cada entrada isolada, as cinco juntas e as 7 listas exatas dos conjuntos: **0 combos novos, 0 perdidos**. "Quase" novo, com a Branching Evolution: Branching Evolution + Walking Ballista + (Vigor ou Rite of Passage), nenhuma das duas na lista. Nenhuma das cinco é Game Changer (Scryfall).

## Validação
- Testes dirigidos: **200/200** (194 + 6 novos; teste de mutação: com o `proliferate` desligado o teste do Atomize FALHA, e com o Trophy sem oponente vivo o teste do Trophy FALHA).
- Smoke (`resumos/smoke_cinco.txt`): 10 variantes, 99 cartas, 0 desconhecidas, 0 duplicadas, 0 exceções em 200 partidas × 2 modos.
- **Bit-identidade** (`resumos/bitident_20000.txt`, 4 fatias de 5.000 sementes × 2 modos, 9.000.000…9.019.999): (1) `SWAPS=()` do arquivo novo == snapshot ANTES, campo a campo (campos `atomize_/casualties_/trophy_` ignorados): **40.000 de 40.000**; (2) partidas em que NENHUMA das 3 novas nem das 3 que saíram foi vista (mão, cemitério, campo, exílio, no início e no fim de cada turno; fora mulligan, Palantír e Kozilek, que decidem pela identidade da carta): **3.894 de 3.894 idênticas**, 0 divergências.
- Replicação cruzada (`resumos/replicacao.txt`): `base` e `p1_so_o_par` daqui == `base` e `p1_offer_negate` de `../2026-10-08-pacote-e-interacao` (simulador sem as 3 cartas): **4/4 séries, 10.000 partidas cada**, todos os campos numéricos antigos iguais e os novos = 0.
- Regressão (`resumos/regressao_cinco_20000.txt`): 20.000 partidas × 2 modos × 2 conjuntos (s1, s2), sementes 5.000.000+i: **0 exceções**, 0 carta acima do baralho, 0 campo negativo.
- Determinismo (`resumos/determinismo.txt`): s4 `no lugar` e `remove+append`, 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos: **0 divergências**.
- **Reprodutibilidade** (`resumos/verificacao_reproducao.txt`): **6/6** (cinco saídas refeitas só dos brutos batem no `cmp`; base e s4, 1.000 sementes × 2 modos, re-simuladas com o simulador congelado: 4.000 de 4.000 partidas idênticas ao bruto).
- **Não rodado (Regra #10):** as varreduras mecânicas de `varredura-2026-10-05/scripts/` (entrada de terreno, fetch, landfall, colisão de nome): a mudança não toca terreno, mulligan, fases nem estado compartilhado por nome.

## O que NÃO foi verificado (Regra #7)
- O valor de remoção e de interação contra oponente real (o "destroy" é estrutural); a escolha do oponente-alvo (o Trophy usa o primeiro oponente vivo, sem critério de ameaça); a quantidade de modos do Casualties; usar Atomize ou Trophy no turno do oponente ou em alvo meu (proliferar sem remover); Beast Within, Maelstrom Pulse, Abrupt Decay, Vraska's Contempt e Putrefy **não estão implementados**.
- Uma só família de sementes; só os 7 conjuntos de corte acima (não varri combinações com Tear Asunder fora de s7, Selkie, Repulsive Mutation, nem cortes fora da interação); nenhuma mudança de terrenos para o BB + GG.
- O scry do Palantír trata as três como valor 25 (vão para o fundo), igual ao Tear Asunder / V.A.T.S. existentes; sem sensibilidade.

## Incidentes (para quem audita)
- Três tentativas do teste (2) da bit-identidade falharam por defeito do teste, não do simulador: (a) o scry do Palantír e o mulligan decidem pela identidade da carta; (b) o embaralhar do Kozilek devolve ao baralho a carta que esteve no cemitério; (c) uma carta descartada pelo oponente (modo resiliência) ou gasta sai das zonas finais. O critério final acumula as zonas no início e no fim de cada turno (`bitident_rem.py`); o (1) nunca divergiu. Também lancei por engano um 2º conjunto de fatias antes de terminar o 1º (dois processos escrevendo nos mesmos arquivos): matei todos por PID e refiz um conjunto limpo.
- A `confere_replicacao.py` comparava o fingerprint do estado inteiro, que inclui os campos novos e por isso muda em toda partida (0/10.000); agora compara os campos numéricos antigos e exige os novos = 0.
- O worker reiniciou nesta sessão (também derrubou a rodada anterior); o driver é retomável por variante (`*_parcial`, apagados depois do bruto final).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_cinco_10000.json.xz`, `dados/raw_cinco_10000_resiliencia.json.xz` | bruto por partida (colunas-v1, 317 campos): 10 variantes × 10.000, padrão / resiliência | usado |
| `dados/cast_padrao.json.xz`, `dados/cast_resiliencia.json.xz` | por partida e turno: terrenos / B / G e se as 3 remoções novas foram vistas e conjuradas (s4, 10.000) | usado |
| `dados/spellbook_cinco.json`, `dados/rulings_remocoes.json`, `dados/rulings_casualties.json` | Spellbook com controles; oráculo e rulings ao vivo | usado |
| `codigo/mothman_goldfish_v1_ANTES.py`, `codigo/mothman_goldfish_v1_DEPOIS.py` | simulador antes e depois do patch (DEPOIS == o vivo; as séries rodaram nele) | usado |
| `lista_proposta_s4.md` | lista proposta (NÃO aplicada) | proposta |
| `resumos/` | `tabela_cinco.md`, `conjuntos_entre_si.md`, `castabilidade.md`, `replicacao.txt`, `bitident_20000.txt` (+ fatias), `regressao_cinco_20000.txt`, `determinismo.txt`, `smoke_cinco.txt`, `verificacao_reproducao.txt`, `indice_dados.md`, logs | usado |
| `orquestracao/` | `patch_remocoes.py`, `gera_config.py` → `config_cinco.json`, `lanca_tudo.sh`, `driver_mm.py` (retomável), `abgen.py`, `bitident_rem.py`, `rank_cinco.py`, `compara_conjuntos.py`, `castabilidade.py`, `resumo_cast.py`, `confere_replicacao.py`, `csb_cinco.py`, `csb_stefano.py`, `gera_lista_proposta.py`, `resimula_amostra.py`, `verificar_reproducao.sh` | usado |

## Como refazer cada tabela
Dentro de `orquestracao/`: `python3 rank_cinco.py > ../resumos/tabela_cinco.md` · `python3 compara_conjuntos.py > ../resumos/conjuntos_entre_si.md` · `python3 resumo_cast.py > ../resumos/castabilidade.md` · `python3 confere_replicacao.py > ../resumos/replicacao.txt` · de dentro da pasta `python3 indice_dados.py > resumos/indice_dados.md` · tudo + re-simulação de amostra: `bash orquestracao/verificar_reproducao.sh --tudo`.
Refazer os brutos: `python3 gera_config.py && bash lanca_tudo.sh` (≈ 1 h 10 em 4 núcleos; `PYTHONHASHSEED=0` é fixado pelo driver); castabilidade: `python3 castabilidade.py 10000 padrao ../dados/cast_padrao.json.xz` (idem resiliência); Spellbook: `python3 csb_cinco.py ../../../lista.md ../dados/spellbook_cinco.json`; bit-identidade: `python3 bitident_rem.py 5000 9000000` (4 fatias).
