"""Fracao de partidas com resultado IDENTICO entre pares de variantes (controle de vacuidade da Regra #10 item 4), SO' dos brutos arquivados. Uso: python3 -I diferem_entre_variantes.py <pasta dados/>"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "dados")
print("Fração de partidas com resultado IDÊNTICO entre pares de variantes (N=10.000, sementes 3.000.000+i), só dos brutos arquivados.")
print("Serve de controle (Regra #10 item 4): variante que não difere da outra é vácua; aqui se vê quais diferem.")
for sufixo in ("", "_resiliencia"):
    r = A.carregar_raw(os.path.join(D, "raw_ab_10000" + sufixo)); N = len(r["antes"])
    print(f"\n[{'padrao' if not sufixo else 'resiliencia'}] N={N}")
    pares = [("depois", "fell_piso_vida_4"), ("depois", "fell_max_terrenos_99"), ("depois", "fell_max_terrenos_4"), ("depois", "fell_nunca_paga_vida"), ("depois", "so_bmc"), ("depois", "so_tapped_first_mana"),
             ("depois", "so_fell_terreno_e_keep"), ("so_fell_terreno", "so_fell_terreno_e_keep"), ("antes", "ref_sem_terreno_virado_primeiro"), ("so_bmc", "so_tapped_first_mana"), ("antes", "depois")]
    for a, b in pares:
        ident = sum(1 for x, y in zip(r[a], r[b]) if x[0] == y[0])
        print(f"  {a:26s} x {b:34s} idênticas={ident:6d} ({100*ident/N:6.2f}%)")
