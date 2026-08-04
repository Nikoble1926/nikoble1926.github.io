# -*- coding: utf-8 -*-
"""The one place any tool learns where things are.

This exists because fo_guard.py was checking the FlexOffers tag in
D:\\repos\\_deploy\\pluginsolarhub while every deploy ran from
D:\\repos\\_deploy\\psh. It reported green against a folder we do not ship.
A guard pointed at the wrong target is worse than no guard, because it
manufactures confidence.

So the path is written once, here, and every tool imports it. If the deploy
folder moves again it moves in one line, and nothing is left behind looking at
the old one.
"""
import os

# the repository, derived from this file so it survives being cloned anywhere
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# the folder wrangler is run from. Not derived - it lives outside the repo.
DEPLOY = r"D:\repos\_deploy\psh"

PROJECT = "pluginsolarhub"
SITE = "https://pluginsolarhub.org"

# directories in the repo that must never reach the web. _drafts holds
# signed-and-ready pages for laws nobody has signed.
NEVER_PUBLIC = ("_drafts", "_templates", "_tools")

# folders that used to be deploy targets and must never be one again
QUARANTINED = (r"D:\repos\_deploy\pluginsolarhub",
               r"D:\repos\_deploy\_STALE_2026-08-02_DO_NOT_DEPLOY")

# what robocopy must exclude, spelled out so runbook and guard agree
ROBOCOPY_XD = (".git", ".wrangler") + NEVER_PUBLIC


def describe():
    return "\n".join(["  REPO    %s" % REPO,
                      "  DEPLOY  %s" % DEPLOY,
                      "  PROJECT %s" % PROJECT,
                      "  never public: %s" % ", ".join(NEVER_PUBLIC)])
