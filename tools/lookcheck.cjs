// Side-by-side look check: original PNG vs re-inked on paper, at video scale.
// Usage: node tools/lookcheck.cjs <story> <out.jpg> id1 id2 id3 [--boil n]
const path = require('path'), fs = require('fs');
const { chromium } = require('../engine/pw.cjs');
(async () => {
  const [story, out, ...rest] = process.argv.slice(2);
  const ids = rest.filter(a => !a.startsWith('--'));
  const root = path.resolve(__dirname, '..');
  const rows = ids.map(id => ({
    id,
    png: 'file://' + path.resolve(story, 'art', id + '.png'),
    tr: JSON.parse(fs.readFileSync(path.resolve(story, 'art', 'traced', id + '.json'), 'utf8')),
  }));
  const H = 1080, W = 2160;
  const html = `<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:#fff}svg{display:block}</style>
<script src="file://${root}/engine/ink.js"></script><script src="file://${root}/engine/paper.js"></script></head><body>
<svg id="s" width="${W}" height="${H * rows.length}" xmlns="http://www.w3.org/2000/svg"><defs>
<pattern id="pp" patternUnits="userSpaceOnUse" width="512" height="512"><rect width="512" height="512" fill="#F2ECDF"/><image id="gi" width="512" height="512" href=""/></pattern>
</defs><g id="g"></g></svg>
<script>
const rows=${JSON.stringify(rows)};
document.querySelector('defs').insertAdjacentHTML('beforeend', Paper.INK_FILTER);
document.getElementById('gi').setAttribute('href', Paper.grainURL());
let s='';
rows.forEach((r,k)=>{
  const y0=k*${H};
  s+='<rect x="0" y="'+y0+'" width="1080" height="1080" fill="#fff"/>';
  s+='<image x="28" y="'+(y0+28)+'" width="1024" height="1024" href="'+r.png+'"/>';
  s+='<rect x="1080" y="'+y0+'" width="1080" height="1080" fill="url(#pp)"/>';
  const [w,h]=r.tr.size; const sc=Math.min(760/w,760/h);
  const items=Ink.buildDrawing(r.tr,{x:1080+540-w*sc/2,y:y0+540-h*sc/2,scale:sc},{w:6.6,inner:0.68,minLen:18,seed:k+1});
  s+='<g filter="url(#inkF)" fill="#1C1815">'+Ink.drawingPaths(items,1).map(d=>'<path d="'+d+'"/>').join('')+'</g>';
  s+='<line x1="1080" y1="'+y0+'" x2="1080" y2="'+(y0+1080)+'" stroke="#999" stroke-width="2"/>';
});
document.getElementById('g').innerHTML=s;
window.ready=true;
</script></body></html>`;
  const tmp = path.join(require('os').tmpdir(), 'lookcheck.html');
  fs.writeFileSync(tmp, html);
  const browser = await chromium.launch({ args: ['--disable-gpu', '--force-color-profile=srgb', '--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: W, height: H * rows.length } });
  await page.goto('file://' + tmp); await page.waitForFunction(() => window.ready === true);
  await page.waitForTimeout(300);
  await page.screenshot({ path: out.replace(/\.jpg$/, '.png'), type: 'png' });
  await browser.close();
  console.log('wrote', out);
})();
