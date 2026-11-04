"""Check and build governor.json from data/governor/<year>.txt (even years 1976-2024).

Each line: ST|S-or-dash|winner surname|party|winner %|runner-up surname|party|runner-up %
Transcribed from Wikipedia's "<year> United States gubernatorial elections" summary tables.
Territories, odd-year races and recall elections (e.g. Wisconsin's June 2012 recall) are not included.

Checks (the build stops on any failure):
  1. Each year has the expected number of November state governor races.
  2. No state appears twice in a year, and every code is a real state.
  3. The winner's share is at least the runner-up's, and the two add up to no more than 100%.
  4. 137 well-known races, from an independent list, have the right winner and party.
"""
import json, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
STATES = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
EXPECTED = {1976:14,1978:36,1980:13,1982:36,1984:13,1986:36,1988:12,1990:36,1992:12,1994:36,1996:11,1998:36,2000:11,
            2002:36,2004:11,2006:36,2008:11,2010:37,2012:11,2014:36,2016:12,2018:36,2020:11,2022:36,2024:11}
# Independent reference: (year, state, winner surname, party letter D/R/O) for widely known races.
SPOT = """1976 NC Hunt D;1976 UT Matheson D;1976 WV Rockefeller D;1976 MO Teasdale D;1976 IL Thompson R
1978 AR Clinton D;1978 CA Brown D;1978 TX Clements R;1978 PA Thornburgh R;1978 NY Carey D;1978 MN Quie R
1980 AR White R;1980 MO Bond R;1980 WV Rockefeller D
1982 NY Cuomo D;1982 CA Deukmejian R;1982 AR Clinton D;1982 TX White D;1982 IL Thompson R;1982 MA Dukakis D;1982 NH Sununu R
1984 NC Martin R;1984 WA Gardner D;1984 MO Ashcroft R;1984 VT Kunin D
1986 AL Hunt R;1986 TX Clements R;1986 AZ Mecham R;1986 PA Casey D;1986 FL Martinez R;1986 MA Dukakis D;1986 NY Cuomo D
1988 IN Bayh D;1988 WV Caperton D;1988 NH Gregg R
1990 TX Richards D;1990 CA Wilson R;1990 AK Hickel O;1990 CT Weicker O;1990 MA Weld R;1990 MI Engler R;1990 FL Chiles D;1990 NY Cuomo D
1992 VT Dean D;1992 IN Bayh D;1992 MO Carnahan D;1992 NC Hunt D
1994 TX Bush R;1994 NY Pataki R;1994 ME King O;1994 FL Chiles D;1994 MD Glendening D;1994 CA Wilson R;1994 PA Ridge R;1994 TN Sundquist R
1996 NH Shaheen D;1996 WA Locke D;1996 IN O'Bannon D
1998 MN Ventura O;1998 FL Bush R;1998 CA Davis D;1998 TX Bush R;1998 AL Siegelman D;1998 GA Barnes D
2000 MO Holden D;2000 NC Easley D;2000 WV Wise D
2002 MA Romney R;2002 PA Rendell D;2002 MD Ehrlich R;2002 NY Pataki R;2002 AL Riley R;2002 MN Pawlenty R;2002 GA Perdue R;2002 IL Blagojevich D;2002 AZ Napolitano D
2004 WA Gregoire D;2004 IN Daniels R;2004 MT Schweitzer D;2004 MO Blunt R
2006 CA Schwarzenegger R;2006 AK Palin R;2006 NY Spitzer D;2006 MA Patrick D;2006 OH Strickland D;2006 FL Crist R;2006 MD O'Malley D
2008 NC Perdue D;2008 MO Nixon D;2008 DE Markell D
2010 OH Kasich R;2010 FL Scott R;2010 CA Brown D;2010 NY Cuomo D;2010 RI Chafee O;2010 WI Walker R;2010 ME LePage R
2012 IN Pence R;2012 NC McCrory R;2012 WA Inslee D;2012 NH Hassan D
2014 IL Rauner R;2014 MD Hogan R;2014 MA Baker R;2014 AK Walker O;2014 PA Wolf D;2014 TX Abbott R
2016 NC Cooper D;2016 MO Greitens R;2016 VT Scott R;2016 WV Justice D;2016 NH Sununu R
2018 GA Kemp R;2018 FL DeSantis R;2018 KS Kelly D;2018 WI Evers D;2018 MI Whitmer D;2018 NY Cuomo D;2018 OH DeWine R;2018 IL Pritzker D
2020 MT Gianforte R;2020 NC Cooper D;2020 WV Justice R;2020 UT Cox R
2022 AZ Hobbs D;2022 PA Shapiro D;2022 NY Hochul D;2022 NV Lombardo R;2022 MD Moore D;2022 MA Healey D;2022 GA Kemp R;2022 KS Kelly D
2024 NC Stein D;2024 NH Ayotte R;2024 IN Braun R;2024 WA Ferguson D;2024 WV Morrisey R"""
NOTES = {(2004, "WA"): "Gregoire won by 133 votes after two recounts.",
         (2010, "UT"): "Special election to finish Jon Huntsman's term.",
         (2016, "OR"): "Special election to finish John Kitzhaber's term.",
         (1990, "CT"): "Former Republican senator Lowell Weicker won on his own A Connecticut Party line.",
         (1998, "MN"): "Former pro wrestler Jesse Ventura won on the Reform Party line.",
         (2003, "CA"): ""}

def side(p):
    return 0 if p == "D" else 1 if p == "R" else 2

def parse(path):
    year = int(os.path.basename(path)[:4]); races = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line: continue
        st, sp, wn, wp, wpct, rn, rp, rpct = line.split("|")
        races.append({"st": st, "special": sp == "S", "wn": wn, "wp": wp, "w": float(wpct), "rn": rn, "rp": rp, "r": float(rpct)})
    return year, races

def main():
    errs = []; out = []; data = {}
    for f in sorted(glob.glob(os.path.join(HERE, "governor", "*.txt"))):
        y, races = parse(f); data[y] = races
        if len(races) != EXPECTED.get(y): errs.append(f"{y}: {len(races)} races, expected {EXPECTED.get(y)}")
        seen = set()
        for r in races:
            if r["st"] not in STATES: errs.append(f"{y}: {r['st']} is not a state")
            if r["st"] in seen: errs.append(f"{y}: {r['st']} listed twice")
            seen.add(r["st"])
            if r["w"] < r["r"]: errs.append(f"{y} {r['st']}: winner {r['w']}% below runner-up {r['r']}%")
            if r["w"] + r["r"] > 100.05: errs.append(f"{y} {r['st']}: shares add to {r['w'] + r['r']}%")
            if r["wp"] == r["rp"] and r["wp"] in "DR": errs.append(f"{y} {r['st']}: both top candidates are {r['wp']}")
    n = 0
    for item in SPOT.replace("\n", ";").split(";"):
        y, st, name, p = item.split(); y = int(y); n += 1
        r = [x for x in data.get(y, []) if x["st"] == st]
        if not r: errs.append(f"spot check {y} {st}: race missing"); continue
        r = r[0]; got = "D" if r["wp"] == "D" else "R" if r["wp"] == "R" else "O"
        if got != p or name.lower() != r["wn"].lower():
            errs.append(f"spot check {y} {st}: expected {name} ({p}), got {r['wn']} ({r['wp']})")
    for y in sorted(data):
        w = [0, 0, 0]
        for r in data[y]: w[side(r["wp"])] += 1
        print(f"{y}: {len(data[y])} races, won D {w[0]} R {w[1]} other {w[2]}")
    print(f"Spot checks: {n} known races")
    if errs:
        print("\n".join("ERROR " + e for e in errs)); sys.exit(1)
    for y in sorted(data):
        out.append({"year": y, "races": [[r["st"], int(r["special"]), r["wn"], side(r["wp"]), r["wp"], r["w"], r["rn"], side(r["rp"]), r["rp"], r["r"],
                                          NOTES.get((y, r["st"]), "")] for r in data[y]]})
    json.dump(out, open(os.path.join(HERE, "governor.json"), "w"), separators=(",", ":"), ensure_ascii=False)
    print("wrote governor.json")

if __name__ == "__main__":
    main()
