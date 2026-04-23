/**
 * CQC Site Verification Script
 * Run: node cqc-test.js
 */

const { chromium } = require('playwright');

const BASE = 'http://localhost:8080';
const MOBILE = { width: 390, height: 844 };
const DESKTOP = { width: 1280, height: 800 };

async function run() {
  // Use system chromium (already has all deps)
  const browser = await chromium.launch({
    executablePath: '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  
  // Track passes/fails
  let passed = 0;
  let failed = 0;
  
  function check(name, condition) {
    if (condition) {
      console.log(`  ✅ ${name}`);
      passed++;
    } else {
      console.log(`  ❌ ${name}`);
      failed++;
    }
  }

  // ─── DESKTOP TESTS ────────────────────────────────────────
  console.log('\n🖥️  DESKTOP (1280x800)');
  await page.setViewportSize(DESKTOP);
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);

  const desktopNavbar = await page.locator('#navbar').boundingBox();
  check('Navbar is visible on load', desktopNavbar !== null);

  const desktopLogo = await page.locator('a.logo img').boundingBox();
  check('Nav logo (50x50) is present', desktopLogo !== null);

  const desktopHeroLogo = await page.locator('.hero-logo img').boundingBox();
  check('Hero logo is present', desktopHeroLogo !== null);

  const desktopNavLinks = await page.locator('.nav-links').isVisible();
  check('Nav links are visible on desktop', desktopNavLinks === true);

  // Scroll down on desktop
  await page.evaluate(() => window.scrollTo(0, 300));
  await page.waitForTimeout(300);
  const desktopAfterScroll = await page.locator('#navbar').isVisible();
  check('Navbar stays visible after scroll on desktop', desktopAfterScroll === true);

  // ─── MOBILE TESTS ─────────────────────────────────────────
  console.log('\n📱 MOBILE (390x844)');
  await page.setViewportSize(MOBILE);
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);

  const mobileHeroLogo = await page.locator('.hero-logo img').boundingBox();
  check('Hero logo is visible on mobile load', mobileHeroLogo !== null && mobileHeroLogo.height > 0);

  const mobileNavHidden = await page.evaluate(() => {
    const n = document.getElementById('navbar');
    const cs = getComputedStyle(n);
    return cs.visibility === 'hidden' || cs.display === 'none';
  });
  check('Navbar is hidden on mobile hero (immersive landing)', mobileNavHidden === true);

  const mobileNavLinks = await page.locator('.nav-links').isVisible();
  check('Nav links hidden on immersive landing', mobileNavLinks === false);

  // Scroll to reveal navbar on mobile
  await page.evaluate(() => window.scrollTo(0, 300));
  await page.waitForTimeout(500);
  
  const mobileAfterScroll = await page.evaluate(() => {
    const n = document.getElementById('navbar');
    const cs = getComputedStyle(n);
    return { visibility: cs.visibility, display: cs.display, className: n.className };
  });
  check('Navbar becomes visible after scroll on mobile', mobileAfterScroll.visibility === 'visible' && mobileAfterScroll.display !== 'none');
  check('Navbar has .scrolled class after scroll', mobileAfterScroll.className.includes('scrolled') === true);

  const mobileNavLinksAfterScroll = await page.locator('.nav-links').isVisible();
  check('Nav links visible after scroll on mobile', mobileNavLinksAfterScroll === true);

  // Check sticky CTA appears
  await page.evaluate(() => window.scrollTo(0, 100));
  await page.waitForTimeout(300);
  const stickyCta = await page.locator('.sticky-cta').isVisible();
  check('Sticky CTA bar appears after scrolling', stickyCta === true);

  // ─── SUMMARY ──────────────────────────────────────────────
  console.log(`\n📊 RESULTS: ${passed} passed, ${failed} failed`);
  await browser.close();
  process.exit(failed > 0 ? 1 : 0);
}

run().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});