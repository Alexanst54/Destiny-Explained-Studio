// No web server required: Playwright serves the committed static files through routing.
// PLAYWRIGHT_MODULE may point to an existing Playwright installation.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'../remotion/node_modules/playwright-core');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:393,height:851},isMobile:true,hasTouch:true,acceptDownloads:true});
 // Managed Chromium blocks blob: navigation. Capture the actual download payload
 // without overriding browser policies; Android file saving needs a device check.
 await context.addInitScript(()=>{
  const create=URL.createObjectURL.bind(URL);
  URL.createObjectURL=blob=>{window.__exported=blob;return create(blob);};
  document.addEventListener('click',event=>{if(event.target.closest?.('a[download]'))event.preventDefault();},true);
 });
 const page=await context.newPage(),errors=[];page.setDefaultTimeout(8000);
 page.on('pageerror',e=>errors.push(e.message));
 await context.route('**/*',async route=>{
  const url=new URL(route.request().url());assert.equal(url.origin,'https://editor.test');
  const rel=url.pathname.replace('/Destiny-Explained-Studio/','')||'index.html';
  assert.ok(!rel.includes('..'));
  const type=rel.endsWith('.js')?'text/javascript':rel.endsWith('.css')?'text/css':'text/html';
  await route.fulfill({body:await fs.readFile(path.join(root,'docs',rel)),contentType:type});
 });
 const url='https://editor.test/Destiny-Explained-Studio/';
 await page.goto(url);await page.locator('#episode-title').waitFor();
 for(const width of [320,360,393,1280]){await page.setViewportSize({width,height:851});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`overflow at ${width}`);}
 await page.setViewportSize({width:393,height:851});
 const original=JSON.parse(await fs.readFile(path.join(root,'remotion/episodes/traveler_episode_002_cinematic.json'),'utf8'));
 original.extra={deep:['keep',1]};original.scenes[0].extension={preserve:true};original.title='<img src=x onerror=alert(1)>';
 await page.locator('#import-file').setInputFiles({name:'episode.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(original))});
 await page.waitForFunction(()=>document.querySelector('#episode-title')?.value.startsWith('<img'));
 assert.equal(await page.locator('#project-heading img').count(),0);
 await page.locator('#episode-title').fill('Titre modifié');await page.locator('#episode-title').blur();
 await page.getByRole('button',{name:'Enregistrer',exact:true}).click();
 await page.reload();await page.locator('#episode-title').waitFor();assert.equal(await page.locator('#episode-title').inputValue(),'Titre modifié');
 async function downloaded(selector){await page.evaluate(()=>{window.__exported=null;});await page.locator(selector).click();await page.waitForFunction(()=>window.__exported instanceof Blob);return page.evaluate(async()=>JSON.parse(await window.__exported.text()));}
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));const archive=await downloaded('#export-button');assert.deepEqual(archive.extra,original.extra);assert.deepEqual(archive.scenes[0].extension,{preserve:true});assert.equal(archive.title,'Titre modifié');
 const compatible=await downloaded('#export-render');assert.equal(compatible.extra,undefined);assert.equal(compatible.scenes[0].extension,undefined);assert.equal(compatible.scenes[0].narration,original.scenes[0].narration);
 await page.getByRole('button',{name:'JSON avancé',exact:true}).click();await page.locator('#advanced-json').fill('{invalid');await page.getByRole('button',{name:'Enregistrer',exact:true}).click();await page.reload();await page.locator('#advanced-json').waitFor();assert.equal(await page.locator('#advanced-json').inputValue(),'{invalid');
 await page.getByRole('button',{name:'Appliquer le JSON',exact:true}).click();assert.ok((await page.locator('#toast').textContent()).length);
 await page.getByRole('button',{name:'Annuler les modifications JSON',exact:true}).click();await page.getByRole('button',{name:'Débutant',exact:true}).click();
 await page.getByRole('button',{name:'+ Nouveau',exact:true}).click();await page.getByRole('button',{name:'+ Ajouter un plan',exact:true}).click();assert.equal(await page.locator('.shot-marker').count(),2);
 await page.locator('#scene-duration').fill('9.5');await page.locator('#scene-duration').blur();await page.getByRole('button',{name:'Enregistrer',exact:true}).click();const changed=await downloaded('#export-button');assert.equal(changed.format.durationFrames,285);
 await fs.mkdir(path.join(root,'remotion/out'),{recursive:true});await page.screenshot({path:path.join(root,'remotion/out/editor-mobile.png'),fullPage:true});
 await page.setViewportSize({width:1280,height:900});await page.screenshot({path:path.join(root,'remotion/out/editor-desktop.png'),fullPage:true});
 // Invalid nested structures stay repairable and complete.
 await page.locator('#import-file').setInputFiles({name:'broken.json',mimeType:'application/json',buffer:Buffer.from('{"title":"Broken","scenes":[null],"direction":{"scenes":[null]},"custom":42}')});
 await page.getByRole('button',{name:'JSON avancé',exact:true}).click().catch(()=>{});
 await page.locator('#advanced-json').waitFor();assert.equal(JSON.parse(await page.locator('#advanced-json').inputValue()).custom,42);
 await page.getByRole('button',{name:'Modèle Voyageur',exact:true}).click().catch(async()=>page.getByRole('button',{name:'Charger le modèle Voyageur',exact:true}).click());
 await page.evaluate(()=>{Storage.prototype.setItem=()=>{throw new DOMException('quota','QuotaExceededError');};});
 await page.getByRole('button',{name:'Enregistrer',exact:true}).click();assert.match(await page.locator('#toast').textContent(),/indisponible ou pleine/);
 assert.deepEqual(errors,[]);console.log('PASS: 4 viewports, import/export payloads (download click mocked), unknown fields, XSS text, storage/reload, invalid draft, plans, durations; no page errors.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
