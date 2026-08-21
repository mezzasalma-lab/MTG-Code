# Comparação — meu Beorn vs. decklist de referência trazida pelo usuário

Fontes: Scryfall REST API (`cards/collection`, `cards/named`, `cards/search?q=is:gamechanger`, campos `oracle_text`, `type_line`, `cmc`, `color_identity`, `legalities.commander`), consultada em 2026-08-20. Comparação feita por diff de conjuntos de nomes entre `/root/mtg-decks/beorn-fierce/lista.md` (meu deck) e a lista colada pelo usuário (referência externa, fonte não identificada — só o texto colado).

---

## 1. Validação da lista de referência

100 cartas, todas encontradas no Scryfall (6 precisaram de busca individual por serem MDFC — o endpoint de coleção não resolve nomes com "//"). Mono-verde, sem violação de identidade de cor, sem cartas banidas.

## 2. Estatísticas comparadas

| | Meu deck | Referência |
|---|---|---|
| Terrenos | 38 | 37 |
| CMC médio (não-terreno, sem comandante) | 3.82 | 3.31 |
| Game Changers | 1 (Natural Order) | 0 |
| Cartas em comum | 28 de 100 | 28 de 100 |

Os dois decks compartilham só 28 cartas — são builds bem diferentes do mesmo comandante, não variações próximas.

## 3. Onde a referência é estruturalmente mais forte — remoção

Minha auditoria anterior (`auditoria.md`) já tinha identificado remoção como o ponto fraco do meu deck: só ~5 cartas (Beast Within, Song of the Dryads, Archdruid's Charm, Ezuri's Predation, Haywire Mite), nenhuma delas um wipe limpo.

A lista de referência tem uma cobertura bem maior, toda verificada por `oracle_text`:

**Fight-based (remoção de criatura):**
- Ram Through — `{1}{G}` instant, sua criatura luta com a do oponente, trample manda o excesso na cara
- Contest of Claws — `{1}{G}` sorcery, fight + discover pelo dano excedente
- Epic Fight — `{2}{G}` sorcery modal, pode dobrar poder/resistência E lutar
- Khalni Ambush // Khalni Territory — instant de fight, MDFC que também joga como terreno
- Bridgeworks Battle // Tanglespan Bridgeworks — sorcery de fight com +2/+2, mesma lógica de MDFC-terreno

**Artefato/encantamento:**
- Boseiju, Who Endures — terreno com channel pra destruir artefato/encantamento/terreno não-básico — essencialmente remoção "de graça" no slot de terreno
- Masked Vandal — corpo cara Changeling, exila carta do cemitério pra destruir artefato/encantamento
- Chomping Changeling — corpo Changeling, destrói artefato/encantamento ao entrar
- Druid of Purification — destrói um artefato/encantamento por jogador (inclusive os seus, é político mas geralmente favorável)
- Rampaging Yao Guai — corpo `{X}{G}{G}{G}` com contadores, destrói artefatos/encantamentos com CMC total até X ao entrar

Isso é **10 peças** de remoção/resposta contra as ~5 do meu deck, cobrindo criatura e artefato/encantamento de forma muito mais completa.

## 4. Onde a referência também é mais eficiente — proteção

Swiftfoot Boots, Silkguard, Strength of Will, Tyvar's Stand, Rhonas the Indomitable (corpo indestrutível nativo). Meu deck tem Heroic Intervention, Lightning Greaves, Obscuring Haze, Gigantic Big Bear (hexproof), Allosaurus Shepherd — pacotes parecidos em volume, mas a referência tem mais peças baratas e instantâneas (Ram Through/Tyvar's Stand custam 1-2 mana vs. meu Ezuri's Predation em 8).

## 5. Peças de valor que meu deck não tem

- **Lithoform Engine** e **Strionic Resonator** — copiam habilidade ativada/disparada. Relevante especificamente porque Beorn tem uma habilidade disparada de combate (converter criatura em Urso) — copiar esse gatilho significa converter 2 criaturas em Urso no mesmo combate.
- **Bonders' Enclave** — terreno, compra repetível com criatura poder 4+, sem custar um slot de spell.
- **Fanatic of Rhonas** e **Werebear** — dorks que continuam relevantes depois do early game (Fanatic escala com poder 4+, Werebear vira 4/4 com threshold), diferente de um dork que só serve pro T1-T2.

## 6. Correção — Necklace of Girion e Ezuri's Predation ficam

Consultei o EDHREC (`https://edhrec.com/commanders/beorn-the-fierce`) a pedido do usuário. Dois erros da versão anterior desta análise, corrigidos:

- **Necklace of Girion**: 47% de inclusão entre decks de Beorn registrados no EDHREC — é staple comum do comandante, não carta fraca/lenta. Removida da lista de corte.
- **Ezuri's Predation**: o próprio EDHREC categoriza como remoção ("sorcery que remove criaturas", 10% de inclusão) — cria um 4/4 pra cada criatura do oponente e cada token luta com uma delas, o que mata a maioria das criaturas da mesa. É remoção em massa assimétrica de fato, não "pseudo-wipe caro" como eu descrevi antes. Erro meu, corrigido. Removida da lista de corte.

## 7. Sugestões de remoção adicionais — via EDHREC, sem tocar em Girion/Ezuri's Predation

| Carta | Inclusão (EDHREC) | Efeito (Scryfall `oracle_text`) |
|---|---|---|
| Nature's Claim | 27% | `{G}` instant, destrói artefato/encantamento, oponente ganha 4 de vida |
| Krosan Grip | 18% | `{2}{G}` instant com Split Second, destrói artefato/encantamento |
| Return to Nature | 13% | `{1}{G}` instant modal, destrói artefato OU encantamento, ou exila cemitério |
| Force of Vigor | 11% | `{2}{G}{G}`, ou grátis exilando carta verde da mão se não for seu turno, destrói até 2 artefatos/encantamentos |

## 8. Sugestões concretas de troca (revisado — mantém Bracket 3, GC continua em 1)

Da comparação com a lista de referência (seção 3), sem envolver Girion nem Ezuri's Predation:

| Cortar do meu deck | Motivo | Trocar por | Ganho |
|---|---|---|---|
| Haywire Mite | Só destrói artefato/encantamento não-criatura, corpo fraco | Rampaging Yao Guai (referência) ou Nature's Claim (EDHREC, 27%) | Mesma função, mais eficiente ou com corpo real |
| Germination Practicum | Lento (`{3}{G}{G}`) | Contest of Claws ou Epic Fight (referência) | Mais uma linha de fight removal |
| 1 Forest | — | Boseiju, Who Endures (referência) — **decidido pelo usuário** | Remoção "de graça" no slot de terreno; reduz 38→37 terrenos, igual à referência |

**Correção — Obscuring Haze também fica.** Texto confirmado (Scryfall): *"If you control a commander, you may cast this spell without paying its mana cost. Prevent all damage that would be dealt this turn by creatures your opponents control."* É um Fog de graça (com o comandante em campo) pro time inteiro — proteção real, não "sem remoção" como eu descrevi antes (ela nunca foi pra ser remoção). Removida da lista de corte. Ram Through continua como sugestão de remoção, só que sem cortar nada específico pra abrir espaço — fica em aberto pro usuário decidir o que tirar, se quiser incluir.

Restam **2 trocas concretas** (Haywire Mite, Germination Practicum) mais a troca de terreno já decidida (Forest → Boseiju).

---

## 9. Opções de "sem tamanho máximo de mão" — mono-verde/incolor

Pedido do usuário: nas simulações, muitas cartas acabam descartadas por limite de mão. Busca no Scryfall (`o:"no maximum hand size" f:commander id<=G`, ou seja identidade de cor verde/incolor, legal em Commander) retornou 9 cartas. As que cabem numa identidade mono-verde:

| Carta | Custo | Efeito adicional | Nota |
|---|---|---|---|
| **Reliquary Tower** | terreno, `{T}: Add {C}` | nenhum além do hand size | Zero custo de oportunidade em spell — só ocupa 1 slot de terreno. Já estava na lista de referência do usuário. |
| **Spellbook** | `{0}` artefato | nenhum | Custo zero pra conjurar, mas não faz mais nada — puro fixador de hand size. |
| **Thought Vessel** | `{2}` artefato | `{T}: Add {C}` (rock de mana) | 2-em-1: vira ramp E resolve o hand size. |
| **Library of Leng** | `{1}` artefato | ao descartar, você escolhe pôr no topo do grimório em vez do cemitério | Sinergiza se o deck fizer self-mill/loot; senão é só hand size barato. |
| **Decanter of Endless Water** | `{3}` artefato | `{T}: Add {C}` de qualquer cor | Fixação de cor é irrelevante em mono-verde — Thought Vessel faz o mesmo mais barato. |
| **Venser's Journal** | `{5}` artefato | ganha 1 de vida por carta na mão, todo upkeep | Caro, mas de valor real se a mão ficar grande de fato. |
| **Praetor's Counsel** | `{5}{G}{G}{G}` sorcery | devolve TODO o cemitério pra mão, uma vez | Não é um fixador barato — é uma bomba de recursão que também resolve hand size pro resto do jogo. Encaixa como wincon/reset, não como peça de suporte. |
| **Wrenn and Seven** | `{3}{G}{G}` planeswalker | hand size vem só do -8 (emblema), junto com devolver todo o cemitério pra mão | O hand size é só um bônus da ultimate — a carta já é boa por outros motivos, não escolher só por isso. |

**Recomendação direta:** Reliquary Tower (custo zero de spell-slot) ou Thought Vessel (se quiser o rock de mana junto) são as inclusões mais eficientes pra resolver o problema específico que você descreveu. Venser's Journal e Praetor's Counsel são upgrades de maior investimento que resolvem o mesmo problema e ainda adicionam outro efeito relevante.

---

## Links

- EDHREC: https://edhrec.com/commanders/beorn-the-fierce
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
