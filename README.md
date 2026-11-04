# Election Night Game

Two phone-friendly, single-page election-night games. Open either `index.html` in a browser; nothing to install.

## Decision Desk (`decision-desk/`)
Eight made-up races with fake votes coming in county by county. Call each race before the rival network does without calling one wrong. The parties are Orange and Purple, and "Tonight's races" are the same for everyone on a given day.

## Mystery Election Night (`mystery-election-night/`)
Replay a **real U.S. election night** without knowing which year it is: presidential (1824–2024), **U.S. Senate (1976–2020)**, **U.S. House (1976–2022)** or **governor (1976–2024)**. The candidates are disguised as colors. You call states and the presidency (by Electoral College majority, which changes by era), then guess the year and see who won and who they beat.

- Every state's final result is real. Only the order and pace of vote counting is simulated.
- Senate nights: call each race (specials included), then which party wins the most races. House nights: call which party wins each state's delegation (with a district-by-district view), then House control (218 seats).
- Ranks scale with the most points possible that night, so every year and race type is equally fair.
- Handles 3–5 candidate races, states whose legislature chose the electors, states that didn't exist yet or didn't vote, split electoral votes, and 1824's House of Representatives decision.

## Data (`data/`)

| Years | Source |
|---|---|
| 1976–2020 | MIT Election Data and Science Lab (from the Clerk of the House), via [Noah Veltman's cleaned dataset](https://github.com/veltman/presidential-election-results) |
| 2024 | County results compiled by [Tony McGovern](https://github.com/tonmcg/US_County_Level_Election_Results_08-24), summed by state |
| Senate 1976–2020 | MIT Election Lab "U.S. Senate 1976–2020" (doi:10.7910/DVN/PEJ5QU), via [coatless/raw-data](https://github.com/coatless/raw-data) |
| House 1976–2022 | MIT Election Lab "U.S. House 1976–2022" (doi:10.7910/DVN/IG0UN2), via [TidyTuesday 2023-11-07](https://github.com/rfordatascience/tidytuesday/tree/main/data/2023/2023-11-07) |
| Governor 1976–2024 (even years) | Wikipedia's "<year> United States gubernatorial elections" results tables, transcribed into `data/governor/<year>.txt` (winner and runner-up shares) |
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

### Senate and House checks (`data/build_congress.py`)
- **House:** every year has exactly 435 districts, and party seat totals match the published post-election results within 2 seats for all 24 elections (most match exactly).
- **Senate:** every year has the right number of regular races for its Senate class (with 4 documented gaps in the source), and 38 well-known races (Franken 2008, Murkowski's 2010 write-in, Georgia 2020 and others) match.
- "Winner" means most votes on election night. Later runoffs (Georgia 2020, etc.) are noted in the game.

### Governor checks (`data/build_governor.py`)
- Every year has the expected number of November governor races (11–37), with no duplicates and no territories.
- Winner and runner-up shares are consistent (winner ahead, total no more than 100%).
- 137 well-known races, from an independent list, have the right winner and party.
- Party totals per year match commonly cited figures (for example, Republicans won 24 of 36 in 1994; 2022 split 18–18).
- Only vote shares are available, so governor nights show percentages, not raw vote counts.

## Rebuild
```
python3 build.py
```
Runs the checks, rebuilds `data/elections.json`, and writes `mystery-election-night/index.html` from `template.html`.
