# Backup versionado da skill `mtg-commander`

Cópia de segurança da skill **`mtg-commander`** (especialista em Commander/EDH, com as regras permanentes do usuário e o protocolo de avaliação de cartas/simuladores).
Criada e atualizada em **2026-09-30**. Regra de manutenção: Regra #9 do `CLAUDE.md` (raiz do repositório).

> **Este backup é a cópia durável.** A pasta viva da skill (`/root/.claude/skills/synced/<id>/mtg-commander/`) é sincronizada com a conta do usuário, mas
> **alterações feitas nela durante uma sessão não são gravadas na conta** e o próximo sync pode sobrescrevê-las. Para a skill da conta refletir a versão
> atualizada, é preciso reinstalá-la a partir daqui (abaixo).

## O que tem aqui

| caminho | o que é |
|---|---|
| `mtg-commander/SKILL.md` | a skill (frontmatter `name`/`description` + fluxo de trabalho, Scryfall, brackets, checklist de análise, tom) |
| `mtg-commander/references/commander-rules.md`, `archetypes.md`, `scryfall-api.md` | referências originais da skill (inalteradas) |
| `mtg-commander/references/user-standing-rules.md` | **regras permanentes do usuário** (20 seções; cópia idêntica de `references/user-standing-rules.md` do repositório) |
| `mtg-commander/references/protocolo-de-avaliacao.md` | **novo:** protocolo de avaliação de cartas, simuladores, A/B e relatório (destilado das Regras #1–#9) e checklist de erros já cometidos |
| `mtg-commander/references/goldfish-sim-card-rules.md`, `pod-simulator-design.md` | lições de processo dos simuladores e design do motor de mesa (cópias idênticas de `references/` do repositório) |
| `mtg-commander/references/CLAUDE-repositorio.md` | texto integral das regras do repositório (cópia idêntica do `CLAUDE.md` da raiz, Regras #1–#9) |
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

## Como restaurar / reinstalar

1. **Claude Code (pasta de skills):** copie `skills-backup/mtg-commander/` inteira para `~/.claude/skills/mtg-commander/`.
2. **Skill da conta (app):** zipe a pasta `mtg-commander/` (com `SKILL.md` na raiz do zip) e envie como skill nas configurações da conta. Não verifiquei o caminho exato dessa tela; o formato
   (`SKILL.md` com frontmatter + `references/`) é o padrão de skills.
3. Conferir: `cd skills-backup && sha256sum -c SHA256SUMS`.

## Como manter (script)

```
bash skills-backup/sincronizar-skill.sh --status        # o que difere (não altera nada)
bash skills-backup/sincronizar-skill.sh --para-skill    # repositório -> skill viva (só os espelhos)
bash skills-backup/sincronizar-skill.sh --para-backup   # skill viva -> skills-backup/ + SHA256SUMS
```

Fluxo: alterou `CLAUDE.md` ou um espelho em `references/` → `--para-skill` → `--para-backup` → commitar tudo junto. Alterou a skill → `--para-backup` → commitar.
As cópias **não podem divergir** (`--status` mostra "igual" nas cinco linhas).
