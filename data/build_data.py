"""Build the game's dataset (elections.json) from:
  - raw/<year>.txt         historical results 1824-1972 (checked by verify.py)
  - elections_modern.json  1976-2024 (built by build_modern.py) (MIT Election Lab via Noah Veltman; 2024 from county totals)

Run verify.py first; this script refuses to build if any year fails.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from verify import parse, check, check_known, check_pop

HERE = os.path.dirname(os.path.abspath(__file__))

# Full names, parties and the winner for each historical year.
META = {
1824: ({"Jackson":("Andrew Jackson","Democratic-Republican"),"Adams":("John Quincy Adams","Democratic-Republican"),"Clay":("Henry Clay","Democratic-Republican"),"Crawford":("William H. Crawford","Democratic-Republican")},"Adams",
       "No one won an Electoral College majority, so the House of Representatives picked Adams, even though Jackson had more electoral and popular votes."),
1828: ({"Jackson":("Andrew Jackson","Democratic"),"Adams":("John Quincy Adams","National Republican")},"Jackson","Jackson won the rematch and unseated Adams."),
1832: ({"Jackson":("Andrew Jackson","Democratic"),"Clay":("Henry Clay","National Republican"),"Wirt":("William Wirt","Anti-Masonic"),"Floyd":("John Floyd","Nullifier")},"Jackson","The first election with national nominating conventions."),
1836: ({"Van Buren":("Martin Van Buren","Democratic"),"Harrison":("William Henry Harrison","Whig"),"White":("Hugh Lawson White","Whig"),"Webster":("Daniel Webster","Whig"),"Mangum":("Willie P. Mangum","Whig")},"Van Buren","The Whigs ran several regional candidates, hoping to deny Van Buren a majority. It didn't work."),
1840: ({"Harrison":("William Henry Harrison","Whig"),"Van Buren":("Martin Van Buren","Democratic"),"Birney":("James G. Birney","Liberty")},"Harrison","“Tippecanoe and Tyler Too.” Harrison died one month after taking office."),
1844: ({"Polk":("James K. Polk","Democratic"),"Clay":("Henry Clay","Whig"),"Birney":("James G. Birney","Liberty")},"Polk","Polk, a surprise “dark horse” nominee, won on a platform of annexing Texas."),
1848: ({"Taylor":("Zachary Taylor","Whig"),"Cass":("Lewis Cass","Democratic"),"Van Buren":("Martin Van Buren","Free Soil")},"Taylor","Former president Van Buren's Free Soil run split the Democratic vote in New York."),
1852: ({"Pierce":("Franklin Pierce","Democratic"),"Scott":("Winfield Scott","Whig"),"Hale":("John P. Hale","Free Soil")},"Pierce","The last election in which the Whigs ran as a major party."),
1856: ({"Buchanan":("James Buchanan","Democratic"),"Frémont":("John C. Frémont","Republican"),"Fillmore":("Millard Fillmore","American (Know-Nothing)")},"Buchanan","The first presidential race with a Republican nominee."),
1860: ({"Lincoln":("Abraham Lincoln","Republican"),"Breckinridge":("John C. Breckinridge","Southern Democratic"),"Bell":("John Bell","Constitutional Union"),"Douglas":("Stephen A. Douglas","Democratic (incl. anti-Lincoln fusion tickets)")},"Lincoln","Lincoln won without a single Southern electoral vote. Secession followed within weeks."),
1864: ({"Lincoln":("Abraham Lincoln","National Union"),"McClellan":("George B. McClellan","Democratic")},"Lincoln","Held during the Civil War. The Confederate states did not take part."),
1868: ({"Grant":("Ulysses S. Grant","Republican"),"Seymour":("Horatio Seymour","Democratic")},"Grant","Mississippi, Texas and Virginia had not yet been readmitted and did not vote."),
1872: ({"Grant":("Ulysses S. Grant","Republican"),"Greeley":("Horace Greeley","Liberal Republican / Democratic"),"O'Conor":("Charles O'Conor","Straight-Out Democratic")},"Grant","Greeley died after Election Day, before the Electoral College met, so his electors scattered."),
1876: ({"Hayes":("Rutherford B. Hayes","Republican"),"Tilden":("Samuel J. Tilden","Democratic"),"Cooper":("Peter Cooper","Greenback")},"Hayes","Disputed returns in Florida, Louisiana and South Carolina all went to Hayes, who won 185–184."),
1880: ({"Garfield":("James A. Garfield","Republican"),"Hancock":("Winfield Scott Hancock","Democratic"),"Weaver":("James B. Weaver","Greenback")},"Garfield","The closest national popular vote ever: under 2,000 votes apart."),
1884: ({"Cleveland":("Grover Cleveland","Democratic"),"Blaine":("James G. Blaine","Republican"),"St. John":("John St. John","Prohibition"),"Butler":("Benjamin Butler","Greenback")},"Cleveland","New York, decided by about 1,000 votes, made Cleveland the first Democrat elected since 1856."),
1888: ({"Harrison":("Benjamin Harrison","Republican"),"Cleveland":("Grover Cleveland","Democratic")},"Harrison","Harrison won the Electoral College while Cleveland won the popular vote."),
1892: ({"Cleveland":("Grover Cleveland","Democratic"),"Harrison":("Benjamin Harrison","Republican"),"Weaver":("James B. Weaver","Populist")},"Cleveland","Cleveland won his rematch, the first president to serve two non-consecutive terms."),
1896: ({"McKinley":("William McKinley","Republican"),"Bryan":("William Jennings Bryan","Democratic / Populist"),"Palmer":("John M. Palmer","National Democratic")},"McKinley","Bryan's “Cross of Gold” crusade against McKinley's front-porch campaign."),
1900: ({"McKinley":("William McKinley","Republican"),"Bryan":("William Jennings Bryan","Democratic")},"McKinley","A rematch of 1896. McKinley won again."),
1904: ({"Roosevelt":("Theodore Roosevelt","Republican"),"Parker":("Alton B. Parker","Democratic"),"Debs":("Eugene V. Debs","Socialist")},"Roosevelt","Theodore Roosevelt, who took over after McKinley's assassination, won a term of his own."),
1908: ({"Taft":("William Howard Taft","Republican"),"Bryan":("William Jennings Bryan","Democratic"),"Debs":("Eugene V. Debs","Socialist")},"Taft","Bryan's third and final run. Taft was Roosevelt's hand-picked successor."),
1912: ({"Wilson":("Woodrow Wilson","Democratic"),"Roosevelt":("Theodore Roosevelt","Progressive (Bull Moose)"),"Taft":("William Howard Taft","Republican"),"Debs":("Eugene V. Debs","Socialist")},"Wilson","Roosevelt's Bull Moose run split the Republicans, and the sitting president, Taft, finished third."),
1916: ({"Wilson":("Woodrow Wilson","Democratic"),"Hughes":("Charles Evans Hughes","Republican")},"Wilson","California decided it by fewer than 4,000 votes."),
1920: ({"Harding":("Warren G. Harding","Republican"),"Cox":("James M. Cox","Democratic"),"Debs":("Eugene V. Debs","Socialist")},"Harding","The first presidential election after women won the vote nationwide."),
1924: ({"Coolidge":("Calvin Coolidge","Republican"),"Davis":("John W. Davis","Democratic"),"La Follette":("Robert M. La Follette","Progressive")},"Coolidge","Progressive Robert La Follette carried his home state of Wisconsin."),
1928: ({"Hoover":("Herbert Hoover","Republican"),"Smith":("Al Smith","Democratic")},"Hoover","Al Smith was the first Catholic nominee of a major party."),
1932: ({"Roosevelt":("Franklin D. Roosevelt","Democratic"),"Hoover":("Herbert Hoover","Republican")},"Roosevelt","A Great Depression landslide that ousted a sitting president."),
1936: ({"Roosevelt":("Franklin D. Roosevelt","Democratic"),"Landon":("Alf Landon","Republican"),"Lemke":("William Lemke","Union")},"Roosevelt","Landon carried only Maine and Vermont."),
1940: ({"Roosevelt":("Franklin D. Roosevelt","Democratic"),"Willkie":("Wendell Willkie","Republican")},"Roosevelt","Roosevelt became the first president elected to a third term."),
1944: ({"Roosevelt":("Franklin D. Roosevelt","Democratic"),"Dewey":("Thomas E. Dewey","Republican")},"Roosevelt","Roosevelt won a fourth term during World War II."),
1948: ({"Truman":("Harry S. Truman","Democratic"),"Dewey":("Thomas E. Dewey","Republican"),"Thurmond":("Strom Thurmond","States' Rights (Dixiecrat)"),"Wallace":("Henry A. Wallace","Progressive")},"Truman","The year of the famous “Dewey Defeats Truman” headline. Truman won."),
1952: ({"Eisenhower":("Dwight D. Eisenhower","Republican"),"Stevenson":("Adlai Stevenson","Democratic")},"Eisenhower","Eisenhower ended 20 years of Democratic presidents."),
1956: ({"Eisenhower":("Dwight D. Eisenhower","Republican"),"Stevenson":("Adlai Stevenson","Democratic")},"Eisenhower","A rematch of 1952, which Eisenhower won by even more."),
1960: ({"Kennedy":("John F. Kennedy","Democratic"),"Nixon":("Richard Nixon","Republican"),"Byrd":("Harry F. Byrd","Unpledged electors")},"Kennedy","The first televised debates, and the first election for Alaska and Hawaii."),
1964: ({"Johnson":("Lyndon B. Johnson","Democratic"),"Goldwater":("Barry Goldwater","Republican")},"Johnson","A Johnson landslide. Goldwater won only Arizona and five Deep South states."),
1968: ({"Nixon":("Richard Nixon","Republican"),"Humphrey":("Hubert Humphrey","Democratic"),"Wallace":("George Wallace","American Independent")},"Nixon","George Wallace carried five Southern states."),
1972: ({"Nixon":("Richard Nixon","Republican"),"McGovern":("George McGovern","Democratic")},"Nixon","Nixon won 49 states. McGovern carried only Massachusetts and D.C."),
}

def historical(path):
    year, cands, nat, size, rows = parse(path)
    names = [c[0] for c in cands]
    full, winner, note = META[year]
    # autofix small total mismatches (verify.py logs them)
    states = []
    for st, avail, cv, tot in rows:
        if tot is not None:
            tot = max(tot, sum(v for v, _ in cv))
        states.append([st, avail, [list(x) for x in cv], tot])
    # sides: candidates who carried a state (plurality, or a legislature's electors) or took >= 5% nationally
    natvotes = [sum(r[2][i][0] for r in states) for i in range(len(names))]
    allv = sum(r[3] for r in states if r[3])
    side = set()
    for st, avail, cv, tot in states:
        if tot is None:
            side.add(max(range(len(cv)), key=lambda i: cv[i][1]))
        else:
            side.add(max(range(len(cv)), key=lambda i: cv[i][0]))
    for i, v in enumerate(natvotes):
        if allv and v / allv >= 0.05: side.add(i)
    for i, n in enumerate(names):
        if n in full: pass
    keep = sorted(side, key=lambda i: -nat.get(names[i], 0) * 1e9 - natvotes[i])
    out_c = []
    for i in keep:
        n = names[i]
        fn, party = full.get(n, (n, cands[i][1]))
        out_c.append({"name": fn, "short": n, "party": party, "ev": nat.get(n, 0)})
    st_out = []
    for st, avail, cv, tot in states:
        vals = [cv[i] for i in keep]
        st_out.append([st, avail, vals, tot])
    return {"year": year, "size": size, "cands": out_c, "winner": [c["short"] for c in out_c].index(winner),
            "note": note, "states": st_out}

def modern():
    out = []
    for e in json.load(open(os.path.join(HERE, "elections_modern.json"))):
        dem = {"name": e["dem"], "short": e["dem"].split()[-1], "party": "Democratic", "ev": e["official"][0]}
        gop = {"name": e["gop"], "short": e["gop"].split()[-1], "party": "Republican", "ev": e["official"][1]}
        st = [[a, ev, [[d, dEV], [g, gEV]], tot] for a, d, g, tot, ev, dEV, gEV in e["states"]]
        notes = {1976:"Carter, a former Georgia governor, beat sitting president Gerald Ford and swept nearly the entire South.",
                 1980:"Reagan ousted a sitting president. Independent John Anderson took about 7% of the vote.",
                 1984:"Reagan won 49 states. Mondale carried only his home state of Minnesota and D.C.",
                 1988:"Bush became the first sitting vice president elected president since Martin Van Buren in 1836.",
                 1992:"Independent Ross Perot won about 19% of the vote, the strongest third-party showing since 1912.",
                 1996:"Clinton won a second term. Ross Perot ran again and took about 8%.",
                 2000:"Florida was decided by 537 votes after the Supreme Court stopped the recount. Gore won the national popular vote.",
                 2004:"Bush won a second term, and Ohio was the state that settled it.",
                 2008:"Obama became the first Black president, flipping states like Indiana and North Carolina.",
                 2012:"Obama won reelection, holding nearly every swing state.",
                 2016:"Clinton won the national popular vote, but Trump won the Electoral College by flipping Michigan, Pennsylvania and Wisconsin.",
                 2020:"Biden won more votes than any candidate in history. Many states took days to finish counting mail ballots.",
                 2024:"Trump became the second president to win non-consecutive terms, after Grover Cleveland."}
        out.append({"year": e["year"], "size": 538, "cands": [dem, gop] if e["winner"] == "D" else [gop, dem],
                    "winner": 0, "note": notes[e["year"]],
                    "states": [[a, ev, (v if e["winner"] == "D" else v[::-1]), tot] for a, ev, v, tot in st]})
    return out

if __name__ == "__main__":
    import glob
    raws = sorted(glob.glob(os.path.join(HERE, "raw", "*.txt")))
    bad = [f for f in raws if check(f)[1] or check_known(f) or [p for p in check_pop(f) if p.startswith("OFF")]]
    if bad:
        sys.exit("Refusing to build; these years fail verify.py: " + ", ".join(os.path.basename(b) for b in bad))
    data = [historical(f) for f in raws] + modern()
    data.sort(key=lambda e: e["year"])
    json.dump(data, open(os.path.join(HERE, "elections.json"), "w"), separators=(",", ":"), ensure_ascii=False)
    for e in data:
        print(e["year"], e["size"], len(e["states"]), "states", "|", " vs ".join(f'{c["short"]}({c["ev"]})' for c in e["cands"]), "| winner:", e["cands"][e["winner"]]["short"])
