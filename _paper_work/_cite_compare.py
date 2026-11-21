"""Re-query Crossref/OpenAlex with author+title, then field-compare."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BIB = ROOT / "reference.bib"
RAW = ROOT / "ccfa-review-reports" / "citation_audit_raw.json"
BBL = ROOT / "main.bbl"
OUT = ROOT / "ccfa-review-reports" / "citation_audit_compare.json"
UA = "RAVEN-MCS-citation-audit/1.0 (mailto:raven.mcs.audit@example.com)"


def get_json(url: str, timeout: int = 25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_bib(text: str) -> list[dict]:
    entries = []
    i = 0
    while True:
        m = re.search(r"@(\w+)\{", text[i:])
        if not m:
            break
        typ = m.group(1)
        start = i + m.end()
        # key
        comma = text.find(",", start)
        key = text[start:comma].strip()
        # find matching closing brace of entry
        depth = 1
        j = comma + 1
        while j < len(text) and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        body = text[comma + 1 : j - 1]
        fields = {}
        k = 0
        while True:
            fm = re.search(r"(\w+)\s*=\s*\{", body[k:])
            if not fm:
                break
            fname = fm.group(1).lower()
            vs = k + fm.end()
            d = 1
            p = vs
            while p < len(body) and d:
                if body[p] == "{":
                    d += 1
                elif body[p] == "}":
                    d -= 1
                p += 1
            val = body[vs : p - 1]
            fields[fname] = re.sub(r"\s+", " ", val).strip()
            k = p
        entries.append({"type": typ, "key": key, "fields": fields})
        i = j
    return entries


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    s = re.sub(r"[{}\\'`\"~^]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_tokens(s: str) -> set[str]:
    stop = {"a", "an", "the", "of", "in", "on", "for", "and", "to", "with", "by", "from"}
    return {t for t in norm(s).split() if t not in stop and len(t) > 2}


def title_score(a: str, b: str) -> float:
    ta, tb = title_tokens(a), title_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def bib_authors(author: str) -> list[str]:
    if not author:
        return []
    parts = re.split(r"\s+and\s+", author, flags=re.I)
    out = []
    for p in parts:
        p = p.strip()
        if not p or p.lower() in {"others", "et al", "et al."}:
            continue
        if "," in p:
            fam, giv = [x.strip() for x in p.split(",", 1)]
            out.append(f"{fam}, {giv}")
        else:
            toks = p.split()
            out.append(f"{toks[-1]}, {' '.join(toks[:-1])}" if len(toks) > 1 else p)
    return out


def family(name: str) -> str:
    name = name.replace("{", "").replace("}", "")
    if "," in name:
        return norm(name.split(",")[0])
    toks = name.strip().split()
    return norm(toks[-1]) if toks else ""


def cr_authors(msg: dict) -> list[str]:
    out = []
    for a in msg.get("author") or []:
        fam = a.get("family") or ""
        giv = a.get("given") or ""
        out.append(f"{fam}, {giv}".strip(", "))
    return out


def cr_pages(msg: dict) -> str:
    return (msg.get("page") or "").replace("–", "-").replace("--", "-")


def cr_year(msg: dict):
    for k in ("published-print", "published", "issued", "published-online"):
        parts = ((msg.get(k) or {}).get("date-parts") or [[None]])[0]
        if parts and parts[0]:
            return int(parts[0])
    return None


def pack_crossref(msg: dict) -> dict:
    return {
        "title": " ".join(msg.get("title") or []),
        "authors": cr_authors(msg),
        "year": cr_year(msg),
        "container": " ".join(msg.get("container-title") or []),
        "volume": str(msg.get("volume") or ""),
        "issue": str(msg.get("issue") or ""),
        "pages": cr_pages(msg),
        "doi": msg.get("DOI") or "",
        "type": msg.get("type") or "",
        "author_count": len(msg.get("author") or []),
    }


def good_match(title: str, first_fam: str, msg: dict) -> bool:
    if (msg.get("type") or "") == "component":
        return False
    ct = " ".join(msg.get("title") or [])
    if title_score(title, ct) < 0.72:
        return False
    cauth = cr_authors(msg)
    if first_fam and cauth:
        cf = family(cauth[0])
        if cf and first_fam and cf != first_fam and first_fam not in cf and cf not in first_fam:
            # allow hyphen/prefix variants
            if not (first_fam.replace(" ", "") == cf.replace(" ", "")):
                return False
    return True


def pick(title: str, first_fam: str, items: list[dict]) -> dict | None:
    best, score = None, 0.0
    for it in items:
        if not good_match(title, first_fam, it):
            continue
        sc = title_score(title, " ".join(it.get("title") or []))
        if sc > score:
            best, score = it, sc
    return best


def crossref_search(title: str, author: str, rows: int = 8) -> list[dict]:
    q = {
        "query.title": title,
        "rows": rows,
        "mailto": "raven.mcs.audit@example.com",
    }
    if author:
        q["query.author"] = author.split(" and ")[0].split(",")[0]
    data = get_json("https://api.crossref.org/works?" + urllib.parse.urlencode(q))
    return data["message"].get("items", [])


def openalex_search(title: str) -> dict | None:
    q = urllib.parse.urlencode({"search": title, "per_page": 5})
    data = get_json("https://api.openalex.org/works?" + q)
    items = data.get("results") or []
    best, score = None, 0.0
    for it in items:
        sc = title_score(title, it.get("title") or "")
        if sc > score:
            best, score = it, sc
    if not best or score < 0.72:
        return None
    auths = []
    for a in (best.get("authorships") or []):
        dn = ((a.get("author") or {}).get("display_name") or "").strip()
        if dn:
            toks = dn.split()
            auths.append(f"{toks[-1]}, {' '.join(toks[:-1])}" if len(toks) > 1 else dn)
    loc = best.get("primary_location") or {}
    src = loc.get("source") or {}
    bibl = best.get("biblio") or {}
    year = best.get("publication_year")
    doi = (best.get("doi") or "").replace("https://doi.org/", "")
    return {
        "title": best.get("title") or "",
        "authors": auths,
        "year": year,
        "container": src.get("display_name") or "",
        "volume": str(bibl.get("volume") or ""),
        "issue": str(bibl.get("issue") or ""),
        "pages": f"{bibl.get('first_page') or ''}-{bibl.get('last_page') or ''}".strip("-"),
        "doi": doi,
        "type": best.get("type") or "",
        "author_count": len(auths),
        "openalex_id": best.get("id"),
    }


def page_span(p: str) -> tuple[int | None, int | None]:
    p = (p or "").replace("–", "-").replace("--", "-")
    m = re.match(r"(\d+)\s*-\s*(\d+)", p)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"(\d+)$", p.strip())
    if m:
        return int(m.group(1)), int(m.group(1))
    return None, None


def compare(bib: dict, src: dict) -> list[dict]:
    issues = []
    ba = bib_authors(bib.get("author", ""))
    sa = src.get("authors") or []
    if ba and sa:
        if family(ba[0]) != family(sa[0]) and family(ba[0]) not in family(sa[0]) and family(sa[0]) not in family(ba[0]):
            issues.append({"level": "critical", "field": "first_author", "bib": ba[0], "src": sa[0]})
        # order of overlapping surnames
        bf = [family(x) for x in ba]
        sf = [family(x) for x in sa]
        if len(ba) + 1 < len(sa) and "others" not in bib.get("author", "").lower():
            issues.append({"level": "critical", "field": "author_omission", "bib_n": len(ba), "src_n": len(sa), "missing": sf[len(ba):]})
        elif abs(len(ba) - len(sa)) >= 1 and "others" not in bib.get("author", "").lower() and len(sa) >= 3:
            # middle-name / given-name extras are warning if surnames match
            if bf != sf[: len(bf)] and set(bf) != set(sf[: max(len(bf), len(sf))]):
                issues.append({"level": "warning", "field": "author_count", "bib_n": len(ba), "src_n": len(sa)})
        # given-name mismatch among shared positions
        n = min(len(ba), len(sa))
        for i in range(n):
            if family(ba[i]) != family(sa[i]) and family(ba[i]) not in family(sa[i]) and family(sa[i]) not in family(ba[i]):
                issues.append({"level": "critical", "field": "author_order", "pos": i + 1, "bib": ba[i], "src": sa[i]})
                break
            # given-name token difference (Cao Shuqing vs Shuqin)
            bg = norm(ba[i].split(",", 1)[-1] if "," in ba[i] else "")
            sg = norm(sa[i].split(",", 1)[-1] if "," in sa[i] else "")
            if bg and sg and bg.split()[0] != sg.split()[0] and bg.split()[0][:3] != sg.split()[0][:3]:
                issues.append({"level": "critical", "field": "author_given", "pos": i + 1, "bib": ba[i], "src": sa[i]})
            elif bg and sg and bg != sg:
                issues.append({"level": "warning", "field": "author_given_minor", "pos": i + 1, "bib": ba[i], "src": sa[i]})

    bt, st = bib.get("title", ""), src.get("title", "")
    if title_score(bt, st) < 0.72:
        issues.append({"level": "critical", "field": "title", "bib": bt, "src": st})

    by, sy = str(bib.get("year") or ""), str(src.get("year") or "")
    if by and sy and by != sy:
        # EA vs print: warning if adjacent year
        try:
            dy = abs(int(by) - int(sy))
        except ValueError:
            dy = 99
        issues.append({"level": "warning" if dy == 1 else "critical", "field": "year", "bib": by, "src": sy})

    bv, sv = str(bib.get("volume") or ""), str(src.get("volume") or "")
    if bv and sv and bv != sv:
        issues.append({"level": "warning", "field": "volume", "bib": bv, "src": sv})
    bn, sn = str(bib.get("number") or "").replace("--", "-"), str(src.get("issue") or "")
    if bv and not bn and sn:
        issues.append({"level": "warning", "field": "issue_missing", "src": sn})
    elif bn and sn and bn != sn:
        issues.append({"level": "warning", "field": "issue", "bib": bn, "src": sn})

    bp, sp = (bib.get("pages") or "").replace("--", "-"), src.get("pages") or ""
    b1, b2 = page_span(bp)
    s1, s2 = page_span(sp)
    if b1 and s1:
        delta = max(abs(b1 - s1), abs((b2 or b1) - (s2 or s1)))
        if delta >= 5:
            issues.append({"level": "critical", "field": "pages", "bib": bp, "src": sp, "delta": delta})
        elif delta >= 1:
            issues.append({"level": "warning", "field": "pages", "bib": bp, "src": sp, "delta": delta})
    elif (not bp) and sp and src.get("volume"):
        issues.append({"level": "warning", "field": "pages_missing_in_bib", "src": sp, "note": "early-access metadata drift"})

    bd, sd = (bib.get("doi") or "").lower(), (src.get("doi") or "").lower()
    if bd and sd and bd != sd:
        issues.append({"level": "critical", "field": "doi_mismatch", "bib": bd, "src": sd})
    return issues


def bbl_order() -> dict[str, int]:
    text = BBL.read_text(encoding="utf-8")
    keys = re.findall(r"\\bibitem\{([^}]+)\}", text)
    return {k: i + 1 for i, k in enumerate(keys)}


def verdict(issues: list[dict], found: bool) -> str:
    if not found:
        return "unverifiable"
    levels = {x["level"] for x in issues}
    if "critical" in levels:
        return "needs_fix"
    if "warning" in levels:
        return "check_suggested"
    return "verified"


def main() -> None:
    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    raw = {r["key"]: r for r in json.loads(RAW.read_text(encoding="utf-8"))}
    order = bbl_order()
    results = []
    for i, e in enumerate(entries, 1):
        f = e["fields"]
        key = e["key"]
        title = f.get("title", "")
        author = f.get("author", "")
        first = family(bib_authors(author)[0]) if bib_authors(author) else ""
        bib = {
            "title": title,
            "author": author,
            "year": f.get("year", ""),
            "journal": f.get("journal") or f.get("booktitle", ""),
            "volume": f.get("volume", ""),
            "number": f.get("number", ""),
            "pages": (f.get("pages") or "").replace("--", "-"),
            "doi": f.get("doi", ""),
            "url": f.get("url", ""),
            "note": f.get("note", ""),
            "howpublished": f.get("howpublished", ""),
        }
        rec = {
            "n": order.get(key),
            "key": key,
            "type": e["type"],
            "bib": bib,
            "source": None,
            "record": None,
            "issues": [],
        }
        # reuse raw if it is a good match
        old = raw.get(key, {})
        reused = False
        if old.get("crossref") and old.get("source") in {"crossref-doi", "crossref-title"}:
            dummy = {
                "title": [old["crossref"].get("title")],
                "type": old["crossref"].get("type"),
                "author": [{"family": a.split(",")[0].strip(), "given": a.split(",")[-1].strip() if "," in a else ""} for a in old["crossref"].get("authors") or []],
            }
            if good_match(title, first, dummy):
                rec["record"] = old["crossref"]
                rec["source"] = old["source"] + "-reused"
                reused = True
        if not reused:
            try:
                items = crossref_search(title, author)
                msg = pick(title, first, items)
                if msg is None and bib["doi"]:
                    try:
                        msg = get_json(
                            "https://api.crossref.org/works/"
                            + urllib.parse.quote(bib["doi"])
                            + "?mailto=raven.mcs.audit@example.com"
                        )["message"]
                    except Exception:
                        msg = None
                if msg is not None:
                    rec["record"] = pack_crossref(msg)
                    rec["source"] = "crossref-requery"
                else:
                    oa = openalex_search(title)
                    if oa:
                        rec["record"] = oa
                        rec["source"] = "openalex"
            except Exception as ex:
                rec["issues"].append({"level": "info", "field": "query_error", "detail": str(ex)})
            time.sleep(0.25)
        if rec["record"]:
            rec["issues"].extend(compare(bib, rec["record"]))
        rec["verdict"] = verdict(rec["issues"], bool(rec["record"]))
        results.append(rec)
        print(f"[{i}/{len(entries)}] [{rec['n']}] {key} -> {rec['source'] or rec['verdict']} ({len(rec['issues'])} issues)", flush=True)

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print("COUNTS", counts)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
