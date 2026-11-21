#!/usr/bin/env python3
"""Backtest + calibration of the simulator-trained freezer model on REAL Danish National Biobank ULT freezer data
(Huang et al., Scientific Data 2023, doi:10.1038/s41597-023-02808-6).

Usage:
  python3 analysis/real_freezer_backtest.py --dir <folder with *_temp.parquet, *_events.parquet, fault_summary.xlsx>
  python3 analysis/real_freezer_backtest.py --temp 806830_temp.parquet [--events 806830_events.parquet] [--faults fault_summary.xlsx]

What it does, per freezer:
  1. Prints the raw columns so the sensor mapping can be checked (mapping guessed from Table 2 of the paper).
  2. Builds the same hourly signals the simulator produces (chamber, compressor on-time per cycle from the state bit,
     1st-stage suction, interstage HX, evaporator outlet, 2nd-stage sump; door pull-down is not rebuilt -> held flat).
  3. Calibration: healthy noise (hourly sd), lag-1 autocorrelation, and fault effect sizes in sigma units in the days
     before each labelled fault -> compare with what the simulator assumes.
  4. Backtest: runs the simulator-trained model (analysis/model.json, exported from index.html) with the same alarm rule,
     reports the first alarm relative to the service-request date (labels lag true onset), the named fault, and
     false-alarm rate on fault-free stretches. Also when a conventional -70 C chamber alarm would have fired.
Output: analysis/real_backtest_results.json + printed summary.
"""
import argparse, glob, json, math, os, re, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, 'model.json')))
SIGS = M['signals']  # ['chamber','ontime','suction1','ihx','evap','sump2','door']
# Simulator assumptions (sigma units at failure), for the calibration comparison
SIM_EFFECTS = {'leak1': {'suction1': 1.5, 'ihx': 2, 'ontime': 1.5, 'evap': .8}, 'comp1': {'ontime': 1.8, 'suction1': 1.2, 'ihx': 1.0},
               'comp2': {'sump2': 2, 'evap': 1.5, 'ontime': 1.8}, 'door': {'door': 2, 'ontime': 1.2}}
# Table 2 column indices in the paper -> our signals
IDX = {'chamber': 0, 'suction1': 1, 'ihx': 6, 'evap': 8, 'sump2': 11}
KEYWORDS = {'chamber': ['chamber', 'cabinet', 'rtd'], 'suction1': ['1st stage compressor suction', '1st_stage_suction', 'suction 1', 'first stage suction'],
            'ihx': ['interstage', 'heat exchanger', 'hx'], 'evap': ['evaporator outlet', 'evap_out', 'evaporator_outlet'],
            'sump2': ['sump']}


def find_time(df):
    if isinstance(df.index, pd.DatetimeIndex):
        return df.index
    for c in df.columns:
        if np.issubdtype(df[c].dtype, np.datetime64):
            return pd.DatetimeIndex(df[c])
    for c in df.columns:
        if re.search('date|time', str(c), re.I):
            return pd.DatetimeIndex(pd.to_datetime(df[c], errors='coerce'))
    raise SystemExit('No datetime column found; columns: %s' % list(df.columns))


EXACT = {'chamber': 'RTD', 'suction1': '1st Suc.', 'ihx': 'H.E.', 'evap': 'Evap. Out', 'sump2': '2nd Sump'}  # column names in the released Revco parquet files


def map_columns(df):
    if all(v in df.columns for v in EXACT.values()):
        return dict(EXACT), ('State' if 'State' in df.columns else None)
    cols = {str(c): c for c in df.columns}
    low = {k.lower(): v for k, v in cols.items()}
    out = {}
    for s, kws in KEYWORDS.items():
        hit = [v for k, v in low.items() if any(w in k for w in kws)]
        if s == 'suction1':
            hit = [v for k, v in low.items() if 'suction' in k and ('1' in k or 'first' in k)] or hit
        if hit:
            out[s] = hit[0]
        elif str(IDX[s]) in cols:
            out[s] = cols[str(IDX[s])]
    state = [v for k, v in low.items() if 'state' in k]
    return out, (state[0] if state else None)


def ontime_hourly(t, state):
    """Compressor on-time per cycle (min) from the Revco state bit 0 (1st-stage compressor), forward-filled per hour."""
    on = (pd.Series(state.values, index=t).fillna(0).astype(int) & 1).astype(int)
    d = on.diff().fillna(0)
    starts, ends = on.index[d == 1], on.index[d == -1]
    rows = []
    j = 0
    for s in starts:
        while j < len(ends) and ends[j] <= s:
            j += 1
        if j < len(ends):
            rows.append((ends[j], (ends[j] - s).total_seconds() / 60))
    if not rows:
        return None
    ser = pd.Series([r[1] for r in rows], index=pd.DatetimeIndex([r[0] for r in rows]))
    ser = ser[(ser > 1) & (ser < 600)]
    return ser.resample('1h').mean().ffill()


def build_hourly(path):
    df = pd.read_parquet(path)
    print(f'\n=== {os.path.basename(path)}: {len(df):,} rows; columns: {list(df.columns)[:30]}')
    t = find_time(df)
    mp, state = map_columns(df)
    print('  sensor mapping (check!):', {k: str(v) for k, v in mp.items()}, '| state column:', state)
    H = pd.DataFrame(index=t)
    for s, c in mp.items():
        H[s] = pd.to_numeric(df[c].values, errors='coerce')
    H = H[~H.index.isna()].sort_index().resample('1h').mean()
    if state is not None:
        ot = ontime_hourly(t, df[state])
        if ot is not None:
            H['ontime'] = ot.reindex(H.index).ffill()
    for s in SIGS:
        if s not in H:
            H[s] = np.nan
    print(f'  hourly span {H.index.min()} -> {H.index.max()} ({len(H):,} h); missing share per signal:',
          {s: round(float(H[s].isna().mean()), 2) for s in SIGS})
    return H[SIGS]


def mlp_forward(net, x):
    W1 = np.array(net['W1']).reshape(net['nin'], net['nh']); W2 = np.array(net['W2']).reshape(net['nh'], net['nout'])
    h = np.tanh(x @ W1 + np.array(net['b1']))
    return h @ W2 + np.array(net['b2'])


def sl(x):
    return np.sign(x) * np.log1p(np.abs(x))


def features(win, base):
    """Mirror of features() in index.html: per signal, deviation of last-WIN mean, WIN slope, WIN std ratio vs baseline."""
    f = []
    W = len(win)
    xs = np.arange(W)
    for s in SIGS:
        mu, sd = base[s]
        y = win[s].values
        if np.all(np.isnan(y)) or not np.isfinite(mu):
            f += [0.0, 0.0, 0.0]; continue
        y = pd.Series(y).interpolate(limit_direction='both').values
        m = y.mean(); sdw = y.std(ddof=1)
        slope = np.polyfit(xs, y, 1)[0]
        f += [sl((m - mu) / sd), sl(slope * W / sd), sl(sdw / sd - 1)]
    return np.array(f)


def run_model(H, start, end, base_hours=None):
    """Learn baseline on the first BASE_N hours after `start`, then run the alarm rule until `end`."""
    BN, WIN, CE, CONSEC, THR = M['BASE_N'], M['WIN'], M['CHECK_EVERY'], M['CONSEC'], M['THR']
    seg = H.loc[start:end]
    if len(seg) < BN + WIN + 10:
        return None
    b = seg.iloc[:BN]
    base = {s: (b[s].mean(), max(b[s].std(), 0.05 if s != 'ontime' else 0.5)) for s in SIGS}
    mu, sd = np.array(M['mu']), np.array(M['sd'])
    streak, votes, alarm, trace = 0, np.zeros(5), None, []
    for i in range(BN + WIN, len(seg), CE):
        f = features(seg.iloc[i - WIN:i], base)
        x = np.clip((f - mu) / sd, -5, 5)  # real data can sit far outside the simulated range; clip to avoid tanh extrapolation
        o = mlp_forward(M['cls'], x); p = np.exp(o - o.max()); p /= p.sum()
        rul = max(0.0, math.expm1(float(mlp_forward(M['rul'], x)[0])))
        trace.append((seg.index[i], float(p[0])))
        if p[0] < THR:
            streak += 1; votes[1:] += p[1:]
        else:
            streak = 0; votes[:] = 0
        if streak >= CONSEC and alarm is None:
            alarm = {'time': seg.index[i], 'fault': M['classes'][int(np.argmax(votes[1:]) + 1)], 'rul_h': rul}
    return alarm, trace, base


def load_faults(path, fid):
    if not path or not os.path.exists(path):
        return []
    xl = pd.read_excel(path, sheet_name=None)
    out = []
    for name, df in xl.items():
        print(f'  fault_summary sheet "{name}": columns {list(df.columns)}')
        idcol = next((c for c in df.columns if re.search('freezer|id|unit|serial', str(c), re.I)), df.columns[0])
        dcol = next((c for c in df.columns if re.search('date|time', str(c), re.I)), None)
        ccol = next((c for c in df.columns if re.search('categ|class|type|fault', str(c), re.I) and c != idcol), None)
        if dcol is None:
            continue
        rows = df[df[idcol].astype(str).str.contains(str(fid))]
        for _, r in rows.iterrows():
            out.append({'date': pd.to_datetime(r[dcol], errors='coerce'), 'category': str(r[ccol]) if ccol else '?'})
    return [o for o in out if pd.notna(o['date'])]


def calib(H, label):
    """Healthy noise/autocorrelation from days 60..20 before the label; fault effect = last 3 days vs that, in sigma."""
    h = H.loc[label - pd.Timedelta(days=60):label - pd.Timedelta(days=20)]
    pre = H.loc[label - pd.Timedelta(days=3):label]
    res = {}
    for s in SIGS:
        a = h[s].dropna()
        if len(a) < 48:
            continue
        sd = a.std(); ac = a.autocorr(1)
        eff = (pre[s].mean() - a.mean()) / sd if sd > 0 and pre[s].notna().any() else None
        res[s] = {'healthy_mean': round(float(a.mean()), 2), 'healthy_sd': round(float(sd), 3), 'lag1_autocorr': round(float(ac), 3),
                  'effect_sigma_last3d': None if eff is None else round(float(eff), 2)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir'); ap.add_argument('--temp', nargs='*', default=[]); ap.add_argument('--faults')
    a = ap.parse_args()
    temps = list(a.temp)
    faults = a.faults
    if a.dir:
        temps += sorted(glob.glob(os.path.join(a.dir, '**', '*temp*.parquet'), recursive=True))
        faults = faults or next(iter(glob.glob(os.path.join(a.dir, '**', 'fault_summary*.xlsx'), recursive=True)), None)
    if not temps:
        sys.exit('No *_temp.parquet files given')
    results = []
    for tp in temps:
        fid = re.findall(r'\d{5,}', os.path.basename(tp))
        fid = fid[0] if fid else os.path.basename(tp).split('_')[0]
        H = build_hourly(tp)
        labels = load_faults(faults, fid)
        print(f'  freezer {fid}: {len(labels)} labelled fault(s):', [(str(l["date"].date()), l["category"]) for l in labels])
        r = {'freezer': fid, 'faults': [], 'healthy_segments': []}
        for l in labels:
            d = l['date']
            out = run_model(H, d - pd.Timedelta(days=45), d + pd.Timedelta(days=2))
            conv = H.loc[d - pd.Timedelta(days=45):d + pd.Timedelta(days=2), 'chamber']
            conv_t = conv[conv > -70].index.min() if conv.notna().any() else None
            e = {'label_date': str(d), 'category': l['category'], 'calibration': calib(H, d)}
            if out:
                al = out[0]
                e['model_alarm'] = None if al is None else {'time': str(al['time']), 'days_before_label': round((d - al['time']).total_seconds() / 86400, 1),
                                                            'named_fault': al['fault'], 'predicted_hours_left': round(al['rul_h'])}
            e['chamber_-70C_alarm'] = None if conv_t is None or pd.isna(conv_t) else {'time': str(conv_t), 'days_before_label': round((d - conv_t).total_seconds() / 86400, 1)}
            print('  FAULT', e['label_date'], e['category'], '| model:', e.get('model_alarm'), '| -70C alarm:', e['chamber_-70C_alarm'])
            r['faults'].append(e)
        # fault-free stretches: 125-day segments not within 60 days before / 14 days after any label
        t0, t1 = H.index.min(), H.index.max()
        seg_start = t0
        while seg_start + pd.Timedelta(days=125) <= t1:
            seg_end = seg_start + pd.Timedelta(days=125)
            if not any(seg_start - pd.Timedelta(days=14) <= l['date'] <= seg_end + pd.Timedelta(days=60) for l in labels):
                out = run_model(H, seg_start, seg_end)
                if out:
                    r['healthy_segments'].append({'start': str(seg_start), 'false_alarm': out[0] is not None,
                                                  'alarm': None if out[0] is None else str(out[0]['time'])})
            seg_start = seg_end
        n = len(r['healthy_segments']); fa = sum(s['false_alarm'] for s in r['healthy_segments'])
        print(f'  fault-free 125-day stretches: {n}, with a (false) alarm: {fa}')
        results.append(r)
    json.dump(results, open(os.path.join(HERE, 'real_backtest_results.json'), 'w'), indent=1, default=str)
    print('\nSaved analysis/real_backtest_results.json. Compare effect_sigma_last3d with simulator assumptions:', SIM_EFFECTS)


if __name__ == '__main__':
    main()
