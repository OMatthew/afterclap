const { chromium } = require('/home/claude/afterclap/engine/pw.cjs');
const fs=require('fs'); const S='/tmp/claude-0/-home-claude/9bf0941c-ed10-5395-ac05-5ad6d3589ded/scratchpad/fbcover/';
const b64 = f => 'data:image/png;base64,' + fs.readFileSync(S+f).toString('base64');
const font = 'data:font/woff2;base64,' + fs.readFileSync('/home/claude/afterclap/node_modules/@fontsource/im-fell-english/files/im-fell-english-latin-400-normal.woff2').toString('base64');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1640, height: 856 } });
  const items = [ // file, centerX, bottomY, height
    ['coins_c.png', 290, 525, 130],
    ['bottle_c.png', 565, 525, 230],
    ['jar_c.png', 830, 538, 310],
    ['orange_c.png', 1090, 525, 175],
    ['margarine_c.png', 1350, 525, 122],
  ];
  const imgs = items.map(([f,x,y,h]) => `<img src="${b64(f)}" style="position:absolute;height:${h}px;left:${x}px;top:${y-h}px;transform:translateX(-50%)">`).join('');
  await p.setContent(`<style>@font-face{font-family:Fell;src:url(${font}) format('woff2')}</style>
  <body style="margin:0;width:1640px;height:856px;position:relative;background:url(${b64('bg.png')});overflow:hidden">${imgs}
  <div style="position:absolute;left:0;right:0;top:568px;text-align:center;font-family:Fell,Georgia,serif;font-size:46px;color:#1C1815">Why ordinary things are the way they are.</div></body>`);
  await p.waitForTimeout(400);
  await p.screenshot({ path: S+'fb-cover.png' });
  await b.close();
})();
