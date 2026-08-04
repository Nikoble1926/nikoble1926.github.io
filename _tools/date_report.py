# -*- coding: utf-8 -*-
"""Report, not a gate.

legislation.effective and certification_requirement.effective are allowed to
differ - Virginia's law commences 1 July 2026 while its certification clause
commences 1 January 2027, and both are correct. What is dangerous is for them to
differ without anyone knowing, which is how a naive in-force count put Virginia
in the wrong column.

So this prints and always exits 0.
"""
import io, sys, os, json, datetime
import paths

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
D = json.load(open(os.path.join(paths.REPO, "data", "plug-in-solar-laws.json"),
                   encoding="utf-8"))
states = D["states"] if isinstance(D, dict) and "states" in D else D
TODAY = datetime.date.today()

rows, diverge = [], []
for s in states:
    leg = s.get("legislation") or {}
    cr = leg.get("certification_requirement")
    if not cr:
        continue
    a, b = leg.get("effective"), cr.get("effective")
    rows.append((s["state"], a, b, a == b))
    if a != b:
        diverge.append((s["state"], a, b))

print("effective-date report  (%d states with a certification requirement)" % len(rows))
print("  %-16s %-12s %-12s %s" % ("state", "law", "requirement", ""))
for st, a, b, same in sorted(rows):
    print("  %-16s %-12s %-12s %s" % (st, a, b, "" if same else "<-- differ"))

print("")
if diverge:
    print("  %d state(s) where the law and the certification clause commence on"
          % len(diverge))
    print("  different dates. This is legal and may be correct. It is listed so that")
    print("  anything counting 'in force' uses certification_requirement.effective:")
    for st, a, b in diverge:
        print("     %-16s law %s, requirement %s" % (st, a, b))
else:
    print("  no divergence")

inforce = [r for r in rows if datetime.date(*map(int, r[2].split("-"))) <= TODAY]
print("")
print("  in force by certification_requirement.effective on %s: %d of %d"
      % (TODAY, len(inforce), len(rows)))
sys.exit(0)
