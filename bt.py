import numpy as np
D='/tmp/hyd/'
prof=np.load('prof.npy'); X=np.load('X.npy')
ps1=np.loadtxt(D+'PS1.txt'); ps2=np.loadtxt(D+'PS2.txt')
seg=lambda a,n: a.reshape(a.shape[0],n,-1).mean(2)
F=np.column_stack([X, seg(ps1,12), seg(ps2,12)])
np.save('F.npy',F)
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
n=len(F); cut=int(n*0.7)  # temporal split: first 70% cycles train, last 30% test
for ci,name in [(0,'cooler'),(1,'valve'),(2,'pump'),(3,'accumulator')]:
    y=prof[:,ci]
    for feats,lab in [(X,'cycle means only'),(F,'means + pressure profile')]:
        m=make_pipeline(StandardScaler(),MLPClassifier((32,),max_iter=800,random_state=0)).fit(feats[:cut],y[:cut])
        acc=(m.predict(feats[cut:])==y[cut:]).mean()
        print(f"{name:12}{lab:28} acc={acc:.3f} classes={sorted(set(y))} test_classes={sorted(set(y[cut:]))}")
# random split for comparison
from sklearn.model_selection import cross_val_score
# autocorrelation of TS1 residual-ish (diff within constant condition)
r=X[:,list(range(X.shape[1]))]
