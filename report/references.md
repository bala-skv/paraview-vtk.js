# References

Each entry says how it was checked on 2026-10-26. Unverified items are marked.

1. Kitware, `paraviewweb` README. https://github.com/Kitware/paraviewweb. VERIFIED: "now in maintenance mode ... not adding any new feature", points to trame.
2. ParaView 5.13.0 release notes / announcement: https://discourse.paraview.org/t/paraview-5-13-0-is-available-for-download/15292 (VERIFIED to exist). Removal of Visualizer, Lite and Divvy: forum thread "Removal of web applications Visualizer, Lite, and Divvy from ParaView 5.13.0", ParaView Discourse, Web Support category, 2024-05-07, https://discourse.paraview.org/c/web-support/10. PARTLY VERIFIED: thread title and date seen in a category listing; thread body and exact URL not read. The 5.13.0 notes wording was not read.
3. ParaView 6.2.0 release notes (`paraview.envs`). NOT VERIFIED: the notes were not found by search. What was verified: the `paraview.envs` module page exists and describes a uv-based virtual-environment manager for pvpython, https://www.paraview.org/paraview-docs/nightly/python/paraview.envs.html. The design doc's claim that it is "new in 6.2" is unconfirmed.
4. vtk.js issue #3473, "[Feature] WebGPU-WebGL feature parity". https://github.com/Kitware/vtk-js/issues/3473. VERIFIED: open tracking issue listing WebGPU features still needed to match WebGL.
5. "VTK WebGPU Roadmap", VTK Discourse. https://discourse.vtk.org/t/vtk-webgpu-roadmap/13749. VERIFIED to exist (statuses in the table date from 2024 and may be outdated).
6. `trame-vtklocal` README (VTK.wasm local rendering). https://github.com/Kitware/trame-vtklocal and https://pypi.org/project/trame-vtklocal. VERIFIED to exist; version compatibility with VTK differs between releases, so re-read before extra E4.
7. S. Jourdain, U. Ayachit, B. Geveci, "ParaViewWeb, a Web Framework for 3D Visualization and Data Processing", IADIS International Conference on Web Virtual Reality and Three-Dimensional Worlds, 2010, pp. 502-506. https://www.iadisportal.org/digital-library/paraviewweb-a-web-framework-for-3d-visualization-and-data-processing. VERIFIED (IADIS portal listing).
8. W. Usher, V. Pascucci, "Interactive Visualization of Terascale Data in the Browser: Fact or Fiction?", IEEE LDAV 2020, pp. 27-36. https://arxiv.org/abs/2009.03254 (PDF: https://arxiv.org/pdf/2009.03254). VERIFIED.
9. S. Shi, C.-H. Hsu, "A Survey of Interactive Remote Rendering Systems", ACM Computing Surveys 47(4), article 57, 2015. DOI 10.1145/2719921, https://doi.org/10.1145/2719921. VERIFIED by search (bibliographic data only; full text not read).
10. Open Scientific Visualization Datasets, P. Klacansky. http://klacansky.com/open-scivis-datasets/ (plain HTTP; HTTPS refused on 2026-10-26). VERIFIED. Per-dataset credits: [STUDENT] to copy each dataset's own credit line from the site into the README.
11. Project-internal evidence: `report/install_log.md`.
