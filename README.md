# Election Night Game

Two phone-friendly, single-page election-night games. Open either `index.html` in a browser; nothing to install.

## Decision Desk (`decision-desk/`)
Eight made-up races with fake votes coming in county by county. Call each race before the rival network does without calling one wrong. The parties are Orange and Purple, and "Tonight's races" are the same for everyone on a given day.

## Mystery Election Night (`mystery-election-night/`)
Replay a **real U.S. presidential election night, any year from 1824 to 2024**, without knowing which year it is. The candidates are disguised as colors. You call states and the presidency (by Electoral College majority, which changes by era), then guess the year and see who won and who they beat.

- Every state's final result is real. Only the order and pace of vote counting is simulated.
- Handles 3–5 candidate races, states whose legislature chose the electors, states that didn't exist yet or didn't vote, split electoral votes, and 1824's House of Representatives decision.

## Data (`data/`)

| Years | Source |
|---|---|
| 1976–2020 | MIT Election Data and Science Lab (from the Clerk of the House), via [Noah Veltman's cleaned dataset](https://github.com/veltman/presidential-election-results) |
| 2024 | County results compiled by [Tony McGovern](https://github.com/tonmcg/US_County_Level_Election_Results_08-24), summed by state |
| 1824–1972 | Wikipedia's state-by-state results tables (which cite Dave Leip's Atlas and CQ's Guide to U.S. Elections), transcribed into `data/raw/<year>.txt` |

### Verification (`data/verify.py`)
Every historical year must pass before the game data will build:

1. Each candidate's state electoral votes add up to the official national total from the source page.
2. They also match an **independent** reference list of official electoral vote totals for every election.
3. The states' electoral votes add up to the size of the Electoral College that year.
4. No state awards more electoral votes than it has.
5. In each popular-vote state, the candidate who took all its electoral votes also got the most votes.
6. Candidates' national popular votes, summed from the states, are within 3% of the published national totals.

Result: **38/38 historical years pass**. 84 national popular-vote totals land within 2%, and two differences were reviewed and explained (1824, 1860). See `data/verify-report.txt`. Every manual fix is logged in `data/corrections.md`, and the 1976–2024 build (`data/build_modern.py`) checks all 13 elections against the official electoral totals.

## Rebuild
```
python3 build.py
```
Runs the checks, rebuilds `data/elections.json`, and writes `mystery-election-night/index.html` from `template.html`.
