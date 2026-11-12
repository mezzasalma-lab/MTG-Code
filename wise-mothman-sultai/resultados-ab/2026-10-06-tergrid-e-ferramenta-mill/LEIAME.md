# Ferramenta de mill nos oponentes + avaliação da Tergrid (Mothman, 2026-10-06)

Pergunta do usuário (2026-10-06): *"Você consegue simular o efeito do mill nos oponentes, ou criar uma ferramenta para isso? Também pensei em colocar a Tergrid no deck, ela aproveita muito o mill, não? Ou apenas sacrifício e discard?"*
Arquivo **permanente e auditável** do que sustenta o §6 de `../../goldfish-log.md` e o §12 de `../../candidatas-pos-eoe.md`.
Simulador: `../../mothman_goldfish_v1.py` no commit **`91b1a3d`** (sem edição nesta rodada). Ferramenta nova: `../../ferramentas/mill_oponentes.py` (commit que adiciona esta pasta). Os outros A/B do deck: `../2026-10-05-ab-pacote-kozilek-master/`, `../2026-10-05-ab-kozilek-self-deck/`.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o mill por turno / por fonte / o que ele rende | `resumos/mill_oponentes_padrao_5000.txt` (5 variantes) e `mill_oponentes_resiliencia_5000.txt` (2 variantes) |
| rodar a ferramenta | `python3 ferramentas/mill_oponentes.py -n 5000 [--modo resiliencia] -v base -v pacote5 …` (uso completo no cabeçalho do arquivo) |
| refazer as tabelas dos brutos / re-simular | `bash orquestracao/verificar_reproducao.sh` · `… --tudo` (re-simula, ~5 min) |
| ver a Tergrid | `resumos/enumera_tergrid.txt`, `resumos/spellbook_tergrid.txt`, `resumos/frequencia_annihilator.txt`, `dados/tergrid_carta.json`, `dados/tergrid_rulings.json` |
| descomprimir / conferir | `bash descomprimir.sh` · `sha256sum -c SHA256SUMS` · `python3 indice_dados.py` (saída em `resumos/indice_dados.txt`) |

## Como foi gerado

- **Ferramenta:** roda o laço de `simulate_one` / `simulate_one_with_interaction` (mesma ordem de chamadas) e amostra, ao fim de cada rodada, o estado dos 3 oponentes passivos (biblioteca de 99 por tipo, 40 de vida, rad, mill real; ver `../../goldfish-log.md` premissas). Produz: (1) por TURNO, cartas milladas, % da biblioteca deles já milada, biblioteca restante e oponentes fora por biblioteca vazia; (2) por FONTE, de onde vem cada carta milada (`opp_mill_by_source`); (3) o que o mill rende (gatilhos do Mothman, contadores, rad, fichas, Konrad, crimes, como os oponentes saem); (4) com 2+ variantes, diferença PAREADA (mesma semente) com IC95% = 1,96·dp(dif)/√N. **Auto-verificação:** as primeiras 8 sementes são comparadas campo a campo com `simulate_one` (o laço da ferramenta tem que reproduzir o do simulador; `> 0` conferido). Não edita o simulador (variantes por `SWAPS`/flags em memória).
- **Lotes:** N = 5.000, sementes 3.000.000+i, 12 turnos. Padrão: `base`, `pacote5`, `pacote5+master`, `bruvac`, `sem_kozilek`. Resiliência: `base`, `pacote5+master`. Definições das variantes: `PRESETS` no topo da ferramenta (`pacote5` = as 5 trocas de `../../candidatas-pos-eoe.md` §0; `master` = The Master of Lake-town ← Negate). Comandos exatos: `orquestracao/comandos.sh`.
- **Tergrid:** (a) oráculo + rulings ao vivo do Scryfall (`dados/tergrid_*.json`); (b) `orquestracao/enumera_tergrid.py` lista POR SCRIPT, lendo o oráculo do repositório (Regra #4, adendo 4), as cartas da lista que fazem o oponente sacrificar/descartar; (c) `orquestracao/spellbook_tergrid.py`: Commander Spellbook antes/depois, com **resolução de nome** (`GET /cards/?q=`), **controle positivo** (Thassa's Oracle + Demonic Consultation aparece) e **controles de corte** (cortar Mindcrank faz sumir Bloodchief Ascension + Mindcrank; cortar Glen Elendra faz sumir Altar of Dementia + The Great Henge); (d) `orquestracao/frequencia_annihilator.py`: em quantas partidas o Kozilek (única fonte de "oponente sacrifica") chega a atacar, N = 10.000 × 2 modos, sementes 3.000.000+i; (e) `orquestracao/crime_deepmuck.py`: teto do elo Lantern → crime → Deepmuck/Freestrider (a Lantern mira um jogador; mirar oponente é crime), medido como os turnos em que o Deepmuck já está em campo e não houve crime (N = 5.000 × 2 modos).
- **A Tergrid NÃO foi implementada no motor do simulador.** O A/B pareado dela não existe; só o oráculo, a enumeração, o Spellbook e o teto de frequência (ver `../../candidatas-pos-eoe.md` §12 para o raciocínio e o que falta).

## Mapa: arquivo → o que é → status → onde é usado

| arquivo | o que é | status | usado em |
|---|---|---|---|
| `dados/mill_oponentes_padrao_5000.json.xz` | bruto por partida (5 variantes × 5.000), modo padrão | usado | `resumos/mill_oponentes_padrao_5000.txt`, `../../goldfish-log.md` §6 |
| `dados/mill_oponentes_resiliencia_5000.json.xz` | idem (2 variantes), resiliência | usado | `resumos/mill_oponentes_resiliencia_5000.txt`, §6 |
| `dados/tergrid_carta.json`, `tergrid_rulings.json` | JSON do Scryfall (oráculo e rulings lidos ao vivo, 2026-10-06) | usado | `candidatas-pos-eoe.md` §12, `enumera_tergrid.py` (marca Game Changer) |
| `dados/spellbook_tergrid.json` | resposta do Commander Spellbook por cenário (8) com nomes resolvidos | usado | `resumos/spellbook_tergrid.txt` |
| `resumos/enumera_tergrid.txt` | saída do `enumera_tergrid.py` (91 cartas lidas, > 0) | usado | §12 |
| `resumos/frequencia_annihilator.txt` | saída do `frequencia_annihilator.py` | usado | §12 |
| `resumos/crime_deepmuck.txt` | saída do `crime_deepmuck.py` | usado | §12 |
| `resumos/verificacao_reproducao.txt` | saída do `verificar_reproducao.sh --tudo` | usado | abaixo |
| `resumos/indice_dados.txt` | saída de `indice_dados.py` | usado | — |

Inválido: nenhum. Superado (**não arquivado**): a primeira versão dos dois `.txt` de mill, gerada antes das duas correções da ferramenta descritas abaixo; o bruto é o mesmo (bit a bit), só mudou o texto: uma linha de desempate e uma linha nova.

## Achados da própria ferramenta (corrigidos antes de arquivar; nenhum afeta os dados brutos)

1. **Ordem de desempate dependia de `PYTHONHASHSEED`** (classe da Regra #10): a linha "por fonte (dif)" ordenava um `set` de nomes por `-|dif|`; empate exato (altar_of_the_brood × mesmeric_orb, −0,25 ambos) saía em ordem diferente entre processos. Detectado ao refazer a tabela do bruto em outro processo (a verificação deu "DIFERE"). Correção: chave `(−|dif|, nome)`; conferido: texto idêntico em 6 valores de `PYTHONHASHSEED` × 2 modos.
2. **A soma por fonte não fechava com o total de cartas milladas** (80,9 contra 83,9 por partida no padrão base): o loop do combo Ascension + Mindcrank/Master (`ascension_hit`) mila a biblioteca inteira do oponente fora de `mill_event`, e por isso fora de `opp_mill_by_source`. Conferido nos brutos: resíduo > 0 só em partidas com `ascension_loops > 0`, resíduo < 0 em 0 partidas (7 variantes × modos); em 1 a 10 partidas por variante o combo disparou com a biblioteca do alvo já vazia (resíduo 0). Correção: linha `ascension_loop` na tabela e **asserção** (resíduo ≥ 0, só com o combo; a soma das fontes = total, e total > 0).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-06: **6 de 6 saídas byte a byte iguais** (`cmp`): as 2 tabelas refeitas **só** dos `.json.xz` (`mill_oponentes.py --do-bruto`, sem as linhas de auto-verificação), e, **re-simulando** (`PYTHONHASHSEED` distinto do original em cada uma), o bruto da resiliência (descomprimido, 777), o texto inteiro da resiliência (com auto-verificação) as duas frases do annihilator (10.000 × 2 modos) e as quatro do teto crime/Deepmuck (5.000 × 2 modos).
Além disso, o bruto foi re-simulado com `PYTHONHASHSEED` diferentes e saiu **idêntico byte a byte** ao arquivado: padrão com 11 e 31 (122.743.686 bytes descomprimidos); resiliência com 22, 32 e 777 (49.755.510 bytes). As execuções de 11 e 22 e a de 777 são anteriores às duas correções da ferramenta (que só mudam o texto); as de 31 e 32 e todas as da `--tudo` usam a versão final.
**Atualização (mesmo dia, depois da correção `LANDFALL_PAYOFF_FIRST`, `../2026-10-06-landfall-payoff-primeiro/`):** o padrão do simulador passou a ligar a ordem "payoff de landfall antes do terreno"; estes lotes são da ordem antiga. `mill_oponentes.py --fixa LANDFALL_PAYOFF_FIRST=false` (que também tira o campo novo `payoff_first_casts` do bruto) e a fixação da chave nos 2 scripts de `orquestracao/` reproduzem os brutos arquivados: `verificar_reproducao.sh --tudo` refeito: **6 de 6 iguais**. Rodar a ferramenta sem `--fixa` usa a ordem nova e dá números ligeiramente diferentes (+1,9% de cartas milladas dos oponentes no padrão).
**Não conferido:** `spellbook_tergrid.json` e `tergrid_*.json` vêm de APIs externas e não foram refeitos (o Spellbook pode mudar com o tempo; os controles positivo e de corte rodaram junto, na mesma consulta); `enumera_tergrid.py` não está no `--tudo` (lê o oráculo do cache do repositório e é determinístico); `log_*` ficam fora do git. A Tergrid não foi simulada, então não há A/B para reproduzir.
