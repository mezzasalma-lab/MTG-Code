"""Varredura estatica de dependencia de ordem de conjunto (hash randomization): laços/compreensões/list()/next(iter())/pop() sobre sets."""
import ast, sys, glob, os, re
import os
ROOT = os.environ.get("ROOT", "/home/user/MTG-Code")
SIMS = sorted(glob.glob(f"{ROOT}/*/*goldfish_v1.py"))
SIMS = [s for s in SIMS if "/resultados-ab/" not in s and not s.endswith("_original.py")]

def is_set_expr(n):
    return isinstance(n, (ast.Set, ast.SetComp)) or (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("set", "frozenset"))

class V(ast.NodeVisitor):
    def __init__(self, src, set_attrs):
        self.src = src.splitlines(); self.hits = []; self.set_names = [set()]; self.set_attrs = set_attrs
    def line(self, n): return n.lineno
    def visit_FunctionDef(self, n):
        self.set_names.append(set())
        self.generic_visit(n)
        self.set_names.pop()
    def visit_Assign(self, n):
        if is_set_expr(n.value) or (isinstance(n.value, ast.BinOp) and (is_set_expr(n.value.left) or is_set_expr(n.value.right))):
            for t in n.targets:
                if isinstance(t, ast.Name): self.set_names[-1].add(t.id)
        # x |= / x = x | y mantem set
        self.generic_visit(n)
    def setlike(self, e):
        if is_set_expr(e): return True
        if isinstance(e, ast.Name) and any(e.id in s for s in self.set_names): return True
        if isinstance(e, ast.Attribute) and e.attr in self.set_attrs: return True
        if isinstance(e, ast.BinOp) and isinstance(e.op, (ast.BitOr, ast.BitAnd, ast.Sub, ast.BitXor)) and (self.setlike(e.left) or self.setlike(e.right)): return True
        return False
    def flag(self, n, why):
        self.hits.append((n.lineno, why, self.src[n.lineno - 1].strip()[:150]))
    def visit_For(self, n):
        if self.setlike(n.iter): self.flag(n, "for sobre set")
        self.generic_visit(n)
    def visit_comprehension(self, n):
        if self.setlike(n.iter): self.flag(n.iter, "compreensao sobre set")
        self.generic_visit(n)
    def visit_Call(self, n):
        f = n.func
        if isinstance(f, ast.Name) and f.id in ("list", "tuple", "next", "iter", "enumerate", "min", "max") and n.args:
            a = n.args[0]
            if f.id == "next" and isinstance(a, ast.Call) and isinstance(a.func, ast.Name) and a.func.id == "iter" and a.args and self.setlike(a.args[0]): self.flag(n, "next(iter(set))")
            elif f.id in ("list", "tuple", "iter", "enumerate") and self.setlike(a): self.flag(n, f"{f.id}(set)")
            elif f.id in ("min", "max") and self.setlike(a): self.flag(n, f"{f.id}(set) (empate depende da ordem)")
        if isinstance(f, ast.Attribute) and f.attr == "pop" and not n.args and self.setlike(f.value): self.flag(n, "set.pop()")
        self.generic_visit(n)

tot = 0
for p in SIMS:
    src = open(p).read()
    tree = ast.parse(src)
    # atributos declarados como Set/set/frozenset nas classes (AnnAssign) -- heuristica
    set_attrs = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            a = ast.unparse(n.annotation) if n.annotation else ""
            v = ast.unparse(n.value) if n.value else ""
            if re.match(r"(typing\.)?(Set|set|frozenset)\b", a) or "default_factory=set" in v:
                set_attrs.add(n.target.id)
    v = V(src, set_attrs); v.visit(tree)
    print(f"== {os.path.relpath(p, ROOT)}  (atributos-set: {len(set_attrs)}) hits: {len(v.hits)}")
    for h in v.hits: print(f"   L{h[0]:5d} {h[1]:30s} {h[2]}")
    tot += len(v.hits)
print("TOTAL", tot)
