// Optional WebXR "Enter VR" control (extra E10). Lives in the Tools panel; not used in ?bench=1.
// Uses vtk.js's own vtkWebXRRenderWindowHelper (Rendering/WebXR/RenderWindowHelper).
// Requirements: secure context (https or localhost), a browser with navigator.xr and an
// immersive-vr device (or an emulator), and a WebGL2 context that can be made XR compatible.
import vtkWebXRRenderWindowHelper from '@kitware/vtk.js/Rendering/WebXR/RenderWindowHelper';

const SESSION = 'immersive-vr';
const SMALL_VOXELS = 128 ** 3; // above this, warn: headset must render two eyes every frame

export function initXR(viewer, body) {
  const el = document.createElement('fieldset');
  el.innerHTML = `<legend>WebXR</legend>
    <button class="xr" disabled>Enter VR</button>
    <output class="xrmsg">checking WebXR...</output>`;
  body.appendChild(el);
  const btn = el.querySelector('.xr');
  const msg = el.querySelector('.xrmsg');
  let helper = null;
  let image = null;
  let inXR = false;
  let supportNote = '';

  const dimsNote = () => {
    if (!image) return '';
    const d = image.getDimensions();
    return d[0] * d[1] * d[2] > SMALL_VOXELS ? ` Volume ${d.join('x')} is large for a headset; use foot_64 or tooth.` : '';
  };
  const setMsg = (t) => { msg.textContent = t; };

  function onSessionEnd() {
    if (!inXR) return;
    inXR = false;
    // helper.stopXR() cancels the XR frame loop, restores canvas size/camera and the 2D animation loop
    helper.stopXR().catch((e) => console.warn('stopXR', e)).finally(() => {
      btn.textContent = 'Enter VR';
      btn.disabled = false;
      setMsg('Session ended, normal view restored.');
      viewer.renderWindow.render();
    });
  }

  async function enter() {
    btn.disabled = true;
    setMsg('Requesting session...');
    try {
      if (!helper) {
        helper = vtkWebXRRenderWindowHelper.newInstance();
        helper.initialize(viewer.fsrw.getApiSpecificRenderWindow()); // JS takes the OpenGL render window
      }
      const done = new Promise((resolve, reject) => {
        const sub = helper.onModified(() => {
          const s = helper.getXrSession();
          if (s) { sub.unsubscribe(); resolve(s); }
        });
        setTimeout(() => { sub.unsubscribe(); reject(new Error('timeout waiting for XR session')); }, 20000);
        window.addEventListener('unhandledrejection', function h(ev) {
          // vtk.js startXR() rethrows session failures inside a promise callback; surface them
          window.removeEventListener('unhandledrejection', h);
          reject(ev.reason instanceof Error ? ev.reason : new Error(String(ev.reason)));
        }, { once: true });
      });
      helper.startXR(0); // XrSessionTypes.HmdVR -> immersive-vr
      const session = await done;
      inXR = true;
      session.addEventListener('end', onSessionEnd);
      btn.textContent = 'Exit VR';
      btn.disabled = false;
      setMsg('In VR session.' + dimsNote());
    } catch (e) {
      console.error('XR start failed', e);
      btn.disabled = false;
      setMsg(`Could not start VR: ${e.message}`);
    }
  }

  btn.onclick = () => (inXR ? helper.getXrSession()?.end() : enter());

  (async () => {
    if (!window.isSecureContext) { setMsg('WebXR needs a secure context (https or localhost).'); return; }
    if (!navigator.xr) { setMsg('navigator.xr not available in this browser.'); return; }
    try {
      const ok = await navigator.xr.isSessionSupported(SESSION);
      if (!ok) { setMsg(`${SESSION} not supported (no headset/runtime found).`); return; }
      supportNote = 'immersive-vr supported.';
      btn.disabled = false;
      setMsg(supportNote);
    } catch (e) {
      setMsg(`isSessionSupported failed: ${e.message}`);
    }
  })();

  return {
    setImage(im) { image = im; if (!btn.disabled && !inXR) setMsg(supportNote + dimsNote()); },
  };
}
