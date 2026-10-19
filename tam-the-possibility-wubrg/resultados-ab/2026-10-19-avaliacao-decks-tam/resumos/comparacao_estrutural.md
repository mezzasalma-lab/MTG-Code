# Estrutura: nosso deck x decks do Moxfield (categorias lidas do oráculo, heurística por regex)

Decks de referência (Moxfield, via EDHREC): 662; bracket 3: 326; 22+ planeswalkers: 318; bracket 3 e 22+ planeswalkers: 173. Média por deck (nosso = contagem exata). Regex sobre `oracle_text` sem o texto de lembrete: **são heurísticas, comparam o mesmo critério nos dois lados, e não são lista exaustiva de efeitos**.

| categoria | nosso | nosso com o pacote de 6 trocas (proposta) | todos Moxfield | Moxfield B3 | Moxfield 22+ PW | Moxfield B3 e 22+ PW |
|---|---|---|---|---|---|---|
| mana de não-terreno (rocha/criatura/aura; sem PW) | 8 | 7 | 6.5 | 6.6 | 6.1 | 6.3 |
| ramp que busca terreno (feitiço/instantâneo) | 0 | 0 | 2.0 | 2.1 | 1.8 | 1.9 |
| planeswalker que produz mana | 5 | 5 | 3.1 | 3.0 | 3.6 | 3.4 |
| contramágica | 0 | 0 | 1.3 | 1.2 | 1.0 | 0.9 |
| instantâneo (qualquer) | 1 | 3 | 6.9 | 6.6 | 5.6 | 5.6 |
| remoção pontual em instantâneo/flash | 0 | 1 | 2.1 | 2.1 | 1.7 | 1.8 |
| remoção em massa de criaturas | 6 | 6 | 3.7 | 4.0 | 4.0 | 4.1 |
| tutor (busca não-terreno) | 2 | 2 | 1.9 | 1.9 | 1.8 | 1.8 |
| compra de cartas (heurística) | 14 | 13 | 13.5 | 13.5 | 14.9 | 14.7 |
| proliferate ou dobra contadores | 8 | 10 | 8.9 | 8.9 | 8.2 | 8.1 |
| proteção de planeswalker / fase / indestrutível | 6 | 7 | 5.4 | 5.4 | 5.4 | 5.4 |
| ficha de Jace / cria planeswalker | 10 | 10 | 4.8 | 4.5 | 4.2 | 4.2 |
| terreno que entra virado (incondicional) | 6 | 6 | 4.1 | 4.0 | 4.2 | 3.9 |
| terreno com fetch | 5 | 5 | 4.4 | 4.4 | 4.5 | 4.7 |

| tipo (campo do EDHREC) | nosso | todos Moxfield | Moxfield B3 | Moxfield 22+ PW | Moxfield B3 e 22+ PW |
|---|---|---|---|---|---|
| planeswalker | 25 | 21.7 | 22.2 | 26.2 | 25.9 |
| creature | 12 | 13.2 | 13.0 | 11.9 | 11.9 |
| instant | 1 | 6.9 | 6.6 | 5.6 | 5.7 |
| sorcery | 4 | 6.4 | 6.5 | 5.5 | 5.7 |
| artifact | 8 | 7.0 | 7.2 | 6.6 | 6.7 |
| enchantment | 14 | 8.0 | 7.8 | 7.7 | 7.6 |
| land | 36 | 35.7 | 35.8 | 35.5 | 35.5 |
