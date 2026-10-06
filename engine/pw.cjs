// Find Playwright without installing it (it ships preinstalled in the build boxes).
let pw;
for (const p of ['playwright', '/opt/npm-tools/node_modules/playwright', 'playwright-core']) {
  try { pw = require(p); break; } catch (e) { /* try next */ }
}
if (!pw) throw new Error('Playwright not found. It is usually under /opt/npm-tools/node_modules/playwright; do not run `playwright install`.');
if (!process.env.PLAYWRIGHT_BROWSERS_PATH) process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/pw-browsers';
module.exports = pw;
