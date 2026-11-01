---
title: Does imagery help?
style: style.css
---

# Does imagery add predictive value?

<p class="lede">Each bar is the percent reduction in out-of-sample error versus a strong baseline (log lagged counts of both outcomes, log population and income, and census covariates). Zero means no improvement; negative means the imagery made predictions worse. Two validation schemes are shown, and the shuffled-imagery placebo shows what noise looks like.</p>

```js
const G = await FileAttachment("data/gains.csv").csv({typed: true});
const R = await FileAttachment("data/radar.csv").csv({typed: true});
const featureName = {
  "+env": "Vegetation + temperature", "+light": "Night lights", "+embed": "Embeddings", "+all": "All optical, light, embeddings",
  "+radar": "Radar (VV, VH)", "+all optical, light, embed": "All optical, light, embeddings", "+all with radar": "All, with radar"
};
const variantName = (v) => v.startsWith("PLACEBO") ? "Placebo: imagery shuffled across tracts" : v.includes("negative binomial") ? "Negative binomial" : v.includes("top 1%") ? "Drop top 1% of tracts" : "Poisson (main)";
const rows = G.filter((d) => d.features !== "+all optical, light, embed").flatMap((d) => [
  {outcome: d.outcome, variant: variantName(d.variant), feature: featureName[d.features] ?? d.features, family: d.family, scheme: "Spatial cross-validation", gain: d.cv_gain_pct},
  {outcome: d.outcome, variant: variantName(d.variant), feature: featureName[d.features] ?? d.features, family: d.family, scheme: "Forward test 2024-25", gain: d.fwd_gain_pct}
]);
const outcomes = new Map([["Felony complaints", "felony_complaints"], ["Shooting incidents", "shootings"]]);
const variants = ["Poisson (main)", "Negative binomial", "Drop top 1% of tracts", "Placebo: imagery shuffled across tracts"];
const outcome = view(Inputs.radio(outcomes, {value: "felony_complaints", label: "Outcome"}));
const variant = view(Inputs.select(variants, {value: "Poisson (main)", label: "Model variant"}));
```

<div class="card">

```js
const sel = rows.filter((d) => d.outcome === outcome && d.variant === variant);
const featOrder = ["Vegetation + temperature", "Night lights", "Embeddings", "Radar (VV, VH)", "All optical, light, embeddings", "All, with radar"];
const present = featOrder.filter((f) => sel.some((d) => d.feature === f));
display(Plot.plot({
  width, height: 90 + present.length * 52, marginLeft: 215, marginRight: 150, marginBottom: 46, style: {fontSize: "13px"},
  x: {label: "Gain over baseline (% deviance reduction)", grid: true, nice: true},
  y: {label: null, domain: present},
  fy: {label: null, domain: ["Spatial cross-validation", "Forward test 2024-25"]},
  color: {domain: ["Spatial cross-validation", "Forward test 2024-25"], range: ["#2c7fb8", "#c51b8a"], legend: true},
  facet: {data: sel, y: "scheme"},
  marks: [
    Plot.ruleX([0], {stroke: "#888"}),
    Plot.barX(sel, {y: "feature", x: "gain", fill: "scheme", tip: true, title: (d) => `${d.feature}\n${d.scheme}\nGain: ${d.gain}%`}),
    Plot.text(sel, {y: "feature", x: "gain", text: (d) => `${d.gain > 0 ? "+" : ""}${d.gain.toFixed(1)}%`, textAnchor: (d) => d.gain >= 0 ? "start" : "end", dx: (d) => d.gain >= 0 ? 6 : -6, fontSize: 12, fill: "currentColor"})
  ]
}));
```

</div>

```js
display(outcome === "felony_complaints"
  ? html`<div class="callout"><b>Felony complaints:</b> no detectable gain. Every feature set stays within about two points of zero, and the placebo looks the same. An earlier ~5% gain came from a weak baseline.</div>`
  : html`<div class="callout"><b>Shootings:</b> vegetation and temperature features cut forward-test error by about 6%, but only about 1% in spatial cross-validation, and the forward test covers two years in which shootings fell sharply. A lead worth following, not a conclusion.</div>`);
```

## Radar sees construction, but not crime

<p class="lede">Sentinel-1 radar backscatter increases where new buildings are filed with the Department of Buildings. The sensor and pipeline work. They still add about one percent or less to crime prediction.</p>

```js
const radarRows = R.map((d) => ({test: d.test, view: d.view === "long_difference" ? "Long difference 2018 to 2025" : "Tract-year panel", estimate: d.estimate, p: d.p, n: d.n}));
display(html`<div class="card"><table class="t"><thead><tr><th>View</th><th>Test</th><th class="n">Estimate</th><th class="n">p</th><th class="n">n</th></tr></thead><tbody>
${radarRows.map((d) => html`<tr><td>${d.view}</td><td>${d.test}</td><td class="n">${d.estimate.toFixed(3)}</td><td class="n">${d.p == null || Number.isNaN(d.p) ? "" : d.p < 0.001 ? "<0.001" : d.p.toFixed(2)}</td><td class="n">${d.n}</td></tr>`)}
</tbody></table></div>`);
```

<p class="note">Filings are applications, not completed buildings, so counts are a noisy yardstick. This is a tract-level association, not recovery of individual construction sites.</p>
