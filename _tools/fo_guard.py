# -*- coding: utf-8 -*-
"""Standing check: the FlexOffers verification tag is still present, byte-exact,
and still inside <head> — on disk and live.

Run this after any homepage edit. There is no generator for the US homepage, so
nothing regenerates the tag if it is lost; this is what makes the loss loud
instead of silent months later when FlexOffers re-checks.

Exit code 1 if anything fails.
"""
import io, os, sys, time, urllib.request
import paths

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
TAG = b'<meta name="fo-verify" content="7f02fbe3-a7e7-42c6-b70d-5b03813ee93d" />'
R = paths.REPO
FILES = [("source homepage", R + r"\index.html"),
         ("page template", R + r"\_templates\page-v2.html"),
         ("deploy copy", os.path.join(paths.DEPLOY, "index.html"))]

fail = 0
for name, p in FILES:
    try:
        b = open(p, "rb").read()
    except FileNotFoundError:
        print("  %-16s MISSING FILE" % name); fail += 1; continue
    n = b.count(TAG)
    hd = b.lower().find(b"</head>")
    pos = b.find(TAG)
    ok = n == 1 and 0 < pos < hd
    fail += 0 if ok else 1
    print("  %-16s %s  occurrences=%d  pos=%d  </head>=%d  in-head=%s"
          % (name, "PASS" if ok else "FAIL", n, pos, hd, 0 < pos < hd))

try:
    url = "https://pluginsolarhub.org/?v=%d" % int(time.time())
    live = urllib.request.urlopen(urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache",
                      "Pragma": "no-cache"}), timeout=45).read()
    n = live.count(TAG)
    hd = live.lower().find(b"</head>")
    pos = live.find(TAG)
    ok = n == 1 and 0 < pos < hd
    fail += 0 if ok else 1
    print("  %-16s %s  occurrences=%d  pos=%d  </head>=%d  in-head=%s"
          % ("LIVE homepage", "PASS" if ok else "FAIL", n, pos, hd, 0 < pos < hd))
    if pos > -1:
        print("")
        print("  exact string as returned live:")
        print("  " + repr(live[pos:pos + len(TAG)].decode("utf-8")))
        print("  byte-identical to the supplied string:",
              live[pos:pos + len(TAG)] == TAG)
        print("")
        print("  context (60 bytes either side):")
        print("  " + repr(live[max(0, pos - 60):pos + len(TAG) + 20].decode("utf-8", "replace")))
except Exception as e:
    print("  %-16s FETCH FAIL %s" % ("LIVE homepage", str(e)[:110])); fail += 1

print("")
print("RESULT:", "ALL PASS" if not fail else "%d FAILURE(S)" % fail)
sys.exit(1 if fail else 0)
