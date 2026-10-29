# Protocolo de avaliação de cartas, simuladores e resultados (usuário mezzasalma)

Destilado operacional das Regras #1–#10 do `CLAUDE.md` do repositório `mezzasalma-lab/MTG-Code` (texto integral em
`references/CLAUDE-repositorio.md` desta skill) e das preferências que o usuário repetiu. **Em caso de dúvida, vale o texto integral.**
Atualizado em 2026-10-22 (Regra #10: varredura mecânica de erros do motor; classes novas do Tam: contador como flag, ordem de pagamento).

## 0. Onde estão as coisas (repositório `mezzasalma-lab/MTG-Code`, branch de trabalho `claude/goldfish-simulator-vjg1ey`)

- Uma pasta por deck (`prismatic-bridge-wurbg/`, `azula-grixis/`, `ur-dragon-wurbg/`, …) com `lista.md`, `auditoria.md`, `checklist-oraculo.md`,
  `goldfish-log.md` e o simulador `*_goldfish_v1.py` (+ testes).
- `scryfall-cache/oracle-cache.json` (oráculo de toda carta mencionada), `rules-cache/comprehensive-rules.txt` (Comprehensive Rules),
  `references/` (regras permanentes e lições de processo), `<deck>/resultados-ab/` (dados brutos arquivados, Regra #8), `skills-backup/` (backup desta skill).
- **18 decks têm arquivos com o MESMO nome** (`goldfish-log.md`, `checklist-oraculo.md`…). **Sempre citar o caminho completo com a pasta do deck**,
  nunca só o nome do arquivo: citar "goldfish-log.md" solto abriu o log da Azula para o usuário (2026-09-30).
- Só commitar/enviar na branch de trabalho; não abrir Pull Request sem pedido; a branch de trabalho NÃO está na `main`.

## 1. Avaliar uma carta que o usuário propõe (incluir, cortar ou trocar) — Regras #4, #5

Nunca "essa carta é boa/forte" isolado. Na ordem:
1. **Oráculo ao vivo (Scryfall) e rulings** (`rulings_uri`) — nunca de memória (já errei o texto da Sisay de memória). Salvar no `oracle-cache.json`.
2. **Ler a documentação do deck antes de listar motores:** `auditoria.md`, `checklist-oraculo.md`, `goldfish-log.md`, com grep de "combo", "infinit", "loop" e do
   nome de cada carta envolvida (a que entra e cada candidata a sair).
3. **Commander Spellbook ANTES e DEPOIS** de cada troca (`POST https://backend.commanderspellbook.com/find-my-combos`, comandante + lista) com **controle positivo**
   (tirar uma carta que está em combos e ver a resposta mudar). Combo que some é custo; combo que aparece (inclusive tutor que monta combo existente) é ganho e pode mudar o Bracket.
   **A API ignora, sem erro, nome de carta que não reconhece** (achado de 2026-10-05, Mothman): resolva cada nome antes via `GET /cards/?q=<nome>` (2 faces: `Frente // Verso`), grave se foi reconhecido e rode também um
   **controle de corte** (tirar peça de combo da lista tem de fazê-lo sumir); sem isso, "nenhum combo novo" pode ser vácuo.
4. **Conferir se o simulador executa o combo.** Se não, o valor da peça no A/B é piso e isso é candidato a fix no simulador.
5. **Enumerar POR SCRIPT** (`type_line` + `oracle_text` ao vivo) as cartas da lista que satisfazem cada condição da carta (tipo de criatura, Treasure, "legendary", "artifact"…). Changeling/Kindred contam em
   toda zona. Depois da varredura por texto, rodar uma 2ª por **alvo** (`destroy target`, `damage to target`) e por **modo alternativo** (overload, kicker, escape): a regex de texto perde efeito escondido.
6. **Listar os motores reais do deck** e checar em quantos a carta entra; checar interação com cartas específicas (restrição de MV/tipo).
7. **Comparar com a alternativa real** (a que sai) pelo mesmo critério.
8. **Prioridade de evidência (Regra #5):** (1) oráculo + regras + linhas deliberadas de um jogador real; (2) motores e cartas do deck; (3) simulador só como APOIO. Se o simulador diz "não faz nada" só por uma
   convenção dele (sem oponente, ataca com tudo, sem bloqueio), isso é candidato a FIX no simulador, não corte de carta. Medir o teto da linha deliberada antes de reclamar que o simulador subestima.
9. **Nunca adicionar/cortar carta da lista por conta própria** — correção é só de implementação; troca de carta é decisão do usuário.

## 2. Implementar carta no simulador — Regras #1, #3, #6, #7

- **Toda habilidade de toda carta**, cláusula por cláusula (estático, ETB, morte, ativadas, custos alternativos, capítulos de saga, gatilhos "whenever"). Único critério válido para 📊 (não implementar):
  impossibilidade estrutural (estado de OPONENTE real). "Baixo valor" ou "raro" nunca. Justificativa "o arquivo não rastreia X" é suspeita se o dado existe no Scryfall.
- **Ler as rulings ANTES de escrever o código** (becomes, phase out, gains control, copy, substituição), listar no `checklist-oraculo.md` e conferir o código.
- **Conceitos compartilhados** (o que é "Urso", "criatura", cores, MV): auditar o conceito, não só a carta; grepar todos os call sites antes de mudar uma função central.
- **Timing de fase nomeado:** conferir ONDE em `play_turn`/`combat_step`/`end_step` a função é chamada; teste unitário isolado não pega isso, só um jogo completo.
- **Fichas:** ataca (e doença de invocação), gatilhos de entra/morre, morre no wipe, conta em todo "you control X".
- **Política de ordem dentro do main phase** (ex.: busca antes ou depois da mão): medir as DUAS ordens antes de concluir; expor como chave de política (`CAND_POLICY`) e registrar as duas medidas.
- **Toda chamada nova só quando a ação de fato aconteceu** (retorno inteiro > 0); uma chamada extra incondicional mudou a base sem a carta em campo e só a bit-identidade pegou.
- Instrumentar a **fonte** de cada evento (de onde vêm as mortes, as entradas em campo): foi assim que apareceu a Liliana −4 sacrificando a Sisay.

## 3. Rodar um A/B — método já validado

- **Pareado** (mesmas sementes em todas as variantes: padrão `3_000_000+i`, resiliência `6_000_000+i`), N ≥ 3.000, IC95% da diferença pareada; "empate/dentro do ruído" quando o IC inclui 0.
- Métricas limitadas por partida (1º ultimate, P(ult ≤ T8), vida ≤ 0, PW-turnos, P(dano ≥ 40/≥ 120)); nunca média de proxy sem teto.
- **Controles:** do lado do corte (carta que deve ficar no fundo do ranking, ex.: Doubling Season/Farseek) e do lado da entrada (PW inerte; corpo 2/2 lendário sem texto para criatura).
- **Condicional** (só partidas em que a carta entrou), **sensibilidade por chave de política** (uma por vez) e **por perfil de mesa**.
- **Validação antes de commitar:** testes dirigidos, lista atual **bit-idêntica** ao snapshot anterior, regressão de 20.000 partidas por modo com 0 exceções e 0 travamentos (alarme de 20 s), smoke test.
- **Reprodutibilidade:** guardar o script; não esperar por `pgrep -f`/`pkill -f` de nome de script (casa com o próprio shell): esperar por arquivo de sinal e matar por PID.
- Documentar a rodada em `<deck>/checklist-oraculo.md` (cláusula por cláusula) e `<deck>/goldfish-log.md` (números), com **correção explícita das premissas minhas que estavam erradas**.

## 4. Como reportar — Regra #7 e preferências do usuário

- **Palavras proibidas sobre auditoria de simulador:** "completo", "tudo revisado", "garantido", "100%". Sempre listar: classes varridas, método (grep, instrumentação, teste dirigido) e **o que NÃO foi verificado**.
- **Português do Brasil, veredito primeiro, sem elogios, sem perguntas quando existe um padrão razoável** (o usuário odeia responder e se repetir): decida, declare a suposição e siga.
- **Traduzir números em linguagem comum** quando pedir ("traduza"): "1 partida em cada 12", "2 partidas a mais em 100", e explicar "±", "pp" e "dentro do ruído". Não empilhar estatística.
- Separar sempre o **medido** do **raciocínio pelo deck**, e dizer o que o simulador não vê (a favor e contra a carta).
- Citar fonte oficial (Scryfall, Comprehensive Rules em `rules-cache/`, EDHREC, Commander Spellbook); nunca inventar.
- Dizer explicitamente **onde está o quê** (GitHub: repositório, branch, caminho completo; o que NÃO está na `main`).

## 5. Arquivar — Regra #8

Toda conclusão que depende de simulação, A/B, regressão, instrumentação ou API é arquivada no MESMO commit em `<deck>/resultados-ab/<data>-<tema>/`: dados brutos `.json.xz`, `LEIAME.md` (mapa arquivo → código → status → tabela e
comando que reproduz), `resumos/`, `orquestracao/`, `SHA256SUMS`, `descomprimir.sh`, verificação byte a byte de pelo menos as tabelas publicadas, link no topo do `goldfish-log.md`. Modelo:
`prismatic-bridge-wurbg/resultados-ab/2026-09-29-candidatas-e-sisay/`. Criar a pasta no início da rodada (a pasta temporária da sessão some).

## 6. Backup desta skill — Regra #9

Alterou esta skill (ou um espelho): `bash skills-backup/sincronizar-skill.sh` e commitar no mesmo commit (README em `skills-backup/`).

## 7. Simulador novo ou alterado — varredura mecânica de erros do MOTOR (Regra #10)

Auditoria carta-a-carta não pega erro de motor (a varredura de 2026-10-05 achou erro em 14 dos 18 decks e nenhum seria pego assim). Antes de declarar pronto:
1. **Scripts** de `varredura-2026-10-05/scripts/` (o `LEIAME.md` da pasta lista os falsos positivos já verificados): `audit_entrada.py` / `audit_entrada2.py` (terreno entra virado quando o oráculo manda; "unless you control…" por
   SUBTIPO), `audit_fetch.py` (sacrifício, 1 de vida, busca por subtipo, thinning), `audit_terreno_nao_e_magia.py`, `audit_landfall.py` (entradas × chamadas de landfall), `audit_landfall_ordem.py` (terreno jogado antes do payoff de landfall; hoje 0 candidatos), `colisao_nome.py` (estado por nome), `audit_tam_terrenos.py` (as de terreno para o simulador do Tam, que não tem `play_land`; 0 falhas), `audit_inicio_de_combate.py` (gatilho "at the beginning of combat" preso a `can_attack`; triagem, leitura à mão). Ler cada divergência à mão.
2. **Classes do motor:** mulligan ESCOLHE o fundo (CR 103.5); imposto do comandante no cast (CR 903.8); upkeep antes do draw; terreno virado jogado primeiro em T1/T2 quando não custa jogada (ensaio a seco + modo GHOST);
   fetch real (inclusive a devolvida do cemitério); "whenever a land enters" em TODO ponto de entrada (play_land, fetch, ramp, blink, saga).
   Ordem terreno × payoff de landfall: com um terreno por jogar, conjurar antes o payoff que o mana de agora já paga, só se um ensaio a seco do resto da fase pré-combate mostrar que o turno não perde nenhuma jogada (a fórmula "mana de agora + 1" falhou: não conta mana de landfall em campo nem 2º land drop; chave `LANDFALL_PAYOFF_FIRST` nos 6 simuladores com payoff: Mothman, Toph, Beorn, Thranduil, Maralen, Prismatic Bridge).
3. **Determinismo:** os `driver.py` fixam `PYTHONHASHSEED=0` e NÃO enxergam dependência de hash; rodar `det_check.sh`/`det_wide2.sh` (3 hash seeds × 1.500 sementes × 2 modos) quando mexer em iteração de `set`/`dict` de strings.
4. **Verificação vazia é vácua:** conferir que contagens são > 0 (smoke de simulador baseado em dict contava 0 cartas); tabela publicada = função só do bruto (`driver.py sum` × re-execução); conferir `Traceback` no log, não o `rc`
   (`$(date)` no mesmo `echo` zera `$?`).
5. **Operação:** verificação completa re-simula o arquivo VIVO (não editar o simulador enquanto roda); commitar e enviar cada deck quando fecha (o contêiner pode reiniciar).
Compra do 1º turno (2026-10-20): Commander multijogador não pula a compra; `audit_compra_t1.py` mede por execução a queda da biblioteca entre `turns=0` e `turns=1` (deve ser ≥ 1 em toda partida; hoje 20 de 20 COMPRA; o Mothman pulava e foi corrigido com `FIRST_TURN_SKIPS_DRAW`); grep de `on_play` não serve.

Duas classes novas (Tam, 2026-10-22; ambas no motor, não na carta): contador acumulado lido como flag (turnos extras da Ichormoon Gauntlet) e ordem de pagamento do mana (Bloom Tender / Faeburrow Elder e unidade irmã de fonte já tocada; `VIVID_LAST`, `SIBLING_FIRST`); a ordem de pagamento NÃO foi varrida nos outros simuladores com Bloom Tender (Hei Bai, Maralen, Prismatic Bridge, Thranduil, Tom Bombadil). Rodar o script commitado e salvar a saída antes de citar o resultado (`audit_tam_terrenos.py` foi commitado com `SyntaxError`). Terceira classe (Beorn, 2026-10-23): gatilho de fase nomeada preso a `can_attack`/doença de invocação (a doença só impede atacar e usar `{T}`, não um gatilho de início de combate); The Ozolith em 3 decks não foi lido à mão.

Classe (k) (Rat King, 2026-10-28): **ensaio a seco que mede só o que sai da MÃO ignora o comandante** (zona de comando). `_tl_dry_run_mv` do "terreno virado primeiro" fez o Rat King perder o T2 (comandante até T2 87,2% → 97,9% com `TAPPED_FIRST_COUNTS_MANA`); 13 simuladores têm a mesma função e não foram medidos (Azula, Bumbleflower, Captain Storm, Edgar, Hei Bai, Kutzil, Maralen, Nekusar, Prismatic Bridge, Thranduil, Toph, Ulalek, Ur-Dragon; Megatron, Mothman, Tam e Vihaan têm a chave com outra função). Medir `commander_cast_turn__ate_T2` com e sem a política; o `abgen` agora gera o indicador de T2.

Não coberto (declarar na Regra #7): magia que põe terreno em campo antes do payoff de landfall, conjuração fora da mão, sacrifício × destroy, `_sick` agregados, fórmulas achatadas, choque que não deduz vida (Kutzil, Edgar), oponente real.

## 8. Erros que já cometi e o que fiz para não repetir (checklist rápido)

| erro | correção |
|---|---|
| citei o oráculo da Sisay de memória (errado) | buscar ao vivo antes de escrever qualquer coisa |
| doc antigo dizia "a lista não tem outlet de sacrifício" e eu reusei | refazer a varredura ao vivo; grepar `NENHUM\|nunca\|não tem` nos docs |
| regex por "each creature" perdeu o Damn (overload) | 2ª varredura por alvo e por modo alternativo |
| recomendei corte sem ver o combo registrado no `auditoria.md` | ler a documentação do deck ANTES de listar motores |
| li o comentário do código ("whenever Beorn attacks … ilegal no turno do cast") em vez do oráculo ("at the beginning of combat") e deixei o gate de ataque por semanas | comparar a CLÁUSULA do oráculo com a condição do `if`, não com o comentário; ler o gatilho de fase antes de aceitar `can_attack` |
| li as rulings do Ichormoon Gauntlet / Bloom Tender só no fechamento da rodada (Regra #3 manda ler ANTES de escrever o código) e citei uma regra de turno extra de memória no rascunho | baixar `rulings_uri` antes de implementar; citar regra só com fonte lida |
| cheguei a escrever "4 planeswalkers diferentes" no LEIAME dos turnos extras do #5 sem conferir o log (era Jace, Domri, Vronos e Jace de novo, 2 no mesmo turno) | reler o log antes de afirmar quem fez o quê |
| li a resposta do usuário *"só não usei o botão de passar turno"* como "o turno extra não foi jogado" e dei o Dack Fayden como "sem fonte no log"; o bruto tinha um 2º início de turno (desvirar + comprar) dentro do bloco | toda resposta que diz o que o usuário NÃO fez se confere contra o bruto antes de virar texto; procurar a assinatura de turno (desvirar tudo + `library → hand`) por bloco; teste com controle de corte |
| aceitei o rótulo do revisor ("sorvedouro de mana") sem medir, e a correção que EU propus para o defeito real (desempate por MV da mão + comandante) piorou o comandante no T2 | apontamento de revisor é hipótese: ler o código, medir o defeito, medir a correção e rejeitar com número quando piora; dizer quando a correção é latente (0 disparos) |
| rodei `det_check.sh` da raiz e ele deu "0 divergentes" (na verdade, `JSONDecodeError` em 0,06 s) | ler a saída inteira; rodar de dentro de `varredura-2026-10-05/scripts/`; resultado em menos de 1 s é suspeito |
| métrica do simulador refletia convenção da IA (atacar com tudo) | Regra #5: linha deliberada, medir o teto |
| declarei "auditoria completa" e apareceram bugs | Regra #7: escopo verificado e não verificado |
| citei `goldfish-log.md` sem pasta e abriu o da Azula | caminho completo sempre |
| dados brutos só na pasta temporária | Regra #8: arquivar no repositório |
| mulligan devolvia o fundo por sorteio; terreno virado nunca jogado primeiro; fetch ficava como dual; gatilho de land enters só no `play_land` (14 de 18 decks) | Regra #10: varrer o MOTOR por script em todo simulador, não só as cartas |
| `driver.py` com `PYTHONHASHSEED=0` escondia dependência de hash (Thranduil: 14/1.500 e 36/1.500 sementes) | `det_check.sh` com 3 hash seeds antes de declarar o simulador determinístico |
| verificação "passou" com 0 cartas contadas / tabela em memória ≠ tabela dos brutos | número vazio ou zero é vácuo: conferir > 0 e comparar `sum` com a re-execução |
| conceito de tipo/cor "N/A" conferido só nas cartas impressas (Thornbite Staff × Mercenary de changeling = Shaman; ficha de Rat preta não disparava Ayara; Treasure nunca mana) | enumerar por script os satisfazedores INCLUINDO toda ficha que a lista cria (`enumera_condicoes.py`) antes de declarar N/A |
| ETB/gatilho com comentário "real e rastreado" e nenhum efeito (Gray Merchant, Emeritus "enters prepared", extort, dreno do Ninja Teen); redução de custo abaixo da mana colorida; gatilho de conjuração 2×; sneak fora do declare blockers | `audit_etb_sem_efeito.py` (executa a carta e mede a mudança de estado) + rulings lidos antes do código |
| combo do Commander Spellbook que o simulador não executa (Marrow-Gnawer + Thornbite Staff; Ayara + Plague of Vermin no Rat King); 38 de 47 decks sem registro de Spellbook | rodar o Spellbook com controles em TODO deck, conferir se o simulador executa o combo (Regra #4, adendo, item 3) e calcular a probabilidade por turno (regra 7) |
| variantes `so_*` do A/B herdando as chaves ligadas do arquivo (todas iguais a `depois`) | cada variante lista as chaves todas; conferir que as variantes diferem entre si e do `antes` |
| ensaio a seco do "terreno virado primeiro" medindo só o MV que sai da MÃO: ignorava o comandante (zona de comando); Rat King perdia o T2 (comandante até T2 87,2% → 97,9% com a correção); 13 simuladores têm a mesma função e não foram medidos | medir o comandante até T2 com e sem a política (o A/B precisa do indicador `__ate_T2`); o ensaio mede o mana gasto no turno, não só o que sai da mão |
| teste "ghost" vácuo: as duas pontas com piso de vida 99, então o ensaio a seco nunca rodava (0 diferenças que não provavam nada) | contar quantas vezes o ensaio executou na configuração ghost (`ghost_vacuidade.py`: 642 execuções vs 0) antes de citar o 0 |
| comentário de código dizendo "CR 119.4: só se paga a vida que se tem" para uma perda de vida que no oráculo é EFEITO ("You lose N life"), não custo | ler a frase do oráculo ("pay" × "lose") antes de citar regra; o que a regra permite e eu não faço é política minha e se declara |
| Spellbook rodado nos 46 decks (2026-10-28), mas sem conferir se cada simulador executa os combos achados (Toph 29, Prismatic Bridge 12, Maralen 9, Ulalek 5...) | próximo passo da Regra #4, adendo, item 3, deck a deck; não está feito |
| política "só conjura o wipe se a perda própria for <= N" comparando só as MORTES: o Swarmyard deixava de ser conjurado quando matava qualquer criatura minha e perdia os 2 Esquilos que ele mesmo cria (−0,114 Esquilos por partida) | medir a perda LÍQUIDA (mortes menos corpos criados pela própria carta) e deixar as duas versões como variantes do A/B |
| `verificar_reproducao --tudo` com o `cmp` apontando para um arquivo de saída que nunca foi gravado (`testes_dirigidos.txt`): 18/19 | gravar a saída de cada teste ANTES da verificação completa; guardar a 1ª execução marcada e refazer |
| tratei a resposta do usuário ("deve ter sido por ativação de PW com custo 0 pelo Ichormoon, ou pelo Flux Channeler") como explicação do T9 sem conferir quando essas cartas entram (Gauntlet no T10, Flux Channeler no T11) | conferir a resposta contra o log antes de aceitar; se não cabe, dizer que não cabe |
