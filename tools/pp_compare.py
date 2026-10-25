"""Vergleich der radialen Abschnittsauslastung von gridsim mit einem pandapower-Lastfluss (Spec 6, Task 11).

Nur zur Prüfung, nicht im Lauf; pandapower ist keine Paketabhängigkeit. Zwei Schritte:

1. ``export`` (Umgebung von gridsim, z. B. ``uv run python tools/pp_compare.py export ...``): je Station Netz
   (Elternabschnitt, R/X, Grenzstrom), Knotenflüsse eines Seeds in den 24 Stunden mit der höchsten
   Abschnittsauslastung und die Auslastung nach gridsim, je Station als ``<out>/<station>.npz``; dazu je Station eine
   Kartenskizze (SVG, Abschnitte nach höchster Auslastung des Seeds gefärbt) und ``sample.json`` (Abschnittstabelle).
2. ``compare`` (pandapower-Container, z. B. ``py.sh pp_compare.py compare ...``): rechnet je Stunde einen
   Lastfluss (Sammelschiene ideal 400 V, Trafo nicht modelliert) und vergleicht den Strom je Abschnitt mit gridsim.

Verglichen wird gridsim **ohne** Spitzenzuschlag (``segment_flow(..., surcharge=False)``): Der Zuschlag hängt am
Abschnitt, nicht an Knoten, und lässt sich in einem Lastfluss nicht abbilden. Gemessen wird also allein der Fehler
der radialen Summation (Verluste, Spannung ≠ 400 V, cos φ je Knoten statt je Abschnitt). Lasten: Bezug mit
cos φ 0,97 induktiv, Einspeisung mit cos φ 1 (wie gridsim).
"""
import argparse
import json
from pathlib import Path

import numpy as np

COS_LOAD = 0.97
TAN_LOAD = float(np.tan(np.arccos(COS_LOAD)))
MIN_LEN_KM = 1e-4          # Abschnitte der Länge 0 (Hausanschluss im Luftlinien-Baum): 0,1 m
REL_FLOOR_PCT = 10.0       # Abweichung nur für Abschnittsstunden mit mindestens 10 % Auslastung


# --- export (gridsim) -------------------------------------------------------------------------------------------

def attach_segment(parent, downstream):
    """Abschnitt, an dessen Ende jeder Knoten hängt: der tiefste Abschnitt, hinter dem der Knoten liegt."""
    m = len(parent)
    depth = np.zeros(m, int)
    for j in range(m):                       # topologisch sortiert: Eltern vor Kindern
        depth[j] = 0 if parent[j] < 0 else depth[parent[j]] + 1
    d = downstream.tocsc()
    out = np.empty(d.shape[1], int)
    for k in range(d.shape[1]):
        segs = d.indices[d.indptr[k]:d.indptr[k + 1]]
        out[k] = segs[np.argmax(depth[segs])]
    return out


def _svg(grid, pct_max, path, title):
    """Kartenskizze der Station: Abschnitte nach höchster Auslastung (grün < 80 %, gelb ≤ 100 %, rot > 100 %)."""
    pts = [np.asarray(g, float) for g in grid.geometry if g is not None and len(g) >= 2]
    if not pts:
        return
    allp = np.vstack(pts)
    (x0, y0), (x1, y1) = allp.min(0), allp.max(0)
    span = max(x1 - x0, y1 - y0, 1.0)
    size, pad = 600, 20
    sc = (size - 2 * pad) / span

    def xy(p):
        return f'{pad + (p[0] - x0) * sc:.1f},{size - pad - (p[1] - y0) * sc:.1f}'

    lines = []
    order = np.argsort(pct_max)
    for j in order:
        g = grid.geometry[j]
        if g is None or len(g) < 2:
            continue
        v = pct_max[j]
        col = '#1a9850' if v < 80 else '#fdae61' if v <= 100 else '#d73027'
        w = 1.0 if grid.service[j] else 2.5
        dash = ' stroke-dasharray="6 3"' if grid.overhead[j] else ''
        lines.append(f'<polyline points="{" ".join(xy(p) for p in g)}" fill="none" stroke="{col}" '
                     f'stroke-width="{w}"{dash}><title>Abschnitt {j}: {v:.0f} %</title></polyline>')
    root = np.asarray(grid.geometry[0][0], float) if len(grid.geometry) and len(grid.geometry[0]) else allp[0]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size + 40}" '
           f'viewBox="0 0 {size} {size + 40}" font-family="sans-serif" font-size="13">'
           f'<rect width="100%" height="100%" fill="#fff"/>{"".join(lines)}'
           f'<rect x="{float(xy(root).split(",")[0]) - 5}" y="{float(xy(root).split(",")[1]) - 5}" width="10" '
           f'height="10" fill="#000"/>'
           f'<text x="{pad}" y="{size + 15}">{title}</text>'
           f'<text x="{pad}" y="{size + 32}" fill="#555">grün &lt; 80 %, orange 80–100 %, rot &gt; 100 % · '
           f'gestrichelt = Freileitung · dünn = Hausanschluss · Maßstab {span:.0f} m</text></svg>')
    Path(path).write_text(svg, encoding='utf-8')


def export(prepared, year, scenario, charging, seed, stations, out, svg_dir=None):
    from gridsim import run as runmod
    from gridsim.data import load_prepared
    from gridsim.feeders.loading import loading_pct, segment_flow
    from gridsim.nodeflow import station_block

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    p = load_prepared(prepared, year)
    _, fe = runmod.feeders_state(prepared)
    params = runmod.RunParams(weather_year=year, scenario=scenario, charging=charging)
    f = runmod.flows(p, params, seed, feeders=fe)
    index = json.loads((Path(prepared) / 'feeders' / 'index.json').read_text())
    sample = {}
    for s in stations:
        grid, sized = fe[s]
        block = station_block(p, params, f, s)
        pos = np.searchsorted(block.nodes, grid.node_index)
        net = block.net()[:, pos]
        flow0 = segment_flow(grid, sized, block, surcharge=False)
        flow1 = segment_flow(grid, sized, block, surcharge=True)
        pct0, pct1 = loading_pct(flow0, sized), loading_pct(flow1, sized)
        hours = np.sort(np.argsort(-pct0.max(axis=1))[:24])
        np.savez_compressed(out / f'{s}.npz', parent=grid.parent, r_ohm=sized.r_ohm, x_ohm=sized.x_ohm,
                            i_max_a=sized.i_max_a, length_m=grid.length_m, service=grid.service,
                            node_seg=attach_segment(grid.parent, grid.downstream), hours=hours,
                            node_p_kw=net[hours].astype(np.float64), gs_flow_kw=flow0[hours].astype(np.float64),
                            gs_pct=pct0[hours].astype(np.float64), gs_pct_sur=pct1[hours].astype(np.float64))
        pmax = pct1.max(axis=0)
        rows = sorted(({'segment': j, 'feeder': int(grid.feeder[j]), 'type': sized.types[j],
                        'parallel': int(sized.parallel[j]), 'length_m': round(float(grid.length_m[j]), 1),
                        'service': bool(grid.service[j]), 'overhead': bool(grid.overhead[j]),
                        'n_nodes': int(grid.downstream[j].nnz), 'i_max_a': float(sized.i_max_a[j]),
                        'max_pct': round(float(pmax[j]), 1), 'hours_over': int((pct1[:, j] > 100).sum()),
                        'design_kw': round(float(fe_design(prepared, s)[j]), 1)}
                       for j in range(len(grid.parent))), key=lambda r: -r['max_pct'])
        km = {}
        for t, ln, par in zip(sized.types, grid.length_m, sized.parallel):
            km[t] = round(km.get(t, 0) + float(ln) * int(par) / 1000, 3)
        sample[s] = {'area': grid.area, 'n_nodes': int(len(grid.node_index)), 'n_feeders': int(len(grid.marked)),
                     'n_segments': int(len(grid.parent)), 'tail_feeders': int(np.sum(grid.tail)) if grid.tail is not None else 0,
                     'marked_feeders': int(np.sum(np.asarray(grid.marked) | np.asarray(sized.marked))),
                     'index': index.get(str(s)), 'km_per_type': km, 'segments': rows}
        if svg_dir:
            Path(svg_dir).mkdir(parents=True, exist_ok=True)
            _svg(grid, pmax, Path(svg_dir) / f'stichprobe-{grid.area}-{s}.svg',
                 f'Station {s} ({grid.area}), {scenario} {year}, Seed {seed}: höchste Auslastung je Abschnitt')
    (out / 'sample.json').write_text(json.dumps({'year': year, 'scenario': scenario, 'charging': charging,
                                                 'seed': seed, 'stations': sample}, ensure_ascii=False, indent=1))


_DESIGN = {}


def fe_design(prepared, s):
    """Auslegungsbezug je Abschnitt (kW) aus der Stationsdatei (``p_load_kw``)."""
    if s not in _DESIGN:
        z = np.load(Path(prepared) / 'feeders' / f'{s}.npz')
        _DESIGN[s] = z['p_load_kw'] if 'p_load_kw' in z.files else np.full(len(z['parent']), np.nan)
    return _DESIGN[s]


# --- compare (pandapower) ---------------------------------------------------------------------------------------

def build_net(z):
    import pandapower as pp
    net = pp.create_empty_network()
    m = len(z['parent'])
    bb = pp.create_bus(net, vn_kv=0.4, name='Sammelschiene')
    pp.create_ext_grid(net, bb, vm_pu=1.0)
    ends = [pp.create_bus(net, vn_kv=0.4) for _ in range(m)]
    lines = []
    for j in range(m):
        km = max(float(z['length_m'][j]) / 1000.0, MIN_LEN_KM)
        a = bb if z['parent'][j] < 0 else ends[z['parent'][j]]
        lines.append(pp.create_line_from_parameters(
            net, a, ends[j], length_km=km, r_ohm_per_km=max(float(z['r_ohm'][j]), 1e-6) / km,
            x_ohm_per_km=max(float(z['x_ohm'][j]), 1e-6) / km, c_nf_per_km=0.0, max_i_ka=float(z['i_max_a'][j]) / 1000))
    loads = [pp.create_load(net, ends[j], p_mw=0.0, q_mvar=0.0) for j in z['node_seg']]
    return net, lines, loads


def compare_station(z):
    """Auslastung pandapower vs. gridsim (ohne Zuschlag) je Stunde und Abschnitt: (pp_pct, gs_pct, vm_min, ok)."""
    import pandapower as pp
    net, lines, loads = build_net(z)
    p_kw = z['node_p_kw']
    pp_pct = np.full(z['gs_pct'].shape, np.nan)
    vm_min = np.full(len(z['hours']), np.nan)
    for h in range(len(z['hours'])):
        p = p_kw[h] / 1000.0
        net.load.loc[loads, 'p_mw'] = p
        net.load.loc[loads, 'q_mvar'] = np.where(p > 0, p * TAN_LOAD, 0.0)
        try:
            pp.runpp(net, algorithm='nr', max_iteration=50, init='flat')
        except pp.LoadflowNotConverged:
            continue
        pp_pct[h] = net.res_line.loc[lines, 'i_ka'].to_numpy() * 1000.0 / z['i_max_a'] * 100.0
        vm_min[h] = float(net.res_bus.vm_pu.min())
    return pp_pct, z['gs_pct'], vm_min


def stats(pp_pct, gs_pct):
    ok = np.isfinite(pp_pct)
    sel = ok & (np.maximum(pp_pct, gs_pct) >= REL_FLOOR_PCT)
    d = (pp_pct - gs_pct)[sel]
    rel = (pp_pct[sel] / np.maximum(gs_pct[sel], 1e-9) - 1.0) * 100.0
    over_pp, over_gs = (pp_pct > 100) & ok, (gs_pct > 100) & ok
    return {'n': int(sel.sum()), 'diff_pp_mean': float(d.mean()) if d.size else None,
            'diff_pp_abs_p95': float(np.percentile(np.abs(d), 95)) if d.size else None,
            'diff_pp_abs_max': float(np.abs(d).max()) if d.size else None,
            'rel_pct_median': float(np.median(rel)) if rel.size else None,
            'rel_pct_p95': float(np.percentile(rel, 95)) if rel.size else None,
            'over100_gs': int(over_gs.sum()), 'over100_pp': int(over_pp.sum()),
            'over100_disagree': int((over_gs ^ over_pp).sum())}


def compare(indir, out):
    indir = Path(indir)
    res, all_pp, all_gs = {}, [], []
    for f in sorted(indir.glob('*.npz'), key=lambda x: int(x.stem)):
        z = dict(np.load(f))
        pp_pct, gs_pct, vm = compare_station(z)
        st = stats(pp_pct, gs_pct)
        st.update({'hours': int(len(z['hours'])), 'not_converged': int(np.isnan(vm).sum()),
                   'vm_min_pu': float(np.nanmin(vm)) if np.isfinite(vm).any() else None,
                   'gs_max_pct': float(gs_pct.max()), 'pp_max_pct': float(np.nanmax(pp_pct)) if np.isfinite(pp_pct).any() else None,
                   'gs_sur_max_pct': float(z['gs_pct_sur'].max())})
        res[f.stem] = st
        all_pp.append(pp_pct.ravel())
        all_gs.append(gs_pct.ravel())
        print(f.stem, json.dumps(st), flush=True)
    total = stats(np.concatenate(all_pp), np.concatenate(all_gs)) if all_pp else None
    Path(out).write_text(json.dumps({'stations': res, 'total': total,
                                     'note': 'gridsim ohne Spitzenzuschlag; Sammelschiene 1,0 pu, Trafo nicht '
                                             'modelliert; Abweichung = pandapower − gridsim in Prozentpunkten, nur '
                                             f'Abschnittsstunden ab {REL_FLOOR_PCT:g} % Auslastung'},
                                    indent=1))
    print('total', json.dumps(total))


def main(argv=None):
    ap = argparse.ArgumentParser(prog='pp_compare')
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('export')
    e.add_argument('--prepared', required=True)
    e.add_argument('--year', type=int, default=2012)
    e.add_argument('--scenario', default='heute')
    e.add_argument('--charging', default='uncontrolled')
    e.add_argument('--seed', type=int, default=0, help='Seed-Index')
    e.add_argument('--stations', type=int, nargs='+', required=True)
    e.add_argument('--out', required=True)
    e.add_argument('--svg', help='Ordner für Kartenskizzen')
    c = sub.add_parser('compare')
    c.add_argument('--in', dest='indir', required=True)
    c.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    if a.cmd == 'export':
        export(a.prepared, a.year, a.scenario, a.charging, a.seed, a.stations, a.out, a.svg)
    else:
        compare(a.indir, a.out)


if __name__ == '__main__':
    main()
