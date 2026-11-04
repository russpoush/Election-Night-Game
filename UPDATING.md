# Keeping the election data current

The games only use **final, certified results that pass the checks**. This file is the routine for adding new elections and for steadily filling older gaps. Scheduled check-ins follow it; so can anyone else.

## Ground rules
1. **Certified results only.** Never add an election before its states certify (usually mid-November to mid-December). Morning-after numbers change.
2. **Every year must pass its checker** before the game is rebuilt. `python3 build.py` refuses to build otherwise.
3. **Every manual fix goes in `data/corrections.md`** with the reason. Never fill a gap from memory; leave it out and log it.
4. **One independent check per data type.** Totals from the source must match a reference that did not come from the same page (official seat or electoral totals, or a list of known winners).
5. **Credit every source** in the README and the game's reveal screen.

## Where each data type comes from

| Data | File(s) | Source | Checker |
|---|---|---|---|
| President 1824–1972 | `data/raw/<year>.txt` | Wikipedia "<year> United States presidential election" state tables | `data/verify.py` (official EV totals, an independent EV list, popular-vote sums) |
| President 1976–2024 | `data/elections_modern.json` | MIT Election Lab via veltman/presidential-election-results; 2024 from tonmcg county results | `data/build_modern.py` (official EV totals) |
| Senate 1976–2020 | `data/congress.json` | MIT Election Lab "U.S. Senate" (doi:10.7910/DVN/PEJ5QU) | `data/build_congress.py` (class sizes, known winners) |
| House 1976–2022 | `data/congress.json` | MIT Election Lab "U.S. House" (doi:10.7910/DVN/IG0UN2) | `data/build_congress.py` (435 districts, published seat totals) |
| Governor 1976–2024 | `data/governor/<year>.txt` | Wikipedia "<year> United States gubernatorial elections" summary tables | `data/build_governor.py` (race counts, known winners) |

Access notes: this workspace reaches GitHub, PyPI and npm from the shell, but not Wikipedia or most other sites. The web reader opens a Wikipedia page only if it came from a search result or the user pasted it, so for a batch of years, ask the user to paste the page links. When a Wikipedia page is too long for the reader, a Kiwix mirror copy of the same article works (used for 1968).

## Routine after each November election (run in mid-December)
1. Confirm states have certified. If not, wait and check again in January.
2. **President years:** get state results (MIT's release, or Wikipedia's state table), add them to `data/elections_modern.json` via `build_modern.py`, and add the year's official EV totals to its checks.
3. **Senate and House:** check whether MIT has published the new year. If not, transcribe from Wikipedia's "<year> United States Senate elections" / House results, then check against published seat totals (House: within 2 seats; Senate: race count and known winners).
4. **Governor:** add `data/governor/<year>.txt` from Wikipedia's yearly page and add the race count to `EXPECTED` and a few known winners to `SPOT` in `build_governor.py`.
5. Run `python3 build.py`, play one night of each new year in a browser, then commit and push. GitHub Pages updates the public site automatically.

## Backlog (pick up one item per check-in)
- [ ] Senate 2022 and 2024 (not yet in the MIT file used here)
- [ ] House 2024
- [ ] 2026 Senate, House and governor (after certification, December 2026)
- [ ] Governor odd-year races (VA, NJ, KY, LA, MS) as their own short nights
- [ ] Senate popular elections 1914–1974 (Wikipedia yearly pages)
- [ ] House seat totals before 1976 (state-level delegation results)
- [ ] Presidential 1789–1820 as an electoral-vote-only mode (no popular vote in many states)
- [ ] County-level maps for modern presidential years (tonmcg data covers 2008–2024)
- [ ] Watch for newer MIT Election Lab releases on GitHub mirrors (search repos for `1976-2024-senate`, `1976-2024-house`)
