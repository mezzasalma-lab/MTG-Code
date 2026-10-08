# The Wise Mothman — Sultai — auditoria (2026-10-05; escopo verificado e não verificado no §8)

> Deck novo informado pelo usuário em 2026-10-05 (100 cartas; **o simulador foi construído depois desta auditoria** — `mothman_goldfish_v1.py`, `goldfish-log.md`; esta auditoria é anterior a ele e não foi reescrita).
> Lista: `lista.md` (nomes reais do Scryfall; original do usuário em `lista-original-usuario.txt`; nomes de capa em `nomes-de-capa.md`).
> Candidatas pós-EOE: `candidatas-pos-eoe.md`. Dados brutos, scripts e como refazer tudo:
> `resultados-ab/2026-10-05-candidatas-pos-eoe/LEIAME.md`.
> Cada número abaixo vem de um script em `orquestracao/` sobre o oráculo do `scryfall-cache/oracle-cache.json`
> (nunca de memória). Onde a frase é raciocínio e não medição, está marcado **(raciocinado)**.

## 1. Identidade de cor, legalidade, duplicatas — ✅

- 100 cartas (comandante + 99), singleton (só básicos repetem), **0 fora de B/G/U**, **0 não-legais** em Commander (`legalities.commander`).
- Cada linha foi resolvida **por set + nº de colecionador** (91 de 91 acharam), não por nome: seis nomes de capa (Universes Beyond / Secret Lair)
  são outras cartas (Regra #2). Tabela completa em `nomes-de-capa.md`:
  Aerith's Curaga Magic = **Heroic Intervention** · Dol Amroth = **Minamo, School at Water's Edge** · Mirelurk Hatchling = **Ruin Crab** ·
  Mothman Egg = **Mesmeric Orb** · The Party Tree = **The Great Henge** · We Want . . . A SHRUBBERY! = **Three Visits**.
  Overgrown Tomb (ECL 350) é um cartão reversível (as duas faces são a mesma carta).
- Os três itens mais importantes que só aparecem pelo nome real: **Ruin Crab** (landfall: oponentes milam 3), **Mesmeric Orb** (milla ao desvirar)
  e **The Great Henge** (peça do combo de 3 cartas, §6).

## 2. Terrenos e cores

**36 slots de terreno = 35 terrenos de face única + 1 MDFC (Agadeem)**; 63 não-terrenos. Básicos: 5 Forest, 4 Island, 3 Swamp.

| cor | fontes diretas | por busca (3 fetch + Fabled Passage) | total incondicional |
|---|---|---|---|
| U | 12 | 4 | **16** |
| B | 12 | 4 | **16** |
| G | 14 | 4 | **18** |

- **Command Tower** conta nas três (identidade do comandante) e as **3 fetches** + **Fabled Passage** contam nas três (Regra 6): Misty (Forest/Island),
  Polluted Delta (Island/Swamp) e Verdant Catacombs (Swamp/Forest) alcançam B, G e U porque a lista tem Breeding Pool, Watery Grave, Overgrown Tomb e
  Zagoth Triome com os subtipos certos. Condicional, não contada: **Plaza of Heroes** (cor só para magia lendária / cor entre lendários).
- **Incolores:** Strip Mine, Swarmyard, Yavimaya Hollow, Urza's Saga (4) + Plaza.
- **Entra virado** (conferido no oráculo): Bojuka Bog e Zagoth Triome sempre; Fabled Passage (o básico buscado entra virado e desvira com 4+ terrenos); Agadeem (paga 3 vida);
  3 shocks (pagam 2); Rejuvenating Springs, Undergrowth Stadium e Morphic Pool **entram desvirados com 2+ oponentes** (mesa de 4: ok; 1v1: virados);
  Shifting Woodland sem Forest. **Pagam vida:** Misty/Delta/Verdant (1), Waterlogged Grove (1 por uso), shocks (2), Agadeem (3).
- **Triagem de pips (NÃO é necessidade turno-a-turno, Regra 8):** cartas que exigem U = 21, B = 11, G = 29; com custo ≤ 2: U 6, B 4, G 13.
  Razão fontes/cartas: U 0,76 · B 1,45 · G 0,62. **(raciocinado)** G e U são as cores apertadas e B tem sobra: trocar um terreno só-B (Bojuka Bog) por
  um terreno G/U ou tricolor vai na direção certa. Não medido turno-a-turno na época desta auditoria (o simulador veio depois).
- Mesmo com 36 slots, o deck tem muita razão de ser **land-heavy**: 14 efeitos além da jogada normal botam terreno em campo (§5). Não recomendo cortar terreno.

## 3. Curva (não-terrenos, X = 0)

`cmc: 0:1 · 1:8 · 2:20 · 3:17 · 4:9 · 5:5 · 6:1 · 9:1 · 10:1` — média **2,94**; 29 de 63 custam ≤ 2. Topo: Great Henge (9, cai com o maior poder), Kozilek (10),
Muldrotha (6). Curva baixa e coerente com o deck (mill/triggers a baixo custo).

## 4. Categorias (conferidas à mão contra o oráculo; o script de regex só tria)

| categoria | quantas | quais |
|---|---|---|
| Ramp/fixação não-terreno | ~10 | Sol Ring, Nature's Lore, Three Visits (buscam **Forest**, inclusive Breeding Pool/Overgrown Tomb/Triome), Gyre Sage (G por contador), Kami of Whispered Hopes (X = poder), Bramble Familiar, Basking Broodscale (Spawn quando recebe contador), The Great Henge (GG), Freestrider Lookout, Kodama (terreno por dano) |
| Compra | muitos gatilhos | The Gitrog Monster, Hollowmurk Siege (modo Sultai: 1×/turno), Danny Pink, Fathom Mage, Generous Patron, Mirelurk Queen (1×/turno), Pollywog Prodigy, Great Henge, Palantír, Psychic Corrosion, Cold-Eyed Selkie, Soul-Guide Lantern, Smuggler's Surprise, Kozilek |
| Remoção pontual | **fraca** | V.A.T.S. (split second, toughness igual), Tear Asunder (com kicker: qualquer não-terreno), Walking Ballista, Boseiju/Cankerbloom/Strip Mine (artefato/encantamento/terreno) |
| Varredores | 3 | Toxic Deluge, Nuclear Fallout (também dá rad), Wave Goodbye (devolve as sem contador) |
| Contramágicas | 6 | Negate, Arcane Denial, Fierce Guardianship, Didn't Say Please (também milla 3), An Offer You Can't Refuse, Glen Elendra Archmage |
| Proteção | 4 | Heroic Intervention, Smuggler's Surprise (modo hexproof/indestrutível poder ≥ 4), Swiftfoot Boots, Plaza of Heroes (lendário) |
| Recursão | 5 | Muldrotha, Six (retrace de permanente no cemitério), Icetill Explorer (joga terreno do cemitério), Evolution Witness, Agadeem |
| Vitória | várias | Mothman crescendo (voa) + doubladores; mill do oponente (Ruin Crab, Memory Erosion, Psychic Corrosion, Mindcrank, Altar of the Brood); rad counters; Bloodchief Ascension + Mindcrank; Altar of Dementia + Great Henge + Glen Elendra; Palantír; Kozilek; Walking Ballista |

**Lacuna estrutural (raciocinada):** remoção pontual de criatura. São 2 cartas de verdade (V.A.T.S., Tear Asunder com kicker) + Ballista + 3 varredores; o
típico é 8–10 (skill, estrutura padrão). Todas as opções baratas em Sultai da janela pós-EOE estão em `resultados-ab/.../resumos/candidatas_por_etiqueta.md`
e no §7 de `candidatas-pos-eoe.md`.

## 5. Motores do deck (enumerado por script: `resumos/motores_por_script.txt`, `condicoes_por_script.txt`)

- **E1 — mill dos dois lados.** Atingem oponente (14): Altar of Dementia, Altar of the Brood, Ashiok, Deepmuck Desperado, Didn't Say Please, Memory Erosion,
  Mesmeric Orb, Mindcrank, Psychic Corrosion, Rampant Frogantua, Ruin Crab, Syr Konrad, Undead Alchemist, Zellix; mais **rad counters** (Mothman, Mirelurk Queen,
  Nuclear Fallout). Auto-mill: Six, Icetill Explorer, Hedge Shredder, Smuggler's Surprise, Fetch Quest, Takenuma, Palantír, Orb.
- **E2 — pagam "milled".** Mothman (nonland: contador em até X criaturas), Mirelurk Queen (compra + contador, 1×/turno), Zellix (criatura milada: Horror 1/1),
  Undead Alchemist (criatura da biblioteca do oponente: Zumbi), Syr Konrad (criatura que vai ao cemitério: 1 de dano), Bloodchief Ascension, Kozilek (ver §7).
- **E3 — contadores.** Colocam +1/+1 (19 cartas, lista no script). Amplificam: Hardened Scales (+1), Kami (+1), Winding Constrictor (+1 de **cada** tipo;
  também nos **rad counters que você recebe**). Pagam: Hollowmurk Siege, Danny Pink, Fathom Mage, Generous Patron, Herd Baloth, Basking Broodscale,
  Evolution Witness, evolve (Gyre Sage, Pollywog, Fathom Mage). **Não há dobrador** (só os três "+1") e **só 1 efeito de proliferate** (Cankerbloom, sacrifício único).
- **E4 — terreno.** 13 fontes além da jogada normal (script) + Rampant Frogantua: 3 fetches, Fabled Passage, Nature's Lore, Three Visits, Kodama,
  Freestrider Lookout, Hedge Shredder, Icetill Explorer, Gitrog, Muldrotha, Fetch Quest. Pagam: Ruin Crab (landfall), Gitrog (terreno ao cemitério = compra),
  Hedge Shredder (terreno milado vai ao campo).
- **E5 — interação/proteção** (§4) e **E6 — combos** (§6).

### Regras que moldam o Mothman (lidas na ruling oficial, `resumos/rulings_principais.md`)

1. **"Up to X targets" = no máximo 1 contador por criatura-alvo.** X maior que o nº de corpos é desperdício; 32 criaturas na lista (+ tokens) — corpos importam.
2. As cartas são milladas todas de uma vez: o gatilho dispara **uma vez** por evento de mill, com X = nº de não-terrenos daquele evento. Cada jogador mill-a
   no **seu** precombat main (rad), então com N jogadores com rad counters você recebe N gatilhos por rodada.
3. **Proliferate interage com rad counters** (ruling do Mothman). O que dá para escolher: proliferar só os rad counters dos oponentes (mais mill e perda de vida
   deles, mais gatilhos para você) e **não** os seus.
4. **Kodama** dá trample a criatura **modificada**: contador de qualquer tipo, Equipamento ou Aura (ruling). O Mothman fica modificado ao receber seu primeiro contador
   (no precombat main seguinte à entrada) **ou imediatamente se equipar a Swiftfoot Boots** (que já está na lista: trample + haste + hexproof).
5. Ordem de substituições de contador é escolha de quem controla (CR 616.1, rulings de Scales/Kami): com +1 e um dobrador, aplique os "+1" antes e dobre depois.
6. Mill duplicado por substituição (Bruvac) conta todas as cartas milladas (CR 701.17d trata de mais de uma carta milada por substituição).

## 6. Combos e Bracket

- **Game Changers: 1** (Fierce Guardianship, `game_changer` do Scryfall). Sem tutor irrestrito, sem destruição em massa de terreno, sem turno extra.
  Pela tabela de Brackets da skill (não reli o texto oficial do Commander RC hoje) o deck é **Bracket 3**.
- **Commander Spellbook** (`POST /find-my-combos`, com **controle positivo**: a lista com Thassa's Oracle + Demonic Consultation devolve o combo deles):
  1. **Bloodchief Ascension + Mindcrank** — mill infinito + perda de vida quase infinita. Precisa de 3 contadores de busca na Ascension e de uma forma de o oponente perder vida.
  2. **Altar of Dementia + The Great Henge** (+ **Glen Elendra Archmage** como o "Persist Creature") — auto-mill infinito, ETB/morte infinitos (o sacrifício devolve o persist, a Henge
     põe +1/+1 e compra, o −1/−1 se cancela). Com Syr Konrad em campo vira dano infinito.
- **Probabilidade real (Regra 7)**, só compras normais, 99 cartas, 7 + 1 por turno: Ascension + Mindcrank **1,6% até T6 · 2,2% T8 · 2,8% T10 · 3,5% T12**;
  Altar + Henge + Glen Elendra **0,2% · 0,3% · 0,4% · 0,6%**. Nenhum é combo cedo: **não muda o Bracket**. (Antes disso: mana, 3 contadores na Ascension, sobreviver.)
- Na época desta auditoria o deck não tinha simulador; **hoje o simulador executa** Ascension + Mindcrank/Master (≈ 2,2% das partidas, ver `goldfish-log.md` §1) e o laço Altar + Henge + Glen (limitado pela biblioteca, ≈ 0,7%).
- **Riverchurn Monument (2026-10-07):** não cria combo novo; 8 combos de 2 peças "quase" (Traumatize, Maddening Cacophony, Jidoor, Singularity Rupture, Cut Your Losses, Terisian Mindbreaker, Fleet Swallower, Kitsune's Technique), nenhuma na lista. Pasta: `resultados-ab/2026-10-07-riverchurn-monument/`.
- **Jace, Wielder of Mysteries (2026-10-07):** não cria combo novo; 12 combos de 2 peças "quase" (Demonic Consultation, Divining Witch, Enter the Infinite, Griselbrand, Hermit Druid, Leveler, Mirror of Fate, Oath of Druids, Paradigm Shift, Phyrexian Devourer, Tainted Pact, Thought Lash), nenhuma peça na lista. Pasta: `resultados-ab/2026-10-07-jace-no-lugar-do-kozilek/`.
- **Pacote Horrigan + Branching Evolution e 7 remoções candidatas (2026-10-08):** 99 nomes reconhecidos, controles ok; o pacote exato (−Offer −Negate +Horrigan +Branching) não cria nem derruba combo; Drown in the Loch, Assassin's Trophy, Putrefy, Beast Within, Deadly Rollick, Atomize e Casualties of War também não. "Quase" novo: **Branching Evolution + Walking Ballista + (Vigor ou Rite of Passage)**, nenhuma das duas na lista (armadilha de Bracket a vigiar se alguém sugerir uma delas). Pasta: `resultados-ab/2026-10-08-pacote-e-interacao/`.
- **Armadilhas de Bracket** (Spellbook "quase": uma carta pós-EOE completaria um combo de 2 peças com uma carta que já está na lista) estão no §8 de `candidatas-pos-eoe.md`.

## 7. Riscos e fraquezas

Medido (por script/Spellbook): proliferate = 1 efeito; amplificadores = 3 (todos "+1"); remoção pontual = 2 + Ballista; 1 Game Changer; 0 dobradores.
**(raciocinado, sem simulação):**
- **Auto-mill sem rede.** Pelo menos 8 fontes de auto-mill (Six 3/ataque, Icetill 1/terreno, Hedge Shredder 2/ataque, Smuggler's 4, Fetch Quest 7, Takenuma 3, Palantír X,
  Orb 1 por permanente desvirado) numa biblioteca de 99; a única recuperação é o Kozilek (embaralha o cemitério de volta, mas **só quando ele vai ao cemitério**: milado, descartado, morto ou contramagicado).
  Os rad counters **seus** também milam e tiram vida (1 por não-terreno).
- **Kozilek é o seguro contra morrer por auto-mill** (correção do usuário, 2026-10-05): ao ir ao cemitério de qualquer lugar (milado, descartado, morto, contramagicado) ele embaralha o cemitério
  na biblioteca. Num deck de auto-mill ele é milado com probabilidade ≈ cartas milladas/99 (15 → 15%, 30 → 30%, 45 → 45%, 60 → 61%), justamente quando o risco de decking sobe. O custo (zera Six/Muldrotha/Icetill/Agatha)
  existe, mas é o preço do seguro. **Não é corte.** Quanto ele salva foi medido no simulador (`mothman_goldfish_v1.py`): o embaralhar tira ≈ 2,4 pontos de 5,7% de deck-out (jogando cuidadoso) — `goldfish-log.md` §2.
- **Proteção do comandante**: Swiftfoot Boots (hexproof), Heroic Intervention, Smuggler's Surprise (só poder ≥ 4), Glen Elendra (contra mágica). Nada contra varredor que exila / −X/−X
  além dos counters do próprio deck.
- **Dois pontos únicos de falha**: Kodama (trample) e Hardened Scales/Constrictor/Kami (amplificação) — redundância baixa.

## 8. O que NÃO foi verificado (Regra 7: escopo declarado, nada de "completo")

- **Esta auditoria é anterior ao simulador.** Nada nela é taxa de vitória nem "colocar a carta X melhora Y%"; as medições estão em `goldfish-log.md` (A/B pareado do pacote de 5 trocas, do Master e do Kozilek) e `candidatas-pos-eoe.md` §0b.
- Pips: só triagem agregada; **não** foi calculada a necessidade de mana turno-a-turno.
- Sem oponente real: rad counters/mill dos oponentes, bloqueios e remoção deles não entram.
- Bracket: tabela da skill, não o texto oficial do dia.
- Preços: Scryfall (`prices.usd`, menor impressão), não o mercado local.
- Não houve leitura cláusula-a-cláusula das 100 cartas contra um motor de simulação (não há motor). A leitura de oráculo e rulings cobriu as cartas centrais (`resumos/rulings_principais.md`).
