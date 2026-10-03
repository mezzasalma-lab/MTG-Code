# Resultados brutos — Partida manual #1 do Vihaan, 8 turnos (2026-10-03)

Arquivo de referência **permanente e auditável** do que sustenta a análise da partida manual do Vihaan, Goldwaker. A conclusão e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Partida manual #1 do Vihaan …") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"Analise esse Goldfish do Vihaan: Assumi algumas mortes em combate para gerar tesouros com o Mahadi, e um oponente fez 2 spells com Lotho e Tax em campo, gerando 2 tesouros fora do meu turno."* + o log JSON do Archidekt playtester.

> **Atualização (mesmo dia):** as 4 lacunas do simulador citadas aqui foram corrigidas em [`../2026-10-03-fora-da-mao/`](../2026-10-03-fora-da-mao/LEIAME.md). Os resumos desta pasta são do simulador **antes** (snapshot `c04840d` em `codigo/`) e continuam reproduzíveis.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (seção mais nova no topo) |
| ver cada tabela pronta | `resumos/` (um `.txt` por saída; mapa abaixo) |
| refazer as saídas a partir do log e do código arquivados | `bash orquestracao/verificar_reproducao.sh` (compara com `cmp`) |
| abrir o log em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta; o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## Respostas do usuário às perguntas da análise (2026-10-03, mensagem seguinte; transcritas sem reescrever)

> *"Eu assumi 3 mortes no T6, e o primeiro ataque o Reaver Cleaver fez 2 de dano no player. O Eldest Reborn me fez sacrificar o Zulaport. Esqueci o Descarte. Magda, Aya e Path foram descartadas pro Wheel of Fortune."*
> *"Além disso quando castei o Dictate eu usei tesouros já criaturas para ativar o Machado mais vezes!"*

Como foram lidas (a leitura é minha, não do usuário): **"Machado" = Mahadi** (autocorretor; "Machado" não é carta da lista, e sacrificar Treasures que já são criaturas só "ativa mais vezes" o Mahadi, que cria 1 Treasure por criatura morta no turno; se o usuário quis dizer o Reaver Cleaver, a leitura muda). **"Esqueci o Descarte" = o capítulo II do Eldest Reborn não foi registrado.** **"Wheel of Fortune"** das três cartas: li como um **2º Wheel depois do T8** (o Wheel do T4 é anterior à compra de Magda/Aya/Path, que vieram dele).
**Efeito no log:** (1) T6: as 3 mortes assumidas dão 3 pelo Mahadi e o Cleaver deu 2: com o Pact Boon da Sevinne's e o ataque da Storm são **7 esperados × 6 linhas "criada"**; (2) T8: os 7 toques de Treasure **não eram atacantes marcados** (premissa errada do `ledger_mana.py`, que vale para T5–T7 onde o Treasure virado reaparece desvirado no turno seguinte): eram **Treasures já criaturas sacrificados para pagar o Dictate**, cada um uma criatura morta para o Mahadi.

## Como ler o log (premissas, a conferir com o usuário)

Formato: lista de 8 turnos; cada turno = registros `{name, id, tapped, token, counters, fromZone, toZone, zone}`. As primeiras linhas de cada turno são as **desvirações** (untap) de quem estava virado; depois vêm as ações em ordem de registro. O log só gera linha quando o **estado muda**:
- ficha apagada não gera linha; ficha que termina o turno **virada** e não tem linha de untap no turno seguinte **sumiu** (sacrificada, morta ou apagada); ficha que termina **desvirada** sem linhas depois é indeterminada (tratada como viva);
- linhas com `toZone = opponentsCards` são marcadores de ação de oponente adicionados pelo usuário (Pentavite T3, Wheel of Fortune T4, The Eldest Reborn T6);
- Equip, vida, e a ordem exata dos gatilhos dentro do turno **não** são registrados (a Prosper do T6 aparece depois do Eldest Reborn do oponente, então a ordem das linhas nem sempre é cronológica).

## Mapa: arquivo → o que é → código → status → onde é usado

| arquivo | o que é | código | status | usado em |
|---|---|---|---|---|
| `dados/partida.json.xz` | o log da partida (8 turnos, 183 registros), extraído por script da mensagem do usuário (sem redigitar) | `orquestracao/extrair_json_da_conversa.py` | usado | todos os resumos |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo + **70 rulings** de 29 cartas do log, lidos ao vivo no Scryfall em 2026-10-03 | `orquestracao/oraculo_com_rulings.py` (rede) | **usado** | `ledger_mana.py`, log, checklist |
| `dados/oraculo_ao_vivo.json` | 1ª consulta (30 cartas, **sem rulings**) | — | **SUPERADO** (guardado, não apagado) | substituído pelo de cima |
| `codigo/vihaan_goldfish_v1_c04840d.py` | simulador do Vihaan como estava no commit `c04840d` (antes das correções de "fora da mão") | `git show c04840d:vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` | referência | `comparacao_simulador.py`, `lacunas_simulador_c04840d.py` |
| `resumos/sequencia_bruta.txt` | a sequência bruta do log, turno a turno, com a leitura de cada registro | `sequencia_bruta.py` | usado | log §1 |
| `resumos/ledger_treasures.txt` | cada Treasure por id: criada/virada/desvirada e o destino | `ledger_treasures.py` | usado | log §2 |
| `resumos/ledger_mana.txt` | conta de mana por turno (fontes líquidas × custo das magias; Treasures que sobrevivem × somem) | `ledger_mana.py` | usado | log §1–2 |
| `resumos/comparacao_simulador_padrao.txt` / `_resiliencia.txt` | partida × simulador (N=10.000, sementes 3.000.000+i): Treasures acumulados T5–T8, por fonte, terrenos no pool de impulso, comandante ≤T3, mana T2–T4 | `comparacao_simulador.py` (usa o snapshot de código) | usado | log §4 |
| `resumos/atacantes_vs_criacao.txt` | por id: nenhum Treasure virado (atacante marcado) foi criado depois do primeiro toque de Treasure do turno (CR 611.2c) | `atacantes_vs_criacao.py` | usado | checklist: Regra #7 |
| `resumos/lacunas_simulador_c04840d.txt` | testes diretos das 4 lacunas do simulador (terreno do exílio, mágica do exílio, contagem de "spell cast"/Lotho, +1/+0 da Storm) | `lacunas_simulador_c04840d.py` | usado | log §4 |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh` | verificação | — |

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh` → ver `resumos/verificacao_reproducao.txt`: refaz as 7 saídas e compara com `cmp`. `sha256sum -c SHA256SUMS` passa.
**Não refeito por `cmp`:** `oraculo_com_rulings.py` (precisa de rede; a resposta bruta do Scryfall está guardada) e `extrair_json_da_conversa.py` (lê a transcrição da sessão, que não está no repositório; o log extraído está em `dados/partida.json.xz`).

## O que NÃO foi verificado (Regra #7)

- O que o log não registra: equips, vida, ordem real dos gatilhos; a atribuição exata de cada Treasure de T6/T7/T8 (depende das respostas do usuário, perguntas listadas no log §3).
- Não avaliei se as escolhas de jogo foram boas (exigiria os motores do deck e o Commander Spellbook, Regra #4). Nenhuma carta foi cortada ou adicionada.
- Simulador: só as funções citadas no log (`play_from_impulse`, `play_land`, `cast_card`, `try_sevinne_flashback`, `do_cascade`, Storm/Cleaver, Lotho/Tax/Mahadi) foram lidas nesta análise.
