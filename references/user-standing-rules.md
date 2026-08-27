# Regras permanentes do usuário (mezzasalma)

> Espelho versionado deste repositório do arquivo canônico em
> `references/user-standing-rules.md` dentro do skill `mtg-commander`
> (`/root/.claude/skills/synced/mtg-commander/`, fora do controle de versão
> deste repo). O skill é a cópia que eu realmente consulto antes de agir —
> esta aqui existe pra ficar versionada e visível no seu histórico do
> GitHub. Se as duas divergirem, atualize as duas juntas.


Instruções dadas explicitamente pelo usuário ao longo de sessões de trabalho
com decks de Commander, que valem **sempre**, não só na conversa em que foram
ditas. Checar este arquivo no início de qualquer trabalho novo com decks
desse usuário.

---

## 1. Nunca inventar dado, sempre citar fonte oficial

Citação literal do usuário: *"Pare de me elogiar e sempre me diga as fontes
oficiais das suas informações, não quero que vc crie ou invente nada, mesmo
que eu não peça explicitamente, ok?"*

- Toda afirmação sobre uma carta (custo, texto, legalidade, preço) precisa
  vir de uma consulta real à API do Scryfall (ou cache local dela),
  citada explicitamente — nunca de memória.
- Toda afirmação sobre popularidade/inclusão de carta num arquétipo precisa
  vir de uma consulta real ao EDHREC — nunca de memória ou "impressão".
- Nenhum elogio gratuito ("ótima pergunta", "excelente ideia") — só
  informação e análise direta.
- Qualquer número que dependa de uma premissa não-verificável (ex: quantos
  spells um oponente conjura por turno num goldfish solo) precisa ser
  marcado explicitamente como premissa assumida, não como dado real — e
  a premissa deve ser validada pelo usuário antes de virar "confirmada".

## 2. Toda vez que um deck for adicionado, rodar a auditoria completa

Citação literal do usuário: *"sempre que eu adicionar um deck aqui RODE A
AUDITORIA COMPLETA"*.

- Não esperar o usuário pedir a auditoria separadamente — ela é automática
  assim que uma lista de deck nova é salva.
- Auditoria completa = checklist de `references/commander-rules.md#analise`
  (identidade de cor, terrenos, curva, ramp, draw, remoção, win conditions,
  sinergia, bracket) com tudo sourced via Scryfall/EDHREC.

## 3. Qualquer efeito de carta com regra estrutural precisa de implementação real em simulador, não só tag

Ver `references/goldfish-sim-card-rules.md` — lista de cartas específicas
(Roaming Throne é a primeira) cujo efeito precisa estar em código de
verdade em **qualquer** simulador de goldfish que as inclua, não só uma tag
decorativa. Checar essa lista antes de considerar um simulador completo.

## 4. Toda regra permanente criada numa sessão tem que ser espelhada no GitHub também

Citação literal do usuário (2026-08-21): *"TODA E QUALQUER REGRA QUE EU
CRIAR AQUI TEM QUE SER COPIADA NO GITHUB TB!"*

- O skill (`/root/.claude/skills/synced/mtg-commander/`) é onde a regra é
  realmente consultada durante o trabalho — mas não é versionada no
  controle de versão do usuário.
- Toda regra permanente registrada aqui precisa ter uma cópia espelhada
  em `references/` na raiz do repositório `MTG-Code` do usuário, commitada
  e enviada pro GitHub. Este arquivo (`user-standing-rules.md`) e o
  `goldfish-sim-card-rules.md` são os dois primeiros exemplos.
- Se as duas cópias divergirem (uma foi atualizada e a outra não),
  atualizar as duas juntas antes de continuar qualquer trabalho.

## 5. Cartas protegidas contra corte, por deck (nunca sugerir cortar, mesmo com baixa sinergia)

Cartas que o usuário vetou explicitamente, independente do que qualquer
métrica (EDHREC, matriz de sinergia, goldfish) mostrar sobre elas.

**Thranduil, the Elvenking (thranduil-sultai):**
- **Roaming Throne** e **Maralen, Fae Ascendant** — *"Nem pensar em tirar o
  trono ou a Maralen"* (stop hook feedback, sessão 2026-08-20/21).
- **Thranduil's Company** — *"Não vamos tirar o Thranduil's Company em
  hipótese alguma."* (2026-08-21), mesmo sendo o único card do deck sem
  nenhuma proteção em nenhuma dimensão da matriz de sinergia
  (`thranduil_synergy_matrix.py`) — vetada por decisão direta do usuário,
  não por análise.

## 6. Auditoria de manabase: sempre contar Command Tower, fetches, Arcane Signet e outros fixers flexíveis como fontes reais

Citação literal do usuário (2026-08-24): *"Sempre que vc for avaliar a
manabase, lembre de contar Command Tower, os fixers (fetch lands, arcane
signet e outros corretores como Dryad) daqui para frente, ok?"*

Contexto: numa auditoria de pips do Hei Bai, um cálculo inicial contou
fetch lands como fontes de só as 2 cores "nomeadas" no texto delas (ex:
Arid Mesa = R ou W), subestimando o alcance real. Fetches buscam por
**tipo** de terreno, não só básica — então também pegam qualquer
dual/triome que carregue aquele tipo. Testado no Hei Bai: as 8 fetches da
lista, cada uma, alcançavam as 5 cores, porque a manabase tinha duais/
triomes multicoloridos suficientes conectando todo tipo básico a todo o
resto.

- **Command Tower, Arcane Signet** (e qualquer fonte "any color in your
  commander's color identity") contam como fonte de TODAS as cores da
  identidade do comandante, não de uma cor só.
- **Fetch lands**: não contar só as 2 cores nomeadas no texto. Cruzar
  contra `type_line` de TODO terreno da lista (duais, triomes, básicas)
  pra achar quais compartilham um dos 2 tipos buscados, e somar a união
  de cores de todos esses alvos — não só o par nomeado.
- **Fixers estáticos que mudam terrenos** (ex: Dryad of the Ilysian
  Grove — "Lands you control are every basic land type"; Yavimaya,
  Cradle of Growth — "Each land is a Forest in addition to its other
  land types") contam como fonte real de cada cor que passam a habilitar,
  uma vez em campo — mas são condicionais (precisam resolver primeiro),
  então registrar separado da contagem "sempre disponível desde o turno 1"
  (terrenos básicos, duais, fetches, rocks), não misturado nela.
- Toda contagem de fonte-por-cor precisa citar de qual das categorias
  acima veio (fixa incondicional vs. condicional-uma-vez-resolvida), não
  só o número final — pra não repetir o erro de subestimar (ou
  superestimar) o alcance real da manabase.

## 7. Combo achado no Commander Spellbook: sempre calcular turno/probabilidade real antes de tratar como achado de Bracket

Citação literal do usuário (2026-08-27), depois de eu alarmar sobre 2
combos infinitos "já montados" no Ur-Dragon sem checar viabilidade: *"Não
viaja, quando eu consigo executar esses combos? Algum antes do turno
8?"* — e depois: *"Adicione nas regras a questão do turno dos combos e
de final do jogo dos brackets na sua análise."*

Contexto: Commander Spellbook (`backend.commanderspellbook.com`) confirma
se uma combinação de cartas FUNCIONA nas regras, dado que todas estão na
lista — não diz nada sobre quão rápido ou provável é montá-la numa
partida real. Achar um combo "included" lá não é, por si só, motivo pra
reclassificar Bracket. No caso do Ur-Dragon, calculei a probabilidade
hipergeométrica real de ter as peças específicas na mão (sem tutor
dedicado buscando as duas juntas) — deu **1,9% até o turno 8** pro combo
de 2 cartas mais provável, **0,23%** pro de 3 cartas — antes ainda de
contar mana, haste, e sobreviver a remoção numa mesa real de 4
jogadores. Não é um "combo turno 3-4", é um evento de cauda.

**Daqui pra frente, sempre que um combo for encontrado via Commander
Spellbook (ou qualquer fonte que só verifique legalidade/funcionamento,
não velocidade):**
- Calcular a probabilidade hipergeométrica real de ter TODAS as peças na
  mão até um turno de referência (6, 8, 10, 12), considerando o tamanho
  real do deck e se existe algum tutor que busque especificamente essas
  peças (o que muda a conta radicalmente).
- Checar custo de mana de cada peça e se alguma tem haste/enabler de
  haste já na lista — combos que exigem sobreviver um ciclo de turno
  sem summoning sickness são mais lentos ainda do que a probabilidade de
  draw sozinha sugere.
- Só tratar um combo como relevante pro critério oficial de Bracket
  ("combo infinito de 2 cartas cedo no jogo") se a análise acima mostrar
  que ele é rápido E provável — não só "existe" — citando o número
  calculado, não uma impressão.
- Registrar esse cálculo explicitamente na auditoria/log, não só a
  conclusão — pra não repetir o erro de alarmar sobre reclassificação de
  Bracket antes de checar viabilidade real.

---

<!-- Adicionar novas regras permanentes abaixo conforme o usuário as
     estabelecer explicitamente. Cada entrada deve citar a frase literal
     do usuário quando possível, pra não perder o contexto original. -->
