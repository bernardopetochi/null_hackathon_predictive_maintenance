// Usage: node analysis/export_model.js -> analysis/model.json (trained demo model, seed 0, Revco-like), for the Python real-data backtest
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
  await p.goto('file://'+path.resolve(__dirname,'..','index.html'));await p.waitForFunction(()=>window.__EVAL,null,{timeout:300000});
  const m=await p.evaluate(()=>{const A=a=>Array.from(a);const net=n=>({nin:n.nin,nh:n.nh,nout:n.nout,W1:A(n.W1),b1:A(n.b1),W2:A(n.W2),b2:A(n.b2)});
    return {signals:SIG.map(s=>s.k),classes:CLASSES,BASE_N,WIN,H,CHECK_EVERY,CONSEC,THR,mu:A(MODEL.mu),sd:A(MODEL.sd),cls:net(MODEL.cls),rul:net(MODEL.rul)};});
  fs.writeFileSync(path.join(__dirname,'model.json'),JSON.stringify(m));console.log('saved, THR',m.THR);await b.close();})();
