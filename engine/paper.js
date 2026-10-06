// Afterclap paper: warm off-white with grain, faint mottling and fibres (from the motion test).
// Browser only. Paper.grainURL() returns a 512x512 tile as a data URL.
(function (root) {
  'use strict';
  const PAPER = '#F2ECDF';
  const INK = '#1C1815';
  function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function grainURL(seed = 99) {
    const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d');
    const img = g.createImageData(512, 512); const r = mulberry32(seed);
    for (let i = 0; i < 512 * 512; i++) {
      const v = r(); const a = Math.pow(r(), 3.2); const dark = v < 0.55;
      img.data[i * 4] = dark ? 70 : 255; img.data[i * 4 + 1] = dark ? 55 : 252; img.data[i * 4 + 2] = dark ? 35 : 245;
      img.data[i * 4 + 3] = Math.round(a * (dark ? 34 : 40));
    }
    g.putImageData(img, 0, 0);
    const wrap = fn => { for (const ox of [-512, 0, 512]) for (const oy of [-512, 0, 512]) fn(ox, oy); };
    for (let i = 0; i < 70; i++) {
      const x = r() * 512, y = r() * 512, R = 40 + r() * 140;
      wrap((ox, oy) => { const gr = g.createRadialGradient(x + ox, y + oy, 0, x + ox, y + oy, R); gr.addColorStop(0, 'rgba(150,115,70,0.012)'); gr.addColorStop(1, 'rgba(150,115,70,0)'); g.fillStyle = gr; g.fillRect(x + ox - R, y + oy - R, 2 * R, 2 * R); });
    }
    g.lineWidth = 0.9;
    for (let i = 0; i < 110; i++) {
      const x = r() * 512, y = r() * 512, a = r() * 6.28, L = 12 + r() * 60, b = (r() - .5) * 30;
      g.strokeStyle = `rgba(${r() < .5 ? '95,75,45' : '255,255,250'},${0.06 + r() * 0.06})`;
      wrap((ox, oy) => { g.beginPath(); g.moveTo(x + ox, y + oy); g.quadraticCurveTo(x + ox + Math.cos(a) * L / 2 - Math.sin(a) * b, y + oy + Math.sin(a) * L / 2 + Math.cos(a) * b, x + ox + Math.cos(a) * L, y + oy + Math.sin(a) * L); g.stroke(); });
    }
    return c.toDataURL('image/png');
  }
  // dry-ink texture filter: a little low-frequency wander + speckled dropout, like a dip pen on rag paper
  const INK_FILTER = `
  <filter id="inkF" filterUnits="userSpaceOnUse" x="-100" y="-100" width="2400" height="40000" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="2" seed="4" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="2.4" xChannelSelector="R" yChannelSelector="G" result="d1"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.30" numOctaves="1" seed="9" result="n2"/>
    <feDisplacementMap in="d1" in2="n2" scale="1.4" xChannelSelector="R" yChannelSelector="G" result="d2"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="1" seed="2" result="n3"/>
    <feColorMatrix in="n3" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.3 0 0 0 1.85" result="g"/>
    <feComposite in="d2" in2="g" operator="in"/>
  </filter>`;
  root.Paper = { PAPER, INK, grainURL, INK_FILTER };
})(typeof self !== 'undefined' ? self : this);
