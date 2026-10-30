"""Build a self-contained static web map at docs/map/index.html.

Choropleth of tract-level outcomes and satellite features with a year slider. Data and geometry are embedded in the
page, so it opens from a file or any static host. Leaflet is loaded from a CDN. Needs data/processed/panel.csv.
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import mapping

OUT = Path("docs/map/index.html")
YEARS = list(range(2018, 2026))
VARS = {
    "felony_rate": ("Felony complaints per 1,000 residents", "RdPu"),
    "shoot_rate": ("Shooting incidents per 1,000 residents", "RdPu"),
    "ndvi_mean": ("Summer vegetation index (Sentinel-2 NDVI)", "Greens"),
    "lst_mean": ("Summer land surface temperature, deg C (Landsat)", "YlOrRd"),
    "ntl": ("Night lights, nW/cm2/sr (VIIRS)", "YlGnBu"),
    "vv_db": ("Summer radar backscatter VV, dB (Sentinel-1)", "Greys"),
}
RAMPS = {
    "RdPu": ["#fde0dd", "#fcc5c0", "#fa9fb5", "#f768a1", "#c51b8a", "#7a0177"],
    "Greens": ["#edf8e9", "#c7e9c0", "#a1d99b", "#74c476", "#31a354", "#006d2c"],
    "YlOrRd": ["#ffffb2", "#fed976", "#feb24c", "#fd8d3c", "#e31a1c", "#800026"],
    "YlGnBu": ["#ffffcc", "#c7e9b4", "#7fcdbb", "#41b6c4", "#2c7fb8", "#253494"],
    "Greys": ["#f7f7f7", "#d9d9d9", "#bdbdbd", "#969696", "#636363", "#252525"],
}


def main():
    panel = pd.read_csv("data/processed/panel.csv", dtype={"geoid": str})
    tracts = gpd.read_file("data/raw/tracts2020.geojson")[["geoid", "boroname", "geometry"]]
    pop = panel.drop_duplicates("geoid").set_index("geoid")["pop"]
    tracts = tracts[tracts.geoid.map(pop).fillna(0) >= 100].reset_index(drop=True)
    tracts["geometry"] = tracts.geometry.simplify(0.0002)
    p = panel[panel.year.isin(YEARS)].copy()
    p["pop"] = p.geoid.map(pop)
    p["felony_rate"] = 1000 * p.felony_complaints / p["pop"]
    p["shoot_rate"] = 1000 * p.shootings / p["pop"]

    data, breaks = {}, {}
    for v in VARS:
        w = p.pivot(index="geoid", columns="year", values=v).reindex(tracts.geoid)[YEARS]
        data[v] = [[None if not np.isfinite(x) else round(float(x), 3) for x in row] for row in w.values]
        vals = w.values[np.isfinite(w.values)]
        if (vals == 0).mean() > 0.3:  # sparse count rate: one class for zero, then quantiles of the positive values
            breaks[v] = [0.0] + [round(float(q), 3) for q in np.quantile(vals[vals > 0], [0.25, 0.5, 0.75, 0.92])]
        else:
            breaks[v] = [round(float(q), 3) for q in np.quantile(vals, [0.17, 0.33, 0.5, 0.67, 0.83])]
    feats = [{"type": "Feature", "properties": {"id": i, "geoid": g, "borough": b},
              "geometry": json.loads(json.dumps(mapping(geom), separators=(",", ":")))}
             for i, (g, b, geom) in enumerate(zip(tracts.geoid, tracts.boroname, tracts.geometry, strict=True))]

    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], list) else [round(x, 5) for x in c]
    for f in feats:
        f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    payload = {"features": feats, "data": data, "breaks": breaks, "years": YEARS,
               "vars": {k: v[0] for k, v in VARS.items()}, "ramps": {k: RAMPS[v[1]] for k, v in VARS.items()}}
    html = TEMPLATE.replace("/*PAYLOAD*/", json.dumps(payload, separators=(",", ":")))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB), {len(feats)} tracts")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NYC from orbit</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css">
<style>
html,body{height:100%;margin:0;font:14px/1.4 system-ui,sans-serif;color:#1b1b1b}
#map{position:absolute;inset:0}
.panel{position:absolute;z-index:1000;background:rgba(255,255,255,.95);border-radius:6px;box-shadow:0 1px 6px rgba(0,0,0,.3);padding:10px 12px}
#ctl{top:10px;right:10px;width:280px}
#ctl select,#ctl input{width:100%;margin:4px 0}
#legend{bottom:24px;left:10px}
#legend i{display:inline-block;width:18px;height:12px;margin-right:6px;vertical-align:middle}
#note{bottom:24px;right:10px;width:300px;font-size:11px;color:#444;max-height:40vh;overflow:auto}
h1{font-size:15px;margin:0 0 6px}
@media(max-width:700px){#ctl,#note{width:auto;left:10px}#note{display:none}}
</style></head><body>
<div id="map"></div>
<div id="ctl" class="panel"><h1>NYC from orbit</h1>
<label>Layer<select id="v"></select></label>
<label>Year: <b id="yl"></b><input id="y" type="range" step="1"></label></div>
<div id="legend" class="panel"></div>
<div id="note" class="panel">Census tracts with at least 100 residents. Rates use 2023 population for every year.
Reported crime reflects reporting and enforcement as well as offending; figures are descriptive, not causal.
Independent project, not affiliated with or endorsed by the NYPD or any other agency.
Data: NYC Open Data (NYPD, DCP; aggregated and modified, not endorsed by the City), ACS (uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau), Contains modified Copernicus Sentinel data 2018-2025, Landsat (USGS), VIIRS (NASA), AlphaEarth (Google and Google DeepMind). See the repository for sources.</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
<script>
const P=/*PAYLOAD*/;
const map=L.map('map',{preferCanvas:true}).setView([40.71,-73.97],11);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:17,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
const vs=document.getElementById('v'),ys=document.getElementById('y'),yl=document.getElementById('yl'),lg=document.getElementById('legend');
for(const k in P.vars){const o=document.createElement('option');o.value=k;o.textContent=P.vars[k];vs.appendChild(o);}
ys.min=0;ys.max=P.years.length-1;ys.value=P.years.length-1;
const NA='#d0d0d0';
function color(v,x){if(x==null)return NA;const b=P.breaks[v];let i=0;while(i<b.length&&x>b[i])i++;return P.ramps[v][i];}
const layer=L.geoJSON({type:'FeatureCollection',features:P.features},{
 style:f=>({weight:.4,color:'#666',fillOpacity:.8,fillColor:NA}),
 onEachFeature:(f,l)=>{l.on('mouseover',()=>{l.setStyle({weight:2,color:'#000'});});l.on('mouseout',()=>{layer.resetStyle(l);restyle(l);});
  l.bindTooltip(()=>{const v=vs.value,yi=+ys.value,x=P.data[v][f.properties.id][yi];return f.properties.borough+' tract '+f.properties.geoid.slice(5)+'<br>'+P.vars[v]+' ('+P.years[yi]+'): <b>'+(x==null?'no data':x)+'</b>';},{sticky:true});}}).addTo(map);
function restyle(l){const v=vs.value,yi=+ys.value;l.setStyle({fillColor:color(v,P.data[v][l.feature.properties.id][yi])});}
function update(){const v=vs.value,yi=+ys.value;yl.textContent=P.years[yi];layer.eachLayer(restyle);
 const b=P.breaks[v],r=P.ramps[v];let h='<b>'+P.vars[v]+'</b><br>';
 const lab=i=>i==0?'&le; '+b[0]:i==b.length?'&gt; '+b[b.length-1]:b[i-1]+' &ndash; '+b[i];
 for(let i=0;i<r.length;i++)h+='<i style="background:'+r[i]+'"></i>'+lab(i)+'<br>';
 lg.innerHTML=h+'<i style="background:'+NA+'"></i>no data<br><small>Same colour scale for all years.</small>';}
vs.onchange=update;ys.oninput=update;update();
</script></body></html>
"""

if __name__ == "__main__":
    main()
