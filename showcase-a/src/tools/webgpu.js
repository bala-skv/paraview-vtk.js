// WebGPU probe for `?api=webgpu`: reports what the browser exposes. vtk.js builds the
// renderer with viewAPI 'WebGPU' (see createViewer in viewer.js); the Volume profile
// already registers the WebGPU volume, slice and geometry classes.
export async function probeWebGPU() {
  const out = { available: !!navigator.gpu, adapter: 'none', features: 0, note: '' };
  if (!navigator.gpu) { out.note = 'navigator.gpu is undefined (insecure context, flag off or browser without WebGPU)'; return out; }
  try {
    const a = await navigator.gpu.requestAdapter();
    if (!a) { out.note = 'requestAdapter() returned null'; return out; }
    const info = a.info || (a.requestAdapterInfo ? await a.requestAdapterInfo() : {});
    out.adapter = [info.vendor, info.architecture, info.device, info.description].filter(Boolean).join(' / ') || 'unknown';
    out.features = a.features ? a.features.size : 0;
    out.fallback = !!a.isFallbackAdapter;
  } catch (e) { out.note = `adapter request failed: ${e.message}`; }
  return out;
}
