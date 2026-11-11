// Start the Python static server on port 8000, then run: node tools/check_mobile.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.join(__dirname,'..');
const origin = 'http://127.0.0.1:8000';
const primary = fs.readdirSync(root).filter(x=>x.endsWith('.html'));
const guides = fs.readdirSync(path.join(root,'seo')).filter(x=>x.endsWith('.html')).map(x=>'seo/'+x);
const widths = [320,375,390,768,1024,1440];
(async () => {
  const browser = await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const errors = [], failedLocal = [], externalCode = [];
  try {
    const context = await browser.newContext({viewport:{width:375,height:812},hasTouch:true});
    await context.route('**/*',route=>{
      const request=route.request();
      if (request.url().startsWith(origin)) return route.continue();
      if (['script','stylesheet','font'].includes(request.resourceType())) externalCode.push(request.url());
      return route.abort(); // Offline asset resilience; never contact external services.
    });
    const page = await context.newPage();
    page.on('pageerror',e=>errors.push(e.message));
    page.on('response',r=>{if(r.url().startsWith(origin)&&r.status()>=400) failedLocal.push([r.url(),r.status()]);});
    let checks=0;
    for (const file of (process.argv.includes('--interactions-only') ? [] : [...primary,...guides])) {
      const response = await page.goto(origin+'/'+file,{waitUntil:'load'});
      assert.equal(response.status(),200,file);
      assert.equal(await page.locator('h1').count(),1,file);
      assert.equal(await page.locator('.site-header').count(),1,file);
      assert.equal(await page.locator('main#main').count(),1,file);
      for(const width of widths) {
        await page.setViewportSize({width,height:812});
        const result = await page.evaluate(()=>{
          const clipped=[];
          const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
          while(walker.nextNode()) {
            const node=walker.currentNode, parent=node.parentElement;
            if(!node.textContent.trim()||parent.closest('script,style,noscript,.table-scroll,.site-skip')) continue;
            const range=document.createRange();range.selectNodeContents(node);
            for(const rect of range.getClientRects()) {
              if(rect.width&&rect.height&&(rect.right>innerWidth+2||rect.left < -2)) {
                clipped.push(node.textContent.trim().slice(0,70));break;
              }
            }
          }
          return {width:innerWidth,scroll:document.documentElement.scrollWidth,clipped};
        });
        assert(result.scroll<=width,`${file} @ ${width}: page overflow ${result.scroll}`);
        assert.deepEqual(result.clipped,[],`${file} @ ${width}: clipped text`);
        checks++;
      }
      await page.setViewportSize({width:320,height:640});
      const toggle=page.locator('.site-menu-toggle'),nav=page.locator('#site-navigation');
      assert(await toggle.isVisible(),file);
      assert(!(await nav.isVisible()),file);
      assert(await toggle.evaluate(el=>el.getBoundingClientRect().height>=44),file);
      await toggle.click();
      assert.equal(await toggle.getAttribute('aria-expanded'),'true');
      assert(await nav.isVisible());
      assert.equal(await nav.locator('a').count(),10);
      assert(await nav.locator('a').evaluateAll(items=>items.every(el=>el.getBoundingClientRect().height>=44)));
      await page.keyboard.press('Escape');
      assert.equal(await toggle.getAttribute('aria-expanded'),'false');
      assert(await toggle.evaluate(el=>el===document.activeElement));
      if(file.startsWith('seo/') && file!=='seo/index.html') {
        assert(await page.locator('.table-scroll').evaluate(el=>el.scrollWidth>el.clientWidth),'Expected local table scroll');
        await page.locator('.table-scroll').focus();
        await page.keyboard.press('ArrowRight');
        await page.locator('summary').first().click();
        assert(await page.locator('details').first().evaluate(el=>el.open));
      }
    }
    if(checks) console.log(`PASS: ${primary.length+guides.length} pages × ${widths.length} widths (${checks} layouts); no page overflow or clipped text; mobile menus and 100 guide tables/FAQs.`);
    for (const file of ['company_registration.html','business_services.html','tax_compliance.html','jobreadyvirtualoffice.html']) {
      await page.goto(origin+'/'+file);
      const form=page.locator('form[data-enquiry]');
      assert.equal(await form.count(),1);
      assert(await form.locator('input,select,textarea').evaluateAll(elements=>elements.every(el=>el.labels.length&&parseFloat(getComputedStyle(el).fontSize)>=16&&el.getBoundingClientRect().height>=44)));
      assert.equal(await form.locator('input[type=tel]').getAttribute('autocomplete'),'tel');
      await form.locator('button[type=submit]').click();
      assert.equal(new URL(page.url()).pathname,'/'+file,'Invalid form navigated');
      assert(!(await form.evaluate(el=>el.checkValidity())));
      await form.locator('input[name=Name]').fill('Mobile UX Test');
      await form.locator('input[name=Phone]').fill('abc');
      assert(!(await form.evaluate(el=>el.checkValidity())));
      await form.locator('input[name=Phone]').fill('+91 90000 00000');
      await form.locator('input[name=Email]').fill('test@example.com');
      await form.locator('textarea').fill('Two desks for a trial visit');
      assert(await form.evaluate(el=>el.checkValidity()));
      let enquiry;
      await page.route('https://wa.me/**',route=>{
        enquiry=route.request().url();
        return route.fulfill({status:200,contentType:'text/html',body:'<p>Intercepted test enquiry. Nothing was sent.</p>'});
      });
      await form.locator('button[type=submit]').click();
      await page.waitForURL('https://wa.me/**');
      const message=new URL(enquiry).searchParams.get('text');
      assert(message.includes('Mobile UX Test')&&message.includes('+91 90000 00000')&&message.includes('Two desks for a trial visit'));
      await page.unroute('https://wa.me/**');
    }
    console.log('PASS: four enquiry forms; accessible labels, mobile input sizes/keyboards, invalid input blocked, entered details retained in intercepted WhatsApp drafts. No messages sent.');
    await page.goto(origin+'/seo/');
    await page.locator('[data-filter="2"]').click();
    assert.equal(await page.locator('[data-guide]:visible').count(),15);
    await page.locator('[data-filter="all"]').click();
    await page.locator('#guide-search').fill('Boring Road');
    assert.equal(await page.locator('[data-guide]:visible').count(),2);
    await page.locator('#guide-search').fill('not-a-workspace-123');
    assert(await page.locator('#no-results').isVisible());
    await page.goto(origin+'/index.html');
    await page.setViewportSize({width:812,height:375});
    await page.locator('.site-menu-toggle').click();
    const contact=page.locator('#site-navigation a').last();
    await contact.scrollIntoViewIfNeeded();
    assert(await contact.evaluate(el=>el.getBoundingClientRect().bottom<=innerHeight+1),'Landscape menu cannot scroll');
    await page.locator('.site-menu-toggle').click();
    await page.setViewportSize({width:1440,height:900});
    assert(await page.locator('#site-navigation').isVisible());
    assert(!(await page.locator('.site-menu-toggle').isVisible()));
    await page.emulateMedia({reducedMotion:'reduce'});
    assert.equal(await page.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior),'auto');
    for(const file of ['index.html','company_registration.html','seo/index.html','seo/best-coworking-space-in-patna.html']) {
      await page.goto(origin+'/'+file);
      await page.setViewportSize({width:390,height:844});
      await page.screenshot({path:'/tmp/mobile-'+file.replaceAll('/','-')+'.png'});
    }
    const nojs = await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:812}});
    await nojs.route('**/*',r=>r.request().url().startsWith(origin)?r.continue():r.abort());
    const fallback=await nojs.newPage();await fallback.goto(origin+'/index.html');
    assert(await fallback.locator('#site-navigation').isVisible(),'Navigation unavailable without JS');
    assert.deepEqual(errors,[]);assert.deepEqual(failedLocal,[]);assert.deepEqual(externalCode,[]);
    console.log('PASS: mobile directory search, short landscape menu, desktop navigation, reduced motion, no-JS navigation; no JS errors or missing local assets; no external code/font dependencies.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
