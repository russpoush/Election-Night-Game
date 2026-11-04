# Data corrections log

Every change made to what was read from Wikipedia, and why.

| Year | State | Change | Reason |
|---|---|---|---|
| 1824 | VA | Total votes 15,371 → 15,466 | Candidate votes added to more than the total; total set to their sum (0.6%) |
| 1828 | ME | EVs: Adams 8, Jackson 1 | Reader returned 2 EVs; Maine split by district (official 8–1) |
| 1828 | NY | EVs: Jackson 20, Adams 16 | Reader returned 2 EVs; New York split by district (official 20–16) |
| 1832 | MD | District rows merged into one statewide row (Jackson 19,156, Clay 19,160) | Game uses one tile per state; EVs Clay 5, Jackson 3, 2 not cast |
| 1832 | MO | Total votes 5,192 → 13,664 | Total was smaller than the candidates' votes; set to their sum |
| 1860 | NJ, NY, PA | Anti-Lincoln "fusion" ticket votes put in the Douglas column (total minus listed candidates) | Reader dropped the fusion columns; fusion tickets combined Douglas, Bell and Breckinridge backers |
| 1860 | OR | 3 EVs to Lincoln (not Breckinridge) | Lincoln won the most votes; official national total confirms it |
| 1860 | TX | Total votes 63,061 → 63,079 | Candidate votes exceeded total by 18; set to their sum |
| 1864 | LA, TN | Removed | Their electoral votes were not counted by Congress; the reader's Tennessee numbers (30,000 / 5,000) were round placeholders, not real returns |
| 1864 | NV | 3 EVs available, 2 cast for Lincoln | One Nevada elector was snowbound and didn't vote |
| 1872 | AR, LA | EVs set to 0 (Grant won both popular votes) | Congress rejected both states' electoral votes; Grant's official total is 286 |
| 1872 | Greeley states | EVs kept under Greeley (66) | Greeley died after Election Day; his electors scattered to Hendricks (42), Brown (18), Jenkins (2), Davis (1) and 3 Georgia votes for Greeley were thrown out. The game treats them as Greeley's states. |
| 1896 | all | Bryan's Democratic, Populist and Silver Party ballot lines merged into one Bryan column | Bryan was the nominee of all three; the game shows one Bryan |
| 1896 | CO | Repaired a malformed field from the reader | Merged Bryan total 161,005 and 4 EVs, matching the official result |
| 1960 | AL, MS, OK | "Unpledged electors" and Byrd merged into one column (Byrd) | Unpledged electors from Alabama (6) and Mississippi (8) plus one Oklahoma faithless elector voted for Harry Byrd (15 total) |
| 1968 | CO–WY, DC | Rows taken from a Wikipedia mirror (wiki.krisyotam.com) of the same article | The main page was too long for the reader and cut off after California |

## Senate and House (MIT Election Lab files)

| Race | Change | Reason |
|---|---|---|
| Senate 2014 Louisiana | Left out | Source file's Cassidy (1,712,379) and Landrieu (1,561,210) totals are corrupted; the real November open-primary figures were about 0.6M each |
| Senate 2020 Wyoming | Lummis set to Republican | Party field is blank in the source |
| Senate 1980 North Dakota | Missing | Not in the source file |
| Senate 1986 North Carolina, 2010 Illinois | Only the special election is in the file | Both seats were filled by elections held the same day; the file lists just the special |
| House, all years | Party = Democratic if any ballot line is Democratic (incl. DFL/NPL), Republican if any line includes "Republican" (incl. Minnesota's "Independent-Republican") | Fusion and state party labels |
| House 1996 Texas (13 districts) | November court-ordered open elections used (filed as special "primaries") | Redistricting replaced the regular general election |
| House 2006 Texas (4 districts) | Special general election used | Redistricting replaced the regular general election |
| House, all years | D.C. delegate and territories left out | Non-voting members |
| House, unopposed seats | Decided at poll close | Some states (e.g., Florida) don't print unopposed races, so there are no vote counts |
