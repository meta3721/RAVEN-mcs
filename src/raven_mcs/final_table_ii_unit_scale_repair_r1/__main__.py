from raven_mcs.final_table_ii_unit_scale_repair_r1.pipeline import run

if __name__ == "__main__":
    result = run()
    print(result["status"], result["gates"].get("n_pass"), "/", result["gates"].get("n_total"))
    raise SystemExit(0 if result["all_gates_pass"] else 1)
