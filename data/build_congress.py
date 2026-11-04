"""Build congress.json (U.S. Senate 1976-2020, U.S. House 1976-2022) from MIT Election Data and Science Lab files
and check it against independent references. Refuses to write if any check fails.

Usage: python3 build_congress.py <1976-2020-senate.csv> <house.csv>
  Senate: MIT Election Lab "U.S. Senate 1976-2020" (doi:10.7910/DVN/PEJ5QU), via github.com/coatless/raw-data
  House:  MIT Election Lab "U.S. House 1976-2022" (doi:10.7910/DVN/IG0UN2), via TidyTuesday 2023-11-07

Rules (each one logged in corrections.md):
  - "Winner" means most votes on election night. Later runoffs (e.g. Georgia, Louisiana) are noted, not applied.
  - A candidate's party is Democratic if any of their ballot lines is Democratic (incl. DFL/NPL), Republican likewise,
    otherwise Other (independents, third parties, write-ins).
  - House: one race per district. Prefer the regular general election; otherwise a special general (Texas 2006);
    otherwise a November special "primary" (Texas 1996 court-ordered open elections). D.C. and territories excluded.
  - A race with a single candidate (or no vote counts) is unopposed and decided at poll close.
"""
import csv, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATES = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())

# Fixes for blank or mislabeled party fields in the source (logged in corrections.md)
PARTY_FIX = {(2020, "WY", "CYNTHIA M. LUMMIS"): "REPUBLICAN"}

def side_of(parties):
    ps = [p.upper() for p in parties]
    if any(p.startswith("DEMOCRAT") and "SOCIALIST" not in p for p in ps): return 0
    if any("REPUBLICAN" in p for p in ps): return 1   # includes Minnesota's "Independent-Republican" label
    return 2

def title(n):
    n = n.strip().title()
    for a, b in (("Mcc", "McC"), ("Mcg", "McG"), ("Mcd", "McD"), ("Mck", "McK"), ("Mcm", "McM"), ("Mcc", "McC")):
        n = n.replace(a, b)
    return n

def race_from_rows(rows, party_key):
    by = collections.defaultdict(int); lines = collections.defaultdict(set); total = 0; wi = set()
    for r in rows:
        v = r["candidatevotes"]; v = int(v) if v not in ("NA", "") else 0
        v = max(v, 0)
        name = r["candidate"] if r["candidate"] not in ("NA", "") else "Write-ins"
        by[name] += v; lines[name].add(PARTY_FIX.get((int(r["year"]), r["state_po"], r["candidate"])) or r[party_key] or ""); total = max(total, int(r["totalvotes"]) if r["totalvotes"] not in ("NA", "") else 0)
        if r["writein"] == "TRUE": wi.add(name)
    real = [n for n in by if n != "Write-ins" and n.upper() != "OTHER" and n.upper() != "BLANK VOTE"]
    votes = [0, 0, 0]; names = [[], [], []]
    for n, v in by.items():
        s = side_of(lines[n]) if n in real else 2
        votes[s] += v
        if n in real: names[s].append((v, n))
    total = max(total, sum(votes))
    win = max(real, key=lambda n: by[n]) if real else None
    unopposed = len([n for n in real if n not in wi]) <= 1 or total == 0
    wside = side_of(lines[win]) if win else None
    return {"votes": votes, "total": total, "win": wside, "winner": title(win) if win else None,
            "unopposed": unopposed, "wvotes": by[win] if win else 0,
            "runner": sorted(((by[n], n) for n in real if n != win), reverse=True)[:1]}

def senate(path):
    rows = list(csv.DictReader(open(path, encoding="latin-1")))
    races = collections.defaultdict(list)
    for r in rows:
        if r["stage"] != "gen" or r["state_po"] not in STATES: continue
        races[(int(r["year"]), r["state_po"], r["special"] == "TRUE")].append(r)
    out = collections.defaultdict(list)
    for k in SENATE_DROP: races.pop(k, None)
    for (y, st, sp), rs in sorted(races.items()):
        x = race_from_rows(rs, "party_simplified")
        out[y].append({"st": st, "special": sp, **x})
    return out

def house(path):
    rows = list(csv.DictReader(open(path, encoding="latin-1")))
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r["state_po"] not in STATES or r["runoff"] == "TRUE": continue
        kind = ("gen" if r["special"] == "FALSE" else "genspecial") if r["stage"] == "GEN" else ("prispecial" if r["special"] == "TRUE" else None)
        if not kind: continue
        groups[(int(r["year"]), r["state_po"], r["district"])][kind].append(r)
    out = collections.defaultdict(lambda: collections.defaultdict(list)); used = collections.Counter()
    for (y, st, d), g in sorted(groups.items()):
        for kind in ("gen", "genspecial", "prispecial"):
            if g.get(kind):
                used[kind] += 1
                x = race_from_rows(g[kind], "party")
                out[y][st].append({"d": int(d) if d.isdigit() else 0, **x}); break
    return out, used

# ---------- independent references ----------
HOUSE_PUBLISHED = {  # seats won (D, R, other) as commonly published after each election
1976:(292,143,0),1978:(277,158,0),1980:(243,192,0),1982:(269,166,0),1984:(253,182,0),1986:(258,177,0),1988:(260,175,0),
1990:(267,167,1),1992:(258,176,1),1994:(204,230,1),1996:(207,227,1),1998:(211,223,1),2000:(212,221,2),2002:(204,229,1),
2004:(202,232,1),2006:(233,202,0),2008:(257,178,0),2010:(193,242,0),2012:(201,234,0),2014:(188,247,0),2016:(194,241,0),
2018:(235,199,0),2020:(222,213,0),2022:(213,222,0)}
SENATE_CLASS = {y: (33 if y % 6 in (0, 4) and y % 6 == (1976 % 6) else None) for y in range(1976, 2021, 2)}
CLASS_SIZE = {}
for y in range(1976, 2021, 2):
    CLASS_SIZE[y] = {1976 % 6: 33, 1978 % 6: 33, 1980 % 6: 34}[y % 6]
SENATE_SPOT = [  # (year, state, special, expected winner-side, surname) from widely reported results
(1976,"NY",False,0,"Moynihan"),(1976,"VA",False,2,"Byrd"),(1980,"IN",False,1,"Quayle"),(1980,"IA",False,1,"Grassley"),
(1992,"CA",False,0,"Boxer"),(1992,"CA",True,0,"Feinstein"),(1994,"TN",False,1,"Frist"),(1994,"PA",False,1,"Santorum"),
(2000,"NY",False,0,"Clinton"),(2000,"MO",False,0,"Carnahan"),(2000,"WA",False,0,"Cantwell"),(2002,"MN",False,1,"Coleman"),
(2006,"CT",False,2,"Lieberman"),(2006,"VT",False,2,"Sanders"),(2006,"VA",False,0,"Webb"),(2006,"MT",False,0,"Tester"),
(2008,"MN",False,0,"Franken"),(2008,"AK",False,0,"Begich"),(2008,"NC",False,0,"Hagan"),(2010,"AK",False,2,"Murkowski"),
(2010,"NV",False,0,"Reid"),(2010,"PA",False,1,"Toomey"),(2012,"ME",False,2,"King"),(2012,"MA",False,0,"Warren"),
(2012,"ND",False,0,"Heitkamp"),(2014,"NC",False,1,"Tillis"),(2020,"WY",False,1,"Lummis"),(2016,"NH",False,0,"Hassan"),
(2016,"WI",False,1,"Johnson"),(2016,"CA",False,0,"Harris"),(2018,"AZ",False,0,"Sinema"),(2018,"TX",False,1,"Cruz"),
(2018,"WV",False,0,"Manchin"),(2020,"AZ",True,0,"Kelly"),(2020,"GA",False,1,"Perdue"),(2020,"GA",True,0,"Warnock"),
(2020,"ME",False,1,"Collins"),(2020,"AL",False,1,"Tuberville")]
SENATE_DROP = {(2014, "LA", False): "Source file's Cassidy and Landrieu totals are corrupted (about 1.7M and 1.6M, versus about 0.6M each in the real November vote); race left out rather than guessed."}
SENATE_MISSING = {(1980, "ND"): "Not in the source file.", (1986, "NC"): "Filed only as the special election held the same day.", (2010, "IL"): "Filed only as the special election held the same day.", (2014, "LA"): "Left out (see SENATE_DROP)."}
RUNOFF_NOTES = {(2020,"GA",False):"No one passed 50%; Jon Ossoff (D) won the January runoff.",
                (2020,"GA",True):"No one passed 50%; Warnock (D) won the January runoff.",
                (2008,"GA",False):"Chambliss (R) fell short of 50% and won the December runoff.",
                (2002,"LA",False):"Landrieu (D) won the December runoff.",
                (2010,"AK",False):"Lisa Murkowski won as a write-in candidate after losing the Republican primary.",
                (2008,"MN",False):"Franken won by 312 votes after a months-long recount."}

def main(spath, hpath):
    errs = []
    sen = senate(spath)
    hou, used = house(hpath)
    # Senate checks
    for y in sorted(sen):
        reg = [r for r in sen[y] if not r["special"]]
        known_gap = sum(1 for (yy, st) in SENATE_MISSING if yy == y)
        if len(reg) + known_gap != CLASS_SIZE[y]: errs.append(f"Senate {y}: {len(reg)} regular races (+{known_gap} documented gaps), expected {CLASS_SIZE[y]}")
        for r in sen[y]:
            if r["winner"] is None: errs.append(f"Senate {y} {r['st']}: no winner")
    for y, st, sp, side, name in SENATE_SPOT:
        r = [x for x in sen[y] if x["st"] == st and x["special"] == sp]
        if not r or r[0]["win"] != side or name.lower() not in (r[0]["winner"] or "").lower():
            errs.append(f"Senate spot check {y} {st}{' special' if sp else ''}: expected {name}, got {r[0]['winner'] if r else None}")
    # House checks
    for y in sorted(hou):
        n = sum(len(v) for v in hou[y].values())
        seats = [0, 0, 0]
        for st in hou[y].values():
            for d in st: seats[d["win"]] += 1
        exp = HOUSE_PUBLISHED[y]
        bad = n != 435 or any(abs(a - b) > 2 for a, b in zip(seats, exp))
        print(f"House {y}: {n} districts, D {seats[0]} R {seats[1]} other {seats[2]}  | published D {exp[0]} R {exp[1]} other {exp[2]}  {'FAIL' if bad else 'OK'}")
        if bad: errs.append(f"House {y}: data D{seats[0]} R{seats[1]} O{seats[2]} ({n} districts) vs published {exp}")
    for y in sorted(sen):
        w = [0, 0, 0]
        for r in sen[y]: w[r["win"]] += 1
        print(f"Senate {y}: {len(sen[y])} races ({sum(r['special'] for r in sen[y])} special), most votes: D {w[0]} R {w[1]} other {w[2]}")
    print(f"Senate spot checks: {len(SENATE_SPOT)} known winners checked")
    print("House race sources used:", dict(used))
    if errs:
        print("\n".join("ERROR " + e for e in errs)); sys.exit(1)
    out = {"senate": [], "house": []}
    for y in sorted(sen):
        out["senate"].append({"year": y, "races": [[r["st"], int(r["special"]), r["votes"], r["total"], r["win"], r["winner"], int(r["unopposed"]),
                                                    RUNOFF_NOTES.get((y, r["st"], r["special"]), "")] for r in sen[y]]})
    for y in sorted(hou):
        out["house"].append({"year": y, "states": {st: [[d["d"], d["votes"], d["total"], d["win"], int(d["unopposed"])] for d in ds] for st, ds in sorted(hou[y].items())}})
    json.dump(out, open(os.path.join(HERE, "congress.json"), "w"), separators=(",", ":"))
    print("wrote congress.json")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
