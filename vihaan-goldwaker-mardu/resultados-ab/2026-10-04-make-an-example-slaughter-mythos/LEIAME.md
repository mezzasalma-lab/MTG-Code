# Resultados brutos — Make an Example, Slaughter the Strong e Mythos of Snapdax: as 3 que o usuário escolheu (2026-10-04)

Arquivo de referência **permanente e auditável** do que sustenta a resposta desta rodada do deck Vihaan, Goldwaker. Conclusões e tabelas legíveis: `vihaan-goldwaker-mardu/goldfish-log.md` (seção "Make an Example, Slaughter the Strong e Mythos of Snapdax: as 3 que o usuário escolheu") e `vihaan-goldwaker-mardu/checklist-oraculo.md` (seção do topo).

Mensagem do usuário, transcrita sem reescrever:
> *"Gostei de Make an Example, Slaughter the Strong, Mythos of Snapdax\nWinnowing não é útil contra decks tribais, onde 90% das criaturas compartilham o mesmo tipo, ou decks de artefatos onde todas as criaturas são criaturas artefatos!"*

**Nada foi trocado na lista** (decisão do usuário) e **o simulador não foi alterado** (`vihaan_goldfish_v1.py` segue no commit `a17049f`). Esta rodada tem duas partes: (1) **Commander Spellbook antes/depois** das 3 cartas com os dois cortes possíveis (Blasphemous Act e Blood Money) e controles positivos; (2) as 3 cartas (e as referências) **separadas por fase do turno** (1ª main × 2ª main), recalculadas a partir do bruto do ensaio a seco da rodada `2026-10-04-wipes-de-sacrificio` (nenhuma simulação nova).

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (3 saídas, segundos) |
| abrir os brutos em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora) |

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `dados/spellbook_cru.json.xz`, `dados/spellbook_resumo.json` | Commander Spellbook `find-my-combos`, 14 consultas: base, `−Act`, `−Blood Money`, 2 controles positivos e, para cada uma das 3 cartas, `+X (sem cortar)`, `−Act +X`, `−Blood Money +X` | `csb_tres.py` | **usado (log: "Commander Spellbook")** | `resumos/spellbook.txt` |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo completo + 69 rulings de 12 cartas (as 3, Winnowing, Teferi's Protection, Boros Charm, Mayhem Devil, Dictate, Revel in Riches, Act, Blood Money, Vihaan), subconjunto de `../2026-10-04-wipes-de-sacrificio/dados/oraculo_candidatas_rulings.json` (lido ao vivo no Scryfall em 2026-10-04, antes de modelar) | — | usado | log / checklist |
| `resumos/estrato_fase_padrao.txt`, `resumos/estrato_fase_resiliencia.txt` | Act, Blood Money, Slaughter, Mythos, By Invitation Only [N=motores] e Edict por fase (1ª main × 2ª main, com e sem Mayhem Devil), a partir de `../2026-10-04-wipes-de-sacrificio/dados/raw_dry_run_{padrao,resiliencia}_10000.json.xz` | `estrato_fase.py` | **usado (log: tabela por fase)** | log |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh` | verificação | — |

Nenhum lote superado ou inválido nesta pasta.

**Comandos que reproduzem cada tabela** (de dentro de `orquestracao/`): `python3 csb_tres.py --sum` → `spellbook.txt` (a consulta à API é `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 csb_tres.py`) · `python3 estrato_fase.py padrao` → `estrato_fase_padrao.txt` · `python3 estrato_fase.py resiliencia` → `estrato_fase_resiliencia.txt`.

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh` → **3/3 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`): o texto do Spellbook refeito do bruto cru, e as duas tabelas por fase refeitas do bruto da rodada anterior. **Não conferido byte a byte:** a resposta do Commander Spellbook e o oráculo/rulings (API ao vivo): as respostas **cruas estão guardadas**, mas uma nova consulta pode devolver dados diferentes (combos e rulings mudam).
Controles positivos do Spellbook funcionaram: cortar Smothering Tithe tira 3 combos; cortar Ashnod's Altar tira 1.

## O que NÃO foi verificado (Regra #7)

- O efeito de cada carta **no campo dos oponentes** (📊: o simulador não modela criatura de oponente). A Make an Example **não está no harness** (só foi medida em castabilidade na rodada anterior: 48,9% dos estados) porque só os oponentes sacrificam.
- A comparação **carta a carta com o que sai** (Act ou Blood Money): só há o Spellbook (nenhum corte tira combo da lista) e as medidas de referência; o corte é decisão do usuário.
- As linhas "Teferi's Protection antes do Mythos" e "gastar os Treasures antes de conjurar o Mythos" são **raciocínio** (oráculo + rulings), não medidas.
- A frequência real de campos grandes, de indestrutível e de Mayhem Devil nas mesas do usuário.
