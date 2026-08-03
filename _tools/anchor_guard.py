# -*- coding: utf-8 -*-
"""Anchor discriminator guard.

The failure this exists to stop is not that two labels differ. It is that
"Anker vs EcoFlow" and "EcoFlow vs Anker" are indistinguishable at a glance and
go to different pages. So the rule is not a fixed string - it is that the link
text must carry something that tells the two apart.

  -> /compare/ecoflow-stream-vs-anker-solix/   must match STREAM|SOLIX|balcony
  -> /compare/anker-vs-ecoflow/                must match brand|ecosystem

Read-only unless --fix is passed. Exit 1 on any failure, so it can sit in front
of the deploy the same way fo_guard.py does.
"""
import io, sys, os, re, html as H
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".git", ".wrangler", "node_modules", "_deploy"}

# Asymmetric on purpose. The failure was one-way: the product page had borrowed
# the brand page's name, so the same string "EcoFlow vs Anker" / "Anker vs
# EcoFlow" pointed at two places. Once the product page always names STREAM or
# SOLIX, no string is ambiguous any more. Policing the brand page as well would
# force a label onto five sentences that read correctly today, and would fix
# nothing - "Anker vs EcoFlow" is that page's honest name.
RULES = {
    "/compare/ecoflow-stream-vs-anker-solix/": (
        re.compile(r"STREAM|SOLIX|balcony", re.I), "EcoFlow STREAM vs Anker SOLIX"),
}
A = re.compile(r'<a\s([^>]*?)href="([^"]+)"([^>]*)>(.*?)</a>', re.S | re.I)

files = []
for dp, dn, fn in os.walk(R):
    if set(os.path.relpath(dp, R).split(os.sep)) & SKIP:
        dn[:] = []
        continue
    dn[:] = [x for x in dn if x not in SKIP]
    files += [os.path.join(dp, f) for f in fn if f.endswith(".html")]

print("anchor guard | %d html files (incl. _templates and _drafts)" % len(files))
assert len(files) > 50, "file list implausibly short"
print("=" * 104)

fail_footer, fail_body = [], []
passing = Counter()
for f in sorted(files):
    t = open(f, encoding="utf-8", errors="replace").read()
    rel = os.path.relpath(f, R)
    for m in A.finditer(t):
        href = m.group(2)
        if href not in RULES:
            continue
        rx, _canon = RULES[href]
        anchor = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", m.group(4)))).strip()
        before = t[:m.start()]
        zone = "footer" if before.rfind("<footer") > before.rfind("</footer>") else "body"
        if rx.search(anchor):
            passing[(href, anchor)] += 1
        else:
            ctx = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ",
                         t[max(0, m.start() - 150):m.end() + 110]))).strip()
            rec = (rel, zone, href, anchor, m.group(0), ctx)
            (fail_footer if zone == "footer" else fail_body).append(rec)

print("PASSING anchors (left alone - the test is the standard, not a fixed string)")
for (href, a), n in passing.most_common():
    print("  x%-4d %-30s %r" % (n, href.split("/")[-2][:28], a))

print("")
print("=" * 104)
print("FAILING - footer (one mechanical swap, %d anchors)" % len(fail_footer))
print("=" * 104)
c = Counter((r[3], r[2]) for r in fail_footer)
for (a, href), n in c.most_common():
    print("  x%-4d %r  ->  %s" % (n, a, RULES[href][1]))

print("")
print("=" * 104)
print("FAILING - body (each one is a sentence, %d anchors)" % len(fail_body))
print("=" * 104)
for rel, zone, href, anchor, raw, ctx in fail_body:
    print("")
    print("  %-46s %r" % (rel, anchor))
    print("     -> %s" % href)
    print("     ...%s..." % ctx[:230])

print("")
print("=" * 104)
print("footer failures: %d anchors | body failures: %d anchors | total %d"
      % (len(fail_footer), len(fail_body), len(fail_footer) + len(fail_body)))
print("distinct files affected: %d"
      % len({r[0] for r in fail_footer + fail_body}))
if fail_footer or fail_body:
    sys.exit(1)
print("clean")
