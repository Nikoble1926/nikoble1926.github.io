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


================================================================
NJ STANDBY — added July 14, 2026 (New Jersey, the 9th state)
================================================================

New pending bill on the Governor's desk:

  NJ — Garden State Plug-In Solar Act (S2368 / A4836)
       Cap 1,200W. Passed BOTH chambers unanimously June 30, 2026
       (Senate 40-0, Assembly 79-0). Awaiting Gov. Sherrill.
       Effective 6 months after enactment.

Files:
  nj-signed-READY.html   <- drop-in replacement for /state-legality/new-jersey/index.html
  nj-signed-pitch-READY.txt <- journalist pitch (Grist / Solar Power World / pv mag US + NJ local)

NJ placeholders to fill (ONLY from primary source on signing day):
  [[SIGN_DATE]]          e.g. "July 20, 2026"  (governor.nj.gov press release)
  [[SIGN_DATE_ISO]]      e.g. "2026-07-20"     (JSON-LD dates)
  [[EFFECTIVE_DATE]]     sign date + 6 months, e.g. "January 20, 2027" — CONFIRM from bill text
  [[CHAPTER_OR_LAW_REF]] the enacted citation assigned on signing, e.g. "P.L.2026, c.NN"
  [[SOURCE_URL_PRIMARY]] Gov. Sherrill press release URL (governor.nj.gov)
  [[REPORTER_NAME]]      pitch only

Already baked in (verified, do NOT placeholder): bill S2368/A4836, Gov. Sherrill,
unanimous 40-0 / 79-0 on June 30 2026, cap 1,200W, cert "nationally recognized
testing laboratory", ~18c/kWh, utilities PSE&G + JCP&L, ordinal = 9th, the
8-state chronological list (UT, ME, VA, CO, MD, CT, VT, NH).

NH LESSON: never fill a date/effective/citation from a tracker or news article —
only from governor.nj.gov + njleg.state.nj.us bill text. If the bill text grants
"no fee / no utility approval," you MAY add it then (it is NOT in our verified
sources today, so the template deliberately does NOT claim it).

------------------------------------------------------------
DAY-OF RUNBOOK (NJ signs) — swap page + update ALL "8 -> 9" cross-refs
------------------------------------------------------------
0. Watcher alert -> confirm from PRIMARY source (governor.nj.gov press release
   + njleg.state.nj.us bill text). Get exact sign date, effective date, chapter.
1. Copy template live and fill placeholders + remove the two DRAFT lines:
     cp _drafts/nj-signed-READY.html state-legality/new-jersey/index.html
     (remove: <meta name="robots" content="noindex,nofollow"> line
      and the "<!-- DRAFT — remove this line when going live -->" comment)
   Grep the file for "[[" to confirm zero remaining placeholders.
2. Data:
     data/plug-in-solar-laws.json (NJ entry): status passed_awaiting_governor -> signed;
       date -> SIGN_DATE_ISO; effective null -> EFFECTIVE_DATE_ISO; signed_by null ->
       "Gov. Sherrill"; source_url -> primary. Bump top-level last_updated.
     data/states/new-jersey.json: same (or re-run the splitter).
3. **THE "8 -> 9" CROSS-REFERENCES (pre-computed — update every one):**
   a. index.html (homepage):
        "8 states now allow plug-in solar" -> "9 states now allow plug-in solar"
        "New Hampshire just signed" -> "New Jersey just signed"
        badge: "8 states &middot; UT&middot;ME&middot;VA&middot;CO&middot;MD&middot;CT&middot;VT&middot;NH"
          -> "9 states ... &middot;NH&middot;NJ"
   b. state-legality/index.html (tracker):
        "8 states have signed plug-in solar into law (CO, ME, MD, UT, VA, CT, VT, NH)"
          -> "9 states ... (CO, ME, MD, UT, VA, CT, VT, NH, NJ)"  [appears TWICE]
        NJ row badge: "Passed legislature — awaiting Governor" -> "Legal — signed"
          (green badge class="g")
   c. changelog/index.html: ADD a new dated entry "New Jersey signs S2368/A4836 —
        9th state". (Do NOT change the existing "NH is the 8th" entry.)
   d. state-legality/new-york/index.html: THE TRAP —
        "NY would be the 9th state to sign" -> "10th"  (NY is now behind NJ).
        Also append New Jersey to NY's national-context list if present.
   e. state-legality/new-hampshire/index.html: NH stays the 8th (do NOT change its
        ordinal). Optional: append "New Jersey — S2368/A4836 (SIGN_DATE)" as #9 to
        its "signed-into-law list now" and drop NJ from any "awaiting" mention.
   f. OPTIONAL (older truncated lists): state-legality/connecticut/ still shows a
        list ending at CT (6th) and omits VT/NH/NJ — pre-existing staleness, only
        touch if doing a full pass.
   To be safe on the day, re-grep so nothing new is missed:
        grep -rl "8 states"  (count refs)
        grep -rl "National context"  (ordered lists)
        grep -rl "would be the 9th"  (NY trap)
4. sitemap.xml: bump <lastmod> for /state-legality/new-jersey/, /state-legality/,
   and (if listed) the data JSON + any changed page above -> today.
5. Deploy chain (CURRENT method — NOT the old "git add -A" below):
     git add EXPLICIT PATHS ONLY (LICENSE case-collision on Windows — never add -A/-u):
       git add state-legality/new-jersey/index.html index.html state-legality/index.html
               changelog/index.html state-legality/new-york/index.html
               data/plug-in-solar-laws.json data/states/new-jersey.json sitemap.xml
       git commit -m "New Jersey: Garden State Plug-In Solar Act signed — page live (9th state)"
       git push origin master
     cd D:\repos\nikoble1926.github.io; git pull
     python _tools\predeploy.py   (must exit 0 - it blocks the deploy if not)
robocopy D:\repos\nikoble1926.github.io D:\repos\_deploy\psh /MIR /XD .git .wrangler
     cd D:\repos\_deploy\psh
     npx wrangler pages deploy . --project-name pluginsolarhub --commit-dirty=true
6. Live verify: new-jersey page shows "Legal — signed" + "9th state"; homepage +
   tracker show "9 states"; NY shows "10th". 0 residual "[[".
7. IndexNow (US key 88adfba1df1e4d34a88399b5e8c915a8): ping new-jersey URL +
   state-legality/ + homepage + tracker + changelog + NY + the two data JSONs + sitemap.
8. GSC Request Indexing: via CENTRAL TASK only (executor profile has no GSC access).
9. Pitch: fill nj-signed-pitch-READY.txt, present to Nikos -> send ONLY on OK.
10. Log everything.

NOTE: the older "Go-live checklist" above (steps using `git add -A`, /root/ server
paths, storm_watch.py) is from the server-era workflow. On the laptop use the
explicit-paths + robocopy + wrangler chain in step 5 above.
