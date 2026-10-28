# Extra E10: WebXR volume viewing in Showcase A

Date: 2026-10-28. Optional extra, not part of the initial report. No real headset was used; all tests ran against an emulated WebXR device in headless Chrome with software GL (SwiftShader).

## Outcome
Works in the emulator. `immersive-vr` session starts through vtk.js's `vtkWebXRRenderWindowHelper`, the render loop switches to the XR frame loop, the volume is drawn in two side-by-side eye viewports, and ending the session restores the normal view.

## What the installed vtk.js 37.4.6 provides (read from node_modules)
- `@kitware/vtk.js/Rendering/WebXR/RenderWindowHelper` (`vtkWebXRRenderWindowHelper`), also exported as `Rendering/WebXR.js` (`{ vtkRenderWindowHelper }`). Constants: `XrSessionTypes = { HmdVR: 0, MobileAR: 1, LookingGlassVR: 2, HmdAR: 3 }`.
- Methods in the JS: `initialize(renderWindow)`, `getXrSupported()` (only `navigator.xr !== undefined`), `startXR(type)`, `enterXR(session)`, `resetXRScene(rescale=0.25, translateZ=-1.5)`, `stopXR()`, `getXrSession()`, property `drawControllersRay`.
- `RenderWindowHelper.d.ts` documents `initialize(): void` without argument, but the JS requires the vtkOpenGLRenderWindow as argument (`model.renderWindow.getRenderable().getInteractor()`). Used: `viewer.fsrw.getApiSpecificRenderWindow()`.
- `startXR` checks `!navigator.xr.isSessionSupported(type)`; that returns a Promise, so the check is always false (never throws), and a failed `requestSession` throws inside a promise rejection handler (surfaces as an unhandled rejection, not as an exception from `startXR`).
- `enterXR`: `gl.makeXRCompatible()`, `new XRWebGLLayer(session, gl)`, `updateRenderState({baseLayer})`, reference space `"local"`, `interactor.switchToXRAnimation()`, then `session.requestAnimationFrame(xrRender)`. `xrRender` sets the renderer viewport to left half / right half per eye, sets camera from `view.transform.inverse.matrix` and `view.projectionMatrix`, and calls `renderWindow.traverseAllPasses()`.
- `stopXR`: cancels the XR frame, `returnFromXRAnimation()`, ends the session (ignores DOMException), restores canvas size, background, projection matrix and viewport. The helper does not listen for the session `end` event itself.
- No XR example directory ships in node_modules (no `Examples/` folder with WebXR; `grep -ril webxr` finds only Rendering/WebXR, Rendering/Core/Camera, RenderWindowInteractor constants and WebGPU/RenderWindow d.ts).
- Volume rendering in XR: no failure found. vtkOpenGLVolumeMapper rendered into both eye viewports in the emulator.

## Code added
- New file `showcase-a/src/xr/index.js`: `initXR(viewer, body)` adds a "WebXR" fieldset to the Tools panel with an Enter VR / Exit VR button and a message line.
  - Feature detection: secure context check (`window.isSecureContext`), `navigator.xr`, then `await navigator.xr.isSessionSupported('immersive-vr')`. Button disabled, with the reason in the message, when any of these fails. Only `immersive-vr` is offered; `immersive-ar` is supported by the helper (`XrSessionTypes.HmdAR`) but not wired or tested.
  - Start: `helper.startXR(0)`; waits (20 s timeout) for `helper.getXrSession()` via `onModified`; shows an error message on failure (via the unhandledrejection event).
  - End: listens to the session `end` event (headset-initiated end or Exit VR button) and calls `helper.stopXR()`, then re-renders.
  - If the loaded volume has more than 128^3 voxels the message advises using foot_64 or tooth.
- Existing lines changed (only `showcase-a/src/tools/index.js`, 2 lines added, none removed):
  - line 23: `import { initXR } from '../xr';`
  - line 323: `  add(initXR(viewer, body));` (just before the final `return {`)
- No change to main.js, vite.config.js, index.html, package.json. No new npm dependency in the app. The button is always present in the Tools panel (no `?xr=1` needed). The `?bench=1` mode never loads the Tools panel code path.

## Test harness (not shipped)
- Emulator: Immersive Web Emulation Runtime, npm package `iwer` version 2.7.0 (npm registry `latest`, modified 2026-10-21), installed in the scratchpad dir, not in the project. Injected with `page.evaluateOnNewDocument` (iwer.min.js plus `new XRDevice(metaQuest3).installRuntime({ forceInstall: true })`). `forceInstall` was required because headless Chrome already exposes a native `navigator.xr`; without the emulator the app showed "immersive-vr not supported (no headset/runtime found)" and the disabled button (verified).
- Script copy: `report/extras/e10_xrtest.mjs` (puppeteer-core from bench/node_modules, `/usr/bin/google-chrome --no-sandbox`, ANGLE SwiftShader, vite dev server on port 5192, dataset foot_64). It wraps `requestSession` and the session `requestAnimationFrame` to count calls.
- Results of the run:
  - before click: button enabled, message "immersive-vr supported.", canvas 1000x800.
  - after click: `requestSession` called 1 time with `"immersive-vr"`; button text "Exit VR"; XR frame callbacks counted 8 after 15 s and 17 after 20 s (about 0.5 frames/s on software GL, so this says nothing about headset performance); canvas backing size 200x120 (the emulator's XRWebGLLayer framebuffer size, used by the helper's `setSize`).
  - Exit VR click: session `end` event fired once; button back to "Enter VR", message "Session ended, normal view restored.", canvas back to 1000x800, normal view rendering again.
- Screenshot: `report/figures/extra_e10_webxr.png` shows the in-session canvas: foot_64 drawn twice, left and right eye viewports (emulator framebuffer is small, so the image is upscaled and the grain is visible).
- Smoke test `?bench=1&data=foot_64.vti&frames=5&reps=1`: page showed "bench complete: 1 rows in localStorage "bench_rows"". `npm run build` in showcase-a: succeeded (chunk size warning as before).
- Observed console message in the page: one 404 resource (not related to XR; also logged without the emulator).

## Known requirements for real use (from the helper source and the WebXR spec; not tested on hardware)
- Secure context (https or localhost); the app checks `window.isSecureContext`.
- A WebGL context made XR compatible (`makeXRCompatible()` in `enterXR`) and `XRWebGLLayer` (baseLayer path, not the WebXR Layers API).
- `immersive-vr` support from the browser and a device runtime.
- Small volume (foot_64 or tooth): two eyes are rendered per frame with the ray-marching volume mapper.

## Not tested
- Any real headset (Quest, PC VR), controllers, hand tracking, head pose motion (emulator device was static), `drawControllersRay`.
- `immersive-ar` sessions (`HmdAR`/`MobileAR`) and Looking Glass.
- Windows, Firefox, Safari, Meta Quest Browser, Chrome on Android.
- Frame rate and comfort in a headset.
- Behavior with the other Tools (isosurface, meshes, widgets, measurement line) while in XR.
