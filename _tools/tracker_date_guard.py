# -*- coding: utf-8 -*-
"""The "Tracker last updated" line must equal the newest changelog entry.

Two sites, two changelogs, two shapes. There is no shared parser, because
guessing that two pages are alike is how the wrong number gets published:

  US  entries are  <li><strong>Month D, YYYY</strong>
  UK  entries are  <tr><td><strong>D Month YYYY</strong>

Three conditions, in order:

  1. Only dates in entry position count. The UK page carries "27 August 2026"
     inside a <div class="note"> after the table - that is the date the
     regulations come into force, not a changelog entry - and "17 July 2026"
     inside the body of an entry. Both must be ignored, so the pattern is
     anchored to the opening markup of an entry rather than searched for
     anywhere on the page.
  2. Dates in the future relative to build time are dropped. That excludes the
     UK row "~ October 2026 expected", and it maintains itself: in October that
     row becomes past and starts counting, with no code change.
  3. The newest of what remains.

The word is "updated", not "verified". "Verified" would claim we re-checked all
fifty states that day. We did not, and the changelog says so in its own scope
note.

Exit 1 on mismatch.
"""
import io, sys, os, re, datetime
import paths

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
TODAY = datetime.date.today()

US_ENTRY = re.compile(r"<li><strong>([A-Z][a-z]+ \d{1,2}, \d{4})</strong>")
# also matches a month-year row such as "~ October 2026", so that the future
# rule is what excludes it rather than the shape of the string
UK_ENTRY = re.compile(r"<tr><td><strong>(?:~\s*)?"
                      r"((?:\d{1,2} )?[A-Z][a-z]+ \d{4})</strong>")
US_FMT, UK_FMT = "%B %d, %Y", "%d %B %Y"

SITES = [
    dict(name="US", repo=paths.REPO,
         changelog="changelog/index.html", entry=US_ENTRY, fmt=US_FMT,
         out_fmt=lambda d: d.strftime("%B %#d, %Y") if os.name == "nt"
                           else d.strftime("%B %-d, %Y"),
         targets=[("state-legality/index.html",
                   re.compile(r"(<strong>Tracker last updated:</strong>\s*)"
                              r"([A-Z][a-z]+ \d{1,2}, \d{4})")),
                  ("state-legality/index.html",
                   re.compile(r"(\(last updated )([A-Z][a-z]+ \d{1,2}, \d{4})(\))"))]),
    dict(name="UK", repo=r"D:\repos\balconysolarhub",
         changelog="changelog/index.html", entry=UK_ENTRY, fmt=UK_FMT,
         out_fmt=lambda d: (d.strftime("%#d %B %Y") if os.name == "nt"
                            else d.strftime("%-d %B %Y")),
         targets=[("changelog/index.html",
                   re.compile(r"(<strong>Tracker last updated:</strong>\s*)"
                              r"(\d{1,2} [A-Z][a-z]+ \d{4})"))]),
]

fail = 0
for s in SITES:
    print("")
    print("%s  %s" % (s["name"], s["repo"]))
    cl = os.path.join(s["repo"], s["changelog"])
    if not os.path.exists(cl):
        print("  FAIL  changelog not found: %s" % cl); fail += 1; continue
    t = open(cl, encoding="utf-8", errors="replace").read()

    raw = s["entry"].findall(t)
    parsed, future = [], []
    for r in raw:
        d = None
        for f in (s["fmt"], "%B %Y"):
            try:
                d = datetime.datetime.strptime(r, f).date()
                # a month-year entry means "some time that month" - treat it as
                # the last day, so it stops being future only once the month is over
                if f == "%B %Y":
                    nxt = datetime.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
                    d = nxt - datetime.timedelta(days=1)
                break
            except ValueError:
                pass
        if d is None:
            print("  skip unparsable entry date: %r" % r); continue
        (future if d > TODAY else parsed).append((r, d))
    print("  entries in entry position : %d" % len(raw))
    if future:
        print("  dropped as future         : %s" % ", ".join(r for r, _ in future))
    if not parsed:
        print("  FAIL  no past-dated entries"); fail += 1; continue
    newest = max(d for _, d in parsed)
    want = s["out_fmt"](newest)
    print("  newest past entry         : %s" % want)

    # prove the exclusions: dates that exist on the page but are not entries
    anywhere = set(re.findall(r"\b\d{1,2} [A-Z][a-z]+ \d{4}\b", t)) | \
               set(re.findall(r"\b[A-Z][a-z]+ \d{1,2}, \d{4}\b", t))
    ignored = sorted(anywhere - set(r for r, _ in parsed) - set(r for r, _ in future))
    print("  dates on the page ignored : %d%s"
          % (len(ignored), ("  e.g. " + ", ".join(ignored[:4])) if ignored else ""))

    for rel, rx in s["targets"]:
        p = os.path.join(s["repo"], rel)
        if not os.path.exists(p):
            print("  FAIL  %s not found" % rel); fail += 1; continue
        body = open(p, encoding="utf-8", errors="replace").read()
        ms = list(rx.finditer(body))
        if not ms:
            print("  FAIL  %-34s no 'Tracker last updated' line matching the pattern" % rel)
            fail += 1
            continue
        for m in ms:
            got = m.group(2)
            ok = got == want
            fail += 0 if ok else 1
            print("  %-4s  %-34s says %-18s wants %-18s"
                  % ("PASS" if ok else "FAIL", rel, got, want))

print("")
print("=" * 78)
if fail:
    print("tracker date guard: %d mismatch(es) - the line disagrees with the changelog" % fail)
    sys.exit(1)
print("tracker date guard: every 'Tracker last updated' line matches its own changelog")
