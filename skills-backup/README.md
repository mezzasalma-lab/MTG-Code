# Backup versionado da skill `mtg-commander`

Cópia de segurança da skill **`mtg-commander`** (especialista em Commander/EDH, com as regras permanentes do usuário e o protocolo de avaliação de cartas/simuladores).
Criada em **2026-09-30**; atualizada em **2026-10-05** (Regra #10), em **2026-10-07** (ordem terreno × payoff de landfall) em **2026-10-22** (classes novas do Tam) e em **2026-10-23** (gatilho de fase preso a `can_attack`). Regra de manutenção: Regra #9 do `CLAUDE.md` (raiz do repositório).

> **Este backup é a cópia durável.** A pasta viva da skill (`/root/.claude/skills/synced/<id>/mtg-commander/`) é sincronizada com a conta do usuário, mas
> **alterações feitas nela durante uma sessão não são gravadas na conta** e o próximo sync pode sobrescrevê-las. Para a skill da conta refletir a versão
> atualizada, é preciso reinstalá-la a partir daqui (abaixo).

## O que tem aqui

| caminho | o que é |
|---|---|
| `mtg-commander/SKILL.md` | a skill (frontmatter `name`/`description` + fluxo de trabalho, Scryfall, brackets, checklist de análise, tom) |
| `mtg-commander/references/commander-rules.md`, `archetypes.md`, `scryfall-api.md` | referências originais da skill (inalteradas) |
| `mtg-commander/references/user-standing-rules.md` | **regras permanentes do usuário** (21 seções; cópia idêntica de `references/user-standing-rules.md` do repositório) |
| `mtg-commander/references/protocolo-de-avaliacao.md` | **novo:** protocolo de avaliação de cartas, simuladores, A/B e relatório (destilado das Regras #1–#10) e checklist de erros já cometidos |
| `mtg-commander/references/goldfish-sim-card-rules.md`, `pod-simulator-design.md` | lições de processo dos simuladores e design do motor de mesa (cópias idênticas de `references/` do repositório) |
| `mtg-commander/references/CLAUDE-repositorio.md` | texto integral das regras do repositório (cópia idêntica do `CLAUDE.md` da raiz, Regras #1–#10) |
| `mtg-commander.zip` | **pacote pronto para enviar à conta** (gerado do backup em 2026-10-05, já com a Regra #10; pasta `mtg-commander/` como raiz do zip) |
| `sincronizar-skill.sh` | mantém skill viva, backup e espelhos iguais (modos abaixo) |
| `SHA256SUMS` | hashes de todos os arquivos de `mtg-commander/` (`cd skills-backup && sha256sum -c SHA256SUMS`) |

## O que mudou nesta atualização (2026-09-30)

Estado anterior da skill (2026-09-26): `SKILL.md` + 3 referências. Agora:
- `SKILL.md`: passa a mandar ler as regras permanentes e o protocolo antes de responder; aponta o repositório `mezzasalma-lab/MTG-Code`, a regra de **citar sempre o caminho completo do arquivo com a
  pasta do deck** e o backup; o Modo A deixa de exigir perguntas que já têm resposta (o usuário odeia se repetir); o "Tom e abordagem" ganha as preferências aprendidas (português, veredito primeiro, sem
  elogios, traduzir números em linguagem comum, palavras proibidas sobre auditoria, arquivamento).
- Restauradas as referências que o repositório declarava como "cópia principal na skill" e que **não existiam** na pasta viva: `user-standing-rules.md` e `goldfish-sim-card-rules.md` (mais
  `pod-simulator-design.md`).
- Novos: `protocolo-de-avaliacao.md` e `CLAUDE-repositorio.md`.

## O que mudou na atualização de 2026-10-05 (Regra #10)

- `CLAUDE.md` (e o espelho `references/CLAUDE-repositorio.md`): **Regra #10** — classes de erro SISTÊMICAS do motor do simulador (mulligan, terreno virado primeiro, entrada de terreno contra o oráculo, fetch real,
  gatilho de "a land enters" em todo ponto de entrada, determinismo com `PYTHONHASHSEED`) são varridas por script em todo simulador novo ou alterado (`varredura-2026-10-05/scripts/`).
- `references/user-standing-rules.md`: nova seção 21 (espelha a Regra #10).
- `mtg-commander/references/protocolo-de-avaliacao.md`: nova §7 (varredura mecânica do motor) e 3 linhas no checklist de erros (agora §8).
- `mtg-commander/SKILL.md`: parágrafo "Simulador novo ou alterado" e uma linha em "Tom e abordagem".
- **Aviso (Regra #9):** a pasta viva da skill é sincronizada com a conta do usuário, mas alterações feitas nela durante uma sessão NÃO são gravadas na conta; este backup é a cópia durável e a skill da conta só reflete a mudança se for reinstalada a partir daqui.

## O que mudou na atualização de 2026-10-07 (ordem terreno × payoff de landfall)

- `CLAUDE.md` (e o espelho `references/CLAUDE-repositorio.md`): Regra #10 passa a listar `audit_landfall_ordem.py` (agora lê também a `lista.md` do deck e reconhece `main_phase(`; **0 candidatos**) e a classe "ordem terreno × payoff de landfall" com a
  chave `LANDFALL_PAYOFF_FIRST` nos 6 simuladores com payoff (Mothman, Toph, Beorn, Thranduil, Maralen, Prismatic Bridge) e o que NÃO cobre (magia que põe terreno em campo, terreno que volta ao campo).
- `references/user-standing-rules.md` §21, `references/goldfish-sim-card-rules.md` (nova seção "Payoff de landfall antes do terreno"), `mtg-commander/references/protocolo-de-avaliacao.md` §7 e `mtg-commander/SKILL.md`: mesma classe.
- A **pasta viva** da skill (`/root/.claude/skills/synced/<id>/mtg-commander/`) só tinha o `SKILL.md` (sem `references/`); foi **reposta inteira a partir deste backup** em 2026-10-07. Como sempre, isso **não grava nada na conta**: a skill da conta só reflete a mudança
  se `mtg-commander.zip` for enviado de novo (passo 2 abaixo, que só o usuário consegue fazer).

## O que mudou na atualização de 2026-10-20 (compra no 1º turno)

- `CLAUDE.md` (e o espelho `references/CLAUDE-repositorio.md`): Regra #10 passa a listar `audit_compra_t1.py` (por **execução**: a queda da biblioteca entre `turns=0` e `turns=1` ≥ 1 em toda partida; **20 de 20 COMPRA**) e a classe "compra do 1º turno" (Commander multijogador não pula; o Mothman era o único que pulava; chave `FIRST_TURN_SKIPS_DRAW`).
- `references/user-standing-rules.md` §21, `mtg-commander/references/protocolo-de-avaliacao.md` §7 e `mtg-commander/SKILL.md`: mesma classe. `mtg-commander.zip` e `SHA256SUMS` refeitos.
- **Cuidado ao rodar o script:** nesta sessão a pasta viva da skill (`/root/.claude/skills/synced/<id>/mtg-commander/`) só tinha um `SKILL.md` ANTIGO (sem `references/`, sem a Regra #10). `sincronizar-skill.sh --para-backup` teria **apagado** este backup e o substituído por essa cópia velha. Por isso a atualização foi feita **direto no backup** (edição dos arquivos + `sha256sum` + `--zip`), sem `--para-backup`. Antes de usar `--para-backup`, rode `--status` e confira que a skill viva é a mais nova; se não for, restaure primeiro a partir do backup (item 1 abaixo). Como sempre, nada disso é gravado na conta: a skill da conta só reflete a mudança se `mtg-commander.zip` for enviado de novo.

## O que mudou na atualização de 2026-10-22 (Tam: classes novas na Regra #10)

- `CLAUDE.md` (e o espelho `references/CLAUDE-repositorio.md`): Regra #10 passa a listar `audit_tam_terrenos.py` (as varreduras de terreno para o simulador do Tam; 0 falhas; `audit_compra_t1` reexecutado: 20 de 20 COMPRA), duas classes de erro novas (contador acumulado lido como flag: turnos extras da Ichormoon Gauntlet; **ordem de pagamento do mana**: Bloom Tender / Faeburrow Elder e unidade irmã de fonte já tocada), o aviso de que um script de varredura que não roda também é vácuo, e o que NÃO cobre (a ordem de pagamento nos outros simuladores com Bloom Tender; perfil de oponente calibrado só no Tam).
- `references/user-standing-rules.md` §21, `mtg-commander/references/protocolo-de-avaliacao.md` §7 e §8 (2 linhas novas no checklist de erros) e `mtg-commander/SKILL.md`: mesma classe. `mtg-commander.zip` e `SHA256SUMS` refeitos.
- **Como foi feito (Regra #9):** os espelhos (`CLAUDE.md`, `user-standing-rules.md`) foram copiados do repositório para cá; `protocolo-de-avaliacao.md`, `SKILL.md` e este README foram editados **direto no backup**. Eu **não** rodei `sincronizar-skill.sh --para-backup`: a pasta viva da skill nesta sessão é mais antiga que este backup e o comando a copiaria por cima dele. A pasta viva não foi atualizada nesta sessão e **nada foi gravado na skill da conta**; para a conta refletir, é preciso enviar `mtg-commander.zip` de novo (passo 2 abaixo, que só o usuário consegue fazer).

## O que mudou na atualização de 2026-10-23 (Beorn: gatilho de fase preso a `can_attack`)

- `CLAUDE.md` (e o espelho `references/CLAUDE-repositorio.md`): Regra #10 passa a listar `audit_inicio_de_combate.py` e a **terceira classe** de erro de motor (gatilho de fase nomeada preso a `can_attack`/doença de invocação: o gatilho da Beorn é "at the beginning of combat on your turn"), com o que NÃO cobre (outras fases; The Ozolith em 3 decks).
- `references/user-standing-rules.md` §21, `mtg-commander/references/protocolo-de-avaliacao.md` (§7 e uma linha nova no checklist de erros) e `mtg-commander/SKILL.md`: mesma classe. `mtg-commander.zip` e `SHA256SUMS` refeitos.
- **Como foi feito (Regra #9):** espelhos copiados do repositório; `protocolo-de-avaliacao.md`, `SKILL.md` e este README editados **direto no backup**; **não** rodei `sincronizar-skill.sh --para-backup` (a pasta viva da skill é mais antiga que o backup e o comando a copiaria por cima). A skill da conta **não** foi atualizada; só o usuário consegue reenviar `mtg-commander.zip`.

## O que mudou na atualização de 2026-10-28 (Rat King: Spellbook, rulings e classes novas na Regra #10)

- `CLAUDE.md` (e o espelho `references/CLAUDE-repositorio.md`): Regra #10 passa a listar `audit_etb_sem_efeito.py` (ETB/feitiço sem efeito e gatilho sem reação; controle positivo no Rat King), as classes (d)–(j) achadas no Rat King (tipo/cor conferido só nas cartas esquecendo as fichas, ETB fantasma, redução de custo abaixo da mana colorida e `pips_b=0` em magias, gatilho de conjuração 2×, fórmula "X" do ruling, custo "sacrifice" e `{T}` da própria fonte, sneak CR 702.190, combo do Spellbook que o simulador não executa), a lição de que **variante de A/B que não difere das outras é vácua**, e o que NÃO cobre (Spellbook: só 9 dos 47 decks têm registro; ETB fantasma nos outros 19 simuladores).
- `references/user-standing-rules.md` §21 e `mtg-commander/references/protocolo-de-avaliacao.md` (4 linhas novas no checklist de erros): mesma classe. `mtg-commander.zip` e `SHA256SUMS` refeitos.
- **Como foi feito (Regra #9):** espelhos copiados do repositório; `protocolo-de-avaliacao.md` e este README editados **direto no backup**; **não** rodei `sincronizar-skill.sh --para-backup` (a pasta viva da skill é mais antiga que o backup e o comando a copiaria por cima). A skill da conta **não** foi atualizada; só o usuário consegue reenviar `mtg-commander.zip`.

## O que mudou na atualização de 2026-10-28 (Rat King, rodada 4: Fell Mire, Black Market Connections, ensaio do terreno virado; Spellbook em todos os decks)

- `CLAUDE.md` (e o espelho `references/CLAUDE-repositorio.md`): Regra #10 ganha a classe (k) (**ensaio a seco que mede só o que sai da mão ignora o comandante**: Rat King, comandante até T2 87,2% → 97,9%; 13 simuladores com a mesma função, não medidos) e troca a frase sobre o Spellbook (rodado nos 46 decks em 2026-10-28; falta conferir se cada simulador executa os combos).
- `references/user-standing-rules.md` §21 (novo bullet do Rat King de 2026-10-28) e `mtg-commander/references/protocolo-de-avaliacao.md` (§7 e 4 linhas novas no checklist de erros) e `mtg-commander/SKILL.md`: mesma classe. `mtg-commander.zip` e `SHA256SUMS` refeitos.
- **Como foi feito (Regra #9):** espelhos copiados do repositório; `protocolo-de-avaliacao.md` e este README editados **direto no backup**; **não** rodei `sincronizar-skill.sh --para-backup` (a pasta viva da skill é mais antiga que o backup e o comando a copiaria por cima). A skill da conta **não** foi atualizada; só o usuário consegue reenviar `mtg-commander.zip`.

**Acréscimo do mesmo dia (rodada 5 do Rat King e goldfish #6 da Tam):** `references/user-standing-rules.md` §21 ganha mais um bullet (wipes no próprio campo, limite de perda líquida como política minha, gravar a saída de cada teste antes da verificação completa, pergunta aberta × confirmada no goldfish manual) e `mtg-commander/references/protocolo-de-avaliacao.md` §8, três linhas novas no checklist de erros. `CLAUDE.md` não mudou nesta rodada. Mesmo procedimento da Regra #9 (espelhos copiados do repositório, protocolo e README editados direto no backup, `--para-backup` não rodado); `mtg-commander.zip` e `SHA256SUMS` refeitos. A skill da conta **não** foi atualizada; só o usuário consegue reenviar `mtg-commander.zip`.

## O que mudou na atualização de 2026-10-29 (revisão de código do PR #1: turno extra do Tam #6)

- `references/user-standing-rules.md` §21 ganha o item (d) no bullet do Rat King/Tam #6 (**resposta do usuário que afirma o que ele NÃO fez se confere contra o bruto**: o turno extra do Oko foi jogado à mão e eu li o contrário) e `mtg-commander/references/protocolo-de-avaliacao.md` §8 ganha uma linha no checklist de erros. `CLAUDE.md`, `goldfish-sim-card-rules.md` e `pod-simulator-design.md` não mudaram. `mtg-commander.zip` e `SHA256SUMS` refeitos.
- **Como foi feito (Regra #9):** `user-standing-rules.md` copiado do repositório; `protocolo-de-avaliacao.md` e este README editados **direto no backup**; **não** rodei `sincronizar-skill.sh --para-backup` (a pasta viva da skill é mais antiga que o backup e o comando a copiaria por cima). A skill da conta **não** foi atualizada; só o usuário consegue reenviar `mtg-commander.zip`.

## Como restaurar / reinstalar

1. **Claude Code (pasta de skills):** copie `skills-backup/mtg-commander/` inteira para `~/.claude/skills/mtg-commander/`.
2. **Skill da conta (app, claude.ai):** pré-requisito: Configurações → Capacidades → "Code execution and file creation" ligado. Depois: **Customize → Skills → "+" → "+ Create skill" → "Upload a skill"** e escolher
   `skills-backup/mtg-commander.zip`. O zip já está pronto (pasta `mtg-commander/` como raiz do zip, com `SKILL.md` dentro, como o app exige; `bash skills-backup/sincronizar-skill.sh --zip` o refaz a partir do backup).
   A documentação oficial não diz o que acontece ao enviar uma skill com o mesmo nome de uma que já existe: o jeito seguro é **excluir (ou desativar) a `mtg-commander` antiga antes de enviar** e conferir na lista.
   **Isso só o usuário consegue fazer: nenhuma ferramenta da sessão grava skills na conta.** Fontes: <https://support.claude.com/en/articles/12512198-how-to-create-custom-skills>,
   <https://support.claude.com/en/articles/12512180-use-skills-in-claude> e <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview> (o texto desses artigos varia entre "Settings > Features" e "Customize > Skills").
3. Conferir: `cd skills-backup && sha256sum -c SHA256SUMS`.

## Como manter (script)

```
bash skills-backup/sincronizar-skill.sh --status        # o que difere (não altera nada)
bash skills-backup/sincronizar-skill.sh --para-skill    # repositório -> skill viva (só os espelhos)
bash skills-backup/sincronizar-skill.sh --para-backup   # skill viva -> skills-backup/ + SHA256SUMS
bash skills-backup/sincronizar-skill.sh --zip           # backup -> skills-backup/mtg-commander.zip (pacote pra enviar à conta)
```

Fluxo: alterou `CLAUDE.md` ou um espelho em `references/` → `--para-skill` → `--para-backup` → commitar tudo junto. Alterou a skill → `--para-backup` → commitar.
As cópias **não podem divergir** (`--status` mostra "igual" nas cinco linhas).
