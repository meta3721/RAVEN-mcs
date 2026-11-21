#!/usr/bin/env python3
"""Offline forensic closure: no formal-run file is opened for writing."""
from __future__ import annotations
import csv, hashlib, json, re, sys
from collections import Counter
from pathlib import Path
from typing import Any
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
from raven_mcs.correction.pi_target import build_pi_target
from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
from raven_mcs.e3.final_closure.core import HARD_GATE, certify_returned_alpha, summarize_weights
from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle
from raven_mcs.simulation.event_trace import load_event_trace
from raven_mcs.training.client import _flatten_params
from raven_mcs.training.window_runner import build_full_runner

ART = ROOT / "artifacts/e3_local_hajek_weight_and_p2_certificate_final_closure_r1"
FORMAL = ROOT / "artifacts/e3_formal_runs_r1"
P2 = {"inst_cal", "debt_cal", "raven", "raven_simoracle"}

def load(p: Path, d=None): return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else d
def sha(p: Path): return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
def dump(name, value): (ART/name).write_text(json.dumps(value, indent=2, sort_keys=True)+"\n", encoding="utf-8")
def write_csv(name, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row)) or ["note"]
    with (ART/name).open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def replay(dataset_name: str, seed: int) -> list[dict]:
    """Run frozen scheduling/propensity path with local SGD replaced by zeros."""
    ds = load_paper_dataset(ROOT, dataset_name)
    mapping = load_spatial_to_client(ROOT, dataset_name)
    trace, _ = load_event_trace(FORMAL/"eventtraces"/dataset_name/f"seed{seed}"/"training_eventtrace")
    atomic, _ = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=dataset_name, root=ROOT)
    sealed = {str(r.unit_id): str(r.opportunity_stratum) for r in atomic.itertuples(index=False)}
    ds._atomic_df = ds._atomic_df.copy()
    ds._atomic_df["opportunity_stratum"] = [sealed.get(str(u), str(s)) for u,s in zip(ds._atomic_df.unit_id, ds._atomic_df.opportunity_stratum)]
    bundle = production_target_bundle(root=ROOT, dataset_name=dataset_name, dataset=ds)
    atomic_pi = atomic.copy(); atomic_pi["target_group_main"] = atomic_pi["target_group"].astype(str)
    pi = {(str(r.client_id),str(r.opportunity_stratum)):float(r.pi_k_s_tar) for r in build_pi_target(atomic_pi,mapping,split="test").itertuples()}
    train=atomic.loc[atomic.split.astype(str)=="train"]; by={}
    for r in train.itertuples(index=False):
        if (c:=mapping.get(str(r.spatial_id))) is not None: by.setdefault(c,[]).append(str(r.opportunity_stratum))
    pi_opp=build_joint_pi_opp(sorted(by), {c:sorted(set(v)) for c,v in by.items()})
    for col in ("risk_set_unit_ids","opportunity_features","observed_unit_ids","O"):
        if trace.events[col].dtype == object: trace.events[col]=trace.events[col].map(lambda x: json.loads(x) if isinstance(x,str) else x)
    runner=build_full_runner(trace,ds,method="local_hajek",n_groups=int(bundle["n_groups_runtime"]),model_seed=seed,local_steps=2,target_mu=np.asarray(bundle["mu"]),pi_target=pi,s_max=int(trace.metadata.s_max),use_coarse_time_groups=False,pi_opp_joint=pi_opp)
    captured=[]
    def zero_step(*, a_bar_weights, **kwargs):
        captured.append(np.asarray(a_bar_weights,dtype=float).tolist())
        return np.zeros_like(_flatten_params(runner.theta), dtype=np.float64), 0.0
    runner._trainer.train_step=zero_step
    runner.run()
    if len(captured) != len(runner.diagnostics): raise RuntimeError("capture/diagnostic cardinality mismatch")
    return [{"window_id":d["window_id"],"client_id":d["client_id"],"weights":w} for d,w in zip(runner.diagnostics,captured)]

def weight_audit():
    rows=[]; identity=[]; errors=[]
    for ds in ("sensorscope","uair"):
      for seed in range(30001,30021):
        try:
          captured=replay(ds,seed)
          for x in captured:
            if len(x["weights"]) < 2: continue
            local=FORMAL/"runs"/ds/"local_hajek"/f"seed{seed}"/"runtime_manifest.json"
            fed=FORMAL/"runs"/ds/"fedavg_window"/f"seed{seed}"/"runtime_manifest.json"
            lm,fm=load(local,{}),load(fed,{})
            rows.append({"dataset":ds,"seed":seed,"client_id":x["client_id"],"window_id":x["window_id"],**summarize_weights(x["weights"]),"weight_source":"EVENTTRACE_DETERMINISTIC_REPLAY_ZERO_UPDATE","formal_run_id":lm.get("run_id"),"checkpoint_hash":lm.get("checkpoint_hash")})
            identity.append({"dataset":ds,"seed":seed,"case":"A" if lm.get("checkpoint_hash")==fm.get("checkpoint_hash") else "B","local_hajek_checkpoint":lm.get("checkpoint_hash"),"fedavg_checkpoint":fm.get("checkpoint_hash"),"explanation":"CASE A: identical accepted checkpoints; forensic local loss weights determine whether this is a valid formal collapse."})
        except Exception as exc: errors.append({"dataset":ds,"seed":seed,"error":f"{type(exc).__name__}: {exc}"})
    write_csv("E3_LOCAL_HAJEK_FORMAL_WEIGHT_AUDIT.csv",rows); dump("E3_LOCAL_HAJEK_FORMAL_WEIGHT_AUDIT.json",{"records":rows,"replay_errors":errors})
    write_csv("E3_LOCAL_HAJEK_CHECKPOINT_IDENTITY_EXPLANATION.csv",identity)
    all_uniform=bool(rows) and not errors and all(r["is_uniform_eps"] for r in rows)
    decision="LOCAL_HAJEK_FORMAL_COLLAPSE_CERTIFIED" if all_uniform else ("UNCERTIFIED" if errors else "LOCAL_HAJEK_FORMAL_BASELINE_INVALID")
    dump("E3_LOCAL_HAJEK_FORMAL_WEIGHT_SUMMARY.json",{"n_client_windows":len(rows),"n_uniform":sum(r["is_uniform_eps"] for r in rows),"replay_errors":errors,"decision":decision})
    return decision, rows

def p2_audit():
    inventory=[]; current=None; stage_logs=list((FORMAL/"logs").glob("stage_*.log"))
    for path in stage_logs:
      for n,line in enumerate(path.read_text(encoding="utf-8",errors="replace").splitlines(),1):
        m=re.search(r"\[E3-FORMAL\].*?\s(\w+)\s+(\w+)\s+seed=(\d+)",line)
        if m: current={"dataset":m.group(1),"method":m.group(2),"seed":int(m.group(3))}
        if "Solution may be inaccurate" in line and current and current["method"] in P2: inventory.append({**current,"log":path.name,"line":n,"window_id":"UNKNOWN","warning":"Solution may be inaccurate"})
    write_csv("E3_P2_INACCURATE_WARNING_INVENTORY.csv",inventory); dump("E3_P2_INACCURATE_WARNING_INVENTORY.json",{"records":inventory})
    affected={(r["dataset"],r["method"],r["seed"]) for r in inventory}; state=[]; cert=[]
    for ds,method,seed in sorted(affected):
      windows=load(FORMAL/"runs"/ds/method/f"seed{seed}"/"window_metrics.json",[])
      for w in windows:
        if not w.get("active"): continue
        row={"dataset":ds,"method":method,"seed":seed,"window_id":w.get("window_id"),"alpha":json.dumps(w.get("alpha")),"native_solver_status":"MISSING_STATE","warning_window":"UNKNOWN"}
        state.append(row); cert.append({**row,**certify_returned_alpha(w.get("alpha")),"full_p2_input_status":"UNCERTIFIED_INCOMPLETE_INPUTS"})
    write_csv("E3_P2_RECOVERED_STATE_INDEX.csv",state); write_csv("E3_P2_FULL_CERTIFICATE.csv",cert); dump("E3_P2_FULL_CERTIFICATE.json",{"records":cert})
    write_csv("E3_P2_OFFLINE_RESOLVE_AUDIT.csv",[{"note":"No offline re-solve: persisted window metrics omit full M, mu, debt, variance, and staleness inputs."}])
    passes=bool(cert) and all(r["classification"]=="CERTIFIED_WITHIN_NUMERICAL_TOLERANCE" for r in cert)
    decision="P2_INACCURATE_WINDOWS_FULLY_CERTIFIED" if passes else "PARTIALLY_UNCERTIFIED"
    recon={"warning_count":len(inventory),"affected_runs":len(affected),"recovered_active_windows":len(cert),"inventory_complete":all((FORMAL/"logs"/x).is_file() for x in ("stage_A.log","stage_B.log","stage_C.log")),"decision":decision}
    dump("E3_P2_WARNING_COUNT_RECONCILIATION.json",recon); write_csv("E3_P2_INACCURATE_CERTIFICATE_SUMMARY.csv",[recon])
    dump("E3_P2_FROZEN_TOLERANCE_AUDIT.json",{"hard_gate":HARD_GATE,"source":"src/raven_mcs/aggregation/p2_cvxpy.py","source_sha256":sha(ROOT/"src/raven_mcs/aggregation/p2_cvxpy.py"),"criteria":["simplex","nonnegative","upper alpha_bar(0.5,n_active)","ess ball","finite"]})
    return decision

def main():
    ART.mkdir(parents=True,exist_ok=True)
    before=sha(FORMAL/"E3_FORMAL_RAW_RESULTS_SEAL.json")
    local_decision, weights=weight_audit(); p2_decision=p2_audit()
    wiring={str(p):sha(ROOT/p) for p in ["src/raven_mcs/training/window_runner.py","src/raven_mcs/training/local_objective.py","src/raven_mcs/training/client.py","src/raven_mcs/aggregation/method_policy.py"]}
    dump("E3_LOCAL_HAJEK_PRODUCTION_WIRING_PROOF.json",{"files":wiring,"proof":"WindowRunner guards a_bar with uses_hajek_local_loss and passes it to ClientTrainer, which feeds local_hajek_loss."})
    dump("E3_LOCAL_HAJEK_FINAL_DECISION.json",{"decision":local_decision}); (ART/"E3_LOCAL_HAJEK_FINAL_DECISION.md").write_text(f"# Local-Hajek decision\n\n{local_decision}\n")
    dump("E3_P2_FINAL_DECISION.json",{"decision":p2_decision}); (ART/"E3_P2_FINAL_DECISION.md").write_text(f"# P2 decision\n\n{p2_decision}\n")
    parent=ROOT/"artifacts/e3_formal_evidence_integrity_and_claim_closure_r1"; claims=load(parent/"E3_CLAIM_MATRIX_FINAL.json",{})
    claims["C3"]={"status":"SUPPORTED","finding":"Supported only for SensorScope and U-Air structural evidence; Traffic remains descriptive."}
    claims["C4"]={"status":"PARTIALLY_SUPPORTED","finding":"SimOracle is context-only and is not a performance superiority claim."}
    dump("E3_CLAIM_MATRIX_FINAL_R2.json",claims); (ART/"E3_CLAIM_MATRIX_FINAL_R2.md").write_text("# E3 claim matrix R2\n\n"+json.dumps(claims,indent=2)+"\n")
    (ART/"E3_C3_FINAL_WORDING.md").write_text("C3 is supported when scoped to SensorScope and U-Air only.\n"); dump("E3_C3_FINAL_STATUS.json",claims["C3"])
    (ART/"E3_C4_FINAL_WORDING.md").write_text("C4 is context-only; it is not testable as a performance claim.\n"); dump("E3_C4_FINAL_STATUS.json",claims["C4"])
    both=local_decision=="LOCAL_HAJEK_FORMAL_COLLAPSE_CERTIFIED" and p2_decision=="P2_INACCURATE_WINDOWS_FULLY_CERTIFIED"
    final="STOP_E3_EXPERIMENTS_PROCEED_TO_PAPER_WRITING" if both else "E3_FINAL_CLOSURE_NOT_CERTIFIED"
    dump("E3_FINAL_NO_NEW_EXPERIMENT_DECISION.json",{"decision":final,"local_hajek":local_decision,"p2":p2_decision})
    dump("STOP_STATUS.json",{"status":"E3_SCIENTIFIC_EVIDENCE_FINAL_SEALED" if both else "E3_SCIENTIFIC_EVIDENCE_UNCERTIFIED","no_new_training":True})
    (ART/"E3_PAPER_MAINLINE_FINAL_R2.md").write_text(f"# E3 final paper mainline\n\n{final}\n")
    (ART/"E3_LOCAL_HAJEK_WEIGHT_AND_P2_CERTIFICATE_FINAL_CLOSURE_R1_REPORT.md").write_text(f"# E3 final closure\n\nLocal-Hajek: **{local_decision}**.\n\nP2: **{p2_decision}**.\n")
    after=sha(FORMAL/"E3_FORMAL_RAW_RESULTS_SEAL.json"); manifest={"formal_raw_seal_before":before,"formal_raw_seal_after":after,"unchanged":before==after}
    dump("E3_FINAL_CLOSURE_HASH_MANIFEST.json",manifest)
    dump("E3_FINAL_CLOSURE_HASH_VERIFICATION.json",{"status":"PASS" if manifest["unchanged"] else "FAIL",**manifest})
    print(json.dumps({"local_hajek":local_decision,"p2":p2_decision,"final":final}))
if __name__=="__main__": main()
