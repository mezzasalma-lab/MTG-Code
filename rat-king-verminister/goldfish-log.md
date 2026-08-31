# Goldfish Log — Rat King, Verminister

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

### Simulação #1 — goldfish Python completo (`ratking_goldfish_v1.py`) — 2026-08-31

**Contexto:** simulador construído do zero a pedido direto do usuário
("faça a análise e crie o simulador sem erros do Verminister"). Passo 0
(checklist de `references/goldfish-sim-card-rules.md`): oráculo real das
53 cartas únicas da lista consultado via `scryfall-cache/oracle-cache.json`
(2 cartas ausentes do cache — Fell the Profane // Fell Mire e Priest of
Forgotten Gods — buscadas na API real da Scryfall e adicionadas antes de
qualquer implementação).

**2 correções reais de grafia em `lista.md`** (mesmo padrão do erro já
corrigido antes nesta lista pra Emeritus of Woe/Demonic Tutor, confirmadas
via Scryfall, não presumidas):
- `Priest of the Forgotten Gods` → **`Priest of Forgotten Gods`** (nome
  real não tem "the" — a busca exata pela grafia antiga retornava
  `not_found` na API).
- `Fell the Profane` → **`Fell the Profane // Fell Mire`** — é uma MDFC
  verdadeira (`layout: modal_dfc`, Instant // Land), o nome sem o verso
  não é o nome completo real da carta.

**⚠️ Lista ainda incompleta — não inventado aqui:** `lista.md` já tinha
uma nota própria avisando que a lista está em 99/100 cartas (98 de
biblioteca + comandante, falta 1 carta que o usuário ainda vai escolher).
O simulador reflete a lista REAL como está — `BASE_LIBRARY` tem 98 cartas,
não 99 — `build_library()` faz `assert len(lib) == 98` (não 99) pra não
mascarar o buraco fingindo uma carta que não existe. **Isso significa que
o simulador não pode ser tratado como "final" até a 100ª carta ser
escolhida** — os números abaixo são válidos pra lista atual, mas vão
mudar quando a carta 100 entrar.

**Motores principais implementados de verdade (não só tag), checklist de
13 categorias completo desde a construção inicial (não retrofit):**
- Rat Colony (24x, "+1/+0 por outro Rat") — escala com `rat_count()` real.
- Skullclamp + geradores de token — loop real de equipar/sacrificar por
  {1}, compra 2.
- Cabal Coffers + Urborg, Tomb of Yawgmoth + Crypt Ghast — combo clássico
  modelado com precisão, incluindo o próprio Cabal Coffers virando fonte
  de "tap de Swamp" pro Crypt Ghast dobrar quando Urborg está em campo.
- Thrumming Stone + Rat Colony (ripple 4) — a peça mais explosiva do
  deck (auditoria.md, seção 8), disparo real a cada magia conjurada.
- Aristocrats/dreno (Zulaport, Ayara, Pitiless Plunderer, Priest of
  Forgotten Gods, Dictate of Erebos, Syr Konrad) — despachados a partir
  de um único ponto central (`on_creature_dies()`), sem duplicar gatilho.
- Devoção ao preto real (soma de pips {B}, não aproximação) — Gray
  Merchant, Nykthos.
- The Soul Stone (Harness) — ativação única liga motor de reanimação
  repetível real todo upkeep.
- Emeritus of Woe // Demonic Tutor — layout real `prepare` (Scryfall
  confirmado), condição de 2+ mortes no turno, custo real pago (não de
  graça) ao usar a cópia do Demonic Tutor.
- Ninja Teen (Classe, 3 níveis reais, nível 3 = motor de recursão via
  sneak do cemitério).
- Rat King, Verminister (comandante): "Disappear" (token + contador
  quando um permanente seu sai de campo) + a habilidade de reanimação
  (sac 3 Rats, traz de volta 1 criatura E todas as cópias do mesmo nome
  do cemitério — devastador com Rat Colony).

**Simplificações documentadas (não inventadas):** sem oponente real,
qualquer efeito "opponent loses life"/edict/toxic fica disponível com
contador de disparo mas sem efeito numérico do lado do oponente (mesma
convenção de todos os simuladores desta sessão) — o ganho de vida
próprio (Zulaport, Ayara, Valley Rotcaller, Gray Merchant) é real.
Fell the Profane // Fell Mire registrada só pela face Instant (remoção é
o gap real do deck, 35 terrenos já bastam). Toxic 1 do Karumonix é N/A
estrutural (sem combate real contra oponente). Thornbite Staff sem
nenhuma criatura Shaman na lista — auto-attach nunca dispara, N/A.

**Robustez:** 20.000 partidas (seeds 9300000-9319999, timeout 2s/jogo) —
0 erros, 0 timeouts.

**n=3000, seed_base=9300000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0.31
Turno medio de conjuracao do Rat King: 2.13 | mediana: 2.0
Nunca conjurado em 8 turnos: 0.3%
Avg Rats totais em campo (final): 14.87
Avg tokens criados: 11.61
Avg reanimacoes via Rat King (sac 3 Rats): 3.35
Avg casts gratis via Thrumming Stone (ripple 4): 0.36
Avg compras via Skullclamp: 0.74
Avg nivel final do Ninja Teen: 0.26
Soul Stone harnessed: 4.3% dos jogos
Avg tutores usados: 0.76
Avg vida final: 38.96
Avg mao final: 2.85

--- Metricas basicas (checklist obrigatorio) ---
RAMP: 0.63
DRAW: 2.32
INTERACTION: 0.49
RECURSION: 3.75
FINISHER/LETHALITY (dreno proxy): 4.95
```

**Leitura:** curva muito rápida (comandante em {1}{B}, conjurada em
média no turno 2,13, quase nunca falha em resolver — 0,3% em 8 turnos).
RECURSION alta (3,75/jogo) reflete o motor de reanimação central do
comandante somado a Echoing Return/Secret Salvage/Reanimate — todos
potencializados pelas 24 cópias de Rat Colony no cemitério. Thrumming
Stone só dispara casts grátis em 36% dos jogos em média (0,36) — a
"explosão" citada na auditoria.md depende de já ter Thrumming Stone em
campo E revelar Rat Colony no topo, evento condicional, não garantido.
Skullclamp com só 0,74 compras médias é mais modesto do que a auditoria
sugere ("motor de draw quase sem fim") — o loop de equipar/sacrificar
roda DEPOIS do loop principal de conjuração no `main_phase()`, então só
usa mana que sobrou depois de gastar em ameaças reais primeiro; pode
estar subestimado por essa ordem de prioridade — candidato a revisão
numa próxima rodada.

`lista.md` corrigida (2 erros de grafia). `ratking_v1_runs.jsonl`
criado (3000 jogos).

---

## Partida #1 — AAAA-MM-DD

- **Formato do teste:** goldfish / playtest com amigos / mesa competitiva
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:** vitória / derrota / sem resolução
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

## Partida #2 — AAAA-MM-DD

- **Formato do teste:**
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:**
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

<!-- Copie o bloco acima para cada nova partida -->
