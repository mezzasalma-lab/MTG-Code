# Goldfish Log — Edgar Markov

## Simulação #1 — gerada por Claude (RNG real, não é partida sua)

**Método:** embaralhei a lista de 100 cartas de `lista.md` com `random.shuffle` do Python (sem seed fixa, entropia do sistema) em 2026-08-20. On the play, sem compra no T1.

**Mão inicial:** Takenuma Abandoned Mire, Smothering Tithe, Godless Shrine, Arcane Signet, Roaming Throne, Swamp, Swords to Plowshares

**T1:** Joga Takenuma, Abandoned Mire.

**T2:** Compra: Sevinne's Reclamation. Joga Godless Shrine. Conjura Swords to Plowshares (`{W}`) — sem alvo real num goldfish solo (não há criatura de oponente), incluído aqui só como jogada de curva hipotética.

**T3:** Compra: Unholy Annex // Ritual Chamber. Joga Swamp. Conjura Arcane Signet (`{2}`).

**T4:** Compra: Skullclamp. Sem terreno na mão. Conjura Skullclamp (`{1}`).

**T5:** Compra: Phyrexian Altar. Sem terreno na mão (3 terrenos + Arcane Signet = 4 fontes de mana no total).
**Correção em relação a uma primeira passada automática:** meu script inicial tentou conjurar Sevinne's Reclamation aqui, mas isso está errado — Sevinne's Reclamation exige um alvo no cemitério com custo de mana 3 ou menos, e nenhuma criatura morreu ainda nessa simulação, então **não há alvo legal e a mágica não pode ser conjurada**. Corrigindo: com 4 mana disponível, a jogada real é conjurar **Roaming Throne** (`{4}`), escolhendo o tipo Vampire ao entrar (sinergiza com o Eminence do próprio Edgar Markov e com os outros gatilhos de Vampiro da lista).

**T6:** Compra: Edgar Markov. Sem terreno na mão. Mana disponível: 3 terrenos + Arcane Signet = 4. Edgar Markov custa `{3}{R}{W}{B}` = 6 total — **não castável ainda**, faltam 2 fontes de mana. Com os 4 mana disponíveis, a jogada real é conjurar **Smothering Tithe** (`{3}{W}`), usando Godless Shrine/Arcane Signet pro W.

**Board final (fim do T6):** Takenuma Abandoned Mire, Godless Shrine, Swamp, Arcane Signet | Skullclamp, Roaming Throne (tipo Vampire), Smothering Tithe.
**Mão remanescente:** Sevinne's Reclamation (ainda sem alvo), Unholy Annex // Ritual Chamber, Phyrexian Altar, Edgar Markov (o próprio comandante preso na mão por falta de mana).
**Observação honesta:** essa mão específica ficou land-light (só 3 terrenos em 6 turnos) e nunca chegou a resolver o próprio comandante em campo — ele ficou parado na mão do T6 em diante por faltar 2 fontes de mana. Não simulei além do T6.

---

## Simulação #2 — goldfish Python completo (`edgar_markov_goldfish_v1.py`) — 2026-08-21

**Script construído do zero**, CARD_DB gerado via Scryfall `cards/collection` (99 cartas), tags derivadas de `oracle_text` real. Passo 0 (regra de Roaming Throne, `references/goldfish-sim-card-rules.md`): varredura mecânica encontrou **16 vampiros com gatilho próprio** (de 20 + o próprio Edgar) — todos implementados como mecânica real (Eminence, contador de ataque do Edgar, Sanctum Seeker, Champion of Dusk, Welcoming Vampire, Clavileño, Vito Fanatic de Aclazotz em 3 estágios, e o pacote de morte Blood Artist/Cruel Celebrant/Cordial Vampire/Vindictive Vampire/Vein Ripper via um loop de sacrifício limitado a 2 por turno).

**Simplificações documentadas no docstring do script:** sem combate real contra o oponente (assume Edgar sempre ataca livre depois do summoning sickness); drain/lifegain rastreados como contadores agregados, não life totals reais; Ashnod's Altar/Phyrexian Altar não contam pro `total_mana()` automático (exigem sacrifício, só geram mana quando o loop de sacrifício os usa de fato).

**n=2000, 8 turnos:**

```
Avg mulligans: 0,58
Turno médio de conjuração do Edgar Markov: 5,90 | mediana: 6
Nunca conjurado em 8 turnos: 17,1%
Avg tokens de Vampiro via Eminence: 2,46
Avg turnos em que Edgar atacou: 1,74
Avg contadores +1/+1 distribuídos: 5,90
Avg drain_total (proxy): 0,65 | Avg lifegain_total (proxy): 0,77
Avg criaturas sacrificadas: 1,09 | Avg gatilhos de morte: 0,58
Avg compras via Champion of Dusk: 0,22 | via Welcoming Vampire: 0,25
Avg drains via Sanctum Seeker: 0,16
Avg Demons via Vito Fanatic (3o estágio): 0,00
Avg gatilhos de Clavileño (sem efeito extra modelado): 0,21
```

**Combo Exquisite Blood + Vito, Thorn of the Dusk Rose — resposta à pergunta em aberto da auditoria original ("não simulei o deck pra saber em que turno esse combo tipicamente monta"):**

```
Partidas em que o combo montou E ligou (até T8): 0,1% (2 de 2000)
Turno médio em que liga, quando acontece: 7,67 | mediana: 8
```

**Leitura:** dentro de uma janela normal de 8 turnos, o combo montar e efetivamente ligar é **raríssimo** (0,1%) — exige que as duas peças específicas (Exquisite Blood + Vito, Thorn of the Dusk Rose, cada uma ~1% de densidade em 99 cartas) sejam compradas e conjuradas na mesma partida, o que é uma coincidência dupla rara mesmo com o volume de tutores do deck (Vampiric Tutor, Diabolic Intent, Demonic Tutor via Emeritus of Woe — o simulador atual não modela ativação de tutor pra buscar peça específica, é uma extensão futura). Isso não muda a classificação de Bracket 4 (o critério oficial é sobre a PRESENÇA estrutural do combo com habilitadores redundantes, não sobre a frequência real de montagem em partidas de goldfish) — mas é um dado real que faltava.

**Roaming Throne:** em campo em 10,2% dos jogos, dobrando em média 0,30 gatilhos de Vampiro por partida — número baixo porque a maioria dos 16 gatilhos de vampiro tem densidade individual baixa (cada vampiro é só 1 carta de 99), a mesma dinâmica de baixa coincidência já vista nos outros decks desse usuário.

---

### Política "caçar o combo" — comprova a classificação de Bracket com dado real — 2026-08-21

**Pedido do usuário:** implementar uma política que prioriza os 2 tutores reais e baratos (Vampiric Tutor `{B}`, Diabolic Intent `{1}{B}`) especificamente pra buscar a peça que falta do combo Exquisite Blood + Vito, Thorn of the Dusk Rose, e conjurar as peças assim que disponíveis — pra medir se o combo consegue ligar antes do turno 6 (o corte oficial de Bracket) quando o jogador está mirando nisso de propósito, não só por sorte.

**Implementação:** novo flag `COMBO_HUNTING_POLICY` (default `False`) + função `combo_hunt()`, chamada no topo do `main_phase`. Diabolic Intent busca a peça faltante direto pra mão (exige sacrificar uma criatura em campo); Vampiric Tutor busca pro topo da biblioteca (pega na próxima compra normal). Novo campo rastreado: `both_combo_pieces_turn` (turno em que as 2 peças já estão em campo, antes de precisar de um gatilho pra "ligar" o loop).

**n=2000, 8 turnos, comparando as duas políticas:**

| Métrica | Genérica (default) | Caçando o combo |
|---|---|---|
| 2 peças em campo até T4 | 0,0% | 0,3% |
| 2 peças em campo até T5 | 0,1% | 1,6% |
| **2 peças em campo até T6** | **0,1%** | **2,6%** |
| 2 peças em campo até T8 | 0,7% | 4,6% |
| Turno médio (quando acontece) | 7,38 | **6,20** |
| **Combo ligado (gatilho de vida disparou) até T6** | **0,0%** | **0,0%** |
| Combo ligado, total em 8 turnos | 0,1% | 0,6% |

**Verificação de correção:** rastreei uma partida individual (seed 6000261) onde as peças alinharam rápido — Vampiric Tutor no T1 buscou Exquisite Blood, Vito Thorn veio de compra natural no T3, Exquisite Blood entrou em campo no T5 assim que teve mana (`{4}{B}`). Confirma que a lógica está certa; é só raro de acontecer, não um bug.

**Leitura:** mesmo com o jogador ativamente perseguindo o combo com os 2 tutores reais, a chance dele estar **ligado** antes do turno 6 é **0,0%** em 2000 partidas. O cálculo manual de "melhor caso turno 5" feito antes de rodar essa simulação era otimista demais — assumia mana certa toda hora e nenhuma outra prioridade competindo, cenário que não reflete a realidade de um deck de 99 cartas singleton. Isso muda a classificação de Bracket de volta pra 3 (ver `auditoria.md` seção 12, 2ª correção) — o critério oficial é "antes do turno 6", e mesmo perseguido de propósito o combo não entrega isso de forma confiável.

---

<!-- Para novas partidas (reais ou novas simulações), use o formato abaixo -->

## Partida #N — AAAA-MM-DD

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
