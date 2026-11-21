import pathlib, re, csv
p = pathlib.Path("results_active_set_repair/round_v1/ACTIVE_SET_REPAIR_REPORT.md")
raw = p.read_bytes(); txt = raw.decode("utf-8"); lines = txt.split("\n")
def pipes(s): return s.replace("\\|","").count("|")
i=0; tables=0; bad=0; rows=0
while i < len(lines):
    if lines[i].startswith("|") and i+1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i+1]):
        hdr = pipes(lines[i]); j=i
        while j < len(lines) and lines[j].startswith("|"):
            rows += 1
            if pipes(lines[j]) != hdr: bad += 1; print("  MISMATCH line %d: hdr=%d row=%d" % (j+1,hdr,pipes(lines[j])))
            j += 1
        tables += 1; i = j
    else: i += 1
print("REPORT: tables=%d rows=%d mismatched=%d | size=%dB lines=%d CRLF=%d" % (tables, rows, bad, len(raw), len(lines), raw.count(b"\r\n")))
O = pathlib.Path("results_active_set_repair/round_v1")
e2 = {r["method"]: r for r in csv.DictReader(open(O/"E2_UAIR_SUMMARY.csv", newline="", encoding="utf-8"))}
pa = {(r["comparator"], r["slice"]): r for r in csv.DictReader(open(O/"PAIRED_STATS.csv", newline="", encoding="utf-8"))}
ok = True
for m, exp in (("fedavg_window",1.111932),("fedasync_window",1.111924),("flamf_timealign_adapted",1.112002),
               ("debt_cal",1.114378),("fedau_window",1.112813),("obsuse_window",1.112034),("raven_wo_design",1.113059)):
    if abs(round(float(e2[m]["RMSE_mu_std_mean"]),6)-exp) > 5e-7: ok=False; print("  R1 mismatch", m)
for comp, sl, met, exp in (("fedavg_window","TEST","Delta_group_rel_mean",-3.078),("fedavg_window","ALL20","Delta_group_rel_mean",-2.711),
                           ("debt_cal","TEST","Delta_group_rel_mean",-0.052),("debt_cal","ALL20","Delta_group_rel_mean",-0.089),
                           ("debt_cal","TEST","Delta_c_s_rel_mean",-0.055),("debt_cal","ALL20","Delta_c_s_rel_mean",0.015),
                           ("fedau_window","ALL20","Delta_group_rel_mean",-3.733),("obsuse_window","ALL20","Delta_c_s_rel_mean",-2.143),
                           ("fedavg_window","TEST","RMSE_mu_std_rel_mean",0.545),("obsuse_window","TEST","WorstGroupRMSE_std_rel_mean",0.443)):
    got = round(float(pa[(comp,sl)][met])*100, 3)
    if abs(got-exp) > 2e-3: ok=False; print("  R2 mismatch", comp, sl, met, got, exp)
print("R1/R2 spot-check vs CSVs:", "ALL MATCH" if ok else "MISMATCHES ABOVE")
