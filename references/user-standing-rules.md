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

---

<!-- Adicionar novas regras permanentes abaixo conforme o usuário as
     estabelecer explicitamente. Cada entrada deve citar a frase literal
     do usuário quando possível, pra não perder o contexto original. -->
