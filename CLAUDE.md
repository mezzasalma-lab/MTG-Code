# MTG-Code — regras permanentes deste repositório

## Regra #1 (obrigatória, sem exceção): TODA habilidade de TODA carta tem que estar implementada

A partir de 2026-09-14, por pedido explícito do usuário ("SEMPRE USE TODAS
AS HABILIDADES DE TODAS AS CARTAS DE HOJE EM DIANTE"), esta é a regra
permanente pra qualquer trabalho neste repositório — simulador novo,
correção pontual, ou adição/troca de carta numa lista existente:

**Toda carta (comandante + decklist) tem TODAS as suas habilidades reais
modeladas no simulador correspondente — nunca só a habilidade "principal"
ou a mais óbvia, nunca só metade de uma carta com 2+ cláusulas.** Isso
inclui: estáticos, ETB, morte/leaves-the-battlefield, ativadas (mesmo as
"secundárias" ou de baixo custo), Sagas (todos os capítulos), custos
alternativos reais (Flashback/Escape/Adventure/Evoke/Warp/Plot/Kicker),
gatilhos "whenever" (mesmo os que parecem redundantes com outra carta), e
qualquer cláusula extra além da primeira frase do oráculo.

### Como fazer isso de verdade (método já validado em 17 decks nesta sessão)

1. **Nunca confiar em memória de oráculo.** Buscar o texto real ao vivo via
   Scryfall (`POST /cards/collection` em lote pra maioria; `/cards/named?
   fuzzy=` individual pra MDFC/split/adventure que o batch erra) antes de
   julgar qualquer carta como "correta" ou "já implementada". Cartas levam
   errata (ex.: Skullclamp em 2023) — o texto que você lembra pode estar
   desatualizado.
2. **Ler o arquivo `.py` inteiro, não só a função relacionada à carta.**
   A maioria dos gaps reais encontrados nesta sessão eram implementação
   PARCIAL: a carta tinha código, mas só pra uma das suas 2+ cláusulas —
   invisível se você só grepar o nome da carta e olhar 1 ocorrência.
3. **Comparar clausula-por-cláusula**, cada frase/parágrafo do oráculo
   contra o código, marcando ✅ implementado, 🐛 corrigido nesta rodada, ou
   📊 estrutural (ver critério abaixo).
4. **Rodar uma varredura automatizada de "tags/nomes órfãos"** (definidos
   em `add()`/`CARD_DB`, nunca referenciados em nenhum dispatch fora
   dali) como primeira triagem — pega tags fantasma, mas NÃO pega
   implementação parcial (uma tag pode estar corretamente referenciada e
   ainda cobrir só parte da carta). As duas técnicas são complementares,
   nunca use só uma.

### Bugs recorrentes pra procurar especificamente (taxonomia confirmada nesta sessão)

- Habilidade ativada com `{T}` que nunca é bloqueada por doença de
  invocação, ou que compartilha o mesmo `{T}` de outra habilidade da MESMA
  fonte sem cobrar as duas.
- Custo de ativação (mana ou vida) nunca de fato deduzido — "mana
  fantasma".
- Efeito estático (anthem, CDA tipo "power = terrenos que controlo",
  contador acumulado) lido em UMA função mas não propagado pra TODAS as
  outras que leem poder/custo/mana daquele mesmo permanente.
- Gatilho compartilhado (morte de criatura, sacrifício, "sempre que você
  compra") ligado só em ALGUNS dos pontos reais do arquivo onde esse
  evento acontece, não em TODOS.
- Carta registrada no `CARD_DB`/dispatch sob um nome, checada em outro
  lugar com nome diferente/abreviado (nunca bate).
- Busca/fetch aplicado sem a restrição de tipo real do oráculo (ex.:
  Farseek só busca terreno básico + Plains/Island/Swamp/Mountain type,
  não "qualquer terreno").
- Custo alternativo real (Evoke, Flashback, Warp, Escape, Plot, Adventure)
  simplesmente inexistente no código — carta só é conjurada pelo custo
  cheio.
- Saga com só o capítulo I implementado, capítulos seguintes nunca
  avançam.
- Fórmula dinâmica real (escala com board state) achatada pra um número
  fixo aproximado quando o arquivo já rastreia os dados pra calcular o
  valor exato.

### Único critério válido pra NÃO implementar algo: impossibilidade estrutural, nunca julgamento de valor

- 📊 **N/A estrutural aceitável:** a habilidade depende de estado de
  OPONENTE real que este simulador goldfish-solo não modela (remoção
  visando permanente do oponente, "target opponent", vida real de
  oponente, bloqueio). Mesmo assim, sempre que possível, contar a
  carta/ativação como métrica proxy (ex.: "spells de interação
  conjurados") em vez de simplesmente ignorá-la.
- ❌ **NUNCA aceitável:** decidir não implementar por achar o efeito "de
  baixo valor esperado", "raro demais pra importar", ou qualquer variação
  de julgamento de valor subjetivo. Se a carta tem a habilidade e ela é
  fisicamente modelável neste motor (mesmo que rara), ela entra.
- Sempre documentar cada decisão de 📊 com a cláusula real do oráculo
  citada — nunca com a própria opinião de que "não vale a pena".

### Constrangimentos que continuam valendo

- Nunca adicionar/cortar carta de nenhuma decklist — correção é sempre
  só de implementação.
- Nunca fabricar estado de tabuleiro do oponente pra fazer uma habilidade
  "funcionar" — usar sempre a convenção de métrica proxy já estabelecida
  (contagem de uso, não efeito de board simulado).
- Toda correção precisa de validação real antes de comitar: smoke test
  (contagem de cartas, 0 desconhecidas/duplicadas), 2.000 partidas antes/
  depois (mesma seed) mostrando a métrica nova se mover na direção
  esperada, 20.000 partidas de regressão com 0 exceções, e teste unitário
  dirigido confirmando que cada correção específica dispara de verdade.
- Documentar toda rodada em `checklist-oraculo.md` (achados + correções +
  validação) e `goldfish-log.md` (números antes/depois) do deck
  correspondente.

Esta regra vale pra QUALQUER trabalho futuro neste repositório, incluindo
decks totalmente novos, não só correções em decks existentes.
