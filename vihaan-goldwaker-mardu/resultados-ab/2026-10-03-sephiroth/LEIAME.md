# Resultados brutos — Sephiroth no simulador do Vihaan (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Correção do simulador: Sephiroth …") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"Quero sim, corrija os itens 2 e 3."* (lacunas do Sephiroth: (2) emblema + Sephiroth de frente = 2 gatilhos por morte e uma 2ª virada = 2º emblema; (3) wipe que mata o Sephiroth junto com outras criaturas: o gatilho dele vale para cada uma das outras, em qualquer ordem de remoção, e ele não vira.)

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (rápido, só lê os `.json.xz`); `--tudo` re-executa também smoke, testes, bit-identidade, regressão e as duas análises de diagnóstico |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta; o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O que foi alterado no simulador

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (código anterior = commit `ba74496`, guardado em `codigo/vihaan_goldfish_v1_ANTES_ba74496.py`, idêntico ao `git show ba74496:…` por `cmp`; o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-03-sephiroth`). **Uma chave por correção; com as três desligadas o arquivo é bit-idêntico ao anterior.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Emblema acumulável** | `SEPHIROTH_EMBLEM_STACKING_ENABLED` | `on_creature_dies` → `_sephiroth_death_triggers`, `enter_battlefield` | `super_nova_emblems` conta emblemas; com emblema **e** Sephiroth de frente, cada morte dispara 2 gatilhos; a 4ª resolução da frente dá um 2º emblema. Antes: um sim/não e só o emblema disparava |
| **Mortes simultâneas em wipe** | `SEPHIROTH_SIMULTANEOUS_DEATH_ENABLED` | `begin_mass_death`/`end_mass_death` em `try_smart_opponent_wipe`, Blood Money, Blasphemous Act | foto do que o Sephiroth enxerga antes do lote; dispara para cada outra criatura (fichas incluídas) em qualquer ordem; **não vira** se morre junto (ruling 2025-06-06) |
| **Contador "neste turno"** | `SEPHIROTH_TURN_BOUNDARY_ENABLED` | `try_smart_opponent_turn`, `enter_battlefield` | zera `sephiroth_deaths_this_turn` em cada turno de oponente (antes só no meu) e na reentrada em campo |

Detalhe que não tem chave: a morte do **próprio** Sephiroth não dispara a habilidade da frente ("another creature"); as vias de permanente nomeado (`sacrifice_named_creature`, `remove_permanent`) passam `dying=` até `_sephiroth_death_triggers`. Com as chaves desligadas esse parâmetro nunca é lido (por isso a bit-identidade se mantém).

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_e_rulings.json` (resposta bruta do Scryfall, 2026-10-03, relida para esta pasta no fim da rodada). **Frente:** *Whenever another creature dies, target opponent loses 1 life and you gain 1 life. If this is the fourth time this ability has resolved this turn, transform Sephiroth.* **Verso:** *Super Nova — As this creature transforms into Sephiroth, One-Winged Angel, you get an emblem with "Whenever a creature dies, target opponent loses 1 life and you gain 1 life."*
Ruling 2025-06-06: *If Sephiroth, Fabled SOLDIER and one or more other creatures die at the same time, its last ability will trigger for each of those other creatures. (It won't transform, though.)* Outra (2025-06-06): se entrar com o verso virado, não houve transformação, então não há emblema. As 8 restantes tratam de faces, cor, valor de mana e fichas-cópia.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada): `antes` = commit `ba74496` · `emblema` · `simultaneas` · `fronteira` — cada correção sozinha · `todas` = as três (o simulador que fica no repositório). As outras 3 chaves do Vihaan (Treasure animado, mulligan, terreno tapped) ficam ligadas em todas as variantes, como no repositório.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` · cada um em modo padrão e em modo resiliência (`FX_MODO=resiliencia`, o oponente tem wipe). 8 turnos. Regressão: sementes `5_000_000+i`. Bit-identidade: sementes `1_000_000+i`, 20.000 partidas.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). Campos: `win_turn`, `drain`, `table_dmg`, `combat`, `creature_deaths`, `life_gained`, `treasures`, `flipped` (1 se tem emblema no fim), `emblems`, `extra` (gatilhos extras do emblema que o código antigo perdia), `fp` (impressão digital do estado final, para contar jogos idênticos).
- **Colunas das tabelas:** `virou pp` = diferença na taxa de jogos com o emblema; `emblemas` = emblemas por jogo; `dano mesa`/`drain` = proxies agregados (nunca vida real de oponente); `win<=8 pp` = vitória (proxy) até o T8.
- **Nenhum lote foi gerado com a 1ª versão do código.** O erro da morte do próprio Sephiroth disparar a frente (5 gatilhos em vez de 4 no wipe) foi pego pelos testes dirigidos **antes** de qualquer A/B; todos os brutos desta pasta saem do código final.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_ba74496.py` | simulador antes da correção (`git show ba74496:…`) | — | referência | variante `antes`, `bitident.py`, `flips_em_wipe.py` |
| `dados/raw_ab_2000.json.xz` | 5 variantes × 2.000 partidas, sementes 1.000.000+, modo padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 5 variantes × 10.000 partidas, sementes 3.000.000+, modo padrão | `fx_ab.py 10000` | **usado (tabela do log, linhas "padrão")** | `resumos/ab_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, modo resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, modo resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (tabela do log, linhas "resiliência")** | `resumos/ab_10000_resiliencia.txt` |
| `dados/oraculo_e_rulings.json` | oráculo + 10 rulings do Sephiroth | consulta direta à API | referência | checklist: cláusulas |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 28 testes dirigidos | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com as 3 chaves desligadas × ANTES: 20.000 partidas × 2 modos, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 7 configurações/modos (140.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/flips_em_wipe_antes_resiliencia.txt` | no código antigo, de onde vinham as viradas (231 jogos de 10.000): 167 wipe com ele morrendo junto, 6 wipe com ele vivo, 58 fora de wipe | `flips_em_wipe.py 10000 3000000` | usado | log: "Leitura (medido)" |
| `resumos/explica_diferencas_emblema_padrao.txt` | os 6 jogos (de 2.000) que mudam de estado na variante `emblema`: só o campo `sephiroth_deaths_this_turn` | `explica_diferencas.py emblema 2000 padrao` | usado | log: leitura (d) |
| `resumos/explica_diferencas_simultaneas_padrao.txt` | os 19 jogos que mudam na variante `simultaneas` e quais campos | `explica_diferencas.py simultaneas 2000 padrao` | usado | log: leitura (d) |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação (11/11) | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/lote.sh` | roda os 4 lotes do A/B e grava os resumos | — | usado | — |

Nenhum lote superado ou inválido nesta pasta.

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **11/11 saídas byte a byte iguais** (`cmp`): as 4 tabelas de A/B refeitas dos `.json.xz` e a **re-execução** do smoke, dos 28 testes, da bit-identidade de 20.000 partidas, da regressão de 140.000 partidas, de `flips_em_wipe.py` e dos dois `explica_diferencas.py`. `sha256sum -c SHA256SUMS` passa. Saída em `resumos/verificacao_reproducao.txt`.
Reverificados também os arquivos anteriores do Vihaan contra o simulador vivo (que agora vem com o Sephiroth novo ligado): `2026-10-03-kingpin` 11/11 e `2026-10-03-inevitable-defeat` 6/6 iguais; `2026-10-03-treasure-animado-e-mulligan` precisou de um ajuste no `fx_common.py` (desligar as 3 chaves novas e ignorar os 6 campos novos) e voltou a 7/7 (nota no `LEIAME.md` dele).
**Não conferido byte a byte:** nada que esteja linkado no log como tabela deixou de ser refeito; o que não é reproduzível por script é a leitura do oráculo no Scryfall (guardada em `dados/oraculo_e_rulings.json`, não refeita por `cmp`).

## O que NÃO foi verificado (Regra #7)

- Só foram varridas, neste arquivo, as classes: gatilho compartilhado "criatura morre" nas vias de remoção/sacrifício (grep de `battlefield.remove`, `constructs -=`, `other_tokens -=` e dos zeramentos de wipe), fronteira de turno (Regra #6) e a fórmula "emblemas × gatilhos". **Não** foi uma auditoria carta a carta; as habilidades de entrada/ataque do Sephiroth (`try_sephiroth_sac_draw`) não foram relidas.
- Wipes próprios (Blood Money, Blasphemous Act) continuam usando o caminho de **sacrifício**, mas "destroy" não é sacrifício: Mayhem Devil dispara a mais e o comandante é excluído. **Não** alterado.
- "Another creature dies" de criatura de **oponente** não entra: o simulador não modela criatura de oponente (📊 estado de oponente).
- O Sephiroth poderia sacrificar Treasures animados como combustível (política); Xorn/Pitiless Plunderer em lote por evento (pré-existente); 7 outros decks sorteiam o fundo no mulligan. **Não** alterados.
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.

## Nota posterior (2026-10-03, rodada "fora da mão"): o que mudou NESTA pasta depois do commit original

O simulador vivo ganhou depois cinco chaves novas (`IMPULSE_*`, `SPELL_CAST_*`, `STORM_*`, `SEVINNE_*`, ver `../2026-10-03-fora-da-mao/LEIAME.md`), **ligadas por padrão**. Para esta pasta continuar reproduzindo o simulador como era no commit dela, `orquestracao/fx_common.py` foi ajustado: `flags()` agora também **desliga** as 5 chaves novas e o conjunto `NOVOS` (campos de `GameState` ignorados na impressão digital) ganhou os 8 campos novos; `orquestracao/smoke.py` passou a carregar o simulador por `F.flags(...)`. Nenhum dado bruto, resumo ou tabela mudou. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 11/11 byte a byte iguais. `SHA256SUMS` regenerado.

Terceira nota (rodada "Prosper e Mahadi", 2026-10-03): o simulador vivo ganhou mais duas chaves ligadas por padrão (`IMPULSE_EXPIRING_FIRST_ENABLED`, `TREASURE_SELF_OUTLET_FARM_ENABLED`; ver `../2026-10-03-exilio-primeiro-e-mahadi/LEIAME.md`). `orquestracao/fx_common.py` agora também as desliga e ignora os 3 campos novos do `GameState`. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 11/11 byte a byte iguais. `SHA256SUMS` regenerado.

Nota (rodada "exílio sempre e Dictate", 2026-10-04): o simulador vivo ganhou mais duas chaves ligadas por padrão (`IMPULSE_ALL_FIRST_ENABLED`, `TREASURE_FARM_WITH_DICTATE_ENABLED`; ver `../2026-10-04-exilio-sempre-e-dictate/LEIAME.md`). `orquestracao/fx_common.py` agora também as desliga e ignora os 2 campos novos do `GameState`. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 11/11 byte a byte iguais. `SHA256SUMS` regenerado.

## Nota de 2026-10-04 (9ª rodada: `../2026-10-04-wipes-proprios/`)

- **As 5 chaves novas** (wipes próprios: destruição fiel, Treasure virado, custo da Blasphemous Act, retenção; imposto do comandante) vêm **ligadas** no simulador vivo. O `orquestracao/fx_common.py` desta pasta as **desliga** (e inclui os 7 campos novos do `GameState` em `NOVOS`) pra continuar reproduzindo o simulador do commit dela.
- `verificar_reproducao.sh --tudo` depois da 9ª rodada: 11/11. `SHA256SUMS` regenerado.
