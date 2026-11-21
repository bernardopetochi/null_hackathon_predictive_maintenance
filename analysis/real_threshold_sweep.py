# Collect p(healthy) traces on real freezers (fault-free 125-day stretches + leak windows) for threshold sweeps. Needs the biobank *_temp.parquet files (not redistributed).
import sys, json, importlib.util, numpy as np, pandas as pd
sys.argv=['x']
spec=importlib.util.spec_from_file_location('bt','/home/user/null_hackathon_predictive_maintenance/analysis/real_freezer_backtest.py');bt=importlib.util.module_from_spec(spec);spec.loader.exec_module(bt)
M=bt.M
F={'806278':[pd.Timestamp('2022-04-19')],'806274':[pd.Timestamp('2017-03-07')],'806019':[]}
fail70={'806278':pd.Timestamp('2022-04-16 22:00'),'806274':pd.Timestamp('2017-02-06 09:00')}
out={}
for fid,labels in F.items():
    H=bt.build_hourly(f'/mnt/project-files/{fid}_temp.parquet')
    segs=[]
    t0,t1=H.index.min(),H.index.max();s=t0
    while s+pd.Timedelta(days=125)<=t1:
        e=s+pd.Timedelta(days=125)
        if not any(s-pd.Timedelta(days=14)<=l<=e+pd.Timedelta(days=60) for l in labels):
            r=bt.run_model(H,s,e)
            if r: segs.append([p for _,p in r[1]])
        s=e
    leaks=[]
    for l in labels:
        # baseline from 90 d before label (clean for both leaks)
        r=bt.run_model(H,l-pd.Timedelta(days=90),l+pd.Timedelta(days=2))
        leaks.append({'t':[str(t) for t,_ in r[1]],'p':[p for _,p in r[1]]})
    out[fid]={'healthy':segs,'leaks':leaks}
    print(fid,len(segs),'segs',flush=True)
json.dump(out,open('/tmp/claude-0/-home-user/d632c975-15e5-5504-b7e7-e0c75a44076b/scratchpad/thr/traces.json','w'))
