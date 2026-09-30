#!/bin/bash
# Sincroniza a skill `mtg-commander` (cópia viva) com o repositório (backup versionado) e os arquivos-espelho.
# Uso:  bash skills-backup/sincronizar-skill.sh [--status | --para-skill | --para-backup]
#   --status       (padrão) mostra o que difere, sem alterar nada
#   --para-skill   copia os ESPELHOS do repositório para dentro da skill viva
#                  (CLAUDE.md -> references/CLAUDE-repositorio.md; references/{user-standing-rules,goldfish-sim-card-rules,pod-simulator-design}.md)
#   --para-backup  copia a skill viva inteira para skills-backup/mtg-commander/ e refaz o SHA256SUMS
# Variável opcional: SKILL_DIR (pasta viva da skill; por padrão /root/.claude/skills/synced/*/mtg-commander)
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP="$REPO/skills-backup/mtg-commander"
SKILL_DIR="${SKILL_DIR:-$(ls -d /root/.claude/skills/synced/*/mtg-commander 2>/dev/null | head -1)}"
[ -d "$SKILL_DIR" ] || { echo "skill viva não encontrada (defina SKILL_DIR)"; exit 1; }
MODO="${1:---status}"
ESPELHOS=("CLAUDE.md:references/CLAUDE-repositorio.md" "references/user-standing-rules.md:references/user-standing-rules.md"
          "references/goldfish-sim-card-rules.md:references/goldfish-sim-card-rules.md" "references/pod-simulator-design.md:references/pod-simulator-design.md")
status() {
  echo "skill viva: $SKILL_DIR"; local ruim=0
  for m in "${ESPELHOS[@]}"; do
    origem="${m%%:*}"; destino="${m##*:}"
    if cmp -s "$REPO/$origem" "$SKILL_DIR/$destino"; then echo "  igual     $origem == skill/$destino"; else echo "  DIFERENTE $origem != skill/$destino"; ruim=1; fi
  done
  if diff -rq "$SKILL_DIR" "$BACKUP" >/dev/null 2>&1; then echo "  igual     skill viva == skills-backup/mtg-commander"; else echo "  DIFERENTE skill viva != skills-backup/mtg-commander:"; diff -rq "$SKILL_DIR" "$BACKUP" 2>&1 | sed 's/^/     /'; ruim=1; fi
  return $ruim
}
case "$MODO" in
  --status) status || true ;;
  --para-skill)
    for m in "${ESPELHOS[@]}"; do cp "$REPO/${m%%:*}" "$SKILL_DIR/${m##*:}"; done
    echo "espelhos copiados para a skill viva"; status || true ;;
  --para-backup)
    rm -rf "$BACKUP"; mkdir -p "$BACKUP"; cp -a "$SKILL_DIR/." "$BACKUP/"
    (cd "$REPO/skills-backup" && find mtg-commander -type f | sort | xargs sha256sum > SHA256SUMS)
    echo "backup atualizado: $BACKUP ($(find "$BACKUP" -type f | wc -l) arquivos)"; status || true ;;
  *) echo "modo desconhecido: $MODO"; exit 2 ;;
esac
