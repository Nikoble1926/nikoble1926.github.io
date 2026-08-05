# -*- coding: utf-8 -*-
"""No deploy folder may contain anything that must not be public, and no
folder that is not a deploy target may be able to act like one.

_deploy/pluginsolarhub sat on this machine for two days containing _drafts and
_templates. _deploy/heatpumpgranthub sat next to _deploy/hpgh carrying the same
Cloudflare project name, two unsent press drafts, and one page fewer than the
live site. Neither was ever deployed. Nothing prevented it either - in both
cases the only protection was that nobody happened to run the command from the
wrong folder.

A folder is "armed" when its .wrangler cache names a live Cloudflare project.
Armed and unknown fails the build. Armed and quarantined warns, because the
label is the mitigation and deletion is the fix.

Fails the build. Does not warn.
"""
import io, sys, os, json
import paths

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("deploy target guard")
print(paths.describe())


def key(p):
    return os.path.normcase(os.path.abspath(p))


def nfiles(p):
    return sum(len(f) for _, _, f in os.walk(p))


def forbidden_in(root):
    """every NEVER_PUBLIC directory anywhere under root, relative to it"""
    out = []
    for dp, dn, fn in os.walk(root):
        for d in dn:
            if d in paths.NEVER_PUBLIC:
                out.append(os.path.relpath(os.path.join(dp, d), root))
    return sorted(out)


def project_of(p):
    """the Cloudflare project this folder would deploy to, or None"""
    f = os.path.join(p, ".wrangler", "cache", "pages.json")
    try:
        with open(f, encoding="utf-8") as fh:
            return json.load(fh).get("project_name")
    except Exception:
        return None


QUAR = set(key(q) for q in paths.QUARANTINED)
KNOWN = dict((key(s["deploy"]), n) for n, s in paths.SITES.items())
LIVE = set(s["project"] for s in paths.SITES.values())
fail = []

print("")
print("-" * 78)
print("known deploy targets")
for name in sorted(paths.SITES):
    d = paths.SITES[name]["deploy"]
    print("")
    print("  %-5s %s" % (name, d))
    if not os.path.isdir(d):
        print("        FAIL  does not exist")
        fail.append("%s: deploy folder missing" % name)
        continue
    if key(d) in QUAR:
        print("        FAIL  this is a quarantined folder")
        fail.append("%s: target is quarantined" % name)
        continue
    got = project_of(d)
    want = paths.SITES[name]["project"]
    bad = forbidden_in(d)
    print("        files %d   project %s" % (nfiles(d), got))
    if got is not None and got != want:
        print("        FAIL  wrangler cache names %r, paths.py says %r" % (got, want))
        fail.append("%s: project name mismatch" % name)
    if bad:
        print("        FAIL  contains material that must never be public:")
        for b in bad:
            print("              %s/  %d file(s)" % (b, nfiles(os.path.join(d, b))))
        fail.append("%s: %s" % (name, ", ".join(bad)))
    elif got in (None, want):
        print("        PASS")

print("")
print("-" * 78)
print("everything else in %s" % paths.DEPLOY_ROOT)
if not os.path.isdir(paths.DEPLOY_ROOT):
    print("  FAIL  deploy root does not exist")
    sys.exit(1)
for entry in sorted(os.listdir(paths.DEPLOY_ROOT)):
    p = os.path.join(paths.DEPLOY_ROOT, entry)
    if not os.path.isdir(p) or key(p) in KNOWN:
        continue
    proj = project_of(p)
    quar = key(p) in QUAR
    bad = forbidden_in(p)
    print("")
    print("  %s" % entry)
    print("        files %d   project %s   quarantined %s"
          % (nfiles(p), proj, "yes" if quar else "NO"))
    if bad:
        print("        carries %s" % ", ".join(bad))
    if proj in LIVE:
        if quar:
            print("        WARN  armed but labelled. Delete it.")
        else:
            print("        FAIL  armed and not quarantined - one wrong cd publishes it")
            fail.append("%s: armed lookalike for project %s" % (entry, proj))
    elif not quar:
        print("        WARN  unknown folder, not armed")

print("")
print("=" * 78)
if fail:
    for f in fail:
        print("  FAIL  %s" % f)
    print("deploy target guard: %d problem(s)" % len(fail))
    sys.exit(1)
print("deploy target guard: three targets clean, nothing else armed")
