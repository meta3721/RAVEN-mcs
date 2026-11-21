"""For every git-modified tracked file, compare working-tree size with HEAD size,
so truncated files can be separated from legitimate edits."""
import subprocess
from pathlib import Path

root = Path('C:/Cursor/raven.mcs')


def git(*a):
    r = subprocess.run(['git', '-C', str(root)] + list(a), capture_output=True, text=True)
    return r.stdout


status = git('status', '--short')
modified = []
for line in status.splitlines():
    if line.startswith(' M') or line.startswith('M '):
        modified.append(line[3:].strip())

print('%-72s %10s %10s %s' % ('path', 'now', 'HEAD', 'verdict'))
print('-' * 112)
truncated = []
for rel in sorted(modified):
    p = root / rel
    now = p.stat().st_size if p.is_file() else -1
    head = git('show', 'HEAD:%s' % rel)
    hsize = len(head.encode('utf-8', errors='replace')) if head else 0
    if now == 0 and hsize > 0:
        verdict = 'TRUNCATED'
        truncated.append(rel)
    elif now < hsize * 0.5 and hsize > 200:
        verdict = 'SHRUNK?'
        truncated.append(rel)
    else:
        verdict = 'ok/edited'
    print('%-72s %10d %10d %s' % (rel[:70], now, hsize, verdict))

print()
print('SUSPECT (truncated/shrunk): %d' % len(truncated))
for t in truncated:
    print('   ', t)
