# Search notes — dataset with a target concentrated at the aggregation level

Date: 2026-10-09. Skill: `ccf-literature-searcher`, standard-mode intent (benchmark/dataset discovery
feeding experiment design). Purpose: find an external spatio-temporal sensing dataset whose **deployment
target concentrates on few aggregation groups** while **many clients are active per aggregation window**,
so that a corrected reference re-weighted onto the feasible set has real room to move a deployment-level
quantity.

## The two conditions, made operational

1. **Target concentration.** On the deployment target mass over aggregation groups, the top group's
   share is far above uniform and the effective number of groups `exp(entropy)` is far below the group
   count. Our own blocks: SensorScope top-1 `0.53 %` of `220` groups, U-Air `0.79 %` of `144`,
   NSW-Traffic `0.58 %` of `172` — all effectively uniform.
2. **Feasible-set slack.** The share of active windows whose active-client count exceeds `3`, because
   `eq:Cr` with `E_min = 3` admits only uniform weights when `K_r <= 3`. Our own block counts:
   SensorScope `24.7 %`, U-Air `19.7 %`, NSW-Traffic `88.9 %` (measured from frozen
   `window_metrics.json`; see `results_text_repairs/round_v1/BLOCK_SCREEN.json`).

## Queries used

```text
mobile crowdsensing dataset urban air quality few monitoring stations concentrated target
bike sharing demand dataset few stations carry most trips concentration spatio-temporal prediction
traffic volume dataset weighted priority corridors main roads target distribution
federated learning benchmark non-IID clients concentrated deployment target subgroup distribution
low-cost air quality sensor network dataset reference grade monitors validation station crowdsourced paper
bike sharing demand prediction benchmark dataset Citi Bike Divvy station concentration paper
ACN-Data electric vehicle charging session dataset Caltech paper
geo-distributed federated learning dataset deployment target concentrated subgroup benchmark paper
"Citi Bike" dataset demand prediction benchmark NeurIPS datasets and benchmarks paper 2023
shared mobility demand dataset de facto benchmark Citi Bike Divvy paper 2024 2025
PurpleAir low-cost sensor network paper reference monitor comparison dataset
urban sensing dataset "few" hubs carry most demand concentration top stations share
```

Source policy applied: MDPI excluded; untraceable PDFs without title/authors/venue excluded; no claim
below is taken from a search snippet.

## Outcome: no candidate reached the inclusion bar

Twelve queries returned mostly fragmentary PDF excerpts with no stable title, author list, venue or
landing page, and several off-topic hits (knowledge tracing, MNIST/CIFAR federated splits, an unrelated
UK driving-network paper). Under the source policy those are excluded, so **`papers.md` contains no
scored candidate**. This is a search outcome, not a finding that the field lacks such datasets.

## Leads that were surfaced but are NOT verified

Listed only so a follow-up pass can start from them. None has been verified for title, venue, year or
content, and none may be cited until it has been.

| lead | URL seen | what it would have to be checked for |
|---|---|---|
| Citi Bike described as a de-facto benchmark for shared-mobility demand (a `MoDE-Boost` preprint) | https://arxiv.org/html/2602.16573v1 | that the record exists and is what it claims; whether the dataset's demand concentrates on few stations; clients per window |
| EV charging sessions at Caltech/JPL (ACN-Data) | https://ieeexplore.ieee.org/document/11469933 , https://www.sciencedirect.com/science/article/pii/S2352340924005547 | session concentration per site; how "clients" would be attributed |
| low-cost sensor networks versus reference-grade monitors, community science | https://pubs.rsc.org/nb/content/articlepdf/2025/ea/d5ea00020c | whether a downloadable paired dataset exists; target = reference sites |
| PM sensor performance, Northeast China | https://rd.springer.com/article/10.1007/s44408-026-00159-6 | instrument performance, not a target-concentration dataset |
| spatial concentration of charging demand, Sweden (policy report) | https://theicct.org/wp-content/uploads/2026/09/ID-649-%E2%80%93-EU-spatiotemporal-analysis_report_final-1.pdf | direct evidence that charging demand concentrates spatially; not a dataset |
| neurips 2023 datasets & benchmarks PDF (title not recovered) | https://proceedings.neurips.cc/paper_files/paper/2023/file/ee799aff607fcf39c01df6391e96f92c-Paper-Datasets_and_Benchmarks.pdf | identify the paper, then test the two conditions |

## Class-level hypotheses (inference, not search evidence)

These are offered as hypotheses to test, and are **not** paper claims:

1. **The productive class is demand-type targets, not sensor-coverage targets.** Metropolitan
   traffic-sensor benchmarks such as Metr-LA and PEMS-BAY place sensors at roughly uniform density along
   a network, so their "target" would concentrate only mildly — the same failure our NSW-Traffic shows.
   What concentrates is *demand*: a few stations, hubs or corridors carry most trips or sessions. The
   lead table above is consistent with this, but the table proves nothing.
2. **The paired-instrument class is structurally the closest match to our setting.** A deployment whose
   target is a small set of reference-grade monitors, with the data contributed by many low-cost
   participants, has exactly the shape the method needs: few target groups, many clients per window.
   Adoption cost is the risk: a new loader, a new client attribution, and a defensible "deployment
   target" definition would all have to be built and pre-registered.

## Recommended next step

Before more retrieval, decide the route, because the retrieval target changes with it:

- **Route A (no new data, fully verified today).** Keep NSW-Traffic, which has the slack
  (`88.9 %`), and define the deployment target to concentrate on priority regions using the frozen
  `43 -> 4` region mapping that already exists (`build_label_free_regions`, E2 public-target identity).
  The project's own V2.3 design plan proposed exactly this target form ("extended target: service-weighted
  target, for example main-road or key monitoring regions weighted twice"; weights fixed before training).
  Both conditions then hold on existing artifacts. Risk: the target is chosen by the authors, so it must
  be pre-registered and justified as a deployment scenario rather than tuned to produce an effect.
- **Route B (external dataset).** Complete a standard-mode search against the lead table, requiring for
  each candidate: a stable dataset page, a group definition, the target-mass concentration, and clients
  per window. Cost: a new loader and client attribution; benefit uncertain until the concentration
  numbers are in hand.
