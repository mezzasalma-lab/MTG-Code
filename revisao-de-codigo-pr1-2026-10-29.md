# Revisão de código do PR #1 (2026-10-29)

Pedido do usuário: *"Revise tudo e salve no GitHub e aqui tb"*. Escolhas dele: revisão de código do diff do PR #1; **corrigir o que achar e relatar**; commit e push na branch do PR (`claude/goldfish-simulator-vjg1ey`); relatório em arquivo na pasta do projeto (este).

O PR tem 289 commits, 3.826 arquivos e ~1.060 arquivos `.py` novos (431 mil linhas de `.py`, quase tudo scripts de resultados e cópias de simuladores). **Uma revisão linha a linha do PR inteiro não foi feita e não cabe numa passada.** O que foi feito está abaixo, com o intervalo exato que cada revisão leu.

## O que foi revisado

| revisão | alvo lido | método | achados | resultado |
|---|---|---|---|---|
| 1 | commit `667ed7f` (Tam, goldfish manual #6): testes, scripts de replay/orquestração, documentação, backup da skill | `code-review`, nível *high*. O alvo `1` foi lido como `HEAD~1..HEAD`, **só o último commit** | 8 | 1 erro de fato meu (turno extra do Oko), 2 testes fracos, 1 organização, 1 verificação fraca, 1 resíduo; 2 não eram defeito. Tudo corrigido em `868a95e` |
| 2 | `git diff 7639380..HEAD -- rat-king-verminister/ratking_goldfish_v1.py` (rodadas 4 e 5 do Rat King: +341/−70 linhas) | `code-review`, nível *high* | 10 | 2 defeitos corrigidos, 1 medição que achou outro defeito (correção testada e **rejeitada**), 1 guarda, 6 não eram defeito. Ver `rat-king-verminister/resultados-ab/2026-10-29-revisao-codigo-pr1/LEIAME.md` |

## Revisão 1: Tam, goldfish manual #6

| # | apontamento | verificação | decisão |
|---|---|---|---|
| 1 | O LEIAME/log dizem que o turno extra do Oko NÃO foi jogado e que o Dack Fayden "não tem fonte no log", mas o bloco T11 tem um 2º início de turno | Conferi no bruto (`goldfish_manual_6_bruto.json`): todo bloco T2–T11 abre com *desvirar tudo + `library → hand`* no índice 0; **só o T11 tem uma 2ª corrida de desvirar ≥ 5** (7 permanentes, eventos 54–60), seguida da compra do Dack (evento 63). Eu tinha lido *"só não usei o botão de passar turno"* ao contrário | **Corrigido** (LEIAME linhas 6 e 7, goldfish-log, checklist, regras, teste). **É inferência do log, não resposta dele: falta ele confirmar.** |
| 2 | O teste da dúvida 6 tinha uma asserção sem relação com a ordem e documentava a conclusão errada | Confirmado | Teste refeito: lê as corridas de desvirar do bruto; **controle de corte** (removendo os eventos 54–62 o teste falha) |
| 3 | O teste do Prismari (T8) só checava P/T estático | Confirmado | Refeito: remove o Lurker (`remove_permanent`) e confere que a ficha de Jace (L2) sobrevive; controle com a ficha em L0 |
| 4 | goldfish-log do Tam com seções fora de ordem (9, 11, 10) e a pasta nova sem link no topo (Regra #8, item 7) | Confirmado | §11 movido para depois do §10; link no topo |
| 5 | Regra #9: a skill foi atualizada sem `--para-backup` | Deliberado e documentado no README: a pasta viva da skill é mais antiga que o backup e o comando a copiaria por cima | **Mantido**; removi só as linhas em branco duplas. A skill da conta **continua não atualizada** |
| 6 | `pws_por_turno.py` com prefixo de id e turno fixos, e o T11 contado como um turno | O script é específico deste log (a docstring já dizia); o T11 tem 2 turnos | Nota na docstring (não muda a saída) |
| 7 | `verificar_reproducao.sh` comparava só a última linha dos testes | Confirmado | Agora também compara **uma linha por teste** (`lista_testes_manual6.py`); **13/13** saídas iguais |
| 8 | Chamada morta de `opp_all_colors` no teste do T3 | Confirmado | Removida |

## Revisão 2: Rat King, rodadas 4 e 5

Tabela completa dos 10 apontamentos, com a verificação de cada um, no `LEIAME.md` da pasta da rodada 6. Resumo:

- **Corrigidos (2):** `WIPE_UNTAPS_STAFF` (wipe meu não desvirava o Thornbite Staff; **latente**, 0 disparos em 20.000 partidas) e `FELL_MIRE_PROTECTED_IN_BOTTOM` (a MDFC contada como terreno no `should_keep` ia ao fundo no `choose_bottom`; muda 9 de 10.000 partidas).
- **Medido e rejeitado (1):** o revisor suspeitou de "sorvedouro de mana" no ensaio do terreno virado. A hipótese não apareceu, mas a medição achou que o mana gasto é **líquido do Dark Ritual**, o que esconde o desenvolvimento do T1 em **1,7%** das partidas. A correção que testei (desempatar por MV da mão + comandante) **piora o comandante no T2: −0,32 ± 0,11 pontos (N=10.000)**, então ficou desligada (`TAPPED_FIRST_TIEBREAK_DEV = False`) e o defeito, **sem correção**.
- **Guarda (1):** criatura fora de `CREATURE_TYPES`/`CREATURE_TOUGHNESS` agora impede o import.
- **Não eram defeito (6):** bloco duplicado do Mercenary, `wipe_held` com contagem, `WIPE_CAST_MAX_OWN_LOSS = 0` (política que o usuário escolheu), nome/duplicação do ensaio do Fell Mire, despacho repetido do `_wipe_effect_on`, e `rat_tokens_created_this_turn` (inalcançável: o wipe mata todas as fichas de Rat ou nenhuma).

Validação da rodada 6: bit-idêntico com as 3 chaves desligadas (20.000 × 2 modos), regressão 20.000 × 2 modos × 2 configurações com 0 exceções, A/B pareado 2.000 e 10.000 nos 2 modos (99,91% das partidas idênticas ao `antes`; comandante até T2 +0,0001 ± 0,0002), 8 testes dirigidos, determinismo com 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos (0 divergentes), scanner de ETB fantasma idêntico ao da rodada 5.

## O que NÃO foi revisado (Regra #7)

- Qualquer coisa fora dos dois alvos da tabela do topo. Em particular: os outros 17 simuladores modificados no PR, a rodada 3 e anteriores do `ratking_goldfish_v1.py`, o `tam_goldfish_v1.py` (5.841 linhas; a revisão 1 leu só o commit `667ed7f`, que não o alterou), ~1.060 `.py` de scripts e cópias, e os dados.
- **Não reexecutei** as verificações dos outros decks. Os 13 simuladores com a função `_tl_dry_run_mv` seguem sem medição do comandante até T2; a classe (l) (métrica líquida no ensaio) só vale onde o ensaio usa o mana líquido, hoje só o Rat King.
- A revisão automática acha o que está no diff que ela lê; não substitui as auditorias por classe da Regra #10, que não foram repetidas neste ciclo (exceto as citadas acima).

## Pergunta em aberto para o usuário

No Tam #6, o turno extra do Oko (`−12` do Gauntlet) foi jogado **à mão dentro do bloco T11**, sem apertar o botão de passar turno? É o que o log mostra (2º início de turno, com compra do Dack Fayden), mas só você pode confirmar.
