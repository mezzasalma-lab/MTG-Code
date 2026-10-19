# Tam, the Possibility: os decks do Moxfield contra o nosso — o que melhorar (2026-10-19)

> Pedido do usuário: *"avalie os decks no Moxfield com o mesmo comandante e ver o que podemos melhorar no nosso"*. **Nada foi alterado na lista**: tudo abaixo é proposta; aplicar só com um "sim". Sem simulador (o usuário pediu para não fazer ainda): nada aqui é velocidade medida, é oráculo + rulings + motores do deck + Commander Spellbook + o que os decks publicados jogam.
> Dados, scripts e como refazer: `resultados-ab/2026-10-19-avaliacao-decks-tam/LEIAME.md`.

## 1. Resumo

- **Fonte dos decks:** a API do **Moxfield devolveu 403** (Cloudflare) e **não contornei**. Usei o **EDHREC**, que guarda as listas enviadas pelos usuários, inclusive as do Moxfield. Baixei 1.219 decks dos 6.931 do Tam (os 719 com bracket 3 ou 4 declarado, de qualquer site, + 500 sorteados sem bracket): **663 são do Moxfield** e 556 do Archidekt. **Um deles (`moxfield.com/decks/vxShAZ1_h32rYdwmXh4z5Q`) tem as MESMAS 63 cartas não-terreno que o nosso**: é o próprio deck do usuário e ficou fora. Base da comparação: **662 decks do Moxfield** (bracket 3: 326; bracket 4: 89; sem bracket: 247).
- **O nosso deck é um Tam superfriends "padrão" com três diferenças reais** (item 3): **mais planeswalkers** (25; média 22,2 no B3), **muito mais cartas "empower Jace"** (10; média 4,5) e **quase nenhuma interação em instantâneo**: **1 instantâneo** (média 6,6), **0 remoção pontual em instantâneo** (2,1) e **0 contramágicas** (1,2).
- **O que falta, pelo oráculo e pelos motores do deck:** (1) interação e proteção em velocidade de instantâneo; (2) **dobrador de contadores** (Doubling Season: 62% dos decks B3); (3) **segunda redução de custo de planeswalker** (Oath of Ajani) por cima da Tam; (4) **proliferate em terreno** (Karn's Bastion) no lugar de um terreno de utilidade fraca; (5) um motor de lealdade que não pede combo (Commodore Guff, 66%).
- **Proposta: pacote de 6 trocas** (item 4): **0 Game Changers; Spellbook: 0 combos novos e 0 perdidos** (hoje 2 combos, depois os mesmos 2). O deck continua com **25 planeswalkers e 21 tipos**. Efeito estático: instantâneos 1 → 3, remoção pontual em instantâneo 0 → 1, proliferate/dobradores 8 → 10 (B3: 8,9) e **custo médio dos planeswalkers 3,56 (só a Tam) → 2,92 (Tam + Oath of Ajani)**.
- **O que o pacote NÃO fecha:** interação em instantâneo continua abaixo da média (3 instantâneos contra 6,6; 1 remoção pontual contra 2,1; 0 contramágicas contra 1,2). Fechar o resto exige cortar mais cartas (item 6, a escolha é sua).
- **Cartas que mudam o Bracket** (item 5): Carth the Lion, Nicol Bolas Dragon-God, Teferi Master of Time, Spark Double, Teferi Time Raveler e o Vorinclex (já no seu sideboard) **criam combos de 2 ou 3 cartas com peças que você já joga**. Estão entre as mais jogadas nos decks, e **não** estão no pacote.

## 2. Método e limites

1. EDHREC: `json.edhrec.com/pages/decks/tam-the-possibility.json` (tabela de 6.931 decks) e `edhrec.com/api/deckpreview/<id>` (cartas por tipo e **URL de origem**). **Não é amostra aleatória de todos os decks**: os com bracket 3 ou 4 declarado entram todos, e os outros 500 são sorteados com semente fixa.
2. Oráculo ao vivo (Scryfall `POST /cards/collection`) das 2.660 cartas distintas dos decks; as categorias do item 3 são **regex sobre o `oracle_text` sem o texto de lembrete** (a mesma heurística dos dois lados, **não** lista exaustiva de efeitos).
3. Rulings ao vivo (Scryfall) das candidatas e das cartas do deck que elas tocam, **lidas antes** de avaliar (Regra #3): Tam, Carth, Doubling Season, Mutational Advantage, Countersculpt, Jace's Machinations, Domri, Interplanar Beacon, Teferi's Talent, Liliana's Talent, Displacer Kitten etc. (`dados/rulings_candidatas.json`).
4. Commander Spellbook com a lista exata, nomes resolvidos antes (a API ignora nome desconhecido): **adições de uma carta por vez: 140 nomes, 37 candidatas; trocas e pacote: 114 nomes; 0 não reconhecidos nos dois lotes**; controle positivo (Thassa's Oracle + Demonic Consultation aparece) e de corte (sem a Consultation some) ok nos dois.
5. **Inclusão ≠ qualidade** (Regra #5): carta rara nos decks do Moxfield não é motivo de corte por si. Cada corte abaixo tem o motivo no oráculo e no motor, e as peças de combo ficam de fora (item 7).

## 3. Estrutura: nosso deck contra os decks do Moxfield (média por deck; B3 = bracket 3, 326 decks; "22+ PW" = bracket 3 com 22 ou mais planeswalkers, 173 decks)

| categoria (oráculo) | nosso | nosso com o pacote | Moxfield B3 | B3 e 22+ PW |
|---|---|---|---|---|
| planeswalkers | **25** | 25 | 22,2 | 25,9 |
| criaturas | 12 | 12 | 13,0 | 11,9 |
| **instantâneos** | **1** | 3 | **6,6** | 5,6 |
| **remoção pontual em instantâneo** | **0** | 1 | **2,1** | 1,8 |
| **contramágicas** | **0** | 0 | **1,2** | 0,9 |
| remoção em massa de criaturas | 6 | 6 | 4,0 | 4,1 |
| ramp que busca terreno (Farseek, Nature's Lore...) | 0 | 0 | 2,1 | 1,9 |
| mana de não-terreno (rochas e criaturas) | 8 | 7 | 6,6 | 6,3 |
| planeswalker que produz mana | 5 | 5 | 3,0 | 3,4 |
| compra de cartas (heurística) | 14 | 13 | 13,5 | 14,7 |
| proliferate ou dobra contadores | 8 | **10** | 8,9 | 8,1 |
| proteção de planeswalker / fase / indestrutível | 6 | 7 | 5,4 | 5,4 |
| ficha de Jace / cria planeswalker (Reality Fracture) | **10** | 10 | 4,5 | 4,2 |
| tutor (busca não-terreno) | 2 | 2 | 1,9 | 1,8 |
| terrenos que entram sempre virados | 6 | 6 | 4,0 | 3,9 |
| terrenos com fetch | 5 | 5 | 4,4 | 4,7 |

Igual ao Moxfield: compra, proteção, tutores e fetch. **A rampa não é a lacuna**: mana de não-terreno + planeswalkers de mana dá 13 no nosso contra 6,6 + 3,0 = 9,6 no B3 (11,7 contando o ramp que busca terreno). Acima: planeswalkers, remoção em massa (6 contra 4) e "empower Jace" (a identidade Reality Fracture do deck). **Abaixo: tudo o que é instantâneo.** Terrenos virados: 6 contra 4.

## 4. Pacote proposto: 6 trocas (nada aplicado)

| # | sai (inclusão B3) | entra (inclusão B3) |
|---|---|---|
| 1 | **Leyline Immersion** (1%) | **Swords to Plowshares** (50%) |
| 2 | **Staff of Compleation** (8%) | **Oath of Ajani** (38%) |
| 3 | **Domri, Chaos Bringer** (2%) | **Doubling Season** (62%) |
| 4 | **Teferi's Talent** (10%) | **Commodore Guff** (66%) |
| 5 | **Baxter Building** (1%) | **Karn's Bastion** (49%) |
| 6 | **Liliana's Talent** (6%) | **Mutational Advantage** (32%) |

**Spellbook: cada troca sozinha e o pacote inteiro = 0 combos novos, 0 perdidos.** (Peças que aparecem como "quase", a uma carta de distância, estão na troca 3.)

1. **Leyline Immersion → Swords to Plowshares.** *Sai:* `{3}{G}`, aura "enchant legendary creature": a lista só tem **duas criaturas lendárias, a Tam e a Kiora of Salt and Sand**. Dá ward `{2}` e `{T}: Add five mana in any combination of colors. Spend this mana only to cast spells`. **Mas o `{T}` da Tam é o mesmo da proliferate dela** (`{W}{U}{B}{R}{G}, {T}`): em cada turno ela faz uma coisa ou a outra; a Tam tem enjoo de invocação quando entra; a aura morre com ela e não é planeswalker (sem desconto da Tam). *Entra:* `{W}` instantâneo, exila criatura (o dono ganha vida igual ao poder): **a primeira remoção pontual em instantâneo do deck (0 → 1)**. *Risco:* W tem 17 fontes (≥1 até o T4: 86,3%); dá vida ao oponente. Path to Exile (35%) é a alternativa (Spellbook como adição: 0 combos novos).
2. **Staff of Compleation → Oath of Ajani.** *Sai:* `{3}` artefato com quatro habilidades que custam `{T}` e vida (1: destruir permanente sua; 2: um mana; **3: proliferate**; 4: comprar), e `{5}` para desvirar: é mais uma fonte de proliferate, que o pacote repõe só em parte (proliferate/dobradores sobem 8 → 10 com tudo). O deck já paga vida em 7 choques, 4 fetches, Starting Town e no `0` do Dellian Fel. *Entra:* `{G}{W}` encantamento lendário: **"Planeswalker spells you cast cost {1} less"**, que soma com a Tam (ruling da Tam: o custo soma os aumentos e depois aplica as reduções). **Custo médio dos 25 planeswalkers: 4,52 sem desconto → 3,56 com a Tam → 2,92 com Tam + Oath** (24 dos 25 têm genérico e **17 têm 2 ou mais**, então os dois descontos valem cheio; a Aminatou, `{W}{U}{B}`, não tem genérico). *Risco:* não desconta o que não é planeswalker (Doubling Season, as Ways); o "+1/+1 em cada criatura" vale pouco com 12 criaturas.
3. **Domri, Chaos Bringer → Doubling Season.** *Sai:* planeswalker `{2}{R}{G}`, 2% dos decks. É **rampa** (`+1`: `{R}` ou `{G}`; habilidade de lealdade, não de mana: só no seu turno e usa a pilha, ruling de 2019-01-25) e o `−3` olha 4 cartas atrás de **criaturas** (12 em 99 ≈ 0,5 por ativação). **Perde-se uma fonte de mana de planeswalker**; o Guff (troca 4) dá `{R}` só para planeswalker. *Entra:* `{4}{G}` encantamento: **tokens e contadores postos por efeito em dobro**; planeswalkers entram com o dobro de lealdade; **o custo de lealdade não dobra** (ruling de 2024-11-08: é custo, não efeito). Com a Tam, cada proliferate põe 2 contadores em vez de 1; dobra toda ficha que o deck cria (as Ways Healer, Deathbringer e Wildspeaker; Elspeth, Sun's Champion `+1`). **Não verifiquei** a interação com o `empower Jace` (se a Season dobra a ficha de Jace criada ou só os contadores): nenhum ruling trata disso. Sem desconto da Tam (não é planeswalker). *Armadilhas (Spellbook "quase", a uma carta de completar):* com a Doubling Season em campo, **Jace, Cunning Castaway** completa um combo de 2 cartas, **Lotus Petal** (com a Wrenn and Realmbreaker, que já está no deck) um de 3, e **Chandra Ablaze** (com o Displacer Kitten, que já está) outro: **não colocar essas cartas** sem decidir o Bracket. Tipos de planeswalker na lista: 21 → 21.
4. **Teferi's Talent → Commodore Guff.** *Sai:* aura `{3}{U}{U}` em planeswalker: `+1` de lealdade por carta comprada e `−12` (emblema de ativar planeswalker em velocidade de instantâneo). Cobre um planeswalker só e morre com ele; sem desconto da Tam; **é uma das fontes de lealdade que a auditoria cita para o laço Teferi + Chain Veil (não verificado)**. *Entra:* `{1}{U}{R}{W}`: **no fim do seu turno põe um contador de lealdade em outro planeswalker seu** (proliferate seletivo por turno, de graça); `+1`: ficha Wizard 1/1 que dá `{R}` só para planeswalker; **`−3`: compra X cartas e X de dano a cada oponente, X = planeswalkers que você controla** (finalizador; X lido ao resolver, ruling de 2023-07-28). 66% dos decks B3 (72% dos com 22+). *Risco:* exige **três cores** (`{U}{R}{W}`) com a Tam: fontes U 20, R 17, W 17.
5. **Baxter Building → Karn's Bastion.** *Sai:* terreno incolor: `{T}: {C}`; `{4},{T}`: quatro mana em qualquer combinação (só conserta cores, líquido 0); `{4},{T}`: compra uma carta **só com criatura de resistência 4 ou mais** (a lista tem 3: Dreamtide Whale, Kiora of Salt and Sand e Onakke Oathkeeper). *Entra:* `{T}: {C}` e **`{4},{T}`: proliferate** (+1 de lealdade em cada planeswalker a cada turno em que sobra mana). *Risco:* o Baxter é um conserto de cor tardio para a ativação de cinco cores da Tam; não conta nas fontes de cor da análise estática (`—`), então a tabela de fontes não muda.
6. **Liliana's Talent → Mutational Advantage.** *Sai:* aura `{B}{B}` (B é a cor mais curta, 16 fontes) em planeswalker: destrói a criatura que causar dano a ele (dissuade, mas o dano já foi feito) e `−8`: todas as criaturas de todos os cemitérios em campo. *Entra:* `{1}{G}{U}` **instantâneo: permanentes seus com contadores (todos os planeswalkers) ganham hexproof e indestrutível, previne todo o dano a eles neste turno, e proliferate** (ruling de 2024-03-08: o conjunto é fixado quando resolve). Proteção em velocidade de instantâneo **e** motor de proliferate. 32% dos decks B3; **está no deck mais parecido com o nosso (similaridade 0,72)**. *Risco:* não protege de exílio, sacrifício nem −X/−X.

**Efeito estático do pacote** (`resumos/pacote_efeitos.md`, `comparacao_estrutural.md`): planeswalkers 25 → 25; instantâneos 1 → 3; proliferate/dobradores 8 → 10; custo médio de planeswalker 3,56 → **2,92**; **Game Changers: nenhum** (campo `game_changer` do Scryfall ao vivo).

## 5. Cartas que MUDAM o Bracket (não estão no pacote; decisão sua)

O Spellbook, com a lista atual **mais cada uma delas, sem cortar nada**, mostra o que cada uma cria (etiqueta de bracket do Spellbook entre parênteses, como a API devolve; não interpretei):

| carta (inclusão B3) | combos novos com cartas que você JÁ joga |
|---|---|
| **Carth the Lion** (67%) | Carth + Teferi, Temporal Archmage + The Chain Veil (E). O passo-a-passo da variante `787-1124-4450` usa o `[+1]` extra do Carth para o `−1` do Teferi custar **zero**, desvirando o Veil: **fecha o laço sem recastar o Teferi da zona de comando** (o combo de 2 cartas atual exige o recast, item 5 de `auditoria.md`). Pré-requisito: até 3 permanentes que somem ≥ `{5}` |
| **Nicol Bolas, Dragon-God** (69%) | Aminatou + Bolas + Oath of Teferi (R); Aminatou + Bolas + The Chain Veil (R) |
| **Teferi, Master of Time** (47%) | Ichormoon Gauntlet + Teferi MoT + The Chain Veil (R); Gauntlet + Oath of Teferi + Teferi MoT (R); Aminatou + Gauntlet + Teferi MoT (R) |
| **Spark Double** (39%) | Aminatou + Oath of Teferi + Spark Double (S) |
| **Teferi, Time Raveler** (37%) | Displacer Kitten + **Sol Ring** + Teferi Time Raveler (E) |
| **Vorinclex, Monstrous Raider** (35%, no seu sideboard) | Vorinclex + **Vraska, Betrayal's Sting** (S): combo de **2 cartas**, "target opponent loses the game" |
| **Narset, Parter of Veils** (46%) | nenhum, mas **é Game Changer** (Scryfall) |

Probabilidade de ter as **3 peças específicas** já vistas (7 cartas + 1 por turno a partir do T2, sem mulligan e sem tutor): **T8 0,23%, T10 0,36%, T12 0,52%**. Os tutores do deck (Entrust the Spark e Tezzeret the Seeker, que busca o Veil) mudam a conta, e o Loyal Tutor mudaria; **não quantifiquei sem simulador**. Nota: o Carth é criatura, então Entrust e Loyal Tutor (só planeswalker) não o buscam; ele próprio busca planeswalker (olha as 7 do topo ao entrar e quando um seu morre) e soma `[+1]` a todo custo de lealdade (ruling de 2021-06-18: o `[−1]` vira `[0]` e o `[0]` vira `[+1]`).

## 6. Opções sem corte definido (a escolha do corte é sua)

- **Interação que combina com os motores:** **Countersculpt** (`{U}{U}`, 12%: contramágica **e `empower Jace 1`**; adicional: *behold a Jace* ou pagar `{1}`; o deck tem 10 cartas que dão ficha de Jace), **Jace's Machinations** (`{2}{U}`, 24%: planeswalkers **Jace** ativam em velocidade de instantâneo até o fim do turno e `empower Jace 8`), **Loyal Tutor** (`{W}`, 71%: busca planeswalker e põe no topo; tutores 2 → 3), **Path to Exile** (35%), **Heroic Intervention** (20%, `{1}{G}`: hexproof e indestrutível para tudo; **não testada no Spellbook**). Spellbook sem combo novo: Loyal Tutor e Path (como adição), Countersculpt e Machinations (trocando o Dack Fayden).
- **Ramp que busca terreno:** Farseek (54%), Nature's Lore (44%), Three Visits (39%): o deck tem 0 contra 2,1; os terrenos tipados do deck são alvos (choques, triomes). **A rampa total já está acima da média**, então não priorizei.
- **Mana:** B é a cor mais curta (16 fontes; ≥1 até o T4: 84,4%; com 17: 86,3%, como W e R hoje). **Godless Shrine** (50%, W/B) ou **Blood Crypt** (38%, B/R) no lugar de um terreno que não produz B (por exemplo um filtro R/G) subiriam B para 17, com 2 de vida por entrada desvirada (**Blood Crypt não foi testado no Spellbook**). **Interplanar Beacon** (60%: `{1},{T}`: dois mana de cores diferentes só para planeswalker, e 1 de vida a cada planeswalker conjurado) e **Chromatic Lantern** (60%).
- **Proliferate em criatura:** Atraxa (49%), Tekuthal (47%), Evolution Sage (40%), Deepglow Skate (54%): criaturas que morrem nas 6 remoções em massa do próprio deck.

## 7. O que eu NÃO mexeria, apesar da baixa inclusão

- **The Chain Veil (64%), Tezzeret the Seeker (6%) e Chromatic Orrery (7%)** são as peças dos **dois combos que o deck já tem** (Orrery + Tezzeret + Chain Veil; Teferi, Temporal Archmage + Chain Veil, este com o recast). Cortar Tezzeret ou Orrery mata o combo de 3 cartas.
- **Displacer Kitten** (6%): o blink reinicia a lealdade de planeswalker (objeto novo) e **reativa o `empower Jace` das 8 Ways** (todas têm "When … enters, empower Jace N"); ficha não volta do exílio (ruling), então a ficha de Jace não é alvo útil. Peça dos "quase" com Doubling Season (Chandra Ablaze) e do combo com Teferi Time Raveler + Sol Ring.
- **As 8 "Way of the…" + Sanctum Lurker** (Paradox 59%, Lurker 77%; Deathbringer 4%, Warlord 6%, Wildspeaker 6%, Healer 10%): todas fazem `empower Jace` (2 a 7) e dão um efeito próprio: Pyromancer `+1: Add {R}` a todo planeswalker; Warlord `−4` de dano; Deathbringer `−2` sacrifica criatura por Beast 4/4; Healer `−2` Cadet; Wildspeaker `−4` Beast 4/4; Mind Sculptor compra ao remover 2+ de lealdade; Necromancer põe lealdade quando criatura sua morre; Paradox dá vida e um 2º terreno. **É a identidade Reality Fracture do deck** e a razão de ter 10 contra 4,5.
- **A base de mana sem terreno básico:** as 4 fetches só acham terrenos com tipo (choques, triomes), e a **Yavimaya, Cradle of Growth** (12%) faz todo terreno ser Forest (fetch acha qualquer terreno). Plaza of Heroes e Great Hall of the Citadel fazem qualquer cor só para magia lendária (todo planeswalker e as 8 Ways são lendários).

## 8. Os decks do Moxfield mais parecidos com o nosso

(similaridade = Jaccard sobre as cartas não-terreno; `resumos/decks_parecidos.md` tem os 8 mais parecidos e o diff completo de cada um.)

| # | deck | simil. | bracket | preço (US$) | PWs | o que ele tem e nós não (destaques) |
|---|---|---|---|---|---|---|
| 1 | https://moxfield.com/decks/PHVhdAZjh02ylPQdrpl4wg | 0,72 | 3 | 8.300 | 23 | **Mutational Advantage, Oath of Ajani**, Bolas Dragon-God, Tekuthal, Brokers Ascendancy, Teferi's Protection (Game Changer) |
| 2 | https://moxfield.com/decks/v537k8Xoo0aeFgp5hX5GqQ | 0,56 | 3 | 9.270 | 25 | Carth, **Commodore Guff**, Bolas, Atraxa, Teferi MoT, The Theorist, Ugin, Tekuthal |
| 3 | https://moxfield.com/decks/DxihAR5p5n-P8euZ9gBitA | 0,44 | 3 | 580 | 21 | 9 instantâneos; **Loyal Tutor, Jace's Machinations, Atomize**, Farseek, Chromatic Lantern, Clever Concealment |
| 4 | https://moxfield.com/decks/XFbn0TRIHEe-1RAgQdPUBw | 0,38 | 3 | 439 | 26 | **Countersculpt, Doubling Season, Carth, Loyal Tutor**, Atraxa, Farseek |
| 5 | https://moxfield.com/decks/WNGgAXFU4XKo2HJqUMcHwQ | 0,37 | 3 | 828 | 30 | **Doubling Season, Commodore Guff**, Carth, Bolas, Spark Double, Teferi Time Raveler, Vorinclex |

## 9. O que NÃO foi feito / verificado (Regra #7)

- **Sem simulador:** nenhum efeito sobre velocidade, mulligan, resiliência ou interação foi medido; as trocas são **raciocinadas** (oráculo, rulings, motores, Spellbook), com números estáticos (custo médio, contagens, hipergeométrica). O que mais precisaria dele: quanto a Doubling Season e o Guff aceleram a vitória e se perder o Baxter e o Staff pesa.
- **Moxfield direto:** bloqueado (403); a amostra vem do EDHREC e não cobre decks do Moxfield que o EDHREC não capturou; só **bracket 3 e 4 declarados + 500 sorteados** entraram.
- **Não verifiquei:** o texto oficial dos Brackets (as etiquetas S, E e R são as que o Spellbook devolve); a probabilidade conjunta das cinco cores; a interação entre o `empower Jace` e a Doubling Season; se as fontes de lealdade do deck repõem o Teferi no laço atual com o Chain Veil; o Spellbook de Heroic Intervention e Blood Crypt.
- **Classes varridas:** frequência de carta e categorias por oráculo (662 decks, regex), combos pelo Spellbook (37 adições individuais + 6 trocas + pacote + 5 opções), rulings das candidatas. **Não varridas:** interação de cada carta nova com cada ruling do deck além das citadas; terrenos candidatos fora os citados; contas de mesa contra oponentes.
