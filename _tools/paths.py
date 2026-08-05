# -*- coding: utf-8 -*-
"""The one place any tool learns where things are.

This exists because fo_guard.py was checking the FlexOffers tag in
D:\\repos\\_deploy\\pluginsolarhub while every deploy ran from
D:\\repos\\_deploy\\psh. It reported green against a folder we do not ship.
A guard pointed at the wrong target is worse than no guard, because it
manufactures confidence.

Extended 5 August 2026, for the same reason a second time. tracker_date_guard
had the UK repository path typed into its own body. And D:\\repos\\_deploy held
a folder named heatpumpgranthub, next to hpgh, carrying the same Cloudflare
project name and two unsent drafts. Nothing had gone wrong yet. Nothing had
stopped it either.

So every site is written once, here.
"""
import os

# the US repository, derived from this file so it survives being cloned anywhere
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# the folder wrangler is run from. Not derived - it lives outside the repo.
DEPLOY = r"D:\repos\_deploy\psh"
PROJECT = "pluginsolarhub"
SITE = "https://pluginsolarhub.org"

# directories in the repo that must never reach the web. _drafts holds
# signed-and-ready pages for laws nobody has signed, and press pitches
# nobody has sent.
NEVER_PUBLIC = ("_drafts", "_templates", "_tools")

# every deploy folder lives under here. The guard walks it looking for
# lookalikes, so it must be the real parent, not a guess.
DEPLOY_ROOT = r"D:\repos\_deploy"

# the three sites. changelog=None means the site has no changelog yet and the
# tracker date guard skips it rather than failing on a file that was never
# supposed to exist.
SITES = {
    "US": dict(repo=REPO,
               deploy=DEPLOY,
               project=PROJECT,
               site=SITE,
               changelog="changelog/index.html"),
    "UK": dict(repo=r"D:\repos\balconysolarhub",
               deploy=r"D:\repos\_deploy\bsh",
               project="balconysolarhub",
               site="https://balconysolarhub.co.uk",
               changelog="changelog/index.html"),
    "HPGH": dict(repo=r"D:\repos\heatpumpgranthub",
                 deploy=r"D:\repos\_deploy\hpgh",
                 project="heatpumpgranthub",
                 site="https://heatpumpgranthub.com",
                 changelog=None),
}

# folders that used to be a deploy target, or look like one, and must never be
# one again. Renamed folders keep their old name on this list too: if anyone
# recreates it, the guard refuses.
QUARANTINED = (r"D:\repos\_deploy\pluginsolarhub",
               r"D:\repos\_deploy\heatpumpgranthub",
               r"D:\repos\_deploy\_STALE_2026-08-02_DO_NOT_DEPLOY",
               r"D:\repos\_deploy\_STALE_2026-08-01_UK_DO_NOT_DEPLOY",
               r"D:\repos\_deploy\_STALE_2026-08-05_HPGH_DO_NOT_DEPLOY")

# what robocopy must exclude, spelled out so runbook and guard agree
ROBOCOPY_XD = (".git", ".wrangler") + NEVER_PUBLIC


def describe():
    out = ["  DEPLOY_ROOT %s" % DEPLOY_ROOT,
           "  never public: %s" % ", ".join(NEVER_PUBLIC), ""]
    for name in sorted(SITES):
        s = SITES[name]
        out.append("  %-5s repo   %s" % (name, s["repo"]))
        out.append("        deploy %s   project %s" % (s["deploy"], s["project"]))
    return "\n".join(out)
