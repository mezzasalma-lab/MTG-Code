# Resultados brutos — Todo boardwipe segurado e custo pago com Treasures animados (2026-10-04)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Todo boardwipe segurado, e o custo pago com Treasures animados (Mayhem Devil)") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**

Princípio do usuário (generalizando a rodada anterior), transcrito sem reescrever:
> *"Todo boardwipe deve ser "segurado" para causar mais "perdas" aos oponentes do que a mim.*
> *Claro que quando utilizados, eu perco tudo que for criatura em campo, mas dependendo das circunstancias isso pode ser mitigado: por exemplo: Com Mayhem Devil em campo, sacrificar tesouros animados para [pagar o custo do wipe ainda causa dano nos oponentes além do efeito do wipe em sim!"*

Na rodada anterior (`../2026-10-04-wipes-proprios/`) eu segurava o wipe só quando ele destruiria Vihaan ou Mahadi (e estendi à Blasphemous Act por palpite meu). O princípio do usuário é mais geral e traz um mitigador concreto (pagar o custo com Treasures animados + Mayhem Devil).

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (rápido, só lê os `.json.xz`); `--tudo` re-executa também smoke, testes, bit-identidade, regressão e o destino do Prosper |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta; o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O que foi alterado no simulador

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py`. Código anterior = commit `47ec126` (guardado em `codigo/vihaan_goldfish_v1_ANTES_47ec126.py`, idêntico ao `git show 47ec126:…` por `cmp`); o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-04-wipes-segurados`. **3 chaves, todas ligadas por padrão; com as 3 desligadas o arquivo é bit-idêntico ao `47ec126`.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Todo wipe segurado** | `OWN_WIPE_HOLD_ALWAYS_ENABLED` | `wipe_held`, `main_phase`, `play_from_impulse` | Blood Money e Blasphemous Act nunca são conjuradas: o simulador não tem nada do lado do oponente pra pesar contra a perda (📊). Generaliza `OWN_WIPE_HOLD_ENGINE_ENABLED` (9ª rodada, só com Vihaan/Mahadi em campo), que continua existindo como base de comparação |
| **Pagar o wipe com animados** | `OWN_WIPE_PAY_WITH_ANIMATED_ENABLED` | `_wipe_pay_with_animated`, `cast_card` | o custo do wipe é pago primeiro com os Treasures **animados vivos e desvirados** (`ceil(custo / valor do Treasure)`; o resto vem dos terrenos): cada sacrifício é mana + morte de criatura + gatilho de sacrifício (Mayhem Devil), antes do wipe resolver (ruling 2019-05-03). Contadores `own_wipe_animated_paid_total`, `own_wipe_pay_drain_total` |
| **Exceção mitigada** | `OWN_WIPE_RELEASE_MITIGATED_ENABLED` | `wipe_mitigated`, `wipe_held` | a única exceção à retenção: Mayhem Devil em campo, animados pagando o custo **inteiro**, e **dano do pagamento > criaturas minhas perdidas** (1 dano = 1 criatura; o efeito no campo do oponente é 📊). Contador `own_wipe_mitigated_casts_total` |

**Premissas minhas, não confirmadas pelo usuário:** (a) a unidade da comparação (1 dano = 1 criatura minha perdida, só com o que o simulador enxerga); (b) só a circunstância do Mayhem Devil libera o wipe (Zulaport, Sephiroth e Plunderer não entram na conta de liberar); (c) exigir os animados pagando o custo inteiro.

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_rulings_ao_vivo.json` é **cópia** do arquivo da rodada anterior (9 cartas, lidas ao vivo no Scryfall em 2026-10-04, antes do código desta rodada): Blood Money, Blasphemous Act, **Mayhem Devil** ("whenever a player sacrifices a permanent", ruling 2019-05-03: o sacrifício que paga um custo tem o gatilho resolvido **antes** da magia), Pitiless Plunderer, Vihaan, Mahadi, Sevinne's, Lotho, Monologue Tax. Nenhuma carta foi adicionada ou cortada.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada; as diferenças da tabela são sempre contra `antes`): `antes` = commit `47ec126` · `sempre` (retenção universal, sem a exceção) · `liberar` (o que fica no repositório) · `sem_hold_pagar` e `sem_hold` = referências **sem nenhuma retenção**, com e sem o pagamento por animados. As chaves da 9ª rodada ficam ligadas em todas as variantes novas.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` · cada um em modo padrão e em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`, 4 configurações (`liberar`, `sempre`, `sem_hold`, `antes`) × 2 modos. Bit-identidade: sementes `1_000_000+i`, 20.000 partidas × 2 modos.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`); lista de campos em `resumos/indice_dados.md`. `--sum` refaz as tabelas só dos brutos.
- **Contagem comparável entre `antes` e as demais:** as colunas "Blood Money", "Blasphemous Act", "wipe com Vihaan|Mahadi" e "Vihaan destruído" vêm de um espião em `resolve_instant_sorcery` aplicado igualmente a todas as variantes; "retenções", "wipe mitigado", "animados pagando" e "dano do pagamento" só existem nas variantes novas (`n/a` no `antes`, que é o snapshot sem esses contadores).
- **Pares extras** (`orquestracao/comparar_pares.py`, só lê os brutos de 10.000): `liberar − sempre` (efeito da exceção) e `sem_hold_pagar − sem_hold` (efeito de pagar com animados quando o wipe sai sempre).
- **Destino do Prosper** (`orquestracao/prosper_destino.py`): resultado **idêntico antes e depois** (89 wipes próprios exilados pelo Prosper, 0 conjurados, 49 expiraram sem uso): a retenção da 9ª rodada já produzia isso.
- **Por que o efeito nos números é ~0:** a retenção da 9ª rodada (Vihaan ou Mahadi em campo) já segurava o wipe em ~100% dos casos no goldfish, porque o Vihaan quase sempre está em campo; a retenção universal **não segura nenhuma jogada a mais** nas 10.000 partidas (0,632 retenções por jogo antes e depois) e a exceção mitigada dispara em 0,05% das partidas.
- **Limite (Regra #5):** o simulador não tem criaturas de oponente: o wipe só pode custar, então "segurar vale +2,16pp" é verdadeiro por construção e **não mede** o benefício real contra os campos dos oponentes (📊).

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_47ec126.py` | simulador antes da correção | — | referência | variante `antes`, `bitident.py`, `prosper_destino_antes_padrao.txt` |
| `dados/raw_ab_2000.json.xz` | 5 variantes × 2.000 partidas, sementes 1.000.000+, padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 5 variantes × 10.000 partidas, sementes 3.000.000+, padrão | `fx_ab.py 10000` | **usado (tabela do log, "padrão")** | `resumos/ab_10000.txt`, `resumos/pares_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (tabela do log, entre parênteses)** | `resumos/ab_10000_resiliencia.txt`, `resumos/pares_10000.txt` |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo + rulings de 9 cartas, ao vivo (cópia do arquivo da rodada anterior) | consulta direta à API | referência | checklist |
| `resumos/pares_10000.txt` | diferenças pareadas `liberar − sempre` e `sem_hold_pagar − sem_hold` | `comparar_pares.py` | usado | log |
| `resumos/prosper_destino_antes_padrao.txt` / `_depois_padrao.txt` | destino de cada carta exilada pelo Prosper (N=10.000, padrão), com quebra por carta | `prosper_destino.py` | usado | log |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 24 testes dirigidos (P1–P7, R1–R3 com variações, invariantes de 3.000 jogos) | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com as 3 chaves desligadas × `47ec126`: 20.000 partidas × 2 modos, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 8 configurações/modos (160.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/lote.sh` | roda os 4 lotes do A/B e grava os resumos | — | usado | — |

Nenhum lote superado ou inválido nesta pasta.

**Comandos que reproduzem cada tabela** (de dentro de `orquestracao/`): `python3 fx_ab.py 2000 --sum` → `ab_2000.txt` · `python3 fx_ab.py 10000 --sum` → `ab_10000.txt` · `FX_MODO=resiliencia python3 fx_ab.py {2000,10000} --sum` → `ab_*_resiliencia.txt` · `python3 comparar_pares.py` → `pares_10000.txt` · `python3 smoke.py` · `python3 testes_dirigidos.py` · `python3 bitident.py 20000 1000000` · `python3 fx_regressao.py 20000` · `FX_SIM=../codigo/vihaan_goldfish_v1_ANTES_47ec126.py python3 prosper_destino.py 10000 3000000` (antes) e sem `FX_SIM` (depois).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **11/11 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`): as 4 tabelas do A/B e o `pares_10000.txt` refeitos dos `.json.xz` e a **re-execução** do smoke, dos 24 testes, da bit-identidade (20.000 partidas × 2 modos), da regressão (160.000 partidas) e do destino do Prosper (antes e depois).
**Os 11 arquivos anteriores do Vihaan foram reverificados com `--tudo` contra o simulador vivo (com as 3 chaves novas ligadas por padrão), todos iguais, sem `DIFERE`:** `wipes-proprios` 11/11, `dictate-metade-dos-animados` 11/11, `dictate-metade` 10/10, `exilio-sempre-e-dictate` 10/10, `exilio-primeiro-e-mahadi` 10/10, `fora-da-mao` 8/8, `sephiroth` 11/11, `treasure-animado-e-mulligan` 7/7, `kingpin` 11/11, `inevitable-defeat` 6/6, `partida-manual-1` 7/7. Para isso, o `orquestracao/fx_common.py` de 8 deles (`sephiroth`, `fora-da-mao`, `exilio-primeiro-e-mahadi`, `treasure-animado-e-mulligan`, `exilio-sempre-e-dictate`, `dictate-metade`, `dictate-metade-dos-animados`, `wipes-proprios`) passou a **desligar as 3 chaves novas** e a ignorar os 3 campos novos do `GameState` em `NOVOS`, e o `smoke.py` do `wipes-proprios` passou por `F.flags` (o mesmo erro das 2 rodadas anteriores, desta vez corrigido **antes** da verificação falhar: só o `cmp` do smoke dele foi conferido isolado antes da cadeia). Os `SHA256SUMS` dessas 8 pastas foram regenerados e o `LEIAME.md` de cada uma ganhou uma nota.
**Não conferido byte a byte:** a leitura do oráculo e das rulings no Scryfall (guardada em `dados/oraculo_rulings_ao_vivo.json`, não refeita por `cmp`).

## O que NÃO foi verificado (Regra #7)

- Só foram varridos, neste arquivo, `wipe_held`, `wipe_mitigated`, `_wipe_pay_with_animated` e a ordem de pagamento em `cast_card`. **Não** foi auditoria carta a carta.
- O **benefício** do wipe contra os campos dos oponentes (📊: o simulador não modela criatura de oponente).
- As 3 premissas acima (unidade 1 dano = 1 criatura; só a circunstância do Mayhem Devil libera; custo inteiro por animados) não foram confirmadas pelo usuário; outras mitigações reais (Zulaport, Sephiroth, Plunderer) não entram na decisão de liberar.
- Lotho/Monologue Tax em 2ª mágica de **oponente** continuam 📊 (convenção do usuário: 1 dos 3 oponentes, 2 mágicas).
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.

## Nota de 2026-10-04 (11ª rodada: `../2026-10-04-blasphemous-edict/`)

- **A chave nova** (`MIRKWOOD_BATS_SACRIFICE_ONLY_ENABLED`: o Mirkwood Bats só dispara em sacrifício de ficha, não em ficha destruída) vem **ligada** no simulador vivo. O `orquestracao/fx_common.py` desta pasta a **desliga** (bloco anexado ao fim do `flags()`; nenhum campo novo do `GameState`) pra continuar reproduzindo o simulador do commit dela.
- `verificar_reproducao.sh --tudo` depois da 11ª rodada: 11/11. `SHA256SUMS` regenerado.
