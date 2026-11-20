"""Static index of the alpo.ge Lean tree (text only; nothing is built or run).

Usage: python3 -I index.py <src-dir> <out-dir>
Writes:
  decls.tsv    full_name  kind  module  line   (namespace-resolved, heuristic)
  imports.tsv  module  imported_module
  files.tsv    module  library  lines  is_statement_file
Heuristics: tracks `namespace X` / `section` / `end` blocks; `_root_.` resets the
namespace; declaration keywords after modifiers/attributes on the same line.
"""
import os, re, sys
from multiprocessing import Pool

DECL = re.compile(
    r'^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|partial|unsafe|nonrec|scoped|local)\s+)*'
    r'(theorem|lemma|def|abbrev|structure|class|inductive|instance|opaque|axiom|example)\s+'
    r'(?:\([^)]*\)\s*)?([^\s:({\[⦃]+)?')
NS = re.compile(r'^namespace\s+(\S+)')
SEC = re.compile(r'^(?:noncomputable\s+)?section\b\s*(\S+)?')
END = re.compile(r'^end\b\s*(\S+)?')
IMP = re.compile(r'^import\s+(\S+)')


def scan(args):
    src, path = args
    rel = os.path.relpath(path, src)
    mod = rel[:-5].replace(os.sep, '.')
    imports, decls = [], []
    stack = []  # list of (kind, name-parts)
    n = 0
    in_comment = 0
    with open(path, encoding='utf-8', errors='replace') as f:
        for n, line in enumerate(f, 1):
            s = line.strip()
            # crude block-comment skipping
            if in_comment:
                if '-/' in s:
                    in_comment = 0
                continue
            if s.startswith('/-') and '-/' not in s[2:]:
                in_comment = 1
                continue
            m = IMP.match(s)
            if m:
                imports.append(m.group(1)); continue
            m = NS.match(line)
            if m:
                stack.append(('ns', m.group(1).split('.'))); continue
            m = SEC.match(line)
            if m:
                stack.append(('sec', [])); continue
            m = END.match(line)
            if m and stack:
                stack.pop(); continue
            m = DECL.match(line)
            if m:
                kind, name = m.group(1), m.group(2)
                if kind == 'example' or not name:
                    continue
                prefix = [p for k, parts in stack if k == 'ns' for p in parts]
                if name.startswith('_root_.'):
                    full = name[len('_root_.'):]
                else:
                    full = '.'.join(prefix + [name])
                decls.append((full, kind, mod, n))
    lib = mod.split('.')[0]
    isstmt = os.path.basename(path).startswith('Statement')
    return mod, lib, n, isstmt, imports, decls


def main():
    src, out = sys.argv[1], sys.argv[2]
    paths = []
    for root, _, files in os.walk(src):
        for fn in files:
            if fn.endswith('.lean'):
                paths.append((src, os.path.join(root, fn)))
    paths.sort()
    os.makedirs(out, exist_ok=True)
    with Pool(8) as pool, \
            open(os.path.join(out, 'decls.tsv'), 'w') as fd, \
            open(os.path.join(out, 'imports.tsv'), 'w') as fi, \
            open(os.path.join(out, 'files.tsv'), 'w') as ff:
        for mod, lib, n, isstmt, imports, decls in pool.imap(scan, paths, chunksize=200):
            ff.write(f'{mod}\t{lib}\t{n}\t{int(isstmt)}\n')
            for i in imports:
                fi.write(f'{mod}\t{i}\n')
            for d in decls:
                fd.write('\t'.join(map(str, d)) + '\n')
    print(len(paths), 'files')


if __name__ == '__main__':
    main()
