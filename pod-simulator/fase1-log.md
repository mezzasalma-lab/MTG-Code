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

## Resultado observado (20.000 partidas, seed 5.000.000+, 10 rodadas, começo alternado)

| | Vitórias | % |
|---|---|---|
| Megatron | 1.013 | 5,1% |
| Rat King Verminister | 11.810 | 59,0% |
| Sem eliminação em 10 rodadas | 7.177 | 35,9% |

Turno médio de eliminação (quando houve): 9,6.

**Leitura honesta:** isso é plausível, não um bug — Megatron é um motor
mais lento e dependente de montagem (comandante + combustível de
artefato), enquanto Rat King ataca com poder pequeno mas consistente
desde cedo. Numa corrida de 10 rodadas sem remoção nenhuma (Fase 2),
consistência bate explosão tardia mais vezes do que não. Ainda assim,
os números de "quem venceria" seguem limitados pelo que falta (ver
abaixo) — não é uma leitura definitiva de poder relativo.

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
