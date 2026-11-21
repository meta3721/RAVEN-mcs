"""Complete, encoding-safe damage scan over all git-modified tracked files."""
import subprocess
from pathlib import Path

root = Path('C:/Cursor/raven.mcs')


def run(args, text=True):
    return subprocess.run(['git', '-C', str(root)] + args, capture_output=True, text=text)


status = run(['status', '--short'], text=False).stdout.decode('utf-8', errors='replace')
modified = [ln[3:].strip() for ln in status.splitlines()
            if ln[:2] in (' M', 'M ', 'MM', 'AM')]

damaged, newfile, ok = [], [], 0
for rel in sorted(modified):
    p = root / rel
    now = p.stat().st_size if p.is_file() else -1
    head = run(['show', 'HEAD:%s' % rel], text=False).stdout
    hsize = len(head)
    if hsize == 0:
        newfile.append((rel, now))
    elif now == 0 or (hsize > 200 and now < hsize * 0.5):
        damaged.append((rel, now, hsize))
    else:
        ok += 1

print('tracked-and-modified: %d   (ok/edited %d, head-empty %d, damaged %d)'
      % (len(modified), ok, len(newfile), len(damaged)))
print()
print('=== DAMAGED (restore from HEAD) ===')
for rel, now, hsize in damaged:
    print('  %-72s now=%-8d HEAD=%d' % (rel, now, hsize))
print()
print('=== HEAD-EMPTY (not damage) ===')
for rel, now in newfile:
    print('  %-72s now=%d' % (rel, now))
