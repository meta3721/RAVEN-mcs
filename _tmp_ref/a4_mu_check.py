"""A4 decisive check: is mu_g exactly (test-unit count in g)/N?

If mu_g = n_g/N then w_i = mu_g/n_g = 1/N for every unit, and RMSE_mu is the
plain pooled unweighted RMSE.  Test: mu_g * N must be a positive integer for
every group, where N = n_test_atomic_supported from the same artifact.
"""
import json
from fractions import Fraction
from pathlib import Path

ART = Path('artifacts/e3_semantic_alignment_and_runner_integration_closure_r1')

for ds, fn in (('sensorscope', 'E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json'),
               ('uair', 'E3_UAIR_TARGET_SEMANTICS_R2.json')):
    j = json.loads((ART / fn).read_text(encoding='utf-8'))
    mu = j['mu']
    n_units = j.get('n_test_atomic_supported')
    n_groups = j.get('n_groups')
    print('=== %s ===' % ds.upper())
    print('  n_groups = %s   n_test_atomic_supported = %s' % (n_groups, n_units))
    print('  mu_construction = %r' % j.get('mu_construction'))
    print('  sum(mu) = %.12f   len(mu) = %d' % (sum(mu.values()), len(mu)))

    vals = list(mu.values())
    scaled = [v * n_units for v in vals]
    nonint = [s for s in scaled if abs(s - round(s)) > 1e-9]
    print('  mu_g * N integral for all groups? %s   non-integral: %d'
          % (not nonint, len(nonint)))
    if nonint[:5]:
        print('    worst offenders: %s' % ['%.6f' % v for v in nonint[:5]])
    # exact rational check
    exact = all(Fraction(v).limit_denominator(10 ** 6).denominator == n_units
                for v in vals)
    print('  (float artefact: check the strongest simple hypothesis)')
    counts = [round(s) for s in scaled]
    print('  implied counts: min=%d max=%d total=%d'
          % (min(counts), max(counts), sum(counts)))
    print('  distinct implied counts: %d (of %d groups)' % (len(set(counts)), len(counts)))
    nz = sum(1 for c in counts if c > 0)
    print('  groups with a positive implied count: %d' % nz)
    print()
