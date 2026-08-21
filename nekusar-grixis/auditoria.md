# Auditoria — Nekusar, the Mindrazer "V9 Wheel Breach Storm" (Grixis — U/B/R)

Auditoria feita via skill `mtg-commander`, dados em tempo real do Scryfall, usando o sistema oficial de Brackets/Game Changers.
Data: 2026-08-20

---

## 1. Validação formal

| Check | Resultado |
|---|---|
| Total de cartas | **100** (99 + comandante) ✅ |
| Singleton | ✅ nenhuma duplicata |
| Identidade de cor (Grixis) | ✅ nenhuma violação |
| Cartas banidas em Commander | ✅ nenhuma — inclusive as peças de fast mana/combo mais pesadas (Mox Opal, Underworld Breach, Dark Ritual, Cabal Ritual) estão todas legais |
| Erros de grafia/cartas não encontradas | ✅ nenhuma |

**Comandante:** Nekusar, the Mindrazer — `{2}{U}{B}{R}` — Legendary Creature Zombie Wizard.
Todo jogador compra uma carta extra no seu draw step; sempre que um oponente compra uma carta, Nekusar causa 1 de dano a ele. É literalmente o motor central do arquétipo "wheel damage" que essa lista executa.

---

## 2. Contagem de Game Changers — correção em relação ao que você declarou

Você anotou 7 Game Changers no cabeçalho da lista. Conferindo carta a carta contra a lista oficial (via Scryfall `is:gamechanger`):

**Real: 8 Game Changers** — Orcish Bowmasters, Underworld Breach, Demonic Tutor, Vampiric Tutor, Imperial Seal, Force of Will, The One Ring, **e Cyclonic Rift** (que ficou de fora da sua contagem).

Não muda a classificação de bracket (ambos os números estão muito acima do teto de 3 do Bracket 3), mas vale corrigir pra próxima vez que for documentar.

---

## 3. Base de mana

- **Terrenos: 36** — bem no meio do ideal (36-38).
- Mana base de altíssima qualidade pra 3 cores: 3 duais originais (Badlands, Underground Sea, Volcanic Island), shocklands completas do Grixis (Blood Crypt, Steam Vents, Watery Grave), 7 fetchlands, Command Tower, Exotic Orchard, City of Brass. Praticamente zero risco de tropeço de cor.
- Terrenos de utilidade fortes: Otawara Soaring City (bounce como land), Cephalid Coliseum (draw/mill), Mikokoro Center of the Sea (draw simétrico), Geier Reach Sanitarium (madness/wheel-adjacent).

Não há nada a corrigir aqui — mana base de nível de torneio.

---

## 4. Curva de mana

CMC médio (sem terrenos, sem comandante): **2.38** — muito baixo, como esperado de um deck de alto poder que quer proteger seu plano e executar rápido.

| CMC | Qtde |
|---|---|
| 0 | 2 (Pact of Negation, Mox Opal) |
| 1 | 12 |
| 2 | 25 |
| 3 | 11 |
| 4 | 11 |
| 5 | 1 (Force of Will) |
| 6 | 1 (Echo of Eons) |

Curva extremamente baixa e concentrada em 1-2 mana — típico de decks de Bracket 4/cEDH que priorizam interação barata e consistência sobre ameaças grandes.

---

## 5. O motor real do deck: dano em massa via "wheel"

**Correção em relação à versão anterior:** eu tinha deixado de fora **Sheoldred, the Apocalypse** (você pegou certo) e também o **Orcish Bowmasters** — os dois são payoffs de dano-por-compra tão diretos quanto Underworld Dreams, só que eu tinha classificado ambos só como "criatura boa"/"Game Changer" sem conectar ao subtema de wheel damage. Refiz a varredura completa da lista carta a carta procurando qualquer gatilho de "draw"/"discard". Compilado abaixo.

### 5.1 — Todas as fontes de DANO/PERDA DE VIDA por compra (9 payoffs)

| Carta | Gatilho exato |
|---|---|
| **Nekusar, the Mindrazer** (comandante) | 1 dano por compra de oponente + todo mundo compra 1 extra no draw step |
| **Orcish Bowmasters** | 1 dano a qualquer alvo por compra de oponente (exceto a 1ª do draw step) + amass Orc 1 — dispara na entrada também |
| **Sheoldred, the Apocalypse** | oponente perde 2 de vida por compra dele; você ganha 2 de vida por compra sua — dano E vida ao mesmo tempo |
| **Underworld Dreams** | 1 dano por compra de oponente |
| **Spiteful Visions** | 1 dano por compra de QUALQUER jogador (inclusive você) + todo mundo compra 1 extra no draw step |
| **Phyrexian Tyranny** | 2 de vida perdida por compra de qualquer jogador, a menos que pague {2} |
| **Razorkin Needlehead** | 1 dano por compra de oponente |
| **Scrawling Crawler** | 1 de vida perdida por compra de oponente + todo mundo compra 1 extra no upkeep |
| **Liliana's Caress** | 2 de vida perdida por DESCARTE de oponente (cobre a metade "discard" dos wheels, não a compra) |

**Bloodchief Ascension** não é um payoff direto de compra — ela conta quest counters quando um oponente perde 2+ vida no turno (ou seja, é alimentada pelos 8 payoffs acima) e, com 3+ contadores, vira um extort/drain repetível. É uma segunda camada em cima do dano que os outros já causam, não uma 10ª fonte independente.

**Matemática de mesa:** com Nekusar + Orcish Bowmasters + Sheoldred + Underworld Dreams + Spiteful Visions + Phyrexian Tyranny + Razorkin Needlehead + Scrawling Crawler todos em campo (cenário extremo, mas é pra isso que a lista foi montada), cada compra de UM oponente já dispara 1+1+2+1+1+2+1+1 = **10 de dano/perda de vida numa única compra**. Um Wheel of Fortune faz cada oponente comprar 7 — o suficiente pra matar a mesa inteira de uma vez em muitos casos, mesmo com só metade desse board montado.

### 5.2 — Todas as fontes de WHEEL / draw-discard em massa (15 cartas)

**Wheels "cheios" (descarta mão inteira, compra 7 ou equivalente):**
1. Wheel of Fortune — todos descartam a mão, compram 7
2. Windfall — todos descartam, compram = maior descarte
3. Winds of Change — todos embaralham a mão na biblioteca, compram o mesmo tanto
4. Echo of Eons — todos embaralham mão+cemitério na biblioteca, compram 7 (tem flashback, ou seja pode ser jogada 2x do próprio cemitério)
5. Wheel and Deal — oponentes alvo descartam e compram 7; você compra 1
6. Magus of the Wheel — sacrifica a criatura: todos descartam e compram 7 (Wheel of Fortune numa criatura, portanto também vulnerável a remoção de criatura antes de ativar)
7. Jace's Archivist — ativação repetível: todos descartam e compram = maior descarte (é um Windfall reutilizável todo turno que sobreviver)
8. Wheel of Misfortune — híbrida: causa dano igual ao maior número escolhido a quem escolheu esse número, E faz quem não escolheu o menor número descartar e comprar 7

**Wheels "parciais"/passivos (draw extra recorrente, não descarta a mão toda):**
9. Nekusar (comandante) — todos compram 1 extra por turno
10. Spiteful Visions — todos compram 1 extra por turno
11. Scrawling Crawler — todos compram 1 extra por turno
12. Teferi's Puzzle Box — no draw step de cada jogador, a mão vai pro fundo da biblioteca e ele compra a mesma quantidade (efetivamente uma nova mão aleatória todo turno, pra todo mundo, todo turno — o wheel mais "automático" da lista)

**Wheels simétricos menores (terrenos/utilidade):**
13. Mikokoro, Center of the Sea — todos compram 1 carta (dispara todos os payoffs "any player draws" como Spiteful Visions/Phyrexian Tyranny)
14. Geier Reach Sanitarium — todos compram 1 e descartam 1
15. Cephalid Coliseum — (threshold, precisa 7+ cartas no cemitério) um jogador alvo compra 3 e descarta 3

**Mindcrank** continua como camada extra: qualquer perda de vida causada pelos payoffs da seção 5.1 também mila o oponente na mesma quantidade — o mesmo wheel que quase mata a mesa também avança um plano B de decking.

---

## 6. Combo e recursão — linha de "storm" real

- **Underworld Breach + Past in Flames** — dá escape (recast do cemitério pagando custo + exilar 3 cartas) pra toda mágica não-terreno no cemitério. Combinado com rituais baratos (Dark Ritual, Cabal Ritual) e os próprios wheels (que enchem o cemitério toda vez que alguém descarta), isso pode virar uma sequência de vários wheels e rituais recastados no mesmo turno — cada recast dispara os payoffs de dano de novo.
- **Brain Freeze** com Storm — se você já conjurou várias mágicas baratas no turno (rituais, wheels, contramágicas), Brain Freeze pode milhar um oponente inteiro numa cópia múltipla.
- **Animate Dead / Reanimate** — reanimação clássica, pode trazer Sheoldred ou qualquer ameaça relevante do cemitério (inclusive do próprio ecossistema de mill que Mindcrank/Brain Freeze geram).

Isso não é um combo de 2 peças isolado — é uma cadeia de recursão que o deck monta ao longo do jogo, mas com potencial de virar uma sequência explosiva de um turno só quando as peças se alinham.

---

## 7. Proteção e remoção — 🟢 nível de torneio

**9 contramágicas**: Force of Will, Mana Drain, Counterspell, Arcane Denial, Swan Song, Flusterstorm, Pact of Negation, Mindbreak Trap, An Offer You Can't Refuse. Isso é o pacote de contramágica mais denso que já vi nas suas listas — cobre praticamente qualquer tipo de resposta que a mesa possa jogar contra o seu wheel.

**Remoção/redirecionamento**: Cyclonic Rift (bounce em massa, Game Changer), Deadly Rollick (exílio, geralmente de graça), Feed the Swarm, Deflecting Swat (redireciona spell/habilidade, geralmente de graça com comandante em campo).

**Stax leve/proteção estrutural**: Cursed Totem (desliga habilidades ativadas de criatura — protege o plano de respostas baseadas em criatura), Defense Grid (taxa mágicas do oponente fora do turno dele, sem te afetar no seu turno), Hexing Squelcher (torna suas mágicas e criaturas incontráveis/com ward), Propaganda (taxa ataques).

Esse é, de longe, o deck mais protegido e mais denso em interação instantânea dos 6 que você já me trouxe.

---

## 8. Tutores — 5, todos fortes — confirma Bracket 4

Demonic Tutor, Vampiric Tutor, Imperial Seal, Beseech the Mirror, Solve the Equation. Todos irrestritos ou quase irrestritos. A regra oficial pede "tutores raros" pra Bracket 1-3 — 5 tutores de alto poder, sozinho, já desqualificaria esse deck de Bracket 3 mesmo que a contagem de Game Changers fosse menor. Isso reforça a autoclassificação de Bracket 4 que você já tinha feito.

---

## 9. Estimativa de Bracket — CONFIRMADA em Bracket 4

Sua autoclassificação como **Bracket 4** está correta, e não é só por causa da contagem de Game Changers (8, bem acima do teto de 3). Três sinais independentes confirmam:

1. **8 Game Changers** (Orcish Bowmasters, Underworld Breach, Demonic Tutor, Vampiric Tutor, Imperial Seal, Force of Will, The One Ring, Cyclonic Rift) — sozinho já ultrapassa o teto de Bracket 3.
2. **5 tutores irrestritos** — muito além de "raros", que é o teto pra Bracket 1-3.
3. **9 contramágicas + pacote de stax leve** — nível de interação incompatível com Bracket 2-3, que preveem "sem restrições" só a partir do Bracket 4.

Esse é o primeiro deck da sua coleção que é genuinamente Bracket 4 por múltiplos critérios independentes, não só no limite como o Hei Bai. Ele provavelmente até flerta com cEDH dependendo da mesa — a estrutura (wheel damage + storm de recursão + contramágica pesada + tutores) é reconhecidamente um arquétipo competitivo do formato.

---

## 10. Sugestões de melhoria

O deck está extremamente bem construído pro que se propõe — não há gap estrutural. Únicos pontos de polimento:

1. **Corrigir a contagem de Game Changers no cabeçalho** (7→8, adicionar Cyclonic Rift) pra documentação futura.
2. Se quiser subir ainda mais o teto (cEDH de verdade), considerar mais fast mana de zero mana (Mox Diamond, Chrome Mox — ambas Game Changers, então isso empurraria a contagem pra 10) e reduzir levemente o número de peças "narrow" (ex: Hexing Squelcher é boa mas situacional) por mais tutores/proteção de combo.
3. Avisar seu grupo antes de sentar com esse deck — ele é visivelmente mais forte que os outros 6 (Bracket 3) que você já registrou.

---

## Links

- EDHREC: https://edhrec.com/commanders/nekusar-the-mindrazer
- Tema Wheels: https://edhrec.com/themes/wheels
- Moxfield (criar/comparar): https://moxfield.com/decks/new
