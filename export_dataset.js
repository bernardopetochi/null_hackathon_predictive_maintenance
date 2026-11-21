// Usage: node analysis/export_dataset.js  -> data/ult_freezer_sim.csv.gz (+ data/README.md written by hand)
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');const zlib=require('zlib');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
  await p.goto('file://'+path.resolve(__dirname,'..','index.html'));await p.waitForFunction(()=>typeof fleetMachine==='function');
  const csv=await p.evaluate(()=>{const rows=['freezer_id,brand,hour,chamber_c,compressor_on_min,suction1_c,interstage_hx_c,evap_out_c,sump2_c,door_pulldown_min,fault_type,fault_active,fault_severity,hours_to_failure,failed'];
    for(const brand of ['revco','haier'])for(let i=0;i<150;i++){BRAND=brand;const m=fleetMachine(5000000+i+(brand==='haier'?100000:0));const id=`${brand}_${String(i).padStart(3,'0')}`;
      while(m.t<m.horizon&&!m.broken){const o=stepMachine(m);const s=severity(m);const act=m.fault&&m.t>=m.fault.onset;
        rows.push([id,brand,m.t,o.chamber.toFixed(2),o.ontime.toFixed(1),o.suction1.toFixed(2),o.ihx.toFixed(2),o.evap.toFixed(2),o.sump2.toFixed(2),o.door.toFixed(0),m.fault?m.fault.type:'none',act?1:0,s.toFixed(4),m.fault?failShot(m)-m.t:'',m.broken?1:0].join(','));}}
    BRAND='revco';return rows.join('\n');});
  fs.mkdirSync(path.join(__dirname,'..','data'),{recursive:true});
  fs.writeFileSync(path.join(__dirname,'..','data','ult_freezer_sim.csv.gz'),zlib.gzipSync(csv));
  console.log('rows',csv.split('\n').length-1);await b.close();})();
