from pathlib import Path

print('=== E3 formal eventtrace dirs and their files ===')
for ds in ['sensorscope', 'uair', 'traffic']:
    base = Path('artifacts/e3_formal_runs_r1/eventtraces') / ds
    if not base.is_dir():
        continue
    seeds = sorted(p.name for p in base.iterdir() if p.is_dir())
    print('  %-12s seeds=%d  %s ... %s' % (ds, len(seeds), seeds[:2], seeds[-1:]))
    s0 = base / seeds[0]
    for f in sorted(s0.iterdir()):
        if f.is_file():
            print('        %-34s %d bytes' % (f.name, f.stat().st_size))
        else:
            print('        %-34s <dir> %d files' % (f.name, len(list(f.rglob('*')))))

print()
print('=== repro bundle E3 eventtrace dirs ===')
for ds in ['sensorscope', 'uair', 'traffic']:
    base = Path('RAVEN_MCS_PUBLIC_REPRO_R1/eventtraces/e3') / ds
    if not base.is_dir():
        print('  %-12s MISSING' % ds)
        continue
    seeds = sorted(p.name for p in base.iterdir() if p.is_dir())
    print('  %-12s seeds=%d' % (ds, len(seeds)))
    s0 = base / seeds[0]
    for f in sorted(s0.rglob('*.parquet')):
        print('        %-46s %d bytes' % (str(f.relative_to(s0)), f.stat().st_size))
    for f in sorted(s0.rglob('*.json')):
        print('        %-46s %d bytes' % (str(f.relative_to(s0)), f.stat().st_size))

print()
print('=== E2 eventtrace complete_aligned files (true values available) ===')
b = Path('RAVEN_MCS_PUBLIC_REPRO_R1/eventtraces/e2/30019/complete_aligned')
for f in sorted(b.rglob('*.parquet')):
    print('   %-52s %d bytes' % (str(f.relative_to(b)), f.stat().st_size))
