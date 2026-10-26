import { defineConfig } from 'vite';

// `base` is configurable for a GitHub Pages deploy (extra E1).
// vtk.js -> xmlbuilder2 imports Node's `events`; Vite externalizes it for the browser,
// which crashes at load ("Class extends value undefined"). Alias to the npm polyfill.
export default defineConfig({
  base: process.env.VITE_BASE || '/',
  resolve: { alias: { events: 'events/' } },
});
