# The Wise Mothman — checklist cláusula-a-cláusula do simulador (2026-10-05)

Simulador: `mothman_goldfish_v1.py` (construído do zero em 2026-10-05, a pedido do usuário: *"Sim, construa o simulador do Mothman — leve em conta que ele dá Counters toda vez que alguém milla cartas"*).
Oráculo e rulings de **todas** as cartas: lidos do `scryfall-cache/oracle-cache.json` e de `resultados-ab/2026-10-05-candidatas-pos-eoe/dados/lista_bruto.json.xz` (JSON do Scryfall + `rulings`, 276 rulings), **não de memória** (Regras #1 e #3).
Cada linha: cláusula do oráculo → onde está no código → **status** → teste dirigido (`testes/testes_dirigidos.py`, 134 testes). Legenda: ✅ implementado e testado · 🐛 achado/corrigido **durante esta construção** · 📊 estrutural (depende de estado de OPONENTE que o goldfish não modela; cláusula citada, nunca "valor baixo").

## 0. Escopo desta auditoria (Regra #7 — nada de "completo")

**Varrido, com método:** (a) as 91 cartas distintas da lista + 6 candidatas do pacote, cláusula a cláusula contra o oráculo e as rulings, com teste dirigido por cláusula (134 testes, cada um confere que o número esperado é > 0); (b) conceitos compartilhados (§3); (c) ordem de fases do turno (§4, Regra #6);
(d) varreduras mecânicas da Regra #10 (`resultados-ab/2026-10-05-simulador-v1-validacao/`): entrada de cada um dos 29 terrenos contra o oráculo, fetch real, jogar terreno ≠ magia, landfall em todo ponto de entrada (7.275 terrenos = 7.275 chamadas), estado por instância, AST de sets (5 candidatos lidos; 1 correção), determinismo (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos: 0 divergentes); (e) regressão 20.000 × 2 modos em 12 configurações sem exceção (código `91b1a3d`).
**NÃO varrido:** caminhos de conjuração fora da mão além de Muldrotha/Six/aventura (não há outros no deck); interação entre **combinações** de redutores de custo (só The Great Henge reduz); política de jogo contra um humano real (a IA é uma heurística declarada, §5); oponentes reais (convenção do repositório: passivos no modo padrão; modo de resiliência é uma amostra estatística, não uma mesa real).

## 1. Convenções declaradas (premissas, não ausência de checagem)

| tema | convenção |
|---|---|
| mesa | 4 jogadores (3 oponentes). Oponentes passivos: biblioteca de 99 (37 terrenos / 28 criaturas / 34 outras, **tipos, não nomes**), vida 40, mão 7, magias por turno em probabilidade (0/1/2), `OPP_SPELLS_PROB`; **sem tabuleiro** (todo atacante conecta). |
| o que **é** real do oponente | biblioteca, cemitério (por tipo), vida, rad counters, compra (perde ao comprar de biblioteca vazia), Mesmeric Orb ao desvirar, Memory Erosion/Pollywog por magia conjurada, contramágicas minhas contra magias deles (MV ≥ 3), 21 de dano de comandante. |
| efeito que precisa de **alvo no tabuleiro** do oponente | metrica proxy `interaction_plays` quando `target_available` (`OPP_TARGET_PROB` = 0,7, a partir do T3); o efeito **próprio** (terreno que vai ao meu cemitério, crime) é real. Citado em cada 📊. |
| modo de resiliência | `simulate_one_with_interaction`: mesmas 7 categorias dos outros decks (remoção, ataque, discard, wipe de criatura/artefato/encantamento, graveyard wipe 1×, graveyard snipe, counter no comandante) + **defesas reais deste deck** (contramágicas/Glen, Heroic Intervention, Smuggler's, Boots, regeneração, Plaza, Angel of Suffering). |
| mulligan | London; **1º grátis** (mesma convenção dos outros simuladores); o jogador **escolhe** as cartas do fundo (CR 103.5). |
| "uma vez a cada turno" | conta **por turno de qualquer jogador** (`turn_id`), não só os meus (Mirelurk Queen, Deepmuck, Freestrider, Hollowmurk Sultai, Danny Pink, Terrasymbiosis). |
| biblioteca | **guarda de self-deck** (`library_budget`): mills/compras *opcionais* e atacantes a mais (por causa do Mesmeric Orb) só se a biblioteca aguenta; compras *obrigatórias* (Danny, Henge) são evitadas pela escolha de alvos do Mothman ("up to X") e por não conjurar a peça. Chave `SELF_MILL_GUARD_ENABLED`; o A/B mede com ela desligada como controle. |

## 2. Cartas (oráculo → código)

### Comandante
| carta | cláusula | código | status | teste |
|---|---|---|---|---|
| **The Wise Mothman** | Flying | tag `flying` (sem bloqueio modelado: irrelevante) | ✅ | — |
| | "enters or attacks, each player gets a rad counter" | `apply_etb` (entrada, qualquer caminho); `combat_step` (ataque); `give_rad` | ✅ | `mothman_etb_da_rad_em_todos`, `mothman_ataque_da_rad` |
| | "whenever one or more nonland cards are milled, +1/+1 counter on each of up to X target creatures, X = nonland cards milled" | `mill_event` → `mothman_trigger`; um gatilho por evento mesmo com vários jogadores (ruling 2024-03-08); cada alvo recebe UM contador, passando pelos substituidores; `choose_counter_targets` ("up to": pula alvo que dispararia compra obrigatória além do orçamento) | ✅ | `mothman_mill_oponente_poe_X_contadores`, `mothman_varios_jogadores_um_gatilho`, `mothman_so_terrenos_nao_dispara`, `mothman_X_maior_que_alvos...` |
| | alvo = criatura de oponente (crime; Generous Patron compra) | `OPP_CREATURE_TARGETS` (padrão 0) | 📊 "target creatures" do oponente: tabuleiro não simulado | — |
| (inerente) | rad counters: no main 1 de cada jogador, mila N; por cada não-terreno: −1 vida, −1 rad (CR 728.1) | `rad_trigger_self`, `rad_trigger_opp` (via `before_triggers`: a perda de vida vem antes dos gatilhos de "milled") | ✅ | `mothman_rad_oponente_no_main_dele`, `rad_proprio_milla_e_perde_vida`, `opp_rad_zero_nao_faz_nada` |

### Terrenos (29 do `CARD_DB`, 27 da lista; entrada de cada um conferida contra o oráculo por script: `varredura_mecanica.txt`, 0 divergências)
| carta | cláusulas | código | status | teste |
|---|---|---|---|---|
| Forest / Island / Swamp | `{T}: add` | `produces` | ✅ | varredura de entrada |
| **Bojuka Bog** | entra virado; ETB: exila cemitério de jogador-alvo; `{T}: B` | `land_enters_tapped` (tag `etb_tapped`), `bojuka_bog_etb` (alvo = oponente com mais cartas; **crime**, interação) | ✅ | `bojuka_bog_exila_cemiterio_de_oponente_e_e_crime` |
| **Boseiju, Who Endures** | `{T}: G`; canal `{1}{G}` (−1 por lendária que controlo): destruir artefato/encantamento/terreno não básico de oponente | `act_boseiju` (descarta → cemitério: Gitrog/Icetill; **só com alvo**, ruling 2022-02-18) | ✅ canal e custo; 📊 "destroy target ... an opponent controls" (alvo de oponente: proxy) | `boseiju_canal_e_interacao_proxy` |
| Breeding Pool / Overgrown Tomb / Watery Grave | choque: paga 2 de vida ou entra virado; tipos básicos | `land_enters_tapped` (vida < 10 → virado), `land_cost_life` | ✅ (política: paga se a vida permite) | `shocklands_pagam_2_de_vida_ou_entram_virados` |
| Command Tower | mana na identidade do comandante (B/G/U) | `produces {B,G,U}` | ✅ | varredura |
| **Fabled Passage** | `{T}`, sacrifica: básico virado; se 4+ terrenos, desvira | `crack_fetch` (fabled): conta o terreno buscado (ruling 2020-06-23) | ✅ | `fabled_passage_desvira_com_4_terrenos` |
| **Minamo** | `{T}: U`; `{U},{T}`: desvirar lendário | `minamo_untap` → Zellix 2ª ativação (`act_zellix_minamo`), Cauldron (`act_cauldron_minamo`), Great Henge para vida (`act_minamo_henge`; saldo de mana ≈ 0) | ✅ | `minamo_desvira_zellix_segunda_ativacao` |
| Misty Rainforest / Polluted Delta / Verdant Catacombs | `{T}`, 1 vida, sacrifica: busca por **subtipo** | `crack_fetch` (`FETCH_TYPES`; a busca acontece **depois** dos gatilhos do cemitério, p.ex. a compra da Gitrog) | ✅ 🐛 (busca antes do gatilho levantava `ValueError` em 3/6.000) | `fetch_real_...`, `fetch_com_gitrog_busca_depois_da_compra` |
| Morphic Pool / Rejuvenating Springs / Undergrowth Stadium | entra virado a menos que haja 2+ oponentes (contagem atual) | `land_enters_tapped` (`slow_opp`); por efeito que põe virado, não desvira (ruling) | ✅ | `slowland_entra_desvirada_com_2_oponentes` |
| **Plaza of Heroes** | `{T}: C`; `{T}`: qualquer cor só p/ magia lendária; `{T}`: qualquer cor **entre meus permanentes lendários**; `{3},{T}`, exilia: lendária ganha hexproof+indestrutível | `mana_sources` + `legendary_colors` 🐛 (a 3ª habilidade faltava); a 4ª em `try_protect_from_destroy` (resiliência) | ✅ | `plaza_cor_dos_lendarios` |
| **Shifting Woodland** | entra virado sem Floresta; `{T}: G`; delirium `{2}{G}{G}`: vira cópia de permanente do cemitério até o fim do turno (sem ETB) | `land_enters_tapped`; `act_woodland` (copia Muldrotha/Icetill/Henge/Kami/Constrictor se o efeito age agora; `copy_of` por `eff_name`/`eff_card`; reset no cleanup) | ✅ (política de escolha: subconjunto; a regra aceita qualquer permanente) | `woodland_delirio_copia_muldrotha`, `shifting_woodland_entra_virado_sem_floresta` |
| **Strip Mine** | `{T}: C`; `{T}`, sacrifica: destruir terreno | `act_strip_mine` (vai ao cemitério → Gitrog/Icetill; **crime**) | ✅ cemitério/crime; 📊 "destroy target land" (alvo de oponente: proxy) | `strip_mine_proxy_com_pagador_de_crime` |
| Swarmyard | `{T}: C`; regenerar Inseto/Rato/Aranha/Esquilo | `regenerate_sources` (Mothman e Icetill são Insetos) | ✅ só com destruição de oponente (resiliência); modo padrão: nenhum efeito de "destroy" existe | `perdas`: protecoes `regenerate` na regressão de resiliência |
| **Takenuma** | `{T}: B`; canal `{3}{B}` (−1 por lendária): mila 3, devolve criatura/PW (escolhida **depois** do mill, ruling) | `act_takenuma` | ✅ | `takenuma_canal_milla_3_e_devolve_criatura` |
| **Urza's Saga** | I: `{T}: C`; II: `{2},{T}`: Construct (0/0, +1/+1 por artefato); III: busca artefato de **custo {0}/{1}** (Sol Ring, Altar of the Brood, Lantern; Ballista **não**: custo `{X}{X}`, ruling 2021-06-18); sacrifica | `saga_add_lore` (entrada + início do main 1), `act_saga_construct`, `urza_chapter_iii` | ✅ | `urza_saga_capitulos`, `urza_saga_constroi_construct_com_poder_por_artefato` |
| **Waterlogged Grove** | `{T}`, 1 vida: G/U; `{1},{T}`, sacrifica: compra | `mana_sources` (`life=1`), `act_waterlogged_grove` | ✅ | `waterlogged_grove_...` (2 testes) |
| Yavimaya Hollow | `{T}: C`; `{G},{T}`: regenerar criatura | `regenerate_sources` | ✅ resiliência (idem Swarmyard) | — |
| **Zagoth Triome** | entra virado; ciclar `{3}` | `act_triome_cycle` (cemitério: Gitrog/Icetill) | ✅ | `triome_ciclo_compra` |
| **Agadeem's Awakening // Agadeem** | MDFC: lado terreno (3 de vida ou entra virado; `{T}: B`) / lado feitiço `{X}{B}{B}{B}`: devolve criaturas de MV **diferentes** ≤ X | `play_land_phase` (terreno só se me faltam terrenos; jogável do cemitério: ruling "land from among a group"), `act_agadeem`/`agadeem_x`; na biblioteca/cemitério conta como feitiço (`is_land_card_name`) | ✅ | `agadeem_feitico_devolve_criaturas_de_mv_diferentes` |

### Criaturas
| carta | cláusula | código | status | teste |
|---|---|---|---|---|
| **Angel of Suffering** | Flying; dano que seria causado a você é prevenido e você mila o dobro | `try_smart_opponent_attack` (resiliência: previne e `mill_event` 2×) | ✅ resiliência; 📊 modo padrão (não há dano ao jogador) | regressão de resiliência (`angel_prevented_total`) |
| **Basking Broodscale** | `{1}{G}`: adapt 1; ao receber contador +1/+1, pode criar Spawn | `act_adapt`, `on_counters_placed` | ✅ | `broodscale_spawn_e_adapt` |
| **Bramble Familiar // Fetch Quest** | `{T}: G`; `{1}{G},{T}`, descarta: volta à mão; aventura `{5}{G}{G}`: mila 7, põe criatura/encantamento/terreno em campo | `mana_sources`; `act_bramble_refill` (descarta o Kozilek); `resolve_fetch_quest` + `adventure_exile` | ✅ | `fetch_quest_milla_7_...` |
| **Cankerbloom** | `{1}`, sacrifica: destruir artefato / destruir encantamento / proliferate | `act_cankerbloom` (proliferate se `proliferate_value ≥ 6`) | ✅ proliferate; 📊 os 2 destroy (proxy com pagadores de crime) | `cankerbloom_sacrifica_e_prolifera` |
| Cold-Eyed Selkie | Islandwalk; dano a jogador: compra tanto | `combat_step` (compra opcional: guarda de biblioteca) | ✅ compra; 📊 islandwalk (sem bloqueio) | `selkie_compra_igual_ao_dano` |
| **Danny Pink** | Mentor; criaturas têm "1ª vez por turno que ganham contador: compra" | `combat_step` (mentor), `on_counters_placed` (por `turn_id`) | ✅ 🐛 (a contagem era por turno meu) | `danny_pink_...`, `danny_mentor_...` |
| Deepmuck Desperado | crime: cada oponente mila 3 (1×/turno) | `commit_crime` | ✅ | `deepmuck_crime_milla_3_uma_vez_por_turno` |
| **Evolution Witness** | `{1}{G}`: adapt 2; ao receber contador: devolve permanente do cemitério | `act_adapt`, `evolution_witness_return` | ✅ | `evolution_witness_adapt_devolve_permanente` |
| **Fathom Mage** | Evolve; compra **por contador** (ruling) | `place_counters`/`on_counters_placed` | ✅ | `fathom_mage_compra_por_contador` |
| Freestrider Lookout | crime: olha 5, terreno virado (1×/turno) | `freestrider_trigger` | ✅ | `freestrider_olha_5_...` |
| **Generous Patron** | ETB support 2; contador em criatura de oponente: compra | `apply_etb` | ✅ support; 📊 2ª cláusula (criatura de oponente) | `generous_patron_apoia_2_outras_criaturas` |
| **Glen Elendra Archmage** | Flying; `{U}`, sacrifica: anular magia não-criatura; Persist | `respond_to_opp_spell`, `remove_permanent` (persist volta com −1/−1; Constrictor +1; Henge cancela) | ✅ | `glen_persist_...`, `glen_elendra_contramagica_com_persist` |
| Gyre Sage | Evolve; `{T}`: G por contador | `mana_sources` | ✅ | `gyre_sage_mana_por_contador` |
| Herd Baloth | contador: pode criar Beast 4/4 | `on_counters_placed` | ✅ | `herd_baloth_ficha_besta_com_contador` |
| **Icetill Explorer** | terreno extra; joga terrenos do cemitério; landfall: mila 1 | `land_drops_available`, `graveyard_land_candidates`, `landfall` | ✅ | `icetill_landfall_...` |
| **Kami of Whispered Hopes** | +1 contador (aditivo); `{T}`: X mana de uma cor, X = poder | `counter_modifiers`, `mana_sources` (bundle) | ✅ | `mothman_scales_constrictor_kami_somam`, `kami_mana_...` |
| **Kodama of the West Tree** | modificadas têm trample; dano a jogador de modificada: básico virado | `is_modified` (contador de **qualquer** tipo, Equipamento), `combat_step` | ✅ | `kodama_dano_de_combate_...` |
| **Kozilek, Butcher of Truth** | ao conjurar: compra 4 (resolve mesmo anulada); Annihilator 4; ao ir a um cemitério de qualquer lugar: embaralha o cemitério na biblioteca | `resolve_spell`; `kozilek_shuffle` (milado, descartado, sacrificado; **e** cada criatura que sai do cemitério pinga Konrad); chave `KOZILEK_SHUFFLE_ENABLED` | ✅; 📊 Annihilator (sacrificar permanentes do oponente) | `kozilek_milado_embaralha_cemiterio`, `kozilek_descartado_...`, `kozilek_conjurado_compra_4` |
| **Mirelurk Queen** | ETB: jogador-alvo 2 rad (crime se oponente); milled: compra + contador (1×/turno) | `apply_etb`, `mill_event` | ✅ | `mirelurk_queen_uma_vez_por_turno`, `once_each_turn_zera_...` |
| **Muldrotha** | 1 terreno + 1 magia permanente de cada tipo do cemitério por turno | `graveyard_cast_options`, `graveyard_land_candidates` | ✅ | `muldrotha_um_de_cada_tipo_por_turno` |
| **Ouroboroid** | início do combate: X contadores em cada criatura, X = poder (calculado uma vez) | `beginning_of_combat` | ✅ | `ouroboroid_poe_X_em_cada_criatura` |
| **Pollywog Prodigy** | Evolve; magia não-criatura de oponente com MV < poder: compra | `opponent_turn` (antes de eu decidir anular, ruling) | ✅ | `memory_erosion_e_pollywog_no_turno_do_oponente` |
| **Rampant Frogantua** | Trample; +10/+10 por jogador que perdeu; dano a jogador: mila tanto (opcional) e terrenos entram virados | `power`, `combat_step` 🐛 (mill **tudo ou nada**, ruling) | ✅ | `frogantua_...` (3 testes) |
| **Ruin Crab** | landfall: cada oponente mila 3 | `landfall` | ✅ | `ruin_crab_landfall_milla_3_cada_oponente` |
| **Six** | Reach; ataque: mila 3 e pega um terreno; permanentes não-terreno do cemitério têm retrace | `combat_step`, `graveyard_cast_options` (descarta terreno; a carta vai à pilha antes: CR 601.2a 🐛) | ✅ | `six_ataque_milla_3_...`, `six_retrace_descarta_terreno` |
| **Syr Konrad** | outra criatura morre / carta de criatura vai a cemitério de fora do campo / **carta de criatura sai do meu cemitério**: 1 dano a cada oponente; `{1}{B}`: cada jogador mila 1 | `creature_dies`, `kill_group` (**mortes simultâneas**: ruling 2019-10-04), `put_card_into_graveyard`, `mill_event`, `graveyard_leave`, `act_konrad` | ✅ 🐛 (3ª cláusula e simultaneidade faltavam) | `syr_konrad_...`, `konrad_mortes_simultaneas_...` |
| **The Gitrog Monster** | Deathtouch; upkeep: sacrifica ou sacrifica terreno; terreno extra; terreno(s) no cemitério: compra (1×/evento) | `gitrog_upkeep`, `land_drops_available`, `mill_event`/`put_card_into_graveyard` | ✅ | `gitrog_...` (2 testes) |
| **Undead Alchemist** | dano de Zumbi a jogador vira mill; criatura milada de oponente: exila + Zumbi (um por Alchemist) | `combat_step`, `mill_event` | ✅ | `undead_alchemist_...` (2 testes) |
| **Walking Ballista** | entra com X contadores; `{4}`: +1; remover: 1 dano | `resolve_spell` (+`on_counters_placed`: "entra com contadores" conta, ruling Hollowmurk), `act_ballista_pump`, `act_ballista_ping` | ✅ | `ballista_enters_com_X_...` |
| **Winding Constrictor** | +1 contador de cada tipo em artefato/criatura meu; e **em mim** | `counter_modifiers`, `give_rad` | ✅ | `constrictor_dobra_rad_proprio` |
| **Zellix** | milled criatura: Horror (1 por evento); `{1},{T}`: jogador-alvo mila 3 | `mill_event`, `act_zellix` (**crime**), granted pelo Cauldron | ✅ | `zellix_...` (3 testes) |

### Artefatos, encantamentos, planeswalker
| carta | cláusula | código | status | teste |
|---|---|---|---|---|
| **Agatha's Soul Cauldron** | mana de qualquer cor p/ habilidades de criatura; criaturas com +1/+1 têm as ativadas das criaturas exiladas (só ativadas, ruling); `{T}`: exila carta de cemitério, criatura exilada → contador | `ability_pips`, `has_granted`, `mana_sources`, `cauldron_use` (preferência: criatura de oponente = crime + contador; senão minha, com `graveyard_leave`) | ✅ | `cauldron_...` (3 testes) |
| **Altar of Dementia** | sacrifica criatura: jogador-alvo mila poder (o do último estado) | `altar_sac`, `act_altar_finisher`, **laço** Altar+Henge+Glen (`altar_henge_loop`, limitado pela MINHA biblioteca: a compra da Henge é obrigatória) | ✅ | `altar_of_dementia_...`, `altar_henge_glen_laco` |
| Altar of the Brood | outro permanente meu entra: cada oponente mila 1 | `enter_permanent_triggers`, `land_enters` | ✅ | `altar_of_the_brood_...` |
| **Bloodchief Ascension** | fim de **cada** turno, se UM oponente perdeu 2+: marcador; 3+: carta no cemitério de oponente (de qualquer lugar): perde 2/eu ganho 2 | `ascension_end_step` (por `lost_life_this_turn`), `ascension_hit`, `opp_card_to_graveyard` (magia anulada / instantânea resolvida) | ✅; combo com Mindcrank (e Master) | `ascension_...` (4 testes) |
| **Hardened Scales** | +1 contador +1/+1 | `counter_modifiers` | ✅ | `mothman_hardened_scales_soma_um` |
| **Hedge Shredder** | ataque: pode milar 2; terreno(s) milados da biblioteca entram virados; Crew 1 | `combat_step`, `crew_shredder`, `mill_event` | ✅ | `hedge_shredder_...` (2 testes) |
| **Hollowmurk Siege** | escolhe Sultai (contador em criatura minha: compra, 1×/turno) ou Abzan (ataque: contador + menace) | `apply_etb` (Abzan com biblioteca curta), `on_counters_placed` (inclui "entra com contadores" e persist −1/−1), `combat_step` | ✅ | `hollowmurk_...` (4 testes) |
| Memory Erosion | oponente conjura: mila 2 | `opponent_turn` | ✅ | `memory_erosion_e_pollywog_...` |
| **Mesmeric Orb** | permanente desvira: o controlador mila 1 (um gatilho por permanente) | `untap_my_permanents`, `opp_untap_and_orb`, `orb_untap` | ✅ | `orb_untap_milla_...`, `orb_oponente_...` |
| **Mindcrank** | oponente perde vida: mila essa quantidade | `lose_life_opp` | ✅ | `mindcrank_dano_vira_mill` |
| **Palantír of Orthanc** | fim do turno: +1 influência (Constrictor soma), scry 2, oponente-alvo escolhe: eu compro, ou eu milo X e ele perde vida = MV total | `palantir_end_step` (**crime**; escolha do oponente: `PALANTIR_OPP_LETS_DRAW`; recusa quando X ≥ minha biblioteca) | ✅ (decisão do oponente é parâmetro) | `palantir_marcador_scry_...` |
| Psychic Corrosion | você compra: cada oponente mila 2 (só "draw", ruling) | `draw_cards` | ✅ | `psychic_corrosion_...` |
| Sol Ring | `{T}: CC` | `mana_sources` | ✅ | `sol_ring_da_dois_incolores` |
| **Soul-Guide Lantern** | ETB: exila carta de cemitério; `{T}`, sacrifica: exila cemitérios dos oponentes; `{1},{T}`, sacrifica: compra | `lantern_etb` (crime), `act_lantern`, `act_lantern_exile` | ✅ 🐛 (a 2ª ativada faltava) | `lantern_...` (2 testes) |
| **Swiftfoot Boots** | hexproof e haste; Equip `{1}` | `act_equip_boots`, `has_haste`, hexproof na resiliência | ✅ | `swiftfoot_boots_da_haste_e_equipa` |
| **The Great Henge** | custa X a menos (maior poder; só genérico); `{T}`: GG + 2 vida; criatura não-ficha entra: contador + compra | `effective_cost`, `mana_sources`, `enter_permanent_triggers` | ✅ | `great_henge_...` (2 testes) |
| **Ashiok, Dream Render** | oponentes não buscam (estático); −1: jogador-alvo mila 4, exila cemitérios dos oponentes | `act_ashiok` (**crime**) | ✅ −1; 📊 estático (o goldfish não modela busca de oponente) | `ashiok_menos_1_...` |

### Instantâneas e feitiços
| carta | cláusula | código | status | teste |
|---|---|---|---|---|
| An Offer You Can't Refuse | anula não-criatura; o dono ganha 2 Treasures | `respond_to_opp_spell` | ✅ (Treasures do oponente irrelevantes) | `contramagicas_respondem_...` |
| Arcane Denial | anula; dono compra até 2 no próximo upkeep, eu 1 | `respond_to_opp_spell`, `pending_denial_*` | ✅ | idem |
| Didn't Say Please | anula; o dono mila 3 | idem | ✅ | `didnt_say_please_milla_3_...` |
| Fierce Guardianship | grátis com comandante; anula não-criatura | `free_cast_possible` | ✅ | `fierce_guardianship_gratis_...` |
| **Heroic Intervention** | meus permanentes: hexproof + indestrutível | `try_protect_from_destroy` | ✅ resiliência | regressão de resiliência |
| Negate | anula não-criatura | idem | ✅ | idem |
| Nature's Lore / Three Visits | busca qualquer **carta com tipo Forest** (inclui duais Forest) em campo (desvirada) | `forest_search` | ✅ | `nature_lore_busca_...` |
| **Nuclear Fallout** | cada criatura −2X/−2X; cada jogador X rad | `act_fallout`, `fallout_x`, `kill_group` | ✅ rad e meu tabuleiro; 📊 −2X/−2X nas criaturas de oponente | `nuclear_fallout_da_X_rad_...` |
| **Repulsive Mutation** | X contadores em criatura minha; anular magia a menos que pague o maior poder | `act_repulsive` (main), `respond_to_opp_spell` (contramágica suave) 🐛 | ✅ | `repulsive_mutation_...` (2 testes) |
| **Smuggler's Surprise** | spree: `+{2}` mila 4 e pega 2 criatura/terreno; `+{4}{G}` 2 criaturas da mão ao campo; `+{1}` poder ≥ 4 hexproof+indestrutível | `act_smugglers` (A/B), `try_protect_from_destroy` (C) | ✅ | `smugglers_surprise_modo_a_...` |
| Tear Asunder / V.A.T.S. | exilar artefato/encantamento (kicker: não-terreno) / destruir criaturas de mesma resistência | `act_removal_proxy` | 📊 alvo no tabuleiro de oponente (proxy `interaction_plays` + crime) | `tear_asunder_e_vats_...` |
| Toxic Deluge | paga X vida; −X/−X em todas | `act_wipe_proxy` (X que poupa meu tabuleiro), `kill_group` | ✅ meu lado; 📊 criaturas de oponente | `toxic_deluge_e_wave_goodbye_proxies` |
| Wave Goodbye | devolve à mão cada criatura sem contador | `act_wipe_proxy`, `resolve_instant_sorcery` | ✅ meu lado; 📊 criaturas de oponente | idem |

### Candidatas (entram só por `SWAPS`)
| carta | cláusula | código | teste |
|---|---|---|---|
| Evolution Sage | landfall: proliferate | `landfall` | `candidata_evolution_sage_...` |
| Karn's Bastion | `{T}: C`; `{4},{T}`: proliferate | `act_karns_bastion` | `candidata_karns_bastion_...` |
| Bruvac the Grandiloquent | oponente que fosse milar: o dobro (substituição) | `mill_event` | `candidata_bruvac_...` (2 testes) |
| The Master of Lake-town | jogador perde vida: mila tanto; morre: compra por cemitério com 7+ | `lose_life_self/opp`, `remove_permanent` | `candidata_master_...` (3 testes) |
| Garruk's Uprising | ETB: compra se controlo poder ≥ 4; trample; criatura poder ≥ 4 entra: compra | `apply_etb`, `has_trample`, `enter_permanent_triggers` | `candidata_garruk_...` |
| Opulent Palace | entra virado; BGU | `land_enters_tapped` | `candidata_opulent_palace_...` |

## 3. Conceitos compartilhados (Regra #3: o bug mora na função auxiliar, não na carta)
| conceito | função | quem lê | verificação |
|---|---|---|---|
| "milled" / "put into a graveyard" | `mill_event` (único ponto de saída de biblioteca por mill) | 12 cartas (Mothman, Queen, Zellix, Alchemist, Konrad, Ascension, Gitrog, Shredder, Kozilek, Bruvac, Master…) | todos os caminhos de mill passam por ele (grep: nenhum `library[:k]` fora dele) |
| "carta vai ao meu cemitério" fora do mill | `put_card_into_graveyard` | Gitrog, Konrad, Kozilek | descarte, sacrifício, fetch, canal, ciclar |
| "carta sai do meu cemitério" | `graveyard_leave` | Konrad | Kozilek, Witness, Takenuma, Smuggler's, Fetch Quest, Agadeem, Six, Muldrotha, Cauldron |
| "contador posto" | `counter_modifiers` → `place_counters` → `on_counters_placed` | Scales, Kami, Constrictor, Danny, Fathom, Hollowmurk, Terrasymbiosis, Baloth, Broodscale, Witness | aditivos antes de multiplicadores (CR 616.1); "entra com contadores" também chama `on_counters_placed` |
| "terreno entra" | `put_land_onto_battlefield` → `land_enters` → `landfall` | Crab, Icetill, Sage, Altar of the Brood, Bog, Saga | varredura: 7.275 entradas = 7.275 chamadas, por 8 origens |
| "criatura" | `is_creature` (Veículo tripulado; cópia do Woodland) | tudo | — |
| "modificada" | `is_modified` (contador de qualquer tipo, Equipamento) | Kodama | ruling 2022-02-18 |
| "Inseto" / "legendário" | `eff_card(p).subtypes/legendary` | Swarmyard, Minamo, Cauldron, Plaza, canais | `legendary_colors` por pips |

## 4. Orquestração do turno (Regra #6): onde cada gatilho de fase mora
`play_turn`: **`begin_any_turn`** (zera "1×/turno") → untap (**Mesmeric Orb** mila por permanente desvirado, já neste turno) → upkeep (zera estado do turno; **Gitrog**; **Arcane Denial**) → draw → **Urza's Saga** (lore, CR 714.2b) → **rad** (inicio do main 1) → main 1 (terreno, conjuração, ativadas) → combate (**crew**; **Ouroboroid**; ataque: Mothman rad, mentor, Six, Shredder, Abzan; dano) → main 2 → fim do turno (**Palantír**, **Ascension**, descarte a 7: o Kozilek vale −10 com biblioteca < 25) → cleanup (cópias do Woodland, Crew). Turno de cada oponente: `begin_any_turn` → upkeep → untap (**Orb**) → compra (perde se vazia) → **rad** → terreno → magias (**Memory Erosion**, **Pollywog**, minha resposta) → fim (**Ascension**).
🐛 achado: o reset de "1×/turno" estava **depois** do untap (o Orb milava antes do reset) e só nos **meus** turnos; ambos corrigidos (teste `orb_no_untap_conta_neste_turno_a_queen`, `once_each_turn_zera_a_cada_turno_de_qualquer_jogador`).

## 5. Política do jogador (a IA é heurística; nada disto é regra do jogo)
Prioridade de conjuração `CAST_PRIORITY`; comandante primeiro; terreno com a melhor cor faltante; T1/T2: terreno virado primeiro se o ensaio a seco mostra que não custa conjuração; ataque com tudo exceto dorks de mana e Zellix; Zumbis (Alchemist) → oponente com mais biblioteca, o resto → o de menor vida; guarda de biblioteca (§1). **Isto é evidência de apoio, não a fonte da verdade (Regra #5):** uma linha de jogo humana pode ser melhor que a da IA (p.ex. segurar mais mana, atacar só com o necessário contra o Orb).

## 6. Rodada 2026-10-06: ferramenta de mill nos oponentes e Tergrid (candidata, NÃO implementada)

Arquivo: `resultados-ab/2026-10-06-tergrid-e-ferramenta-mill/`. **O simulador (`91b1a3d`) não foi alterado.** Escopo declarado (Regra #7): varridas = o oráculo e as rulings da Tergrid (leitura ao vivo), a enumeração por script das cláusulas "oponente sacrifica / descarta" nas 91 cartas distintas da lista, o Spellbook antes/depois com controles, a frequência do Annihilator e o teto crime/Deepmuck; **não varridas** = qualquer A/B da Tergrid, o comportamento de oponente real.

| cláusula da Tergrid (candidata) | status | evidência |
|---|---|---|
| frente: "whenever an opponent sacrifices a nontoken permanent or discards a permanent card, you may put that card from a graveyard onto the battlefield" | 📊 **estrutural**: depende de sacrifício/descarte do OPONENTE (Regra #1); proxy medido = o Kozilek (única fonte, Annihilator 4) ataca em 2,02% (padrão) / 2,24% (resiliência) das partidas | `resumos/frequencia_annihilator.txt`; `enumera_tergrid.txt` (0 fontes de descarte) |
| verso: "{T}: target player loses 3 life unless they sacrifice a nonland permanent of their choice or discard a card" | 📊 a escolha é do alvo (ruling: pode escolher perder vida mesmo tendo o que sacrificar); a parte **mensurável sem fabricar oponente** é o crime (mirar oponente): teto 0,27 turno/partida de espaço com Deepmuck em campo | `resumos/crime_deepmuck.txt` |
| verso: "{3}{B}: untap Tergrid's Lantern" | não simulado | — |

Rulings lidas ANTES de concluir (Regra #3, `dados/tergrid_rulings.json`): permanent card = artefato/criatura/encantamento/terreno/planeswalker; qualquer cemitério; custo pago com sacrifício/descarte também dispara; o alvo da Lantern escolhe.

🐛 **Achados da ferramenta `mill_oponentes.py` (corrigidos antes de arquivar; os brutos não mudam):** (1) a linha "por fonte (dif)" ordenava um `set` de nomes por −|dif|: o desempate dependia de `PYTHONHASHSEED` (classe da Regra #10; achado ao refazer a tabela do bruto em outro processo); (2) a soma por fonte não fechava com o total de cartas milladas (80,9 × 83,9): o loop do combo Ascension + Mindcrank/Master (`ascension_hit`) mila a biblioteca inteira fora de `mill_event`. Correção: linha `ascension_loop` + asserção (resíduo ≥ 0 e só com `ascension_loops > 0`; soma = total; total > 0).

## 7. Partida manual #1 (2026-10-06): o que o log contradiz das regras (aguardando o usuário)

Arquivo: `resultados-ab/2026-10-06-partida-manual-1/`. **O simulador (`91b1a3d`) não foi alterado nesta rodada de auditoria.** Escopo declarado (Regra #7): varridas = mana por turno, jogadas de terreno, retraces, contadores do Mothman com Kami/Scales, mill meu por fonte, rulings de 23 cartas lidas ao vivo; **não varridas** = vida, marcadores de rad, ordem da pilha, escolhas de alvo fora do log, o que o oponente simulado milou.

| cláusula (oráculo) | o log mostra | status |
|---|---|---|
| Kami: "if one or more +1/+1 counters would be put on a permanent you control, that many plus one" | 7 colocações (T5 ×1, T6 ×3, T7 ×3) com o Kami em campo, todas com +1 | 🐛 do jogo manual (aguarda resposta); o simulador aplica (`counter_modifiers`) |
| Mothman: "whenever one or more nonland cards are milled, +1/+1 counter on each of up to X target creatures" (ruling 2024-03-08: 1 gatilho por evento simultâneo) | gatilhos de mill meu sem contador: T4 (X = 2), T7 (Siege), T8 (Palantír) | ❓ pode ser "até X" = 0 |
| rad (CR 728.1: no início da fase principal 1, mila N = marcadores; cada não-terreno tira 1) | T6 ≥ 1 e T8 ≥ 1 mill meu a menos que o exigido (limite inferior firme) | ❓ rad ou landfall do Icetill |
| Icetill: "play an additional land" e "play lands from your graveyard" | usado em T5 (2 jogadas) e T8 (Saga do cemitério); T6 1 de 2, T7 0 de 2, T8 1 de 2, T9 0 de 2 | ❓ escolha ou esquecimento; 6 gatilhos do Crab perdidos |
| Ruin Crab: landfall, cada oponente mila 3 | 2 gatilhos reconstruídos (T7 pelo Shredder, T8 pela Saga); não estão no log | 📊 mill de oponente fora do log (aviso do usuário) |
| Memory Erosion: oponente conjura, mila 2 | 2 eventos reconstruídos (T6 Aven Mindcensor, T7 Evacuation) | 📊 idem |
| Hedge Shredder: "land cards put into your graveyard from your library → battlefield tapped" | T7: Forest milada entrou em campo; sem o landfall do Icetill depois | ✅ a entrada; ❓ o mill do Icetill que ela devia disparar |
| Wave Goodbye: "return each creature without a +1/+1 counter" | devolveu Patron e Shredder; ficaram as 5 com contador | ✅ |
| Evacuation (oponente simulado): "return all creatures to their owners' hands" | devolveu Ruin Crab, Mothman, Six, Kami, Icetill | ✅ (Mothman à mão, sem imposto; legal) |

## 8. Orquestração do turno (Regra #6), 2026-10-06: ordem terreno × payoff de landfall

🐛 **achado (partida manual #1):** `main_phase` fazia `play_land_phase` → `cast_loop`, então Ruin Crab / Icetill Explorer / Evolution Sage (landfall) entravam depois do terreno do turno e não disparavam com ele. **Corrigido** atrás de `LANDFALL_PAYOFF_FIRST` (`cast_landfall_payoffs_first`, antes de `play_land_phase`; testes `payoff_primeiro_*`). O código de cada carta já estava certo: o bug morava na ORDEM das chamadas de `main_phase`, a mesma classe do Megatron (Regra #6). Validação e A/B: `resultados-ab/2026-10-06-landfall-payoff-primeiro/`. Classe varrida nos outros 18 simuladores por `varredura-2026-10-05/scripts/audit_landfall_ordem.py`: candidato Toph; Beorn, Maralen, Thranduil e Prismatic Bridge a ler à mão.

## 9. Partida manual #2 (2026-10-06): o que o log contradiz das regras (aguardando o usuário)

Arquivo: `resultados-ab/2026-10-06-partida-manual-2/`. Escopo declarado (Regra #7): varridas = mana T2-T6, contadores com Kami/Constrictor/Henge/Ouroboroid, compras do Henge, rad com o Constrictor, jogadas de terreno, rulings de 16 cartas lidas ao vivo; **não varridas** = vida, rad como marcador, ordem da pilha, o T7 depois do gatilho de combate.

| cláusula (oráculo) | o log mostra | status |
|---|---|---|
| Gyre Sage: "{T}: Add {G} for each +1/+1 counter on this creature" | T3 (0 contadores) e T4 (1) pagos como se desse 1 e 2 | 🐛 do jogo manual (aguarda resposta); o simulador acerta |
| The Great Henge: custa `{X}` a menos, X = maior poder; "nontoken creature enters: +1/+1 counter and draw" | T4: custo 5 com 4 fontes; compra da Broodscale ausente | 🐛 / ❓ |
| Kami: "that many plus one" e Winding Constrictor: "that many plus one" em artefato/criatura | T5 Constrictor 1 (2), Kami 2 (3); T6 Ouroboroid 2 (3), gatilho +2 (+3), combate +6 (+7) por criatura, ficha sem contador; T5 Mothman +3 e T7 +13 certos | 🐛 do jogo manual; o simulador acerta |
| Ouroboroid: X = poder no gatilho (ruling: calculado uma vez), em CADA criatura | T6: fichas Eldrazi Spawn sem contador | 🐛 do jogo manual; o simulador inclui fichas |
| Winding Constrictor: "if you would get one or more counters, you get that many plus one" (rad) | mills do T6 e T7 ≥ 1 abaixo do exigido | ❓ (rad não está no log) |
| Gyre Sage: evolve (condição "if" checada na entrada, ruling 2013-04-15) | +2 no T5 sem criatura que dispare | ❓ |

