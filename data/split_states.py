#!/usr/bin/env python3
"""Split /data/plug-in-solar-laws.json into per-state JSON files.

Each /data/states/<slug>.json carries the full state record plus the
inherited top-level keys (schema_version, last_updated, source) so each
file stands alone.

Also writes /data/states/index.json — a thin directory listing of every
per-state file with {slug, state, status, page_url, file}.

Re-run whenever the master dataset changes:
    python3 /root/pluginsolarhub/data/split_states.py
"""
import json
import pathlib

DATA = pathlib.Path("/root/pluginsolarhub/data")
MASTER = DATA / "plug-in-solar-laws.json"
OUT = DATA / "states"

INHERITED_KEYS = ("schema_version", "last_updated", "source", "disclaimer", "license")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    master = json.loads(MASTER.read_text(encoding="utf-8"))

    inherit = {k: master[k] for k in INHERITED_KEYS if k in master}
    states = master["states"]

    index = []
    for s in states:
        slug = s["slug"]
        rec = {**inherit, **s}
        rec["source_file"] = "/data/plug-in-solar-laws.json"
        out_path = OUT / f"{slug}.json"
        out_path.write_text(
            json.dumps(rec, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        index.append({
            "slug": slug,
            "state": s["state"],
            "status": s["status"],
            "page_url": s["page_url"],
            "file": f"/data/states/{slug}.json",
        })

    idx_obj = {
        **inherit,
        "count": len(index),
        "states": index,
    }
    (OUT / "index.json").write_text(
        json.dumps(idx_obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"wrote {len(states)} per-state files + index.json to {OUT}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
