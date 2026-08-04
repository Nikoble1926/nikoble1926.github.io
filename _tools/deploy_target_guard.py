# -*- coding: utf-8 -*-
"""The deploy folder must not contain anything that must not be public.

_deploy/pluginsolarhub sat on this machine for two days containing _drafts and
_templates. Running wrangler against it would have published nj-signed-READY,
which announces a New Jersey law that has not been signed. Nothing stopped that
except nobody happening to run the command.

Fails the build. Does not warn.
"""
import io, sys, os
import paths

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
print("deploy target guard")
print(paths.describe())

fail = []

if not os.path.isdir(paths.DEPLOY):
    print("  FAIL  deploy folder does not exist: %s" % paths.DEPLOY)
    sys.exit(1)

if os.path.abspath(paths.DEPLOY) in [os.path.abspath(q) for q in paths.QUARANTINED]:
    print("  FAIL  DEPLOY points at a quarantined folder")
    sys.exit(1)

found = []
for name in paths.NEVER_PUBLIC:
    p = os.path.join(paths.DEPLOY, name)
    if os.path.exists(p):
        n = sum(len(f) for _, _, f in os.walk(p)) if os.path.isdir(p) else 1
        found.append((name, n))

# and anywhere deeper, in case a nested copy sneaks in
deep = []
for dp, dn, fn in os.walk(paths.DEPLOY):
    for d in list(dn):
        if d in paths.NEVER_PUBLIC:
            rel = os.path.relpath(os.path.join(dp, d), paths.DEPLOY)
            if rel not in [f[0] for f in found]:
                deep.append(rel)

total = sum(len(f) for _, _, f in os.walk(paths.DEPLOY))
print("")
print("  files in deploy folder      : %d" % total)
print("  forbidden dirs at top level : %s"
      % (", ".join("%s (%d files)" % x for x in found) if found else "none"))
print("  forbidden dirs deeper       : %s" % (", ".join(deep) if deep else "none"))

if found or deep:
    print("")
    print("  FAIL  the deploy folder contains material that must never be public.")
    for name, n in found:
        print("        %s/  %d file(s)" % (name, n))
    for rel in deep:
        print("        %s/" % rel)
    print("  Fix the robocopy /XD list, do not deploy.")
    sys.exit(1)

print("")
print("  PASS  nothing in the deploy folder that must not be public")
