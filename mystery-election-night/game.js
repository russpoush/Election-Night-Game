const ELECTIONS=__DATA__;
const CONGRESS=__CONGRESS__;
(function(){
"use strict";
function hashStr(s){let h=1779033703^s.length;for(let i=0;i<s.length;i++){h=Math.imul(h^s.charCodeAt(i),3432918353);h=h<<13|h>>>19}return h>>>0}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
let rng=Math.random;
const R=(a,b)=>a+(b-a)*rng(), RI=(a,b)=>Math.floor(R(a,b+1));
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}

const NAMES={AL:"Alabama",AK:"Alaska",AZ:"Arizona",AR:"Arkansas",CA:"California",CO:"Colorado",CT:"Connecticut",DE:"Delaware",DC:"District of Columbia",FL:"Florida",GA:"Georgia",HI:"Hawaii",ID:"Idaho",IL:"Illinois",IN:"Indiana",IA:"Iowa",KS:"Kansas",KY:"Kentucky",LA:"Louisiana",ME:"Maine",MD:"Maryland",MA:"Massachusetts",MI:"Michigan",MN:"Minnesota",MS:"Mississippi",MO:"Missouri",MT:"Montana",NE:"Nebraska",NV:"Nevada",NH:"New Hampshire",NJ:"New Jersey",NM:"New Mexico",NY:"New York",NC:"North Carolina",ND:"North Dakota",OH:"Ohio",OK:"Oklahoma",OR:"Oregon",PA:"Pennsylvania",RI:"Rhode Island",SC:"South Carolina",SD:"South Dakota",TN:"Tennessee",TX:"Texas",UT:"Utah",VT:"Vermont",VA:"Virginia",WA:"Washington",WV:"West Virginia",WI:"Wisconsin",WY:"Wyoming"};
const GRID={AK:[0,0],ME:[10,0],VT:[9,1],NH:[10,1],WA:[0,2],ID:[1,2],MT:[2,2],ND:[3,2],MN:[4,2],IL:[5,2],WI:[6,2],MI:[7,2],NY:[8,2],RI:[9,2],MA:[10,2],OR:[0,3],NV:[1,3],WY:[2,3],SD:[3,3],IA:[4,3],IN:[5,3],OH:[6,3],PA:[7,3],NJ:[8,3],CT:[9,3],CA:[0,4],UT:[1,4],CO:[2,4],NE:[3,4],MO:[4,4],KY:[5,4],WV:[6,4],VA:[7,4],MD:[8,4],DE:[9,4],AZ:[1,5],NM:[2,5],KS:[3,5],AR:[4,5],TN:[5,5],NC:[6,5],SC:[7,5],DC:[8,5],OK:[3,6],LA:[4,6],MS:[5,6],AL:[6,6],GA:[7,6],HI:[0,7],TX:[3,7],FL:[8,7]};
const CLOSE={GA:0,IN:0,KY:0,SC:0,VT:0,VA:0,NC:30,OH:30,WV:30,AL:60,CT:60,DE:60,DC:60,FL:60,IL:60,ME:60,MD:60,MA:60,MS:60,MO:60,NH:60,NJ:60,OK:60,PA:60,RI:60,TN:60,AR:90,AZ:120,CO:120,KS:120,LA:120,MI:120,MN:120,NE:120,NM:120,NY:120,ND:120,SD:120,TX:120,WI:120,WY:120,IA:180,MT:180,NV:180,UT:180,CA:240,HI:240,ID:240,OR:240,WA:240,AK:360};
const COLORS=[{n:"Orange",c:"#ff8a3d",ink:"#1a0d02"},{n:"Purple",c:"#a57cff",ink:"#140a2b"},{n:"Teal",c:"#2ec4b6",ink:"#04201d"},{n:"Pink",c:"#ff6b9a",ink:"#2b0612"},{n:"Lime",c:"#a3d94a",ink:"#152203"}];
const START=-10, END=480, PER_SEC=2.5;
const KIND_LABEL={pres:"Presidential",senate:"Senate",house:"House"};
const PARTY3=[{name:"Democrats",short:"Democrats",party:"Democratic"},{name:"Republicans",short:"Republicans",party:"Republican"},{name:"Independents & others",short:"Independents",party:"Independent / third party"}];

// ---------- set up a night ----------
let E,units,col,maj,t,running=false,speed=1,last=0,ended=false,selected=null,presCall=null,rivalPresT=null,seenRival=new Set(),yearGuess=null,label="",kind="pres";
const NS=()=>E.cands.length;
const sideName=i=>i<0?"Even split":COLORS[col[i]].n, sideColor=i=>i<0?"#8b95a9":COLORS[col[i]].c, sideInk=i=>i<0?"#0b0f17":COLORS[col[i]].ink;
const sw=i=>`<i class="sw" style="background:${sideColor(i)}"></i>`;
const nameHTML=i=>`<b style="color:${sideColor(i)}">${sideName(i)}</b>`;

// One race (a state for president/Senate, a district for House): plan how its votes get counted tonight.
function simRace(s,close){
  s.close=close;
  if(s.leg){s.margin=100;s.rivalT=close;return s}
  const sh=s.votes.map(v=>s.total?v/s.total:0);
  const order=sh.map((v,i)=>i).sort((x,y)=>sh[y]-sh[x]);
  const A=order[0],B=order.length>1?order[1]:order[0];
  s.margin=100*(sh[A]-(order.length>1?sh[B]:0));
  const f=R(.55,.7);
  const kMax=Math.min(sh[A],sh[B])*(1-f)/f*.7;
  const k=(rng()<.5?1:-1)*Math.min(R(.01,.06),kMax);
  s.p1=sh.slice();s.p2=sh.slice();
  if(A!==B){s.p1[A]+=k;s.p1[B]-=k;s.p2[A]-=k*f/(1-f);s.p2[B]+=k*f/(1-f)}
  s.f=f;
  const span=(END-close)*R(.7,1.08),big=Math.log10(Math.max(s.total,1000))-5;
  s.t1=close+R(2,15);s.d1=clamp(span*R(.25,.4)*(.8+big*.3),20,span*.5);s.n1=RI(3,7);
  s.t2=s.t1+s.d1*R(.5,1.1);s.d2=Math.max(20,close+span-s.t2);s.n2=RI(3,6);
  s.rivalT=null;
  const am=s.margin;
  if(am>=15)s.rivalT=close+RI(0,3);
  else if(am>=.5){
    const thr=clamp(1-am*.07+R(-.03,.06),.25,.97);
    for(let m=close;m<=END;m++){const x=raceAt(s,m);if(x.r>=thr&&x.n>0&&leaderOf(x)===s.winner){s.rivalT=m;break}}
  }
  return s;
}
function prog(m,s0,d,n){const x=(m-s0)/d;if(x<=0)return 0;if(x>=1)return 1;return Math.ceil(x*n)/n}
function raceAt(s,m){
  if(s.leg)return {v:s.votes.map(()=>0),n:0,oth:0,r:m>=s.close?1:0};
  const a=prog(m,s.t1,s.d1,s.n1),b=prog(m,s.t2,s.d2,s.n2);
  const v=s.p1.map((p,i)=>s.total*(s.f*a*p+(1-s.f)*b*s.p2[i]));
  const n=s.total*(s.f*a+(1-s.f)*b);
  return {v,n,oth:Math.max(0,n-v.reduce((x,y)=>x+y,0)),r:s.total?n/s.total:1};
}
function at(u,m){
  if(!u.districts)return raceAt(u,m);
  const v=E.cands.map(()=>0),lead=E.cands.map(()=>0);let n=0,T=0,oth=0,done=0;
  u.districts.forEach(d=>{const x=raceAt(d,m);x.v.forEach((y,i)=>v[i]+=y);n+=x.n;oth+=x.oth;T+=d.total;
    if(d.leg?m>=d.close:x.n>0)lead[d.leg?d.winner:leaderOf(x)]++;if(x.r>=.9999)done++});
  return {v,n,oth,r:done===u.districts.length?1:(T?n/T:0),lead,done};
}
function leaderOf(x){let b=0;x.v.forEach((v,i)=>{if(v>x.v[b])b=i});return b}
function oneHot(i,n,k=1){const a=Array(n).fill(0);if(i>=0)a[i]=k;return a}

function setup(k,idx,seed){
  kind=k;rng=mulberry32(hashStr(seed));
  if(k==="pres")setupPres(idx);else if(k==="senate")setupSenate(idx);else setupHouse(idx);
  col=shuffle([0,1,2,3,4]).slice(0,NS());
  // rival network: when does a side become certain of the big prize?
  rivalPresT=null;
  const times=new Set();units.forEach(u=>{if(u.districts)u.districts.forEach(d=>{if(d.rivalT!==null)times.add(d.rivalT)});else if(u.rivalT!==null)times.add(u.rivalT)});
  for(const m of [...times].sort((a,b)=>a-b)){if(rivalSeats(m).some(v=>v>=maj)){rivalPresT=m;break}}
  t=START;ended=false;selected=null;presCall=null;seenRival=new Set();yearGuess=null;
}
function setupPres(idx){
  const P=ELECTIONS[idx];
  E={kind:"pres",year:P.year,cands:P.cands,winner:P.winner,size:P.size,note:P.note,years:ELECTIONS.map(e=>e.year)};
  maj=Math.floor(P.size/2)+1;
  units=P.states.map(([a,ev,vals,tot])=>{
    const leg=tot===null,votes=vals.map(v=>v[0]),evs=vals.map(v=>v[1]);
    const total=leg?0:Math.max(tot,votes.reduce((x,y)=>x+y,0));
    const order=votes.map((v,i)=>i).sort((x,y)=>votes[y]-votes[x]);
    return simRace({a,name:NAMES[a],ev,leg,votes,evs,total,call:null,winner:leg?evs.indexOf(Math.max(...evs)):order[0]},CLOSE[a]);
  });
}
function setupSenate(idx){
  const Y=CONGRESS.senate[idx];
  const has3=Y.races.some(r=>r[4]===2);
  const cands=PARTY3.slice(0,has3?3:2).map(c=>({...c,ev:0}));
  units=Y.races.map(([a,special,votes,total,win,winner,unopp,note])=>{
    const vv=has3?votes.slice():votes.slice(0,2);
    const w=win<cands.length?win:0;
    cands[w].ev++;
    return simRace({a,special:!!special,name:NAMES[a]+(special?" (special)":""),ev:1,leg:!!unopp&&!total,votes:vv,evs:oneHot(w,cands.length),total,call:null,winner:w,who:winner,note},CLOSE[a]);
  });
  units.forEach(u=>{if(u.leg)u.unopp=true});
  const wins=cands.map(c=>c.ev);
  E={kind:"senate",year:Y.year,cands,winner:wins.indexOf(Math.max(...wins)),size:units.length,years:CONGRESS.senate.map(y=>y.year),note:""};
  maj=Math.floor(units.length/2)+1;
}
function setupHouse(idx){
  const Y=CONGRESS.house[idx];
  let has3=false;Object.values(Y.states).forEach(ds=>ds.forEach(d=>{if(d[3]===2)has3=true}));
  const cands=PARTY3.slice(0,has3?3:2).map(c=>({...c,ev:0}));
  units=Object.entries(Y.states).map(([a,ds])=>{
    const districts=ds.map(([d,votes,total,win,unopp])=>{
      const vv=has3?votes.slice():votes.slice(0,2);
      cands[win].ev++;
      return simRace({d,votes:vv,total,winner:win,leg:!!unopp},CLOSE[a]);
    });
    const seats=cands.map((c,i)=>districts.filter(d=>d.winner===i).length);
    const top=Math.max(...seats),tops=seats.filter(s=>s===top).length;
    const u={a,name:NAMES[a],ev:districts.length,districts,evs:seats,winner:tops>1?-1:seats.indexOf(top),close:CLOSE[a],call:null};
    // rival calls the state once enough of its districts are called to settle the delegation majority
    u.rivalT=null;
    const times=[...new Set(districts.map(d=>d.rivalT).filter(x=>x!==null))].sort((x,y)=>x-y);
    for(const m of times){
      const called=cands.map(()=>0);let left=districts.length;
      districts.forEach(d=>{if(d.rivalT!==null&&d.rivalT<=m){called[d.winner]++;left--}});
      if(u.winner>=0){if(called.every((c,i)=>i===u.winner||called[u.winner]>c+left)){u.rivalT=m;break}}
      else if(left===0){u.rivalT=m;break}
    }
    return u;
  });
  const seats=cands.map(c=>c.ev);
  E={kind:"house",year:Y.year,cands,winner:seats.indexOf(Math.max(...seats)),size:435,years:CONGRESS.house.map(y=>y.year),note:""};
  maj=218;
}
function rivalSeats(m){
  const e=E.cands.map(()=>0);
  units.forEach(u=>{
    if(u.districts)u.districts.forEach(d=>{if(d.rivalT!==null&&m>=d.rivalT)e[d.winner]++});
    else if(u.rivalT!==null&&m>=u.rivalT)u.evs.forEach((v,i)=>e[i]+=v);
  });
  return e;
}
function myEV(){const e=E.cands.map(()=>0);units.forEach(u=>{if(u.leg&&t>=u.close)u.evs.forEach((v,i)=>e[i]+=v);else if(u.call&&u.call.party>=0&&!u.districts)e[u.call.party]+=u.ev});return e}
function nationalR(m){let n=0,T=0;units.forEach(u=>{const x=at(u,m);if(!u.leg){n+=x.n;T+=u.districts?u.districts.reduce((a,d)=>a+d.total,0):u.total}});return T?n/T:1}
const callable=u=>!u.leg;

// ---------- scoring ----------
function statePts(s){if(!s.call)return 0;if(s.call.party!==s.winner)return -50;return 20+Math.round(30*(1-s.call.r))+((s.rivalT===null||s.call.t<s.rivalT)?10:0)}
function presPts(){if(!presCall)return 0;if(presCall.party!==E.winner)return -600;return 300+Math.round(200*(1-presCall.r))+((rivalPresT===null||presCall.t<rivalPresT)?150:0)}
function stateFinal(s){return ended||at(s,t).r>=.9999}
function liveScore(){let x=units.filter(stateFinal).reduce((a,s)=>a+statePts(s),0);if(ended)x+=presPts()+(yearGuess===E.year?250:0);return x}
function maxScore(){return 60*units.filter(callable).length+900}
function rankFor(total){const p=total/maxScore();return total<0?"Retraction Machine":p<.1?"Intern":p<.25?"Junior Analyst":p<.4?"Senior Analyst":p<.55?"Decision Desk Chief":"Election Night Legend"}

// ---------- formatting ----------
function fmtTime(m){let mins=Math.round(m)+19*60;mins=((mins%1440)+1440)%1440;let h=Math.floor(mins/60),mm=mins%60;const ap=h>=12?"PM":"AM";h=h%12||12;return h+":"+String(mm).padStart(2,"0")+" "+ap}
function fmtV(n){if(n>=1e6)return(n/1e6).toFixed(2)+"M";if(n>=1e3)return Math.round(n/1e3)+"K";return String(Math.round(n))}
const $=id=>document.getElementById(id);
function setHTML(el,html){if(el.dataset.h!==html){el.dataset.h=html;el.innerHTML=html}}
const unitWord=()=>kind==="pres"?"state":kind==="senate"?"race":"state";

// ---------- map ----------
function buildMap(){
  const tileUnit={};units.forEach((u,i)=>{if(!(u.a in tileUnit)||(units[tileUnit[u.a]].special&&!u.special))tileUnit[u.a]=i});
  let h="";
  Object.keys(GRID).forEach(a=>{const [x,y]=GRID[a];if(!(a in tileUnit))h+=`<rect class="gone" x="${x*30+3}" y="${y*30+3}" width="24" height="24" rx="4"></rect><text class="gone" x="${x*30+15}" y="${y*30+15}">${a}</text>`});
  Object.entries(tileUnit).forEach(([a,i])=>{const [x,y]=GRID[a];h+=`<rect data-i="${i}" tabindex="0" aria-label="${units[i].name}" x="${x*30+1}" y="${y*30+1}" width="28" height="28" rx="4"></rect><text data-l="${i}" x="${x*30+15}" y="${y*30+15}">${a}</text>`});
  $("map").innerHTML=h;
  const extra=units.map((u,i)=>i).filter(i=>!Object.values(tileUnit).includes(i));
  $("specials").innerHTML=extra.length?`<span class="muted">Special elections:</span> `+extra.map(i=>`<button type="button" class="chip" data-unit="${i}">${units[i].a} special</button>`).join(""):"";
  const missing=Object.keys(GRID).length-Object.keys(tileUnit).length;
  $("notvoting").hidden=!missing;
  $("notvoting").textContent=kind==="pres"?"Faded = not a state yet, or didn't vote that year":"Faded = no race in that state this year";
}
function tileStyle(u){
  const x=at(u,t);
  let fill="#1f2737",op=1,stroke="#2c3649",w=1,dash="",ink="#6b7489";
  if(u.leg&&t>=u.close){fill=sideColor(u.winner);op=.85;stroke="#e9edf5";ink=sideInk(u.winner)}
  else if(u.call){fill=sideColor(u.call.party);stroke="#ffffff";w=2;ink=sideInk(u.call.party)}
  else if(t>=u.close&&(u.districts?x.lead.some(v=>v>0):x.n>0)){
    let L,m;
    if(u.districts){const l=x.lead;L=l.indexOf(Math.max(...l));m=(Math.max(...l)-l.slice().sort((a,b)=>b-a)[1]||0)/u.ev;if(l.filter(v=>v===l[L]).length>1)L=-1}
    else{L=leaderOf(x);const s=x.v.slice().sort((a,b)=>b-a);m=(s[0]-(s[1]||0))/x.n}
    fill=sideColor(L);op=.22+.5*clamp(m/.3,0,1);stroke=x.r<.999?"#e9edf5":"none";w=x.r<.999?1:0;dash=x.r<.999?"3 2":"";ink="#e9edf5";
  }
  else if(t>=u.close){stroke="#e9edf5";dash="3 2";ink="#e9edf5"}
  return {fill,op,stroke,w,dash,ink};
}
function renderMap(){
  $("map").querySelectorAll("rect[data-i]").forEach(rect=>{
    const i=+rect.dataset.i,u=units[i],txt=$("map").querySelector(`text[data-l="${i}"]`);
    const s=tileStyle(u);
    if(selected===i){s.stroke="#ffd23f";s.w=2.5;s.dash=""}
    rect.setAttribute("fill",s.fill);rect.setAttribute("fill-opacity",s.op);rect.setAttribute("stroke",s.stroke);rect.setAttribute("stroke-width",s.w);rect.setAttribute("stroke-dasharray",s.dash);
    txt.setAttribute("fill",s.ink);
  });
  document.querySelectorAll("[data-unit]").forEach(b=>{const u=units[+b.dataset.unit],s=tileStyle(u);b.style.borderColor=selected===+b.dataset.unit?"#ffd23f":s.stroke==="none"?s.fill:s.stroke;b.style.background=s.fill==="#1f2737"?"transparent":s.fill+"55"});
}

// ---------- panels ----------
function voteRows(x){
  const rows=E.cands.map((c,i)=>{const p=x.n?100*x.v[i]/x.n:0;return `<div class="vrow">${sw(i)}<span class="vn" style="color:${sideColor(i)}">${sideName(i)}</span><span class="vbar"><i style="width:${p}%;background:${sideColor(i)}"></i></span><span class="vp num">${x.n?p.toFixed(1)+"%":"–"}</span><span class="vv num">${fmtV(x.v[i])}</span></div>`}).join("");
  const oth=x.n?100*x.oth/x.n:0;
  return `<div class="vote">${rows}<div class="vrow muted"><i class="sw" style="background:#3a4357"></i><span class="vn">Others</span><span class="vbar"><i style="width:${oth}%;background:#3a4357"></i></span><span class="vp num">${x.n?oth.toFixed(1)+"%":"–"}</span><span class="vv num">${fmtV(x.oth)}</span></div></div>`;
}
function renderDetail(){
  const el=$("detail");
  if(selected===null){setHTML(el,`<div class="ptitle">Pick a ${unitWord()}</div><p class="empty" style="margin:4px 0 0">Tap any state on the map to watch its count and make a call. States light up as their polls close.</p>`);return}
  const s=units[selected],x=at(s,t),open=t<s.close,fin=stateFinal(s);
  const rivalCalled=s.rivalT!==null&&t>=s.rivalT;
  const pill=open?`<span class="pill">Polls open</span>`:s.leg?`<span class="pill done">Decided</span>`:fin?`<span class="pill done">Final</span>`:rivalCalled?`<span class="pill rival">Rival called it</span>`:`<span class="pill counting">Counting</span>`;
  const sub=kind==="pres"?`${s.ev} electoral vote${s.ev===1?"":"s"}`:kind==="senate"?"1 Senate seat":`${s.ev} House seat${s.ev===1?"":"s"}`;
  let html=`<div class="head"><div class="title">${s.name}<span>${sub} · Polls close ${fmtTime(s.close)} ET</span></div>${pill}</div>`;
  if(s.leg){
    html+=`<div class="facts">${open?`Results arrive at ${fmtTime(s.close)} ET.`:kind==="pres"?`No popular vote here: <b>the state legislature chose the electors.</b> Its electoral votes went to ${s.evs.map((v,i)=>v?`${nameHTML(i)} (${v})`:"").filter(Boolean).join(", ")}.`:`<b>Unopposed.</b> ${nameHTML(s.winner)} wins the seat.`}</div>`;
    setHTML(el,html);return;
  }
  if(s.districts){
    const lead=x.lead.map((v,i)=>v?`${nameHTML(i)} ${v}`:"").filter(Boolean).join(" · ")||"no results yet";
    html+=`<div class="facts">${open?`Votes start coming in after polls close at <b>${fmtTime(s.close)} ET</b>.`:`Seats led right now: ${lead} <span class="muted">(${x.done} of ${s.ev} districts fully counted)</span>`}</div>`;
    if(!open)html+=`<div class="dlist">${s.districts.map(d=>{const y=raceAt(d,t);if(d.leg)return `<div class="drow"><span class="dn">${d.d?"District "+d.d:"At-large"}</span><span>Unopposed: ${nameHTML(d.winner)}</span></div>`;if(!y.n)return `<div class="drow"><span class="dn">${d.d?"District "+d.d:"At-large"}</span><span class="muted">No votes yet</span></div>`;const L=leaderOf(y),srt=y.v.slice().sort((a,b)=>b-a),m=100*(srt[0]-(srt[1]||0))/y.n;return `<div class="drow"><span class="dn">${d.d?"District "+d.d:"At-large"}</span><span>${nameHTML(L)} +${m.toFixed(1)}</span><span class="muted num">${Math.round(y.r*100)}% in</span></div>`}).join("")}</div>`;
  }else{
    const srt=x.v.map((v,i)=>[v,i]).sort((a,b)=>b[0]-a[0]);
    const lead=x.n?`${sideName(srt[0][1])} +${(100*(srt[0][0]-(srt[1]?srt[1][0]:0))/x.n).toFixed(1)}`:"no votes yet";
    html+=voteRows(x)+`<div class="facts">${open?`Votes start coming in after polls close at <b>${fmtTime(s.close)} ET</b>.`:`<b class="num">${Math.round(x.r*100)}%</b> of expected vote in · Leader: <b>${lead}</b> · Votes left: <b class="num">~${fmtV(s.total-x.n)}</b>`}</div>`;
  }
  if(s.call||fin){
    let v="";
    if(s.call)v+=`You called it for ${nameHTML(s.call.party)} at ${fmtTime(s.call.t)} with ${Math.round(s.call.r*100)}% in.`;
    else v+=`You didn't call this ${unitWord()}.`;
    if(rivalCalled)v+=` Rival called it at ${fmtTime(s.rivalT)}.`;
    if(fin){
      if(s.districts)v+=`<br>Final: ${s.evs.map((e,i)=>e?`${nameHTML(i)} ${e}`:"").filter(Boolean).join(" · ")} seat${s.ev===1?"":"s"}${s.winner<0?" (an even split)":""}.`;
      else{v+=`<br>Final: ${nameHTML(s.winner)} wins the most votes, by ${s.margin.toFixed(2)} pts.`;
        if(kind==="pres"&&s.evs.filter(e=>e>0).length>1)v+=` Electoral votes split: ${s.evs.map((e,i)=>e?`${sideName(i)} ${e}`:"").filter(Boolean).join(", ")}.`}
      if(s.call){const p=statePts(s);v+=p<0?` <b class="r">Wrong call. ${p} pts.</b>`:` <b class="g">Correct! +${p} pts.</b>`}
      else if(!s.districts&&s.margin<.5)v+=` <b class="y">Razor thin. Smart to stay out.</b>`;
    }
    html+=`<div class="verdict">${v}</div>`;
  }else{
    const dis=open||ended?"disabled":"";
    const opts=E.cands.map((c,i)=>i);if(s.districts&&s.ev%2===0)opts.push(-1);
    html+=`<div class="calls">${opts.map(i=>`<button data-call="${i}" ${dis} type="button" style="border-color:${sideColor(i)};color:${sideColor(i)}">${i<0?"Call an even split":"Call "+sideName(i)}</button>`).join("")}</div>`;
    if(s.districts)html+=`<p class="psub">Call which color wins the most of ${s.name}'s ${s.ev} seat${s.ev===1?"":"s"}.</p>`;
  }
  setHTML(el,html);
}
function bigCallText(){
  if(kind==="pres")return {title:"Call the presidency",q:`Who becomes president? ${maj} electoral votes is a majority this year.`,btn:i=>`${sideName(i)} wins`};
  if(kind==="senate")return {title:"Call the night",q:`Which color wins the most of tonight's ${E.size} Senate races?`,btn:i=>`${sideName(i)} wins most`};
  return {title:"Call the House",q:"Which color wins a House majority (218 of 435 seats)?",btn:i=>`${sideName(i)} wins the House`};
}
function renderPres(){
  const el=$("pres"),B=bigCallText();
  const rivalDone=rivalPresT!==null&&t>=rivalPresT;
  let html=`<div class="ptitle">${B.title}</div>`;
  if(presCall){
    html+=`<div class="verdict">You called it for ${nameHTML(presCall.party)} at ${fmtTime(presCall.t)} with ${Math.round(presCall.r*100)}% of the vote in.${rivalDone?` Rival called it at ${fmtTime(rivalPresT)}.`:""}${ended?`<br>${presCall.party===E.winner?`<b class="g">Correct! +${presPts()} pts.</b>`:`<b class="r">Wrong. ${presPts()} pts.</b>`}`:"<br>You'll find out at the end of the night."}</div>`;
  }else{
    html+=`<p class="psub">${B.q} Worth up to 650 points if you're right and early; costs 600 if you're wrong.${rivalDone?` <b class="y">The rival network already called it at ${fmtTime(rivalPresT)}.</b>`:""}</p>
    <div class="calls big">${E.cands.map((c,i)=>`<button data-pres="${i}" ${t<0||ended?"disabled":""} type="button" style="border-color:${sideColor(i)};color:${sideColor(i)};background:${sideColor(i)}1f">${B.btn(i)}</button>`).join("")}</div>`;
  }
  if(ended&&!yearGuess)html+=`<button class="primary" id="backGuess" type="button" style="width:100%;margin-top:10px">Guess the year</button>`;
  setHTML(el,html);
}
function renderBar(){
  $("clock").textContent=fmtTime(t);
  $("tl").style.width=(100*(t-START)/(END-START))+"%";
  $("score").textContent=liveScore().toLocaleString();
  const rv=rivalSeats(t);
  const my=kind==="house"?rv:myEV();
  const goal=kind==="pres"?`${maj} to win`:kind==="senate"?`${E.size} races`:"218 to win";
  $("evrow").innerHTML=E.cands.map((c,i)=>`<span style="color:${sideColor(i)}">${sideName(i)} ${my[i]}</span>`).join("")+`<span class="mid">${goal}</span>`;
  // first color fills from the left, second from the right, any others follow the first; a majority marker for each end
  const w=my.map(v=>100*v/E.size);let left=w[0];
  $("evbar").innerHTML=`<i style="left:0;width:${w[0]}%;background:${sideColor(0)}"></i><i style="right:0;width:${w[1]}%;background:${sideColor(1)}"></i>`+
    E.cands.slice(2).map((c,j)=>{const i=j+2,h=`<i style="left:${left}%;width:${w[i]}%;background:${sideColor(i)}"></i>`;left+=w[i];return h}).join("")+
    `<b class="half" style="left:${100*maj/E.size}%"></b><b class="half" style="left:${100-100*maj/E.size}%"></b>`;
  $("rival").textContent=kind==="house"?`Seats called by the rival network · Your state calls: ${units.filter(u=>u.call).length}`:"Rival network: "+E.cands.map((c,i)=>`${sideName(i)} ${rv[i]}`).join(" · ");
  $("evlabel").textContent=kind==="pres"?"Your calls (electoral votes)":kind==="senate"?"Your calls (Senate races)":"House seats";
  const lv=$("live");lv.textContent=ended?"Final":running?"Live":"Paused";lv.classList.toggle("on",running);
  $("play").textContent=ended?"Done":running?"Pause":"Start";
  $("kindtag").textContent=KIND_LABEL[kind];
}
function renderAll(){renderMap();renderDetail();renderPres();renderBar()}
function chyron(h){$("chyron").innerHTML=h}

// ---------- loop ----------
function frame(ts){
  if(!running){last=0;return}
  if(last){
    const prev=t;t=Math.min(END,t+(ts-last)/1000*PER_SEC*speed);
    const closing=[...new Set(units.filter(s=>prev<s.close&&t>=s.close).map(s=>s.a))];
    if(closing.length)chyron(`<b>${fmtTime(units.find(s=>s.a===closing[0]).close)} ET</b> Polls closed: ${closing.join(", ")}`);
    units.forEach((s,i)=>{if(s.rivalT!==null&&t>=s.rivalT&&!seenRival.has(i)){seenRival.add(i);if(!closing.length&&!s.leg)chyron(`<b>RIVAL NETWORK</b> projects ${s.name} for ${sideName(s.winner)}${s.districts&&s.winner<0?"":""}.`)}});
    if(rivalPresT!==null&&prev<rivalPresT&&t>=rivalPresT)chyron(`<b>RIVAL NETWORK PROJECTS: ${sideName(E.winner).toUpperCase()} ${kind==="pres"?"WINS THE PRESIDENCY":kind==="senate"?"WINS THE MOST SENATE RACES":"WINS THE HOUSE"}</b>`);
    if(t>=END){endNight();return}
    renderAll();
  }
  last=ts;requestAnimationFrame(frame);
}
function setRunning(v){running=v;renderBar();if(v){last=0;requestAnimationFrame(frame)}}

// ---------- end of night ----------
function yearOptions(){
  rng=Math.random;
  const near=E.years.filter(y=>y!==E.year).sort((a,b)=>Math.abs(a-E.year)-Math.abs(b-E.year)).slice(0,8);
  return shuffle([E.year,...shuffle(near).slice(0,3)]).sort((a,b)=>a-b);
}
function endNight(){
  ended=true;running=false;t=END;renderAll();
  let twist="";
  if(kind==="pres"&&Math.max(...rivalSeats(END))<maj){twist=`<p class="y">Twist: no one reached ${maj} electoral votes. The House of Representatives decided this one.</p>`;chyron(`<b>NO ONE HAS A MAJORITY.</b> The House of Representatives will choose the president.`)}
  $("endSheet").innerHTML=`<h2>Polls are closed. Which ${KIND_LABEL[kind].toLowerCase()} election was this?</h2>${twist}
    <p class="muted">Guess right for 250 more points.</p>
    <div class="years">${yearOptions().map(y=>`<button type="button" data-year="${y}">${y}</button>`).join("")}</div>
    <button class="ghost" id="peek" type="button">Look at the map first</button>`;
  $("end").hidden=false;
  $("peek").onclick=()=>{$("end").hidden=true;$("pres").dataset.h="";renderPres()};
}
function revealBody(){
  if(kind==="pres"){
    const allV=units.reduce((a,s)=>a+s.total,0);
    const pv=E.cands.map((c,i)=>units.reduce((a,s)=>a+(s.leg?0:s.votes[i]),0));
    const hasLeg=units.some(s=>s.leg);
    const w=E.winner,W=E.cands[w],losers=E.cands.map((c,i)=>i).filter(i=>i!==w);
    return `<div class="who">${nameHTML(w)} was <b>${W.name}</b> (${W.party}), who won the presidency${losers.length?` over ${losers.map(i=>`<b>${E.cands[i].name}</b> (${E.cands[i].party}, playing ${sideName(i)})`).join(losers.length>2?", ":" and ")}`:""}.</div>
      <table class="num">${E.cands.map((c,i)=>`<tr><td>${sw(i)}${c.name}</td><td>${c.ev} EV · ${allV?(100*pv[i]/allV).toFixed(1):"–"}%</td></tr>`).join("")}</table>
      <p class="muted" style="font-size:12.5px">Electoral votes are the official count. Popular vote is the share of all votes cast${hasLeg?" in states that held a popular vote":""}.</p>
      <p style="font-size:14px">${E.note}</p>`;
  }
  const who=E.cands.map((c,i)=>`${nameHTML(i)} = ${c.name}`).join(" · ");
  if(kind==="senate"){
    const notes=units.filter(u=>u.note);
    return `<div class="who">${who}</div>
      <table class="num">${E.cands.map((c,i)=>`<tr><td>${sw(i)}${c.name}</td><td>${c.ev} race${c.ev===1?"":"s"} won</td></tr>`).join("")}</table>
      ${notes.length?`<p style="font-size:13.5px">${notes.map(u=>`<b>${u.name}:</b> ${u.note}`).join("<br>")}</p>`:""}
      <details><summary>All ${E.size} winners</summary><div class="wlist">${units.slice().sort((a,b)=>a.name.localeCompare(b.name)).map(u=>`<div>${sw(u.winner)}<b>${u.name}</b> · ${u.who}${u.unopp?" (unopposed)":""}</div>`).join("")}</div></details>
      <p class="muted" style="font-size:12.5px">"Winner" means most votes on election night. Runoffs held later are noted above.</p>`;
  }
  const yi=CONGRESS.house.findIndex(y=>y.year===E.year),prev=yi>0?CONGRESS.house[yi-1]:null;
  let change="";
  if(prev){const ps=[0,0,0];Object.values(prev.states).forEach(ds=>ds.forEach(d=>ps[d[3]]++));const d=E.cands[1].ev-ps[1];change=`<p style="font-size:14px">Compared with ${prev.year}, Republicans ${d>=0?"gained":"lost"} ${Math.abs(d)} seat${Math.abs(d)===1?"":"s"} and Democrats ${E.cands[0].ev-ps[0]>=0?"gained":"lost"} ${Math.abs(E.cands[0].ev-ps[0])}.</p>`}
  return `<div class="who">${who}. <b>${E.cands[E.winner].name}</b> won the House.</div>
    <table class="num">${E.cands.map((c,i)=>`<tr><td>${sw(i)}${c.name}</td><td>${c.ev} seat${c.ev===1?"":"s"}</td></tr>`).join("")}</table>${change}
    <p class="muted" style="font-size:12.5px">Seats counted by most votes on election night, from MIT Election Lab district results.</p>`;
}
function reveal(){
  const total=liveScore();
  const called=units.filter(s=>s.call),right=called.filter(s=>s.call.party===s.winner).length,wrong=called.length-right;
  const rank=rankFor(total),gotYear=yearGuess===E.year;
  const share=`Mystery Election Night (${KIND_LABEL[kind]}) · ${label}\n${total.toLocaleString()} pts · ${rank}\nYear: ${gotYear?"✅":"❌"} · Big call: ${!presCall?"⬜":presCall.party===E.winner?"✅":"❌"}\nCalls: ${right} right, ${wrong} wrong`;
  const statePtsSum=called.reduce((a,s)=>a+statePts(s),0);
  $("endSheet").innerHTML=`
    <div class="reveal">
      <div class="muted" style="font-size:13px">${gotYear?`<b class="g">You got it!</b>`:`<b class="r">You guessed ${yearGuess}.</b>`} It was</div>
      <div class="yr">${E.year}${kind!=="pres"?` <span class="kindyr">${KIND_LABEL[kind]}</span>`:""}</div>
      ${revealBody()}
    </div>
    <div><div class="big num">${total.toLocaleString()}</div><div class="rank">${rank}</div><div class="muted" style="font-size:12.5px">Top possible this night: ${maxScore().toLocaleString()}</div></div>
    <table>
      <tr><td>${kind==="senate"?"Race":"State"} calls<br><span class="muted">${right} right, ${wrong} wrong</span></td><td class="${statePtsSum<0?"r":"g"}">${statePtsSum}</td></tr>
      <tr><td>${bigCallText().title}<br><span class="muted">${presCall?`${sideName(presCall.party)} at ${fmtTime(presCall.t)} ET`:"No call"}</span></td><td class="${presPts()<0?"r":presPts()>0?"g":"muted"}">${presPts()}</td></tr>
      <tr><td>Year guess</td><td class="${gotYear?"g":"muted"}">${gotYear?250:0}</td></tr>
    </table>
    <div class="btns">
      <button class="primary" id="copy" type="button">Copy my score</button>
      <button class="ghost" id="again" type="button">Play another ${KIND_LABEL[kind].toLowerCase()} election</button>
      <button class="ghost" id="close" type="button">Look at the final map</button>
    </div>
    <p class="muted" id="copied" style="font-size:12.5px">${kind!=="pres"?"Results: MIT Election Data and Science Lab.":E.year>=1976?"Results: MIT Election Data and Science Lab via Noah Veltman (1976–2020); 2024 summed from county results compiled by Tony McGovern.":"Results: Wikipedia state-by-state tables (which cite Dave Leip's Atlas and CQ's Guide to U.S. Elections), checked against official electoral vote totals."} Vote counting order is simulated; final results are real.</p>`;
  $("copy").onclick=async()=>{try{await navigator.clipboard.writeText(share);$("copied").textContent="Copied. Send it to your partner."}catch(e){$("copied").textContent="Couldn't copy here. Your score: "+total}};
  $("again").onclick=()=>{$("end").hidden=true;startRandom(era)};
  $("close").onclick=()=>{$("end").hidden=true};
  try{const k="men-played-"+kind,pl=JSON.parse(localStorage.getItem(k)||"[]");if(!pl.includes(E.year)){pl.push(E.year);localStorage.setItem(k,JSON.stringify(pl))}}catch(e){}
  renderAll();
}

// ---------- start ----------
let era="all";
function start(k,idx,seed,lbl){label=lbl;setup(k,idx,seed);buildMap();renderAll();chyron("Polls close in 10 minutes.");window.scrollTo(0,0);setRunning(true)}
const today=new Date(),dkey=today.getFullYear()+"-"+(today.getMonth()+1)+"-"+today.getDate();
function startDaily(){era="all";start("pres",hashStr("men-"+dkey)%ELECTIONS.length,"daily-"+dkey,"Mystery of "+today.toLocaleDateString(undefined,{month:"short",day:"numeric"}))}
function startRandom(which){
  era=which||"all";
  const k=era==="senate"||era==="house"?era:"pres";
  const list=k==="pres"?ELECTIONS:CONGRESS[k];
  let pool=list.map((e,i)=>i).filter(i=>k!=="pres"||era==="all"||(era==="old"?list[i].year<1976:list[i].year>=1976));
  try{const pl=JSON.parse(localStorage.getItem("men-played-"+k)||(k==="pres"?localStorage.getItem("men-played"):null)||"[]");const un=pool.filter(i=>!pl.includes(list[i].year));if(un.length)pool=un}catch(e){}
  start(k,pool[Math.floor(Math.random()*pool.length)],"r-"+Date.now(),"Random mystery");
}

// ---------- events ----------
function pick(i){selected=i;renderMap();renderDetail()}
document.addEventListener("click",e=>{
  const r=e.target.closest("rect[data-i]");
  if(r){pick(+r.dataset.i);return}
  const ch=e.target.closest("[data-unit]");
  if(ch){pick(+ch.dataset.unit);return}
  const c=e.target.closest("[data-call]");
  if(c&&!c.disabled&&selected!==null){const s=units[selected];if(s.call||s.leg||t<s.close||ended)return;s.call={party:+c.dataset.call,t,r:at(s,t).r};chyron(`<b>YOUR DESK</b> projects ${s.name}: ${sideName(s.call.party)}.`);renderAll();return}
  const p=e.target.closest("[data-pres]");
  if(p&&!p.disabled&&!presCall&&!ended){presCall={party:+p.dataset.pres,t,r:nationalR(t)};chyron(`<b>YOUR DESK PROJECTS: ${bigCallText().btn(presCall.party).toUpperCase()}</b>`);renderAll();return}
  const y=e.target.closest("[data-year]");
  if(y){yearGuess=+y.dataset.year;reveal();return}
  if(e.target.id==="backGuess"){$("end").hidden=false}
});
document.addEventListener("keydown",e=>{const r=e.target.closest&&e.target.closest("rect[data-i]");if(r&&(e.key==="Enter"||e.key===" ")){e.preventDefault();pick(+r.dataset.i)}});
$("play").onclick=()=>{if(!ended)setRunning(!running)};
document.querySelectorAll("[data-speed]").forEach(b=>b.onclick=()=>{speed=+b.dataset.speed;document.querySelectorAll("[data-speed]").forEach(x=>x.classList.toggle("sel",x===b))});
$("startDaily").onclick=()=>{$("intro").hidden=true;startDaily()};
document.querySelectorAll("[data-era]").forEach(b=>b.onclick=()=>{$("intro").hidden=true;startRandom(b.dataset.era)});

// background behind the start screen: a neutral empty map (gives nothing away)
E={kind:"pres",year:0,cands:[{name:"",ev:0},{name:"",ev:0}],winner:0,size:538,years:[]};units=[];col=[0,1];maj=270;t=START;
buildMap();$("map").querySelectorAll("rect.gone").forEach(r=>r.classList.remove("gone"));$("notvoting").hidden=true;renderBar();renderDetail();renderPres();
})();
