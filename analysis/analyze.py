import numpy as np, json, sys
D='/tmp/hyd/'
prof=np.loadtxt(D+'profile.txt')
sens={}
for s in ['PS1','PS2','PS3','EPS1','FS1','FS2','TS1','TS2','TS3','TS4','VS1','CE','CP','SE']:
    a=np.loadtxt(D+s+'.txt'); sens[s+'_mean']=a.mean(1)
    if s in ('PS1','PS2','VS1','FS1','EPS1'): sens[s+'_std']=a.std(1)
    print(s,a.shape,file=sys.stderr)
names=list(sens); X=np.column_stack([sens[n] for n in names])
cool,valve,pump,acc,stable=prof.T
# design matrix one-hot (baseline = healthy level)
def oh(v,levels): return np.column_stack([(v==l).astype(float) for l in levels])
M=np.column_stack([np.ones(len(cool)),oh(cool,[20,3]),oh(valve,[90,80,73]),oh(pump,[1,2]),oh(acc,[115,100,90])])
cols=['int','cool20','cool3','valve90','valve80','valve73','pump1','pump2','acc115','acc100','acc90']
mask=stable==0
res={}
for j,n in enumerate(names):
    y=X[mask,j]; b,*_=np.linalg.lstsq(M[mask],y,rcond=None); r=y-M[mask]@b; sd=r.std()
    res[n]={'healthy':b[0],'resid_sd':sd,**{c:b[i]/sd for i,c in enumerate(cols) if i>0}}
print('cycles',len(cool),'stable',mask.sum())
print(f"{'sensor':12}{'healthy':>9}{'sd':>8}"+''.join(f"{c:>9}" for c in cols[1:]))
for n,v in res.items(): print(f"{n:12}{v['healthy']:9.2f}{v['resid_sd']:8.3f}"+''.join(f"{v[c]:9.1f}" for c in cols[1:]))
# temporal drift / cycle-to-cycle autocorrelation of residuals within constant-condition blocks
json.dump({'names':names,'res':res},open('effects.json','w'),indent=1,default=float)
np.save('X.npy',X); np.save('prof.npy',prof)
