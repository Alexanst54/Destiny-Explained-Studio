const {chromium}=require('../remotion/node_modules/playwright-core');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:393,height:851},isMobile:true,hasTouch:true});
 await context.addInitScript(()=>{const create=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{window.__exported=b;return create(b);};document.addEventListener('click',e=>{if(e.target.closest?.('a[download]'))e.preventDefault();},true);});
 const page=await context.newPage(),errors=[];page.setDefaultTimeout(8000);page.on('pageerror',e=>errors.push(e.message));
 await context.route('**/*',async r=>{const url=new URL(r.request().url());assert.equal(url.origin,'https://editor.test');const rel=url.pathname.slice(1)||'index.html';if(rel==='favicon.ico'){await r.fulfill({status:204,body:''});return;}assert.ok(!rel.includes('..'));await r.fulfill({body:await fs.readFile(path.join(root,'docs',rel)),contentType:rel.endsWith('.js')?'text/javascript':rel.endsWith('.css')?'text/css':'text/html'});});
 await page.goto('https://editor.test/');await page.getByRole('button',{name:'Démo Europe',exact:true}).click();
 await page.locator('#characters-tab').click();await page.locator('#character-search').waitFor();
 for(const width of [320,360,393,1280]){await page.setViewportSize({width,height:851});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'characters overflow '+width);}
 await page.setViewportSize({width:393,height:851});
 await page.locator('#character-search').fill('Cayde');const card=page.locator('[data-character-id="cayde-6"]');await card.locator('summary').click();await card.getByRole('button',{name:'Ajouter à la scène',exact:true}).click();
 assert.equal(await page.locator('.cast-card').count(),2);const cast=page.locator('.cast-card').last();await cast.getByLabel('Animation du personnage',{exact:true}).selectOption('salute');
 await page.getByRole('button',{name:'← Épisode',exact:true}).click();await page.locator('#weather-tab').click();
 for(const width of [320,360,393,1280]){await page.setViewportSize({width,height:851});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'weather overflow '+width);}
 await page.setViewportSize({width:393,height:851});await page.getByLabel('Intensité météo',{exact:true}).fill('0.6');await page.getByLabel('Intensité météo',{exact:true}).blur();
 await page.getByLabel('Évolution vers',{exact:true}).selectOption('rain');
 assert.match(await page.locator('#validation-region').textContent(),/Météo rain inhabituelle/);
 await fs.mkdir(path.join(root,'remotion/out'),{recursive:true});await page.screenshot({path:path.join(root,'remotion/out/living-weather-mobile.png'),fullPage:true});
 await page.getByRole('button',{name:'← Épisode',exact:true}).click();await page.getByRole('button',{name:'Enregistrer',exact:true}).click();await page.reload();await page.locator('#episode-title').waitFor();
 await page.locator('#export-render').click();await page.waitForFunction(()=>window.__exported instanceof Blob);const e=await page.evaluate(async()=>JSON.parse(await window.__exported.text()));assert.equal(e.schemaVersion,'0.4.0');assert.equal(e.scenes[0].livingWorld.cast[1].animation,'salute');assert.equal(e.scenes[0].weather.intensity,.6);assert.equal(e.scenes[0].weather.to.type,'rain');assert.equal(e.scenes[0].livingWorld.groups[0].count,8);
 await page.locator('#characters-tab').click();await page.screenshot({path:path.join(root,'remotion/out/living-characters-mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);await browser.close();console.log('PASS Living Worlds: touch, 4 widths, search, add cast, animation, weather transition, warning, save/reload, renderer export.');
})().catch(e=>{console.error(e);process.exit(1);});
