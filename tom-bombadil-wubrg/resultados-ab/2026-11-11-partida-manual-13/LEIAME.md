# Tom Bombadil: partida manual #13 (2026-11-11): dados brutos, scripts, ledgers, testes e rulings

Arquivo da Regra #8 (`CLAUDE.md`). **Status: compilada com as respostas do usuário (2026-11-11)**; a análise em prosa está na seção "Partida manual #13" de `tom-bombadil-wubrg/goldfish-log.md`.
**7 turnos**, simulador de interação **On**, **Mulligan (0)**, com foto da mão inicial. O usuário parou no T7 (*"Não joguei mais, não usei o gold"*).

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do playtester do Archidekt que o usuário colou com *"Goldfish manual do Tom Bombadão. Mão inicial na foto. Segue o log:"* (7 blocos de turno, 102 registros), extraído **por script, sem redigitar** da transcrição da sessão (`orquestracao/extrair_json_da_conversa.py`). A mensagem inteira está em `dados/mensagem_usuario_original.txt.xz`.
- **Foto da mão inicial** (`dados/mao_inicial_foto.webp`; "Keep this", **Mulligan (0)**, interação **On**): Satsuki the Living Lore, Historian's Boon, Godless Shrine, The First Iroan Games, Command Tower, Wooded Foothills, The Cruelty of Gix. A 8ª carta do T1 (Serra's Sanctum) é a compra do turno (8 = 7 + 1, confere com o log).
- Oráculos: `scryfall-cache/oracle-cache.json` (todos os nomes do log estão lá, exceto a **Song of the Dryads**, carta do oponente simulado: *"Enchant permanent. Enchanted permanent is a colorless Forest land."*, vista só no log).
- **Rulings** (Scryfall, ao vivo, 2026-11-11) de 23 cartas em `resumos/rulings_scryfall.json` (86 rulings, 0 erros de rede), **lidas antes de concluir**. As que decidem: Tom Bombadil (2023-06-16: "triggers when ... it has been removed from the stack"), as de Saga de Binding the Old Gods e Summon: Yojimbo (*"Removing lore counters won't cause a previous chapter ability to trigger. If lore counters are removed from a Saga, the appropriate chapter abilities will trigger again when the Saga receives more lore counters."*), Song of the Dryads (*"loses all other abilities"*) e Satsuki (um marcador numa Saga que já está no capítulo final não dispara nada).
- Regras: **`rules-cache/comprehensive-rules.txt`** (CR de 2026-09-25, regra permanente §18; **nada foi baixado**), trechos em `resumos/cr_2026-09-25_trechos.txt` (714.2b, 714.2d, 714.2e, 714.3c, 714.4, 704.3, 117.5, 603.2, 603.3b, 302.6, 305.2).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz`, `dados/mensagem_usuario_original.txt.xz`, `dados/mao_inicial_foto.webp` | log bruto, mensagem e foto | bruto |
| `analisa_partida.py` → `resumos/trace.md` | trace e verificações automáticas (cópia da #12) | usado (`cmp`) |
| `ledger_compras.py` → `resumos/ledger_compras.md` | compras ESPERADO × LOG por turno (16 × 16); eventos esperados = leitura minha (cabeçalho do script) | usado (`cmp`) |
| `ledger_fichas.py` → `resumos/ledger_fichas.md` | fichas ESPERADAS pelo oráculo da Historian's Boon × LOG: **Soldier −1 no T5, Angel −1 no T7** | usado (`cmp`) |
| `ledger_mana.py` → `resumos/ledger_mana.md` | mana disponível × custo por turno; custos lidos do cache e conferidos por `assert` | usado (`cmp`) |
| `testes_manual13.py` → `resumos/testes_manual13.txt` | 15 testes dirigidos contra o bruto, o oráculo, as rulings e a CR, cada um com controle de corte | **15/15** (`cmp`) |
| `resumos/estado_por_turno.txt`, `resumos/sequencia_bruta.txt` | estado ao fim de cada turno; os 102 registros em ordem | apoio: **o log não registra ficha que some** |
| `resumos/rulings_scryfall.json` | rulings ao vivo de 23 cartas | usado (**não** conferido por `cmp`: depende da API) |
| `resumos/cr_2026-09-25_trechos.txt` | trechos da CR do `rules-cache` | usado (`cmp`) |
| `orquestracao/*.py` | extração do JSON, rulings, estado por turno, sequência bruta, trechos da CR | apoio |
| `verificar_reproducao.sh`, `descomprimir.sh`, `SHA256SUMS` | refaz cada saída de `resumos/` dos `.xz` e compara com `cmp`; somas | ver abaixo |

Reproduz (qualquer pasta): `bash tom-bombadil-wubrg/resultados-ab/2026-11-11-partida-manual-13/verificar_reproducao.sh`. Simulador (`tom_goldfish_v1.py`): **não alterado**.

## Resultado em 1 minuto
**0 violações provadas pelo log; 2 pontos de fichas esquecidos, confirmados pelo usuário; os 2 "incrementos extras" de marcador têm fonte.**
1. **T5: faltou o 2º Human Soldier.** A There and Back Again (encantamento não-ficha) entrou pelo Tom com a Historian's Boon em campo: *"Whenever this enchantment or another nontoken enchantment you control enters, create a 1/1 white Soldier"*. Resposta: *"Esqueci"*.
2. **T7: faltou o Angel da Boon.** A Boon dispara quando o capítulo final **dispara** (o marcador chega a 3), **não** quando a Saga é sacrificada. Resposta: *"Esqueci de criar o boon pq não sacrifiquei a saga"*: o motivo declarado está errado (o Angel não depende do sacrifício), o fato (esqueceu) está confirmado.
3. **T7: a Goldberry tirando o marcador (3 → 2) para a Saga ficar em campo é legal, se foi com o capítulo III ainda na pilha** (pergunta do usuário: *"É isso mesmo?"*). O log mostra essa ordem: marcador 3 → Goldberry vira → marcador 2 → **só então** a ficha do Smaug (capítulo III resolvendo) → Goldberry com 1 marcador → Binding the Old Gods (Tom). A CR 714.4 só manda sacrificar a Saga com marcadores ≥ capítulo final **se ela não é fonte de um capítulo que disparou e ainda não saiu da pilha**; com o marcador removido em resposta, quando o capítulo sai da pilha a Saga tem 2 e não é sacrificada. **Se a Goldberry tivesse sido ativada DEPOIS** (com o gatilho do Tom na pilha), a Saga já teria sido sacrificada: as ações baseadas em estado rodam antes de qualquer jogador receber prioridade e antes de o gatilho do Tom entrar na pilha (CR 117.5, 704.3). Pelas rulings, a Saga com 2 marcadores dispara o capítulo III de novo no próximo marcador (Smaug, Angel da Boon e, 1 vez por turno, o Tom).
4. **T6: o clique do saber da There and Back Again foi pulado, mas o efeito do capítulo II foi aplicado.** O log tem a Ketria Triome (Forest Island **Mountain**) da biblioteca para o campo virada no T6 (é o "Search your library for a Mountain card"); no T7 há dois cliques na Saga (→2, →3) e um só na Yojimbo (→2). Leitura minha: o 1º clique do T7 é o atraso do T6 e o 2º é o do T7. Resposta do usuário: *"Pulei, esqueci"*.
5. **T5–T6: Song of the Dryads.** O oponente a pôs no Tom no T5 (o marcador `Forest` no log); no T6 o capítulo I da Summon: Yojimbo a **exilou** (*"Exilei o Song of the Dryads para o Tom voltar ao normal"*), alvo legal (encantamento do oponente). Enquanto durou, o Tom era um terreno incolor Forest sem as outras habilidades (ruling de 2014-11-07); nenhum capítulo final resolveu nesse intervalo.
6. **T7:** parou, sem jogar as 4 cartas da mão; **a ficha de Gold ficou sem uso**. **Interações usadas: sem resposta.**
7. **Compras 16 = 16**: T5 tem 3 porque o marcador natural da Iroan (2 → 3) dispara o capítulo III antes de qualquer magia do turno, e o Soldier do T4 (3 marcadores +1/+1: 4/4) já cumpre "creature with power 4 or greater": Goldberry e Fertile Ground vêm antes de o Tom ser lançado. **Mana fecha de T2 a T6** (T6 sem folga, supondo a Fertile Ground num terreno que vira depois; o Bloom Tender ficou sem uso).

## O que o script prova e o que não prova
**Prova:** 1 terreno por turno (objetos distintos), a busca da Foothills, compras por turno, ordem dos eventos de Saga no log, fichas por turno, marcadores por objeto, 1 gatilho do Tom por turno, a presença/ausência do marcador `Forest` no Tom.
**Não prova:** vida (o log não a registra), a COR da mana (só o total; o T5 foi conferido à mão), em qual terreno a Fertile Ground ficou, quantas interações o gerador usou, a ordem exata da pilha (o log registra mudanças de estado, não a pilha), o que sumiu sem registro (fichas), a intenção do usuário. **A leitura "Goldberry em resposta ao capítulo III" vem da ORDEM dos registros do log, que pode refletir a ordem dos cliques e não a da pilha.**

## Respostas do usuário (2026-11-11), na ordem das dúvidas
1. T5, 2º Soldier: *"Esqueci"*. 2. T7, Angel e Goldberry: *"Esqueci de criar o boon pq não sacrifiquei a saga. Quando o marcador foi a 3 e triggou o Tom Bombadil, eu usei a Goldberry e tirei 1 lore counter voltando para 2, assim ela permanece em campo. É isso mesmo?"* 3. T6, marcador: *"Pulei, esqueci"*. 4. Song/Yojimbo: *"Exilei o Song of the Dryads para o Tom voltar ao normal."* 5. T7: *"Não joguei mais, não usei o gold"*.
**Sem resposta:** quantas interações foram usadas; se o 1º clique do T7 na There and Back Again foi mesmo o atraso do T6; se a Goldberry foi ativada com o capítulo III na pilha ou depois (o log sugere "na pilha").

## Verificação de reprodutibilidade
`bash verificar_reproducao.sh` (2026-11-11): **12 conferências, 0 falhas** (2 `.xz` íntegros; trace, `trace_stderr` vazio, 3 ledgers, estado por turno, sequência bruta, trechos da CR e os 15 testes refeitos e iguais por `cmp`; e `SHA256SUMS` confere). **Não conferidos por `cmp`:** `resumos/rulings_scryfall.json` (API ao vivo) e a extração do JSON da conversa (depende do registro da sessão). Os eventos esperados dos ledgers são leitura minha, declarada no cabeçalho de cada script.
