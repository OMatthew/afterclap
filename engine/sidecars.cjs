const fs = require('fs'), path = require('path');

// Sidecars use the same caption groups as the picture, even with burned-in captions off.
function writeSidecars(plan, OUT, sname, opt = () => null) {
  const start = opt('from') ? Math.round(+opt('from') * plan.fps) / plan.fps : 0;
  const end = opt('to') ? Math.min(plan.duration, Math.round(+opt('to') * plan.fps) / plan.fps) : plan.duration;
  if (!Number.isFinite(start) || !Number.isFinite(end) || start < 0 || end <= start) throw new Error('Invalid --from/--to range');
  const stamp = t => {
    const ms = Math.round(Math.max(0, t) * 1000);
    return `${String(Math.floor(ms / 3600000)).padStart(2, '0')}:${String(Math.floor(ms / 60000) % 60).padStart(2, '0')}:${String(Math.floor(ms / 1000) % 60).padStart(2, '0')},${String(ms % 1000).padStart(3, '0')}`;
  };
  const caps = plan.captions.filter(c => c.t1 > start && c.t0 < end);
  fs.writeFileSync(path.join(OUT, `${sname}.srt`), caps.map((c, i) =>
    `${i + 1}\n${stamp(Math.max(start, c.t0) - start)} --> ${stamp(Math.min(end, c.t1) - start)}\n${c.text}\n`).join('\n'));
  const file = path.join(OUT, `${sname}-chapters.txt`);
  if (plan.chapters.length) {
    const chapters = plan.chapters.filter((c, i, all) => c.t < end && (c.t >= start || !all[i + 1] || all[i + 1].t > start));
    fs.writeFileSync(file, chapters.map((c, i) => {
      const t = i === 0 ? 0 : Math.max(0, Math.floor(c.t - start));
      const ts = t >= 3600 ? `${Math.floor(t / 3600)}:${String(Math.floor(t / 60) % 60).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}` : `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`;
      return `${ts} ${String(c.title).replace(/[\r\n]+/g, ' ')}`;
    }).join('\n') + '\n');
  } else if (fs.existsSync(file)) fs.unlinkSync(file);
}

module.exports = { writeSidecars };
