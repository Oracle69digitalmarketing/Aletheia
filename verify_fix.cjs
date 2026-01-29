const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Log all console messages
  page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
  page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));

  try {
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    console.log('Page loaded');

    const goalInput = await page.locator('textarea[placeholder*="New Year\'s resolution"]');
    await goalInput.fill('Learn to play piano in 6 months');

    const generateButton = await page.locator('button:has-text("Generate")');
    await generateButton.click();
    console.log('Clicked Generate');

    // Wait for the loading state to appear
    await page.waitForSelector('text=Architecting Strategy', { timeout: 5000 });
    console.log('Loading state appeared');

    // Wait for the results to appear
    await page.waitForSelector('text=Strategic Plan', { timeout: 60000 });
    console.log('Results appeared');

    // Take a full page screenshot
    await page.screenshot({ path: '/home/jules/verification/full_dashboard.png', fullPage: true });

    const rootHtml = await page.evaluate(() => document.getElementById('root').innerHTML);
    console.log('Root content length:', rootHtml.length);

  } catch (error) {
    console.error('Test failed:', error);
    await page.screenshot({ path: '/home/jules/verification/failure.png' });
  } finally {
    await browser.close();
  }
})();
