# -*- coding: utf-8 -*-
"""Runs every guard. Exit 1 if any fails. Call this before robocopy.

    python _tools/predeploy.py && robocopy ... && npx wrangler pages deploy ...

The point is that it refuses rather than warns. A guard that prints a warning
into a scrollback nobody reads is the same as no guard.
"""
import io, sys, os, subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
GUARDS = ["deploy_target_guard.py", "fo_guard.py", "anchor_guard.py",
          "availability_guard.py", "tracker_date_guard.py"]
REPORTS = ["date_report.py"]   # printed, never fatal

results = []
for g in GUARDS:
    print("")
    print("#" * 96)
    print("# %s" % g)
    print("#" * 96)
    r = subprocess.run([sys.executable, os.path.join(HERE, g)])
    results.append((g, r.returncode))

for g in REPORTS:
    print("")
    print("#" * 96)
    print("# %s   (report only - cannot fail the build)" % g)
    print("#" * 96)
    subprocess.run([sys.executable, os.path.join(HERE, g)])

print("")
print("=" * 96)
for g, rc in results:
    print("  %-26s %s" % (g, "PASS" if rc == 0 else "FAIL (exit %d)" % rc))
bad = [g for g, rc in results if rc]
print("=" * 96)
if bad:
    print("DEPLOY BLOCKED by: %s" % ", ".join(bad))
    sys.exit(1)
print("all guards pass - safe to sync and deploy")
