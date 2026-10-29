# Rodada 6 do Rat King, Verminister (2026-10-29): revisão de código do PR #1 — Staff após wipe, MDFC no fundo do mulligan, ensaio do terreno virado

Arquivo **permanente e auditável** do que sustenta as conclusões desta rodada. Tabelas legíveis e decisões: `rat-king-verminister/goldfish-log.md` (seção desta rodada, no topo) e `checklist-oraculo.md`. Relatório geral da revisão (as duas revisões do PR #1, o que foi e o que NÃO foi revisado): `../../../revisao-de-codigo-pr1-2026-10-29.md`.

Pedido do usuário (2026-10-29): *"Revise tudo e salve no GitHub e aqui tb"*; escolhas dele: revisão de código do diff do PR, **corrigir o que achar e relatar**, commit e push na branch do PR, arquivo na pasta do projeto.

> **STATUS DESTA PASTA:** fechada em 2026-10-29. Verificação de reprodutibilidade: `bash orquestracao/verificar_reproducao.sh --tudo` → **22/22 saídas byte a byte iguais** (`resumos/verificacao_reproducao.txt`): tabelas do A/B, resumos derivados dos brutos, arquivo vivo == `codigo/ratking_goldfish_v1_DEPOIS.py`, smoke, bit-identidade, regressão, testes dirigidos, as 2 medições (e o bruto das decisões do ensaio) e os 4 brutos do A/B re-simulados idênticos. **Não coberto por `cmp`:** determinismo (3 hash seeds) e o scanner de ETB fantasma (1 execução cada) e o texto interpretado deste LEIAME. A revisão automática (`code-review`, nível *high*) rodou sobre `git diff 7639380..HEAD -- rat-king-verminister/ratking_goldfish_v1.py` (rodadas 4 e 5, +341/−70 linhas) e devolveu 10 apontamentos. **Cada um foi lido contra o código antes de qualquer correção**; 2 eram defeitos reais (corrigidos), 1 gerou uma medição que achou OUTRO defeito cuja correção foi **medida e rejeitada**, 1 virou guarda, e 6 não eram defeito (tabela abaixo).

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver a decisão sobre cada apontamento | tabela abaixo |
| refazer as tabelas do A/B a partir dos dados | `bash orquestracao/verificar_reproducao.sh` |
| refazer TUDO (re-simula; **não editar o simulador enquanto roda**) | `bash orquestracao/verificar_reproducao.sh --tudo` |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |

## Os 10 apontamentos e o que foi decidido

| # | o que o revisor disse | o que eu verifiquei | decisão |
|---|---|---|---|
| 1 | `apply_own_wipe` não dispara o gatilho do Thornbite Staff ("Whenever a creature dies, untap this creature") que `on_creature_dies` dispara em toda morte normal | **Confirmado** no código. Teste dirigido R6-1 (carta e ficha de Mercenary como holder, holder que morre junto, wipe que não mata) | **Corrigido** (`WIPE_UNTAPS_STAFF`). **Latente:** em 20.000 partidas com "conjura sempre" houve 6.332 wipes meus, o Staff em campo em 839, holder equipado em 89 e **holder virado no momento do wipe em 0** (`resumos/staff_apos_wipe_20000.txt`): a ordem atual das fases não produz o caso. O A/B não mostra efeito (`so_staff` idêntico ao `antes` em 100%); a prova é o teste dirigido, não o A/B |
| 2 | `TAPPED_FIRST_COUNTS_MANA` decide por `mana_spent_this_turn`, que conta mana gasto em qualquer sorvedouro (extort, ativações) | A hipótese do **sorvedouro NÃO apareceu**: nas 1.304 decisões de 3.000 partidas, os 8 casos "mana maior sem desenvolvimento maior" são todos T2, comandante × Dark Ritual + Rat Colony, e ali a métrica de mana ACERTA (prefere o comandante). **Mas a medição achou outro defeito:** o `mana_spent_this_turn` é LÍQUIDO do Dark Ritual (−3), então Ritual + magia no T1 empata 0 × 0 com "jogar só o terreno virado", e o empate vai para o virado: **52 de 3.000 partidas (1,7%)**, todas T1 (`resumos/vies_ensaio_3000.txt`) | Correção testada: desempate por MV da mão + comandante (`TAPPED_FIRST_TIEBREAK_DEV`). **Rejeitada:** joga o desvirado no T1 e **custa o comandante no T2: −0,32 ± 0,11 pontos (N=10.000)** (−0,40 ± 0,28 em N=2.000). Chave fica `False`, código mantido para reproduzir a medida. O defeito real (Ritual líquido) fica **registrado, não corrigido**: uma correção boa precisaria olhar o T2 |
| 3 | `should_keep` conta a MDFC (Fell the Profane // Fell Mire) como terreno, mas `choose_bottom` a trata como magia de MV 4 e pode devolvê-la | **Confirmado** (`FELL_CARD` não está em `LAND_NAMES`; é a não-terreno de maior MV). Teste dirigido R6-2/R6-2b | **Corrigido** (`FELL_MIRE_PROTECTED_IN_BOTTOM`): protege a MDFC só quando há menos de 3 terrenos reais. Muda 9 de 10.000 partidas; efeito dentro do ruído, exceto `fell_mire_land_plays_total` +0,0008 ± 0,0006 (a direção esperada) |
| 4 | bloco do Mercenary + Staff duplicado em `black_market_connections_step` e `mercenary_enters` | Os dois blocos são idênticos e usam a mesma chave; nenhuma divergência hoje | **Não é defeito agora; não alterei** (risco de manutenção, fora do escopo de "corrigir erro") |
| 5 | `wipe_held` muta estado dentro de um predicado | A contagem usa um conjunto por turno (1 retenção por nome por turno), zerado em `play_turn`; os ensaios a seco rodam em cópia profunda | **Não é defeito; não alterei** |
| 6 | `WIPE_CAST_MAX_OWN_LOSS = 0` conjura Damnation em tabuleiro vazio e a segura para sempre depois | É a política que o usuário escolheu ("Opção B nos wipes, e meça no A/B") e o A/B de 2026-10-28 precificou cada limite; conjurar no vazio é o comportamento antigo (proxy de interação, convenção da CLAUDE.md) | **Política, não bug; não alterei** |
| 7 | `_fm_dry_run_mv` se chama MV mas devolve mana; três ensaios quase iguais | A docstring já diz que devolve mana | **Manutenção; não alterei** |
| 8 | `_wipe_effect_on` reconstrói um dict e o despacho por chave se repete | Cobertos pelos testes WP1–WP9 da rodada 5 | **Manutenção; não alterei** |
| 9 | `CREATURE_TYPES`/`CREATURE_TOUGHNESS` podem divergir do `CARD_DB` sem erro | Hoje cobrem as 18 criaturas (WP0 compara com o oráculo arquivado) | **Guarda de importação** (não muda comportamento): criatura fora das tabelas faz o simulador não importar. Teste R6-4 |
| 10 | `apply_own_wipe` não ajusta `rat_tokens_created_this_turn` | **Não alcançável:** `wipe_plan` mata ou TODAS as fichas de Rat (Damnation, Kindred que não nomeia Rat) ou nenhuma (Kindred nomeando Rat, Swarmyard); nunca parte | **Nada a corrigir** |

## O que mudou no simulador

`ratking_goldfish_v1.py` ganhou 3 chaves, 1 contador e 1 guarda. Com as 3 chaves desligadas ele é **bit-idêntico** ao snapshot `codigo/ratking_goldfish_v1_ANTES_a052820.py` (20.000 × 2 modos, `resumos/bitident_20000.txt`; o contador novo `wipe_staff_untaps_total` é ignorado na comparação).

| chave | padrão | o que faz |
|---|---|---|
| `WIPE_UNTAPS_STAFF` | `True` | `apply_own_wipe` chama `staff_untap_on_death` (o holder que sobreviveu desvira) e conta `wipe_staff_untaps_total` |
| `FELL_MIRE_PROTECTED_IN_BOTTOM` | `True` | `choose_bottom` não devolve a MDFC quando ela é o 3º "terreno" que `should_keep` contou |
| `TAPPED_FIRST_TIEBREAK_DEV` | **`False`** (medido e rejeitado) | no empate de mana do ensaio do terreno virado, desempata por MV da mão + comandante |

## Como os dados foram gerados

- **A/B pareado, bit-identidade, regressão:** `orquestracao/driver.py` + `abgen.py` (cópias da rodada 5; leem `orquestracao/config.json`). Sementes: A/B N=2.000 → `1_000_000+i`; N=10.000 → `3_000_000+i`; regressão e bit-identidade → `5_000_000+i`. Variantes: `antes` (snapshot), `depois` (arquivo vivo = padrões acima), `so_staff`, `so_bottom`, `so_tiebreak` (cada uma lista as 3 chaves explicitamente; as outras `False`). `depois` é idêntica a `so_bottom` em 100% das partidas, como esperado (Staff latente, desempate desligado).
- **Controle de vacuidade:** `resumos/diferem_entre_variantes.txt` (fração de partidas idênticas entre pares): `so_staff` = `antes` em 100% (latente, declarado acima); `so_bottom` difere em 9; `so_tiebreak` em 172.
- **Testes dirigidos:** `orquestracao/testes_dirigidos.py` (8 testes; chave ligada e desligada; R6-3 usa as sementes 1000008 e 1000307 em que o Ritual + magia no T1 só sai com o terreno desvirado).
- **Medições (sobre o simulador da rodada 5, não o vivo):** `orquestracao/medir_vies_ensaio.py` (3.000 partidas) e `medir_staff_apos_wipe.py` (20.000 partidas, "conjura sempre").
- **Determinismo:** `varredura-2026-10-05/scripts/det_check.sh rat-king-verminister ratking_goldfish_v1.py 8 1500`, **rodado de dentro da pasta dos scripts** (a 1ª tentativa, da raiz, deu `JSONDecodeError` em 0,06 s: era vácua, foi refeita) → `resumos/determinismo.txt`: 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, 0 divergentes.
- **Scanner de ETB fantasma** (`audit_etb_sem_efeito.py`): saída idêntica à da rodada 5 (42 cartas conjuradas, 25 sem mudança de estado, todas já classificadas).

## Mapa: arquivo → o que é → código → status → onde aparece

| arquivo | o que é | código | status | onde aparece |
|---|---|---|---|---|
| `dados/raw_ab_2000.json.xz`, `raw_ab_10000.json.xz` | A/B padrão: `antes` + `depois` + 3 variantes, N=2.000 / 10.000 | `orquestracao/driver.py ab` | usado (2ª execução, desempate desligado por padrão) | `resumos/ab_*.txt`; log |
| `dados/raw_ab_2000_resiliencia.json.xz`, `raw_ab_10000_resiliencia.json.xz` | idem, modo resiliência | idem | usado | `resumos/ab_*_resiliencia.txt` |
| `dados/vies_ensaio_decisoes.json.xz` | as 1.304 decisões do ensaio do terreno virado (mana e desenvolvimento dos dois terrenos) | `orquestracao/medir_vies_ensaio.py` | usado | `resumos/vies_ensaio_3000.txt` |
| `superado-1a-execucao-tiebreak-ligado/` | brutos, tabelas e log da 1ª execução do A/B, com `TAPPED_FIRST_TIEBREAK_DEV = True` por padrão (`depois` = tudo ligado); **superada** porque o desempate foi rejeitado e o padrão passou a `False`. As mesmas sementes reaparecem na variante `so_tiebreak` da 2ª execução | `driver.py` com `codigo/ratking_goldfish_v1_1a_execucao_tiebreak_LIGADO.py` | **SUPERADO** (guardado) | — |
| `resumos/ab_2000.txt`, `ab_10000.txt`, `*_resiliencia.txt` | tabelas pareadas (diferença ± IC95%, fração idêntica) | `driver.py sum` (só dos brutos) | usado | log |
| `resumos/resumo_variantes_10000.md` | uma linha por variante, métricas escolhidas | `orquestracao/resumo_variantes.py` | usado | log |
| `resumos/diferem_entre_variantes.txt` | fração de partidas idênticas entre pares de variantes | `orquestracao/diferem_entre_variantes.py` | controle de vacuidade | log |
| `resumos/bitident_20000.txt`, `regressao_20000.txt`, `smoke.txt`, `testes_dirigidos.txt` | bit-identidade (0 diferentes), regressão (0 exceções; `mana_spent_this_turn` negativo em 80 (padrão) e 85 (resiliência) das 20.000 partidas com as chaves padrão, 80 e 86 com todas desligadas; na rodada 5 eram 80/86 e 76/80: é o líquido do Ritual, que existia antes), smoke (99 cartas, 0 desconhecidas), 8/8 testes | `driver.py` / `testes_dirigidos.py` | verificação | log |
| `resumos/vies_ensaio_3000.txt`, `staff_apos_wipe_20000.txt` | as duas medições | `medir_*.py` | usado | log |
| `resumos/determinismo.txt`, `audit_etb_sem_efeito_DEPOIS.txt` | determinismo (3 hash seeds) e scanner | scripts da varredura | verificação (1 execução, não coberta por `cmp`) | log |
| `resumos/log_*.txt` | logs da bateria | — | log | — |
| `resumos/indice_dados.md` | o que há em cada arquivo de `dados/` | `indice_dados.py` | índice | — |
| `resumos/verificacao_reproducao.txt` | saída de `verificar_reproducao.sh --tudo` | `orquestracao/verificar_reproducao.sh` | verificação | — |
| `codigo/ratking_goldfish_v1_ANTES_a052820.py` | o simulador antes desta rodada (== o da rodada 5) | — | usado | — |
| `codigo/ratking_goldfish_v1_DEPOIS.py` | o simulador usado pelo A/B final (== o arquivo vivo; `cmp` em `--tudo`) | — | usado | — |

## Escopo (Regra #7): o que esta rodada NÃO fez

- **Revisão automática só do `ratking_goldfish_v1.py`, rodadas 4 e 5** (`7639380..HEAD`). Não revi: a rodada 3 e anteriores do mesmo arquivo; os outros 17 simuladores modificados no PR; os ~1.060 outros arquivos `.py` do PR (scripts de resultados, cópias `_original`, testes); os dados e a documentação.
- **Classe do ensaio a seco:** os 13 simuladores com a mesma função `_tl_dry_run_mv` seguem sem medição (já declarado na rodada 4). A classe nova achada aqui, **métrica líquida no ensaio** (Ritual/Culling subtraem do mana gasto), só vale para quem usa `mana_spent_this_turn` no ensaio: hoje, só o Rat King; os outros usam o MV da mão.
- **O defeito do Ritual líquido no T1 ficou sem correção** (rejeitei a única que testei). Uma correção que olhe o T2 não foi tentada.
- **O desvirar do Staff após wipe é latente:** a ordem de fases do `play_turn` nunca deixa o holder virado quando o wipe resolve; se a ordem mudar, a correção passa a agir.
- Nenhuma conclusão sobre oponente real (N/A estrutural, goldfish solo).
