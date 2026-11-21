// Injected into index.html (after the model is trained). Evaluates the model and simple baselines on the same freezers.
function ruleStats(m){ // per-hour statistics used by the baseline rules
  const h=m.hist,n=h.ontime.length,bl=m.bl;
  let on=0;for(let j=n-24;j<n;j++)on+=h.ontime[j];on/=24;
  const zOn=(on-bl.ontime.mu)/bl.ontime.sd*Math.sqrt(24); // z of a 24-h mean
  let zMax=0;for(const {k} of SIG){let s=0;for(let j=n-WIN;j<n;j++)s+=h[k][j];s/=WIN;zMax=Math.max(zMax,Math.abs((s-bl[k].mu)/bl[k].sd));}
  return {zOn,zMax};
}
async function calibrateRules(){ // same operating point as the model: <=10% of 120 healthy validation freezers ever alarm
  const on=[],z=[];
  for(let i=0;i<120;i++){const m=brandify(newMachine(700000+i));let wOn=-1e9,wZ=-1e9;const qOn=[],qZ=[];
    while(m.t<3000){stepMachine(m);if(m.t%CHECK_EVERY||!m.bl||m.t<BASE_N+WIN)continue;const r=ruleStats(m);
      qOn.push(r.zOn);qZ.push(r.zMax);if(qOn.length>CONSEC){qOn.shift();qZ.shift();}
      if(qOn.length===CONSEC){wOn=Math.max(wOn,Math.min(...qOn));wZ=Math.max(wZ,Math.min(...qZ));}}
    on.push(wOn);z.push(wZ);await new Promise(r=>setTimeout(r,0));}
  on.sort((a,b)=>a-b);z.sort((a,b)=>a-b);
  return {kOn:on[Math.floor(on.length*0.9)],kZ:z[Math.floor(z.length*0.9)]};
}
async function robustEval({n=400,healthyOnly=false,seedBase=900000,rules}){
  const res=[];
  for(let i=0;i<n;i++){
    let m;if(healthyOnly){m=brandify(newMachine(seedBase+i));m.horizon=3000;}else m=fleetMachine(seedBase+i);
    const st={model:{s:0,t:null,cls:null,votes:new Float64Array(5)},on:{s:0,t:null},z:{s:0,t:null},conv:null};
    while(m.t<m.horizon&&!m.broken){const o=stepMachine(m);
      if(st.conv===null&&m.t>BASE_N&&o.chamber>CHAMBER_ALARM)st.conv=m.t;
      if(m.t%CHECK_EVERY)continue;const f=features(m);if(!f)continue;
      const pr=predict(f);const r=ruleStats(m);
      if(st.model.t===null){if(pr.p[0]<THR){st.model.s++;for(let k=1;k<5;k++)st.model.votes[k]+=pr.p[k];}else{st.model.s=0;st.model.votes.fill(0);}
        if(st.model.s>=CONSEC){st.model.t=m.t;let b=1;for(let k=2;k<5;k++)if(st.model.votes[k]>st.model.votes[b])b=k;st.model.cls=CLASSES[b];}}
      if(st.on.t===null){st.on.s=r.zOn>rules.kOn?st.on.s+1:0;if(st.on.s>=CONSEC)st.on.t=m.t;}
      if(st.z.t===null){st.z.s=r.zMax>rules.kZ?st.z.s+1:0;if(st.z.s>=CONSEC)st.z.t=m.t;}
    }
    const fs=m.fault?failShot(m):null,on=m.fault?m.fault.onset:Infinity;
    const lead=t=>t===null?null:(t<on?'early':Math.max(0,Math.min(fs,m.t)-t));
    res.push({type:m.fault?m.fault.type:'healthy',model:lead(st.model.t),modelCls:st.model.cls,on:lead(st.on.t),z:lead(st.z.t),conv:lead(st.conv),hours:m.t});
    if(i%20===0)await new Promise(r=>setTimeout(r,0));
  }
  return res;
}
