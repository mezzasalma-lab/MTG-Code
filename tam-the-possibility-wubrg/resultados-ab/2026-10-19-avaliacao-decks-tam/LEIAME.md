# 2026-10-19 — Tam, the Possibility: avaliação contra os decks do Moxfield (só proposta, nada aplicado)

Pedido do usuário (2026-10-19): *"Quero que vc avalie os decks no Moxfield com o mesmo comandante e ver o que podemos melhorar no nosso"*. **Entregue:** `../../avaliacao-moxfield.md` (a análise, em português, veredito primeiro). **A `lista.md` NÃO foi alterada**: as 6 trocas e as demais cartas são propostas, a aplicação depende de um "sim" do usuário. **Sem simulador** (pedido anterior do usuário): nenhum efeito sobre velocidade foi medido.

## Como os dados foram obtidos (e o limite)

- A API do **Moxfield devolveu 403** (Cloudflare); **não foi contornado**. O **EDHREC** guarda as listas enviadas pelos usuários, inclusive as do Moxfield, com a URL de origem: `coleta_edhrec.py` baixou a tabela de decks (6.931 do Tam em 2026-10-19), escolheu **todos os 719 com bracket 3 ou 4 declarado + 500 sorteados sem bracket (semente fixa)** e baixou `edhrec.com/api/deckpreview/<urlhash>` de cada um (1.219: **663 do Moxfield**, 556 do Archidekt).
- O deck `moxfield.com/decks/vxShAZ1_h32rYdwmXh4z5Q` tem **as mesmas 63 cartas não-terreno** que o nosso (é o deck do usuário já publicado): **fora de todas as comparações**. Base: **662 decks do Moxfield** (bracket 3: 326; bracket 4: 89; sem bracket: 247).
- **Não é amostra aleatória de todos os decks do Tam**; os 247 sem bracket são só uma amostra dos sem bracket.

## Mapa: arquivo → o que é → quem usa

| arquivo | o que é | usado em |
|---|---|---|
| `dados/decks_edhrec.jsonl.xz` | os 1.219 decks (campos úteis: URL de origem, bracket, preço, salt, tipos, cartas por tipo, tags) | `comparacao_estrutural`, `decks_parecidos`, `inclusao_cartas` |
| `dados/oraculos_referencia.json.xz` | oráculo ao vivo (Scryfall, por nome) de 2.660 cartas distintas, com `game_changer` | idem, `pacote_efeitos` |
| `dados/rulings_candidatas.json` | oráculo, `game_changer` e rulings (Scryfall) de 38 cartas, **lidos antes de avaliar** (Regra #3) | `avaliacao-moxfield.md` §4 a §7 |
| `dados/spellbook_adicoes.json` | Spellbook: deck exato + **uma candidata por vez** (37), 140 nomes resolvidos, 0 não reconhecidos, controles ok | §5 e §6 |
| `dados/spellbook_trocas.json` | Spellbook: cada uma das 6 trocas, o pacote e 5 opções (114 nomes, 0 não reconhecidos, controles ok) | §4 e §6 |
| `dados/spellbook_carth_variante.json` | passo-a-passo do combo que o Carth cria (variante `787-1124-4450`: `−1` do Teferi custa 0, **sem recast**) | §5 |

Scripts em `orquestracao/`: `coleta_edhrec.py`, `oraculos_referencia.py` (acrescenta ao `scryfall-cache/oracle-cache.json` o que faltava), `rulings_candidatas.py`, `csb_base.py` (cópia de `csb_tam.py` do registro), `csb_adicoes.py`, `csb_trocas.py`, `csb_carth_detalhe.py` (os quatro de Spellbook, com resolução de nomes, controle positivo e de corte), `comparacao_estrutural.py`, `decks_parecidos.py`, `inclusao_cartas.py`, `pacote_efeitos.py`, `indice_dados.py`, `verificar_reproducao.sh`.

| saída (`resumos/`) | script | o que mostra |
|---|---|---|
| `comparacao_estrutural.md` | `comparacao_estrutural.py` | nosso × Moxfield por categoria de oráculo (**regex**, heurística dos dois lados) e por tipo; coluna "com o pacote" |
| `decks_parecidos.md` | `decks_parecidos.py` | os 8 decks mais parecidos (Jaccard sobre as não-terreno) e o diff de cada um |
| `inclusao_cartas.md` | `inclusao_cartas.py` | % de inclusão de cada carta (B3, B3 com 22+ PW, todos); cartas ≥ 30% fora do nosso deck; cartas nossas < 15% |
| `pacote_efeitos.md` | `pacote_efeitos.py` | efeito **estático** do pacote: custo médio dos planeswalkers (Tam; Tam + Oath of Ajani), tipos, `game_changer` |
| `log_coleta.txt`, `log_spellbook_adicoes.txt`, `log_spellbook_trocas.txt`, `log_spellbook_carth.txt` | os scripts de API | a saída das execuções válidas |
| `indice_dados.md`, `verificacao_reproducao.txt` | `indice_dados.py`, `verificar_reproducao.sh` | o que há em cada arquivo; a conferência byte a byte |

## Como refazer

```
bash descomprimir.sh                          # .xz -> dados_json/ (fora do git)
cd orquestracao
python3 comparacao_estrutural.py | cmp - ../resumos/comparacao_estrutural.md
bash verificar_reproducao.sh                  # 5 comparações offline (cmp)
sha256sum -c ../SHA256SUMS
```

**Verificação feita antes de declarar arquivado:** `verificar_reproducao.sh` = **5/5 iguais** com `PYTHONHASHSEED` 0, 0, 7 e 123 (`resumos/verificacao_reproducao.txt`). **NÃO reproduzíveis byte a byte** (consultam API ao vivo; o bruto está arquivado): `coleta_edhrec.py`, `oraculos_referencia.py`, os 4 de Spellbook e `rulings_candidatas.py`. As 4 primeiras saídas dependem também de `../../lista.md` e do `scryfall-cache/oracle-cache.json`: **se uma troca for aplicada, elas mudam de propósito** (refazer e arquivar de novo).

## Escopo verificado e NÃO verificado (Regra #7)

**Varrido:** frequência de cada carta e 14 categorias de oráculo nos 662 decks (regex); combos pelo Spellbook (37 adições individuais, 6 trocas, o pacote, 5 opções, 1 variante lida); rulings das candidatas; custo médio dos planeswalkers; **cada afirmação de oráculo do documento foi conferida contra `oracle_text` do cache** (a primeira versão do texto tinha erros de detalhe escritos de memória, entre eles o custo do Loyal Tutor e o que as Ways fazem, corrigidos antes de arquivar).
**NÃO verificado:** velocidade, mulligan e resiliência (sem simulador); o texto oficial dos Brackets (as etiquetas S/E/R são as do Spellbook); a interação do `empower Jace` com a Doubling Season (nenhum ruling); se as fontes de lealdade do deck repõem o Teferi no laço atual com o Chain Veil; Spellbook de Heroic Intervention e Blood Crypt; decks do Moxfield fora do EDHREC.

## Incidentes

- Moxfield: 403 (Cloudflare), não contornado; amostra via EDHREC.
- Scripts: a comparação estrutural excluía o deck do usuário por igualdade de conjuntos que falhava (listas de terrenos diferentes): trocado por igualdade só das não-terreno; nomes de duas faces davam `info()` vazio: apelido da face da frente; empates de ordenação dependiam do hash: desempate por nome (conferido com `PYTHONHASHSEED` 1, 7 e 123).
