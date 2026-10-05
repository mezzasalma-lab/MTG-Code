# Protocolo de avaliação de cartas, simuladores e resultados (usuário mezzasalma)

Destilado operacional das Regras #1–#10 do `CLAUDE.md` do repositório `mezzasalma-lab/MTG-Code` (texto integral em
`references/CLAUDE-repositorio.md` desta skill) e das preferências que o usuário repetiu. **Em caso de dúvida, vale o texto integral.**
Atualizado em 2026-10-05 (Regra #10: varredura mecânica de erros do motor).

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
   SUBTIPO), `audit_fetch.py` (sacrifício, 1 de vida, busca por subtipo, thinning), `audit_terreno_nao_e_magia.py`, `audit_landfall.py` (entradas × chamadas de landfall), `colisao_nome.py` (estado por nome). Ler cada divergência à mão.
2. **Classes do motor:** mulligan ESCOLHE o fundo (CR 103.5); imposto do comandante no cast (CR 903.8); upkeep antes do draw; terreno virado jogado primeiro em T1/T2 quando não custa jogada (ensaio a seco + modo GHOST);
   fetch real (inclusive a devolvida do cemitério); "whenever a land enters" em TODO ponto de entrada (play_land, fetch, ramp, blink, saga).
3. **Determinismo:** os `driver.py` fixam `PYTHONHASHSEED=0` e NÃO enxergam dependência de hash; rodar `det_check.sh`/`det_wide2.sh` (3 hash seeds × 1.500 sementes × 2 modos) quando mexer em iteração de `set`/`dict` de strings.
4. **Verificação vazia é vácua:** conferir que contagens são > 0 (smoke de simulador baseado em dict contava 0 cartas); tabela publicada = função só do bruto (`driver.py sum` × re-execução); conferir `Traceback` no log, não o `rc`
   (`$(date)` no mesmo `echo` zera `$?`).
5. **Operação:** verificação completa re-simula o arquivo VIVO (não editar o simulador enquanto roda); commitar e enviar cada deck quando fecha (o contêiner pode reiniciar).
Não coberto (declarar na Regra #7): conjuração fora da mão, sacrifício × destroy, `_sick` agregados, fórmulas achatadas, choque que não deduz vida (Kutzil, Edgar), oponente real.

## 8. Erros que já cometi e o que fiz para não repetir (checklist rápido)

| erro | correção |
|---|---|
| citei o oráculo da Sisay de memória (errado) | buscar ao vivo antes de escrever qualquer coisa |
| doc antigo dizia "a lista não tem outlet de sacrifício" e eu reusei | refazer a varredura ao vivo; grepar `NENHUM\|nunca\|não tem` nos docs |
| regex por "each creature" perdeu o Damn (overload) | 2ª varredura por alvo e por modo alternativo |
| recomendei corte sem ver o combo registrado no `auditoria.md` | ler a documentação do deck ANTES de listar motores |
| métrica do simulador refletia convenção da IA (atacar com tudo) | Regra #5: linha deliberada, medir o teto |
| declarei "auditoria completa" e apareceram bugs | Regra #7: escopo verificado e não verificado |
| citei `goldfish-log.md` sem pasta e abriu o da Azula | caminho completo sempre |
| dados brutos só na pasta temporária | Regra #8: arquivar no repositório |
| mulligan devolvia o fundo por sorteio; terreno virado nunca jogado primeiro; fetch ficava como dual; gatilho de land enters só no `play_land` (14 de 18 decks) | Regra #10: varrer o MOTOR por script em todo simulador, não só as cartas |
| `driver.py` com `PYTHONHASHSEED=0` escondia dependência de hash (Thranduil: 14/1.500 e 36/1.500 sementes) | `det_check.sh` com 3 hash seeds antes de declarar o simulador determinístico |
| verificação "passou" com 0 cartas contadas / tabela em memória ≠ tabela dos brutos | número vazio ou zero é vácuo: conferir > 0 e comparar `sum` com a re-execução |
