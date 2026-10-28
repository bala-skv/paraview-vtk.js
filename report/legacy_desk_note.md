# Desk note: legacy ParaViewWeb applications

[DRAFT - student to review]

Facts only; opinions are `[STUDENT]`. Checked 2026-10-28. Items I could not confirm are marked UNVERIFIED.

## What each one was

| Name | What it was (source wording) | Source |
|---|---|---|
| ParaViewWeb JS library (`paraviewweb`) | "Web framework for building interactive visualization relying on VTK or ParaView to produce visualization data". Overview lists six areas: common data model, visualization components (1D histograms, parallel coordinates, mutual-information diagram), interaction (mouse/touch), data access (WebSocket helpers, Girder client), UI widgets (lookup-table and transfer-function editors), rendering viewers (image viewers, image compositing, WebGL geometry viewers on Three.js). BSD-3-Clause. | https://github.com/Kitware/paraviewweb (README read); https://kitware.github.io/paraviewweb/docs/ (Overview read) |
| Visualizer | "The ParaViewWeb Visualizer application ... Provide a Web based interface to ParaView similar to the ParaView Desktop Qt client." Kitware 2017 post: "the ParaView client for the web", reusing the source/filter property UI of the Qt client. npm `pvw-visualizer`. Launch: `pvpython -m paraview.apps.visualizer`. | https://github.com/Kitware/visualizer (README read); https://www.kitware.com/updates-and-a-new-addition-to-the-paraviewweb-family/ (dated 2017-11-07) |
| Lite (ParaView Lite) | "an open-source, javascript visualization application ... intended to serve a more refined and dedicated UI for controlling data processing and visualization remotely via a Web page." Launch: `pvpython -m paraview.apps.lite`. | https://github.com/Kitware/paraview-lite (README read); https://kitware.github.io/paraview-lite/ |
| Divvy | "exploring relationships between variables"; 2017 post: "the new kid in the ParaViewWeb family ... uses ParaView as its data processing and visualization backend to provide an analytical view of data." Launch: `pvpython -m paraview.apps.divvy` UNVERIFIED (the page said a pvpython command pointing to a data file; exact module name not shown). | https://kitware.github.io/divvy/; Kitware 2017 post above |
| LightViz | "Provide a tailored user interface for Scientific Visualization using ParaViewWeb as backend." README: "should not be used for production usage as it has been deprecated and is no longer supported." npm `light-viz`. | https://raw.githubusercontent.com/Kitware/light-viz/master/README.md (read); https://github.com/kitware/light-viz/ |

## When and why they were unbundled or deprecated

- **ParaViewWeb JS library.** README states: "This repository is now in maintenance mode which means we are not adding any new feature." It recommends trame for building interactive 3D web apps and names vtk.js as the library the stack now uses for local and remote rendering. The README gives no date. Source: https://github.com/Kitware/paraviewweb (read 2026-10-28).
- **Visualizer, Lite, Divvy (ParaView 5.13).** Primary source: ParaView Discourse, "Removal of web applications Visualizer, Lite, and Divvy from ParaView 5.13.0", topic 14575, posted 2024-05-07 by Cory Quammen (Kitware), https://discourse.paraview.org/t/removal-of-web-applications-visualizer-lite-and-divvy-from-paraview-5-13-0/14575 (body read via the Discourse JSON endpoint). The post is a proposal ("strongly considering removal ... from the ParaView application bundle"). Reasons stated: it "will streamline maintenance of the ParaView binary bundles"; users "would no longer be tied to any version of our Python web dependencies (i.e. wslink)"; the new `--venv` capability in 5.13 allows a virtual environment for web apps; "You will still be able to install Visualizer, Lite, and Divvy in your virtual environment and run them with ParaView"; the move "will free ParaView 5.13 to be used with both old and new web applications without any risk of library conflict." Two replies (Ben Boeckel, Sebastien Jourdain) discuss whether to ship a requirements file; Jourdain says no. The thread has 3 posts and I did not find a post announcing a final decision.
- **Release.** ParaView 5.13.0 announcement posted 2024-08-23: https://discourse.paraview.org/t/paraview-5-13-0-is-available-for-download/15292. Release notes: https://www.kitware.com/paraview-5-13-0-release-notes/ (read). It lists "Removed web applications divvy, lite, and visualizer": "divvy, lite and visualizer are not bundled with ParaView anymore", with links to the separate repos https://kitware.github.io/divvy/, https://kitware.github.io/paraview-lite/, https://kitware.github.io/visualizer/. The same notes add `--venv` to all ParaView executables (available in Programmable Source, Programmable Filter and the Python Shell). The notes do not mention trame or ParaViewWeb. The docs.paraview.org release-notes URL I tried returned 404.
- **LightViz.** Marked deprecated in its own README (above); no date or version given.
- **Installed 6.2.0 check.** `paraview/apps/` in `/home/bala/opt/ParaView-6.2.0-MPI-Linux-Python3.12-x86_64` contains `trame.py` (runs the app named by `--trame-app` or `TRAME_APP`), `glance.py` (stub returning `is_supported() == False`) and `packages.py`; no visualizer, lite or divvy modules. `paraview/web/` still ships `protocols.py` and `pv_wslink.py`. `paraview.envs` (uv-based venv manager) is present in 6.2.0.
- **Visualizer repo status.** https://github.com/Kitware/visualizer exists (BSD-3-Clause, 211 commits, empty Releases section); its README has no status or deprecation statement and no trame mention. Commit dates were not retrievable from the page I fetched. Earlier forum remark (Jourdain, 2023-04-16, https://discourse.paraview.org/t/way-forward-with-paraview-web/11900): ParaViewWeb docs are "legacy doc really good for reference but not really useful today for new comers"; he pointed to the paraview-visualizer Docker files as a reference.

## trame / vtk.js equivalent for each

Only equivalences stated by a source I read are given; the rest are Unknown.

| Legacy | Source-stated successor | Status |
|---|---|---|
| ParaViewWeb JS library | trame (named in its README); vtk.js for rendering | Stated in README |
| Visualizer | Still runnable from a venv with ParaView (Discourse 14575). A trame-based ParaView app is launched through `pvpython -m paraview.apps.trame` with a user-supplied app (`PV/.../paraview/apps/trame.py`); no source I read says it is a drop-in Visualizer replacement | UNVERIFIED as a replacement |
| Lite | Same venv statement as Visualizer | UNVERIFIED as a replacement |
| Divvy | Same venv statement | UNVERIFIED as a replacement |
| LightViz | README names none | Unknown |
| Glance (in-browser vtk.js viewer; not in your list) | `paraview/apps/glance.py` is a stub returning unsupported in 6.2.0 | Installed-source fact |

This project's Showcase B (trame + pvpython) and Showcase A (vtk.js) are the two modern paths we built; they do not replicate Visualizer's UI. [STUDENT: interpret]
