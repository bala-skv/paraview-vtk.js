// Parse every file in public/data/index.json with vtk.js and compare against the index. Run: npm run verify-data
import { readFileSync } from 'node:fs';
import vtkXMLImageDataReader from '@kitware/vtk.js/IO/XML/XMLImageDataReader.js';

const dir = new URL('./public/data/', import.meta.url);
const index = JSON.parse(readFileSync(new URL('index.json', dir), 'utf8'));
let bad = 0;
for (const e of index) {
  const buf = readFileSync(new URL(e.file, dir));
  const reader = vtkXMLImageDataReader.newInstance();
  try {
    reader.parseAsArrayBuffer(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
    const img = reader.getOutputData(0);
    const dims = img.getDimensions();
    const [lo, hi] = img.getPointData().getScalars().getRange();
    const ok = dims.join() === e.dims.join() && lo === e.range[0] && hi === e.range[1];
    console.log(`${ok ? 'OK  ' : 'BAD '} ${e.name.padEnd(14)} dims=${dims} range=[${lo}, ${hi}] spacing=${img.getSpacing().map((s) => +s.toFixed(4))}`);
    if (!ok) bad++;
  } catch (err) {
    console.log(`FAIL ${e.name}: ${err.message}`);
    bad++;
  }
}
process.exit(bad ? 1 : 0);
