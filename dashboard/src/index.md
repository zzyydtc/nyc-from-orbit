---
title: NYC from orbit
style: style.css
---

# Can satellites help predict crime in New York City?

<p class="lede">A tract-level test, 2018 to 2025, of whether vegetation, heat, night lights, radar and learned image embeddings add anything to next year's felony complaints and shootings beyond last year's counts and census demographics. Explore the data below, then see the answer.</p>

<script src="./vendor/maplibre-gl.js"></script>
<link id="ml-worker" rel="preload" as="script" href="./vendor/maplibre-gl-csp-worker.js">

<div class="kpis">
  <div class="card kpi"><div class="big null">~0%</div><div class="label">Felony complaints: added predictive value from imagery, once the baseline is set properly</div></div>
  <div class="card kpi"><div class="big pos">~6%</div><div class="label">Shootings: possible gain in a two-year forward test, but only about 1% in spatial cross-validation</div></div>
  <div class="card kpi"><div class="big null">&le;1%</div><div class="label">Radar backscatter, even though it does detect new construction</div></div>
</div>

```js
while (!window.maplibregl) await new Promise((r) => setTimeout(r, 50));
const maplibregl = window.maplibregl;
maplibregl.setWorkerUrl(document.getElementById("ml-worker").href);
const tracts = await FileAttachment("data/tracts.geojson").json();
const V = await FileAttachment("data/values.json").json();
const years = V.years;
const ramps = {
  felony_rate: ["#fde0dd", "#fcc5c0", "#fa9fb5", "#f768a1", "#c51b8a", "#7a0177"],
  shoot_rate: ["#fde0dd", "#fcc5c0", "#fa9fb5", "#f768a1", "#c51b8a", "#7a0177"],
  ndvi_mean: ["#edf8e9", "#c7e9c0", "#a1d99b", "#74c476", "#31a354", "#006d2c"],
  lst_mean: ["#ffffb2", "#fed976", "#feb24c", "#fd8d3c", "#e31a1c", "#800026"],
  ntl: ["#ffffcc", "#c7e9b4", "#7fcdbb", "#41b6c4", "#2c7fb8", "#253494"],
  vv_db: ["#f7f7f7", "#d9d9d9", "#bdbdbd", "#969696", "#636363", "#252525"]
};
const NA = "#cfd3dc";
function bin(v, x) {
  if (x == null) return NA;
  const b = V.vars[v].breaks;
  let i = 0;
  while (i < b.length && x > b[i]) i++;
  return ramps[v][i];
}
```

```js
const layerInput = html`<select>${Object.entries(V.vars).map(([k, d]) => html`<option value=${k}>${d.label} (${d.unit})</option>`)}</select>`;
const layer = Generators.input(layerInput);
const yearInput = html`<input type="range" min="2018" max="2025" step="1" value="2025">`;
const year = Generators.input(yearInput);
const playBtn = html`<button class="playbtn" type="button">&#9654; Play</button>`;
let timer = null;
playBtn.onclick = () => {
  if (timer) { clearInterval(timer); timer = null; playBtn.innerHTML = "&#9654; Play"; return; }
  playBtn.innerHTML = "&#10074;&#10074; Pause";
  if (+yearInput.value >= 2025) yearInput.value = 2018;
  timer = setInterval(() => {
    const next = +yearInput.value + 1;
    if (next > 2025) { clearInterval(timer); timer = null; playBtn.innerHTML = "&#9654; Play"; return; }
    yearInput.value = next;
    yearInput.dispatchEvent(new Event("input", {bubbles: true}));
  }, 900);
};
invalidation.then(() => timer && clearInterval(timer));
display(html`<div class="controls">
  <label>Layer<br>${layerInput}</label>
  <label>Year<br>${yearInput}</label>
  ${playBtn}
</div>`);
```

```js
const selected = Mutable(null);
const setSelected = (s) => (selected.value = s);
```

<div class="grid grid-cols-4" style="grid-auto-rows: auto; gap: 14px;">
  <div class="card" style="grid-column: span 3; padding: 0; border: none; background: none; box-shadow: none;">
    <div class="mapwrap">
      <div id="map"></div>
      <div class="yearbadge" id="yearbadge"></div>
      <div class="legend" id="legend"></div>
    </div>
    <p class="note">Census tracts with at least 100 residents. Rates use 2023 population for every year. Hover a tract for its value; click it to see its history.</p>
  </div>
  <div class="card" id="detail">
    <h3>Selected tract</h3>
    <div id="detail-body" class="note">Click a tract on the map.</div>
  </div>
</div>

```js
const map = new maplibregl.Map({
  container: "map",
  style: {
    version: 8,
    sources: {osm: {type: "raster", tileSize: 256, maxzoom: 17, tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], attribution: "&copy; OpenStreetMap contributors"}},
    layers: [{id: "osm", type: "raster", source: "osm", paint: {"raster-saturation": -0.9, "raster-brightness-max": 0.92, "raster-opacity": 0.75}}]
  },
  center: [-73.97, 40.71], zoom: 10.2, minZoom: 8.5, maxZoom: 15, attributionControl: {compact: true}
});
map.addControl(new maplibregl.NavigationControl({showCompass: false}), "top-right");
await new Promise((r) => map.on("load", r));
map.addSource("tracts", {type: "geojson", data: tracts, promoteId: "i"});
map.addLayer({id: "fill", type: "fill", source: "tracts", paint: {"fill-color": ["coalesce", ["feature-state", "c"], NA], "fill-opacity": 0.82}});
map.addLayer({id: "line", type: "line", source: "tracts", paint: {"line-color": "#4b5363", "line-width": ["interpolate", ["linear"], ["zoom"], 9, 0.15, 13, 0.8], "line-opacity": 0.55}});
map.addLayer({id: "sel", type: "line", source: "tracts", paint: {"line-color": "#111", "line-width": 2.4}, filter: ["==", ["get", "i"], -1]});
invalidation.then(() => map.remove());
```

```js
// Recolor on layer or year change.
const yi = years.indexOf(year);
const vals = V.vars[layer].values;
for (let i = 0; i < vals.length; i++) map.setFeatureState({source: "tracts", id: i}, {c: bin(layer, vals[i][yi])});
document.getElementById("yearbadge").textContent = year;
const b = V.vars[layer].breaks, r = ramps[layer];
const lab = (k) => k === 0 ? `&le; ${b[0]}` : k === b.length ? `&gt; ${b[b.length - 1]}` : `${b[k - 1]} &ndash; ${b[k]}`;
document.getElementById("legend").innerHTML = `<b>${V.vars[layer].label}</b><br><span style="opacity:.75">${V.vars[layer].unit}</span><br>` +
  r.map((c, k) => `<i style="background:${c}"></i>${lab(k)}<br>`).join("") + `<i style="background:${NA}"></i>no data<br><span style="opacity:.7">Same scale for all years.</span>`;
```

```js
// Hover popup and click selection.
const popup = new maplibregl.Popup({closeButton: false, closeOnClick: false, offset: 8});
map.on("mousemove", "fill", (e) => {
  map.getCanvas().style.cursor = "pointer";
  const f = e.features[0];
  const v = V.vars[layer].values[f.properties.i][years.indexOf(year)];
  popup.setLngLat(e.lngLat).setHTML(`<b>${f.properties.borough}</b>, tract ${f.properties.geoid.slice(5)}<br>${V.vars[layer].label} (${year}): <b>${v == null ? "no data" : v}</b>`).addTo(map);
});
map.on("mouseleave", "fill", () => { map.getCanvas().style.cursor = ""; popup.remove(); });
map.on("click", "fill", (e) => setSelected({i: e.features[0].properties.i, geoid: e.features[0].properties.geoid, borough: e.features[0].properties.borough}));
```

```js
// Selected-tract panel.
const body = document.getElementById("detail-body");
map.setFilter("sel", ["==", ["get", "i"], selected ? selected.i : -1]);
if (!selected) {
  body.className = "note";
  body.textContent = "Click a tract on the map.";
} else {
  body.className = "";
  const rows = years.map((y, k) => ({year: y, felony: V.vars.felony_rate.values[selected.i][k], shoot: V.vars.shoot_rate.values[selected.i][k]}));
  const mk = (key, color, title) => Plot.plot({
    width: 250, height: 120, marginLeft: 34, marginBottom: 22, title,
    x: {tickFormat: "d", ticks: 4, label: null},
    y: {label: null, grid: true, nice: true},
    marks: [Plot.lineY(rows, {x: "year", y: key, stroke: color, strokeWidth: 2}), Plot.dot(rows, {x: "year", y: key, fill: color, r: 3}),
      Plot.ruleX(rows.filter((d) => d.year === year), {x: "year", stroke: "#888", strokeDasharray: "3,3"})]
  });
  body.replaceChildren(html`<div><b>${selected.borough}</b>, tract ${selected.geoid.slice(5)}</div>
    <div class="note" style="margin-bottom:6px">GEOID ${selected.geoid}</div>
    ${mk("felony", "#c51b8a", "Felony complaints per 1,000")}
    ${mk("shoot", "#7a0177", "Shootings per 1,000")}`);
}
```
