"""Comparacoes pareadas ENTRE variantes do A/B Ram Through -> Herd Heirloom (o driver so' compara cada variante com `antes`), SO' dos brutos arquivados (dados/raw_ab_<N>[_resiliencia].json.xz):
  P_troca_com_gatilho_novo   = depois              - so_gatilho_beorn      (a TROCA, ja' com o gatilho da Beorn corrigido nos dois lados)
  P_troca_com_gatilho_antigo = troca_gatilho_antigo - antes                (a TROCA no simulador de antes; mesmas sementes)
  P_so_mana                  = troca_so_mana        - troca_sem_habilidades (o que a habilidade 1 (mana de criatura) soma ao Heirloom "em branco")
  P_so_compra                = troca_so_compra      - troca_sem_habilidades (o que a habilidade 2 (trample + compra) soma)
  P_as_duas                  = troca_gatilho_antigo - troca_sem_habilidades (as duas juntas)
Uso: python3 comparacoes.py [N ...]   (padrao: 10000)"""
import os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
DEST = json.load(open(os.path.join(AQUI, "config.json")))["destaque"]
PARES = [("P_troca_com_gatilho_novo", "so_gatilho_beorn", "depois"), ("P_troca_com_gatilho_antigo", "antes", "troca_gatilho_antigo"),
         ("P_so_mana", "troca_sem_habilidades", "troca_so_mana"), ("P_so_compra", "troca_sem_habilidades", "troca_so_compra"), ("P_as_duas", "troca_sem_habilidades", "troca_gatilho_antigo")]
for N in [int(x) for x in sys.argv[1:]] or [10000]:
    for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
        res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_{N}{suf}"))
        for rot, base, var in PARES:
            print(f"LOTE N={N}, modo {modo}")
            print(A.tabela_pareada(res[base], res[var], DEST, rotulo=f"[{rot}: {var} - {base}]"))
            print()
