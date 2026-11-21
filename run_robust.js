// Usage: node analysis/run_robust.js  (needs playwright). Writes analysis/robustness_results.json
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const PAGE='file://'+path.resolve(__dirname,'..','index.html');
const SEEDS=+(process.env.SEEDS||5);
function summ(rows,key){
  const f=rows.filter(r=>r.type!=='healthy'),h=rows.filter(r=>r.type==='healthy');
  const caught=f.filter(r=>typeof r[key]==='number'),leads=caught.map(r=>r[key]).sort((a,b)=>a-b);
  const out={n_fault:f.length,caught:caught.length/f.length,caught_1d:f.filter(r=>typeof r[key]==='number'&&r[key]>=24).length/f.length,
    median_lead_h:leads.length?leads[Math.floor(leads.length/2)]:null,early_false:f.filter(r=>r[key]==='early').length/f.length,
    n_healthy:h.length,healthy_false_alarm:h.length?h.filter(r=>r[key]!==null).length/h.length:null};
  if(key==='model'){const c=caught.filter(r=>r.modelCls===r.type).length;out.fault_named=caught.length?c/caught.length:null;
    out.by_type={};for(const t of ['leak1','comp1','comp2','door']){const a=f.filter(r=>r.type===t);out.by_type[t]=a.filter(r=>typeof r.model==='number').length/a.length;}}
  return out;}
(async()=>{const b=await chromium.launch();const p=await b.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto(PAGE);await p.waitForFunction(()=>window.__EVAL,null,{timeout:300000});
  await p.addScriptTag({content:fs.readFileSync(path.join(__dirname,'robust_page.js'),'utf8')});
  const R={seeds:[],shift:{},healthy:{}};
  for(let s=0;s<SEEDS;s++){
    const rows=await p.evaluate(async s=>{SEED_OFF=s;BRAND='revco';await trainAll();const rules=await calibrateRules();
      return {rules,THR,rows:await robustEval({n:400,seedBase:900000,rules})};},s);
    const e={seed:s,thr:rows.THR,rules:rows.rules};for(const k of ['model','on','z','conv'])e[k]=summ(rows.rows,k);
    R.seeds.push(e);console.log('seed',s,JSON.stringify(e.model),'on',e.on.caught.toFixed(2),e.on.median_lead_h,'z',e.z.caught.toFixed(2),'conv',e.conv.median_lead_h);
    if(s===0){ // same model: big healthy set + cross-brand shift
      const hr=await p.evaluate(async r=>robustEval({n:1000,healthyOnly:true,seedBase:3000000,rules:r}),rows.rules);
      R.healthy={};for(const k of ['model','on','z','conv'])R.healthy[k]=summ(hr,k);
      console.log('healthy1000',JSON.stringify(R.healthy.model),'on',R.healthy.on.healthy_false_alarm,'z',R.healthy.z.healthy_false_alarm);
      const sh=await p.evaluate(async r=>{BRAND='haier';const x=await robustEval({n:400,seedBase:910000,rules:r});BRAND='revco';return x;},rows.rules);
      R.shift.revco_to_haier={};for(const k of ['model','on','z','conv'])R.shift.revco_to_haier[k]=summ(sh,k);
      console.log('shift',JSON.stringify(R.shift.revco_to_haier.model),'on',R.shift.revco_to_haier.on.caught,'z',R.shift.revco_to_haier.z.caught);}
  }
  // in-domain reference: train and test on Haier-like
  const hh=await p.evaluate(async()=>{SEED_OFF=0;BRAND='haier';await trainAll();const rules=await calibrateRules();const x=await robustEval({n:400,seedBase:910000,rules});BRAND='revco';return x;});
  R.shift.haier_to_haier={};for(const k of ['model','on','z','conv'])R.shift.haier_to_haier[k]=summ(hh,k);
  console.log('haier in-domain',JSON.stringify(R.shift.haier_to_haier.model));
  fs.writeFileSync(path.join(__dirname,'robustness_results.json'),JSON.stringify(R,null,1));await b.close();})();
