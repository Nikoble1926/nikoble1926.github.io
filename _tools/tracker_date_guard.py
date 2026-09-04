# -*- coding: utf-8 -*-
"""A freshness line must equal the artefact it claims to describe.

Rewritten 4 September 2026. The previous version compared the visible line
against the newest changelog entry. That held while the changelog only recorded
data work. It stopped holding the day the changelog also became a register of
corrections: adding a line saying "we fixed a wrong sentence in the privacy
policy" made the guard demand that the fifty-state tracker advertise itself as
freshly reviewed. It had not been. The guard was asking the page to lie.

Badges cannot rescue it. US entries carry L (law) or D (dataset / site update),
but a privacy correction is literally a site update, two L entries are
themselves corrections, one entry carries no badge at all, and the UK table has
no per-row classification whatsoever - only three section headings, one of which
mixes a dataset release, a new guide and a correction. Neither site encodes
"did this touch the data", which is the only question that matters here.

So the guard stops reading prose and reads the artefact:

  US   state-legality/index.html says "last updated <date>", four times.
       Truth = max(last_reviewed) across data/plug-in-solar-laws.json.
       All four occurrences must equal it AND each other.

  UK   changelog/index.html says "Dataset last updated: <date>".
       Truth = last_updated in data/uk-plug-in-solar.json.

Both are measured, self-maintaining, and move only when the data moves.

Run with --selftest to exercise the failure paths on its own. main() runs them
first and refuses to report on the real files if a case that must fail does not.

Exit 1 on mismatch.
"""
import io, sys, os, re, json, datetime
import paths

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Every phrasing of the freshness line on the US tracker page: the JSON-LD
# answer, the visible answer box, the tracker line and the citation block.
# The L is capitalised in two of the four ("Last updated August 26, 2026.")
# and lower case in the other two. Writing the pattern from memory found two
# of four; the selftest caught it before it reached a real file.
US_LINE = re.compile(r"(?:Tracker last updated:</strong>\s*|[Ll]ast updated )"
                     r"([A-Z][a-z]+ \d{1,2}, \d{4})")
UK_LINE = re.compile(r"<strong>Dataset last updated:</strong>\s*"
                     r"(\d{1,2} [A-Z][a-z]+ \d{4})")

fmt_us = lambda d: d.strftime("%B %#d, %Y") if os.name == "nt" else d.strftime("%B %-d, %Y")
fmt_uk = lambda d: d.strftime("%#d %B %Y") if os.name == "nt" else d.strftime("%-d %B %Y")


def _walk(o, key):
    """every value stored under `key`, at any depth"""
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and isinstance(v, str):
                out.append(v)
            out += _walk(v, key)
    elif isinstance(o, list):
        for v in o:
            out += _walk(v, key)
    return out


def newest_reviewed(blob):
    """US truth: the most recent date any state record was reviewed."""
    vals = sorted(set(_walk(blob, "last_reviewed")))
    if not vals:
        return None, 0
    return datetime.datetime.strptime(vals[-1], "%Y-%m-%d").date(), len(vals)


def dataset_updated(blob):
    """UK truth: the dataset's own last_updated field."""
    v = blob.get("last_updated")
    if not v:
        return None
    return datetime.datetime.strptime(v, "%Y-%m-%d").date()


def check_text(text, rx, want):
    """(found, mismatched). Zero occurrences is a failure in its own right:
    it means the line was renamed or deleted and nobody told the guard."""
    found = rx.findall(text)
    return found, [g for g in found if g != want]


def selftest():
    """The negative cases must fail. A guard that only proves the happy path
    proves nothing - that is how the previous version's green was trusted."""
    ok = True

    def want(label, cond):
        nonlocal ok
        print("     %s %s" % ("ok  " if cond else "FAIL", label))
        if not cond:
            ok = False

    print("  selftest: US truth")
    blob = {"states": [{"last_reviewed": "2026-08-03"}, {"last_reviewed": "2026-08-25"},
                       {"nested": {"last_reviewed": "2026-07-01"}}]}
    d, n = newest_reviewed(blob)
    want("max of three dates, one nested = 2026-08-25", str(d) == "2026-08-25" and n == 3)
    want("empty dataset returns None", newest_reviewed({})[0] is None)

    print("  selftest: UK truth")
    want("last_updated read", str(dataset_updated({"last_updated": "2026-09-02"})) == "2026-09-02")
    want("missing field returns None", dataset_updated({}) is None)

    print("  selftest: US page, four occurrences")
    good = ('{"text":"... Last updated August 25, 2026."} '
            '<span class="tag">Last updated August 25, 2026.</span> '
            '<strong>Tracker last updated:</strong> August 25, 2026 &middot; '
            '(last updated August 25, 2026), https://...')
    f, bad = check_text(good, US_LINE, "August 25, 2026")
    want("all four found and matching", len(f) == 4 and not bad)
    drift = good.replace("(last updated August 25, 2026)", "(last updated August 26, 2026)", 1)
    f2, bad2 = check_text(drift, US_LINE, "August 25, 2026")
    want("ONE stale occurrence out of four MUST fail",
         len(f2) == 4 and bad2 == ["August 26, 2026"])
    f3, bad3 = check_text("nothing here", US_LINE, "August 25, 2026")
    want("a page with no line at all MUST fail", not f3)

    print("  selftest: UK page")
    ukgood = '<span class="tag"><strong>Dataset last updated:</strong> 2 September 2026</span>'
    f4, bad4 = check_text(ukgood, UK_LINE, "2 September 2026")
    want("matching line passes", len(f4) == 1 and not bad4)
    f5, bad5 = check_text(ukgood.replace("2 September", "16 August"), UK_LINE, "2 September 2026")
    want("stale line MUST fail", bad5 == ["16 August 2026"])
    f6, _ = check_text('<strong>Tracker last updated:</strong> 2 September 2026', UK_LINE,
                       "2 September 2026")
    want("the OLD label no longer counts as the line", not f6)

    print("  selftest: %s" % ("all cases behaved" if ok else "A CASE DID NOT BEHAVE"))
    return ok


def main():
    print("tracker date guard - freshness lines against the data they describe")
    print("")
    if not selftest():
        print("")
        print("SELFTEST FAILED - refusing to report on the real files")
        return 1
    print("")

    fail = 0

    # ---- US -------------------------------------------------------------
    repo = paths.SITES["US"]["repo"]
    print("US  %s" % repo)
    dpath = os.path.join(repo, "data", "plug-in-solar-laws.json")
    ppath = os.path.join(repo, "state-legality", "index.html")
    if not os.path.exists(dpath):
        print("  FAIL  dataset not found: %s" % dpath); fail += 1
    elif not os.path.exists(ppath):
        print("  FAIL  page not found: %s" % ppath); fail += 1
    else:
        d, n = newest_reviewed(json.load(open(dpath, encoding="utf-8")))
        if d is None:
            print("  FAIL  no last_reviewed anywhere in the dataset"); fail += 1
        else:
            want = fmt_us(d)
            print("  distinct last_reviewed values : %d" % n)
            print("  newest (the truth)            : %s" % want)
            body = open(ppath, encoding="utf-8", errors="replace").read()
            found, bad = check_text(body, US_LINE, want)
            print("  occurrences on the page       : %d" % len(found))
            if not found:
                print("  FAIL  state-legality/index.html has no freshness line"); fail += 1
            for g in found:
                print("  %-4s  %-30s says %-18s wants %s"
                      % ("PASS" if g == want else "FAIL", "state-legality/index.html", g, want))
            fail += len(bad)
            if found and len(set(found)) > 1:
                print("  FAIL  the page disagrees with itself: %s" % sorted(set(found)))
                fail += 1

    # ---- UK -------------------------------------------------------------
    repo = paths.SITES["UK"]["repo"]
    print("")
    print("UK  %s" % repo)
    dpath = os.path.join(repo, "data", "uk-plug-in-solar.json")
    ppath = os.path.join(repo, "changelog", "index.html")
    if not os.path.exists(dpath):
        print("  FAIL  dataset not found: %s" % dpath); fail += 1
    elif not os.path.exists(ppath):
        print("  FAIL  page not found: %s" % ppath); fail += 1
    else:
        d = dataset_updated(json.load(open(dpath, encoding="utf-8")))
        if d is None:
            print("  FAIL  dataset has no last_updated"); fail += 1
        else:
            want = fmt_uk(d)
            print("  dataset last_updated (truth)  : %s" % want)
            body = open(ppath, encoding="utf-8", errors="replace").read()
            found, bad = check_text(body, UK_LINE, want)
            print("  occurrences on the page       : %d" % len(found))
            if not found:
                print("  FAIL  changelog/index.html has no 'Dataset last updated' line")
                fail += 1
            for g in found:
                print("  %-4s  %-30s says %-18s wants %s"
                      % ("PASS" if g == want else "FAIL", "changelog/index.html", g, want))
            fail += len(bad)

    print("")
    print("=" * 78)
    if fail:
        print("tracker date guard: %d mismatch(es) - a line disagrees with its dataset" % fail)
        return 1
    print("tracker date guard: every freshness line matches the data it describes")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    sys.exit(main())
