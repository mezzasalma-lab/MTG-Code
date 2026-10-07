# The Wise Mothman — candidatas das coleções pós-Edge of Eternities (2026-10-05)

> Pedido do usuário: *"analise em todas as coleções após Edge of Eternities o que podemos adicionar para melhorar o deck, especialmente em termos de mill e
> proliferate. Algo que dê trample para o comandante também seria muito útil."* Auditoria do deck: `auditoria.md`.
> Dados brutos, scripts e como refazer cada número: `resultados-ab/2026-10-05-candidatas-pos-eoe/LEIAME.md`.
> **O corpo deste documento (§1–§10) é anterior ao simulador** (oráculo + rulings + Commander Spellbook + contas de probabilidade; onde é raciocínio, está marcado
> **(raciocinado)**). **O §0b abaixo traz o que o simulador mediu depois** (A/B pareado, `goldfish-log.md`). Nada foi cortado ou adicionado na lista do usuário: são sugestões.

## 0. Veredito

**Pacote recomendado: 5 trocas** (todas dentro do Bracket 3; Spellbook: 0 combo novo, 0 combo some; curva média 2,94 → 3,00; fontes de cor U/B/G 16/16/18 → 17/16/19) **+ The Master of Lake-town, com o corte ainda em aberto.**

> **Correção (2026-10-05, usuário): o Kozilek NÃO é corte.** Eu tinha proposto Kozilek ← Master tratando o "embaralha o cemitério na biblioteca" como custo (zera Six/Muldrotha/Icetill).
> O usuário lembrou que ele é **o seguro contra morrer por auto-mill**: o deck tem 8+ fontes de auto-mill e nenhum outro efeito que devolva cartas à biblioteca. Sobra a pergunta
> "a quantas partidas isso salva?", que só um simulador responde — **respondido no §0b**: ≈ 2,4 pontos de deck-out (5,7% → 3,3%) jogando cuidadoso.
> O Master fica **sem corte designado** (candidatos a medir: Negate, Strip Mine, Yavimaya Hollow); números do pacote antigo de 6 trocas ficam em `resumos/` marcados como SUPERADOS.

> **Atualização 2026-10-07 — Riverchurn Monument** (pedido do usuário: inclusão + 5 cortes): `resultados-ab/2026-10-07-riverchurn-monument/LEIAME.md` e `goldfish-log.md` §11. Cortes sugeridos, do menos ao mais importante: Offer, Negate, Cold-Eyed Selkie, Toxic Deluge, Arcane Denial (a Muldrotha **saiu** da lista em 2026-10-07: é a recursão mais forte do deck, ver `goldfish-log.md` §11). **Conflito:** Offer, Negate e Selkie já estão reservados neste documento (Garruk's Uprising, Master e Evolution Sage); o Monument mede +0,3 a +0,9 ponto de T8 por cima do pacote.

| entra | sai | por quê entra (motor do deck) | por quê sai |
|---|---|---|---|
| **Evolution Sage** (2G, 3/2, ECC) | Cold-Eyed Selkie | landfall → proliferate: 14 efeitos além da jogada normal botam terreno; proliferate cresce 19 cartas com +1/+1, os rad counters, Ascension, Palantír, Urza's Saga | 1 vínculo de motor (compra se conectar), corpo 1/1 |
| **Karn's Bastion** (terreno, EOC) | Swarmyard | `{4},{T}`: proliferate, sem gastar slot de mágica (terreno incolor por terreno incolor) | 1 vínculo (regenera Inseto: Mothman/Icetill) |
| **Bruvac the Grandiloquent** (2U, 1/4, SLD) | Soul-Guide Lantern | "se oponente fosse milar, milla o dobro": dobra 14 fontes de mill do oponente + os rad counters dele; dobra o X do Mothman | cantrip com hate de cemitério |
| **The Master of Lake-town** (1BB, 3/2 toque mortal, HOB) | *(a medir; **não** o Kozilek)* | "quando um jogador perde vida, ele milla essa quantidade": perda de vida do oponente na lista = Ascension, Mindcrank, Konrad, Palantír, Ballista + rad counters; **2º parceiro da Bloodchief Ascension** (Spellbook) | — |
| **Garruk's Uprising** (2G) | An Offer You Can't Refuse | **trample no time inteiro** (Mothman incluso) + compra quando entra criatura de poder ≥ 4 (9 na lista, mais com contadores) | contramágica que dá 2 Treasures ao oponente; sobram 5 contramágicas |
| **Opulent Palace** (terreno BGU, ECC) | Bojuka Bog | G e U são as cores apertadas (triagem); troca virado-por-virado | só B (B tem sobra), entra virado. **Com a Lantern também fora, o único hate de cemitério que sobra é o `−1` da Ashiok**: se a sua mesa tem reanimação, corte **Yavimaya Hollow** (incolor, regenera) no lugar da Bojuka Bog |

**Respostas diretas**

- **Proliferate:** hoje só **1** efeito (Cankerbloom, sacrifício único) numa lista com 19 cartas de contador +1/+1, 3 de rad e 3 amplificadores "+1". O pacote leva a 3
  (Sage, Bastion + Cankerbloom). O Mothman ainda ganha de brinde o ruling: "efeitos como proliferate interagem com rad counters".
- **Mill:** o deck já tem 14 fontes de mill no oponente. O que faltava não era mais mill, era **multiplicador** (Bruvac) e **conversor de vida em mill** (Master of Lake-town).
- **Trample no comandante:** o deck **já tem** Kodama + (qualquer contador ou a Swiftfoot Boots, que já está na lista). O que falta é redundância: **Garruk's Uprising**
  (não é criatura, então sobrevive a remoção de criatura).
- **Mais do que o pacote?** Há mais 14 candidatas boas (§9). Eu **não** escolhi cortes para elas (o simulador mediu só o pacote de 5 e o Master, §0b): os próximos cortes menos ligados são Negate, Yavimaya Hollow e Strip Mine
  (os dois últimos são terreno e baixariam os 36 slots).

## 0b. O que o simulador mediu (2026-10-05, depois de escrever o §0)

Simulador: `mothman_goldfish_v1.py` (commit `91b1a3d`), 3 oponentes **passivos**, N = 10.000 pareado, IC95%; detalhes, tabelas e limites em `goldfish-log.md`; dados brutos e como refazer em `resultados-ab/2026-10-05-ab-pacote-kozilek-master/` e `…-ab-kozilek-self-deck/`.

| pergunta | medido (modo padrão; resiliência na mesma direção, menor) |
|---|---|
| **Kozilek evita morrer por self-mill?** | **Sim.** Deck-out: 3,3% com ele, 5,7% com ele **sem o embaralhar** (+2,4 ± 0,4), 6,0% com ele cortado (+2,7 ± 0,6). Joga-se descuidado: 8,1% → 10,9% / 11,6%. Ele embaralha em 27% das partidas (milado/descartado) e é conjurado em só 4%. **Disciplina de biblioteca (+4,9 pontos) vale o dobro do Kozilek.** |
| pacote de 5 trocas | mesa limpa até T8: **+4,6 ± 1,4** pontos (50,7% → 55,3%); até T10: +2,3 ± 0,9; deck-out −0,7 ± 0,5. Maior contribuição individual: Evolution Sage (+2,4) e Opulent Palace (+2,0); Bastion e Uprising não se distinguem de zero. As trocas **não se somam** (individuais somam +7,7). |
| **Master of Lake-town** (sem designar o corte) | ← Negate **+3,6 ± 1,3** (T8) · ← Strip Mine +2,2 ± 1,2 · ← Yavimaya Hollow +1,8 ± 0,7. O corte menos custoso, **em velocidade**, é Negate; o simulador não mede o valor de uma contramágica contra oponente real. Combo da Ascension: 2,2% → 3,4–4,2% das partidas. |
| **pacote de 5 + Master ← Negate** | T8 **+6,9 ± 1,4**, T10 +2,6 ± 0,9; resiliência T8 +3,6 ± 1,2. |

**Limite do medidor:** a mesa passiva cai por perda de vida (rad + Mindcrank/Konrad/Palantír + combate), não pelo tamanho das criaturas: cortar o Hardened Scales moveu os contadores em −7,5 mas **não** a velocidade (+0,3 ± 1,4). Por isso **este A/B não valoriza cartas de crescer contadores** (Terrasymbiosis, Corpsejack, Mutational Advantage…), e a lista Tier 2 **não foi simulada**.

## 1. Escopo e método

- **Janela:** coleções com data ≥ **2025-08-01** (Edge of Eternities em diante). EOE/EOC/EOS e promos têm exatamente essa data: **incluí e sinalizei** (Terrasymbiosis, Karn's Bastion,
  Tekuthal, Loading Zone…), porque o usuário já tem cartas do EOE e pode querer ignorá-las.
- **Filtro:** Scryfall `f:commander id<=bug date>=2025-08-01`, `unique=prints` → **5.474 impressões = 3.097 cartas únicas** legais em Commander dentro de B/G/U
  (1.595 com ao menos uma impressão inédita; 1.502 só reimpressões, mantidas porque a carta "sai" nesses produtos, ex.: Evolution Sage no ECC).
  Sets (nº de impressões): ECL 217, ECC 123, EOE 237, EOC 123, EOS 144, SOS 208, SOC 229, SOA 114, TLA 202, TLE 143, TMT 183, TMC 92, SPM 145, OM1 100, MSH 237, MSC 418,
  HOB 176, HOC 81, FRA 242, FRC 40, FDC 209, FIC 16, SLD 482, SLC 45, SLZ 261, PLST 305, SPG 36, MAR 53, AA1–4 56, e promos.
- **Excluí:** Alchemy digital (não legal), tokens, memorabilia. **Ainda não lançados hoje (2026-10-05):** The List (PLST, 2026-11-09), SLD de 2026-10-12/19, Star Trek (TRK/TRC, 2026-11-13) e
  Mystery Booster Commander (MBC, 2026-11-09): **246 cartas só aparecem em impressões futuras**, marcadas `NAO-LANCADA`. Star Trek e MBC ainda não são legais em Commander,
  então o filtro mostra poucas; consultei os dois set a set (§10).
- **Etiquetas por regex sobre o oráculo** (triagem; li o texto de cada uma): rad 2, proliferate 19, amplificadores 55, mill 95, gatilhos de contador 15, trample concedido 85, terrenos com 2+ de B/G/U 90.
  Listas completas com custo/tipo/set/preço/EDHREC: `resultados-ab/.../resumos/candidatas_por_etiqueta.md`. Para cada carta citada abaixo o oráculo está no
  `scryfall-cache/oracle-cache.json` e as rulings em `resumos/rulings_principais.md`.
- **Para cada candidata principal:** oráculo + rulings (Regra #3), motores do deck em que entra por script (`condicoes_por_script.txt`), Commander Spellbook antes/depois (com
  controle positivo e dois controles de corte de peça de combo, que **sumiram** como esperado), preço do Scryfall.

## 2. Proliferate (pedido do usuário)

Quem proliferar: cada carta com contador (19 com +1/+1, os rad counters de **todos** os jogadores, Bloodchief Ascension, Palantír, Urza's Saga, Ashiok).
Com Hardened Scales + Kami + Winding Constrictor em campo, **cada proliferate põe 4 contadores** por criatura com +1/+1 (**raciocinado**: replacement effects, ordem à sua escolha, CR 616.1).

| carta | custo / tipo | set · USD | veredito |
|---|---|---|---|
| **Evolution Sage** | 2G 3/2 | ECC 2,88 (PLST 2,36) | **Troca 1.** Motor de landfall (§5 da auditoria). |
| **Karn's Bastion** | terreno | EOC · 2,41 | **Troca 2.** Sem custo de slot de mágica. |
| Mutational Advantage | 1GU instant | SLD 7,73 (PIP 7,24) | Tier 2: protege "permanentes com contador" (quase todas as criaturas depois do 1º gatilho) **e** proliferate. Sobrepõe Heroic Intervention (que protege tudo). |
| Contentious Plan | 1U sorcery | SLD 5,29 (WAR 0,32) | Tier 2: cantrip + proliferate. |
| Tekuthal, Inquiry Dominus | 2UU 3/5 voa | EOC · 1,65 | Tier 2: dobra proliferate; só vale com ≥ 4 efeitos (hoje 1; pacote 3). Corpo 3/5 voador segura contadores. |
| Vraska, Betrayal's Sting | 4BB/P PW | ECC · 1,95 | Tier 2: `0`: compra + proliferate todo turno; `−2`: criatura vira Treasure (remoção + ramp). 6 de custo, sem proteção de PW. |
| Thrummingbird | 1U 1/1 voa | EOC · 0,26 | Tier 2: proliferate no dano de combate, mas 1/1. |
| Tezzeret's Gambit, Experimental Augury, Expansion Algorithm, Contagion Clasp, Surge Conductor, Lulu, Sword of Truth and Justice, Ripples of Potential, High Perfect Morcant | | | **Não escolhidas:** efeito único (Gambit/Augury/Algorithm), artefato lento (Clasp, 4+T), poucos artefatos (Conductor: 12 na lista), US$ 111 (Lulu), exige 3 Elfos para proliferar (Morcant: só 3 na lista). |

Nuances que mudam a decisão (**raciocinado**): proliferate é **escolha**: proliferar só os rad counters dos oponentes e **não** os seus; não proliferar Urza's Saga
(avança capítulo) nem -1/-1 do Glen Elendra.

## 3. Mill e rad (pedido do usuário)

O gatilho do Mothman conta **cada nonland milado de cada jogador**, no evento de mill de cada um. Dos 99 cards, ≈ 64% são não-terreno (63/99).

| carta | custo / tipo | set · USD | veredito |
|---|---|---|---|
| **Bruvac the Grandiloquent** | 2U 1/4 lendária | SLD 54,00 (JMP 42,24) | **Troca 3.** Dobra rad-mill, Ruin Crab (3→6), Memory Erosion/Psychic Corrosion (2→4), Mindcrank, Altar of the Brood. CR 701.17d: as cartas extras milladas contam. Caro. |
| **The Master of Lake-town** | 1BB 3/2 | HOB · 0,50 | **Troca 4.** Perda de vida → mill: rad counters (cada não-terreno tira 1 de vida → mais mill), Mindcrank, Ascension, Konrad, Palantír, Ballista. Morre: compra 1 por cemitério com 7+. **Spellbook: Bloodchief Ascension + Master = infinite mill** (2º parceiro da Ascension). Fontes de perda de vida na lista: 5 não-terrenos (Ascension, Mindcrank, Konrad, Palantír, Ballista) + 8 terrenos que cobram vida **de você** (3 fetches 1, 3 shocks 2, Waterlogged Grove 1, Agadeem 3) + os rad counters. Risco: simétrico, **te milla** a cada vida que você paga e nos **seus** rad counters. |
| Lo and Li, Royal Advisors | 2BB 3/3 | TLE · 0,21 | Tier 2: `{2}{U/B}`: alvo mill 4 (mana sink repetível) + contador em cada Advisor quando oponente milla/descarta (Danny Pink, Generous Patron e ele). |
| Oko, Lorwyn Liege // Shadowmoor Scion | 2U PW | ECL · 0,76 | Tier 2: `−1` mill 3 + permanente à mão; `−3` dois Elks 3/3 (corpos para o Mothman). Vira por `{G}`. |
| Grist, the Hunger Tide | 1BG PW | AA2 sem preço (MH2/PLST 0,40) | Tier 2: `+1` token Inseto + mill 1 (repete se Inseto: Icetill Explorer); **`−2` sacrifica e destrói criatura/PW** (remoção, que falta). |
| Trystan, Callous Cultivator | 2G 3/4 | ECL · 0,34 | Tier 2: auto-mill 3 ao entrar e a cada transformação (paga B/G por turno). Auto-mill sem rede (§7 da auditoria). |
| Maddening Cacophony, Traumatize, Kitsune's Technique | | SLD 5,91 · MAR 3,18 · TMT 0,84 | Tier 3: mill grande em 1 mágica (8 / metade / metade com Sneak). Num pod, 1 oponente. |
| The Ghoul, Gunslinger | 1BB 2/3 | SLD · 8,14 | Tier 3: rad ao morrer Zumbi/Mutante: só Mothman, Evolution Witness, Mirelurk Queen e Undead Alchemist na lista. |
| Hama, Captain N'ghathrod, Seedship Broodtender, Primal Witchstalker, Theorix Charm, Liliana the Repentant, Aftermath Analyst, Madame Hydra… | | | Boas em separado, mas **efeito de 1 uso** ou nicho (Horrors: só 2 na lista). Texto e preço em `candidatas_por_etiqueta.md`. |

## 4. Trample para o comandante (pedido do usuário)

**O que o deck já faz (ruling do Kodama):** criatura com contador (qualquer tipo), Equipamento ou Aura é *modificada* e ganha trample. Mothman recebe o 1º contador no
precombat main seguinte à entrada (gatilho dele próprio, X ≥ 1 com ≈ 64% de chance por carta milada) **ou imediatamente com Swiftfoot Boots** (já na lista).
Ponto único de falha: o Kodama (3 mana, 3/3, lendário).

| carta | custo / tipo | set · USD | papel |
|---|---|---|---|
| **Garruk's Uprising** | 2G encantamento | ECC/FDC · 0,40 | **Troca 5.** Trample para **todas** as criaturas; compra ao entrar com poder ≥ 4 (e uma vez ao entrar, se já controlar). Não é criatura: sobrevive a remoção. EDHREC 90. |
| Rancor | G aura | MAR 1,73 (PLST 1,07) | Tier 2: +2/+0 trample, volta à mão; 1 mana. Aura = modificada (Kodama também). |
| Biosynthic Burst | 1G instant | EOE · 0,28 | Tier 2: +1 contador, reach, trample, **indestrutível** até o fim do turno e desvira: protege o comandante em resposta. |
| Drix Fatemaker | 3G 3/2 (Warp 1G) | EOE · 0,16 | Tier 2: ETB +1/+1 num alvo (amplificado) e "tem trample quem tem +1/+1": trample imediato no Mothman. |
| Emil, Nev, Training Regimen, Badgermole, Surrak and Goreclaw, Dominion Supervisor (TRK) | | | **Redundantes com o Kodama** ("modificada" ⊃ "com contador"); só valem se o Kodama for removido. Surrak and Goreclaw ainda completa Altar of Dementia + Glen Elendra (§8). |

## 5. Contadores: amplificadores e compra por contador

Hoje: **3 efeitos "+1"** (Scales, Kami, Constrictor) e **0 dobradores**. Com um dobrador e os três "+1", cada contador do Mothman vira `(1 + 3) × 2 = 8` por criatura-alvo (**raciocinado**, ordem a seu favor).

| carta | custo | set · USD | nota |
|---|---|---|---|
| **Terrasymbiosis** | 2G | EOE · 9,33 | "Quando você põe contador +1/+1, compra essa quantidade (1×/turno)": com os três "+1" compra 4 de uma vez. Melhor fonte de compra do deck. Mesma data do EOE. |
| **Corpsejack Menace** | 2BG 4/4 | TMC · 0,37 | Dobra +1/+1 (CR/ruling: "twice that many"). Vai ser o dobrador mais barato. Spellbook: sem combo. |
| Loading Zone | 3G | EOE · 1,28 | Dobra todos os contadores nas suas criaturas; Warp {G}. Mesma data do EOE. |
| Doubling Season / Primal Vigor / Shang-Chi / Doc Samson / High Score / Solid Ground / Michelangelo | | | 28,36 · 6,09 · 0,65 · 0,28 · 1,25 · 1,78 · 2,35 — ver `candidatas_por_etiqueta.md`. Doc Samson e Solid Ground são "+1" + mana/corpo. |
| Berta, Wise Extrapolator / Ant-Man, Colony Commander / Innkeeper's Talent | | | Berta (mana ao receber contador + token com X contadores), Ant-Man (Inseto por contador, 1×/turno), Innkeeper's Talent (nível 3 dobra contadores **em jogador também**, US$ 24). |

Nenhum dos três principais entra no pacote **porque não achei um corte com o mesmo critério** (poucos vínculos de motor); eles são a primeira fila quando o usuário apontar o corte (o simulador de hoje não os valoriza: ver o limite do medidor no §0b).

## 6. Terrenos

- **Opulent Palace** (BGU, entra virado): **Troca 6**. Alivia G/U (triagem de pips).
- Tipados com ciclar (**raciocinado**): Festering Thicket (Pântano-Floresta), Fetid Pools (Ilha-Pântano), Rain-Slicked Copse (Floresta-Ilha), todos `ciclar {2}`, entram virados, são buscáveis por Misty/Delta/Verdant e **o ciclo manda terreno ao cemitério** (Gitrog compra, Icetill joga de novo).
- **Karn's Bastion:** a troca 2.
- **Fora do pacote:** checklands/snarls da janela (Woodland Cemetery, Hinterland Harbor, Drowned Catacomb, Necroblossom Snarl, Vineglimmer Snarl, Choked Estuary) entram desvirados na maioria das mãos, mas cada par de cores já tem shock + slowland na lista (BG: Overgrown Tomb + Undergrowth Stadium; GU: Breeding Pool + Rejuvenating Springs + Waterlogged Grove; UB: Watery Grave + Morphic Pool); ganho esperado pequeno **(raciocinado)**. Os 90 terrenos com 2+ cores estão em `candidatas_por_etiqueta.md`.

## 7. Lacuna fora do pedido: remoção pontual

A auditoria mostrou só 2 remoções pontuais de criatura + Ballista. Opções baratas pós-EOE em Sultai (todas fora do pacote): **Infernal Grasp** (1B instant, ECC/EOC/MAR/OMB/SOC, 0,26),
**Assassin's Trophy** (BG, 1,05), **Heartless Act** (1B, TLA, 0,25: destrói criatura *sem contador* ou tira até 3), **Bitter Triumph** (1B), **Beast Within** (2G). Todas são "crime" (mirar oponente) e
alimentam Deepmuck Desperado e Freestrider Lookout. Não escolhi o corte.

## 8. Combos e Bracket (Commander Spellbook, com antes/depois)

**Lista base:** 2 combos (Ascension + Mindcrank; Altar + Great Henge + Glen Elendra), ambos tardios (1,6–3,5% até T12 e 0,2–0,6%, sem tutor).

**Cada candidata do §2–§6 adicionada (sem cortar):** só 7 criam combo; **nenhuma tira**:
- **Master of Lake-town + Bloodchief Ascension** — infinite mill (a mesma estrutura de Mindcrank; Master é segundo parceiro). Com Master: Ascension + (Mindcrank **ou** Master) = **3,0% T6 · 4,0% T8 · 5,2% T10 · 6,4% T12** (só Mindcrank: 1,6–3,5%).
- **Altar of Dementia + Arwen / Bioengineered Future / Gorma / Surrak and Goreclaw** (com Glen Elendra): infinite mill/ETB (3 peças com 2 já na lista; **0,2–1,6%** até T10 mesmo com 5 completadores).
- **Dakmor Salvage + The Gitrog Monster**: auto-mill infinito **no cleanup** (excesso de mão): é armadilha que **te decka**, não vitória.
- **Syr Konrad + The Mindskinner** (ainda não lançada: The List 2026-11-09): quase infinito.

**Armadilhas de Bracket** (o Spellbook mostra que *uma* carta pós-EOE completa um combo de 2 peças com uma carta já na lista; não recomendei nenhuma):
Basking Broodscale + {Mazirek, Long Feng, Tarrian's Soulcleaver, Donatello the Brains, (Sadistic Glee, Blade of the Bloodchief, Ghost Lantern: The List)} = mana incolor/triggers infinitos;
Fathom Mage / Generous Patron + {Iron Man Armored Avenger, Lyla, Stark's Ingenuity} = compra infinita; Walking Ballista + Heroic Feast = dano infinito; Kami + Freed from the Real = mana infinita;
Ouroboroid + Sage of Hours = turnos infinitos; Psychic Corrosion + Peer into the Abyss = mill infinito. Chance de ter as duas peças (1 já na lista) com 1 completador: 1,6% (T6), 2,2% (T8); com 3: 4,3% / 5,7%; com 5: 6,4% / 8,3%.
**Se quiser ficar no Bracket 3, evite adicionar vários.** Tabela completa: `resumos/spellbook_resumo.md` (§5).

**Pacote de 5 trocas (Kozilek mantido):** base 2 → 2 combos; `novos: nenhum`; `sumiram: nenhum`; "quase" 134 → 143. Com o Master no lugar do Negate: 3 combos (+ Ascension + Master). *(O pacote antigo de 6 trocas, com Kozilek fora, está SUPERADO.)* Controle: cortar Mindcrank ou Glen Elendra (no lugar da Sage) **derruba** o combo correspondente de 2 para 1.

## 9. Fila para depois (Tier 2/3, sem corte designado)

Terrasymbiosis, Corpsejack Menace, Mutational Advantage, Contentious Plan, Lo and Li, Oko, Grist, Rancor, Biosynthic Burst, Tekuthal, Vraska, Drix Fatemaker, Trystan, Thrummingbird.
Se o usuário escolher cortes, a ordem de menos ligados (por `motores_por_script.txt`): Negate (1, a 5ª contramágica), Strip Mine (1), Yavimaya Hollow (1), Plaza of Heroes (1), Wave Goodbye (2).
**Eu não recomendo cortar terreno por mágica** (o §0b mediu só trocas terreno-por-terreno e o Master por Strip Mine/Hollow) (36 slots, 14 efeitos de terreno).

## 10. Ainda não lançadas (spoiler de hoje; texto pode mudar; ver `dados/pre_lancamento_cartas.json.xz`)

- **Homer, the Hermit** (BGU, MBC 2026-11-09, 3 mana): *Landfall — qualquer número de jogadores-alvo milam X, X = 2× nº de Caranguejos/Lagostas/Nautilos/Estrelas/Trilobitas que você controla.*
  Caranguejos na lista: Ruin Crab, Mirelurk Queen + o próprio Homer = X até **6 por terreno** (12 com Bruvac). Spellbook já o reconhece (quase com Hedge Shredder).
  É o achado mais específico para o deck; **ainda não é legal**.
- **Dominion Supervisor** (2G, TRK 2026-11-13): ETB +1/+1 num alvo e "criaturas com contador têm trample" (3º redundante com Kodama). **Captain Kathryn Janeway** (3G): terreno extra por turno e explora. **First Contact** (1G instant): mill 4.
  **Ceti Eel**, **Syndicate Liquidators**, **Support Mission**, **Greensleeves** (MBC), **The Weaver King**, **Blor the Impervious** (MBC).
- Preço e legalidade só quando lançar; rodar `scryfall-cache/sets/fetch_set.py trk trc mbc` de novo antes de analisar.

## 11. O que foi medido × raciocinado × NÃO verificado

- **Medido (script/API):** tudo de §1 (contagens, filtros, listas); auditoria; Spellbook (base, cada candidata, cada troca, pacote, controles); probabilidades hipergeométricas;
  curva e fontes antes/depois; rulings; preços (menor impressão do Scryfall).
- **Raciocinado:** quanto cada carta "vale" no jogo (compra/Mothman/proliferate com os três "+1"); quais cartas saem; riscos de auto-mill; escolha entre Garruk's Uprising e as demais; ordem de substituições.
- **Não verificado:** taxa de vitória, velocidade, necessidade de mana turno-a-turno, comportamento com oponentes reais, Bracket pelo texto oficial do dia, preço no mercado local, e, **para o §1–§10**, nenhum A/B (o §0b, escrito depois, mede o pacote de 5, o Master e o Kozilek no simulador; ver `goldfish-log.md` §5 para o que continua sem medir).

## 12. Tergrid, God of Fright // Tergrid's Lantern (pergunta do usuário, 2026-10-06)

> Pergunta: *"ela aproveita muito o mill, não? Ou apenas sacrifício e discard?"* Dados, scripts e como refazer: `resultados-ab/2026-10-06-tergrid-e-ferramenta-mill/LEIAME.md`.
> **A Tergrid NÃO foi implementada no motor do simulador**: abaixo só há oráculo, rulings, enumeração por script, Commander Spellbook e dois tetos medidos.

**Veredito (lido do oráculo; raciocinado): o mill NÃO dispara a Tergrid.** A frente só reage a "oponente **sacrifica** um permanente não-ficha ou **descarta** uma carta de permanente"; milar leva carta do topo da biblioteca ao cemitério, que não é sacrifício nem descarte. O que ela aproveita é sacrifício e descarte do oponente.

**Oráculo (Scryfall ao vivo, `dados/tergrid_carta.json`):** frente `{3}{B}{B}`, 4/5, Menace: *"Whenever an opponent sacrifices a nontoken permanent or discards a permanent card, you may put that card from a graveyard onto the battlefield under your control."* Verso `{3}{B}`, artefato lendário (Lantern): *"{T}: Target player loses 3 life unless they sacrifice a nonland permanent of their choice or discard a card. {3}{B}: Untap Tergrid's Lantern."*
**Rulings (`dados/tergrid_rulings.json`, lidas antes de concluir):** "permanent card" = artefato, criatura, encantamento, terreno ou planeswalker; vale qualquer cemitério; sacrificar/descartar **como custo** também dispara (o gatilho resolve antes); se a carta sair do cemitério antes, não volta; **o alvo da Lantern pode escolher perder 3 de vida mesmo tendo o que sacrificar ou descartar**.

**Cláusula × lista (script `enumera_tergrid.py`, 91 cartas distintas lidas do oráculo do repositório, não de memória):**

| a Tergrid precisa de… | cartas da lista que fazem isso | observação |
|---|---|---|
| oponente **sacrificar** | **1**: Kozilek, Butcher of Truth (Annihilator 4) | o script também listou Altar of Dementia: é sacrifício **meu** de criatura (falso positivo, conferido à mão) |
| oponente **descartar** | **0** | os 5 "discard" da lista (Boseiju, Bramble Familiar, Six, Takenuma, Zagoth Triome) são descartes meus |
| **mill** | 14 fontes (§3) | **não dispara** a frente |

- **Medido:** o Kozilek ataca ao menos 1 vez em **2,02%** das partidas no padrão (N = 10.000) e **2,24%** na resiliência, 1,33–1,40 ataques por partida em que ataca. É o **teto** das partidas em que a frente dispararia por sacrifício vindo do próprio deck (e ainda exigiria a Tergrid em campo: 5 + 10 de mana). O sacrifício/descarte que o oponente faz **por conta própria** (fetchland, Treasure, mão cheia) é jogo real e **não é modelado** (oponentes passivos).
- **O elo possível com o mill é só o verso (Lantern):** (1) se o alvo **escolher** perder vida, isso alimenta Mindcrank / Master of Lake-town / Ascension; a escolha é dele (ruling). (2) Mirar oponente é **crime** (ruling 2024-04): dispara Deepmuck Desperado (mila 3 em cada oponente) e Freestrider Lookout, 1×/turno cada. **Medido** (`crime_deepmuck.py`, N = 5.000): Deepmuck em campo em 14,7% das partidas (15,9% resiliência) e **57,0%** (64,0%) dos turnos dele sem crime. Isso é espaço de **0,27 turno por partida** para a Lantern: no máximo ≈ 0,27 × 3 cartas × oponentes vivos (≤ 3) ≈ **2,4 cartas por partida** contra 83,9 milladas no total (≤ ~3%; ≤ ~4% na resiliência), **mesmo que a Lantern estivesse sempre em campo junto** (ela é 1 carta entre 99 e custa `{3}{B}`; raciocinado: o ganho real fica uma fração disso).
- **Spellbook** (`dados/spellbook_tergrid.json`; nomes resolvidos, controle positivo Thassa's Oracle + Demonic Consultation apareceu, controles de corte derrubaram Ascension + Mindcrank e Altar of Dementia + Great Henge): Tergrid no lugar de Negate / Strip Mine / Yavimaya Hollow / Cold-Eyed Selkie → base 2 combos, **2 em todos**, **0 novo, 0 some**, 0 combo "quase" com Tergrid.
- **Bracket:** a Tergrid é **Game Changer** (campo `game_changer` do Scryfall); a lista passa de 1 (Fierce Guardianship) para 2. O limite de Game Changers por Bracket eu **não reli** no texto oficial hoje.

**Contra os motores do deck (Regra #4, raciocinado):** mill (não aciona a frente); contadores (a frente é só mais um corpo 4/5 que recebe contador, sem trample); rad/perda de vida (só a Lantern, se o alvo preferir perder vida); crime (Lantern, teto acima); Kozilek (Annihilator 4 + Tergrid em campo reanimaria os 4 permanentes não-ficha sacrificados, mas em ≤ ~2% das partidas; o Kozilek não tem haste, então só ataca no turno seguinte ao da conjuração). **Eu não recomendo incluí-la por causa do mill** (nenhum dos números acima sustenta isso). Se a ideia é a Tergrid contra mesas reais com fetchland, Treasure e descarte, essa é uma decisão de mesa que este goldfish não mede. Nada foi cortado ou adicionado.

**Medido × raciocinado × NÃO verificado:** medido = enumeração, frequência do Kozilek, teto do Deepmuck, Spellbook, `game_changer`. Raciocinado = a leitura do oráculo (mill ≠ sacrifício/descarte), o valor da Lantern, a recomendação. **Não verificado** = um A/B pareado da Tergrid (exigiria implementar a frente e o verso e uma chave `TERGRID_OPP_CHOICE` com o teto "o oponente sempre perde 3 de vida" e o piso "sempre sacrifica/descarta"), o comportamento de oponentes reais e o limite de Game Changers do Bracket.
