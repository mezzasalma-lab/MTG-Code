# Resultados brutos — Kingpin, Wilson Fisk no Vihaan (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Kingpin, Wilson Fisk — avaliação como possível inclusão — 2026-10-03") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"E a inclusao de Kingpin, Wilson Fisk no VIhaan?"* (com foto da carta).

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer uma tabela a partir dos dados | rodar o comando da coluna "comando" do mapa, **de dentro de `orquestracao/`** (os scripts leem os `.json.xz` direto, via `raw_io.py`) |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O simulador não foi alterado

> **Nota posterior (2026-10-03, mesma data, depois desta rodada): o simulador vivo mudou.** A frase "o simulador não foi alterado" vale **para esta rodada** (medidas com o commit `6e623d3`).
> Depois dela, `vihaan_goldfish_v1.py` ganhou o roteamento do Treasure animado (todo sacrifício de Treasure depois da animação conta como morte de criatura), o mulligan com escolha das cartas do fundo
> e o terreno tapped em T1/T2 (`../2026-10-03-treasure-animado-e-mulligan/LEIAME.md`). Consequências para esta pasta: (1) **as tabelas continuam reproduzíveis**, porque `--sum` lê só os brutos `.json.xz`;
> (2) `bitident.py` e qualquer rerodada **sem** `--sum` rodam contra o arquivo VIVO e **passam a divergir**: para refazê-los, extraia o simulador antigo com
> `git show 6e623d3:vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (há uma cópia em `../2026-10-03-treasure-animado-e-mulligan/codigo/vihaan_goldfish_v1_ANTES_6e623d3.py`) ou desligue as 3 chaves
> (`ANIMATED_TREASURE_ROUTING_ENABLED`, `MULLIGAN_SMART_BOTTOM_ENABLED`, `TAPPED_LAND_FIRST_ENABLED`); (3) os números **absolutos** daqui são do simulador antigo, não comparáveis com rodadas feitas depois da correção;
> o "achado lateral" do Treasure animado citado no log desta rodada foi **corrigido** nessa rodada seguinte.


`vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (último commit `6e623d3`) **não foi editado**: o Kingpin e a instrumentação entram por *monkeypatch* em tempo de execução (`orquestracao/kp_harness.py`) e pelo `swap` que o próprio simulador já tem.
A base do harness (sem o Kingpin na lista) foi comparada com o módulo original, carregado como módulo separado e sem nenhum patch, nas 3 políticas: ver `resumos/bitident.txt`.
Código desta pasta: o commit que a adiciona (`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-03-kingpin`).

## Como os dados foram gerados

- **Sementes:** `3_000_000 + i`, a mesma semente em todas as variantes de um lote (**pareado**; IC95% = 1,96·dp/√N da diferença). N = 6.000 por variante. Horizontes de 8 e 12 turnos.
- **Variante:** `swap=[(SAI, ENTRA)]` do próprio `simulate_one` (troca **posicional**, a carta nova entra na linha da cortada). `ENTRA` = `Kingpin, Wilson Fisk` (`kp|X`) ou `Blank Card` (`blank|X`).
- **Blank Card:** carta inconjurável (instantâneo, MV 99). Como entra NA MESMA POSIÇÃO do Kingpin, `Kingpin<-X` e `Blank<-X` são o contrafactual exato um do outro nas mesmas sementes; a comparação isola o efeito do Kingpin do viés de "carta morta não gasta mana".
- **Modelagem** (`orquestracao/kp_harness.py`, detalhes na docstring e no `checklist-oraculo.md`): gatilho em `on_permanent_sacrificed(is_creature=True)`, 1×/turno, cria 2 Treasures por `create_treasures` (Xorn, Procession, Academy). **Políticas (`KP_POLICY`):** `sim` = só o que o simulador já roteia como sacrifício de criatura · `anim` = + sacrificar um Treasure ANIMADO por qualquer via conta (só para o Kingpin) · `delib` = `anim` + linha deliberada de sacrificar um Treasure animado por nada no end step. Cor: o simulador não a modela; o {B} é medido à parte.
- **Horizonte e fatias:** `KP_TURNS=12` roda 12 turnos; `KP_SLOTS` limita os cortes (14 cartas na rodada de 12 turnos); `KP_BLANKS` acrescenta `Blank<-X` (3 slots).
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`; campos em `kp_harness.summarize`).
- **Colunas das tabelas:** `win<=T` = `win_turn` ≤ T (dano de mesa+combate proxy ≥120, Revel in Riches ou combo); `revel<=T` = condição do Revel in Riches cumprida até T; `cmd<=3` = comandante conjurado até T3; `Treasures` = Treasures criados; `cast%` = % das partidas com o Kingpin conjurado; `disp/jogo` e `T/jogo` = disparos e Treasures do Kingpin **por partida em que ele foi conjurado**.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela do log que o usa |
|---|---|---|---|---|
| `dados/raw_ab_kingpin_6000_sim.json.xz` | 68 variantes (base + 64 `Kingpin<-X`, todas as cartas não-terreno + 3 `Blank<-X`), 8 turnos, política `sim` | `kp_ab.py` com `KP_POLICY=sim` | usado | `resumos/ab_kingpin_6000_sim.txt`; base de `kingpin_vs_blank.txt` (8 turnos, Blank) e de `castabilidade_b_kingpin.txt` |
| `dados/raw_ab_kingpin_6000_anim.json.xz` | idem, política `anim` | `KP_POLICY=anim` | usado | `resumos/ab_kingpin_6000_anim.txt` |
| `dados/raw_ab_kingpin_6000_delib.json.xz` | idem, política `delib` | `KP_POLICY=delib` | usado | `resumos/ab_kingpin_6000_delib.txt`; `condicional_kingpin_vs_blank.txt` |
| `dados/raw_ab_kingpin_6000_{sim,anim,delib}_t12_slots.json.xz` | 15 variantes (base + 14 cortes), 12 turnos | `KP_TURNS=12 KP_SLOTS=…` | usado | `resumos/ab_kingpin_6000_t12_{sim,anim,delib}_slots.txt`; `kingpin_vs_blank.txt` (12 turnos) |
| `dados/raw_ab_kingpin_6000_delib_t12_slots_blk.json.xz` | 7 variantes (base + 3 `Kingpin<-X` + 3 `Blank<-X`), 12 turnos | `KP_TURNS=12 KP_SLOTS=… KP_BLANKS=…` | usado (a Blank não depende da política) | `resumos/ab_kingpin_6000_t12_delib_blank.txt`; `kingpin_vs_blank.txt` |
| `dados/spellbook_vihaan_kingpin_swaps.json` | **resumo** do `find-my-combos` do Commander Spellbook (combos incluídos e "quase" por lista: base, +Kingpin, 29 trocas); **não** guarda a resposta crua | `csb_generic.py` | usado | `resumos/spellbook_vihaan_kingpin_swaps.txt` |
| `dados/rulings_Kingpin_Wilson_Fisk.json` | oráculo bruto do Scryfall + rulings do Kingpin (0) (lidos ao vivo em 2026-10-03) | consulta direta à API | referência | checklist: Kingpin |
| `dados/rulings_contexto_vihaan_xorn_manufactor_procession.json` | rulings de Vihaan (5), Xorn (1), Academy Manufactor (4), Anointed Procession (6), Dictate of Erebos (5), Mirkwood Bats (0), Goldspan Dragon (3), Ashnod's Altar (0), Sephiroth (10) | consulta direta à API | referência | checklist: Kingpin |
| `resumos/enumeracao.txt` | enumeração por script das 94 entradas distintas de `lista.md` (saídas de sacrifício, geradores/multiplicadores de Treasure, pagadores de ficha e de morte, tipos, Treasure-criatura) | `kp_enumeracao.py` | usado | log: motores |
| `resumos/castabilidade_b_kingpin.txt` | P(≥4 de mana e fonte de B) por turno nas partidas-base | `kp_cor.py` | usado | log: Cor |
| `resumos/bitident.txt` | base do harness × simulador original sem patch, nas 3 políticas (300 partidas cada) | `bitident.py` | verificação | log: escopo verificado |

## Mapa: tabela → comando que a reproduz (de dentro de `orquestracao/`)

| resumo salvo (`resumos/`) | comando |
|---|---|
| `ab_kingpin_6000_<política>.txt` | `KP_POLICY=<política> python3 kp_ab.py 6000 --sum` (política ∈ sim, anim, delib) |
| `ab_kingpin_6000_t12_<política>_slots.txt` | `KP_POLICY=<política> KP_TURNS=12 KP_SLOTS="Academy Manufactor\|Monologue Tax\|Back in Town\|Teferi's Protection\|Blasphemous Act\|Life Insurance\|Council's Judgment\|Requisition Raid\|Shoot the Sheriff\|Path to Exile\|Orochi Soul-Reaver\|Lotho, Corrupt Shirriff\|Sol Ring\|Arcane Signet" python3 kp_ab.py 6000 --sum` (sem as barras invertidas: o separador é `\|`; o script `verificar_reproducao.sh` tem a linha exata) |
| `ab_kingpin_6000_t12_delib_blank.txt` | `KP_POLICY=delib KP_TURNS=12 KP_SLOTS="Monologue Tax\|Academy Manufactor\|Back in Town" KP_BLANKS="Monologue Tax\|Academy Manufactor\|Back in Town" python3 kp_ab.py 6000 --sum` |
| `kingpin_vs_blank.txt` | `python3 kp_vs_blank.py` |
| `condicional_kingpin_vs_blank.txt` | `python3 kp_cond.py` |
| `castabilidade_b_kingpin.txt` | `python3 kp_cor.py` |
| `enumeracao.txt` | `python3 kp_enumeracao.py` (lê o cache do Scryfall e `lista.md`) |
| `bitident.txt` | `python3 bitident.py 300 8` |
| `spellbook_vihaan_kingpin_swaps.txt` | a partir da raiz do repositório: `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-03-kingpin/orquestracao/csb_generic.py vihaan-goldwaker-mardu "Vihaan, Goldwaker" saida.json "CARTA1\|CARTA2\|…" "Kingpin, Wilson Fisk"` (cortes separados por `\|`, sem a barra invertida); depende da API ao vivo, **não** é refeito byte a byte |
| `indice_dados.md` | `python3 ../indice_dados.py` |

Sem `--sum`, o mesmo script **roda** as simulações de novo (e grava os brutos). `bash orquestracao/verificar_reproducao.sh` refaz todas as tabelas de uma vez e compara com `cmp`.

## Verificações feitas ao arquivar (2026-10-03)

- **Reprodutibilidade:** ver `resumos/reproducao_cmp.txt` (saída de `verificar_reproducao.sh`: 11 tabelas refeitas dos `.json.xz` e comparadas com `cmp`).
- **Bit-identidade:** `bitident.py 300 8`: 300/300 partidas idênticas em 101 campos do `GameState` nas políticas `sim`, `anim` e `delib` (original sem patch × base do harness).
- **Controles:** no A/B, cortar Sol Ring custa −2,8 a −3,2pp de win ≤T8 e cortar Arcane Signet atrasa o comandante (−0,6pp ≤T3); no Spellbook, cortar Smothering Tithe ou Gleaming Splendor remove 3 combos e cortar Mahadi ou Ashnod's Altar remove 1.
- **Observação sobre os cabeçalhos:** os resumos foram regenerados dos brutos depois de renomear colunas (`disp.` → `disp/jogo`, `T/disp` → `T/jogo`); as linhas de dados são idênticas às da primeira execução (conferido linha a linha).
- **Não conferido byte a byte:** `spellbook_*.json` (API ao vivo; resposta crua não guardada) e `rulings_*.json`.
- **Hashes:** `SHA256SUMS` cobre `dados/`, `resumos/`, `orquestracao/`, `indice_dados.py`, `descomprimir.sh` e `.gitignore`.
