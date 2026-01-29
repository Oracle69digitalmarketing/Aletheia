const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  page.on('console', msg => {
    console.log(`[BROWSER ${msg.type().toUpperCase()}] ${msg.text()}`);
  });

  page.on('pageerror', err => {
    console.log(`[BROWSER ERROR] ${err.stack || err.message}`);
  });

  try {
    console.log('Navigating to http://localhost:5173...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle', timeout: 30000 });
    console.log('Page title:', await page.title());

    // Check if #root has content
    const content = await page.innerHTML('#root');
    console.log('Root content length:', content.length);
    if (content.length === 0) {
        console.log('Root is EMPTY!');
    }

    await page.screenshot({ path: 'debug_screenshot.png' });
    console.log('Screenshot saved as debug_screenshot.png');

  } catch (error) {
    console.error('FAILED to load page:', error);
  } finally {
    await browser.close();
  }
})();
