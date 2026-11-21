"""Approved same-state shadows; do not call P2 again or mutate the runner."""
from .schema import InputError
def shadow_actions(runner,decision):
    if not runner.calibration_only or runner.isolated_test:raise InputError('diagnostic shadows require approved real calibration_only')
    runner.collection_authorization.require(seed=runner.seed,source=runner.config.source)
    forced=decision.reason in {'TERMINAL','WARMUP','DEADLINE','MIN_CLIENTS'}
    no_q=decision.action if forced else ('CLOSE' if decision.B-dict(decision.components)['debt']>=.02+1e-7 else 'WAIT')
    elapsed=runner.now-runner.window_open
    fixed={}
    for period in (.5,2.):
        fixed[str(period)]=decision.action if forced else ('CLOSE' if elapsed>=period-1e-9 else 'WAIT')
    return dict(no_Q_stop=no_q,fixed_time_0_5=fixed['0.5'],fixed_time_2=fixed['2.0'],
        forced=forced,no_Q_B=None if forced else decision.B-dict(decision.components)['debt'],P2_recomputed=False,
        legal_actions=[decision.action] if runner.now==100 or decision.reason=='DEADLINE' or (decision.reason=='WARMUP' and elapsed>=1-1e-9) else
            (['WAIT'] if decision.reason in {'WARMUP','MIN_CLIENTS'} else ['CLOSE','WAIT']))
