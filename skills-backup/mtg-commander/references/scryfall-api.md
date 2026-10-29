# Scryfall API — Referência de Uso

API base: `https://api.scryfall.com`
Documentação oficial: https://scryfall.com/docs/api

A API é gratuita, sem autenticação, com rate limit gentil (10 req/s). Respeitar 50-100ms entre chamadas.

---

## Endpoints Principais

### Busca por nome exato
```
GET https://api.scryfall.com/cards/named?exact=Sol+Ring
```
Retorna: objeto carta único ou erro 404.

### Busca por nome fuzzy (parcial/aproximado)
```
GET https://api.scryfall.com/cards/named?fuzzy=sol+ring
```
Útil quando o usuário não lembra o nome exato.

### Busca por critérios (search)
```
GET https://api.scryfall.com/cards/search?q=QUERY&order=edhrec&dir=desc
```
Retorna: lista paginada de cartas. Campo `data` contém array, `has_more` indica mais páginas, `next_page` tem URL da próxima.

Parâmetros úteis:
- `order=edhrec` — ordena por popularidade no EDHREC
- `order=usd` — ordena por preço
- `dir=asc` / `dir=desc`
- `page=2` — paginação

---

## Sintaxe de Queries Scryfall

### Filtros de cor
- `c:g` — verde
- `c:gu` — verde E azul (ambas)
- `c:g OR c:u` — verde OU azul
- `c<=gub` — contém no máximo essas cores
- `c=wubrg` — exatamente 5 cores (WUBRG)
- `id:gub` — identidade de cor (inclui incolor)

### Filtros de tipo
- `t:creature`
- `t:instant`
- `t:sorcery`
- `t:enchantment`
- `t:artifact`
- `t:planeswalker`
- `t:land`
- `t:legendary` — legendárias
- `t:"legendary creature"` — criaturas lendárias (comandantes)

### Filtros de CMC / Mana
- `cmc=3` — exatamente 3
- `cmc<=2` — 2 ou menos
- `cmc>=5` — 5 ou mais
- `m:{G}{G}` — custo contém dois manas verdes

### Filtros de texto (oracle)
- `o:flying` — tem a palavra flying no texto
- `o:"enters the battlefield"` — texto exato
- `o:"draw a card"` — compra de carta
- `o:"add {G}"` — produz mana verde
- `o:"whenever you cast"` — trigger de conjuração
- `o:trample o:haste` — AND implícito
- `o:trample OR o:haste` — OR explícito

### Filtros de formato
- `f:commander` — legal em Commander
- `f:cedh` — não existe, usar `f:commander` com ban list manual
- `banned:commander` — banidas em Commander
- `is:commander` — pode ser usada como comandante (criatura lendária ou walker com habilidade)

### Filtros de preço
- `usd<=1` — até $1 dólar
- `usd>=10` — $10 ou mais
- `usd=0.50` — exatamente $0.50
- `eur<=2` — até €2

### Filtros de raridade
- `r:common` / `r:c`
- `r:uncommon` / `r:u`
- `r:rare` / `r:r`
- `r:mythic` / `r:m`

### Filtros de poder/resistência
- `pow>=5` — poder 5 ou mais
- `tou<=2` — resistência 2 ou menos
- `pow=tou` — poder igual à resistência

### Filtros de set
- `s:MH3` — Modern Horizons 3
- `s:CMR` — Commander Legends
- `s:LTR` — Lord of the Rings

### Combinações úteis para Commander

**Ramp verde barato:**
```
c:g t:instant OR t:sorcery o:"land" cmc<=3 f:commander
```

**Wipes brancos:**
```
c:w o:"destroy all" OR o:"exile all" t:instant OR t:sorcery f:commander
```

**Criaturas com etb útil baratas:**
```
c:b t:creature o:"enters the battlefield" cmc<=3 f:commander order=edhrec
```

**Tutores pretos:**
```
c:b o:"search your library" t:sorcery OR t:instant f:commander order=edhrec
```

**Budget ramp (abaixo de $2):**
```
c:g o:"add" t:instant OR t:sorcery cmc<=3 usd<=2 f:commander
```

**Comandantes de uma cor:**
```
t:"legendary creature" id=g is:commander f:commander order=edhrec
```

**Comandantes multicoloridos:**
```
t:"legendary creature" id:gub is:commander f:commander
```

---

## Campos Importantes no Retorno JSON

```json
{
  "name": "Sol Ring",
  "mana_cost": "{1}",
  "cmc": 1.0,
  "type_line": "Artifact",
  "oracle_text": "...",
  "colors": [],
  "color_identity": [],
  "legalities": {
    "commander": "legal",
    "vintage": "restricted"
  },
  "prices": {
    "usd": "1.50",
    "usd_foil": "5.00",
    "eur": "1.20"
  },
  "edhrec_rank": 1,
  "image_uris": {
    "normal": "https://cards.scryfall.io/normal/...",
    "small": "https://cards.scryfall.io/small/..."
  },
  "purchase_uris": {
    "tcgplayer": "https://...",
    "cardmarket": "https://..."
  },
  "related_uris": {
    "edhrec": "https://edhrec.com/cards/sol-ring"
  }
}
```

### Campos mais usados:
- `name` — nome da carta
- `mana_cost` — custo de mana
- `cmc` — custo mana convertido
- `oracle_text` — texto de regras
- `type_line` — linha de tipo
- `colors` — cores da carta
- `color_identity` — identidade de cor (inclui text box)
- `legalities.commander` — `"legal"`, `"not_legal"`, `"banned"`
- `prices.usd` — preço em dólar (pode ser null)
- `prices.eur` — preço em euro
- `edhrec_rank` — ranking de popularidade no EDHREC (menor = mais popular)
- `related_uris.edhrec` — link direto para página EDHREC da carta

---

## Erros Comuns

| Código | Significado |
|--------|-------------|
| 404 | Carta não encontrada |
| 422 | Query inválida |
| 429 | Rate limit excedido (aguardar) |

---

## URLs EDHREC — Construção Manual

Como o EDHREC não tem API pública, construir URLs manualmente:

**Página do comandante:**
```
https://edhrec.com/commanders/NOME-EM-KEBAB-CASE
```
Exemplos:
- Korvold → `https://edhrec.com/commanders/korvold-fae-cursed-king`
- Atraxa → `https://edhrec.com/commanders/atraxa-praetors-voice`
- Edgar Markov → `https://edhrec.com/commanders/edgar-markov`

**Regras de conversão para kebab-case:**
1. Letras minúsculas
2. Espaços viram hifens
3. Vírgulas, apóstrofes e caracteres especiais são removidos
4. Acentos removidos (Ä→a, é→e, etc.)

**Página de tema:**
```
https://edhrec.com/themes/TEMA
```
Ex: `https://edhrec.com/themes/aristocrats`, `https://edhrec.com/themes/tokens`

**Página de tribal:**
```
https://edhrec.com/tribes/CRIATURA
```
Ex: `https://edhrec.com/tribes/elf`, `https://edhrec.com/tribes/vampire`

**Página de carta:**
```
https://edhrec.com/cards/NOME-EM-KEBAB-CASE
```
(ver também `related_uris.edhrec` no retorno da Scryfall API)
