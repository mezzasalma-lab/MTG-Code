# Revisão dos terrenos de mana restrita/condicional nos simuladores (2026-11-11)

Pedido do usuário (2026-11-11): *"Vc vai precisar revisar e corrigir o Plaza e demais terrenos em todos os simuladores"*.
Gatilho: partida manual #3 do Wise Mothman, em que o usuário (e o simulador) não jogaram a Plaza of Heroes no T4, mesmo sendo o único jeito de pagar o {B} do comandante.

**Escopo declarado (Regra #7). Nada abaixo é "revisão completa".** O que foi feito, com que método, e o que NÃO foi:

| classe | método | simuladores | resultado |
|---|---|---|---|
| inventário de terrenos com mana restrita/condicional | script estático (`scripts/audit_terrenos_condicionais.py`, oráculo do `scryfall-cache`) | 46 decks com `lista.md`, 189 terrenos, 20 com simulador | triagem; a modelagem de cada terreno foi lida à mão só nos casos citados abaixo |
| **(o) ESCOLHA do terreno ignora o comandante** (outro terreno da mão deixaria o comandante conjurável neste turno) | instrumentação em runtime (`scripts/audit_terreno_comandante.py`, `audit_terreno_comandante_pb.py`): ensaio a seco com o terreno em campo e remoção imediata, só LÊ o estado | Mothman, Tam, Prismatic Bridge | Mothman 6,69% (padrão) / 7,01% (resiliência) das partidas, N=10.000; Tam 32,15% / 34,15% (N=2.000, dominado por T2/T3); Prismatic Bridge: ver `audit_terreno_comandante_pb_*` |
| (o) nos outros 17 simuladores | só `grep` da função de escolha do terreno | Azula, Beorn, Captain Storm, Edgar, Hei Bai, Kutzil, Maralen, Megatron, Bumbleflower, Nekusar, Rat King, Thranduil, Tom, Toph, Ulalek, Ur-Dragon, Vihaan | **NÃO medido**: cada um tem API de estado diferente (nomes em lista × `Permanent`); só os 3 acima têm a Plaza, mas o erro vale para qualquer terreno que dê cor/mana só para o comandante (Command Tower, Great Hall, Cavern de tipo do comandante, etc.) |
| mana contada em dobro / terreno fora da regra do `{T}` | leitura à mão + teste dirigido, nos terrenos em que o nome aparece numa linha de acúmulo de mana | todos (grep de 31 nomes de terreno) | **1 bug real: Oakhollow Village (Bumbleflower)** |

## Achados

### 1. Mothman, Tam, Prismatic Bridge: a Plaza (e qualquer terreno que libere o comandante) não era escolhida
Causa: `land_play_score` (Mothman/Tam) pontuava a Plaza como terreno incolor (−4) e a escolha do Prismatic Bridge preferia o "terreno que cobre cor que falta" pela lista `produces`, onde a Plaza só tem `{C}`. O ensaio do "terreno virado primeiro" (classe (k)) também ignora o comandante.
Correção: `commander_enabling_land` (chaves `PLAZA_ENABLES_COMMANDER` no Mothman, `COMMANDER_ENABLING_LAND` no Tam e no Prismatic Bridge). Validação em `wise-mothman-sultai/resultados-ab/2026-11-11-plaza-comandante/`, `tam-the-possibility-wubrg/resultados-ab/2026-11-11-terreno-comandante/`, `prismatic-bridge-wurbg/resultados-ab/2026-11-11-terreno-comandante/`.

### 2. Bumbleflower: Oakhollow Village rendia 2 mana por 1 `{T}` (mana fantasma) e tinha 2 erros de regra
Oráculo: `{T}: Add {C}.` / `{T}: Add {G}. Spend this mana only to cast a creature spell.` / `{G}, {T}: Put a +1/+1 counter on each Frog, Rabbit, Raccoon, or Squirrel you control that entered the battlefield this turn.`
- `lands_available` já contava o terreno (está em `LAND_NAMES`) e `rocks_mana` somava +1 de novo. **Teste dirigido: 2 Forest + Oakhollow = 4 de mana; 3 Forest = 3.** Chave `OAKHOLLOW_COUNTS_ONCE`.
- `color_sources` tratava o terreno como criatura (só fonte de {G} se `entered_turn < turn`; terreno não tem enjoo de invocação, CR 302.6) e como fonte de {G} para QUALQUER magia (o {G} só paga magia de criatura; o {C} segue pagando o genérico de qualquer magia). Chave `OAKHOLLOW_MANA_RULES`.
Validação em `ms-bumbleflower-bant/resultados-ab/2026-11-11-oakhollow-mana/`.

### 3. Lacunas achadas na leitura e NÃO corrigidas (cada uma exige a cadeia completa de validação)
- **Ulalek: Eldrazi Temple e Shrine of the Forsaken Gods tratados como 1 mana genérica.** Oráculo: Eldrazi Temple `{T}: Add {C}{C}. Spend this mana only to cast colorless Eldrazi spells or activate abilities of colorless Eldrazi`; Shrine `{T}: Add {C}{C}. Spend this mana only to cast colorless spells. Activate only if you control seven or more lands`. O docstring do simulador diz "tratadas como terreno genérico de 1 mana". Isso **subestima** a mana do Ulalek e não é impossibilidade estrutural (a cor e o tipo da magia estão no cache; o modelo de mana é agregado, então a correção é um bônus por magia conjurada, não por pip). **Pendente.**
- **Nekusar: Gemstone Caverns** (`add("Gemstone Caverns", 0, "land", set())`, 1 menção): a cláusula de mão inicial ("if this card is in your opening hand and you're not the starting player, you may begin the game with it on the battlefield with a luck counter on it; exile a card from your hand") e o `{T}: Add {C}` / "any color com luck counter" não estão modelados como cláusulas. **Pendente.**
- **Exotic Orchard: convenção INCONSISTENTE entre simuladores** (oráculo: "any color that a land an opponent controls could produce"). Azula, Bumbleflower, Tam e Ur-Dragon a tratam como terreno que não produz nada ("dependente de oponente, não presumido"); Kutzil, Megatron, Prismatic Bridge e Edgar como "qualquer cor da identidade do comandante". A mesa real tem 3 oponentes; a escolha de convenção muda o resultado dos decks que a têm. **Decisão do usuário** (a Regra #1 proíbe fabricar estado de oponente; a pergunta é qual proxy usar de forma uniforme).
- **Edgar: Command Tower produz as 5 cores** (identidade do Edgar é W/B/R): inofensivo no simulador (nenhuma magia do deck pede U/G), mas diverge do oráculo.
- **Maralen, Nekusar, Ulalek: modelo de mana agregado (sem pips)**: as restrições de cor dos terrenos (Cavern, Secluded Courtyard, Reflecting Pool, Command Tower) não são rastreadas por construção. Não é um bug de terreno específico; é o limite de modelagem declarado nesses arquivos.

### 4. O que não foi lido
Nenhuma varredura das **ativadas** dos terrenos (Boseiju, Takenuma, Eiganjo, Spawning Bed, Urza's Cave, Cabal Coffers, Crypt of Agadeem, Big Apple etc.) além das linhas de acúmulo de mana acima; o Rat King, o Edgar, o Ur-Dragon e o Tam tiveram auditoria própria de terrenos em rodadas anteriores (não reaberta aqui).
