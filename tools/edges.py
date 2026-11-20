"""Heuristic declaration-level reference graph, then the cone of a root.

Usage:
  python3 -I edges.py build          -> out/edges.tsv  (decl \t referenced project decl)
  python3 -I edges.py cone ROOT      -> out/cone_<ROOT>.txt (BFS depth per declaration)
Root-level lower-case names resolve only when at least 5 characters long.
A declaration's text is the span from its line to the next indexed declaration in the same
file. Identifiers resolve as in show.py (exact dotted/capitalised name, own namespace prefixes,
`open`/`namespace` prefixes of the file). Dot-notation (`x.foo`), instance resolution, notation
and tactic-generated references are not seen, and short local names may resolve spuriously, so
the cone is neither an upper nor a lower bound of the kernel's dependency cone.
"""
import os, re, sys
from collections import defaultdict, deque
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('RH_SRC', os.path.normpath(os.path.join(HERE, '../lean/src')))
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_'!?ₐ-ₜ₀-₉α-ωΑ-Ω₂]*(?:\.[A-Za-z_][A-Za-z0-9_'!?ₐ-ₜ₀-₉α-ωΑ-Ω₂]*)*")
NAMES = None


def load_names():
    global NAMES
    NAMES = set()
    for l in open(os.path.join(HERE, 'out/decls.tsv'), encoding='utf-8'):
        NAMES.add(l.split('\t', 1)[0])


def work(item):
    mod, decls = item  # decls: list of (line, full)
    if NAMES is None:
        load_names()
    p = os.path.join(SRC, mod.replace('.', '/') + '.lean')
    L = open(p, encoding='utf-8', errors='replace').read().split('\n')
    opens = set()
    for l in L:
        if l.startswith('open '):
            opens.update(t for t in l[5:].split() if t[:1].isupper())
        elif l.startswith('namespace '):
            opens.add(l.split()[1])
    opens = sorted(opens)
    decls.sort()
    out = []
    for i, (ln, full) in enumerate(decls):
        end = decls[i + 1][0] - 1 if i + 1 < len(decls) else len(L)
        body = re.sub(r'--[^\n]*', '', '\n'.join(L[ln - 1:end]))
        parts = full.split('.')
        prefixes = ['.'.join(parts[:k]) + '.' for k in range(len(parts) - 1, 0, -1)]
        seen = set()
        for tok in set(IDENT.findall(body)):
            r = None
            if tok.startswith('_root_.'):
                t = tok[7:]
                r = t if t in NAMES else None
            elif tok in NAMES and ('.' in tok or tok[0].isupper() or len(tok) >= 5):
                r = tok
            else:
                for pre in prefixes:
                    if pre + tok in NAMES:
                        r = pre + tok; break
                if r is None:
                    for ns in opens:
                        if ns + '.' + tok in NAMES:
                            r = ns + '.' + tok; break
            if r and r != full:
                seen.add(r)
        out.extend((full, r) for r in seen)
    return out


def build():
    per = defaultdict(list)
    for l in open(os.path.join(HERE, 'out/decls.tsv'), encoding='utf-8'):
        full, kind, mod, ln = l.rstrip('\n').split('\t')
        per[mod].append((int(ln), full))
    items = list(per.items())
    n = 0
    with Pool(8) as pool, open(os.path.join(HERE, 'out/edges.tsv'), 'w') as f:
        for res in pool.imap_unordered(work, items, chunksize=100):
            for a, b in res:
                f.write(f'{a}\t{b}\n'); n += 1
    print(n, 'edges')


def cone(root):
    g = defaultdict(list)
    for l in open(os.path.join(HERE, 'out/edges.tsv'), encoding='utf-8'):
        a, b = l.rstrip('\n').split('\t'); g[a].append(b)
    depth = {root: 0}
    q = deque([root])
    while q:
        x = q.popleft()
        for y in g[x]:
            if y not in depth:
                depth[y] = depth[x] + 1; q.append(y)
    with open(os.path.join(HERE, f'out/cone_{root}.txt'), 'w') as f:
        for k, d in sorted(depth.items(), key=lambda kv: (kv[1], kv[0])):
            f.write(f'{d}\t{k}\n')
    print(len(depth), 'declarations in heuristic cone of', root)


if __name__ == '__main__':
    if sys.argv[1] == 'build':
        build()
    else:
        cone(sys.argv[2])
