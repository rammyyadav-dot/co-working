// Run against the Python static server: node tools/check_seo_browser.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const topics = JSON.parse(fs.readFileSync(path.join(__dirname,'../seo/keyword-map.json'),'utf8'));
(async () => {
  const browser = await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000}});
    const errors = [], failed = [], external = [];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('requestfailed',r=>failed.push(r.url()));
    page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:8000/')) external.push(r.url());});
    const origin = 'http://127.0.0.1:8000';
    await page.goto(origin+'/seo/');
    assert.equal(await page.locator('[data-guide]:visible').count(),100);
    for (let i=0;i<5;i++) {
      await page.locator(`[data-filter="${i}"]`).click();
      assert.equal(await page.locator('[data-guide]:visible').count(),[25,25,15,15,20][i]);
    }
    await page.locator('[data-filter="all"]').click();
    await page.locator('#guide-search').fill('Boring Road');
    assert.equal(await page.locator('[data-guide]:visible').count(),2);
    await page.locator('#guide-search').fill('no-such-workspace-123456');
    assert.equal(await page.locator('[data-guide]:visible').count(),0);
    assert(await page.locator('#no-results').isVisible());
    await page.locator('#guide-search').fill('');
    assert.equal(await page.locator('[data-guide]:visible').count(),100);
    await page.screenshot({path:'/tmp/seo-hub-desktop.png'});
    for (const topic of topics) {
      const response = await page.goto(origin+'/seo/'+topic.slug+'.html');
      assert.equal(response.status(),200);
      assert.equal(await page.locator('h1').innerText(),topic.keyword);
      assert.equal(await page.title(),topic.keyword+' | JobReady');
      const metadata = await page.evaluate(() => {
        const content = (key) => document.querySelector(`meta[name="${key}"],meta[property="${key}"]`)?.content;
        return {title:document.title,description:content('description'),ogTitle:content('og:title'),ogDescription:content('og:description'),image:content('og:image'),card:content('twitter:card')};
      });
      assert.equal(metadata.ogTitle,metadata.title);
      assert.equal(metadata.ogDescription,metadata.description);
      assert(metadata.image.endsWith('/'+topic.slug+'.png'));
      assert.equal(metadata.card,'summary_large_image');
      assert.equal(await page.locator('details').count(),5);
      await page.locator('summary').nth(1).click();
      assert(await page.locator('details').nth(1).evaluate(el=>el.open));
      assert.equal(await page.locator('#enquire a[href^="https://wa.me/"]').count(),1);
      for (const width of [1440,390]) {
        await page.setViewportSize({width,height:900});
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Overflow: ${topic.slug} @ ${width}`);
      }
    }
    await page.goto(origin+'/seo/best-coworking-space-in-patna.html');
    await page.setViewportSize({width:1440,height:1000});
    await page.screenshot({path:'/tmp/seo-page-desktop.png'});
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:'/tmp/seo-page-mobile.png'});
    await page.goto(origin+'/seo/');
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile directory overflow');
    await page.screenshot({path:'/tmp/seo-hub-mobile.png'});
    assert.deepEqual(errors,[]); assert.deepEqual(failed,[]); assert.deepEqual(external,[]);
    console.log('PASS: 100 pages at desktop/mobile widths; HTTP, H1, FAQ interactions and enquiry links; directory category/search/empty-state tests; zero page errors, failed requests or external dependencies.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
