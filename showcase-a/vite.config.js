import { defineConfig } from 'vite';

// `base` is configurable for a GitHub Pages deploy (extra E1).
export default defineConfig({
  base: process.env.VITE_BASE || '/',
});
