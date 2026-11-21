"""Write papers.md and papers.csv for the literature-search folder (no candidate met the inclusion bar)."""
from __future__ import annotations

import pathlib

D = pathlib.Path(r"C:\Cursor\raven.mcs\literature-search-20261009-concentrated-target")
D.mkdir(parents=True, exist_ok=True)

(D / "papers.md").write_text("""# Papers — dataset with a target concentrated at the aggregation level

**No scored candidate.** Twelve queries (listed in `search-notes.md`) returned fragmentary PDF excerpts
without a stable title, author list, venue or landing page, plus off-topic hits. Under the source policy
in `references/search-and-scoring.md` — untraceable PDFs and snippet-only evidence are excluded — none
could be entered in the table below.

| title | venue/year | type | insight | completeness | numeric evidence | quality | URL |
|---|---|---|---|---|---|---|---|
| _none_ | | | | | | | |

The unverified leads that a follow-up pass should start from are in `search-notes.md`, together with the
class-level hypotheses and the two candidate routes. Nothing in this folder may be cited as a source
until its record has been verified.
""", encoding="utf-8")

(D / "papers.csv").write_text(
    "title,venue_year,paper_type,insight,completeness,numeric_evidence,quality,url\n"
    "# no candidate met the inclusion bar; see search-notes.md for unverified leads\n",
    encoding="utf-8")

for f in ("papers.md", "papers.csv", "search-notes.md"):
    p = D / f
    print(f"  {p.name:<18} {p.stat().st_size:>6} B")
