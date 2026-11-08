const {chromium}=require('../remotion/node_modules/playwright-core');
const http=require('node:http'),fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const root=path.resolve(__dirname,'../docs');
 const server=http.createServer(async(req,res)=>{try{const name=new URL(req.url,'http://localhost').pathname;const file=path.resolve(root,'.'+(name==='/'?'/index.html':name));if(!file.startsWith(root+path.sep))throw new Error('path');res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(await fs.readFile(file));}catch{res.statusCode=404;res.end('missing');}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  const context=await browser.newContext(),page=await context.newPage();page.setDefaultTimeout(10000);
  await page.goto('http://127.0.0.1:'+server.address().port);await page.locator('#episode-title').waitFor();
  await page.evaluate(()=>navigator.serviceWorker.ready);await page.waitForFunction(()=>!!navigator.serviceWorker.controller);
  await page.getByRole('button',{name:'Démo Fundament',exact:true}).click();await page.getByRole('button',{name:'Enregistrer',exact:true}).click();
  await context.setOffline(true);await page.reload();await page.locator('#episode-title').waitFor();assert.match(await page.locator('#episode-title').inputValue(),/Fundament/);
  await page.locator('#characters-tab').click();await page.locator('#character-search').fill('aurash');assert.equal(await page.locator('[data-character-id="aurash"]').count(),1);
  console.log('PASS: cached static editor reloads offline with saved scene and searchable character catalog.');
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exit(1);});
