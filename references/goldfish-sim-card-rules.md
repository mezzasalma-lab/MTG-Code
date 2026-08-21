# Regras permanentes pra simuladores de goldfish

> Espelho versionado deste repositório do arquivo canônico em
> `references/goldfish-sim-card-rules.md` dentro do skill `mtg-commander`
> (`/root/.claude/skills/synced/mtg-commander/`, fora do controle de versão
> deste repo). O skill é a cópia que eu realmente consulto antes de escrever
> ou editar um simulador — esta aqui existe pra ficar versionada e visível
> no seu histórico do GitHub. Se as duas divergirem, atualize as duas juntas.

Cartas nesta lista precisam ter o efeito real implementado em código em
**qualquer** simulador Python de goldfish que inclua elas — não basta marcar
com uma tag decorativa (`trigger_doubler`, etc). Checar esta lista sempre que
uma carta daqui aparecer na decklist de um simulador novo ou existente.

Adicionada por pedido explícito do usuário (sessão do Thranduil, 2026-08-21):
"Quero que isso seja feito em todos os decks com essa carta daqui em diante."

---

## Roaming Throne

`{4}` Artifact Creature — Golem, 4/4, Ward {2}.

Oracle text (Scryfall): *"As this creature enters, choose a creature type.
This creature is the chosen type in addition to its other types. If a
triggered ability of another creature you control of the chosen type
triggers, it triggers an additional time."*

**O que implementar:**
- Rastrear o tipo de criatura escolhido (na prática: o tipo tribal central do
  deck — Elfo, Dragão, Zumbi, etc — é quase sempre a escolha certa; documentar
  a premissa no código se não for óbvio).
- Para CADA gatilho de criatura desse tipo já modelado no simulador (draw
  engines, geradores de token, gatilhos do próprio comandante, etc), disparar
  uma **segunda vez completa** quando o Roaming Throne estiver em campo — não
  só dobrar o número final. Um gatilho que resolve "compre 2, descarte 1" vira
  dois disparos separados de "compre 2, descarte 1", não vira "compre 4,
  descarte 2" resolvido de uma vez (pra manter fidelidade caso o efeito tenha
  escolhas que podem variar entre os dois disparos).
- **Não dobra habilidades ativadas nem estáticas** — só gatilhos ("whenever"),
  e só de criaturas do tipo escolhido. Enchantments/artifacts/instants/sorceries
  nunca são afetados, mesmo compartilhando o tipo tribal via texto solto.
- Rastrear e reportar uma métrica agregada de "quantos gatilhos foram
  dobrados" pra medir o impacto real nos resultados do goldfish.

**Referência de implementação:** `thranduil-sultai/thranduil_goldfish_v1.py`
no repositório de decks do usuário — função `roaming_throne_active()` no
`GameState`, aplicada em `_apply_etb`, `_creature_cast_engines_trigger` e
`combat_step`.

---

<!-- Adicionar novas entradas abaixo conforme surgirem cartas com efeitos
     estruturais que exigem implementação explícita (não só tag) em qualquer
     simulador que as inclua. -->
