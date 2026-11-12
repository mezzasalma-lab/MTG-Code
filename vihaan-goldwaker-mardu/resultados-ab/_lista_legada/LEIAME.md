# `_lista_legada` — a lista do Vihaan como estava em `a17049f` (com Blood Money)

`lista.md` desta pasta é uma **cópia exata** de `vihaan-goldwaker-mardu/lista.md` no commit `a17049f` (conferido por `cmp` com `git show a17049f:vihaan-goldwaker-mardu/lista.md`).

**Por que existe (2026-10-04, 12ª rodada):** o usuário trocou `Blood Money` por `Mythos of Snapdax` na lista viva. Os simuladores `ANTES` guardados em `*/codigo/` leem **`lista.md` do diretório de trabalho** no `import` (e fazem `assert name in CARD_DB`), e vários scripts de arquivos anteriores leem a lista viva para enumerar cartas ou consultar o Commander Spellbook. Sem esta cópia, **nenhum** arquivo anterior reproduziria o que publicou.

**Como é usada:**
- `orquestracao/fx_common.py` de cada pasta do Vihaan (`carrega`): `chdir` para esta pasta quando o caminho carregado é um snapshot ANTES, para o deck quando é o arquivo vivo (e, no arquivo vivo, desliga `MYTHOS_REPLACES_BLOOD_MONEY_ENABLED` e `CASCADE_DECLINE_HELD_WIPES_ENABLED` e refaz `BASE_LIBRARY`, o que devolve a lista antiga na posição antiga);
- `kp_harness.py`, `vih_harness.py` e os `bitident.py` do Kingpin e da Inevitable Defeat: desligam as mesmas chaves no módulo vivo;
- `comparacao_simulador.py` e `lacunas_simulador_c04840d.py` (partida manual #1): `chdir` para cá;
- `enumeracao*.py`, `csb_*.py`, `kp_enumeracao.py`, `vih_enumeracao.py`: leem esta lista no lugar da viva.
- O `csb_generic.py` (kingpin, inevitable-defeat, blasphemous-edict) recebe o diretório do deck como argumento de linha de comando: para refazer **aquelas** consultas como foram publicadas, passe `vihaan-goldwaker-mardu/resultados-ab/_lista_legada` no lugar de `vihaan-goldwaker-mardu`.

Não editar. A lista **atual** do deck é `../../lista.md`.
