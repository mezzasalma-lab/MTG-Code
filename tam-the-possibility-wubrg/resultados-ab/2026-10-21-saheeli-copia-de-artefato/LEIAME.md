# 2026-10-21 — Tam: Saheeli −2 como cópia de artefato de mana

Origem: o goldfish manual #2 do usuário (`../2026-10-20-goldfish-manual-2/LEIAME.md`). No T6 ele usou o `−2` da Saheeli num Servo para copiar o Fellwar Stone até o fim do turno e pagar o Teferi (4 de mana). O simulador só modelava metade da cláusula do oráculo (*"Target artifact you control becomes a copy of another target artifact **or creature** you control until end of turn, except it's an artifact in addition to its other types"*): a cópia de P/T de criatura grande. A metade "artefato" não existia (o `checklist-oraculo.md` declarava *"não varrido: cópia de habilidades"*). Regras #1 e #5 da CLAUDE.md: é implementação parcial de uma carta modelável, não limite do goldfish.

## Conclusão (medido)

**Implementada**, com a chave `SAHEELI_COPY_MANA_ARTIFACT` (padrão `True`; `False` = comportamento do commit `e01054f`, bit a bit). Efeito **pequeno no baseline**: a cópia de mana dispara em **2,94% das partidas do modo padrão e 2,02% da resiliência** (N = 10.000 pareado; `resumos/resumo_saheeli.md`); **97,06% / 97,98% das partidas são idênticas** ao simulador anterior. No baralho todo o ganho médio é **0,058 (padrão) / 0,040 (resiliência) de mana por partida**. As métricas de mesa quase não se mexem (a do usuário, T6, é um caso raro no baralho todo):

| | modo padrão (depois / antes / dif. ± IC95%) | modo resiliência |
|---|---|---|
| ativações da Saheeli por partida | 0,9569 / 0,9397 / **+0,0172 ± 0,0057 \*** | 0,4034 / 0,3849 / **+0,0185 ± 0,0064 \*** |
| mana disponível no início do T6 | 7,1166 / 7,1145 / +0,0021 ± 0,0021 \* | 6,2197 / 6,2192 / +0,0005 ± 0,0011 |
| planeswalkers no fim do T6 | 3,1370 / 3,1341 / +0,0029 ± 0,0014 \* | 1,6337 / 1,6329 / +0,0008 ± 0,0009 |
| mesa limpa até T8 | 13,19% / 13,12% / +0,07 ± 0,08 | 0,42% / 0,41% / +0,01 ± 0,02 |
| mesa limpa até T10 | 64,84% / 64,74% / **+0,10 ± 0,10 \*** (no limite) | 4,80% / 4,80% / 0,00 ± 0,06 |

**A linha de base de `../../goldfish-log.md` §1 continua valendo dentro de ±0,1 ponto.** Não renumerei o log. No replay do goldfish manual #2 (mão com Saheeli e Fellwar desde o início) a cópia dispara em 47% (padrão) e 14% (resiliência) das ordens: o efeito depende da mão, e cai para ~3% no baralho todo.

## O que mudou no código (`tam_goldfish_v1.py`)

- `Permanent.copy_of`: nome da carta de que o artefato virou cópia até o fim do turno; limpo em `end_step`. `is_creature` devolve se a **carta copiada** é criatura (uma cópia de Sol Ring/Signet/Fellwar deixa de ser criatura: sem doença de invocação, CR 302.6, e a ruling de 2019-05-03: só a que "becomes a creature" fica sem poder usar `{T}` no turno em que entrou). `mana_sources` usa `p.copy_of or card.name`.
- `saheeli_mana_choice`: alvo = **Servo/Food desvirado**; fonte = o artefato de mana **não lendário** que mais rende (**Sol Ring 2**, Arcane Signet 1, Fellwar Stone 1, esse só com cor de terreno de oponente). **Chromatic Orrery e The Chain Veil não são copiados** (`Legendary Artifact` no Scryfall: a cópia violaria a regra da lenda e eu perderia um dos dois). Só em `main1`/`main2`.
- `saheeli_mana_wanted`: **ensaio a seco** (marca a cópia, testa `can_cast_name`, desmarca; sem efeito colateral): só gasta os 2 de lealdade se uma carta valiosa da mão (prioridade ≥ 40) que não cabia passa a caber.
- `activation_pick`: a ativação passa a poder ocorrer **antes** de conjurar (como o `+1` da Chandra) só nesse caso (`saheeli_mana_pre`); nos demais, o `−2` antigo (cópia de P/T) é o mesmo.
- Contadores `saheeli_mana_copies` e `saheeli_mana_copy_extra` (campos `m_*` novos).

**Rulings** (`../2026-10-19-simulador-baseline/dados/rulings_deck.json`, 8 da Saheeli, conferidas contra o código **depois** de escrevê-lo; nenhuma o contradiz): copia os valores IMPRESSOS + efeitos de cópia, sem contadores nem efeitos que mudam P/T/tipos; é artefato além dos outros tipos; se o alvo copia algo que copia outra coisa, vira o original (não ocorre: copio só cartas em campo); efeito que já se aplicava continua (não ocorre); doença de invocação só se virar criatura no turno em que entrou (a cópia de artefato de mana não é criatura).

## O que NÃO está coberto (Regra #7)

(1) A cópia de **habilidades de criatura** (Birds, Bloom Tender, Flux Channeler, Displacer Kitten...) continua só P/T. (2) Staff of Compleation não é copiado (traz outras habilidades: a cópia teria que modelar todas). (3) Cópia com alvo que não seja Servo/Food (o Treasure perderia a própria habilidade). (4) **Política**: o simulador só usa a cópia de mana se uma carta valiosa da mão passa a caber (ensaio a seco); um jogador pode usá-la por outros motivos. (5) Uma só família de sementes por lote.

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| testes dirigidos | **171/171** (146 anteriores + 16 de `t_manual2.py`, sendo 13 do relato do goldfish #2 e 3 da cópia de mana, + 9 de `t_manual3.py`) | `../../testes/` |
| smoke (99 cartas, 0 desconhecidas, 0 duplicadas, 200 partidas × 2 modos × 2 versões) | 0 exceções | `resumos/smoke.txt` |
| **bit-identidade:** vivo com `SAHEELI_COPY_MANA_ARTIFACT=False` == snapshot `e01054f` (sementes 5.000.000+i; impressão digital do resultado inteiro; `copy_of` ignorado em qualquer profundidade) | **20.000 / 20.000 por modo, 0 diferenças** | `resumos/bitident_20000.txt` |
| regressão 20.000 × 2 modos, `depois` e `chave_desligada` | 0 exceções, 0 carta acima do baralho, 0 campo negativo (4 configurações) | `resumos/regressao_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo (chave ligada e desligada) | 0 divergências nos 4 casos | `resumos/determinismo.txt` |
| A/B pareado `antes` × `depois`, N = 2.000 e 10.000 × 2 modos | tabela acima | `resumos/ab_*.txt`, `resumo_saheeli.md` |
| reprodutibilidade (`orquestracao/verificar_reproducao.sh --tudo`) | ver `resumos/verificacao_reproducao.txt` | idem |

### 1ª rodada INVÁLIDA (guardada e marcada, Regra #8)

A primeira bit-identidade deu **"diverge 20.000/20.000"**: todo `Permanent` ganhou o atributo novo `copy_of`, e a impressão digital (que cobre o resultado inteiro, em qualquer profundidade) incluía o campo que o snapshot não tem. Provei em 120 sementes por modo que essa era a única causa (sem ignorar o campo: 120/120 diferentes; ignorando-o em qualquer profundidade: 0/120). Acrescentei ao `driver.py` a chave `ignora_profundo` do `config.json` (`["copy_of"]`) e **refiz bit-identidade e A/B** (`cadeia2.sh`). Ficam arquivados e marcados: `resumos/bitident_20000_V1_INVALIDO.txt`; `resumos/ab_*_V1.txt` e `dados/raw_ab_*_V1.json.xz` (as tabelas, exceto a linha "IDÊNTICO ao anterior", são **iguais** às refeitas: reprodução gratuita do A/B).

## Mapa arquivo → o que é → status

| arquivo | o que é | status |
|---|---|---|
| `codigo/tam_goldfish_v1_ANTES_e01054f.py` (+ `tam_cartas.json`) | o simulador antes da correção | variante `antes` |
| `dados/raw_ab_2000[_resiliencia].json.xz`, `raw_ab_10000[_resiliencia].json.xz` | bruto por partida (colunas-v1): `antes` e `depois` | **usado** (2ª rodada, `copy_of` ignorado) |
| `dados/raw_ab_*_V1.json.xz`, `resumos/ab_*_V1.txt`, `resumos/bitident_20000_V1_INVALIDO.txt` | 1ª rodada | **superado / INVÁLIDO** (a impressão digital incluía `copy_of`) |
| `resumos/ab_*.txt`, `resumo_saheeli.md`, `bitident_20000.txt`, `regressao_20000.txt`, `smoke.txt`, `determinismo.txt`, `indice_dados.md`, `cadeia_horarios.txt`, `log_driver.txt`, `verificacao_reproducao.txt` | resultados | usado |
| `orquestracao/` | `driver.py` (com `ignora_profundo`), `abgen.py`, `config.json`, `cadeia.sh` (1ª), `cadeia2.sh` (2ª), `resumo_saheeli.py`, `verificar_reproducao.sh` | usado |

## Como refazer

```
bash descomprimir.sh                                                  # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 resumo_saheeli.py | cmp - ../resumos/resumo_saheeli.md       # a tabela desta conclusão, só dos brutos
bash verificar_reproducao.sh                                          # tabelas do A/B, resumo_saheeli e índice: cmp byte a byte
bash verificar_reproducao.sh --tudo                                   # re-simula smoke, bit-identidade, regressão e os 4 lotes (~70 min; não edite o simulador enquanto roda)
sha256sum -c ../SHA256SUMS                                            # integridade (rodar na pasta do arquivo)
```
