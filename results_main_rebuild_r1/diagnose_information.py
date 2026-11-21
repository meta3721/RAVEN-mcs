"""Predeclared Central-all control for the remaining U-Air learning failure.

No optimizer search: reuse the selected delivered NDMF optimizer (SGD .03).
This privileged control cannot qualify the deployable backbone or RAVEN.
"""
from concurrent.futures import ProcessPoolExecutor
from train_central import *

if __name__=='__main__':
    save(OUT/'CENTRAL_ALL_DIAGNOSTIC_CONFIG.json',dict(dataset='uair',model='ndmf',optimizer='sgd',lr=.03,
        seeds=list(SEEDS),budget=200,selection='same best Central-delivered configuration, no new search',
        purpose='information-versus-fitting diagnostic for failed dataset',test_scoring=False))
    with ProcessPoolExecutor(max_workers=2) as ex:
        results=list(ex.map(run_one,[('uair',s,'ndmf','sgd',.03,'central_all') for s in SEEDS]))
    pd.DataFrame(results).to_csv(OUT/'P1_CENTRAL_ALL_UAIR_DIAGNOSTIC.csv',index=False)
    print('PRIVILEGED_CONTROL',json.dumps(results),flush=True)
