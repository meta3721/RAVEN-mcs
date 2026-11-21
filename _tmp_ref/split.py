import pathlib, collections
p = pathlib.Path("results_active_set_repair/round_v1/WORKTREE_DIFF.sha256")
codes = collections.Counter(l.split("  ")[1] for l in p.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#"))
print("WORKTREE_DIFF split:", dict(codes), "| total", sum(codes.values()))
