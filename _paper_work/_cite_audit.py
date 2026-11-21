"""Crossref/OpenAlex bibliographic audit for reference.bib."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BIB = Path(__file__).resolve().parent / "reference.bib"
OUT = Path(__file__).resolve().parent / "ccfa-review-reports" / "citation_audit_raw.json"
UA = "RAVEN-MCS-citation-audit/1.0 (mailto:raven.mcs.audit@example.com)"


def parse_bib(text: str) -> list[dict]:
    entries = []
    for m in re.finditer(r"@(\w+)\{([^,]+),([\s\S]*?)\n\}", text):
        typ, key, body = m.group(1), m.group(2).strip(), m.group(3)
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", body):
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", fm.group(2)).strip()
        entries.append({"type": typ, "key": key, "fields": fields})
    return entries


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[{}\\'`\"]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_tokens(s: str) -> set[str]:
    stop = {"a", "an", "the", "of", "in", "on", "for", "and", "to", "with", "by"}
    return {t for t in norm(s).split() if t not in stop and len(t) > 2}


def first_author_last(author: str) -> str:
    if not author:
        return ""
    first = author.split(" and ")[0]
    if "," in first:
        return norm(first.split(",")[0])
    parts = first.strip().split()
    return norm(parts[-1]) if parts else ""


def get_json(url: str, timeout: int = 25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def crossref_by_doi(doi: str):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi) + "?mailto=raven.mcs.audit@example.com"
    return get_json(url)["message"]


def crossref_by_title(title: str):
    q = urllib.parse.urlencode({
        "query.bibliographic": title,
        "rows": 5,
        "mailto": "raven.mcs.audit@example.com",
    })
    data = get_json("https://api.crossref.org/works?" + q)
    return data["message"].get("items", [])


def openalex_by_title(title: str):
    q = urllib.parse.urlencode({"search": title, "per_page": 5})
    data = get_json("https://api.openalex.org/works?" + q)
    return data.get("results", [])


def cr_authors(msg: dict) -> list[str]:
    out = []
    for a in msg.get("author") or []:
        fam = a.get("family") or ""
        giv = a.get("given") or ""
        out.append(f"{fam}, {giv}".strip(", "))
    return out


def cr_pages(msg: dict) -> str:
    return (msg.get("page") or "").replace("–", "-")


def cr_year(msg: dict):
    for k in ("published-print", "published", "issued", "published-online"):
        parts = ((msg.get(k) or {}).get("date-parts") or [[None]])[0]
        if parts and parts[0]:
            return int(parts[0])
    return None


def pick_crossref(title: str, items: list[dict]) -> dict | None:
    tset = title_tokens(title)
    best, score = None, 0.0
    for it in items:
        ct = " ".join(it.get("title") or [])
        cset = title_tokens(ct)
        if not tset or not cset:
            continue
        sc = len(tset & cset) / max(len(tset), 1)
        if sc > score:
            best, score = it, sc
    return best if score >= 0.55 else None


def main() -> None:
    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    results = []
    for i, e in enumerate(entries, 1):
        f = e["fields"]
        title = f.get("title", "")
        rec = {
            "key": e["key"],
            "type": e["type"],
            "bib": {
                "title": title,
                "author": f.get("author", ""),
                "year": f.get("year", ""),
                "journal": f.get("journal") or f.get("booktitle", ""),
                "volume": f.get("volume", ""),
                "number": f.get("number", ""),
                "pages": f.get("pages", "").replace("--", "-"),
                "doi": f.get("doi", ""),
            },
            "status": "pending",
            "issues": [],
            "source": None,
        }
        try:
            msg = None
            if rec["bib"]["doi"]:
                try:
                    msg = crossref_by_doi(rec["bib"]["doi"])
                    rec["source"] = "crossref-doi"
                except Exception as ex:
                    rec["issues"].append(f"DOI lookup failed: {ex}")
            if msg is None:
                items = crossref_by_title(title)
                msg = pick_crossref(title, items)
                rec["source"] = "crossref-title" if msg else rec["source"]
            if msg is None:
                rec["status"] = "not_found_crossref"
            else:
                rec["crossref"] = {
                    "title": " ".join(msg.get("title") or []),
                    "authors": cr_authors(msg),
                    "year": cr_year(msg),
                    "container": " ".join(msg.get("container-title") or []),
                    "volume": msg.get("volume") or "",
                    "issue": msg.get("issue") or "",
                    "pages": cr_pages(msg),
                    "doi": msg.get("DOI") or "",
                    "type": msg.get("type") or "",
                    "author_count": len(msg.get("author") or []),
                }
        except Exception as ex:
            rec["status"] = "error"
            rec["issues"].append(str(ex))
        results.append(rec)
        print(f"[{i}/{len(entries)}] {e['key']} -> {rec.get('source') or rec['status']}", flush=True)
        time.sleep(0.35)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
