# 2026-10-19 — Registro do deck Tam, the Possibility (WUBRG): lista, auditoria estática e dados brutos

Pedido do usuário (2026-10-19): *"Fiz um deck novo: … As cartas marcadas Sideboard são do Sideboard, obviamente! Registra ele e não faça o simulador ainda"*. **Feito:** lista registrada, 113/113 nomes conferidos no Scryfall, auditoria estática (`../../auditoria.md`), oráculo das 27 cartas que faltavam gravado em `scryfall-cache/oracle-cache.json`. **Não feito (pedido do usuário): o simulador.**

## O que foi gerado e de onde vem

| arquivo | o que é |
|---|---|
| `../../lista-original-usuario.txt` (e `dados/lista_original_usuario.txt`) | a lista do usuário, **literal** (export do Archidekt, 113 linhas) |
| `../../lista.md` | 1 comandante + 99 do deck por categoria (as do usuário) + 13 de sideboard em seção própria; nomes reais |
| `../../nomes-de-capa.md` | resultado da conferência por set + nº de colecionador: 113/113, **nenhum nome de capa diferente** (Regra #2) |
| `../../auditoria.md` | a auditoria estática (checklist de `commander-rules.md#analise`, combos com probabilidade, EDHREC, pontos de atenção, o que não foi feito) |
| `resumos/analise_estatica.md` | as tabelas completas por trás da auditoria (composição, curva, planeswalkers e tipos, base de mana por terreno, EDHREC, combos, varreduras) |

## Dados brutos e como refazer (Regra #8)

| arquivo (`dados/`) | o que é | usado em |
|---|---|---|
| `resolvido.json.xz` | resposta bruta do Scryfall (`POST /cards/collection` por `{set, collector_number}`) das 113 linhas: 113 resolvidas por set + número, 0 por fallback de nome | `lista.md`, `nomes-de-capa.md`, `analise_estatica.md` |
| `edhrec_tam.json.xz` | `json.edhrec.com/pages/commanders/tam-the-possibility.json` de 2026-10-19 (6.931 decks) | `analise_estatica.md` §5 |
| `spellbook_tam.json` | Commander Spellbook do deck exato: 116 nomes resolvidos (0 não reconhecidos), 2 combos, 92 "quase", controle positivo e de corte ok | `analise_estatica.md` §6, `auditoria.md` §5 |
| `spellbook_combos_detalhe.json` | variantes completas (passo-a-passo e pré-requisitos) dos 2 combos | idem |
| `lista_original_usuario.txt` | a lista literal | `orquestracao/resolve.py` |

Scripts em `orquestracao/`: `resolve.py` (Scryfall), `csb_tam.py` (Spellbook, com resolução de nomes, controle positivo e de corte), `analise_estatica.py` (lê só os dados arquivados), `indice_dados.py`, `verificar_reproducao.sh`. Cada script que consulta API grava o bruto em `dados/`; **só `analise_estatica.md` e `indice_dados.md` se refazem offline** (`cmp`); `resolve.py`, `csb_tam.py` e o snapshot do EDHREC dependem de API ao vivo e **não são reproduzíveis byte a byte** (o bruto está arquivado).

```
bash descomprimir.sh                              # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 analise_estatica.py | cmp - ../resumos/analise_estatica.md
bash verificar_reproducao.sh                      # 3 comparações: análise, índice e lista.md x Scryfall
sha256sum -c ../SHA256SUMS
```

**Verificação feita antes de declarar arquivado:** `verificar_reproducao.sh` = 3/3 iguais (`resumos/verificacao_reproducao.txt`).

## Incidentes

- A primeira versão da análise contava 0 cartas "empower Jace" (a regex comparava `"empower Jace"` com o texto em minúsculas) e classificou a Starting Town como "sempre virada", e os terrenos lentos e a Spire Garden como mono-cor; corrigidos antes de gravar a auditoria (a saída de 0 cartas foi o sinal de que era erro, não resultado: Regra #10, item 4).
- O primeiro Spellbook falhou por caminho relativo errado; refeito (`resumos/log_spellbook_tam.txt` é o da execução válida).
