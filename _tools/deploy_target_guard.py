# -*- coding: utf-8 -*-
"""No deploy folder may contain anything that must not be public, and no
folder that is not a deploy target may be able to act like one.

_deploy/pluginsolarhub sat on this machine for two days containing _drafts and
_templates. _deploy/heatpumpgranthub sat next to _deploy/hpgh carrying the same
Cloudflare project name, two unsent press drafts, and one page fewer than the
live site. Neither was ever deployed. Nothing prevented it either - in both
cases the only protection was that nobody happened to run the command from the
wrong folder.

Extended twice more on 5 August 2026, both times because the guard itself had
looked at the wrong place and printed reassurance:

  - D:\\repos\\_deploy carries its own .wrangler cache, from a deploy run out of
    the parent folder on 29 July. This version walked the children of the root
    and never the root, so it looked for _deploy/.wrangler/.wrangler/cache and
    called the root "not armed". A deploy from there would have published 712
    files - including all three quarantine folders whole - to heatpumpgranthub.
  - project_of() caught every exception and returned None, and the caller read
    None as "not armed". A cache it cannot parse now says so out loud.

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
    """What Cloudflare project would a deploy from this folder go to?

    Returns (status, project):
      ("none",       None)    no .wrangler cache - the folder is inert
      ("armed",      "name")  the cache names a live project
      ("half",       None)    a cache, an account, but no project chosen
      ("unreadable", None)    a cache is there and we could not parse it

    The last state is why this returns a status at all. The first version
    caught every exception and returned None, and the caller read None as
    "not armed". A test bait written by PowerShell 5.1 carried a UTF-8 BOM,
    json.load raised, and the guard called an armed folder safe. Reading it
    with utf-8-sig fixes that one bait. Refusing to be silent about a file we
    cannot read fixes the class.
    """
    f = os.path.join(p, ".wrangler", "cache", "pages.json")
    if not os.path.exists(f):
        return ("none", None)
    try:
        with open(f, encoding="utf-8-sig") as fh:
            name = json.load(fh).get("project_name")
    except Exception as e:
        print("        cannot read %s: %s" % (f, e))
        return ("unreadable", None)
    return ("armed", name) if name else ("half", None)


QUAR = set(key(q) for q in paths.QUARANTINED)
KNOWN = dict((key(s["deploy"]), n) for n, s in paths.SITES.items())
LIVE = set(s["project"] for s in paths.SITES.values())

fail = []

# Folders we deleted ourselves on 9 August 2026. Everything below asks "is it
# armed?" - this one does not. We removed these; if one is back, either someone
# restored a backup over the top of _deploy or a script we do not know about
# recreated it. Both are reasons to stop, and neither becomes safe by the folder
# happening to be empty today.
print("")
print("-" * 78)
print("folders deleted on 9 August 2026 - existence alone fails")
for q in paths.DELETED_2026_08_09:
    if os.path.isdir(q):
        st, proj = project_of(q)
        print("  %-58s PRESENT  (%s, %d file(s))" % (q, st, nfiles(q)))
        print("        FAIL  this folder was deleted on 9 Aug 2026. It is back.")
        fail.append("%s: deleted folder has reappeared" % os.path.basename(q))
    else:
        print("  %-58s absent" % q)
print("")
print("-" * 78)
print("folders that must not be deploy targets at all")


def report_footprint(label, p, fatal):
    """A wrangler cache here means someone once deployed from this folder."""
    st, proj = project_of(p)
    if st == "none":
        print("  %-46s clean" % label)
        return
    bad = forbidden_in(p)
    n = nfiles(p)
    print("  %-46s %s  project %s" % (label, st, proj))
    print("        %d file(s), %s"
          % (n, ("carries " + ", ".join(bad)) if bad else "nothing forbidden"))
    if st == "armed" and fatal:
        print("        FAIL  a deploy from here publishes all of the above to %r" % proj)
        fail.append("%s: armed, would publish %d files to %s" % (label, n, proj))
    else:
        print("        WARN  a wrangler cache does not belong here. Remove it.")


# the parent of every deploy folder. It holds the quarantined copies, so a
# deploy from here publishes everything we ever quarantined.
report_footprint(paths.DEPLOY_ROOT, paths.DEPLOY_ROOT, fatal=True)
# the repositories. These hold _drafts, _templates, _tools and .git.
for name in sorted(paths.SITES):
    report_footprint(paths.SITES[name]["repo"], paths.SITES[name]["repo"], fatal=True)

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
    st, got = project_of(d)
    want = paths.SITES[name]["project"]
    bad = forbidden_in(d)
    print("        files %d   project %s" % (nfiles(d), got))
    if st == "unreadable":
        print("        FAIL  a wrangler cache we cannot read - assume armed")
        fail.append("%s: unreadable wrangler cache" % name)
        continue
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
    st, proj = project_of(p)
    quar = key(p) in QUAR
    bad = forbidden_in(p)
    print("")
    print("  %s" % entry)
    print("        files %d   project %s   quarantined %s"
          % (nfiles(p), proj, "yes" if quar else "NO"))
    if bad:
        print("        carries %s" % ", ".join(bad))
    if st == "unreadable":
        print("        FAIL  a wrangler cache we cannot read - assume armed")
        fail.append("%s: unreadable wrangler cache" % entry)
        continue
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
