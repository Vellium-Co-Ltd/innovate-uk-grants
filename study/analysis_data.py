"""Firm table + outcome panels the analysis reads (no outcomes compared here).

load_firms() -> {crn: {g, sic2, inc_year, closed, ceased_year, status, size, product, award, postcode_area}}
  g = first grant year (treated.tsv t0) or 0 for the never-funded pool. Sector and incorporation from the live register
  (register.tsv) for firms on it, else from the Companies House profile (ch_profiles.jsonl) — the same rule for both groups.
  Cached to data/study/firms.tsv on first build (the register is 466MB; streamed once).
load_panel(name) -> {(crn, year): (value, tag, file, source)} from data/study/panel_<name>.tsv (panel.py cache).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "data" / "study"
CLOSED = ("dissolved", "liquidation", "converted-closed", "insolvency-proceedings", "administration", "receivership",
          "removed", "closed")
COLS = ["crn", "g", "sic2", "inc_year", "closed", "ceased_year", "status", "size", "product", "award", "postcode_area"]


def gbp(v):
    """Pounds with a sign, as every results file writes them."""
    return f"£{v:+,.0f}"


def _build():
    firms = {}
    for line in list(open(ROOT / "treated.tsv"))[1:]:
        p = line.rstrip("\n").split("\t")
        firms[p[0]] = dict(g=int(p[2]), product=p[3], size=p[4], award=float(p[6] or 0))
    for line in list(open(ROOT / "pool.tsv"))[1:]:
        p = line.rstrip("\n").split("\t")
        if p[0] not in firms:
            firms[p[0]] = dict(g=0, product="", size="", award=0.0)
    with open(ROOT / "register.tsv") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(head)}
        for line in fh:
            p = line.rstrip("\n").split("\t")
            f = firms.get(p[0])
            if f is None:
                continue
            sic = p[ix["SICCode.SicText_1"]].split(" ")[0]
            f.update(sic2=sic[:2] if sic[:1].isdigit() else "", inc_year=int(p[ix["IncorporationDate"]][:4] or 0)
                     if p[ix["IncorporationDate"]][:4].isdigit() else 0, status=p[ix["CompanyStatus"]],
                     postcode_area="".join(ch for ch in p[ix["RegAddress.PostCode"]].split(" ")[0] if ch.isalpha())[:2],
                     ceased_year=int(p[ix["DissolutionDate"]][:4]) if p[ix["DissolutionDate"]][:4].isdigit() else 0)
    for line in open(ROOT / "ch_profiles.jsonl"):
        r = json.loads(line)
        f = firms.get(r["crn"])
        if f is None or "status" in f or r.get("not_found"):
            continue
        sic = (r.get("sic_codes") or [""])[0]
        f.update(sic2=sic[:2] if sic[:1].isdigit() else "", inc_year=int((r.get("date_of_creation") or "0")[:4]),
                 status=r.get("company_status") or "", ceased_year=int((r.get("date_of_cessation") or "0")[:4]),
                 postcode_area="".join(ch for ch in (r.get("postcode") or "").split(" ")[0] if ch.isalpha())[:2])
    for f in firms.values():
        f.setdefault("sic2", ""); f.setdefault("inc_year", 0); f.setdefault("status", "not_found")
        f.setdefault("ceased_year", 0); f.setdefault("postcode_area", "")
        f["closed"] = int(any(w in f["status"].lower().replace(" ", "-") for w in CLOSED) or f["ceased_year"] > 0)
    with open(ROOT / "firms.tsv", "w") as fh:
        fh.write("\t".join(COLS) + "\n")
        for crn, f in sorted(firms.items()):
            fh.write("\t".join(str(f[c]) if c != "crn" else crn for c in COLS) + "\n")


def load_firms():
    if not (ROOT / "firms.tsv").exists():
        _build()
    out = {}
    for line in list(open(ROOT / "firms.tsv"))[1:]:
        p = dict(zip(COLS, line.rstrip("\n").split("\t")))
        out[p["crn"]] = dict(p, g=int(p["g"]), inc_year=int(p["inc_year"]), closed=int(p["closed"]),
                             ceased_year=int(p["ceased_year"]), award=float(p["award"]))
    return out


def load_panel(name):
    out = {}
    for line in list(open(ROOT / f"panel_{name}.tsv"))[1:]:
        crn, y, v, tag, file, src = line.rstrip("\n").split("\t")
        out[(crn, int(y))] = (float(v), tag, file, src)
    return out
