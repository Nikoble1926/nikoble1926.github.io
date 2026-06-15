PRE-BUILT SIGNING TEMPLATES — pluginsolarhub.org
================================================

Two pending plug-in solar bills are sitting on governors' desks
(as of June 14, 2026):

  NY  — SUNNY Act / A.9111C / S.8512C (sponsored by State Sen. Liz Krueger)
        Cap 1,200W. Awaiting Gov. Hochul.
  NH  — SB 540
        Cap 1,200W. Awaiting Gov. Ayotte.

When either is signed, this folder has everything ready to ship the
news story + a pitch to journalists in < 30 minutes.

This folder is intentionally NOT in sitemap.xml. The HTML files include
<meta name="robots" content="noindex,nofollow"> as a belt-and-suspenders
guard. Do not link to these from any live page.

Files
-----
  ny-signed-READY.html   <- drop-in replacement for /state-legality/new-york/index.html
  nh-signed-READY.html   <- drop-in replacement for /state-legality/new-hampshire/index.html
  ny-pitch-READY.txt     <- short journalist pitch (PV Magazine / CleanTechnica style)
  nh-pitch-READY.txt     <- ditto for NH
  README.txt             <- this file

Placeholders to fill in (case-sensitive, literal brackets)
----------------------------------------------------------
  [[SIGN_DATE]]          Pretty signing date, e.g. "July 8, 2026"
  [[SIGN_DATE_ISO]]      ISO date for JSON-LD, e.g. "2026-07-08"
  [[EFFECTIVE_DATE]]     Pretty effective date, e.g. "October 1, 2026"
  [[GOVERNOR]]           e.g. "Kathy Hochul" (NY) or "Kelly Ayotte" (NH)
  [[CAP_W]]              The watt cap, e.g. "1,200"
  [[STATE_ORDINAL]]      "7th" or "8th" depending on whether it's the
                         next state to sign after Connecticut
  [[SOURCE_URL_PRIMARY]] The first authoritative source — usually a
                         pv-magazine-usa.com or state governor press
                         release URL
  [[REPORTER_NAME]]      First name of the journalist you're pitching

Go-live checklist (about 15 minutes once a bill is signed)
----------------------------------------------------------
  1. Find the primary source (governor press release + PV Magazine USA).
     Confirm exact signing date, effective date, cap, governor name.
  2. Copy the appropriate file out:
       cp _drafts/ny-signed-READY.html state-legality/new-york/index.html
       (or cp _drafts/nh-signed-READY.html state-legality/new-hampshire/index.html)
  3. Replace every [[PLACEHOLDER]] in the copied file. Use one careful
     sed -i pass per placeholder (case-sensitive). Verify by grepping
     for any remaining "[[" in the file.
  4. Remove these two lines from the copied file (they're in the head):
       <meta name="robots" content="noindex,nofollow"><!-- DRAFT -->
       <!-- DRAFT — remove this line when going live -->
  5. Update /data/plug-in-solar-laws.json:
        legislation.status:         "passed_awaiting_governor" -> "signed"
        legislation.date:           bill action date           -> SIGN_DATE_ISO
        legislation.effective:      null                       -> EFFECTIVE_DATE_ISO
        legislation.signed_by:      null                       -> "Gov. <name>"
        legislation.source_url:     null                       -> primary source URL
     Also: bump top-level last_updated to today's date.
  6. Re-run the per-state JSON splitter:
        python3 /root/pluginsolarhub/data/split_states.py
  7. Update /state-legality/index.html badge + tag for the state from
     "Gray area" to "Early mover" (green badge class="g").
  8. Update /sitemap.xml:
        <lastmod> for /state-legality/<slug>/ -> today
        <lastmod> for /state-legality/         -> today
        <lastmod> for /data/plug-in-solar-laws.json (if listed) -> today
  9. git add -A && git commit -m "<State>: <bill> signed — page goes live"
        && git push origin master
 10. Poll Pages build until built. Verify live:
        curl -sI https://pluginsolarhub.org/state-legality/<slug>/ | head -1
        curl -s  https://pluginsolarhub.org/state-legality/<slug>/ | grep -c "Quick answer"
 11. IndexNow ping:
        python3 /root/storm-watch/storm_watch.py --ping \
          "https://pluginsolarhub.org/state-legality/<slug>/" \
          "https://pluginsolarhub.org/state-legality/" \
          "https://pluginsolarhub.org/data/plug-in-solar-laws.json" \
          "https://pluginsolarhub.org/data/states/<slug>.json" \
          "https://pluginsolarhub.org/data/states/index.json" \
          "https://pluginsolarhub.org/sitemap.xml"
 12. Fill in the corresponding pitch template (replace all
     [[PLACEHOLDER]] occurrences) and email two or three journalists at
     PV Magazine USA, CleanTechnica, and any state-level energy outlet.

Notes
-----
 - The signing chronology in the HTML lists the next state as the
   [[STATE_ORDINAL]] state to sign. If NY signs first it's the 7th and
   NH (when signed later) is the 8th — update the chronology list inside
   the OTHER HTML file when the second one signs.
 - Do not commit these *-READY.* files with their placeholders filled in
   — overwrite the live page and leave the templates pristine for any
   future re-use (e.g. CA, NJ, MA, RI when they introduce their bills).
