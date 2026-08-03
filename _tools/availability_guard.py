# -*- coding: utf-8 -*-
"""Availability guard - positional, not presence.

The rule is asymmetric, like the anchor guard, because the harm is one-sided:
a page that merely mentions a restricted product harms nobody, and a page that
sends the reader to buy it without saying where it is sold does. So only buy
prompts are policed.

And the check is POSITIONAL. Presence is not enough: on 3 August the page
how-much-does-balcony-solar-cost contained "Utah" twice and both were about
electricity rates in low-tariff states. A presence check would have passed it
while the buy button still said nothing. The restriction has to come BEFORE the
link, or be inside the link's own label - which is the only string a reader
cannot skip, because it is what they look at in order to click.

Exit 1 on any failure.
"""
import io, sys, os, re, json, html as H

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)
SKIP = {".git", ".wrangler", "node_modules", "_deploy"}
WINDOW = 900          # characters of page text allowed between marker and link

DATA = json.load(open(os.path.join(HERE, "availability.json"), encoding="utf-8"))
RESTRICTED = {k: v for k, v in DATA["products"].items()
              if v.get("us_status") == "restricted" and v.get("buy_url_contains")}

A = re.compile(r'<a\s[^>]*?href="([^"]+)"[^>]*>(.*?)</a>', re.S | re.I)

files = []
for dp, dn, fn in os.walk(R):
    if set(os.path.relpath(dp, R).split(os.sep)) & SKIP:
        dn[:] = []
        continue
    dn[:] = [x for x in dn if x not in SKIP]
    files += [os.path.join(dp, f) for f in fn if f.endswith(".html")]

print("availability guard | %d html files | %d restricted product(s)"
      % (len(files), len(RESTRICTED)))
if len(files) < 50:
    print("  file list implausibly short - the skip test is wrong"); sys.exit(1)

checked, passed, failed = [], [], []
for f in sorted(files):
    t = open(f, encoding="utf-8", errors="replace").read()
    rel = os.path.relpath(f, R).replace("\\", "/")
    for pid, p in RESTRICTED.items():
        if p["buy_url_contains"] not in t:
            continue
        marker = p["restriction_marker"]
        for m in A.finditer(t):
            if p["buy_url_contains"] not in m.group(1):
                continue
            label = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).strip()
            in_label = marker.lower() in label.lower()
            before = t[max(0, m.start() - WINDOW):m.start()]
            in_window = marker.lower() in before.lower()
            rec = (rel, pid, label, in_label, in_window)
            checked.append(rec)
            (passed if (in_label or in_window) else failed).append(rec)

print("")
print("PASSED - restriction reaches the reader before the click")
print("-" * 96)
for rel, pid, label, il, iw in passed:
    where = ("label" if il else "") + ("+" if il and iw else "") + ("above" if iw else "")
    print("  %-46s %-34s [%s]" % (rel, label[:34], where))
print("")
print("FAILED - buy prompt with no restriction before it")
print("-" * 96)
for rel, pid, label, il, iw in failed:
    print("  %-46s %-34s  (marker '%s' not in label and not in the %d chars above)"
          % (rel, label[:34], RESTRICTED[pid]["restriction_marker"], WINDOW))
if not failed:
    print("  none")

print("")
print("buy prompts checked: %d | passed: %d | failed: %d"
      % (len(checked), len(passed), len(failed)))
sys.exit(1 if failed else 0)
