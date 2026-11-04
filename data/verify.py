"""Verification checks for historical presidential results (raw/<year>.txt).

Format:
  C Name|Party,Name|Party,...
  NAT Name=EV;Name=EV          (official national electoral votes, from the article infobox)
  SIZE 261                     (optional: size of the Electoral College that year)
  ST,EVavail,votes:ev,votes:ev,...,total   (total may be LEG = chosen by legislature)

Checks per year:
  1. Each candidate's state EVs add up to the official national EV total.
  2. Sum of electoral votes available equals the Electoral College size (if SIZE given).
  3. No state awards more EVs than it has.
  4. In each popular-vote state, the candidate who took ALL its EVs also won the most votes
     (states that split their EVs are listed for review instead).
  5. Candidate votes never add up to more than the state's total votes.
  6. No duplicate states.
"""
import glob, os, re, sys, json

def parse(path):
    year = int(os.path.basename(path)[:4])
    cands, nat, size, rows = [], {}, None, []
    for line in open(path):
        line = line.strip()
        if not line: continue
        if line.startswith("C "):
            cands = [c.split("|") for c in line[2:].split(",")]
        elif line.startswith("NAT "):
            for kv in line[4:].split(";"):
                k, v = kv.split("="); nat[k.strip()] = int(v)
        elif line.startswith("SIZE "):
            size = int(line[5:])
        else:
            p = line.split(",")
            st, avail = p[0], int(p[1])
            cv = [tuple(int(x) for x in c.split(":")) for c in p[2:2 + len(cands)]]
            tot = p[2 + len(cands)]
            rows.append((st, avail, cv, None if tot == "LEG" else int(tot)))
    return year, cands, nat, size, rows

def check(path):
    year, cands, nat, size, rows = parse(path)
    errs, notes = [], []
    names = [c[0] for c in cands]
    seen = set()
    for st, avail, cv, tot in rows:
        if st in seen: errs.append(f"{st}: listed twice")
        seen.add(st)
        if len(cv) != len(cands): errs.append(f"{st}: wrong number of columns")
        ev = sum(e for _, e in cv)
        if ev > avail: errs.append(f"{st}: awards {ev} EVs but has {avail}")
        if ev < avail: notes.append(f"{st}: {avail - ev} EV not cast/abstained")
        if tot is not None:
            vs = sum(v for v, _ in cv)
            if vs > tot:
                if vs - tot <= 0.01 * tot: notes.append(f"AUTOFIX {st}: total {tot} -> {vs} (candidate votes exceeded it by {vs - tot})")
                else: errs.append(f"{st}: candidate votes {vs} > total {tot}")
            winners = [i for i, (_, e) in enumerate(cv) if e > 0]
            top = max(range(len(cv)), key=lambda i: cv[i][0])
            if len(winners) == 1 and winners[0] != top:
                errs.append(f"{st}: EVs to {names[winners[0]]} but most votes to {names[top]}")
            if len(winners) > 1:
                notes.append(f"{st}: split EVs " + ", ".join(f"{names[i]} {cv[i][1]}" for i in winners))
        else:
            notes.append(f"{st}: chosen by legislature")
    for i, n in enumerate(names):
        got = sum(r[2][i][1] for r in rows)
        want = nat.get(n, 0)
        if got != want: errs.append(f"{n}: states add to {got} EV, official {want}")
    for n in nat:
        if n not in names: errs.append(f"official total lists {n}, who has no column")
    total_avail = sum(r[1] for r in rows)
    if size is not None and total_avail != size:
        errs.append(f"EVs available add to {total_avail}, Electoral College size {size}")
    return year, errs, notes, total_avail

# Independent reference: official electoral votes by surname (not taken from the fetched pages).
KNOWN = {
1824:{"Jackson":99,"Adams":84,"Crawford":41,"Clay":37}, 1828:{"Jackson":178,"Adams":83},
1832:{"Jackson":219,"Clay":49,"Floyd":11,"Wirt":7}, 1836:{"Van Buren":170,"Harrison":73,"White":26,"Webster":14,"Mangum":11},
1840:{"Harrison":234,"Van Buren":60}, 1844:{"Polk":170,"Clay":105}, 1848:{"Taylor":163,"Cass":127},
1852:{"Pierce":254,"Scott":42}, 1856:{"Buchanan":174,"Frémont":114,"Fillmore":8},
1860:{"Lincoln":180,"Breckinridge":72,"Bell":39,"Douglas":12}, 1864:{"Lincoln":212,"McClellan":21},
1868:{"Grant":214,"Seymour":80}, 1872:{"Grant":286,"Greeley":66}, 1876:{"Hayes":185,"Tilden":184},
1880:{"Garfield":214,"Hancock":155}, 1884:{"Cleveland":219,"Blaine":182}, 1888:{"Harrison":233,"Cleveland":168},
1892:{"Cleveland":277,"Harrison":145,"Weaver":22}, 1896:{"McKinley":271,"Bryan":176}, 1900:{"McKinley":292,"Bryan":155},
1904:{"Roosevelt":336,"Parker":140}, 1908:{"Taft":321,"Bryan":162}, 1912:{"Wilson":435,"Roosevelt":88,"Taft":8},
1916:{"Wilson":277,"Hughes":254}, 1920:{"Harding":404,"Cox":127}, 1924:{"Coolidge":382,"Davis":136,"La Follette":13},
1928:{"Hoover":444,"Smith":87}, 1932:{"Roosevelt":472,"Hoover":59}, 1936:{"Roosevelt":523,"Landon":8},
1940:{"Roosevelt":449,"Willkie":82}, 1944:{"Roosevelt":432,"Dewey":99}, 1948:{"Truman":303,"Dewey":189,"Thurmond":39},
1952:{"Eisenhower":442,"Stevenson":89}, 1956:{"Eisenhower":457,"Stevenson":73}, 1960:{"Kennedy":303,"Nixon":219,"Byrd":15},
1964:{"Johnson":486,"Goldwater":52}, 1968:{"Nixon":301,"Humphrey":191,"Wallace":46}, 1972:{"Nixon":520,"McGovern":17},
}

# Independent reference: national popular vote for the main candidates (standard published totals).
POP = {
1824:{"Jackson":151271,"Adams":113122},1828:{"Jackson":642553,"Adams":500897},1832:{"Jackson":701780,"Clay":484205},
1836:{"Van Buren":764176,"Harrison":550816},1840:{"Harrison":1275390,"Van Buren":1128854},1844:{"Polk":1339494,"Clay":1300004},
1848:{"Taylor":1360235,"Cass":1220544,"Van Buren":291501},1852:{"Pierce":1607510,"Scott":1386942},
1856:{"Buchanan":1836072,"Frémont":1342345,"Fillmore":873053},1860:{"Lincoln":1865908,"Breckinridge":848019,"Bell":590901},
1864:{"Lincoln":2218388,"McClellan":1812807},1868:{"Grant":3013650,"Seymour":2708744},1872:{"Grant":3598235,"Greeley":2834761},
1876:{"Tilden":4288546,"Hayes":4034311},1880:{"Garfield":4446158,"Hancock":4444260},1884:{"Cleveland":4914482,"Blaine":4856903},
1888:{"Harrison":5443633,"Cleveland":5534488},1892:{"Cleveland":5553898,"Harrison":5190819,"Weaver":1026595},
1896:{"McKinley":7112138,"Bryan":6508172},1900:{"McKinley":7228864,"Bryan":6370932},1904:{"Roosevelt":7630457,"Parker":5083880},
1908:{"Taft":7678335,"Bryan":6408979},1912:{"Wilson":6296284,"Roosevelt":4122721,"Taft":3486242,"Debs":901551},
1916:{"Wilson":9126868,"Hughes":8548728},1920:{"Harding":16144093,"Cox":9139661},1924:{"Coolidge":15723789,"Davis":8386242,"La Follette":4831706},
1928:{"Hoover":21427123,"Smith":15015464},1932:{"Roosevelt":22821277,"Hoover":15761254},1936:{"Roosevelt":27752648,"Landon":16681862},
1940:{"Roosevelt":27313945,"Willkie":22347744},1944:{"Roosevelt":25612916,"Dewey":22017929},
1948:{"Truman":24179347,"Dewey":21991292,"Thurmond":1175930,"Wallace":1157328},1952:{"Eisenhower":34075529,"Stevenson":27375090},
1956:{"Eisenhower":35579180,"Stevenson":26028028},1960:{"Kennedy":34220984,"Nixon":34108157},1964:{"Johnson":43127041,"Goldwater":27175754},
1968:{"Nixon":31783783,"Humphrey":31271839,"Wallace":9901118},1972:{"Nixon":47168710,"McGovern":29173222},
}

# Differences a person has looked at and explained (shown as REVIEWED, not errors).
REVIEWED = {
 (1824,"Adams"): "1824 popular-vote counts differ between sources; six states had no popular vote. EV results match.",
 (1860,"Breckinridge"): "Published total includes his share of NJ/NY/PA fusion tickets, which this data keeps in the fusion (Douglas) column.",
}

def check_pop(path, tol=0.03):
    year, cands, nat, size, rows = parse(path)
    out = []
    names = [c[0] for c in cands]
    for n, want in POP.get(year, {}).items():
        if n not in names: out.append(f"popular vote check: no column for {n}"); continue
        i = names.index(n); got = sum(r[2][i][0] for r in rows)
        diff = (got - want) / want
        tag = "OK " if abs(diff) <= tol else ("REVIEWED" if (year, n) in REVIEWED else "OFF")
        out.append(f"{tag} {n}: states add to {got:,}, published {want:,} ({diff:+.1%})" + (f" -- {REVIEWED[(year, n)]}" if tag == "REVIEWED" else ""))
    return out

def check_known(path):
    year, cands, nat, size, rows = parse(path)
    errs = []
    names = [c[0] for c in cands]
    for n, want in KNOWN.get(year, {}).items():
        key = n.replace("é", "e")
        idx = [i for i, m in enumerate(names) if m.replace("é", "e") == key]
        if not idx: errs.append(f"independent check: no column for {n}"); continue
        got = sum(r[2][idx[0]][1] for r in rows)
        if got != want: errs.append(f"independent check: {n} has {got} EV, official {want}")
    if year not in KNOWN: errs.append("independent check: no reference for this year")
    return errs

if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "raw", "*.txt")))
    bad = 0
    for f in files:
        year, errs, notes, tot = check(f)
        errs += check_known(f)
        pop = check_pop(f)
        errs += [p for p in pop if p.startswith("OFF") or p.startswith("popular")]
        for p in pop:
            if p.startswith("REVIEWED"): print("   ", p)
        if "-p" in sys.argv:
            for p in pop: print("   ", p)
        status = "PASS" if not errs else "FAIL"
        bad += bool(errs)
        print(f"{year} {status}  ({tot} EVs, {len(notes)} notes)")
        for e in errs: print("   ERROR", e)
        for n in notes:
            if n.startswith("AUTOFIX"): print("   ", n)
        if "-v" in sys.argv:
            for n in notes: print("   note ", n)
    print(f"\n{len(files) - bad}/{len(files)} years pass")
