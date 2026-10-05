# Resultados brutos — The Wise Mothman: auditoria da lista e candidatas pós-Edge of Eternities (2026-10-05)

Arquivo **permanente e auditável** do que sustenta `wise-mothman-sultai/auditoria.md` e `wise-mothman-sultai/candidatas-pos-eoe.md`.
Aqui não há simulador (o deck não tem): os dados são **consultas à API do Scryfall e do Commander Spellbook**, contagens por script sobre o oráculo e contas de probabilidade.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver a conclusão | `../../candidatas-pos-eoe.md` (veredito no §0) e `../../auditoria.md` |
| ver uma tabela pronta | `resumos/` (mapa abaixo) |
| refazer todas as tabelas a partir dos dados | `bash verificar_reproducao.sh` (escreve numa pasta temporária; compara com `cmp`) |
| só descomprimir os dados | `bash descomprimir.sh` (vai para `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |

## Como foi gerado

- **Lista do usuário** (`../../lista-original-usuario.txt`, 91 linhas = 100 cartas): cada linha resolvida por **set + nº de colecionador** (`POST /cards/collection`), 91/91 achadas; guardado o JSON completo + `rulings`
  de cada uma (`dados/lista_bruto.json.xz`). `../../lista.md` tem os nomes reais; `../../nomes-de-capa.md` mapeia os 6 nomes de capa.
- **Pool pós-EOE:** `GET /cards/search?q=f:commander id<=bug date>=2025-08-01&unique=prints` (32 páginas, **5.474 impressões**), agrupado por `oracle_id` → **3.097 cartas únicas**
  (`dados/candidatas_impressoes_bruto.json.xz` → `dados/candidatas_indice.json.xz`). Hoje é 2026-10-05: `NAO-LANCADA` = todas as impressões com data futura.
- **Etiquetas** (regex sobre o oráculo: rad, proliferate, dobradores, mill, gatilhos de contador, trample concedido, terrenos com 2+ cores) → `resumos/candidatas_por_etiqueta.md`. **Triagem, não julgamento:**
  falsos positivos conhecidos (ex.: Angel of Suffering cai em "dobra" por "twice that many cards"; o regex de "entra virado" dava falso positivo nos choques e foi removido do script: esse ponto foi conferido à mão no oráculo).
- **Rulings** das cartas centrais e das 131 candidatas da shortlist: `dados/rulings_shortlist.json.xz`, `dados/lista_bruto.json.xz` → `resumos/rulings_principais.md`.
- **Commander Spellbook** (`POST https://backend.commanderspellbook.com/find-my-combos`, commander + 99 cartas; nomes resolvidos antes via `GET /cards/?q=`; **nome desconhecido é ignorado
  pela API sem erro**, por isso `mm_csb_lote.py` registra `spellbook_reconhece`: 121/121 reconhecidas): base, **controle positivo** (Thassa's Oracle + Demonic Consultation devolve o combo deles),
  cada candidata adicionada, cada troca, o pacote de 6 trocas, e **dois controles de corte** (cortar Mindcrank ou Glen Elendra faz o combo respectivo sumir: 2 → 1 nos dois).
  Passo a passo dos combos: `dados/spellbook_variantes_*.json.xz` (`GET /variants/<id>/`).
- **Probabilidades** (hipergeométrica, 99 cartas, 7 + 1 por turno): `resumos/numeros_por_script.txt`.
- **Preços:** `prices.usd` do Scryfall, menor impressão da janela (índice) e entre **todas** as impressões das cartas principais (`dados/precos_todas_impressoes.json.xz`).
- **Ainda não lançadas:** `dados/pre_lancamento_cartas.json.xz` (Homer the Hermit, Dominion Supervisor, etc.) e `dados/sets_nao_lancados_consulta.json.xz` (`e:trk or e:trc`, `e:mbc`, `e:sds`, sem filtro de legalidade).
- **Cache do repositório:** gravadas em `scryfall-cache/oracle-cache.json` no mesmo passo (Regras 14/15): 36 cartas novas da lista, 230 novas do pool (das 375 lidas; as outras já estavam) e 10 de pré-lançamento (total do cache: 3.324). `Overgrown Tomb` (ECL 350, cartão reversível) usa a chave do nome real.
- **Scripts** (`orquestracao/`, caminhos absolutos do repo `/home/user/MTG-Code`; os de API precisam de rede):

| script | o que faz | comando |
|---|---|---|
| `mm_fetch_lista.py` | baixa a lista por set+nº, grava bruto + cache | `python3 mm_fetch_lista.py ../../lista-original-usuario.txt dados` |
| `mm_fetch_candidatas.py` | baixa o pool pós-EOE | `python3 mm_fetch_candidatas.py dados` |
| `mm_candidatas.py` | agrega por `oracle_id` e gera o índice | `python3 mm_candidatas.py dados resumos` |
| `mm_listas_por_etiqueta.py` | tabelas por etiqueta | `… dados resumos/candidatas_por_etiqueta.md` |
| `mm_auditoria.py` · `mm_motores.py` · `mm_numeros.py` · `mm_condicoes.py` | auditoria, motores, hipergeométrica, condições | `… ../../lista.md resumos/<saida>.txt` |
| `mm_rulings_cache.py` | grava as lidas no cache e baixa as rulings | `python3 mm_rulings_cache.py dados mm_shortlist.json` |
| `mm_csb.py` · `mm_csb_lote.py` · `mm_quase_detalhe.py` | Spellbook (cenários, lote de candidatas, combos "quase") | ver docstrings; entradas em `mm_cen_*.json`, `mm_shortlist.json` |
| `mm_precos.py` | menor preço entre todas as impressões | `python3 mm_precos.py dados/precos.json "Carta A" "Carta B"` |
| `resumo_spellbook.py` · `resumo_rulings.py` | resumos **só** dos `.json` | `python3 resumo_*.py dados_json > resumos/…` |
| `mm_tags.py` · `mm_cat.py` · `mm_dump.py` | exploração interativa (listas por etiqueta/categoria) usada na leitura; não geram resumo publicado | — |

## Mapa: arquivo → o que é → status → onde é usado

| arquivo (`dados/`) | o que é | status | usado em |
|---|---|---|---|
| `lista_bruto` | 91 cartas da lista (JSON Scryfall + rulings) | usado | auditoria §1–§5, `rulings_principais.md` |
| `candidatas_impressoes_bruto` | 5.474 impressões do pool pós-EOE | usado | tudo de `candidatas-pos-eoe.md` |
| `candidatas_indice` | 3.097 cartas únicas (derivado; reproduzido byte a byte) | usado | `candidatas_por_etiqueta.md`, filtros |
| `rulings_shortlist` | rulings das 131 candidatas | usado | `rulings_principais.md` |
| `spellbook_base_e_controle` | base + controle positivo | usado | auditoria §6 |
| `spellbook_variantes_base`, `spellbook_variantes_candidatas` | passo a passo dos combos (base; Master+Ascension, Dakmor+Gitrog, Mindskinner+Konrad) | usado | idem |
| `spellbook_candidatas` | 121 candidatas adicionadas (sem cortar) | usado | `candidatas-pos-eoe.md` §8 |
| `spellbook_swaps` | 12 cenários de troca (S1–S6, T2a–e, "PACOTE 1") + 2 controles de corte | usado; o cenário **"PACOTE 1" está SUPERADO** pelo pacote final (trocou Negate por Mutational Advantage e não tinha a troca de terreno) | §0, §8 |
| `spellbook_pacote_final` | **pacote de 6 trocas** e variante com Mutational Advantage | usado (final) | §0, §8 |
| `spellbook_quase_pool` | combos "falta 1 carta" cuja carta está no pool | usado | §8 (armadilhas de Bracket) |
| `precos_todas_impressoes`, `pre_lancamento_cartas`, `sets_nao_lancados_consulta` | preços e pré-lançamento | usado | §3–§6, §10 |

`resumos/`: `auditoria_mecanica.txt`, `auditoria_pacote_final.txt`, `motores_por_script.txt`, `numeros_por_script.txt`, `condicoes_por_script.txt`, `candidatas_por_etiqueta.md`, `spellbook_resumo.md`, `rulings_principais.md`,
`lista_pacote_final_proposta.md` (**proposta, não é a lista do usuário**), e `log_spellbook_*.txt` (saída de tela dos lotes; **não** são derivados do bruto).
Lote superado: o cenário "PACOTE 1 (S1..S6)" de `spellbook_swaps` (mantido e marcado, não apagado). Inválido: nenhum.

## Verificação de reprodutibilidade (feita antes de declarar arquivado)

`bash verificar_reproducao.sh` em 2026-10-05: **9 de 9 `cmp` iguais**, refeitos **só** a partir dos `.json.xz`, de `../../lista.md` e do `scryfall-cache`:
`candidatas_indice.json`, `candidatas_por_etiqueta.md`, `auditoria_mecanica.txt`, `auditoria_pacote_final.txt`, `motores_por_script.txt`, `numeros_por_script.txt`, `condicoes_por_script.txt`, `spellbook_resumo.md`, `rulings_principais.md`.
Verificação não vácua: o índice tem 3.097 cartas, `rad` 2, `proliferate` 19, `mill` 95, Spellbook base 2 combos e controle positivo com 3.

**Não conferido:** (1) as respostas das APIs são de **2026-10-05**; refazer a consulta amanhã pode dar outro resultado (cartas novas, combos novos) — por isso o bruto está aqui;
(2) `log_spellbook_*.txt` e os JSON de `dados/precos…` vêm de rede; (3) o resumo das rulings é a leitura dos JSON, não uma nova consulta; (4) o `cache` depende do conteúdo do repositório nesta data.
