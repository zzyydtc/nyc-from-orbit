---
title: Trends
style: style.css
---

# Reported crime by borough, 2018 to 2025

<p class="lede">Felony complaints and shooting incidents per 1,000 residents, summed over census tracts with at least 100 residents. Rates divide by 2023 population, so they track counts rather than demographic change.</p>

```js
const B = await FileAttachment("data/boroughs.csv").csv({typed: true});
const colors = {Manhattan: "#c51b8a", Bronx: "#7a0177", Brooklyn: "#2c7fb8", Queens: "#31a354", "Staten Island": "#e08214"};
const order = Object.keys(colors);
const metric = view(Inputs.radio(new Map([["Felony complaints", "felony_per_1000"], ["Shooting incidents", "shootings_per_1000"]]), {value: "felony_per_1000", label: "Outcome"}));
```

<div class="card">

```js
const lbl = metric === "felony_per_1000" ? "Felony complaints per 1,000 residents" : "Shooting incidents per 1,000 residents";
display(Plot.plot({
  width, height: 460, marginRight: 90, style: {fontSize: "13px"},
  x: {tickFormat: "d", label: null, ticks: 8},
  y: {label: lbl, grid: true, zero: true},
  color: {domain: order, range: order.map((k) => colors[k])},
  marks: [
    Plot.line(B, {x: "year", y: metric, stroke: "borough", strokeWidth: 2.4, curve: "monotone-x"}),
    Plot.dot(B, {x: "year", y: metric, fill: "borough", r: 3}),
    Plot.text(B.filter((d) => d.year === 2025), {x: "year", y: metric, text: "borough", fill: "borough", dx: 8, textAnchor: "start", fontWeight: 600}),
    Plot.tip(B, Plot.pointer({x: "year", y: metric, stroke: "borough", title: (d) => `${d.borough}, ${d.year}\n${lbl.split(" per")[0]}: ${d[metric]} per 1,000\nCount: ${(metric === "felony_per_1000" ? d.felony : d.shootings).toLocaleString()}`}))
  ]
}));
```

</div>

<div class="callout">Shootings fell sharply in 2025. That shift sits inside the forward test window (2024 and 2025), which is one reason the shooting result for satellite features is a lead, not a conclusion.</div>

<p class="note">Counts come from geocoded NYC Open Data records assigned to 2020 census tracts. 2025 shootings come from a separate dataset (see About). Reported crime reflects reporting and enforcement as well as offending.</p>
