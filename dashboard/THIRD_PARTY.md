# Third-party software in the dashboard

The built dashboard in `docs/dashboard/` bundles the following open-source software. Licenses are those declared by each package.

| Package | Version | License | Use |
|---|---|---|---|
| Observable Framework | 1.13.4 | ISC | Static site generator and runtime |
| Observable Plot | 0.6.17 | ISC | Charts |
| D3 | 7.9.0 | ISC | Dependency of Plot and Framework |
| MapLibre GL JS | 5.9.0 | BSD-3-Clause | Interactive map (vendored in `src/vendor/`, license in `src/vendor/maplibre-gl-LICENSE.txt`) |

Map tiles are loaded at view time from OpenStreetMap (c) OpenStreetMap contributors under the ODbL, subject to the OSM tile usage policy. Data notices are in the repository README.
