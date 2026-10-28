// Writes public/mesh/sample_torus.obj, a small generated torus (about 2k triangles) used by the mesh loader.
// Placed in the middle of the 256^3 sample volumes. Run: node gen_sample_mesh.mjs
import { mkdirSync, writeFileSync } from 'node:fs';

const R = 60, r = 20, nu = 48, nv = 24, c = [128, 128, 128];
const v = [], n = [], f = [];
for (let i = 0; i < nu; i++) {
  for (let j = 0; j < nv; j++) {
    const u = (2 * Math.PI * i) / nu, w = (2 * Math.PI * j) / nv;
    const nx = Math.cos(u) * Math.cos(w), ny = Math.sin(u) * Math.cos(w), nz = Math.sin(w);
    v.push([c[0] + (R + r * Math.cos(w)) * Math.cos(u), c[1] + (R + r * Math.cos(w)) * Math.sin(u), c[2] + r * nz]);
    n.push([nx, ny, nz]);
  }
}
const id = (i, j) => (i % nu) * nv + (j % nv) + 1;
for (let i = 0; i < nu; i++) {
  for (let j = 0; j < nv; j++) {
    const a = id(i, j), b = id(i + 1, j), d = id(i, j + 1), e = id(i + 1, j + 1);
    f.push([a, b, e], [a, e, d]);
  }
}
const out = ['# generated torus', ...v.map((p) => `v ${p.map((x) => x.toFixed(3)).join(' ')}`),
  ...n.map((p) => `vn ${p.map((x) => x.toFixed(4)).join(' ')}`),
  ...f.map((t) => `f ${t.map((k) => `${k}//${k}`).join(' ')}`)];
mkdirSync('public/mesh', { recursive: true });
writeFileSync('public/mesh/sample_torus.obj', out.join('\n') + '\n');
console.log(`wrote public/mesh/sample_torus.obj: ${v.length} vertices, ${f.length} triangles`);
