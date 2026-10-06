// Usage: node render.cjs <outDir> [times...]
//   no times  -> renders every frame (30 fps) to outDir/f_00000.png
//   times     -> renders stills at those seconds to outDir/still_<t>.png
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const path = require('path'), fs = require('fs');
const FPS = 30, DUR = 9.9;
(async () => {
  const out = path.resolve(process.argv[2] || 'frames'); fs.mkdirSync(out, { recursive: true });
  const times = process.argv.slice(3).map(Number);
  const jobs = times.length ? times.map(t => ({ t, file: `still_${t.toFixed(2)}.png` }))
    : Array.from({ length: Math.round(FPS * DUR) }, (_, i) => ({ t: i / FPS, file: `f_${String(i).padStart(5, '0')}.png` }));
  const browser = await chromium.launch({ args: ['--disable-gpu', '--force-color-profile=srgb'] });
  const P = Math.min(Number(process.env.PAR || 3), jobs.length);
  const url = 'file://' + path.join(__dirname, 'index.html');
  const t0 = Date.now(); let done = 0;
  await Promise.all(Array.from({ length: P }, async (_, w) => {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    await page.goto(url); await page.waitForFunction(() => window.ready === true);
    for (let i = w; i < jobs.length; i += P) {
      await page.evaluate(t => renderAt(t), jobs[i].t);
      await page.screenshot({ path: path.join(out, jobs[i].file), type: 'png' });
      if (++done % 30 === 0) console.log(`${done}/${jobs.length}  ${((Date.now() - t0) / 1000).toFixed(1)}s`);
    }
  }));
  console.log(`done ${jobs.length} in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  await browser.close();
})();
