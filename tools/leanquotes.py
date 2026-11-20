"""Quote extractor and citation check for the exposition (text only; nothing from the tree runs).

Usage:
  python3 -I leanquotes.py extract [DIR]   write DIR/quotes/<name>.lean and .loc.tex for every
                                           \\leanquote{Name} in DIR/main.tex and DIR/sections/*.tex
  python3 -I leanquotes.py check [DIR]     re-extract in memory and fail by name on:
      QUOTE-DRIFT   a quotes/ file differs from the source text
      QUOTE-MISSING a \\leanquote has no quotes/ file
      NAME          \\lean{Name} or \\leanquote{Name} not a declaration of the tree
      LOC           \\leanloc{path}{line}: path not a file of the tree, or line N does not start a
                    declaration (\\leanlocx{path}{line} only requires the line to exist)
      CITE          \\cite key missing from refs.bib
      FORBIDDEN     a local path in the article text
DIR defaults to ../article. The source tree is ../lean/src (or $RH_SRC); the declaration index is
out/decls.tsv, written by `python3 -I index.py ../lean/src out`.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.normpath(os.path.join(HERE, '../article'))
SRC = os.environ.get('RH_SRC', os.path.normpath(os.path.join(HERE, '../lean/src')))
INDEX = os.path.join(HERE, 'out/decls.tsv')

TOP = re.compile(r'^(?:@\[|private |protected |noncomputable |theorem |lemma |def |abbrev |structure |'
                 r'class |inductive |instance |opaque |end\b|namespace |section\b|open |variable |#|attribute |set_option )')
DECLKW = re.compile(r'^\s*(?:@\[[^\]]*\]\s*)*(?:private |protected |noncomputable )*'
                    r'(theorem|lemma|def|abbrev|structure|class|instance|inductive)\b')
FORBIDDEN = re.compile(r'/Users/|/home/|/private/tmp')
MAXLINES = 30


def load_index():
    d = {}
    for l in open(INDEX, encoding='utf-8'):
        full, kind, mod, ln = l.rstrip('\n').split('\t')
        d.setdefault(full, (kind, mod, int(ln)))
    return d


def tex_files(root):
    fs = [os.path.join(root, 'main.tex')]
    sd = os.path.join(root, 'sections')
    if os.path.isdir(sd):
        fs += sorted(os.path.join(sd, f) for f in os.listdir(sd) if f.endswith('.tex'))
    return [f for f in fs if os.path.exists(f)]


def strip_comments(t):
    return re.sub(r'(?<!\\)%[^\n]*', '', t)


def extract(name, idx):
    """Statement text as written: theorems/lemmas up to the first ':=', definitions and
    structures up to the next top-level command (at most MAXLINES lines)."""
    kind, mod, ln = idx[name]
    rel = mod.replace('.', '/') + '.lean'
    L = open(os.path.join(SRC, rel), encoding='utf-8').read().split('\n')
    out = [L[ln - 1]]
    for l in L[ln:ln - 1 + MAXLINES]:
        if l and TOP.match(l):
            break
        out.append(l)
    while out and not out[-1].strip():
        out.pop()
    if kind in ('theorem', 'lemma', 'instance'):
        text = '\n'.join(out)
        i = text.find(':=')
        if i >= 0:
            text = text[:i].rstrip() + ' := …'
        out = text.split('\n')
    return 'src/' + rel, ln, '\n'.join(out) + '\n'


def qfile(root, name):
    return os.path.join(root, 'quotes', name.replace('.', '-'))


def scan(root):
    text = '\n'.join(strip_comments(open(f, encoding='utf-8').read()) for f in tex_files(root))
    quotes = re.findall(r'\\leanquote\{([^}]*)\}', text)
    names = re.findall(r'\\lean\{([^}]*)\}', text)
    locs = re.findall(r'\\(?:leanloc|stl)\{([^}]*)\}\{(\d+)\}', text)
    locxs = re.findall(r'\\(?:leanlocx|stlx)\{([^}]*)\}\{(\d+)\}', text)
    cites = [k.strip() for g in re.findall(r'\\cite[pt]?(?:\[[^\]]*\])?\{([^}]*)\}', text) for k in g.split(',')]
    return text, quotes, names, locs, locxs, cites


def unlatex(s):
    return s.replace('\\_', '_')


def cmd_extract(root):
    idx = load_index()
    _, quotes, *_ = scan(root)
    os.makedirs(os.path.join(root, 'quotes'), exist_ok=True)
    for q in sorted(set(quotes)):
        path, ln, body = extract(q, idx)
        open(qfile(root, q) + '.lean', 'w', encoding='utf-8').write(body)
        open(qfile(root, q) + '.loc.tex', 'w', encoding='utf-8').write(
            '\\nolinkurl{' + path + ':' + str(ln) + '}%\n')
    print(len(set(quotes)), 'quotes extracted')


def cmd_check(root):
    idx = load_index()
    text, quotes, names, locs, locxs, cites = scan(root)
    fails = []
    for q in sorted(set(quotes)):
        if q not in idx:
            fails.append(f'NAME {q} (in \\leanquote)'); continue
        path, ln, body = extract(q, idx)
        f = qfile(root, q) + '.lean'
        if not os.path.exists(f):
            fails.append(f'QUOTE-MISSING {q}')
        elif open(f, encoding='utf-8').read() != body:
            fails.append(f'QUOTE-DRIFT {q}')
    for n in sorted(set(unlatex(x) for x in names)):
        if n not in idx:
            fails.append(f'NAME {n}')
    for p, ln in locs + locxs:
        p = unlatex(p)
        fp = os.path.join(SRC, p[4:] if p.startswith('src/') else p)
        if not os.path.exists(fp):
            fails.append(f'LOC {p}:{ln} (no such file)'); continue
        L = open(fp, encoding='utf-8').read().split('\n')
        n = int(ln)
        if n > len(L):
            fails.append(f'LOC {p}:{ln} (past end of file)')
        elif (p, ln) in locs and not DECLKW.match(L[n - 1]):
            fails.append(f'LOC {p}:{ln} (line does not start a declaration: {L[n-1][:60]!r})')
    bib = open(os.path.join(root, 'refs.bib'), encoding='utf-8').read()
    keys = set(re.findall(r'@\w+\{([^,\s]+),', bib))
    for c in sorted(set(c for c in cites if not c.startswith('#'))):
        if c not in keys:
            fails.append(f'CITE {c}')
    for m in FORBIDDEN.finditer(text):
        fails.append(f'FORBIDDEN {m.group(0)!r}')
    for f in fails:
        print('FAIL', f)
    print(f'{len(set(quotes))} quotes, {len(set(names))} names, {len(locs) + len(locxs)} locations, '
          f'{len(set(cites))} citation keys checked; {len(fails)} failures')
    return 1 if fails else 0


if __name__ == '__main__':
    root = sys.argv[2] if len(sys.argv) > 2 else ROOT_DEFAULT
    if sys.argv[1] == 'extract':
        cmd_extract(root)
    else:
        sys.exit(cmd_check(root))
