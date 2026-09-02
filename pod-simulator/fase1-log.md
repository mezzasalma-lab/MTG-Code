# Fase 1 — Log de resultados e limitações

Motor: `pod_engine_v1.py`. Decks: Nekusar-Grixis vs Rat King Verminister
(escolhidos por serem os 2 simuladores mais simples do repositório, **não**
fazem parte da mesa alvo — ver `references/pod-simulator-design.md`).

## O que foi validado (objetivo real da Fase 1)

- **Dois simuladores solo totalmente independentes alternam turnos numa
  mesa compartilhada sem conflito** — cada um mantém seu próprio
  `GameState` nativo intacto, zero mudança nos 2 arquivos originais.
- **Vida real (40 cada), dano real entre os dois, eliminação real** —
  antes disso, "dano" em qualquer simulador desta biblioteca era um
  número solto sem alvo. Agora existe um oponente de verdade recebendo
  o dano e podendo ser eliminado.
- **20.000 partidas, 0 exceções, ~46s** — a arquitetura não trava nem
  degrada com o volume de jogo.

## Resultado observado (20.000 partidas, seed 5.000.000+, 10 rodadas, começo alternado)

| | Vitórias | % |
|---|---|---|
| Nekusar-Grixis | 13.275 | 66,4% |
| Rat King Verminister | 5.264 | 26,3% |
| Sem eliminação em 10 rodadas | 1.461 | 7,3% |

Turno médio de eliminação (quando houve): 9,0.

## ⚠️ Por que esse resultado NÃO deve ser lido como "Nekusar é mais forte"

Achado real ao construir isso (não decidido a priori): **nenhum dos 2
decks rastreia poder/toughness de criatura de forma completa**:

- Nekusar não tem plano de combate nenhum (`combat_step` dele é
  literalmente `pass`) — o oráculo real de "wheel"/drenar-por-compra
  está corretamente implementado.
- Rat King tem `base_power` só em algumas cartas (a maioria fica em 0
  por padrão) — o motor de valor real dele (tokens de Rato, Black
  Market Connections, sinergias de artefato) não se traduz em "poder de
  combate" no meu cálculo aproximado (`combat_power_this_turn()`), que
  hoje só soma `base_power` + 1 por token — um piso capenga, não uma
  leitura fiel do plano de jogo real do deck.

Ou seja: o placar acima mede **o motor de dano do Nekusar contra uma
aproximação capenga do combate do Rat King**, não os dois decks em pé
de igualdade. Essa distorção só desaparece quando o pod tiver decks com
combate real e P/T rastreado de verdade (Toph, na Fase 4) — até lá,
qualquer "quem ganha" saído daqui é sobre o motor de teste, não sobre o
Magic real.

## Limitações conhecidas (documentadas, não esquecidas)

- **Bloqueio é uma aproximação crua** (`estimate_block_reduction`): "1
  de dano abatido por criatura em campo do defensor", sem toughness
  real, sem escolha de QUAL criatura bloqueia. Fase 4 (quando a Toph,
  que já rastreia toughness em objetos `Permanent`, entrar) é o
  primeiro ponto natural pra refinar isso de verdade.
- **Sem interação real ainda** (remoção, contramágica) — isso é Fase 2,
  não estava no escopo da Fase 1.
- **`NUM_OPPONENTS` do Nekusar dividido por 3** pra virar "dano a 1
  oponente" — matematicamente correto pro Nekusar especificamente (ele
  já assume mesa de 4 e multiplica por 3 em cada efeito), mas é uma
  correção ad-hoc que só funciona porque eu sei ler o código dele; a
  Fase 4 vai precisar de um jeito mais sistemático de normalizar isso
  pros 4 decks novos.
