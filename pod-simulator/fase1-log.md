# Fase 1 — Log de resultados e limitações

Motor: `pod_engine_v1.py`. Par padrão atual: **Megatron vs Rat King
Verminister**. Nenhum dos dois faz parte da mesa alvo (Edgar
Markov/Ur-Dragon/Toph/Maralen) — ver `references/pod-simulator-design.md`.

## Histórico: por que trocou de Nekusar pra Megatron

A primeira versão usava Nekusar-Grixis vs Rat King. Resultado: Nekusar
venceu 66,4% em 20.000 partidas — mas isso não media força real, media
"motor de drenar bem modelado" contra "combate mal modelado": Nekusar
não tem plano de combate nenhum (`combat_step` dele é literalmente
`pass`), então toda vitória dele vinha só do lado bem-coberto pelos
dados (drenar via gatilho de compra). Pedido do usuário (2026-09-02):
*"Preciso de um modelo que tenha sempre o combate como teste também,
senão o Nekusar ganha mais mesmo."*

Troquei Nekusar por **Megatron** — tem combate real e central
(`megatron_combat()`, poder de ataque genuíno rastreado em 22
criaturas, do próprio comandante a finalizadores como Kozilek/Ulamog/
Galactus). Nekusar continua importável no motor (não removido), só
deixou de ser o par padrão.

### Achado real ao fazer a troca: risco de contar dano 2x

O Megatron já modela o próprio combate DENTRO do `play_turn()` dele —
só o comandante ataca de verdade no desenho do próprio deck (Rakdos the
Muscle, Steel Seraph, Osgir etc. são peças de valor/combustível, nunca
atacam). Minha camada genérica de combate (soma o poder de toda
criatura pronta) teria contado o comandante 2x e inventado ataques que
o deck nunca faz. Corrigido com `COMBAT_MODELED_INTERNALLY` — decks
onde o combate já está embutido no `proxy_damage_total` (Megatron)
zeram a camada genérica; decks sem isso (Nekusar, Rat King) continuam
usando a camada genérica pra preencher o buraco real.

### Achado real #2: poder dinâmico do Rat Colony nunca era usado (pedido do usuário 2026-09-02)

Pergunta do usuário: *"Como Rat king tem pouquíssimo poder de criatura,
se cada Rat Colony ganha +1/0 por rato em campo?"* — motivo real: o
arquivo do Rat King já tem `rat_colony_power(state)` calculando certo
("2 + 1 por cada OUTRO Rat que você controla"), mas essa função **nunca
era chamada em lugar nenhum** — nem no simulador solo original (decisão
documentada e válida lá: "sem combate real, sem oponente" — não há pra
quem atacar mesmo) nem no meu `creature_power()` do motor de mesa, que
usava só o poder impresso estático (2) — um bug real aqui, já que agora
EXISTE um oponente pra atacar.

Rat Colony é carta de **cópias ilimitadas** (24x na lista) — com N
cópias em campo, o poder total delas sozinhas é `N × (2 + N - 1)`,
crescimento quadrático. Confirmado numa partida de teste: **23 cópias
de Rat Colony simultâneas em campo**, board genuinamente enorme.
Corrigido com uma tabela de overrides de poder dinâmico por carta
(`DYNAMIC_POWER_OVERRIDES`), extensível pra outras cartas parecidas que
os 4 decks da mesa alvo devem ter.

## Resultado observado (20.000 partidas, seed 5.000.000+, 10 rodadas, começo alternado, POS fix do Rat Colony)

| | Vitórias | % |
|---|---|---|
| Megatron | 632 | 3,2% |
| Rat King Verminister | 16.344 | 81,7% |
| Sem eliminação em 10 rodadas | 3.024 | 15,1% |

Turno médio de eliminação (quando houve): 9,0. Dano de combate médio do
Rat King por partida: 57,2 (mediana 45,0, máximo observado 3.623 numa
partida com board de Rat Colony saindo do controle).

**Leitura honesta:** o fix mudou o resultado de forma real e grande (Rat
King foi de 59,0% pra 81,7%) — não é ruído, é a diferença entre usar o
poder real de uma carta central do deck vs um valor estático errado.
Megatron continua perdendo a maioria por ser um motor mais lento e
dependente de montagem; Rat King, além de consistente, agora tem seu
verdadeiro teto de poder de combate refletido. Ainda assim, os números
seguem limitados pelo que falta (bloqueio aproximado, sem interação
real) — não é uma leitura definitiva de poder relativo entre os 2.

## O que foi validado (objetivo real da Fase 1)

- Dois simuladores solo totalmente independentes alternam turnos numa
  mesa compartilhada sem conflito, sem tocar nos arquivos originais.
- Vida real (40 cada), dano real com alvo real, eliminação real.
- **Combate real dos dois lados** — o pedido específico desta rodada:
  nenhum dos dois decks do par padrão tem combate "inventado" nem
  "ignorado", cada um usa o motor de dano que reflete seu desenho real
  (Megatron via seu próprio `combat_step`, Rat King via a camada
  genérica que preenche a ausência real de modelagem de combate lá).
- 20.000 partidas, 0 exceções, ~34s.

## Limitações conhecidas (documentadas, não esquecidas)

- **Bloqueio ainda é uma aproximação crua** (`estimate_block_reduction`):
  sem toughness real rastreada nesses decks, "1 de dano abatido por
  criatura em campo do defensor" — só decks com objetos `Permanent`
  (Toph, Fase 4) têm P/T real pra um bloqueio matemático de verdade.
- **35,9% de jogos sem decisão em 10 rodadas** é alto — pode precisar de
  mais rodadas pra um sinal mais limpo, ou é genuinamente como esse
  confronto específico se comporta (motor lento vs grind consistente).
  Não investigado a fundo ainda, registrado como próximo ponto de
  atenção se o padrão persistir com outros pares.
- **Sem interação real ainda** (remoção, contramágica) — Fase 2, fora do
  escopo daqui.
- **`NUM_OPPONENTS` dividido por 3** pra Nekusar/Megatron (ambos assumem
  mesa de 4) — matematicamente correto pra esses 2 especificamente, mas
  ainda uma correção ad-hoc por deck, não um mecanismo sistemático.
