const {chromium}=require('../remotion/node_modules/playwright-core');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const context=await browser.newContext({viewport:{width:393,height:851},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
 await context.addInitScript(()=>{const create=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{window.__exported=b;return create(b);};document.addEventListener('click',e=>{if(e.target.closest?.('a[download]'))e.preventDefault();},true);});
 const page=await context.newPage(),errors=[];page.setDefaultTimeout(15000);page.on('pageerror',e=>errors.push(e.message));
 await context.route('**/*',async route=>{const url=new URL(route.request().url());assert.equal(url.origin,'https://editor.test');const rel=url.pathname.replace('/Destiny-Explained-Studio/','').replace(/^\//,'')||'index.html';if(rel==='favicon.ico'){await route.fulfill({status:204,body:''});return;}assert.ok(!rel.includes('..'));await route.fulfill({body:await fs.readFile(path.join(root,'docs',rel)),contentType:rel.endsWith('.js')?'text/javascript':rel.endsWith('.css')?'text/css':'text/html'});});
 await page.goto('https://editor.test/Destiny-Explained-Studio/');await page.getByRole('button',{name:'Ouvrir la démo Riis',exact:true}).click();
 for(const width of [320,360,393,1280]){await page.setViewportSize({width,height:851});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'storyboard overflow '+width);}
 await page.setViewportSize({width:393,height:851});assert.equal(await page.getByRole('navigation',{name:'Plans du storyboard'}).getByRole('button').count(),5);
 await page.getByRole('button',{name:'Dupliquer le plan',exact:true}).click();assert.equal(await page.getByRole('navigation',{name:'Plans du storyboard'}).getByRole('button').count(),6);
 await page.getByRole('button',{name:'Descendre le plan',exact:true}).click();await page.getByRole('button',{name:'Monter le plan',exact:true}).click();
 page.once('dialog',d=>d.accept());await page.getByRole('button',{name:'Supprimer le plan',exact:true}).click();
 await page.getByRole('navigation',{name:'Plans du storyboard'}).getByRole('button').nth(2).click();
 await page.getByLabel('Étiquette du lieu',{exact:true}).first().fill('Riis — schematic');await page.getByLabel('Étiquette du lieu',{exact:true}).first().blur();
 await page.getByLabel('Style des sous-titres',{exact:true}).selectOption('clean-documentary');
 await page.getByRole('button',{name:'Charger l’aperçu',exact:true}).click();await page.locator('#hybrid-preview video, #hybrid-preview [data-caption-fallback], #hybrid-preview svg').first().waitFor({timeout:30000});
 for(const width of [320,360,393,1280]){await page.setViewportSize({width,height:851});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'preview overflow '+width);}
 await fs.mkdir(path.join(root,'remotion/out'),{recursive:true});await page.screenshot({path:path.join(root,'remotion/out/hybrid-editor-mobile.png'),fullPage:true});
 await page.getByRole('button',{name:'Enregistrer le Short',exact:true}).click();await page.reload();await page.locator('#storyboard-tab').click();
 await page.getByRole('button',{name:'Copie Short pour rendu',exact:true}).click();await page.waitForFunction(()=>window.__exported instanceof Blob);const e=await page.evaluate(async()=>JSON.parse(await window.__exported.text()));assert.equal(e.scenes.length,5);assert.equal(e.scenes[2].visual.nodes[0].label,'Riis — schematic');assert.equal(e.shorts.captions.style,'clean-documentary');assert.equal(e.format.durationFrames,1050);assert.equal(e.render.composition,'HybridShort');
 // Real caption DOM at 320 px: complete timing and long tokens in all three styles.
 await page.setViewportSize({width:320,height:851});
 for(const style of ['clean-documentary','dynamic-shorts','cinematic-minimal']){
  const long=structuredClone(e);long.shorts.captions.style=style;long.scenes[0].narration='W'.repeat(100)+' continues.';
  long.shorts.alignedWords=long.scenes.flatMap(s=>{const tokens=s.narration.split(/\s+/),step=s.durationFrames/30/tokens.length;return tokens.map((text,i)=>({text,start:s.startFrame/30+i*step,end:s.startFrame/30+(i+1)*step}));});
  await page.locator('#import-file').setInputFiles({name:'long.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(long))});
  await page.getByRole('button',{name:'Charger l’aperçu',exact:true}).click();const caption=page.locator('[data-caption-style="'+style+'"]');await caption.waitFor();
  assert.ok(await caption.evaluate(el=>el.scrollWidth<=el.clientWidth+1),'long caption overflow '+style);
  assert.equal(await page.locator('[data-caption-fallback]').count(),0);
 }
 assert.deepEqual(errors,[]);await browser.close();console.log('PASS Hybrid: touch storyboard, reorder/duplicate/delete, content, captions, shared preview, persistence/export, four widths, reduced motion, no page errors.');
})().catch(e=>{console.error(e);process.exit(1);});
