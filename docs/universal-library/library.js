const el=id=>document.getElementById(id);
const node=(tag,text,parent)=>{const n=document.createElement(tag);n.textContent=text;parent?.append(n);return n;};
try {
 const response=await fetch('./catalog.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=await response.json();
 const activities=new Map(data.activities.map(a=>[a.id,a]));const encounters=new Map(data.encounters.map(a=>[a.id,a]));const locations=new Map(data.locations.map(a=>[a.id,a]));const sources=new Map(data.sources.map(a=>[a.id,a]));
 for(const a of data.activities) {const o=node('option',`${a.frName} (${a.game})`);o.value=a.id;el('activity').append(o);}
 for(const a of data.destinations??[]) {const o=node('option',a.frName);o.value=a.id;el('destination').append(o);}
 el('summary').textContent=`${data.entities.length} entrées Atlas (identités, formes et lieux), ${data.entities.filter(e=>e.implementation).length} implémentations enregistrées. Priorités absentes du catalogue : ${data.unlistedPriorities.join(', ')||'aucune'}.`;
 function draw(){
  const q=el('search').value.toLocaleLowerCase();const state=el('status').value;const activity=el('activity').value;const kind=el('kind').value;const destination=el('destination').value;
  const items=data.entities.filter(e=>(!q||`${e.id} ${e.name} ${e.enName}`.toLocaleLowerCase().includes(q))&&(!state||e.status.includes(state))&&(!activity||e.activityIds.includes(activity))&&(!kind||e.kind===kind)&&(!destination||e.destinationIds.includes(destination)));el('cards').replaceChildren();
  for(const e of items){const card=node('article','',el('cards'));node('h2',e.name,card);node('small',e.id,card);node('p',`${({'implemented-user-approved':'Modèle validé','implemented':'Générateur disponible','partial-dedicated-prototype':'Prototype dédié partiel','missing':'Manquant'})[e.status]??e.status} · ${e.kind} · ${e.composition??e.nature??e.family}`,card).className='status';
   for(const preview of e.previews){const a=node('a','',card);a.href='../'+preview.path.replace(/^docs\//,'');const img=document.createElement('img');img.src=a.href;img.alt=`${e.name} — rendu Blender ${preview.quality}`;img.loading='lazy';a.append(img);}
   node('p',`Familles candidates : ${e.familyCandidates.join(', ')||'non résolues'}`,card);node('p',`Animations : ${e.implementation?.animations.join(', ')||'aucune implémentée'}`,card);node('p',`Variantes : ${e.variants.join(', ')||'aucune documentée'}`,card);
   const details=node('details','',card);node('summary','Activités, rencontres, lieux et sources',details);const list=node('ul','',details);
   for(const id of e.activityIds)node('li',activities.get(id)?.frName??id,list);for(const id of e.encounterIds)node('li',encounters.get(id)?.frName??id,list);for(const id of e.arenaIds)node('li',locations.get(id)?.frName??id,list);
   for(const id of e.sourceIds){const s=sources.get(id);if(s){const a=node('a',s.title,node('li','',list));a.href=s.url;a.rel='noopener';a.target='_blank';}}
   if(e.implementation){const gallery=node('a','Galerie et rapport technique',card);gallery.href='../'+e.implementation.gallery.replace(/^docs\//,'');node('code',`python remotion/blender/render_universal.py ${e.id} work/${e.id} --lod 0 --view environment`,card);const b=node('button','Exporter la sélection JSON',card);b.onclick=()=>{const blob=new Blob([JSON.stringify({selectionId:e.id,lod:0,quality:'balanced',view:'environment'},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=e.id+'-selection.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};}
   else node('p',e.kind==='environment'?'Étude de famille possible seulement sur demande explicite ; arène spécifique manquante.':'Aucun modèle dédié ; génération générique bloquée.',card);
  }
 }
 for(const id of ['search','status','activity','destination','kind'])el(id).addEventListener('input',draw);draw();
}catch(error){el('error').textContent=`Impossible de charger le catalogue : ${error.message}. Servir le dépôt avec python -m http.server 8000 puis ouvrir /docs/universal-library/.`;}
