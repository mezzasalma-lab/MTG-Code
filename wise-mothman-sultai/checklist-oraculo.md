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
| **Riverchurn Monument** (2026-10-07) | `{1},{T}`: qualquer nº de jogadores-alvo milam 2; **Exhaust** `{2}{U}{U},{T}`: milam tantas quanto o cemitério (uma vez por objeto) | `act_riverchurn_tap`, `act_riverchurn_exhaust`, `riverchurn_opp_end_step`, `Permanent.exhausted` | `monument_...` (16 testes), ver §11 |

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

## 9. Partida manual #2 (2026-10-06): o que o log contradiz das regras (respostas do usuário recebidas em 2026-10-07)

Arquivo: `resultados-ab/2026-10-06-partida-manual-2/`. Escopo declarado (Regra #7): varridas = mana T2-T6, contadores com Kami/Constrictor/Henge/Ouroboroid, compras do Henge, rad com o Constrictor, jogadas de terreno, rulings de 16 cartas lidas ao vivo; **não varridas** = vida, rad como marcador, ordem da pilha, o T7 depois do gatilho de combate.

| cláusula (oráculo) | o log mostra | status |
|---|---|---|
| Gyre Sage: "{T}: Add {G} for each +1/+1 counter on this creature" | T3 (0 contadores) e T4 (1) pagos como se desse 1 e 2 | 🐛 do jogo manual (**confirmado pelo usuário**: leu como 1 por ponto de poder); o simulador acerta |
| The Great Henge: custa `{X}` a menos, X = maior poder; "nontoken creature enters: +1/+1 counter and draw" | T4: custo 5 com 4 fontes; compra da Broodscale ausente | 🐛 do jogo manual (T4: o usuário **esqueceu a compra**; o custo 5 com 4 fontes é a consequência da leitura da Gyre Sage / da Takenuma não jogada) |
| Kami: "that many plus one" e Winding Constrictor: "that many plus one" em artefato/criatura | T5 Constrictor 1 (2), Kami 2 (3); T6 Ouroboroid 2 (3), gatilho +2 (+3), combate +6 (+7) por criatura, ficha sem contador; T5 Mothman +3 e T7 +13 certos | 🐛 do jogo manual (resposta 3 **cortada**: a ordem Constrictor→Kami coincide com o ledger, o +1 do Constrictor sobre si mesmo segue sem explicação); o simulador acerta |
| Ouroboroid: X = poder no gatilho (ruling: calculado uma vez), em CADA criatura | T6: fichas Eldrazi Spawn sem contador | 🐛 do jogo manual (**confirmado**: esqueceu as fichas); o simulador inclui fichas |
| Winding Constrictor: "if you would get one or more counters, you get that many plus one" (rad) | mills do T6 e T7 ≥ 1 abaixo do exigido | 🐛 do jogo manual (**confirmado**: pegou 1 rad e não 2); rad como marcador segue fora do log |
| Gyre Sage: evolve (condição "if" checada na entrada, ruling 2013-04-15) | +2 no T5 sem criatura que dispare | ✅ **achado retirado**: o usuário disse que vieram do mill do rad com o Mothman (gatilho "whenever one or more nonland cards are milled"; o Mothman dá rad a CADA jogador, então o mill dos oponentes também dispara e o log não o registra; de quem foi o mill não consta) |

## 10. Orquestração do turno (Regra #6), 2026-10-07: a guarda do payoff antes do terreno

🐛 **achado:** a guarda do comandante em `cast_landfall_payoffs_first` (`custo <= mana de agora + 1`) é cega a cor, a mana de landfall em campo e a land drops extras; no Mothman o Ruin Crab `{U}` gastava o único Island e o comandante `{1}{B}{G}{U}` não saía. ✅ ensaio a seco (`LANDFALL_GUARD_DRYRUN`, padrão). Escopo declarado (Regra #7): **varrido** = a guarda nos 3 payoffs (Ruin Crab, Icetill Explorer, Evolution Sage) com teste dirigido, A/B 2.000 e 10.000 (guarda aritmética × ensaio × base), regressão, bit-identidade e determinismo; **NÃO varrido** = magia que põe terreno em campo antes do payoff (Kodama's Reach etc.), Altar of the Brood, 2ª fase principal. Pasta: `resultados-ab/2026-10-07-guarda-ensaio-a-seco/`.

## 11. Riverchurn Monument (2026-10-07): cláusula a cláusula, rulings lidas ANTES do código

Pasta: `resultados-ab/2026-10-07-riverchurn-monument/`. Oráculo e rulings: `dados/riverchurn_scryfall.json` (Scryfall ao vivo; `flavor_name`: nenhum), cache `scryfall-cache/oracle-cache.json`. Rulings de 2025-02-07 (3): (R1) exhaust a qualquer momento em que se pode ativar habilidade; (R2) sai e volta = objeto novo, o exhaust pode ser ativado de novo; (R3) gatilho de "ativar exhaust" resolve antes. Rulings do Mothman que valem aqui: um evento de mill simultâneo de vários jogadores dispara o gatilho **uma vez** (2024-03-08).

| cláusula (oráculo / ruling) | código | status | teste |
|---|---|---|---|
| `{1}{U}`, artefato | `add("Riverchurn Monument", "{1}{U}", {"artifact"}, {"riverchurn"})`, `CAST_PRIORITY` 57 | ✅ (prioridade é convenção, sem sensibilidade: **não verificado**) | `monument_main_phase_ativa_com_mana_sobrando_e_swaps_...` |
| `{1},{T}`: "any number of target players each mill two cards" | `act_riverchurn_tap`: alvos = todo oponente vivo com biblioteca (+ eu só com `RIVERCHURN_SELF` e `safe_self_mill`); **um** `mill_event` (um gatilho do Mothman, ruling 2024-03-08); Bruvac dobra por substituição | ✅ | `monument_tap_cada_oponente_mila_2_...`, `monument_tap_sem_mana_ou_virado_...` |
| artefato: sem doença de invocação para `{T}` (só criatura tem, CR 302.6) | `perms_named(...)` sem checar `entered_turn` | ✅ | `monument_artefato_sem_doenca_de_invocacao` |
| Exhaust `{2}{U}{U},{T}`: "mill cards equal to the number of cards in their graveyard" | `act_riverchurn_exhaust`: N lido **na resolução**, antes de milar, por jogador-alvo; custo `{2}{U}{U}` pago de verdade (`spend`) | ✅ | `monument_exhaust_mila_o_tamanho_...`, `monument_exhaust_exige_UU_...` |
| "(Activate each exhaust ability only once.)" + R2 | `Permanent.exhausted` por instância: sair e voltar cria `Permanent` novo (`exhausted=False`) | ✅ | `monument_exhaust_...uma_vez_so`, `monument_novo_objeto_...` |
| R1: "any time you could activate an ability" | padrão: só com mana sobrando na minha fase principal (limite inferior); chaves `RIVERCHURN_TAP_FIRST` (antes das conjurações) e `RIVERCHURN_OPP_END_STEP` (fim do último turno de oponente, ignora a reserva das contramágicas) | ✅ (3 políticas medidas) | `monument_tap_first_...`, `monument_fim_do_turno_do_oponente_...` |
| R3: gatilho de "ativar exhaust" resolve antes | nenhuma carta da lista tem esse gatilho (varredura do oráculo: `resumos/confere_gatilho_de_ativar.txt`) | 📊 N/A: nada na lista dispara por ativar habilidade | — |
| é artefato: Altar of the Brood ("another permanent you control enters"), Mesmeric Orb ("a permanent becomes untapped": o Monument virado me mila 1 ao desvirar), Construct da Urza's Saga (+1/+1 por artefato), recastável por Muldrotha/Six | ganchos genéricos já existentes (`enter_permanent_triggers`, `untap_my_permanents`, `is_artifact`, `graveyard_cast_options`) | ✅ | `monument_altar_of_the_brood_e_orb_e_artefato_...` |
| "Any number of target players" inclui o controlador | `RIVERCHURN_SELF` (padrão desligado; medido: +1,31 × +1,03 ponto de T8) | ✅ (política) | `monument_alvo_eu_so_com_chave_...` |
| cada carta posta no cemitério de oponente com a Ascension armada (3+): "perde 2" | `mill_event` já trata por carta; Exhaust grande vira dano real | ✅ | `monument_exhaust_com_ascension_armada_...` |

**Achado de modelagem (Regra #5):** com `remove+append` nenhuma partida da variante era idêntica à da base, então o "pareamento por semente" de todos os A/B anteriores com `SWAPS` era quase só nominal; `SWAP_IN_PLACE` (padrão `False`, números arquivados intactos) deixa 79% idênticas. **Pergunta aberta (não mudei o código):** Zellix, "Whenever a **player** mills one or more creature cards": num mill simultâneo de 3 oponentes (Monument, Altar of the Brood, Psychic Corrosion…) o gatilho pode ser **por jogador** (até 3 Horrors) e o simulador conta **1 por evento**. Nem as rulings do Scryfall nem uma busca na web decidiram; o Mothman/Queen ("one or more nonland cards are milled") são por evento (ruling). Efeito esperado: Zellix subestimado; o resultado do Monument não muda de sinal (o corte do Zellix é lateral).

## 12. Jace, Wielder of Mysteries (2026-10-07): cláusula a cláusula, rulings lidas ANTES do código

Pasta: `resultados-ab/2026-10-07-jace-no-lugar-do-kozilek/`. Oráculo e rulings: `dados/jace_scryfall.json` (Scryfall ao vivo; `flavor_name`: nenhum), cache `scryfall-cache/oracle-cache.json`. Carta: `{1}{U}{U}{U}`, Planeswalker lendário — Jace, lealdade 4. Rulings de 2019-05-03 (5): (R1) sem poder vencer (Platinum Angel) a compra com biblioteca vazia continua substituída, não perco por tentar; (R2) dois Jaces: primeiro o jogador do turno (não se aplica à mesa de 1 Jace); (R3) alvo ilegal do +1 no resolver: não resolve e **não compro**; (R4) o +1 em mim: mila 2 e **depois** compro; (R5) o −8 com menos de 7 cartas e o Jace já fora de campo: compro o que der e **venço antes das ações baseadas em estado** (vence com biblioteca ≤ 7).

| cláusula (oráculo / ruling) | código | status | teste |
|---|---|---|---|
| `{1}{U}{U}{U}`, Planeswalker, lealdade 4, lendário | `add("Jace, Wielder of Mysteries", "{1}{U}{U}{U}", {"planeswalker"}, {"jace_wom"}, legendary=True)`; `apply_etb`: `loyalty = 4`; `CAST_PRIORITY` 66 | ✅ (prioridade é convenção, sem sensibilidade: **não verificado**) | `jace_custa_UUU_entra_com_lealdade_4_e_a_magia_entra_pelo_cast` |
| estático: "If you would draw a card while your library has no cards in it, you win the game instead" (+ R1) | `draw_cards`: biblioteca vazia **e** Jace em campo → `jace_win` (todo oponente vivo é eliminado, `combo_win = "jace"`); sem Jace → `decked` como antes. Vale para **toda** fonte de compra (Fathom Mage, Pollywog, Palantír, Henge, Gitrog, Selkie, Psychic Corrosion, Hollowmurk, Lantern, Mirelurk, Danny, Kozilek, Arcane Denial: lista por script em `resumos/enumeracao_condicoes.txt`) porque todas passam por `draw_cards` | ✅ | `jace_estatico_comprar_com_biblioteca_vazia_vence_e_sem_ele_perco` |
| `+1`: "Target player mills two cards." | `act_jace`: um `mill_event` (**um** gatilho do Mothman por mill simultâneo); alvo = `best_opp_library` com `commit_crime`; mirando **eu** só quando a biblioteca ≤ 2 (linha de vitória, `JACE_WIN_LINE`); Bruvac dobra por substituição (já no `mill_event`) | ✅ | `jace_mais1_oponente_mila_2_um_gatilho_do_mothman_e_compro_1` |
| `+1`: "Draw a card." (depois do mill, R4) | `draw_cards(state, 1, source="jace")` depois do `mill_event`; em mim com biblioteca ≤ 2 a compra seguinte é vitória (R4+estático) | ✅ | `jace_mais1_em_mim_com_biblioteca_ate_2_esvazia_e_a_compra_vence` |
| R3: alvo ilegal → sem compra | oponentes são alvos válidos enquanto vivos (`best_opp_library` só devolve vivo com biblioteca); sem alvo o `continue` não gasta a habilidade nem compra | ✅ (por construção; nenhum teste dirigido de "alvo ilegal", **não verificado em jogo**) | — |
| `−8`: "Draw seven cards. Then if your library has no cards in it, you win the game." (+ R5) | `act_jace`: com lealdade ≥ 8 e biblioteca ≤ 7: paga 8, o Jace sai (cemitério) **antes** de resolver (o estático some), compra `min(7, biblioteca)` e vence se a biblioteca ficou vazia; com biblioteca > 7 o −8 não é usado | ✅ (política: o −8 só quando vence) | `jace_menos8_vence_com_biblioteca_ate_7_e_sai_de_campo` |
| uma habilidade de lealdade por turno, velocidade de feitiço | `used_ability_turn`, só na minha fase principal (`ACTIONS`) | ✅ | cobertos pelos testes acima |
| é planeswalker: alvo de ataque/remoção de oponente | 📊 **estrutural (parcial)**: o goldfish não modela ataque nem remoção de oponente; **proxy** `JACE_REMOVAL_PROB` (padrão 0; 20%/33%/50% por rodada de oponentes) tira o Jace de campo, só com a chave | 📊 | `jace_removal_prob_tira_o_jace_so_com_a_chave` |
| conceito compartilhado: reserva de biblioteca (`SELF_MILL_RESERVE` = 8, `library_budget`) e descarte do Kozilek | **Regra #3**: com o Jace em campo a reserva cai a 0 (esvaziar a biblioteca passa a ser a linha de vitória), o Kozilek deixa de ser descartado como seguro (`discard_value` 90) e o Bramble `act_bramble_refill` não reabastece | ✅ | `jace_em_campo_a_reserva_de_biblioteca_cai_a_zero_e_o_kozilek_nao_e_descartado` |
| sem a linha de vitória (`JACE_WIN_LINE = False`): só motor (+1 em oponente, 1 compra) mas o estático continua valendo | chave mede "o Jace sem a política de vitória" (piso do valor da carta) | ✅ | `jace_sem_a_linha_de_vitoria_so_motor_e_o_estatico_continua_valendo` |
| partidas completas sem exceção, algumas vencidas pelo Jace | — | ✅ | `jace_partidas_completas_nao_dao_excecao_e_vencem_algumas` |

**Anti-sinergia declarada (por script, `resumos/enumeracao_condicoes.txt`):** só 2 cartas da lista devolvem cartas à biblioteca / embaralham o cemitério (Kozilek, Freestrider Lookout). O Kozilek milado ou descartado com o Jace em campo **desfaz** o esvaziamento da biblioteca; por isso o Jace e o Kozilek se atrapalham quando coexistem. **Commander Spellbook** (`resumos/log_spellbook_jace.txt`): 91 nomes reconhecidos, controles positivo (Thassa + Consultation) e de corte (Ascension + Mindcrank some ao cortar o Mindcrank) passaram; o Jace **não cria combo novo** (12 combos de 2 peças "quase", todos com a outra peça fora da lista: Demonic Consultation, Divining Witch, Enter the Infinite, Griselbrand, Hermit Druid, Leveler, Mirror of Fate, Oath of Druids, Paradigm Shift, Phyrexian Devourer, Tainted Pact, Thought Lash); cortar o Kozilek não derruba nenhum combo da base (só um "quase" de 3 peças: Kozilek + Morality Shift + Syr Konrad). **Fontes de {U}:** 16 dos 36 terrenos (4 Island, Breeding Pool, Watery Grave, Zagoth Triome, Command Tower, Morphic Pool, Plaza of Heroes, Rejuvenating Springs, Waterlogged Grove, Minamo, Fabled Passage, Misty Rainforest, Polluted Delta): o UUU depende do mana.

## 13. Agent Frank Horrigan e The Master, Transcendent (2026-10-07, lista do Stefano): cláusula a cláusula, rulings lidas ANTES do código

Pasta: `resultados-ab/2026-10-07-comparacao-stefano/`. Oráculo e rulings: `dados/rulings_candidatas.json` (Scryfall ao vivo; `flavor_name`: nenhum; 4 impressões cada, todas PIP), cache `scryfall-cache/oracle-cache.json`. Código: dois blocos de patch aplicados ao simulador (`orquestracao/patch_hm.py`, `patch_hm2.py`, `patch_hm3.py`; simulador resultante congelado em `codigo/mothman_goldfish_v1_HM.py`, idêntico ao vivo).

**Agent Frank Horrigan** (`{5}{B}{G}`, criatura lendária Mutant Warrior 8/6). Rulings de 2024-03-08 (9): (R1) a indestrutibilidade vale desde que ele é declarado atacante e pelo resto do turno, não importa o que aconteça com o alvo; (R2) entrando já atacando (efeito de entrar atacando) ele NÃO é indestrutível; (R3) proliferar duas vezes: ninguém responde entre as duas; (R4) as duas passadas são **escolhas independentes**; (R5) qualquer permanente com contador (inclusive de oponente) e qualquer jogador com contador (inclusive oponente); (R6) não é preciso escolher tudo, "qualquer número" inclui zero; (R7) quem tem mais de um tipo de contador recebe um de cada; (R8) dá para responder à magia/habilidade, não ao proliferate já resolvendo; (R9) alvo ilegal: não resolve.

| cláusula | código | status | teste |
|---|---|---|---|
| `{5}{B}{G}`, 8/6, lendária, Mutant Warrior | `add("Agent Frank Horrigan", ...)`, `CAST_PRIORITY` 71; no mulligan vai ao fundo como todo MV ≥ 7 | ✅ (prioridade é convenção, sem sensibilidade: **não verificado**) | `horrigan_custa_7_e_entrar_prolifera_...` |
| Trample | tag `trample` (contra a mesa passiva todo dano passa; vale para o dano de combate e para `has_trample`) | ✅ | `horrigan_sem_haste_...` (dano ≥ 8) |
| "has indestructible as long as it attacked this turn" (R1, R2) | `Permanent.attacked_turn_id` gravado ao declarar o ataque; `is_indestructible` = atacou neste `turn_id`; `try_protect_from_destroy` o poupa; **no turno do oponente (outro `turn_id`) não vale**, então o wipe de oponente o mata. `-X/-X` (Deluge, Fallout) não é destroy | ✅ | `horrigan_indestrutivel_so_no_turno_...` |
| "Whenever Agent Frank Horrigan enters or attacks, proliferate twice" (R3-R7) | `apply_etb` (entrar, inclusive reanimado pela Master/Muldrotha/Six) e o laço de gatilhos de ataque de `combat_step`; `proliferate(times=2)` = 2 passadas independentes; política: tudo que ajuda (criaturas com contador, Ascension, Ashiok, Palantír, rad dos OPONENTES), nunca rad próprio nem lore da Urza's Saga nem `-1/-1` do persist | ✅ (política) | `horrigan_custa_7_...`, `horrigan_com_hardened_scales_e_constrictor_...`, `horrigan_sem_haste_...` (ataque) |
| amplificadores somam por passada (Scales, Kami, Constrictor) | `counter_modifiers` já lia os três; conferido: 1 contador vira 3 / 5 / 9 depois de 1 gatilho (nenhum / um / os três) | ✅ | idem |
| The Great Henge "costs {X} less, X = greatest power" | `effective_cost` lê o maior poder: com o Horrigan a Henge custa `{G}{G}` | ✅ | `horrigan_reduz_The_Great_Henge_ao_custo_GG` |
| doença de invocação / Swiftfoot Boots | `can_attack`, `has_haste` já existentes | ✅ | `horrigan_sem_haste_...` |
| sensibilidade: só o corpo | chave `HORRIGAN_PROLIF_TIMES = 0` (padrão 2) | ✅ | `horrigan_chave_sem_proliferate_so_o_corpo` |

**The Master, Transcendent** (`{1}{B}{G}{U}`, criatura-artefato lendária Mutant 2/4). Rulings de 2024-03-08 (11): (R1) "mill" é a palavra: carta posta no cemitério vindo da biblioteca por outro efeito NÃO é alvo legal; (R2) a base 3/3 **sobrepõe características definidas por habilidade** (CDA); (R3) efeitos e contadores de P/T continuam valendo; (R4-R10) regras de rad counter (inerentes, não saem ao fim do turno, mill no início da fase principal 1 do jogador, cada não-terreno tira 1 rad e 1 de vida, proliferate interage, várias cartas milladas de uma vez = um gatilho de "milled", com menos cartas na biblioteca mila as que der).

| cláusula | código | status | teste |
|---|---|---|---|
| `{1}{B}{G}{U}`, 2/4, artefato e criatura, lendária, Mutant | `add("The Master, Transcendent", ...)`, `CAST_PRIORITY` 67 | ✅ (prioridade sem sensibilidade: **não verificado**) | `master_custa_1BGU_...` |
| "When The Master enters, target player gets two rad counters" | `apply_etb`: `pick_rad_target` (oponente com mais biblioteca e menos rad) + `commit_crime` ("target player" = oponente) | ✅ | `master_custa_1BGU_...` |
| `{T}`: "Put target creature card in a graveyard that was milled this turn onto the battlefield under your control" (R1) | `mill_event` registra criatura milada por `turn_id` (minha: nome; de oponente: contagem); `act_master`; alvo em **qualquer** cemitério; descartada/morta ou milada em outro turno não conta; o corpo entra pelo caminho normal de entrada (Henge compra, ETB dispara, Konrad "sai do cemitério") | ✅ | `master_leva_criatura_minha_...`, `master_so_alveja_carta_milada_...`, `master_reanimada_dispara_Henge_...` |
| "It's a green Mutant with base power and toughness 3/3. (It loses its other colors and creature types.)" (R2, R3) | `Permanent.base_pt = (3, 3)` lido em `power()`/`toughness()` ANTES das CDAs (Frogantua, Construct) e somando contadores; `Permanent.mutant` troca os subtipos (`perm_subtypes`: Alchemist ×2 e Swarmyard) | ✅ | `master_base_3_3_sobrepoe_a_CDA_...` |
| habilidade com `{T}` de criatura: doença de invocação; Swiftfoot Boots dá haste | `master_ready` | ✅ | `master_tem_doenca_de_invocacao_e_Boots_da_haste` |
| instante: também no turno do oponente, depois do rad dele (milla no início da fase principal 1 dele) | `opponent_turn` chama `act_master` depois do `rad_trigger_opp` (chave `MASTER_OPP_TURN`); só desvira no MEU untap, então vale uma ativação por rodada | ✅ | `master_no_turno_do_oponente_usa_o_mill_do_rad_dele` |
| criatura de OPONENTE milada | 📊 **estrutural (parcial)**: as cartas do oponente são "terreno / criatura / outra" (28 criaturas de 99); a Master leva um "Opponent Creature Card" 3/3 genérico, **sem as habilidades da carta real** (a base 3/3 não depende da carta, as habilidades sim). Morre → volta ao cemitério e à mão DELE (Wave Goodbye); chave `MASTER_TAKE_OPP = False` desliga | 📊 | `master_criatura_de_oponente_milada_...` |
| conceitos compartilhados (Regra #3) | `power()`/`toughness()` (2 pontos), subtipos (3 pontos), Wave Goodbye, `remove_permanent`, lista de alvos da remoção de oponente na resiliência (Master e Horrigan logo depois da Muldrotha) | ✅ | testes acima |
| combinação com Horrigan | a Master reanimando o Horrigan milado: entra como 3/3 e prolifera duas vezes | ✅ | `master_reanimando_o_Horrigan_milado_...` |

**Conflito declarado (não modelado):** o Undead Alchemist exila e cria Zumbi no gatilho de "criatura milada do oponente", antes de a Master poder agir no caminho do simulador (ele remove o `C` do cemitério dentro do `mill_event`); no jogo real a Master (instantânea) poderia responder ao gatilho. **NÃO verificado.**

## 14. Fractured Sanity, Screeching Scorchbeast, Inexorable Tide, Branching Evolution, Loading Zone, The Earth Crystal (2026-10-07, lista do Stefano): cláusula a cláusula, rulings lidas ANTES do código

Pasta: `resultados-ab/2026-10-07-candidatas-stefano-2/`. Oráculo e rulings: `dados/rulings_candidatas2.json` (Scryfall ao vivo, set + nº da lista do Stefano; `flavor_name`: nenhum), cache `scryfall-cache/oracle-cache.json`. Código: `orquestracao/patch_c2.py` sobre o simulador com Horrigan/Master; resultado congelado em `codigo/mothman_goldfish_v1_C2.py`. **Spellbook** (`resumos/log_spellbook_cand2.txt`, 96 nomes reconhecidos, controle positivo e de corte passaram): nenhuma das seis cria combo (as seis juntas também não); "quase" novo com a peça: Fractured Sanity + Doomsday Excruciator, Inexorable Tide + **Evolution Witness** (falta uma peça fora da lista), Branching Evolution / Loading Zone / The Earth Crystal + Walking Ballista + Vigor ou Rite of Passage (peças fora da lista).

| carta | cláusula (oráculo / ruling) | código | status | teste |
|---|---|---|---|---|
| **Fractured Sanity** `{U}{U}{U}` feitiço | "Each opponent mills fourteen cards." (não mira: não é crime) | `resolve_instant_sorcery`: **um** `mill_event` com os três oponentes (um gatilho do Mothman, X = soma dos não-terrenos; Bruvac dobra) | ✅ | `fractured_sanity_custa_UUU_...` |
| | "Cycling {1}{U}" + "When you cycle this card, each opponent mills four cards" (resolve ANTES da compra; o gatilho e o ciclar não são magias, 2021-06-18) | `act_fractured_cycle`: política: cicla quando o UUU não fecha (< 3 fontes de `{U}` em campo, ou T ≥ 9) e há mana; mila 4 em cada oponente, DEPOIS compra; vai ao cemitério | ✅ (política) | `fractured_sanity_ciclar_...` |
| **Screeching Scorchbeast** `{4}{B}{B}` 5/5 voa, menace | "Whenever this creature attacks, each player gets two rad counters" (eu também; Constrictor soma +1 nos meus) | `combat_step`: `give_rad(0, 2)` e cada oponente vivo | ✅ | `scorchbeast_custa_4BB_...` |
| | "Whenever one or more nonland cards are milled, you may create that many 2/2 black Zombie Mutant creature tokens. Do this only once each turn." (qualquer jogador; um gatilho por evento simultâneo; "you may" na resolução: se não criar, o gatilho volta) | `mill_event`: `nonland_total` de TODOS os jogadores do evento; cria quando o evento tem ≥ `SCORCH_MIN_X` (3); uma vez por `turn_id` por Scorchbeast; ficha "Zombie Mutant Token" 2/2 (subtipos Zombie e Mutant: o Undead Alchemist as converte em mill) | ✅ (política) | `scorchbeast_evento_pequeno_...`, `scorchbeast_zumbis_viram_mill_...` |
| **Inexorable Tide** `{3}{U}{U}` encantamento | "Whenever you cast a spell, proliferate." (resolve antes da magia, 2011-01-01; escolha livre, "qualquer número") | `on_my_spell_cast` nos **4** pontos de conjuração (`cast_card`, `cast_commander`, `cast_custom` e o do Repulsive Mutation), inclusive cemitério (Muldrotha/Six) e comandante anulado; a própria Tide não se dispara | ✅ | `inexorable_tide_prolifera_em_toda_conjuracao_...` |
| **Branching Evolution** `{2}{G}` encantamento | "twice that many +1/+1 counters" em criatura minha; entrar com contadores também (2020-06-23); ordem de substituições à escolha (aditivos antes dos multiplicativos) | `counter_modifiers`: `mult *= 2 ** (... + Branching Evolution)` (só criatura, só +1/+1) | ✅ | `branching_evolution_dobra_...` |
| **Loading Zone** `{3}{G}` encantamento | "If one or more counters would be put on a creature, Spacecraft, or Planet you control, twice that many of each of those kinds" | já existia em `counter_modifiers` (todos os tipos, criatura); cartas novas: `add()` | ✅ | `loading_zone_dobra_...` |
| | **Warp `{G}`**: "Exile this enchantment at the beginning of the next end step, then you may cast it from exile on a later turn" | cara `warp` (custo `{G}`; política: só quando o custo cheio não cabe e há criatura): `Permanent.warped`; `end_step` exila (não vai ao cemitério) para `state.warp_exile`; recastável **em turno posterior** pelo custo cheio (`warpexile`) | ✅ (política) | `loading_zone_dobra_todos_os_contadores_warp_G_...` |
| | conceito compartilhado (Regra #3): o −1/−1 do persist da Glen Elendra passa pelos substituidores e a criatura com **tenacidade 0 morre antes dos gatilhos de entrada** (CR 704.5f; tem −1/−1: sem persist) | `remove_permanent`: `(1 + plus) * mult` por `counter_modifiers(.., "-1/-1")`; chave `PERSIST_ZERO_TOUGHNESS_DIES` (padrão True; False = o 0/0 ficava em campo). **Achado do baseline:** Winding Constrictor + Glen Elendra já dava um 0/0 vivo | ✅ | `persist_da_Glen_Elendra_com_dobrador_ou_Constrictor_...` |
| **The Earth Crystal** `{2}{G}{G}` artefato lendário | "Green spells you cast cost {1} less" (só o genérico do custo total; 2025-06-06); pip híbrido `{G/U}` é verde; o comandante (B G U) é verde | `effective_cost`: `g -= 1` por Crystal quando algum pip aceita `G` | ✅ | `the_earth_crystal_verdes_custam_...` |
| | "twice that many +1/+1 counters" em criatura minha | `counter_modifiers` (junto com a Branching Evolution) | ✅ | idem |
| | "`{4}{G}{G}, {T}`: Distribute two +1/+1 counters among one or two target creatures you control" (cada alvo recebe ≥ 1) | `act_earth_crystal`: dois alvos (1 + 1, cada um passa pelos amplificadores e dobradores) quando há duas criaturas, senão 2 num só | ✅ (política) | `the_earth_crystal_ativada_...` |
| todas | resiliência: entram na lista de alvos da remoção de oponente (depois da Muldrotha) | `INTERACTION_ENGINE_PRIORITY` | ✅ | — |
| todas | prioridade de conjuração: Fractured 64, Scorchbeast 70, Tide 60, Branching 70, Loading Zone 58, Crystal 61 | `CAST_PRIORITY` | ✅ convenção, **sem sensibilidade: NÃO verificado** | — |

**Não coberto (declarar na Regra #7):** o Zumbi Mutant que ataca contra oponentes reais (a mesa é passiva), a política de esperar um evento de mill maior para o Scorchbeast (só `SCORCH_MIN_X` em 1/3/6), o Warp de um turno do oponente, Loading Zone em Spacecraft/Planet (a lista não tem), e a ordem humana real de ciclar a Fractured Sanity.

## 15. Remoções candidatas (2026-10-08, pergunta "interação por remoção?"): oráculo e rulings lidos ANTES de recomendar

Fonte: Scryfall ao vivo em 2026-10-08, `resultados-ab/2026-10-08-pacote-e-interacao/dados/rulings_remocoes.json` (15 rulings). **Nenhuma destas cartas está no simulador nem na lista**; esta seção registra o que se leu, não uma implementação.

| carta | oráculo (resumo) | rulings relevantes | no simulador? |
|---|---|---|---|
| **Drown in the Loch** `{U}{B}` | escolha: anula magia com MV ≤ cartas no cemitério **do controlador dela**, ou destrói criatura com MV ≤ cartas no cemitério **do controlador dela** | 2019-10-04: `{X}` na pilha usa o X escolhido; em campo X = 0 | ❌ (não implementada; o cemitério do oponente está medido em `resumos/gy_oponentes.md`) |
| **Atomize** `{2}{B}{G}` | destrói permanente não-terreno alvo; proliferate | 2024-03-08: escolhe qualquer número de permanentes e jogadores com contador (zero inclusive); cada um recebe 1 de CADA tipo que já tem | ❌ (o proliferate já está modelado em `proliferate()`; o "destroy" é estrutural) |
| **Deadly Rollick** `{3}{B}` | com comandante, pode ser conjurada sem pagar; exila criatura alvo | 2020-04-17: qualquer comandante seu serve; ninguém pode agir durante a conjuração | ❌ |
| **Assassin's Trophy** `{B}{G}` | destrói permanente de oponente; ele pode buscar um básico | 2018/2024: se não for destruído (indestrutível), ele ainda busca; alvo ilegal: não resolve, ninguém busca | ❌ |
| **Putrefy, Beast Within, Casualties of War** | oráculos no `scryfall-cache` (já estavam) | rulings não lidas | ❌ |

**Conceito compartilhado (Regra #3) conferido para a recomendação:** quais cartas da lista só pegam magia **não-criatura** (Offer, Negate, Fierce Guardianship, Glen Elendra — oráculos no cache): 4 de 6 contramágicas; só Arcane Denial e Didn't Say Please pegam qualquer magia (Repulsive Mutation é "anula a menos que pague"). O argumento "redundância" do corte Offer + Negate vem daí (raciocinado).
**Não coberto (Regra #7):** as rulings de Putrefy, Beast Within e Casualties of War.

## 16. Atomize, Casualties of War e Assassin's Trophy (2026-10-08, pedido do usuário): cláusula a cláusula, rulings lidas ANTES do código

Fonte: Scryfall ao vivo em 2026-10-08 (`resultados-ab/2026-10-08-cinco-entradas-remocao/dados/rulings_remocoes.json` das rodadas anteriores em `../2026-10-08-pacote-e-interacao/dados/` + `dados/rulings_casualties.json`). Nenhuma das três é Game Changer (campo `game_changer` do Scryfall = false). Agent Frank Horrigan e Branching Evolution já estavam auditados (§13 e §14).

| carta | cláusula do oráculo | ruling | código | status | teste |
|---|---|---|---|---|---|
| **Atomize** `{2}{B}{G}` instant | "Destroy target nonland permanent." | alvo: permanente não-terreno | alvo de OPONENTE: estrutural (o tabuleiro dele não é simulado): `act_removal_proxy` só conjura com `target_available` (P = 0,7 a partir do T3); `interaction_plays` +1; `commit_crime` (mira permanente de oponente: Deepmuck / Freestrider) | 📊 (a destruição) + ✅ (crime, métrica proxy) | `atomize_custa_2BG_...` |
| | "Proliferate." | 2024-03-08: escolhe qualquer número de permanentes e jogadores com contador (zero inclusive), cada um recebe 1 de CADA tipo que já tem; não se pode escolher carta fora do campo | `proliferate(state, "atomize")`: criaturas minhas com contador (passando por Scales / Branching / Constrictor), quest / influence / loyalty / charge, rad dos oponentes que têm; não os meus rad, nem o −1/−1 do persist. O crime vem ANTES (o gatilho do Deepmuck resolve antes da magia) | ✅ | `atomize_com_Hardened_Scales_e_Branching_...` (+1 → Scales → Branching = +4; Deepmuck mila 3 em cada oponente antes) |
| **Casualties of War** `{2}{B}{B}{G}{G}` feitiço | "Choose one or more — artefato / criatura / encantamento / terreno / planeswalker alvo" | 2019-05-03: cada alvo é destruído na ordem do texto, gatilhos só depois; cada modo uma vez | alvos de OPONENTE: estrutural; uma magia que mira = UM crime; `interaction_plays` +1; **não invento quantos modos haveria**. Custo `{2}{B}{B}{G}{G}` pelos pips | 📊 + ✅ (custo, crime, métrica) | `casualties_custa_2BBGG_...` |
| **Assassin's Trophy** `{B}{G}` instant | "Destroy target permanent an opponent controls." | alvo: permanente de oponente (sempre crime) | idem Atomize | 📊 + ✅ | `trophy_custa_BG_...` |
| | "Its controller may search their library for a basic land card, put it onto the battlefield, then shuffle." | 2018-10-05 / 2024-02-02: se o alvo é legal mas não é destruído (indestrutível), o controlador ainda busca; alvo ilegal: não resolve e ninguém busca | o oponente-alvo (o 1º vivo) tira 1 terreno ('L') da biblioteca e ganha 1 terreno em campo (`Opp.lands`, que o simulador usa na mana do oponente); o embaralhar não tem efeito observável. O proxy supõe alvo legal e destruído | ✅ (no que o simulador rastreia) | `trophy_custa_BG_...` (−1 'L', +1 `lands`, só no oponente alvo; sem 'L' não há busca) |

**Política (declarada, não é cláusula do oráculo):** as três entram em `act_removal_proxy`, que conjura UMA remoção por turno com mana sobrando (depois das ativadas e do desenvolvimento) e `target_available`; ordem de preferência quando há várias: Casualties of War, Atomize, Assassin's Trophy, Tear Asunder, V.A.T.S. O scry do Palantír trata as três como valor 25 (< 30: vão para o fundo), igual ao Tear Asunder e ao V.A.T.S. já existentes.
**Conceito compartilhado (Regra #3) conferido:** `commit_crime` (Deepmuck Desperado, Freestrider Lookout) e `on_my_spell_cast` (Inexorable Tide, "magias conjuradas") passam por `cast_custom`; nenhum outro lugar do arquivo lê a tag das remoções além de `castable_candidates`, `resolve_instant_sorcery` e `act_removal_proxy` (grep).
**Não coberto (Regra #7):** (a) Atomize / Trophy no tempo do oponente (resposta a uma magia ou habilidade), (b) alvo MEU (Atomize em criatura minha com persist, em ficha ou em artefato esgotado para só proliferar), (c) a escolha do oponente-alvo (usa o primeiro vivo, sem critério de ameaça), (d) a quantidade de modos do Casualties, (e) o Beast Within (3/3 para o oponente) e as outras remoções de permanente (Maelstrom Pulse, Abrupt Decay, Vraska's Contempt, Putrefy) NÃO estão implementadas.

**Status (2026-10-08, depois da confirmação do usuário):** Agent Frank Horrigan (§13), Branching Evolution (§14), Atomize, Casualties of War e Assassin's Trophy (este §16) agora fazem parte da lista oficial (`lista.md` e `DECKLIST_TEXT`); sairam An Offer You Can't Refuse, Negate, V.A.T.S., Wave Goodbye e Didn't Say Please (suas linhas das auditorias anteriores continuam válidas como histórico, mas elas já não estão na lista).
