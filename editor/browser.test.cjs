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
  assert.ok(!rel.includes('..'));if(rel.replace(/^\//,'')==='favicon.ico'){await route.fulfill({status:204,body:''});return;}
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
 await page.locator('#scene-location').selectOption('europa');
 const sceneElements=page.locator('.voxel-elements').first();
 await sceneElements.locator(':scope > summary').click();
 await sceneElements.getByRole('button',{name:'+ Ajouter un élément',exact:true}).click();
 await sceneElements.getByLabel('Type d’élément',{exact:true}).selectOption('snow');
 await sceneElements.getByLabel('Animation de l’élément',{exact:true}).selectOption('blizzard');
 await sceneElements.getByLabel('Nombre de particules',{exact:true}).fill('48');
 await sceneElements.getByLabel('Nombre de particules',{exact:true}).blur();
 const worlds=await downloaded('#export-render');assert.equal(worlds.scenes[0].location,'europa');assert.ok(worlds.environments.some(e=>e.id==='europa'));assert.equal(worlds.scenes[0].elements[0].type,'snow');assert.equal(worlds.scenes[0].elements[0].count,48);assert.equal(worlds.direction.scenes[0].shots[0].environment,'scene');
 const activeShot=page.locator('.plan-card[open]').last();
 await activeShot.getByLabel('Décor du plan',{exact:true}).selectOption('black-garden');
 const override=await downloaded('#export-render');assert.equal(override.direction.scenes[0].shots[1].environment,'black-garden');assert.ok(override.environments.some(e=>e.id==='black-garden'));assert.equal(override.scenes[0].location,'europa');
 const shotElements=page.locator('.plan-card[open]').last().locator('.voxel-elements');
 await shotElements.locator(':scope > summary').click();
 await shotElements.getByLabel('Source des éléments',{exact:true}).selectOption('custom');
 await shotElements.getByRole('button',{name:'Supprimer cet élément',exact:true}).click();
 const noElements=await downloaded('#export-render');assert.deepEqual(noElements.direction.scenes[0].shots[1].elements,[]);assert.equal(noElements.scenes[0].elements.length,1);
 await shotElements.getByLabel('Source des éléments',{exact:true}).selectOption('scene');
 const inherited=await downloaded('#export-render');assert.equal('elements' in inherited.direction.scenes[0].shots[1],false);assert.equal(inherited.scenes[0].elements[0].count,48);
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await fs.mkdir(path.join(root,'remotion/out'),{recursive:true});await page.screenshot({path:path.join(root,'remotion/out/editor-mobile.png'),fullPage:true});
 await page.setViewportSize({width:1280,height:900});await page.screenshot({path:path.join(root,'remotion/out/editor-desktop.png'),fullPage:true});
 // Atlas is a real mobile tab: filters, variants, scene/shot assignment and persistence.
 await page.locator('#atlas-tab').click();await page.locator('#atlas-search').waitFor();
 for(const width of [320,360,393,1280]){await page.setViewportSize({width,height:851});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Atlas overflow at ${width}`);}
 await page.setViewportSize({width:393,height:851});
 await page.locator('#atlas-search').fill('riis');
 const riis=page.locator('[data-place-id="riis"]');await riis.waitFor();
 await riis.getByLabel('Variante historique',{exact:true}).selectOption('before-whirlwind');
 await riis.getByRole('button',{name:'Utiliser pour la scène',exact:true}).click();
 await page.locator('#atlas-search').fill('Fundament');const fundament=page.locator('[data-place-id="fundament"]');await fundament.waitFor();
 await fundament.getByLabel('Variante historique',{exact:true}).selectOption('krill-origins');
 await fundament.getByRole('button',{name:'Utiliser pour le plan',exact:true}).click();
 await page.locator('#atlas-search').fill('');await page.locator('#atlas-parent').selectOption('europa-regions');
 assert.ok((await page.locator('#atlas-count').textContent()).includes('résultat'));
 assert.ok(await page.locator('.atlas-card').count()>0);
 await page.locator('#atlas-parent').selectOption('');await page.locator('#atlas-category').selectOption('lore-world');await page.locator('#atlas-civilization').selectOption('eliksni');
 assert.equal(await page.locator('.atlas-card').count(),1);assert.equal(await page.locator('[data-place-id="riis"]').count(),1);
 await page.locator('[data-place-id="riis"] summary').click();
 const sourceLinks=await page.locator('[data-place-id="riis"] a').evaluateAll(links=>links.map(a=>a.href));assert.ok(sourceLinks.length);assert.ok(sourceLinks.every(url=>url.startsWith('https://')));
 await page.screenshot({path:path.join(root,'remotion/out/atlas-editor-mobile.png'),fullPage:true});
 await page.getByRole('button',{name:'← Épisode',exact:true}).first().click();
 await page.getByRole('button',{name:'Enregistrer',exact:true}).click();await page.reload();await page.locator('#episode-title').waitFor();
 const selected=await downloaded('#export-render');assert.equal(selected.schemaVersion,'0.3.0');assert.deepEqual(selected.scenes[0].atlas,{locationId:'riis',variantId:'before-whirlwind'});assert.deepEqual(selected.direction.scenes[0].shots[1].atlas,{locationId:'fundament',variantId:'krill-origins'});
 assert.equal(selected.scenes[0].elements[0].count,48); // Previously edited fields survive Atlas changes.
 // Invalid nested structures stay repairable and complete.
 await page.locator('#import-file').setInputFiles({name:'broken.json',mimeType:'application/json',buffer:Buffer.from('{"title":"Broken","scenes":[null],"direction":{"scenes":[null]},"custom":42}')});
 await page.getByRole('button',{name:'JSON avancé',exact:true}).click().catch(()=>{});
 await page.locator('#advanced-json').waitFor();assert.equal(JSON.parse(await page.locator('#advanced-json').inputValue()).custom,42);
 await page.getByRole('button',{name:'Modèle Voyageur',exact:true}).click().catch(async()=>page.getByRole('button',{name:'Charger le modèle Voyageur',exact:true}).click());
 await page.evaluate(()=>{Storage.prototype.setItem=()=>{throw new DOMException('quota','QuotaExceededError');};});
 await page.getByRole('button',{name:'Enregistrer',exact:true}).click();assert.match(await page.locator('#toast').textContent(),/indisponible ou pleine/);
 assert.deepEqual(errors,[]);console.log('PASS: 4 viewports, import/export payloads (download click mocked), unknown fields, XSS text, storage/reload, invalid draft, plans, durations, library scene/shot selection, element editing, Atlas filters/variants/scene+shot selection/persistence; no page errors.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
