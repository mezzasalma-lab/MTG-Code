# 2026-10-10 — Mothman: 1 Swamp → Underground Sea (aplicado)

Pedido do usuário (2026-10-10), depois de eu medir 12 candidatos a sair pelo Underground Sea sem tirar o Bojuka Bog: *"Troca o Swamp pelo Underground Sea"*. **Lista APLICADA** em `lista.md` e no `DECKLIST_TEXT` do simulador, trocada NO LUGAR: a linha `3 Swamp` virou `1 Underground Sea` + `2 Swamp` na mesma posição (a `SWAPS` em lugar acha a 1ª cópia de `Swamp`, então a biblioteca é a mesma do A/B). A lista anterior está em `../../lista-anterior-2026-10-10.md`.

**Os dados desta troca já estavam medidos e arquivados** na pasta irma `../2026-10-10-underground-sea-sem-bojuka/` (variante `u3_swamp`, N = 10.000 × 2 modos, sementes 3.000.000+i, simulador congelado = o vivo de antes da troca). Esta pasta guarda só o que a APLICAÇÃO precisou: bit-identidade da lista, regressão e determinismo do simulador vivo, o Spellbook antes/depois da lista exata e a nova linha de base derivada do bruto da pasta irma.

## Conclusão (medido × raciocinado)

1. **O ganho** (`resumos/base_nova.md`; nova / anterior / diferença pareada ± IC95%; padrão | resiliência): comandante conjurado até T4 **66,17% / 65,44% / +0,73 ± 0,20 \*** | **60,87% / 60,12% / +0,75 ± 0,21 \***; até T5 +0,65 ± 0,18 \* | +0,67 ± 0,19 \*; mesa limpa até T8 **60,31% / 59,57% / +0,74 ± 0,36 \*** | 28,19% / 27,97% / +0,22 ± 0,34 (ruído); T10 +0,38 \* | +0,43 \*; 1º oponente fora até T6 +0,62 \* | +0,53 \*; deck-out −0,04 | −0,08 (sem efeito); vida mínima +0,23 \* | +0,24 \* (e 0,04 fetch quebrada a menos por partida, `../2026-10-10-underground-sea-sem-bojuka/resumos/tabela_u.md`). É o esperado: o Sea é um Swamp que também dá `{U}` e nunca entra virado.
2. **Nova linha de base** (padrão / resiliência): comandante até T4 **66,2% / 60,9%**, até T5 79,0% / 73,2%; mesa limpa até T7 19,2% / 7,5%, **T8 60,3% / 28,2%**, T10 89,3% / 62,9%; 1º oponente fora até T6 45,9% / 27,9%; deck-out 2,62% / 1,44%. O simulador vivo com `SWAPS=()` é a lista aplicada (bit-idêntico ao ANTES + u3 `no lugar`: 20.000/20.000, `resumos/bitident_lista.txt`).
3. **Fontes efetivas por cor** (`../2026-10-10-underground-sea-sem-bojuka/resumos/fontes_por_cor.md`): B 16 / G 19 / **U 17** (eram 16 / 19 / 16). Terrenos: 36, dos quais 2 Swamp, 5 Forest, 4 Island e 1 Underground Sea.
4. **O que se perde:** o Swamp era terreno **básico** e o Underground Sea não é (rulings de 2008-10-01: "tem os tipos básicos mas não é básico"); isso importa contra Wasteland / Blood Moon / Back to Basics no pod, que o simulador **não modela**. Prismatic Vista passa a ter 2 Swamps como alvo (5 Forest, 4 Island); Polluted Delta e Verdant Catacombs buscam o próprio Sea (tipo Swamp) e a Misty Rainforest também (tipo Island).
5. **Spellbook** (`dados/spellbook_viva.json`, `resumos/log_spellbook_viva.txt`): 91 nomes resolvidos (não reconhecidos: nenhum), a lista viva == a anterior com a troca (multiconjunto de nomes); antes 2 combos, depois 2 combos: **0 novos, 0 perdidos, 0 "quase" criados ou derrubados**. Controle positivo (Thassa's Oracle + Demonic Consultation aparece) e de corte (sem o Mindcrank some Ascension + Mindcrank) ok. O Underground Sea não é Game Changer (Scryfall ao vivo); o Bracket não muda.

## O que mudou no simulador

**Nenhuma regra nova.** Só a lista: `DECKLIST_TEXT` (a linha `3 Swamp` → `1 Underground Sea` + `2 Swamp`) e `lista.md`. O Underground Sea (`add("Underground Sea", …, produces={"U","B"}, land_types={"Island","Swamp"})`, sem `etb_tapped`, sem a etiqueta `basic`) já existia desde `../2026-10-09-terrenos-proxy`. Teste novo `lista_viva_tem_underground_sea_no_lugar_de_um_swamp_e_ele_conta_como_swamp_e_island` (**207/207** testes): a lista viva tem 1 Sea e 2 Swamp, o Sea produz U/B desvirado com os dois tipos e **não** é básico (a Vista só acha Forest / Island / Swamp), e a troca de volta por `SWAPS` restaura os 3 Swamps.

## Escopo verificado e NÃO verificado (Regra #7)

**Verificado:** a biblioteca viva == a do A/B (bit-identidade em 20.000 comparações); o conceito "terreno básico / tipo de terreno" nas cartas da lista que o leem (Prismatic Vista, Nature's Lore, Three Visits, Shifting Woodland, Misty Rainforest, Polluted Delta, Verdant Catacombs: já varridos por script em `../2026-10-09-terrenos-proxy`; o teste novo trava o caso da Vista).
**NÃO verificado:** Wasteland / Blood Moon / Back to Basics contra o Sea (estado de oponente, estrutural); uma só família de sementes; a escolha do Swamp (e não do Island) como terreno a trocar foi medida (u3 +0,73 contra u4 Island +0,51 no T4) mas a diferença direta entre os dois fica no ruído (+0,22 ± 0,27, `../2026-10-10-underground-sea-sem-bojuka/resumos/pares_diretos.md`).

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| testes dirigidos | **207/207** (1 novo) | `../../testes/testes_dirigidos.py` |
| smoke (99 cartas, 91 distintas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos sem exceção) | ok | `resumos/smoke_vivo.txt` |
| bit-identidade: vivo `SWAPS=()` == ANTES congelado + u3 `no lugar` | 20.000/20.000 (4 fatias × 2.500 sementes × 2 modos, sementes 9.500.000+) | `resumos/bitident_lista.txt` |
| regressão 20.000 × 2 modos, sementes 5.000.000+i, simulador VIVO | 0 exceções, 0 carta acima do baralho, 0 contador negativo | `resumos/regressao_vivo_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo (vivo; vivo com `COMMANDER_REMOVAL_SHARE=0.5`) | 0 divergências nos 2 casos | `resumos/determinismo.txt` |
| reprodutibilidade (`orquestracao/verificar_reproducao.sh`) | **1/1**: `base_nova.md` refeita só do bruto da pasta irma, igual com `cmp` | `resumos/verificacao_reproducao.txt` |

(A reprodutibilidade do próprio A/B — as tabelas, a replicação cruzada 6/6 e a re-simulação 8/8 — está na pasta irma, `resumos/verificacao_reproducao.txt` de lá.)

## Arquivos

| arquivo | o que é |
|---|---|
| `codigo/mothman_goldfish_v1_ANTES.py` | o simulador vivo de antes da troca (`cmp` igual à cópia congelada da pasta irma) |
| `orquestracao/bitident_lista.py`, `lanca_validacao.sh`, `config_vivo.json`, `base_nova.py`, `csb_viva.py`, `csb_stefano.py`, `driver_mm.py`, `abgen.py`, `verificar_reproducao.sh` | os scripts desta validação |
| `dados/spellbook_viva.json` | Commander Spellbook da lista exata (antes × depois) |
| `resumos/` | saídas de cada script |

## Como refazer

```
cd orquestracao
python3 base_nova.py | cmp - ../resumos/base_nova.md
bash verificar_reproducao.sh
python3 bitident_lista.py 2500 9500000        # uma fatia da bit-identidade (PYTHONHASHSEED=0)
sha256sum -c ../SHA256SUMS
```
