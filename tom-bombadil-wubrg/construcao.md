# Tom Bombadil — como a lista foi construída (2026-09-22)

Fontes, todas consultadas ao vivo nesta data:
- Oráculo e rulings das 100 cartas: Scryfall (`/cards/collection`,
  `/cards/named`, `rulings_uri` das peças-chave).
- EDHREC: `json.edhrec.com/pages/commanders/tom-bombadil.json` (21.240
  decks no total) e `.../tom-bombadil/upgraded.json` (**1.799 decks no
  Bracket 3**). As porcentagens abaixo são desses 1.799. Temas mais
  comuns do comandante: Sagas (2.462 decks), Enchantress (1.354),
  Proliferate (31) e Counters Matter (39).
- Lista de Game Changers: Scryfall `is:gamechanger` (53 cartas nesta data).
- Regras do Bracket 3 ("Upgraded"): até 3 Game Changers, sem destruição
  em massa de terrenos, sem encadear turnos extras, sem combo infinito de
  2 cartas no começo do jogo.
- Regras de Saga (CR 714, `rules-cache/comprehensive-rules.txt`).
- Base: deck r66v do Moxfield (57 cartas mantidas), mais o deck antigo
  5UwU e o EDHREC para as trocas.

## 1. Regras que definem a estratégia

- **714.2b**: um capítulo N dispara "quando um ou mais marcadores de saber
  (lore) são colocados na Saga, se ela tinha menos de N e passou a ter N
  ou mais". Consequências diretas:
  - **Adicionar** marcador fora do turno normal (proliferate, Satsuki,
    Clockspinning, mover marcador) dispara o próximo capítulo na hora.
  - Colocar **vários de uma vez** dispara todos os capítulos
    atravessados (Resourceful Defense, Nexus Mentality).
  - **Remover** não dispara nada, mas o capítulo dispara de novo quando o
    marcador volta. Ou seja, remover marcador repete capítulos.
- **714.3b**: o marcador do turno entra no **início da fase principal
  pré-combate** (o texto de lembrete diz "depois da compra"). A mana de
  capítulos como a da The Bath Song já pode ser usada nessa mesma fase.
- **714.4**: a Saga é sacrificada quando atinge o capítulo final, **menos
  enquanto o capítulo final dela ainda estiver na pilha**. Se você remove
  um marcador em resposta ao capítulo final, a Saga **não é sacrificada**
  e o capítulo final se repete no turno seguinte (e o Tom dispara de novo).
- **Ruling do Tom**: o gatilho dele acontece depois que o capítulo final
  termina de resolver. Funciona até se o próprio capítulo final devolve o
  Tom ao campo (Elspeth Conquers Death). O Tom revela até achar uma
  "Saga card". Para cartas de duas faces, fora do campo vale só a face da
  frente: Kami War, Jugan e Fable contam como Saga. **Urza's Saga também
  conta**: é Saga de verdade, e colocá-la no campo pelo Tom não gasta a
  jogada de terreno.

## 2. Motores do deck (usados na avaliação de cada carta, Regra #4)

| # | Motor | Peças |
|---|---|---|
| M1 | **Tom**: revela uma Saga de graça por turno ao resolver um capítulo final. Com 4+ marcadores de saber somados nas Sagas, ganha hexproof e indestrutível | comandante |
| M2 | **Acelerar Sagas** (adicionar marcador) | Satsuki, Flux Channeler, Ripples of Potential, Karn's Bastion, Clockspinning, Barbara Wright (read ahead) |
| M3 | **Repetir capítulos / manter a Saga viva** (remover marcador) | Power Conduit, O'aka, Scholar of New Horizons, Hex Parasite, Clockspinning, Goldberry (1ª habilidade) |
| M4 | **Mover marcadores entre permanentes**: tira de uma Saga (repete capítulo) e põe em outra (avança capítulo) | Nesting Grounds, Resourceful Defense, Goldberry, Nexus Mentality. **São as 4 únicas cartas com identidade WUBRG que movem marcadores e funcionam em Saga**. Tidus, Bioshift, Fate Transfer, Ozolith, Slippery Bogbonder, Leech Bonder etc. só funcionam em **criatura** |
| M5 | **Copiar gatilhos** (capítulo, Tom, Resourceful Defense, Narci) | Strionic Resonator, Weaver of Harmony, Estrid's Invocation (recopia uma Saga a cada manutenção) |
| M6 | **Retorno por capítulo final / Saga sacrificada** | Narci (compra 1 por encantamento sacrificado + drena X = valor de mana da Saga), Historian's Boon (Anjo 4/4), Femeref Enchantress (compra quando um encantamento vai do campo para o cemitério) |
| M7 | **Enchantress** (compra ou mana por encantamento) | Sythis, Enchantress's Presence, Setessan Champion, Eidolon of Blossoms, Sanctum Weaver, Serra's Sanctum |
| M8 | **Recursão de Sagas** | Replenish, Resurgent Belief, Starfield of Nyx, Hall of Heliod's Generosity (põe Saga no topo, e o Tom revela exatamente ela) |

### Linhas-chave (do oráculo e das regras, não do simulador)

1. **Reação em cadeia com Resourceful Defense.** Uma Saga termina e é
   sacrificada com 3 marcadores. O Resourceful Defense põe esses 3 numa
   segunda Saga, que dispara todos os capítulos atravessados (714.2b) e
   também termina. Os marcadores dela vão para uma terceira, e assim por
   diante. Cada capítulo final dispara Narci (drena e compra), Historian's
   Boon (Anjo) e Femeref (compra). O Tom revela 1 Saga nova (1 vez por
   turno). É finito, porque depende das Sagas em campo, então não é combo
   infinito (ok no Bracket 3).
2. **Capítulo final todo turno.** Com o capítulo final na pilha, remova 1
   marcador (Power Conduit, O'aka, Scholar, Goldberry, Clockspinning ou
   Hex Parasite, todos em velocidade de instantâneo). Pela 714.4 a Saga
   fica, o capítulo final se repete no próximo turno e o Tom dispara de
   novo.
3. **Read ahead (Barbara Wright).** Summon: Bahamut entra direto no IV
   (Mega Flare), Knights of Round no V, Kiora no III e Battle at the
   Helvault no III (Avacyn). O Tom dispara já no turno em que a Saga é
   conjurada.
4. **Revelação escolhida.** Enlightened Tutor ou Hall of Heliod's
   Generosity põem a Saga que você quer no topo, e o gatilho do Tom revela
   exatamente essa. Com Strionic Resonator copiando o gatilho do Tom, são
   2 Sagas.
5. **Proteção do Tom.** Ele precisa de 4+ marcadores de saber somados nas
   Sagas. Sagas de 4 e 5 capítulos (Galactus, In the Darkness Bind Them,
   Knights of Round, Bahamut, First Iroan Games, Yojimbo) e proliferate
   seguram esse número.

## 3. Game Changers (3/3): escolhidos pelos motores

- **Serra's Sanctum** (M7): `{T}: Add {W}` para cada encantamento. Paga as
  Sagas caras (Bahamut 9, Knights 8, Kiora 7) e as ativações que custam
  mana (Clockspinning com buyback, Hex Parasite, Resourceful Defense
  `{4}{W}`).
- **Enlightened Tutor** (M1/M4): busca qualquer artefato ou encantamento
  (qualquer Saga, Resourceful Defense, Power Conduit, Strionic Resonator)
  e põe **no topo**. Com o Tom, isso escolhe a próxima Saga revelada.
- **Teferi's Protection**: o deck inteiro é tabuleiro de encantamentos. O
  pior cenário real é um wipe de encantamentos ou de tudo, e essa é a
  proteção mais completa. Ripples of Potential é a segunda linha: faz
  phase out das Sagas que ganharam marcador.

Considerados e deixados de fora: Smothering Tithe e Rhystic Study (valor
genérico, sem ligação com nenhum motor M1–M8), Seedborn Muse (só
aumentaria remoções de marcador, e o que limita o motor é adicionar
marcador, não remover).

## 4. Cortes do r66v (43 cartas: 39 nomes + 1 cópia a menos de Forest, Island, Mountain e Plains), cada um com o motivo relacional

**Anti-sinergia direta com o foco do deck:**
- **Sterling Grove**: "Other enchantments you control have **shroud**".
  Shroud impede o alvo **inclusive seu**. Nesting Grounds ("target
  permanent"), Goldberry ("another target permanent"), Resourceful
  Defense ("target permanent you control"), Clockspinning, Hex Parasite e
  Nexus Mentality **miram** a Saga, e todos parariam de funcionar nas
  Sagas enquanto o Grove estiver em campo. A parte de tutor ficou com o
  Enlightened Tutor, que também põe no topo.

**Pacote voltron** (plano de dano de comandante com o Tom): Rancor, Steel
of the Godhead, Helm of the Gods, Idolized, Dueling Grounds, Strength of
the Harvest, Nylea's Colossus. São encantamentos (alimentam M7), mas
nenhum mexe com Saga ou marcador. Cada slot foi para uma peça de M2–M5.

**Sagas mais fracas** (Kang Dynasty, Three Blind Mice, Vault 21: House
Gambit, Origin of the Hulk, The Huntsman's Redemption, The Hunger Tide
Rises, Rediscover the Way, Revival of the Ancestors, Ajani Fells the
Godsire, Michiko's Reign of Truth, Summon: Titan). **O Tom revela uma Saga
aleatória da biblioteca**, então a qualidade média das Sagas é
literalmente o valor do comandante. Entraram as Sagas com maior inclusão
no Bracket 3 do EDHREC: Elspeth Conquers Death 67%, The Eldest Reborn
67%, The Bath Song 61%, The Cruelty of Gix 60%, Summon: Knights of Round
53%, In the Darkness Bind Them 52%, Summon: Primal Odin 52%, Birth of the
Imperium 50%, Summon: Yojimbo 50%, Summon: Fenrir 45%, The First Iroan
Games 38%, Fable of the Mirror-Breaker 35%. Das 12 Sagas mantidas do r66v, as de maior
inclusão são Binding 78%, There and Back Again 77%, Kami War 74%, Kiora
70%, Bahamut 64% e War of the Last Alliance 41%.

**Redundância de enchantress ou de valor:** Tuvasa, Entity Tracker e
Eutropia deram lugar a Femeref Enchantress (compra quando uma Saga
**termina**, que é o evento central do deck) e Historian's Boon (retorno
por capítulo final).

**Tutor e recursão genéricos:** Wargate, All Suns' Dawn, Estrid, the
Masked (o −7 precisa de 3 turnos na mesa) e Rydia, Summoner of Mist. A
Rydia é temática (marcador de finality), mas a recursão de Saga já tem
Replenish, Resurgent Belief, Starfield e Hall of Heliod. **Rydia é a 1ª
opção de volta** se o usuário quiser mais recursão.

**Rampa redundante:** Dryad of the Ilysian Grove e Sylvan Caryatid (o
Prismatic Omen já dá todos os tipos básicos a todos os terrenos),
Wild Growth, Spelunking e Destiny Spinner. Entraram Sol Ring (80%),
Arcane Signet (82%) e Farseek (57%). O Farseek busca tríomes e shocks,
que têm os tipos Plains/Island/Swamp/Mountain.

**Terrenos:** Plaza of Heroes, Sea of Clouds, Bountiful Promenade,
Murmuring Bosk, Cascading Cataracts, Forbidden Orchard, Fabled Passage e
Bloodstained Mire saíram. Entraram Serra's Sanctum, Karn's Bastion
(proliferate num terreno, M2), **Urza's Saga** (Saga que o Tom revela;
o capítulo III busca Sol Ring ou Hex Parasite, custo `{1}`; e remover o
marcador a mantém viva, M3), 6 shocks, 5 fetches e as 10 tríomes. Sem
orçamento, então a melhor base possível.

## 5. Contagem por função

| Função | Qtd |
|---|---|
| Sagas (spells) | 24 (+ Urza's Saga no slot de terreno = **25 cartas Saga**) |
| Motor de marcadores (M2–M5) | 15 |
| Retorno por Saga terminada (M6) | 3 |
| Enchantress (M7) | 4 |
| Rampa | 10 |
| Recursão | 3 |
| Interação/proteção fora de Saga | 4 (as Sagas com remoção somam mais 11: Kami War, Binding, Bahamut, Helvault, Awaken, Galactus, ECD, Eldest Reborn, Birth, Primal Odin, Yojimbo) |
| Terrenos | 36 |
| Comandante | 1 |
| **Total** | **100** |

Game Changers: 3 (Serra's Sanctum, Enlightened Tutor, Teferi's Protection).
Nenhuma carta de destruição em massa de terreno, turno extra ou combo
infinito de 2 cartas. O Galactus destrói 1 terreno alvo por ataque, o que
não é destruição em massa.
