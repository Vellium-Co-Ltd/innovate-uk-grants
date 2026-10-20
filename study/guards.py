"""The plan check the analysis runs (public form of Vellium's shared study guards).

check_study_lock refuses when PROTOCOL.md no longer matches the fingerprint in data/study/PROTOCOL-LOCK.json, or when a
locked version has no archived text matching its fingerprint in study/protocol_versions/. Vellium's internal review list
(the reporting standard and lessons register each plan is reviewed against) is not part of this release; review_missing
returns nothing here.
"""
import hashlib
import json
from pathlib import Path


def review_missing(review_path):
    return []


def check_study_lock(study, data=None):
    study = Path(study)
    data = Path(data) if data else study.parent / "data" / study.name
    lock = json.loads((data / "PROTOCOL-LOCK.json").read_text())
    if hashlib.sha256((study / "PROTOCOL.md").read_bytes()).hexdigest() != lock["sha256"]:
        raise SystemExit(f"PROTOCOL.md changed since the lock ({lock['locked_utc']})")
    for h in lock.get("history", []) + [lock]:
        arch = study / "protocol_versions" / f"PROTOCOL-v{h['version']}.md"
        if not arch.exists() or hashlib.sha256(arch.read_bytes()).hexdigest() != h["sha256"]:
            raise SystemExit(f"plan v{h['version']} has no archived text matching its fingerprint")
    return lock
