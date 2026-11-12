# A/B pareado: o Kozilek evita a morte por self-mill? (2026-10-05)

Pergunta do usuário (2026-10-05): *"O Kozilek serve para evitar a morte por self mill"* → quanto ele salva, e com que estilo de jogo. Arquivo **permanente e auditável** do que sustenta o §"Kozilek" de `../../goldfish-log.md`.
Simulador: `../../mothman_goldfish_v1.py` no commit **`91b1a3d`**. Companheiro: `../2026-10-05-ab-pacote-kozilek-master/` (mesmo driver, mesmas sementes dos lotes).

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver a tabela principal | `resumos/compacto_10000.txt` (padrão) e `compacto_10000_resiliencia.txt`; todas as métricas em `ab_10000*.txt` |
| refazer as tabelas dos brutos | `bash orquestracao/verificar_reproducao.sh` (`--tudo` re-simula o lote de 2.000) |
| descomprimir / conferir | `bash descomprimir.sh` · `sha256sum -c SHA256SUMS` |

## Como foi gerado

Pareamento, IC95%, métricas e lotes iguais ao do companheiro (2.000 = sementes 1.000.000+i com 19 variantes; 10.000 = sementes 3.000.000+i com 9 variantes; modos padrão e resiliência; 12 turnos). Variantes em `orquestracao/config.json`:

- **O que é "Kozilek sem seguro":** `K_sem_embaralhar` (a carta existe, compra 4 ao ser conjurada, mas o gatilho "quando vai a um cemitério, embaralha o cemitério na biblioteca" é desligado) e `K_cortado_por_forest` (a carta sai da lista, entra uma Forest).
- **Estilo de jogo (a guarda de biblioteca):** a IA evita, por regra declarada, mill/compra *opcionais*, atacantes a mais (por causa do Mesmeric Orb) e engines de compra obrigatória quando a biblioteca não aguenta (`library_budget`). `guarda_desligada` = IA descuidada (controle: tem que MOVER `self_lost` para cima, e moveu); `reserva_0`/`reserva_16` = reserva de segurança (cartas intocáveis na biblioteca) de 0 e de 16 em vez de 8; `orb_sem_limite` = pode conjurar o Mesmeric Orb com qualquer biblioteca; `palantir_sempre_recusa` = o oponente sempre recusa o Palantír (eu milo X em vez de comprar).
- Cada um dos "estilos" combinado com `K_sem_embaralhar` e `K_cortado_por_forest`.

## Mapa

| arquivo | o que é | status | usado em |
|---|---|---|---|
| `dados/raw_ab_2000.json.xz`, `raw_ab_2000_resiliencia.json.xz` | bruto por partida (19 variantes × 2.000) | usado | `ab_2000*.txt`, `compacto_2000*.txt` |
| `dados/raw_ab_10000.json.xz`, `raw_ab_10000_resiliencia.json.xz` | bruto (9 variantes × 10.000) | usado | `ab_10000*.txt`, `compacto_10000*.txt`, `../../goldfish-log.md` |
| `resumos/smoke.txt` | 19 variantes: 99 cartas, 0 desconhecidas, 0 exceções em 200 partidas/modo | usado | — |
| `resumos/regressao_20000.txt` | 4 configurações extremas × 20.000, 0 exceções | usado | — |

Execuções superadas e não arquivadas: as mesmas do companheiro (2 erros raros de combate e 1 reinício do contêiner).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-05, no commit `91b1a3d`: **12 de 12 saídas byte a byte iguais** (`cmp`): as 4 tabelas `ab_*.txt` e as 4 `compacto_*.txt` refeitas **só** dos `.json.xz`, e, **re-simulando** o lote de 2.000 nos dois modos (pasta temporária), as 2 tabelas e os 2 **brutos** (descomprimidos) idênticos aos arquivados (saída: `resumos/verificacao_reproducao.txt`).
Isso também prova o determinismo do simulador entre processos nesse lote.
**Não conferido:** os lotes de 10.000 foram verificados só das tabelas a partir do bruto (não re-simulados: ~25 min cada); `smoke.txt` e `regressao_20000.txt` não foram refeitos pelo script (saídas das execuções originais); `log_*.txt` ficam fora do git.

## Atualização (2026-10-06): a ordem terreno × payoff de landfall mudou no simulador; estes lotes são da ordem ANTIGA
O padrão do simulador passou a ligar `LANDFALL_PAYOFF_FIRST` (payoff de landfall conjurado antes do terreno; `../2026-10-06-landfall-payoff-primeiro/`). Os lotes desta pasta são do simulador `91b1a3d` = chave **desligada**. Para que a re-execução continue idêntica aos brutos arquivados, `orquestracao/driver_mm.py` fixa `LANDFALL_PAYOFF_FIRST = False` em toda variante (`setdefault`) e `orquestracao/abgen.py` ignora o campo novo `payoff_first_casts` (sempre 0 com a chave desligada). `bash orquestracao/verificar_reproducao.sh --tudo` refeito em 2026-10-06: **12 de 12 iguais** (`resumos/verificacao_reproducao.txt`).

