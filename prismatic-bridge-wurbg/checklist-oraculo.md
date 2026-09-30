# Checklist cláusula-a-cláusula — Esika // The Prismatic Bridge

## Rodada das 4 candidatas: Dihada, Commodore Guff, Vronos, Sarkhan the Masterless — 2026-09-29

**Pedido do usuário:** avaliar a inclusão de cada uma (prós e contras, não
cortes). Números, tabelas e leitura em `goldfish-log.md` (mesma data).

**Premissas do pedido que o oráculo não confirma:**
- **Commodore Guff** não põe contador em "todos os PW": é **um** "another
  target planeswalker you control" por end step. O "todos" sai do proliferate
  que a lista já tem.
- **Vronos** tira de fase **até 2 OUTROS** PWs, no "beginning of the next end
  step" (o gatilho é atrasado); ele mesmo não é protegido.
- Nomes reais: **Dihada, Binder of Wills** (não "Bender") e **Sarkhan the
  Masterless** (não "Soul Aflame").

**Fontes:**
- oráculo ao vivo pelo Scryfall (`/cards/named?exact=`, 2026-09-29). Dihada,
  Vronos e Sarkhan entraram no `oracle-cache.json` (a Guff já estava, texto
  idêntico ao ao vivo).
- rulings ao vivo: Sarkhan (2), Vronos (11), Guff (1), Dihada (0).
- Commander Spellbook com a lista antes e depois de cada troca (e das 4
  juntas) e um controle positivo (tirar a Chain Veil derruba 4 combos: o
  pipeline reage a mudança de lista).

### Cláusula a cláusula (entram só via `swap`; a lista não muda)

| Carta | Cláusula (oráculo ao vivo) | Implementação | |
|---|---|---|---|
| **Dihada** ({1}{R}{W}{B}, 5) | +2: "Up to one target legendary creature gains vigilance, lifelink, and indestructible until your next turn." | `_eff_dihada_plus2`: a lendária que mais ganha (falta vigilância/lifelink, depois maior poder). `_pt` dá as 3 palavras-chave; a criatura vira parede (`_choose_blocker` conta indestrutível), não morre no bloqueio, escapa de "destroy" (wipe do oponente e os meus). Acaba no meu próximo untap. Lendárias criatura da lista (enumeradas por script): Atraxa, Carth, Vorinclex, Peregrine Dynamo. | ✅ |
| | −3: "Reveal the top four cards ... legendary cards ... into your hand and the rest into your graveyard. Create a Treasure token for each card put into your graveyard this way." | `_eff_dihada_minus3`: legendárias vão pra mão (não é compra), o resto pro cemitério, 1 Treasure por carta × Doubling Season. Treasure = 1 mana de qualquer cor (`treasure_stock` em `total_mana`/`color_sources`), persiste entre turnos, some ao ser gasto (`_settle_treasures`). 24 cartas da lista são lendárias (script sobre o `type_line`; Plaza of Heroes NÃO é). | ✅ |
| | −11: "Gain control of all nonland permanents until end of turn. Untap them. They gain haste until end of turn." | `_eff_dihada_ult`: fontes de mana não-terreno desviram (mana extra) e as criaturas de oponente rastreadas atacam com haste (poder somado → `our_combat_step`). A política só usa com 10+ de poder pra roubar (modo padrão nunca: não há oponente). PW/artefato/encantamento do oponente: 📊 ("all nonland permanents" além de criatura: o modelo só tem criatura de oponente). | ✅ / 📊 |
| **Commodore Guff** ({1}{U}{R}{W}, 5) | "At the beginning of your end step, put a loyalty counter on another target planeswalker you control." | `guff_end_step` (chamado em `play_turn`, depois dos retornos da Oath e antes do proliferate da Atraxa e do phase out do Vronos). Alvo: o mais perto do ultimate, nunca ela mesma. Passa por `add_loyalty`: Doubling Season/Vorinclex/Innkeeper nv.3 dobram, All Will Be One dispara. Fora de fase não dispara. | ✅ |
| | +1: "Create a 1/1 red Wizard creature token with '{T}: Add {R}. Spend this mana only to cast a planeswalker spell.'" | `_eff_guff_plus1` (`make_pw_token`: Doubling Season dobra). `wizard_pool` = Wizards de turnos anteriores (doença de invocação); abate a parte GENÉRICA do custo de magia de PW (`spell_cost`, `_wizard_used`); conservador: a {R} também poderia pagar um símbolo {R}. Wizard é criatura: bloqueia (`CHUMP_OK`), morre em wipe. | ✅ / 📝 |
| | −3: "You draw X cards and Commodore Guff deals X damage to each opponent, where X is the number of planeswalkers you control." | `_eff_guff_minus3`: X no momento da resolução (ruling 2023-07-28), ela inclusa; compra X; dano no oponente é proxy (`pw_life_lost_opponent_total`). | ✅ |
| **Vronos** ({3}{U}{U}, 5) | +1: "Up to two other target planeswalkers you control phase out at the beginning of the next end step." | `_eff_vronos_plus1` agenda; `vronos_phase_out_step` roda no fim do end step do meu turno (depois de Guff/Atraxa/Sterling Grove: fora de fase não é alvo nem escolha do proliferate). Até 2 maiores lealdades; Teferi, Time Raveler fica de fora (fora de fase perderia o estático que protege a Bridge de contramágica). `phased_out` zera no meu untap (ruling: volta de fase no untap, com os marcadores). Fora de fase o PW não é atacado, não é alvo de remoção, nem ativa na janela do emblema do Teferi TA. | ✅ |
| | −2: "For each opponent, return up to one target nonland permanent that player controls to its owner's hand." | `_eff_vronos_minus2`: uma criatura (a maior que ainda ataca) por oponente vivo → `_bounce_creature` (ficha morre, comandante recasta, carta volta com doença). Só permanente criatura de oponente é rastreado: bounce de artefato/encantamento/PW dele é 📊. | ✅ / 📊 |
| | −7: "Target artifact you control becomes a 9/9 Construct artifact creature and gains vigilance, indestructible, and 'This creature can't be blocked.'" | `_eff_vronos_ult`: o artefato de menos custo de perder (Signet > Lantern > Sol Ring > Gauntlet > Chain Veil; a rocha continua produzindo mana). Sem duração. Ataca se estava em campo desde o começo do turno (ruling; `artifact_enter_turn` em `noncreature_etb`), vigilância, indestrutível (wipe "destroy" de artefato não o leva). Só em modo de combate (modo padrão não tem alvo). | ✅ |
| **Sarkhan the Masterless** ({3}{R}{R}, 5) | "Whenever a creature attacks you or a planeswalker you control, each Dragon you control deals 1 damage to that creature." | `opponent_combat`: N = fichas Dragon em campo (no turno do oponente só o −3 cria Dragão; os PWs do +1 só são Dragão no MEU turno). Cada atacante leva N; toughness ≤ N morre antes de causar dano; o resto fica com dano marcado até o fim do turno (restaurado). A lista tem 0 Dragões (script sobre o `type_line`). Fora de fase não dispara. | ✅ |
| | +1: "Until end of turn, each planeswalker you control becomes a 4/4 red Dragon creature and gains flying." | `_eff_sarkhan_plus1`. Rulings 2019-05-03: cada PW (ela inclusa) **deixa de ser planeswalker** até o fim do turno, mantém marcadores e habilidades, **ainda ativa** o que não ativou, não perde lealdade por dano; só ataca quem estava sob controle desde o começo do turno; o efeito só pega PW que já estava em campo (CR 611.2c). Ativa por último (`_activation_order`): o animado perde "Planeswalkers you control have..." da Ichormoon Gauntlet. Ataque: 4 de poder voador por PW pronto (+2 por emblema da Elspeth), sem vigilância. | ✅ / 📝 |
| | −3: "Create a 4/4 red Dragon creature token with flying." | `_eff_sarkhan_minus3` (Doubling Season dobra). Dragão de guarda: bloqueia e alimenta o estático. Política: só com ameaça real e < 2 Dragões (`_defensive_choice`). | ✅ |
| (as 4) | Bolas: "has all loyalty abilities of all other planeswalkers on the battlefield" | `_bolas_borrowed_choice` empresta os −3 de compra da Guff e da Dihada. | ✅ |
| (as 4) | Peregrine Dynamo copia habilidade ativada de fonte lendária | `_copy_value` ranqueia Guff −3 (35) e Dihada −3 (30); o −11 e o −7 entram como ultimate (90). | ✅ |
| (as 4) | Tam (candidata FRA): X = tipos de PW | `PW_TYPES`: Dihada, Guff, Vronos e Sarkhan são 4 tipos novos. | ✅ |

### 🐛 Achado/correção da minha própria premissa (registrado)

- **Sarkhan: eu tinha modelado que o PW animado não ativa mais.** O ruling de 2019-05-03 diz o contrário (**"you can still activate their loyalty abilities if you haven't done so yet this turn"**). Corrigi antes do A/B final (as variantes Vronos/Sarkhan do primeiro lote foram descartadas e rodadas de novo). O que muda de verdade é a Ichormoon Gauntlet.
- **Vronos −7: eu tinha modelado "ataca só no turno seguinte".** O ruling diz que ataca no mesmo turno se o artefato já estava em campo desde o começo do turno. Passou a usar `artifact_enter_turn`.
- **Ruling da Sarkhan que NÃO modelei:** "They don't lose loyalty if they're dealt damage while they're not planeswalkers." No simulador o oponente não age no meu turno, então nunca há dano nesse intervalo (📊 estrutural: instantâneo de oponente no meu turno).

### Escopo do que foi (e do que NÃO foi) verificado (Regra #7)

**Varridas, com o método:**
- conceito "legendário" (Dihada −3/+2, Halfling/Plaza): script sobre o `type_line` ao vivo das 99 cartas: 24 lendárias, batem com `LEGENDARY_CARD_NAMES`; Plaza of Heroes não é lendária;
- conceito "Dragão": script: 0 Dragões na lista (Ugin e Bolas não têm o tipo Dragon);
- conceito "artefato" (Vronos −7): 6 na lista (Sol Ring, Arcane Signet, Chromatic Lantern, Ichormoon Gauntlet, The Chain Veil, The Peregrine Dynamo, criatura-artefato);
- conceito "Wizard": Flux Channeler (na lista) e Tam (candidata FRA); nenhum payoff de Wizard na lista;
- combos: Spellbook antes/depois de cada carta e das 4 juntas: **0 combos novos, 0 quase-combos novos**; controle positivo funcionou;
- Game Changer: nenhuma das 4 é (`is:gamechanger` no Scryfall). O deck continua com 3.
- rulings ao vivo das 4 cartas lidos e conferidos contra o código (2 premissas minhas corrigidas, acima);
- teste dirigido por cláusula: 23 testes novos (124/124).

**NÃO varridas nesta rodada:**
- as outras 99 cartas contra as 4 novas uma a uma (só os conceitos acima e os motores da lista);
- o gatilho "Guff end step" contra a ordem exata com TODOS os outros gatilhos de end step (só Oath, Atraxa, Sterling Grove, Vronos);
- a frente do comandante (Esika, God of the Tree) não existe no simulador, então o Dragão do +1 não ganha vigilância nem mana (a Esika só vale com ela em campo, o que exclui a Bridge);
- instantâneo de oponente no MEU turno (afeta principalmente os PWs animados pela Sarkhan);
- 📊 estruturais com a cláusula citada acima (Dihada −11 além de criatura; Vronos −2 além de criatura).

## Adendo (2026-09-29, 2º pedido do dia): Sisay, Weatherlight Captain

**Pedido do usuário:** "E a avaliação de Sisay, Weatherlight Captain para o deck da PB?"

**Correção de premissa minha, ANTES de escrever código (Regra #1):** eu lembrava o oráculo dela errado ("poder = maior
MV entre as outras lendárias"). O oráculo ao vivo (Scryfall, 2026-09-29; já estava no `oracle-cache.json`, texto idêntico)
é outro: *"Sisay gets +1/+1 for each color among other legendary permanents you control. {W}{U}{B}{R}{G}: Search your
library for a legendary permanent card with mana value less than Sisay's power, put that card onto the battlefield, then
shuffle."* ({2}{W}, Legendary Creature — Human Soldier 2/2). Rulings ao vivo (2): se ela sai depois de ativada mas antes de
resolver, usa-se a última informação; carta com {X} na biblioteca conta X = 0.

### Cláusula a cláusula (entra só via `swap`; a lista não muda)

| Cláusula (oráculo ao vivo) | Implementação | |
|---|---|---|
| "+1/+1 for each color among other legendary permanents you control." | `_sisay_bonus` / `_pt`: união das cores dos OUTROS permanentes lendários em campo. A The Prismatic Bridge conta ("Legendary Enchantment" de 5 cores): com ela em campo a Sisay é 7/7. A cor branca dela própria não conta; fora de fase não existe; marcadores +1/+1 somam. | ✅ |
| "{W}{U}{B}{R}{G}: Search your library for a legendary permanent card with mana value less than Sisay's power, put that card onto the battlefield, then shuffle." | `sisay_activate` / `sisay_targets` / `_sisay_pick` / `_sisay_fetch`. Custo: 5 de mana com as 5 cores (modelo de cor agregado do arquivo: 1 fonte por cor). **Sem {T}**: ativa no turno em que entra. Alvo: lendária permanente da biblioteca com MV < poder e que eu ainda não controlo (regra da lenda). O "then shuffle" resolve ANTES dos ETBs (o gatilho do Carth olha o topo depois). ETB por `_return_to_battlefield`: PW entra com lealdade × Doubling Season e ativa no mesmo main phase (CR 606.3); Oath of Teferi pisca; Carth olha as 7; a Chain Veil registra o turno de entrada. Política: sem PW em campo o melhor PW; com 2+ PWs a Oath of Teferi; senão o PW de maior MV; senão a peça de motor. A busca passa na frente da mão (medido: −0,086 vs −0,069 do turno do 1º ultimate com a mão primeiro). | ✅ |
| Ruling: "If Sisay leaves the battlefield after you've activated its last ability but before that ability resolves, use its last known existence" | 📊 não modelado: o simulador não tem instantâneo de oponente respondendo à ativação (ela resolve inteira). Estrutural (resposta de oponente). | 📊 |
| Ruling: "{X} in a card in a library is considered to be 0" | Sem efeito: nenhuma lendária da lista tem {X} (script sobre o oráculo). | ✅ |
| (interação) The Peregrine Dynamo copia a ativação (fonte lendária que não é comandante) | `sisay_activate`: +1 busca por {1}, uma vez por turno; disputa o {T} da Dynamo com a cópia de PW, que vem antes no main phase. | ✅ |
| (interação) Delighted Halfling e Plaza of Heroes pagam a Sisay (é lendária) | `LEGENDARY_CARD_NAMES`. | ✅ |
| (interação) É criatura: a Bridge a acerta e ela entra com doença de invocação | `creature_enters`; a doença NÃO afeta a busca (não tem {T}). | ✅ |
| (convenção) Não ataca | 📝 peça de motor, como a Tam (`NON_ATTACKING_NAMES`); ela bloqueia como qualquer criatura minha (`_choose_blocker`). | 📝 |
| (interação) Liliana −4 ("each player sacrifices two creatures of their choice"), Eternal Wanderer −4 e os wipes próprios matam a Sisay | A escolha do −4 é MINHA: `liliana_spares_sisay` (padrão ligado) deixa a Sisay por último e usa o +1 se ela seria uma das 2 sacrificadas. Wipes próprios e Elspeth −3 (poder ≥ 4, com a Bridge ela é 7/7) continuam matando (`_mass_creature_removal` lê o poder real por `_pt`). Achado pela instrumentação de fontes de morte na avaliação Sisay × Arena Rector. | ✅ |
| (interação) Redundância do motor de PW de graça (pergunta de 2026-09-30) | Fontes por script sobre o oráculo ao vivo: da BIBLIOTECA só a Bridge (repetível) e a Arena Rector (só se morrer); da MÃO Urza II e Ugin −10. Instrumentação por fonte (`motor_pw_gratis.py`): a Sisay é o 2º motor repetível, mas entra tarde (mediana T8), falha junto com a Bridge (mesmo mana de 5 cores; 21% das partidas padrão sem Bridge até o T6) e escolhe só até MV ≤ 6 (não alcança Ugin/Kaya). Combos: as 2 peças dos 4 combos de 2 peças de PW/artefato são alcançáveis; o simulador só executa o da Vraska (piso zero). Números na seção "Sisay como redundância do motor de PW de graça" do `goldfish-log.md`. | ✅ medido / 📊 combos não executados pelo simulador (piso) |
| (convenção) Ativação no fim do turno do oponente (a habilidade não tem restrição de timing) | ✅ modelada como chave de sensibilidade (`sisay_round_end`, **desligada por padrão**): `try_sisay_round_end` usa a mana que sobrou do meu turno (`mana_held_back`, CR 500.1) na mesma janela de fim de rodada que Tam e Loyal Tutor já usam; criatura buscada entra sem doença de invocação; Dynamo copia por {1}. Soma ≤ 0,005 turno no padrão e +0,19 PW-turnos vivos na resiliência (seção "Sisay com a janela de fim de rodada" do log). Padrão desligado só pra não invalidar os A/B já publicados. | ✅ |

### Escopo do que foi (e do que NÃO foi) verificado (Regra #7)

**Varridas, com o método:**
- conceito "lendária permanente" e MV, por script sobre o `type_line`/`cmc` ao vivo: 24 lendárias na lista (17 PWs + Chain Veil, Oath of Nissa, Oath of Teferi, Vorinclex, Carth, Atraxa, Peregrine Dynamo), MV 1 (1), 3 (5), 4 (6), 5 (4), 6 (6), 7 (1), 8 (1); nenhum terreno, instantâneo ou feitiço lendário; com a Bridge (7/7, MV < 7) ela alcança 22 das 24 (Kaya MV 7 e Ugin MV 8 ficam de fora);
- conceito "cor entre lendárias": o vermelho só existe no Nicol Bolas; sem a Bridge e sem o Bolas o máximo é 2 + 4 = 6 (W, U, B, G);
- combos: Commander Spellbook antes/depois: **0 combos novos**; 2 quase-combos novos com Intruder Alarm (não está na lista); nenhuma combinação conhecida usa a Sisay com as 99;
- não é Game Changer (`is:gamechanger`); o deck segue com 3;
- rulings ao vivo lidos e conferidos contra o código antes do A/B;
- teste dirigido por cláusula: 12 novos ao todo nesta sequência (136/136: 10 da Sisay, 1 da política do −4 da Liliana, 1 da linha deliberada da Arena Rector).

**NÃO varridas:**
- as outras 99 cartas contra a Sisay uma a uma (só os conceitos "lendária", "cor", "MV" e os motores da lista);
- a ordem da política de ativação contra TODAS as janelas do turno (testei mão-primeiro vs busca-primeiro e a janela de fim de rodada; resposta a remoção não);
- o modelo de cor é agregado (1 fonte por cor): o custo {W}{U}{B}{R}{G} pode ser mais difícil de pagar numa mesa real do que aqui;
- 📊 resposta de oponente à ativação (ruling da última informação).

## Rodada Reality Fracture: Tam, Loyal Tutor, Entrust the Spark — 2026-09-25

**Gatilho:** o usuário confirmou as 3 candidatas de FRA que eu tinha
apontado pro deck ("Tam, the Possibility, Loyal Tutor e Entrust the Spark
foram as que pensei mesmo"). Regra 10 aplicada: oráculo ao vivo, curva,
motores do deck e simulador rodado com vários cortes e um controle.

**Fontes:**
- oráculo ao vivo pelo Scryfall (`/cards/named?exact=`, 2026-09-25), salvo no
  `oracle-cache.json`. As 3 cartas ainda não têm rulings publicadas.
- CR atualizadas para a versão efetiva de 2026-09-25 (`rules-cache/`).
- rulings da The Chain Veil, da Oath of Teferi e da Urza Assembles the Titans.

### As 3 candidatas: cláusula a cláusula (entram só via `swap`, a lista não muda)

| Carta | Cláusula (oráculo ao vivo) | Implementação |
|---|---|---|
| Tam, the Possibility ({1}{G}{U}, Legendary Creature — Gorgon Wizard 2/4) | "Planeswalker spells you cast cost {1} less to cast." | `spell_cost`: abate só genérico (tabela `GENERIC_MANA`). Aminatou ({W}{U}{B}) e Nicol Bolas ({U}{B}{B}{B}{R}) não caem; cada cópia reduz de novo. |
| | "{W}{U}{B}{R}{G}, {T}: Proliferate X times, where X is the number of planeswalker types among planeswalkers you control." | `try_tam_proliferate`. X = tipos distintos (`PW_TYPES`, CR 205.3j): 4 Teferis contam 1, The Eternal Wanderer não tem tipo. Tem {T}, então sofre doença de invocação (CR 302.6). Duas janelas: (a) main, antes da passada de lealdade, só se deixa um ultimate pagável no turno; (b) end step do último oponente, com a mana que sobrou do meu turno. Cada proliferate passa pelo mesmo `proliferate_loyalty` (Doubling Season/Vorinclex/Innkeeper, All Will Be One, veneno, +1/+1, lore da Urza). |
| | (Regra #4: The Peregrine Dynamo) "Copy target activated ... ability ... from another legendary source that's not a commander" | A Tam é lendária e não é comandante. A Dynamo copia a ativação na janela de fim de rodada ({1}): X proliferates de novo sem os 5 de mana. No main a Dynamo fica guardada pro ultimate. |
| | 2/4 no combate | Não ataca (perderia o {T}); bloqueia normalmente (`CREATURE_STATS`). A Bridge pode acertá-la (é criatura). |
| Loyal Tutor ({W}, Instant) | "Search your library for a planeswalker card, reveal it, then shuffle and put that card on top." | `try_loyal_tutor`. Com a Bridge em campo, o PW escolhido vai pro topo e o gatilho de upkeep dela o põe em campo de graça. Mesmo ranking da Arena Rector: maior MV, depois maior lealdade; nunca um nome que já controlo. Janelas: end step do último oponente (mana que sobrou) ou em resposta ao gatilho da Bridge no upkeep (CR 113.7a: remover a Bridge depois do gatilho na pilha não o anula). Sem a Bridge, vira "compre o PW certo", só a partir do T8 (`LOYAL_TUTOR_DRAW_MIN_TURN`, política medida: ver goldfish-log). Dispara Inexorable Tide/Flux Channeler/Ichormoon (`on_spell_cast`). |
| Entrust the Spark ({3}{G}{U}, Sorcery) | "You may sacrifice a planeswalker. If you do, search your library for a planeswalker card, put it onto the battlefield, then shuffle." | `_entrust_choice` + `resolve_entrust_the_spark`. Sem PW em campo fica na mão (não faz nada). Sacrifica o PW de menor lealdade, que quase sempre já ativou no turno, e busca o melhor PW direto pro campo. O buscado ativa no mesmo main phase (CR 606.3). O sacrifício é morte: o gatilho do Carth the Lion resolve DEPOIS da busca (`defer_triggers`). |

### 🐛 Bugs de motor achados nesta rodada (afetam a lista atual, não só as candidatas)

1. **PW que entra no main phase só ativava no turno seguinte (Regra #6, orquestração).**
   - A única passada de lealdade (`activate_planeswalkers`) rodava ANTES do loop de conjuração.
   - Afetava todo PW conjurado da mão, capítulo II da Urza no meio do main, ficha da Tamiyo CS −X que entra durante a passada.
   - CR 606.3: "A player may activate a loyalty ability of a permanent they control any time they have priority and the stack is empty during a main phase of their turn, but only if no player has previously activated a loyalty ability of that permanent that turn". Não há doença de invocação pra lealdade.
   - Ruling da Chain Veil: vale também "planeswalkers that come under your control later in the turn".
   - Novo `activate_unactivated_planeswalkers`, chamado depois de cada conjuração e no fim do main.
   - Na rodada anterior, o fix 8 ("PW conjurado ganha lealdade") deu a lealdade, mas não a ativação.
2. **Desconto de custo usava `mv - len(colors)` como genérico.**
   - O Tamiyo's Notebook deixava Nicol Bolas ({U}{B}{B}{B}{R}) em 3 e Counterspell/Damn/Mana Drain em 1.
   - Nova tabela `GENERIC_MANA`, tirada do `mana_cost` real do cache (CR 601.2f: redução só abate genérico).
3. **Proliferate e Deepglow Skate não punham lore na Urza Assembles the Titans (Regra #3).**
   - CR 701.34a ("any number of permanents ... that have a counter") e 714.2b (capítulo dispara ao cruzar N).
   - É escolha do jogador: `try_urza_extra_lore` só inclui a saga se o capítulo vale agora.
     - II: com PW de MV≤6 na mão.
     - III: só antes da passada de lealdade do meu turno; senão o "this turn" se perde e a saga é sacrificada.

### 📝 Aproximações documentadas (não são 📊 de oponente)

- Cópias da Tam (ficha do Oko −5) seguem a doença de invocação da carta original. O motor rastreia criatura nomeada por nome.
- O custo {W}{U}{B}{R}{G} usa o modelo de cor agregado do arquivo: 1 fonte por cor, sem casamento fonte↔símbolo. É a mesma convenção de toda conjuração deste simulador.

### Avaliação (Regra #4/#5/#10: deck primeiro, simulador como apoio)

**Motores da lista em que cada carta entra:**

| Carta | Motores / cartas da lista que ela alimenta | Onde não entra |
|---|---|---|
| **Loyal Tutor** | **The Prismatic Bridge.** O gatilho de upkeep põe em campo o PW que a carta botou no topo: Ugin (MV 8), Kaya (7), Elspeth/Liliana/Wanderer/Teferi TA/Vraska (6), por {W}. Pode ser conjurada em resposta ao próprio gatilho (CR 113.7a: remover a Bridge depois disso não anula o gatilho) ou com a mana que sobrou no end step alheio. **Paradox Haze e Sphinx** dão upkeeps extras, então mais janelas. Por ser mágica não-criatura, dispara **Inexorable Tide/Flux Channeler** (proliferate) e **Ichormoon** (+1 marcador). **Doubling Season:** o PW entra com o dobro. | Sem a Bridge, é tutor pro topo que custa 1 carta (seleção, não vantagem). Não é criatura: não serve de alvo da Bridge. |
| **Tam, the Possibility** | **PW −{1}:** 15 dos 17 PWs têm genérico (Aminatou e Bolas não). **Proliferate X vezes** (a lista tem 12 tipos de PW em 17 PWs): cada proliferate é dobrado por **Doubling Season/Vorinclex/Innkeeper nv3**, dispara **All Will Be One** 1× por permanente, acelera o **Ichormoon Gauntlet [−12]** (turno extra), soma veneno depois da **Vraska −9** e avança a **Urza**. **Peregrine Dynamo** copia a ativação (fonte lendária). **Lendária:** Esika (frente) dá mana a ela; Plaza of Heroes e Delighted Halfling ajudam a conjurá-la. Corpo 2/4 bloqueia. | Custa {W}{U}{B}{R}{G} por ativação, disputa mana com a mão. É criatura: a Bridge pode acertá-la no lugar de um PW. |
| **Entrust the Spark** | **Troca um PW gasto** (Elspeth/Teferis depois do emblema, TR com pouca lealdade, ficha-cópia do Oko) pelo melhor PW da biblioteca **direto no campo**, que ativa no mesmo turno. **Carth the Lion:** o sacrifício é morte, então olha as 7 do topo (depois da busca). **Doubling Season:** o buscado entra com o dobro. Com Ugin: 14 de lealdade, dá pra fazer o −10 no mesmo turno. **Oath of Teferi/Chain Veil:** ativa 2×. | Morta na mão sem PW em campo. 5 manas de feitiço, num slot da curva que já tem 9 cartas. Não é alvo da Bridge. |

**Curva** (62 não-terrenos, CMC médio 3,66; 1:7, 2:12, 3:15, 4:8, 5:9, 6:7, 7:1, 8:2, 9:1).
Com os cortes da recomendação:
- CMC 1: Swan Song sai e Loyal Tutor entra; Veil of Summer também sai.
- CMC 4 → 3: Arena Rector sai e Tam entra.
- CMC 5: Entrust entra.

Resultado (calculado sobre a lista trocada, Scryfall `cmc`):

| CMC | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| cartas | 6 | 12 | 16 | 7 | 10 | 7 | 1 | 2 | 1 |

O CMC médio vai de 3,66 para 3,71. O único custo real na curva é o 1-drop a
menos (Veil de 1 → Entrust de 5).

**Cortes, pela ordem do deck (não do simulador):**
1. **Arena Rector.** ~~A lista não tem outlet de sacrifício de criatura
   (varredura do oráculo), então o gatilho de morte só acontece se o oponente
   ou um wipe matar ela.~~ **CORREÇÃO 2026-09-29 (varredura por script sobre o
   oráculo ao vivo das 99 cartas, pedida na avaliação Sisay × Arena Rector):
   isso estava ERRADO.** A lista tem 2 outlets de sacrifício de propósito
   (Liliana, Dreadhorde General −4: "Each player sacrifices two creatures of
   their choice"; The Eternal Wanderer −4: "Each player sacrifices all creatures
   they control not chosen this way"), 4 wipes que matam a minha criatura
   (Blasphemous Act, Supreme Verdict, Toxic Deluge, Damn overload) e 4 removedores
   de alvo único que posso apontar pra ELA (Damn {B}{B} "Destroy target creature";
   Void Rend {W}{U}{B} "Destroy target nonland permanent"; Nicol Bolas −3
   "Destroy target creature or planeswalker"; Ugin +2 "3 damage to any target").
   Não servem: Farewell exila (não morre), Swords/Path/Anguished Unmaking exilam,
   Elspeth −3 só destrói poder ≥ 4 (a Arena Rector é 1/2), All Will Be One só
   acerta oponente/criatura de oponente. A minha 1ª varredura (regex) **perdeu o
   Damn** porque o "each creature" dele só aparece no overload; a 2ª, por alvo
   ("destroy target", "damage to target"), achou os 4 de alvo único. O simulador
   já modelava os outlets de mesa (`source=liliana_minus4`, `wanderer_minus4`,
   wipes próprios); a linha deliberada Damn/Void Rend na própria Arena Rector
   passou a existir como chave de sensibilidade (`arena_rector_outlet`,
   desligada por padrão). **PENDÊNCIA (não é impossibilidade estrutural, é
   trabalho que ficou por fazer):** Bolas −3 e Ugin +2 apontados pra própria
   Arena Rector não estão modelados. Teto de impacto: o teto de Damn/Void Rend
   (linha antes da mão, 4,8% a 7,2% das partidas) deu só −0,009 turno no 1º
   ultimate; Bolas e Ugin aparecem em frequência menor que as duas mágicas. Ainda é alvo da
   Bridge que não traz PW, e no A/B foi o melhor corte pras 3 candidatas; na
   resiliência cortá-la por um corpo sem texto custa PW-turnos e dano (ver
   `goldfish-log.md`, seção Sisay × Arena Rector).
2. **Swan Song.** É a contramágica mais estreita das 4: só encantamento,
   instantâneo ou feitiço. E dá ao oponente um 2/2 voador, que num deck de
   superfriends é um atacante de PW a mais. Counterspell, Mana Drain e Dovin's
   Veto são mais amplas.
3. **Veil of Summer.** Só vale contra azul/preto. O simulador não distingue
   ela de Dovin's Veto/Void Rend (P1 × P2 indistinguível). As duas são
   incontraláveis e mais amplas do que o modelo de oponente mede:
   - Void Rend destrói qualquer permanente não-terreno;
   - Veto contra-ataca qualquer mágica não-criatura.
   Pela Regra #5, ficam.

Não cortar:
- tutores de terreno (ramp já curto; no A/B, cortar ramp foi sempre dos piores);
- Blasphemous Act (cortar piora a sobrevivência na resiliência);
- Doubling Season (controle, sempre no fundo).

**Veredito:** Loyal Tutor é a melhor das 3 no deck: é a carta que a Bridge
pede. Tam é a segunda, com ganho medido significativo nas duas pontas
(velocidade e resiliência). Entrust the Spark é positiva, mas marginal por
cima das outras duas (−0,02 turno). Entra se a ideia é colocar as 3; o
ganho vem quase todo de Loyal Tutor + Tam.

**Situação na data:**
- As 3 ainda aparecem como `not_legal` no Scryfall porque a coleção não
  lançou (lançamento em 2026-10-02).
- Nenhuma é Game Changer (`game_changer: false`), então o deck continua com
  3/3 no teto do Bracket 3.
- EDHREC (json de cada carta, 2026-09-25, pré-lançamento):
  - Loyal Tutor está em 2.478 decks no geral e em 104 decks da Esika (synergy +0,053);
  - Tam está em 125 decks no geral e em 49 decks da Esika (synergy +0,069);
  - Entrust está em 596 decks e ainda não aparece na página da Esika.

## Rodada dedicada: auditoria completa das 100 cartas + todos os gaps — 2026-09-24

**Gatilho:** "Sim, faz a rodada dedicada fechando os gaps restantes" (depois da
rodada do modelo de combate, que listou 14 gaps). Método da Regra #1 inteiro:
oráculo AO VIVO das 100 cartas (Scryfall `/cards/collection`, 0 não
encontradas), rulings de toda carta com interação duvidosa, leitura do `.py`
inteiro, comparação cláusula por cláusula, e checagem de ordem de fases
(Regra #6). O saldo foi bem maior que os 14 gaps da lista: a auditoria achou
**bugs de motor** que afetavam o deck inteiro.

### 🐛 Bugs de motor (os maiores, afetavam todas as partidas)

1. **Terreno na mão era "conjurado" como mágica de custo 0.** O loop de
   conjuração não excluía terrenos: todo terreno da mão ia pro campo todo
   turno, além do land drop. Medido no commit anterior: até o T4, 2,65 land
   drops mas 5,0 terrenos em campo. Inflava toda a mana do deck e
   adiantava a Bridge em ~1 turno (T4,2 → T5,2 real).
2. **Planeswalker conjurado da mão entrava sem lealdade** (só os postos pela
   Bridge/Urza/Ugin/Tamiyo tinham). 57% dos PWs em campo no fim da partida
   nunca tinham ativado nada.
3. **Doubling Season dobrava o custo [+N] de lealdade.** Ruling oficial: "if
   you activate an ability whose cost has you put loyalty counters on a
   planeswalker, the number you put on isn't doubled ... cost, not effect".
   Vorinclex e Innkeeper nível 3 ("If YOU would put") dobram — ruling do
   Carth confirma. Novo `cost_counter_multiplier` (vale pra custo e pra
   marcador em jogador/veneno).
4. **Carth the Lion cobrava {1} de MANA por ativação.** O oráculo é
   "cost an additional **[+1]**" — é +1 de LEALDADE (rulings: [+1]→[+2],
   [0]→[+1], [−6]→[−5]; 2 Carths = [+2]). Era um bônus tratado como imposto.
5. **Delighted Halfling nunca gerava mana colorida** (o filtro "cor ∈
   produces={C}" vinha antes do filtro "só pra lendária").
6. **Bloom Tender contava "cores" de terreno** (o `CARD_DB` guarda
   identidade de cor nos terrenos; terreno é incolor). Novo `permanent_colors`.
7. **Mulligan embaralhava as cartas postas no fundo** (CR 103.5: vão pro
   fundo, sem embaralhar).
8. **Gatilhos de "sempre que conjurar" não disparavam na conjuração da
   própria Bridge** (nem da Sterling Grove, nem das remoções do modelo de
   combate). Novo ponto único `on_spell_cast`.
9. **Ordem de turno extra (Regra #6):** no modo resiliência os 3 oponentes
   jogavam ANTES do turno extra e de novo depois dele. "Take an extra turn
   after this one" vem logo depois do nosso turno.
10. **Regra de lenda** não existia pra segundos exemplares (fichas-cópia).

### Cláusula por cláusula — o que mudou nesta rodada

| Carta | Cláusula (oráculo ao vivo) | Antes → agora |
|---|---|---|
| Aminatou | +1 compra e devolve 1 ao topo; −1 blink; −6 troca permanentes | +1 era vazio → implementado (com a Bridge em campo, põe PW caro no TOPO pra Bridge colocar de graça — Regra #4); −1 implementado (blink de Deepglow/PW/Carth/Oath de Nissa); −6 📊 (permanentes não-criatura de oponente não modelados; entregaria todos os nossos PWs) |
| Kaya | 0: compre 2 | nunca escolhido → política usa quando ela está segura e a mão curta |
| Narset | −2: olha 4, pega não-criatura não-terreno | comprava o topo → seleção real |
| Nicol Bolas | "has all loyalty abilities of all other planeswalkers" | deferido → empresta ultimates/+ dos outros (ruling: 1 ativação por turno, custo sai do Bolas); −8 1x (📊 quem perde depende de lendária do oponente) |
| Oko | +1 compra 2, descarta 1 (crime) ou 2; −5 ficha-cópia de cada outro não-terreno | +1 vazio, −5 inexistente → implementados; crime rastreado (toda ação nossa que mira oponente); fichas-cópia com o nome da carta, regra de lenda, Doubling Season ×2 |
| Tamiyo, Compleated Sage | −7 Tamiyo's Notebook (custo −{2}, {T}: compre) | só contava → implementado; cópia de encantamento do cemitério agora dispara ETB (bug achado pelo teste) |
| Tamiyo, Field Researcher | −7 emblema: conjurar da mão sem pagar | só as 3 compras → emblema implementado |
| Teferi, Hero | +1 desvira 2 terrenos no end step | nunca → mana pra flash/resposta; −8 emblema acumula (2 = 2 exílios por compra) |
| Teferi, Temporal Archmage | +1 olha 2 pega 1; −1 desvira 4; −10 lealdade no turno dos oponentes | +1 comprava o topo; −1 e emblema inexistentes → implementados (emblema: 1 ativação por PW em cada turno de oponente; não re-ulta, a permissão não acumula) |
| Teferi, Time Raveler | estático: oponente só conjura em velocidade de feitiço | → oponente não contramagica a Bridge (resiliência); +1 📝 (sem janela de instantâneo no nosso lado) |
| Teferi, Who Slows the Sunset | +1 desvira terreno/artefato/criatura; −2 olha 3; −7 emblema desvira tudo no untap do oponente | só vida / compra do topo → mana extra, seleção real, mana de pé no turno dos oponentes; compra do emblema conta só oponente vivo e acumula por emblema |
| Elspeth | −7 emblema | acumula (+2/+2 por emblema) |
| Vraska | 0 "lose 1 life"; −9 veneno | vida nunca saía; −9 nunca usado → veneno real, proliferate em jogador envenenado, Vorinclex dobra, eliminação com 10 |
| Ugin | −10 põe terrenos em campo | landfall (Evolution Sage) agora dispara |
| Ichormoon Gauntlet | PWs ganham [0] proliferate e [−12] turno extra; +1 marcador ao conjurar não-criatura | 100% ausente → implementado |
| The Peregrine Dynamo | copia habilidade ativada/disparada de fonte lendária | 📝 "exceção arquitetural" → implementado (copia a melhor ativação de PW, a Chain Veil, ou o proliferate de end step da Atraxa; cópia não paga custo — ruling) |
| Oath of Nissa | ETB olha 3; PW com mana de qualquer cor | 100% ausente → implementado |
| Oath of Teferi | ETB exila outro permanente, volta no end step | ausente → implementado (volta antes do proliferate da Atraxa) |
| Paradox Haze | cópias | 2 Hazes = 2 upkeeps extras (ruling) |
| Nesting Grounds | {1},{T}: mover marcador | ausente → move 1 lealdade pra um PW alcançar o ultimate no turno (CR 122.5: mover = pôr → Doubling Season dobra, All Will Be One dispara) |
| Sterling Grove | {1}, sacrifique: tutor de encantamento pro topo | ausente → só sem a Bridge em campo (com ela, o upkeep revela o topo e manda o encantamento pro fundo — anti-sinergia real) e em resposta a remoção mirando a Grove |
| Plaza of Heroes | cor p/ lendária; cor de lendária em campo; {3},{T}, exile: protege criatura lendária | só {C} → as 3 implementadas (a Bridge é lendária de 5 cores) |
| Interplanar Beacon | +1 vida ao conjurar PW; mana de 2 cores só p/ PW | ausentes → implementadas |
| Shocklands (10) | paga 2 vida ou entra virada | de graça → política: paga só se a mana muda o turno |
| City of Brass / Mana Confluence | 1 de dano/vida por uso | ausente → aproximação (viradas por último) |
| The World Tree | entra virada | ausente → implementado |
| Blasphemous Act | −{1} por criatura em campo | ausente no loop genérico → `spell_cost` |
| Innkeeper's Talent | nível 1 fora do modelo de combate; nível 2 ward {1} | nível 1 só no combate → todo modo; ward implementado (suposição: oponente paga a partir do T4) |
| Counterspell / Mana Drain / Swan Song / Dovin's Veto | contramágica | 📊 → no modo resiliência ficam na mão e contramagicam remoção/wipe/contramágica do oponente (Swan Song dá o Bird 2/2 voador; Mana Drain dá a mana no próximo main) |
| Mutational Advantage / Ripples of Potential | hexproof/indestrutível/previne dano; phasing | só o proliferate → respostas protetoras (remoção e combate letal a PW) |
| Veil of Summer | "spells you control can't be countered" | 📊 → protege a conjuração da Bridge |
| Delighted Halfling | "that spell can't be countered" | → Bridge paga com ela não é contramagicada |
| Kaya | hexproof | → oponente não a escolhe como alvo |
| Urza | cópia pela Tamiyo CS | começa saga nova |

### 📊 / 📝 que continuam (com a cláusula citada)

- **Exotic Orchard** — "any color that a land an opponent controls could
  produce": terrenos do oponente não modelados; assume as 5 cores numa mesa de 3.
- **Esika, God of the Tree** (frente do MDFC) — conjurar a Esika significa não
  ter a Bridge; o plano do deck é sempre a Bridge (política, não omissão).
- **Aminatou −6**, **Bolas +1 (oponente exila)**, **Narset/Ashiok estáticos**,
  **Vorinclex (oponente põe metade)**, **Kaya 0 (oponentes fazem scry)**,
  **Rhystic Study**, **Veil (compra se oponente conjurou azul/preta)**,
  **Swords/Path (efeito no oponente)** — dependem de estado de oponente não
  modelado.
- **The World Tree** (busca de Gods) — não há God no grimório (Esika está na
  zona de comando).
- 📝 Teferi, Time Raveler +1 (feitiço com flash): o simulador não tem janela
  de instantâneo do nosso lado além das respostas.
- 📝 Segunda Urza simultânea (cópia do Oko −5) e cópia de Innkeeper (nível 1)
  não têm estado próprio; cópia de Bloom Tender usa a doença da original.
- 📝 Teto do simulador de 400 permanentes: Oko −5 com Doubling Season copia a
  própria Doubling Season e o tabuleiro cresce ×4, ×8... (real). Acima disso a
  partida já está decidida; bate em ~4% das partidas.

### Validação

- Reestruturação dos PWs em tabela de habilidades: **md5 idêntico** ao antes
  (padrão e resiliência) antes de qualquer correção.
- Cada correção medida isoladamente (2.000 partidas, mesmas seeds) — tabela no
  `goldfish-log.md`.
- `test_prismatic_bridge_goldfish.py`: **85/85** (33 testes novos, um por
  correção; o da ordem de turno extra roda o loop inteiro — Regra #6).
- Regressão: 20.000 partidas modo padrão + 20.000 mesa mista + 5.000 em cada
  perfil (go-wide/voltron/low/sem combate) + 5.000 com cada carta de
  pillowfort: **0 exceções**. Travamento achado e resolvido no caminho:
  crescimento explosivo real (Oko −5 copiando Doubling Season) → teto de 400
  permanentes no simulador.

## Modelo de combate (oponente ataca planeswalkers) + 9 correções pré-existentes — 2026-09-24

**Gatilho:** pergunta do usuário — *"Conseguimos implementar no goldfish um
simulador de ataque aos PW? [...] Vale incluir Silent Arbiter e Dueling [Grounds]?"*
— aprovado com 3 perfis de mesa + perfil **misto** ("um pouco de cada,
simulando diferentes decks de forma aleatória", que é a mesa real dele).

**Nota sobre "não fabricar tabuleiro do oponente" (CLAUDE.md):** o modelo
cria criaturas de oponente abstratas (P/R/voar/atropelar) como MODELO DE
AMEAÇA, mesma categoria do modo de resiliência já aprovado (remoção/wipe
de oponente simulados) — foi exatamente o que o usuário pediu. Só existe
no modo de resiliência (`simulate_one_with_interaction(attack_profile=...)`);
o modo padrão continua sem oponente nenhum (confirmado bit-a-bit abaixo).

### O modelo (suposições documentadas, não dados reais)

- Arquétipos por oponente: `go_wide` (1–3 criaturas 1/1–2/2 por turno a
  partir do T2, até 15; 15% voam, 10% ímpeto), `voltron` (comandante 3/3
  com atropelar a partir do T3, +1..3/+1..3 por turno até 20; volta 1 turno
  depois de removido com metade do bônus; 35% voa; até 2 apoios 2/2) e
  `low` (30%/turno de uma 3/3 ou 4/4 a partir do T3, até 3). `mixed` sorteia
  o arquétipo de cada oponente por partida.
- O campo cresce todo turno do oponente; ele só ataca a mim/meus PWs no
  turno em que passa no gate de atenção já existente (1/3).
- Alvo: atacantes, do maior pro menor, vão pro PW de maior lealdade até
  somar o suficiente pra matá-lo; depois o próximo; o resto na minha vida.
- Imposto (Sphere/Ghostly Prison): o oponente usa até metade da mana dele
  (turno, máx. 10). Ghostly Prison: atacante de vida não pago é
  redirecionado pro PW (ruling oficial: "a creature that can't attack you
  can still attack a planeswalker you control").
- Bloqueio: prefere matar-e-sobreviver, depois parede, depois chump com
  ficha/dork se o PW morreria ou o atacante tem poder ≥2, troca com
  "motor" só se o PW morreria. Voar/atropelar/toque mortífero/golpe
  duplo/vínculo com a vida modelados. Criatura que atacou no meu turno
  fica virada até o meu untap (não bloqueia).
- Nossas remoções/wipes agora têm efeito real nos 2 lados e ficam na mão
  até existir ameaça (instantâneas usadas na velocidade de feitiço, no meu
  turno — simplificação).
- O motor não encerra a partida com vida ≤ 0 — a métrica `died_turn` marca.

### Cláusula-a-cláusula (cartas que o modelo toca)

| Carta | Cláusula (oráculo Scryfall ao vivo) | Status |
|---|---|---|
| Silent Arbiter / Dueling Grounds | "No more than one creature can attack/block each combat." | ✅ (só no A/B, fora da lista) |
| Sphere of Safety | imposto {X} por atacante em você OU nos seus PWs, X = seus encantamentos | ✅ (A/B) |
| Ghostly Prison | imposto {2} só pra atacar VOCÊ (PW não é protegido — ruling) | ✅ (A/B) |
| The Eternal Wanderer | "No more than one creature can attack The Eternal Wanderer each combat." | 🐛→✅ novo |
| The Eternal Wanderer | +1 exila criatura até o end step do dono; −4 cada jogador fica com 1 | ✅ com alvo real |
| Nicol Bolas, Dragon-God | −3 destrói criatura | ✅ ; −8 📊 (depende de o oponente controlar lendária — só o comandante voltron é rastreado; segue como contagem) |
| Kaya, Intangible Slayer | −3 exila + ficha 1/1 voadora (cópia) pra nós ; +2 "you gain 3 life" | ✅ ; vida do +2 🐛 agora real |
| Vraska, Betrayal's Sting | −2 criatura vira Treasure | ✅ (comandante: 2 turnos até voltar) |
| Teferi, Hero of Dominaria | −3 3ª do topo ; −8 emblema "sempre que comprar, exile permanente de oponente" | ✅ (emblema: só no modelo de combate) |
| Teferi, Time Raveler | −3 devolve criatura | ✅ (ficha some; comandante recasta com doença) |
| Tamiyo, Compleated Sage | +1 vira e congela 1 | ✅ |
| Tamiyo, Field Researcher | +1 compra quando as 2 marcadas causam dano de combate (até meu próximo turno) ; −2 congela 2 | ✅ (+1: ataque proxy + bloqueio) |
| Elspeth, Sun's Champion | −3 destrói poder ≥4 (dos 2 lados) ; −7 emblema +2/+2 e voar | ✅ |
| Liliana, Dreadhorde General | estático "criatura sua morre → compre" ; −4 cada um sacrifica 2 ; −9 cada oponente fica com 1 de cada tipo | ✅ |
| Ugin, the Spirit Dragon | +2 3 de dano ; −X exila coloridos MV ≤ X (dos 2 lados) ; −10 ganha 7 de vida | ✅ ; vida do −10 🐛 agora real |
| Oko, the Ringleader | início de combate: vira cópia de criatura sua (não lendária, sem marcadores — CR 707.2) | ✅ novo |
| Innkeeper's Talent | nível 1: +1/+1 no início de combate (dobra com dobradores) | ✅ novo |
| Arena Rector | "When this creature dies... search for a planeswalker, put it onto the battlefield" | ✅ (antes 📊: nada matava criatura nossa — agora combate/wipes/remoção matam) |
| Atraxa, Praetors' Voice | voar/vigilância/toque mortífero/vínculo ✅ ; "At the beginning of your end step, proliferate" | 🐛 nunca existia → ✅ |
| Deepglow Skate / Carth the Lion | ETB | 🐛 só disparava conjurando da mão → ✅ em todo ponto de entrada (`creature_enters`) |
| Remoções/wipes (Swords, Path, Damn, Anguished Unmaking, Void Rend, Toxic Deluge, Supreme Verdict, Blasphemous Act, Farewell) | efeito real, custo real ({B}{B}/overload {2}{W}{W}, "pay X life", "−{1} por criatura", 13 de dano, "lose 3 life") | ✅ no modelo de combate |
| The Peregrine Dynamo | "Legendary **Artifact** Creature" | 🐛 wipe de artefato nunca a alcançava (Regra #3) → ✅ |

### 🐛 Bugs pré-existentes achados e corrigidos (valem no modo padrão também)

1. **Sphinx of the Second Sun implementado com um texto que a carta não
   tem.** O código dava "if you cast it, take an extra turn" + sacrifício
   no upkeep (auditoria de 09-13/14 escrita de memória — exatamente o que a
   Regra #1 proíbe). Oráculo real: "At the beginning of each of your
   postcombat main phases, there is an additional beginning phase after
   this phase." Rulings oficiais conferidas: untap real, gatilhos de upkeep
   disparam (a Bridge de novo!), compra no draw step, efeitos "until your
   next turn" não expiram, depois vai pro end phase (sem main phase).
   Paradox Haze não dobra esse upkeep ("first upkeep each turn"). Novo:
   `sphinx_additional_beginning_phase`, chamado no main pós-combate de
   `play_turn` (Regra #6: ordem real das fases conferida).
2. **Criatura entrando fora do "conjurar da mão"** (Bridge, ult do Ugin,
   cópia da Tamiyo CS): sem doença de invocação (dork gerava mana no
   mesmo turno) e sem ETB de Deepglow Skate/Carth the Lion. Novo ponto
   único `creature_enters`.
3. **Atraxa**: proliferate de end step nunca implementado.
4. **Doubling Season**: só a metade de marcador existia; "creates twice
   that many tokens" nunca. E cópias (Tamiyo CS copiando Doubling
   Season/Vorinclex do cemitério) não empilhavam.
5. **Damn**: cor registrada como {B,W}; a cor da carta é só preta ({B}{B};
   o {W} é do overload/identidade de cor).
6. **Oath of Teferi + capítulo III da Urza somavam** (+2 ativações). Os 2
   dizem "twice rather than only once" — não empilham (ruling oficial da
   Oath). Só a Chain Veil soma.
7. **Urza Assembles the Titans**: marcador de lore não era dobrado por
   Doubling Season/Vorinclex/Innkeeper nível 3; agora dobra, com Read ahead
   real (CR 702.155a: no turno em que entra só dispara o capítulo com
   número EXATO de marcadores).
8. **All Will Be One**: carta na lista com ZERO código. Agora dispara em
   todo ponto em que colocamos marcadores (lealdade, PW entrando — ruling
   oficial 2023-02-04 —, +1/+1, lore). Modelo de combate: mata a maior
   criatura de oponente que o dano mata; senão, dano no oponente (proxy).
9. **Vida real**: ganhos de vida dos PWs (Kaya +2, Teferi Sunset +1, Ugin
   −10) só alimentavam contador; e o gatilho de end step da The Chain Veil
   ("if you didn't activate a loyalty ability... lose 2 life") não existia.

### Gaps restantes confirmados (NÃO feitos nesta rodada — ficam pra uma rodada dedicada)

Listados aqui pra não sumirem (Regra #1 — nenhum é julgamento de valor,
é escopo desta rodada): Oath of Nissa (ETB + mana de qualquer cor pra PW),
Oath of Teferi (ETB blink), Ichormoon Gauntlet (2 cláusulas), Nicol Bolas
(estático), Oko −5 e +1, Vraska −9, Aminatou −1/−6, Teferi Temporal
Archmage −1, Teferi Hero +1 (untap 2 terrenos no end step), Tamiyo CS −7
(Notebook), Nesting Grounds (mover marcador), Sterling Grove (tutor),
Innkeeper's Talent nível 2 (ward {1}), Kaya 0 (política nunca escolhe).

### Validação

- Modelo de combate sozinho: modo padrão **bit-idêntico** (md5 de 300
  seeds × 10 turnos = `78111885dbba34ca35dc78d829e8053c`, igual ao antes).
- As 9 correções: antes/depois medidos uma a uma (2.000 partidas, mesmas
  seeds, padrão + resiliência) — tabela em `goldfish-log.md`.
- `test_prismatic_bridge_goldfish.py`: **52/52** testes dirigidos (cada
  cláusula acima dispara de verdade; Sphinx/Atraxa/Chain Veil testados
  rodando `play_turn` inteiro — Regra #6).
- Regressão: 20.000 partidas modo padrão + 20.000 mesa mista + 5.000 em
  cada perfil (go_wide/voltron/low/sem combate) + 5.000 com cada carta de
  pillowfort: **0 exceções**.

## CR 903.9a: comandante passa pelo cemitério de verdade antes da zona de comando — 2026-09-21

**Gatilho:** mesmo achado do usuário aplicado a todos os 9 decks desta
sessão, depois de eu documentar em TODOS eles que "o comandante nunca
dispara gatilho de morte": *"O comandante não morre e ao invés de ir
pro cemitério, pode ser movido de volta a zona de comando? Pq até onde
sei, comandantes podem ser mortos sim! Confere essa regra com muita
calma e atenção!"* Raciocínio completo da regra em
`megatron-tyrant-mardu/checklist-oraculo.md` (CR 903.9a é ação baseada
em estado — CR 704 — não substituição; texto oficial cacheado em
`rules-cache/comprehensive-rules.txt`, Regra 18 de
`references/user-standing-rules.md`).

**Achado específico deste deck: 2 call sites reais, não só 1.** Este
deck tem DOIS sistemas de remoção de comandante — `remove_permanent`
(novo chokepoint do modo de resiliência, porte dos outros 6 decks) E
`resolve_removal_round` (sistema ANTIGO, específico deste deck, mira
só Bridge/protetores, sempre ativo desde o turno 1 e rodando em modo
PADRÃO também, não só resiliência — `simulate_one` chama `play_turn`
sem `skip_legacy_removal`). Os dois desviavam o comandante direto pra
zona de comando sem passar pelo cemitério. Corrigidos os 2.

**Comandante é Enchantment, não Creature** (The Prismatic Bridge,
confirmado Scryfall) — checado se isso muda o critério: este deck tem
**0 cartas "creature dies"/"planeswalker dies" que reagiriam a um
ENCANTAMENTO morrendo** (Carth the Lion, o único gatilho de morte real
do deck, reage só a "a creature or a planeswalker you control dies" —
Bridge nunca é nenhum dos 2). Correção puramente estrutural, sem
impacto numérico, nos 2 call sites.

**Validação:** compilação OK. Bit-identidade em modo padrão
(replicando o path completo de `simulate_one`, 3000 seeds cada, COM e
SEM Greater Auramancy — já que `resolve_removal_round` roda em ambas
as variantes) contra o commit anterior: **0/3000 mismatches em cada
variante**. Regressão de 20.000 partidas em modo padrão (exercitando o
sistema legado) + 20.000 em modo de resiliência: 0 exceções nos 2, 0
comandantes presos no cemitério. 3 testes dirigidos: (1)
`remove_permanent` no comandante — não fica presa no cemitério; (2)
`resolve_removal_round` (sistema legado) no comandante — mesma
checagem; (3) permanente comum continua indo pro cemitério
normalmente.

## `try_smart_opponent_removal` nunca respeitava shroud de Sterling Grove/Greater Auramancy — 2026-09-21

**Gatilho:** usuário perguntou diretamente, revisando os números de A/B
da rodada anterior: *"Vc levou em conta que existe menos remoção de
encantamento do que de criatura, na Prismatic Bridge? E que a Greater
Auramancy e outro encantamento protegem todos os encantamentos no
deck..."*

**Oráculo real confirmado via Scryfall** — Greater Auramancy ({1}{W},
Shadowmoor 2008) e Sterling Grove ({G}{W}, Modern Horizons 2 2021): as
duas têm a MESMA cláusula, *"Other enchantments you control have
shroud"* (shroud de verdade, não hexproof — protege só contra efeitos
que usam a palavra "target"). Checado contra as 4 wipes reais desta
própria lista (Toxic Deluge/Blasphemous Act/Supreme Verdict/Farewell) —
nenhuma usa "target" ("all creatures", "destroy all creatures", "exile
all X"), então shroud nunca bloqueia um wipe de verdade — o número de
enchantment wipe do A/B anterior (0,48/jogo) está correto, shroud
genuinamente não se aplica a essa categoria.

**Mas achei um bug real na categoria de remoção ALVO** (`try_smart_
opponent_removal`, diferente da categoria de wipe): shroud DEVERIA
bloquear essa categoria (remoção pontual sempre usa "target" de
verdade), mas a função nunca checava `protectors_in_play()`. 2 dos 8
itens de `NONPLANESWALKER_ENGINE_PRIORITY` são encantamentos reais
(Doubling Season, Innkeeper's Talent) — ficavam vulneráveis a remoção
direta mesmo com Sterling Grove em campo, quando deveriam estar
protegidos até o protetor sair primeiro.

**Achado de arquitetura**: o sistema LEGADO (`resolve_removal_round`,
desligado desde que o modo de resiliência substituiu ele) já modelava
isso certo — redirecionava a remoção pro protetor primeiro via
`protectors_in_play()`. Essa checagem nunca foi portada pra
`try_smart_opponent_removal` quando o modo de resiliência assumiu a
categoria — mesmo padrão da Regra #3 do CLAUDE.md (conceito
compartilhado certo numa função, nunca propagado pra função nova que
substituiu ela).

**Corrigido:** se o alvo determinado (lealdade de planeswalker ou
fallback `NONPLANESWALKER_ENGINE_PRIORITY`) for um Encantamento de
verdade (`C(target).type == "Enchantment"`) E houver protetor em campo,
redireciona pro protetor (`protectors_in_play()`, mesma função já
existente). Planeswalkers nunca são encantamento nesta lista (sem
híbrido, confirmado) — o ramo de lealdade nunca precisa de
redirecionamento, shroud de Sterling Grove/Greater Auramancy não
alcança planeswalker nenhum.

**Validação:** modo padrão 100% bit-idêntico ao HEAD anterior (2.000
seeds — mudança é 100% dentro do modo de resiliência, nunca tocado em
modo padrão) + regressão de 20.000 partidas em modo resiliência, 0
exceções + 3 testes dirigidos (Doubling Season nunca removido com
Sterling Grove em campo, 0/1000; Doubling Season removível normalmente
sem protetor, 1000/1000; planeswalker nunca redirecionado mesmo com
protetor em campo, 1000/1000).

**Resultado (A/B 2000 jogos mesma seed_base):** efeito real mas
pequeno, como esperado de uma carta única precisando estar em campo no
exato momento do roll — Sterling Grove passa a ser removido em 0,3%
dos jogos (0,0% antes, nunca era alvo desta categoria antes do fix).
Doubling Season/Innkeeper's Talent removidos praticamente na mesma taxa
(2,5%/4,0-4,2%) porque a maioria dos jogos onde eles são removidos não
tinha Sterling Grove em campo simultaneamente — a correção só muda o
comportamento na janela estreita onde as duas condições coincidem, mas
está certa pela regra real independente do tamanho do efeito medido.

## Modo de resiliência ganha wipe de artefato e wipe de encantamento — 2026-09-20

**Gatilho:** "Temos que incluir remoções de artefatos e encantamentos
tb: Vandalblast, Farewell, Austere Command, etc…" — raciocínio completo
(e a correção de design que se seguiu no mesmo dia) em
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Implementado direto no design FINAL** (este deck recebeu a extensão
DEPOIS da correção de design, então nunca passou pela versão com
rolagens independentes): `try_smart_opponent_wipe(state, log)` único —
1 rolagem "algum wipe acontece" seguida de escolha ponderada de 1 TIPO
só (`WIPE_TYPE_WEIGHTS = {"creature": 0.4, "artifact": 0.2,
"enchantment": 0.15}`), restrita aos tipos com alvo legal em campo
(`C(n).type == "Creature"/"Artifact"/"Enchantment"`).

**Achado real específico deste deck — o ÚNICO dos 7 onde o wipe alcança
o comandante:** The Prismatic Bridge É Enchantment de verdade
(confirmado via Scryfall), então um wipe de ENCANTAMENTO escolhido pela
rolagem ponderada a atinge — o único dos 3 tipos que faz isso neste
deck (wipe de criatura e de artefato nunca a alcançam). `remove_
permanent()` já trata isso corretamente (CR 903.9 — vai pra zona de
comando, nunca cemitério de verdade) sem precisar de exceção extra
dentro da função de wipe. The Chain Veil (já em `NONPLANESWALKER_
ENGINE_PRIORITY`, o maior multiplicador de ativação do deck) é um
artefato real, alvo legal de wipe de artefato.

**Teste dirigido específico:** confirmado que quando a rolagem escolhe
"enchantment" e a Bridge está em campo, ela é removida do battlefield,
`bridge_in_play` vira `False`, e ela NUNCA aparece em `state.graveyard`
(1.241/1.241 disparos corretamente roteados pra zona de comando em
3.000 chamadas simuladas).

**Validação:** modo padrão 100% bit-idêntico ao commit `d66e569` (2.000
seeds) + regressão de 20.000 partidas em modo resiliência, 0 exceções +
testes dirigidos (no máximo 1 tipo por chamada; distribuição ponderada
correta; roteamento CR 903.9 da Bridge via wipe de encantamento).

**Resultado (A/B 2000 jogos mesma seed_base):** % de jogos com pelo
menos 1 wipe de qualquer tipo sobe de 38,7% pra 64,5% (antes = commit
`d66e569`, só wipe de criatura). Avg wipes totais por jogo: 0,465 →
0,982. 16,4% dos jogos "depois" sofrem pelo menos 1 artifact wipe,
27,9% pelo menos 1 enchantment wipe (inclui os casos onde a própria
Bridge é a vítima).

## Porte completo do modo de resiliência (interação de oponente) — 2026-09-20

**Gatilho:** usuário pediu direto, mesmo protocolo já aplicado a
Megatron/Ur-Dragon/Hei Bai/Markov/Ulalek/Toph: *"Repita o processo todo
com o deck da Prismatic Bridge."*

**Diferença estrutural real vs. os outros 6 decks, resolvida ANTES de
implementar:** este arquivo já tinha um sistema de remoção de oponente
próprio (`resolve_removal_round`), construído sob medida em rodada
anterior pra responder "vale incluir Greater Auramancy?" — 12%/oponente/
turno, sempre ativo desde o turno 1, sem gates, mira só Bridge/
protetores. Simplesmente empilhar o modo de resiliência padrão por cima
duplicaria a pressão de remoção (o mesmo problema de "3 contra 1" já
corrigido no Megatron). Perguntei ao usuário antes de implementar; opção
escolhida: **o modo de resiliência SUBSTITUI o sistema antigo dentro
dele mesmo, sem tocar no modo padrão.** `play_turn()` ganhou um parâmetro
`skip_legacy_removal: bool = False` (default preserva 100% o
comportamento de todo call site existente); `simulate_one_with_
interaction()` passa `True`, desligando `resolve_removal_round` só
dentro do modo de resiliência. `resolve_removal_round` continua
intocado no modo padrão, respondendo à pergunta original do Greater
Auramancy sem nenhuma mudança.

**2 bugs reais de Carth the Lion encontrados e corrigidos, sem relação
com o modo de resiliência** — achados só por auditar como
`remove_permanent` deveria interagir com `state.loyalty` (Regra #3 do
CLAUDE.md: conceito compartilhado, não carta isolada). Oráculo real
(Scryfall): *"Whenever Carth enters or a planeswalker you control dies,
look at the top seven cards of your library. You may reveal a
planeswalker card from among them and put it into your hand. Put the
rest on the bottom of your library in a random order."*
1. **"Put the rest on the bottom" estava recolocando no TOPO**
   (`state.library = top7 + rest`) — o oposto do oráculo real. Corrigido
   pra `rest + shuffled_top7`. Isso muda a ordem da biblioteca em TODO
   ETB da Carth, não só quando acha um planeswalker — e por consequência
   o restante do jogo inteiro (mesma seed) diverge depois desse ponto,
   já que consome a mesma `state.rng` compartilhada por tudo mais.
2. **A metade "morte de planeswalker" nunca disparava.** O comentário
   original (2026-09-01) dizia "nada remove nossos planeswalkers uma vez
   em campo" — isso já era FALSO em modo padrão: `add_loyalty()` mata um
   planeswalker de verdade quando a lealdade cai a 0 ou menos (ex.:
   ultimate que zera a própria lealdade). Medido: **1.861 mortes de
   planeswalker em 3.000 partidas de modo padrão** — não um evento raro,
   um evento comum que nunca disparava o gatilho de card advantage da
   Carth. Corrigido: extraído `_planeswalker_dies()` de dentro de
   `add_loyalty()` (mesma cascata real de "um planeswalker seu morre",
   reusada tanto pra lealdade chegando a 0 quanto pra remoção/wipe de
   oponente — a regra real não distingue a causa).

**Consequência real de validação:** como os 2 fixes mudam o consumo de
`state.rng` no meio de partidas reais, comparação bit-a-bit contra o
checkpoint anterior diverge amplamente (~19% das seeds em 5.000, a
maioria delas SEM nenhuma métrica relacionada à Carth mudando —
confirmado por teste dirigido que isso vem do reordenamento de
biblioteca no ETB, não de um bug novo). Isso é o comportamento CORRETO
e esperado de uma correção real de RNG-stream compartilhado (mesmo
padrão já visto no fix do Blightsteel Colossus no Megatron) — validação
trocada de bit-idêntico pra comparação agregada A/B, exatamente como
naquele caso.

**Achado real adicional, documentado mas NÃO corrigido nesta rodada**
(📊, mesma classe do token do Ugin no Ulalek): Arena Rector — *"When
this creature dies, you may exile it. If you do, search your library
for a planeswalker card, put it onto the battlefield, then shuffle."*
Diferente do bug real da Carth (já alcançável em modo padrão, 1.861/
3.000 jogos), morte de CRIATURA nomeada nunca foi possível neste arquivo
antes desta rodada — só fica relevante especificamente quando o NOVO
wipe/remoção alcança a própria Arena Rector, não um pré-requisito
estrutural do port (diferente dos 2 fixes da Carth, que já custavam
valor real em modo padrão hoje).

**Implementado (7 categorias, design final direto):** ataque sem
bloqueio, remoção "inteligente" (mira o planeswalker de MAIOR lealdade
em campo — motor dinâmico real deste deck, qualquer um dos 17 pode
estar em campo a qualquer momento — com fallback pra
`NONPLANESWALKER_ENGINE_PRIORITY` curada: Doubling Season, The Chain
Veil, Vorinclex, Innkeeper's Talent, Deepglow Skate, Carth the Lion,
Evolution Sage, Flux Channeler), discard aleatório, board wipe (só
`type == "Creature"` de verdade — a Bridge é Enchantment, nunca
alcançada por um wipe de criatura), graveyard hate (mass exile + exílio
único, alvo = maior MV entre criatura OU planeswalker no cemitério,
mesmo critério real que `Tamiyo, Compleated Sage -X` já usa pra
recursão), e counterspell mirando só o cast da Bridge (normal ou
flash). `remove_permanent()` (novo): comandante vai pra zona de comando
(CR 903.9, mesma convenção que `resolve_removal_round` já usava);
planeswalker delega pra `_planeswalker_dies` (loyalty dict + Carth
sincronizados); token deixa de existir sem cemitério; carta nomeada vai
pro cemitério de verdade.

**Achado real de calibração, DIFERENTE dos outros 6 decks — a Bridge
sobrevive MAIS sob o modo de resiliência novo que sob o sistema antigo:**
o sistema antigo (`resolve_removal_round`) foi construído
especificamente pra ameaçar a Bridge (essa era a pergunta de pesquisa
original do arquivo). O novo sistema padronizado, seguindo a MESMA
convenção já estabelecida nos outros 6 decks, exclui o comandante de
`NONPLANESWALKER_ENGINE_PRIORITY`/board wipe (ela já tem categoria
dedicada de counterspell, e remoção não a mata de verdade mesmo via CR
903.9) — resultado real medido: Bridge removida em média 1,24x sob o
sistema antigo vs. **0,00x** sob o novo (nunca removida diretamente,
só contra-atacada no cast); Bridge em campo no fim da partida 72,0%
(antigo) vs. **90,8%** (novo). Isso é uma consequência ESPERADA e
CORRETA da decisão de design escolhida pelo usuário (substituir, não
empilhar, mantendo a mesma convenção dos outros decks) — mas muda
substancialmente o que os números do modo de resiliência deste deck
respondem, comparado à pergunta original do Greater Auramancy (que
continua sendo respondida pelo modo padrão intocado). Registrado aqui
explicitamente pra não virar uma surpresa silenciosa.

**Validação:**
- Regressão de 20.000 partidas em modo padrão (pós-fix da Carth) E em
  modo resiliência, 0 exceções nos dois.
- Testes dirigidos: comandante removido vai pra zona de comando (nunca
  cemitério) e fica recastável (taxa já existia, confirmada); remoção
  de planeswalker sincroniza `state.loyalty` e dispara Carth
  corretamente; token não vai pro cemitério; carta nomeada vai;
  `skip_legacy_removal=True` desliga o sistema antigo por completo
  dentro do modo de resiliência, `False` (default) mantém o sistema
  antigo rodando normalmente no modo padrão; taxa de ataque pós-wipe
  cai pra ~13,5% da taxa base (~ fator 0,15 esperado); reordenamento de
  biblioteca da Carth confirmado batendo com o oráculo real ("rest" vai
  pro fundo, não pro topo).
- `run_batch_with_interaction` (2000 jogos, 10 turnos): avg ataques
  sofridos 2,04, avg remoções inteligentes 1,80 (miram planeswalkers,
  não a Bridge), avg board wipes 0,77 (56,1% das partidas), avg
  counterspells 0,06, avg vida final 36,82, Bridge recastada após
  remoção em apenas 4,5% das partidas (baixo porque ela quase nunca é
  removida sob o novo sistema, ver achado de calibração acima).

## Auditoria oráculo-por-oráculo completa — 2026-09-13/14

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil/Nekusar/Ms.
Bumbleflower/Rat King. Oráculo real via Scryfall pras 65 cartas + 29
terrenos + comandante (MDFC modal, layout `modal_dfc` confirmado —
Esika, God of the Tree {1}{G}{G} / The Prismatic Bridge {W}{U}{B}{R}{G}),
comparado cláusula-por-cláusula contra o código já existente (que já
tinha passado por 3 rodadas anteriores — 2026-08-21, 08-28, 09-01 — e é
um dos arquivos mais maduros e documentados do repositório).

**Achado principal — 3 fontes reais de "ativar lealdade mais de 1x por
turno" nunca implementadas, num deck com 17 planeswalkers:**

1. **Oath of Teferi** — "You may activate the loyalty abilities of
   planeswalkers you control **twice each turn** rather than only
   once." Estático, sempre ligado enquanto em campo — a carta inteira
   tinha `tags=set()` (nem fantasma, tag nenhuma).
2. **The Chain Veil** — "{4}, {T}: For each planeswalker you control,
   you may activate one of its loyalty abilities **once this turn** as
   though none of its loyalty abilities have been activated this
   turn." Habilidade ativada real, paga — também `tags=set()`.
3. **Urza Assembles the Titans** — Saga (Read ahead) 100% ausente:
   capítulo I (revela o topo, planeswalker vai pra mão — scry 4 não
   modelado, sem infra de scry neste arquivo), capítulo II (planeswalker
   MV≤6 da mão pra campo de graça), capítulo III (dobra ativação de
   lealdade só naquele turno, depois sacrifica).

Com 17 planeswalkers na lista, esses 3 multiplicadores de ativação são
provavelmente o maior bloco de valor real do deck fora da própria Bridge
— nenhum estava implementado. Corrigido com uma função central
`extra_pw_activation_sources()` (as 3 fontes são aditivas, não mutuamente
exclusivas — Oath of Teferi permite 2x, Chain Veil/Urza cap. III cada
um concede "mais uma" em cima disso), consumida por
`activate_planeswalkers()` (que já ativava 1x por planeswalker por
turno, CR 606.3 — agora ativa `1 + extras` vezes, respeitando a taxa do
Carth the Lion em CADA ativação individual, inclusive as extras).

**Achado secundário — 11 cartas de interação nunca contavam pra métrica,
ao contrário de todos os outros decks da sessão:** Counterspell, Mana
Drain, Path to Exile, Swords to Plowshares, Anguished Unmaking, Damn,
Void Rend, Toxic Deluge, Blasphemous Act, Supreme Verdict e Farewell
tinham as tags reais (`removal`/`counterspell`/`wipe`) desde a
construção original, mas essas tags nunca eram lidas em lugar nenhum —
as cartas eram conjuradas pelo loop genérico (corretamente sem efeito
de bordo real, Regra 1: sem oponente/spell real pra mirar, e nenhum
wipe destrói o próprio board sem motivo), mas nem sequer contavam como
"interação conjurada" na métrica agregada, inconsistente com a
convenção das 5 métricas básicas usada em todos os outros decks
auditados nesta sessão. Corrigido com `interaction_spells_cast_total`.

**Validação:** smoke test (105 nomes no `CARD_DB`, 99 cartas na
decklist, 0 desconhecidas) + 2.000 partidas antes/depois (mesma seed
3000000) + 20.000 partidas de regressão (seed 7000000), 0 exceções em
ambas. Testes unitários dirigidos confirmaram cada correção: Oath of
Teferi e The Chain Veil dobram as ativações reais de um planeswalker no
mesmo turno; Urza dispara os 3 capítulos corretamente (tutora
planeswalker no I, coloca em campo de graça no II, marca a flag de
dobra no III e se sacrifica); Swords to Plowshares agora conta pra
`interaction_spells_cast_total` ao ser conjurada. Métricas de 2.000
partidas subiram como esperado: ativações de planeswalker por partida
7.01→8.65, ultimates usados 1.18→1.48, draws via planeswalker
3.87→4.66 — nenhuma mudança de categoria no comportamento típico do
deck, só o motor de superfriends ficando mais completo.

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron e Nekusar.

**Aviso importante sobre este deck especificamente:** diferente dos
outros, este simulador foi construído **deliberadamente com escopo
restrito** (docstring original: *"Este é um simulador FOCADO, não um
goldfish completo de curva geral... Escopo deliberadamente restrito ao
que a pergunta do usuário pede: turno em que a Bridge resolve, taxa de
acerto da Bridge em criatura/planeswalker, e sobrevivência da
Bridge/protetores sob remoção do oponente"*). Não modela casting geral de
toda a lista com a mesma profundidade dos outros 6 decks — mas modela
com precisão real tudo que compõe o motor central (Bridge + 17
planeswalkers com lealdade rastreada). Nesta rodada, apliquei o mesmo
padrão "compile TUDO" às lacunas que **estavam documentadas como
deferidas**, não ao escopo original do simulador em si.

## 🐛 Achados corrigidos nesta rodada

O docstring antigo tinha 2 notas de "deferido": uma citando "14 cartas
tageadas draw sem gatilho" (na verdade só 2 não-planeswalker, ambas
genuinamente 📊 — ver abaixo) e outra citando 6 fontes de proliferate
fora de escopo "por volume". Investigando cada uma individualmente
contra o oráculo real (não a alegação do comentário antigo):

1. **Sphinx of the Second Sun** — "if you cast it, take an extra turn"
   nunca implementado (nem a fila de turnos extras existia no arquivo).
   Corrigido: `extra_turns_pending`/`sphinx_sacrifice_pending`, mesma
   convenção já usada nos simuladores do Maralen/Megatron desta sessão.
   Verificado que a condição "if you cast it" **não** é satisfeita
   quando a Bridge põe a carta em campo (ela não conjura, só coloca) —
   isso é regra real, não uma lacuna.
2. **Carth the Lion** — ETB "look at top 7, reveal planeswalker, put in
   hand" 100% ausente (eu tinha memorizado errado o texto dela antes de
   verificar — não é a habilidade que eu assumi inicialmente). Corrigido:
   `do_carth_etb()`. Estático real "planeswalker loyalty abilities cost
   {1} more" também implementado (`activate_planeswalkers()`, taxa real
   nas nossas próprias ativações).
3. **Flux Channeler / Inexorable Tide** — "whenever you cast a
   noncreature/any spell, proliferate" 100% ausentes apesar de reusarem
   uma função (`proliferate_loyalty()`) já testada pro Evolution
   Sage/Vraska. Corrigidos, disparam independentemente se ambos em campo.
4. **Mutational Advantage / Ripples of Potential** — proliferate no
   próprio efeito ao serem conjuradas, 100% ausente. Corrigido.

Validado com 6+ testes unitários isolados + regressão de 20.000 partidas
(0 erros, alternando `with_greater_auramancy`) + `run_batch` confirmando
ativação real (Sphinx extra turn 4,7% dos jogos, Carth tutor 11,2%).

## Reclassificações (não bugs, verificação corrigiu minha própria memória)

- **Arena Rector**: eu lembrava errado como ETB "exile + recast lendário
  do cemitério" — o texto real é um **gatilho de MORTE** ("When this
  creature dies..."). Como nada remove nossas próprias
  criaturas/planeswalkers neste modelo (`resolve_removal_round()` só
  atinge Sterling Grove/Greater Auramancy/a própria Bridge), esse
  gatilho nunca teria janela real — 📊 estrutural confirmado, não gap.
- **The Peregrine Dynamo**: "{1},{T}: copy target activated/triggered
  ability from another legendary source" — exceção arquitetural real
  (escolher QUAL dentre N fontes legendárias copiar), mesma classe do
  Strionic Resonator/Weaver of Harmony noutros decks — 📝.
- **Rhystic Study / Veil of Summer**: ambas opponent-dependent de
  verdade ("whenever an opponent casts a spell" / "if an opponent has
  cast a blue or black spell this turn") — 📊, mesma convenção
  consistente em todo o resto da sessão. A nota antiga do docstring
  ("14 cartas") estava contando os 12 planeswalkers com tag "draw" que
  JÁ tinham sido corrigidos na rodada de lealdade (2026-08-28) — a nota
  ficou desatualizada, não os gaps continuavam reais.

## Deferido, confirmado genuinamente fora de escopo (não implementado)

- **Nicol Bolas, Dragon-God** — estático "has all loyalty abilities of
  all other planeswalkers" exigiria uma segunda camada de escolha por PW
  em cima da lógica já hardcoded de `resolve_planeswalker()`.
- **Ichormoon Gauntlet** — concede uma habilidade de lealdade NOVA
  ("[0]: Proliferate", "[−12]: extra turn") a cada um dos 17
  planeswalkers — mesma classe de reestruturação do Nicol Bolas, escopo
  desproporcional ao resto desta rodada.

---

## Resumo numérico

- **~65 cartas não-terreno** (escopo do simulador — foco no motor
  Bridge/planeswalker, não curva geral completa).
- **🐛 Corrigido nesta rodada:** 5 cartas (Sphinx of the Second Sun,
  Carth the Lion, Flux Channeler, Inexorable Tide, Mutational
  Advantage/Ripples of Potential).
- **📊/📝 Confirmado estrutural (2 reclassificações de memória errada,
  não bugs):** Arena Rector, The Peregrine Dynamo.
- **Deferido, genuinamente desproporcional:** Nicol Bolas, Ichormoon
  Gauntlet (ambos exigiriam reestruturar a arquitetura hardcoded de
  planeswalker deste arquivo especificamente, não um julgamento de
  valor sobre a carta em si).
