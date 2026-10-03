# Lote anterior (Blank Card como artefato MV 99) — mantido para auditoria; números IDÊNTICOS aos atuais

Primeiro lote da ablação e do A/B (2026-10-03) do Vihaan, rodado com a "Blank Card" (carta inconjurável usada como controle) declarada como **artefato MV 99**.
Nos dados do Megatron isso inflava o dano (o Megatron sacrificava a Blank trazida ao campo como combustível). **No Vihaan não mudou nada**: as tabelas
`ab_vihaan_10000_cor-sim.txt`, `ab_vihaan_10000_cor-best.txt` e `ablacao_vihaan.txt` saem **byte a byte iguais** com a Blank como instantâneo (conferido com `cmp`);
`ab_vihaan_10000.txt` é o modo sem porta de cor, num formato de colunas anterior (sem as colunas Magda/Witch), por isso não é comparável por `cmp`. O lote foi refeito mesmo assim,
por consistência com os outros decks, e este fica guardado e marcado, não apagado (Regra #8 do `CLAUDE.md`).

Substituído por: `../dados/raw_*.json.xz` (brutos por partida, que este lote não tinha; só tabelas agregadas) e `../resumos/*.txt`.
`BLANK_TYPE=artifact` reproduz este lote.
