# Varredura de 2026-10-05 no Beorn — nenhuma correção de código

Pedido do usuário (2026-10-05): *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*.

Esta pasta existe só pra registrar **por que o "terreno virado primeiro em T1/T2" não se aplica** ao Beorn e apontar as varreduras que cobrem o deck. `beorn_goldfish_v1.py` **não foi alterado**.

| arquivo | o que é | como reproduzir |
|---|---|---|
| `resumos/terrenos_que_entram_virados.txt` | terrenos de `lista.md` cujo oráculo (cache `scryfall-cache/oracle-cache.json`) diz que podem entrar virados: só Bala Ged Recovery // Bala Ged Sanctuary (MDFC; a face de terreno custa a magia) | script embutido no comando de arquivamento (regex `enters( the battlefield)? tapped\|If you don't, it enters tapped` sobre `oracle_text` dos terrenos da lista) |

Outras varreduras que incluem o Beorn (0 achados): `../../../varredura-2026-10-05/` — entrada de terrenos (`audit_entrada_ANTES.txt`), determinismo entre processos (`determinismo_1500_sementes_estado_final.txt`), jogar terreno ≠ magia (`audit_terreno_nao_e_magia_ANTES.txt`).

**Escopo:** a lista tem 1 terreno que entra virado e ele é MDFC; **não** é uma auditoria do resto do arquivo (Regra #7).
