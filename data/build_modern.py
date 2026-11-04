"""Build elections_modern.json (1976-2024).

Usage: python3 build_modern.py <veltman data.csv> <tonmcg 2024_US_County_Level_Presidential_Results.csv>
  - https://github.com/veltman/presidential-election-results (MIT Election Lab / House Clerk data, 1976-2020)
  - https://github.com/tonmcg/US_County_Level_Election_Results_08-24 (2024 county results, summed by state)
Checks every year's electoral votes against the official totals and stops on any mismatch.
"""
import csv,json,collections,sys,os
V=sys.argv[1]; T=sys.argv[2]
ST="AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()
EV={
1970:"9 3 6 6 45 7 8 3 3 17 12 4 4 26 13 8 7 9 10 4 10 14 21 10 7 12 4 5 3 4 17 4 41 13 3 25 8 6 27 4 8 4 10 26 4 3 12 9 6 11 3",
1980:"9 3 7 6 47 8 8 3 3 21 12 4 4 24 12 8 7 9 10 4 10 13 20 10 7 11 4 5 4 4 16 5 36 13 3 23 8 7 25 4 8 3 11 29 5 3 12 10 6 11 3",
1990:"9 3 8 6 54 8 8 3 3 25 13 4 4 22 12 7 6 8 9 4 10 12 18 10 7 11 3 5 4 4 15 5 33 14 3 21 8 7 23 4 8 3 11 32 5 3 13 11 5 11 3",
2000:"9 3 10 6 55 9 7 3 3 27 15 4 4 21 11 7 6 8 9 4 10 12 17 10 6 11 3 5 5 4 15 5 31 15 3 20 7 7 21 4 8 3 11 34 5 3 13 11 5 10 3",
2010:"9 3 11 6 55 9 7 3 3 29 16 4 4 20 11 6 6 8 8 4 10 11 16 10 6 10 3 5 6 4 14 5 29 15 3 18 7 7 20 4 9 3 11 38 6 3 13 12 5 10 3",
2020:"9 3 11 6 54 10 7 3 3 30 16 4 4 19 11 6 6 8 8 4 10 11 15 10 6 10 4 5 6 4 14 5 28 16 3 17 7 8 19 4 9 3 11 40 6 3 13 12 4 10 3"}
EV={k:dict(zip(ST,map(int,v.split()))) for k,v in EV.items()}
for k,v in EV.items(): assert len(v)==51 and sum(v.values())==538,(k,sum(v.values()))
def era(y): return 1970 if y<=1980 else 1980 if y<=1988 else 1990 if y<=2000 else 2000 if y<=2008 else 2010 if y<=2020 else 2020
# split electoral votes: (year,state): (demEV,gopEV)
SPLIT={(2008,'NE'):(1,4),(2020,'NE'):(1,4),(2024,'NE'):(1,4),(2016,'ME'):(3,1),(2020,'ME'):(3,1),(2024,'ME'):(3,1)}
CAND={1976:("Jimmy Carter","Gerald Ford","D",(297,240)),1980:("Jimmy Carter","Ronald Reagan","R",(49,489)),1984:("Walter Mondale","Ronald Reagan","R",(13,525)),
1988:("Michael Dukakis","George H. W. Bush","R",(111,426)),1992:("Bill Clinton","George H. W. Bush","D",(370,168)),1996:("Bill Clinton","Bob Dole","D",(379,159)),
2000:("Al Gore","George W. Bush","R",(266,271)),2004:("John Kerry","George W. Bush","R",(251,286)),2008:("Barack Obama","John McCain","D",(365,173)),
2012:("Barack Obama","Mitt Romney","D",(332,206)),2016:("Hillary Clinton","Donald Trump","R",(227,304)),2020:("Joe Biden","Donald Trump","D",(306,232)),2024:("Kamala Harris","Donald Trump","R",(226,312))}
# pledged (state-result) totals expected, accounting for faithless electors
PLEDGED={1976:(297,241),1988:(112,426),2000:(267,271),2004:(252,286),2016:(232,306)}
data=collections.defaultdict(dict)
for r in csv.DictReader(open(V)):
  data[int(r['year'])][r['state']]=[int(r['demVotes']),int(r['gopVotes']),int(r['totalVotes'])]
names={}
import re
abbr=dict(zip("Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware District_of_Columbia Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New_Hampshire New_Jersey New_Mexico New_York North_Carolina North_Dakota Ohio Oklahoma Oregon Pennsylvania Rhode_Island South_Carolina South_Dakota Tennessee Texas Utah Vermont Virginia Washington West_Virginia Wisconsin Wyoming".replace("_"," ").split(" ") if False else [],[]))
FULL=["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]
f2a=dict(zip(FULL,ST))
d24=collections.defaultdict(lambda:[0,0,0])
for r in csv.DictReader(open(T)):
  a=f2a[r['state_name']];d24[a][0]+=int(float(r['votes_dem']));d24[a][1]+=int(float(r['votes_gop']));d24[a][2]+=int(float(r['total_votes']))
data[2024]=dict(d24)
out=[]
for y in sorted(data):
  ev=EV[era(y)];D=G=0;rows=[]
  for s in ST:
    d,g,t=data[y][s]
    if (y,s) in SPLIT: de,ge=SPLIT[(y,s)]
    else: de,ge=(ev[s],0) if d>g else (0,ev[s])
    D+=de;G+=ge;rows.append([s,d,g,t,ev[s],de,ge])
  exp=PLEDGED.get(y,CAND[y][3])
  ok=(D,G)==exp
  print(y,D,G,"expected",exp,"OK" if ok else "MISMATCH")
  if not ok: sys.exit(1)
  td=sum(r[1] for r in rows);tg=sum(r[2] for r in rows);tt=sum(r[3] for r in rows)
  c=CAND[y]
  out.append({"year":y,"dem":c[0],"gop":c[1],"winner":c[2],"official":c[3],"pv":[round(100*td/tt,1),round(100*tg/tt,1)],"states":rows})
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'elections_modern.json'),'w'),separators=(',',':'))
print("written",len(out))
