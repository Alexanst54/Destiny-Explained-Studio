import {newHybridProject,templateLabels} from '../remotion/hybrid/templates.ts';
import {sceneTypes,transitionTypes,captionStyles} from '../remotion/hybrid/schema.ts';
import {pacing,captionTiming,sourceUrl,sourceTitle} from '../remotion/hybrid/state.ts';
import {validateWords} from '../remotion/src/voxel/episode/schema.ts';
import {addStoryboard,duplicateStoryboard,setStoryboardType,resizeStoryboard} from './hybrid-model.mjs';
import hybridRiis from '../remotion/episodes/hybrid_riis.json' with {type:'json'};
import hybridOryx from '../remotion/episodes/hybrid_oryx.json' with {type:'json'};
import hybridGarden from '../remotion/episodes/hybrid_black_garden.json' with {type:'json'};
import {characterCatalog,charactersById,searchCharacters} from '../remotion/characters/index.ts';
import {civilizations,animations as livingAnimations} from '../remotion/characters/schema.ts';
import {weatherTypes,weatherPresets} from '../remotion/weather/schema.ts';
import whirlwindDemo from '../remotion/episodes/living_whirlwind.json' with {type:'json'};
import europaDemo from '../remotion/episodes/living_europa.json' with {type:'json'};
import fundamentDemo from '../remotion/episodes/living_fundament.json' with {type:'json'};
import {atlas,locationsById,sourcesById,searchAtlas,resolveAtlas} from '../remotion/atlas/index.ts';
import {categories} from '../remotion/atlas/schema.ts';
import atlasDemo from '../remotion/episodes/atlas_demo.json' with {type:'json'};
import {clone,setAtlasReference,catalog,templateEpisode,demoEpisode,setEnvironment,newElement,removeProperty,newEpisode,parseImport,validateEpisode,compatibleCopy,sceneList,planFor,patch,reflow,invalidateVoice,setDuration,moveScene,addScene,deleteScene,addShot,moveShot,deleteShot,spreadShots,newAction,newEvent,frameCue,phraseCue,shotStart,secondsLabel,slug} from './model.mjs';
let view='episode',atlasTarget='scene';
const atlasFilters={query:'',category:'',civilization:'',era:'',parentId:''};
const atlasVariants=new Map();let atlasLimit=20;
const KEY='destiny-explained-editor-v1';
const $=selector=>document.querySelector(selector);
const list=v=>Array.isArray(v)?v:[];
const record=v=>v&&typeof v==='object'&&!Array.isArray(v);
const labels={'dark-age':'Âge sombre','red-war':'Guerre rouge','pre-invasion':'Avant l’invasion','universe-realm':'Univers, dimensions et royaumes','stellar-body':'Systèmes et astres','destination-region':'Destinations et régions',zone:'Zones et sous-zones','historical-site':'Lieux historiques','activity-site':'Raids, donjons et missions','ship-station':'Vaisseaux et stations','lore-world':'Mondes du lore','historical-variant':'Variantes historiques',human:'Humaine',vex:'Vex',hive:'Ruche',cabal:'Cabale',eliksni:'Éliksni',awoken:'Éveillée',krill:'Krill',lubraean:'Lubraéenne','golden-age':'Âge d’or','city-age':'Âge de la Cité',ancient:'Antiquité','pre-whirlwind':'Avant le Tourbillon','post-whirlwind':'Après le Tourbillon','the-tower':'La Tour et la Dernière Cité',europa:'Europe enneigée','black-garden':'Le Jardin noir','pyramid-interior':'Intérieur de Pyramide',scene:'Décor de la scène',custom:'Liste propre au plan','vex-structure':'Structure vex','light-fragments':'Fragments de Lumière',crystal:'Cristaux',snow:'Neige',still:'Immobile',pulse:'Pulsation lumineuse',drift:'Dérive',blizzard:'Tempête de neige',frame:'Temps dans la scène',phrase:'Mots de narration','wide-tilt-up':'Plan large vers le ciel','slow-orbit-traveler':'Orbite lente du Voyageur','push-in-sky':'Travelling vers le ciel','close-up-ghost':'Gros plan du Spectre','medium-guardian':'Plan moyen du Gardien','wide-pullback':'Recul large',calm:'Calme',balanced:'Équilibrée',cinematic:'Cinématique',tower:'La Tour','golden-age-vision':'Vision de l’Âge d’or','collapse-vision':'Vision de l’Effondrement','light-space':'Espace de Lumière',guardian:'Gardien',ghost:'Spectre',idle:'Repos',walk:'Marche',run:'Course',jump:'Saut',fall:'Chute',resurrect:'Résurrection',combat:'Combat',interact:'Interaction','look-up':'Regard vers le ciel',hover:'Flottement',orbit:'Orbite',scan:'Scan',dolly:'Travelling',zoom:'Zoom',follow:'Suivi', 'close-up':'Gros plan',perspective:'Changement d’angle',particles:'Particules',explosion:'Explosion voxel',hologram:'Hologramme',beam:'Rayon lumineux',shake:'Secousse',cut:'Coupe franche',fade:'Fondu sombre',wipe:'Volet',match:'Raccord de caméra'};
Object.assign(labels,{exo:'Exos',machine:'Machines',cosmic:'Entités cosmiques',taken:'Corrompus',scorn:'Infâmes','witness-precursors':'Précurseurs (forme inconnue)',clear:'Temps clair',clouds:'Nuages',rain:'Pluie',thunderstorm:'Orage',fog:'Brouillard',sandstorm:'Tempête de sable','strong-wind':'Vent violent',spores:'Spores atmosphériques',energy:'Particules d’énergie',supernatural:'Atmosphère surnaturelle',flee:'Fuite',look:'Regard',salute:'Salut',talk:'Discussion',observe:'Observation',kneel:'Agenouillement',attack:'Attaque',hit:'Impact',terminal:'Utiliser un terminal',appear:'Apparition',disappear:'Disparition',grid:'Grille',line:'Ligne',scatter:'Dispersion',canonical:'Canon (illustration stylisée)',reconstruction:'Reconstitution artistique','alternate-history':'Histoire alternative — non canon',default:'Apparence de référence'});
Object.assign(labels,templateLabels,{voxel:'Cinématique voxel',map:'Carte animée',timeline:'Frise chronologique',graphic:'Graphique explicatif',text:'Texte cinématique',slide:'Glissement',flash:'Flash léger',hypothesis:'Hypothèse — non canon',documented:'Documenté',partial:'Partiel',unknown:'Inconnu','clean-documentary':'Clean Documentary','dynamic-shorts':'Dynamic Shorts','cinematic-minimal':'Cinematic Minimal',hook:'Hook',quote:'Citation',question:'Question',reveal:'Révélation',conclusion:'Conclusion',effect:'Bruitage',ambience:'Ambiance',music:'Musique'});
Object.assign(labels,Object.fromEntries([...atlas.sources,...characterCatalog.sources].map(s=>[s.id,s.title])));
const friendly=v=>labels[v]??v;
function node(tag,attrs={},...children){
 const e=document.createElement(tag);
 for(const [key,value]of Object.entries(attrs)){
  if(key.startsWith('on'))e.addEventListener(key.slice(2).toLowerCase(),value);
  else if(key==='class')e.className=value;
  else if(key==='text')e.textContent=value;
  else if(key in e&&!key.startsWith('aria-'))e[key]=value;
  else e.setAttribute(key,String(value));
 }
 for(const c of children.flat(Infinity)){if(c===null||c===undefined||c===false)continue;e.append(c instanceof Node?c:document.createTextNode(String(c)));}
 return e;
}
const button=(text,click,attrs={})=>node('button',{type:'button',onClick:click,...attrs},text);
const small=text=>node('p',{class:'hint'},text);
let library=[],active='',episode,rawDraft='',mode='beginner',sceneIndex=0,shotIndex=0,tab='shots',undo=[],redo=[],saveTimer,validateTimer,lastFocused,storageError='';
let toastTimer,historyTick=0;
const rawDirty=()=>mode==='advanced'&&rawDraft!==JSON.stringify(episode,null,2);
function commitControl(fn,value){const before=clone(episode),tick=historyTick;fn(value);if(tick===historyTick&&JSON.stringify(before)!==JSON.stringify(episode))history(before);refresh();}
function toast(message){const e=$('#toast');e.hidden=false;e.textContent=message;clearTimeout(toastTimer);toastTimer=setTimeout(()=>e.hidden=true,5000);}
function current(){return library.find(p=>p.key===active);}
function save(){
 clearTimeout(saveTimer);
 const p=current();if(!p)return;
 p.episode=clone(episode);p.rawDraft=rawDraft;p.mode=mode;p.updatedAt=new Date().toISOString();
 try{localStorage.setItem(KEY,JSON.stringify({version:1,active,projects:library}));storageError='';}
 catch{storageError='Sauvegarde locale indisponible ou pleine. Exportez votre JSON pour le conserver.';}
 const status=$('#save-status');if(status)status.textContent=storageError||`Enregistré à ${new Date().toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'})}`;
 if(status)status.classList.toggle('error-text',Boolean(storageError));
}
const scheduleSave=()=>{clearTimeout(saveTimer);saveTimer=setTimeout(save,250);const s=$('#save-status');if(s)s.textContent='Enregistrement…';};
function history(before){historyTick++;undo.push(before);if(undo.length>30)undo.shift();redo=[];}
function replace(next,{structural=true,message='',remember=true}={}){
 if(remember)history(clone(episode));episode=next;
 rawDraft=JSON.stringify(episode,null,2);scheduleSave();
 if(structural)render();else refresh();if(message)toast(message);
}
function edit(next){episode=next;rawDraft=JSON.stringify(episode,null,2);scheduleSave();clearTimeout(validateTimer);validateTimer=setTimeout(refresh,180);}
function createProject(raw,name){
 save();if(raw.shorts){view='storyboard';storyboardIndex=0;}else view='episode';const key=slug('projet');library.push({key,episode:clone(raw),rawDraft:JSON.stringify(raw,null,2),mode:'beginner',updatedAt:new Date().toISOString()});
 active=key;episode=clone(raw);rawDraft=JSON.stringify(raw,null,2);mode='beginner';sceneIndex=0;shotIndex=0;undo=[];redo=[];save();render();if(name)toast(name);
}
function switchProject(key){save();const p=library.find(p=>p.key===key);if(!p)return;active=key;episode=clone(p.episode);rawDraft=p.rawDraft??JSON.stringify(episode,null,2);mode=p.mode??'beginner';sceneIndex=0;shotIndex=0;undo=[];redo=[];save();render();}
function snapshotInput(input){input.addEventListener('focus',()=>{lastFocused=clone(episode);});input.addEventListener('change',()=>{if(lastFocused&&JSON.stringify(lastFocused)!==JSON.stringify(episode))history(lastFocused);lastFocused=null;refresh();});}
function textField(title,value,change,{area=false,id,help,rows=3}={}){
 const input=node(area?'textarea':'input',{id:id??slug('champ'),value:typeof value==='string'?value:'',...(area?{rows}:{type:'text'}),onInput:e=>change(e.target.value)});
 snapshotInput(input);return node('label',{class:'field',htmlFor:input.id},node('span',{},title),input,help?small(help):null);
}
function numberField(title,value,change,{min,max,step='any',id,help}={}){
 const input=node('input',{id:id??slug('nombre'),type:'number',inputMode:'decimal',step,value:Number.isFinite(value)?value:'',...(min!==undefined?{min}:{}),...(max!==undefined?{max}:{}),onInput:e=>change(e.target.value===''?null:Number(e.target.value))});
 snapshotInput(input);return node('label',{class:'field',htmlFor:input.id},node('span',{},title),input,help?small(help):null);
}
function selectField(title,value,options,change,id){
 const select=node('select',{'aria-label':title,id:id??slug('choix'),onChange:e=>commitControl(change,e.target.value)});
 if(!options.includes(value))select.append(node('option',{value:typeof value==='string'?value:'',selected:true,disabled:true},value?`Non reconnu : ${String(value)}`:'À renseigner'));
 for(const option of options)select.append(node('option',{value:option,selected:option===value},friendly(option)));
 return node('label',{class:'field',htmlFor:select.id},node('span',{},title),select);
}
function checkbox(title,value,change){return node('label',{class:'check'},node('input',{type:'checkbox',checked:value===true,onChange:e=>commitControl(change,e.target.checked)}),title);}
function changeField(path,value,{dirty=false,full=false}={}){let next=patch(episode,path,value);if(dirty)invalidateVoice(next);if(full)replace(next);else edit(next);}
function actionTools(up,down,remove,disableUp,disableDown,disableRemove=false){return node('div',{class:'item-tools'},button('↑',up,{'aria-label':'Monter',disabled:disableUp}),button('↓',down,{'aria-label':'Descendre',disabled:disableDown}),button('Supprimer',remove,{class:'danger-quiet',disabled:disableRemove}));}
function directionIndex(){return list(episode.direction?.scenes).findIndex(p=>p?.sceneId===sceneList(episode)[sceneIndex]?.id);}
function timeline(){
 const scenes=sceneList(episode),total=Number(episode.format?.durationFrames)||1,w=Math.max(650,scenes.length*140),svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
 svg.setAttribute('viewBox',`0 0 ${w} 78`);svg.setAttribute('width',String(w));svg.setAttribute('height','78');svg.setAttribute('role','img');svg.setAttribute('aria-label','Chronologie des scènes');
 scenes.forEach((s,i)=>{
  const x=(Number(s?.startFrame)||0)/total*w,width=Math.max(4,(Number(s?.durationFrames)||0)/total*w);
  const r=document.createElementNS(svg.namespaceURI,'rect');r.setAttribute('x',String(x+2));r.setAttribute('y','7');r.setAttribute('width',String(Math.max(2,width-4)));r.setAttribute('height','64');r.setAttribute('rx','8');r.setAttribute('class',i===sceneIndex?'bar active':'bar');
  const title=document.createElementNS(svg.namespaceURI,'title');title.textContent=`Scène ${i+1} · ${secondsLabel(s?.startFrame)} → ${secondsLabel((s?.startFrame??0)+(s?.durationFrames??0))}`;r.append(title);r.addEventListener('click',()=>{sceneIndex=i;shotIndex=0;render();});svg.append(r);
  if(width>65)for(const [text,y]of [[`Scène ${i+1}`,32],[secondsLabel(s?.startFrame),54]]){const t=document.createElementNS(svg.namespaceURI,'text');t.setAttribute('x',String(x+12));t.setAttribute('y',String(y));t.setAttribute('class','timeline-text');t.textContent=text;svg.append(t);}
 });
 return node('div',{class:'timeline-scroll'},svg);
}
function shotTimeline(s,p){
 return node('div',{class:'shot-timeline'},...list(p?.shots).map((shot,i)=>{
  const start=record(shot)?shotStart(episode,s,shot):null,next=p.shots[i+1],end=next&&record(next)?shotStart(episode,s,next):s.durationFrames;
  return button([node('span',{class:'eyebrow'},`PLAN ${i+1}`),node('strong',{},start===null?'Ancrage à corriger':secondsLabel(start)),node('small',{},end===null?'?':`→ ${secondsLabel(end)}`)],()=>{shotIndex=i;render();},{class:i===shotIndex?'shot-marker selected':'shot-marker','aria-pressed':i===shotIndex});
 }));
}
function validationBox(){
 let result;try{result=validateEpisode(episode);}catch(error){result={valid:false,strict:false,unknown:[],errors:[{path:'JSON',message:error.message}],warnings:[]};}
 const summary=result.valid?(result.unknown.length?'Structure compatible · champs supplémentaires conservés':'Structure compatible avec le moteur'):'À corriger avant le rendu';
 const box=node('section',{class:result.valid?'validation valid':'validation invalid','aria-label':'Validation'},node('div',{class:'section-heading'},node('strong',{},result.valid?'✓ '+summary:'! '+summary),node('span',{class:'pill'},result.errors.length?`${result.errors.length} erreur(s)`:'JSON')));
 if(result.errors.length)box.append(node('ul',{class:'error-list'},...result.errors.slice(0,15).map(e=>node('li',{},node('code',{},e.path||'épisode'),' — ',translate(e.message)))));
 for(const warning of result.warnings)box.append(small(warning));
 if(result.unknown.length)box.append(node('details',{},node('summary',{},'Voir les champs non reconnus (jamais supprimés du projet)'),node('ul',{},...result.unknown.slice(0,30).map(path=>node('li',{},node('code',{},path))))));
 box.append(small('La voix, sa durée réelle et les ancrages vocaux seront vérifiés après génération dans Colab.'));
 return box;
}
function translate(message){return message.replace('Voiceover is pending: preview is silent.','Voix en attente : aperçu silencieux.').replace('Word alignment is pending: preview captions use estimated timing.','Sous-titres en attente : minutage estimé dans l’aperçu.').replace('Narration cue not found','Ancrage vocal introuvable').replace('narration cue not found','Ancrage vocal introuvable').replace('cue outside scene','Le début sort de la scène').replace('effect exceeds scene','L’effet dépasse la scène').replace('action exceeds scene','L’animation dépasse la scène').replace('shots must be ordered and at least 12 frames long','Les plans doivent être ordonnés et durer au moins 12 images').replace('first shot must begin at scene start','Le premier plan doit commencer à zéro').replace('transition too long','La transition est trop longue').replace('tracking an invisible actor','Le suivi vise un personnage invisible').replace('Duplicate direction id','Identifiant dupliqué').replace('camera path crosses its target','La caméra traverse son point visé').replace('overlapping guardian actions','Des animations du Gardien se chevauchent').replace('overlapping ghost actions','Des animations du Spectre se chevauchent');}
function refresh(){
 const ub=$('#undo-button'),rb=$('#redo-button');if(ub)ub.disabled=!undo.length;if(rb)rb.disabled=!redo.length;
 const v=$('#validation-region');if(v)v.replaceChildren(validationBox());
 const t=$('#timeline-region');if(t)t.replaceChildren(timeline());
 const stat=$('#episode-stat');if(stat)stat.textContent=`${sceneList(episode).length} scènes · ${secondsLabel(episode.format?.durationFrames)} · 1080 × 1920`;
 const heading=$('#project-heading');if(heading)heading.textContent=typeof episode.title==='string'?episode.title:'Épisode sans titre';
 const durationLabel=$('#scene-duration-label');if(durationLabel)durationLabel.textContent=secondsLabel(sceneList(episode)[sceneIndex]?.durationFrames);
 document.querySelectorAll('.scene-button').forEach((button,i)=>{const s=sceneList(episode)[i];button.querySelector('strong').textContent=typeof s?.narration==='string'?s.narration.slice(0,65):'À renseigner';button.querySelector('small').textContent=secondsLabel(s?.durationFrames);});
 const scene=sceneList(episode)[sceneIndex],region=$('#shot-timeline-region');if(region&&scene)region.replaceChildren(shotTimeline(scene,planFor(episode,scene.id)));
}
function cueFields(item,path){
 const at=record(item.at)?item.at:{},voice='phrase'in at;
 return node('div',{class:'cue-fields'},selectField('Début',voice?'phrase':'frame',['frame','phrase'],kind=>{
  const value=kind==='frame'?frameCue(at,0):phraseCue(at,'');changeField([...path,'at'],value,{full:true});
 }),voice?textField('Phrase de narration',at.phrase,v=>changeField([...path,'at','phrase'],v),{help:'Mots consécutifs en anglais, présents dans cette scène.'}):numberField('Début dans la scène (s)',Number(at.sceneFrame)/30,v=>changeField([...path,'at','sceneFrame'],v===null?null:Math.round(v*30)),{min:0,step:0.1}),voice?node('div',{class:'two-col'},numberField('Occurrence',at.occurrence??1,v=>changeField([...path,'at','occurrence'],v),{min:1,step:1}),numberField('Décalage (images)',at.offsetFrames??0,v=>changeField([...path,'at','offsetFrames'],v),{min:-90,max:90,step:1})):null);
}
function vectorFields(title,value,path){return node('fieldset',{class:'vector'},node('legend',{},title),node('div',{class:'three-col'},...['X','Y','Z'].map((axis,i)=>numberField(axis,Array.isArray(value)?value[i]:null,v=>changeField([...path,i],v),{step:0.1}))));}
function shotCard(s,p,item,index){
 if(!record(item))return node('div',{class:'card'},'Plan illisible : utilisez le mode JSON avancé.');
 const pi=directionIndex(),path=['direction','scenes',pi,'shots',index];
 const card=node('details',{class:'plan-card',open:index===shotIndex});
 card.append(node('summary',{},node('span',{class:'number-badge'},String(index+1).padStart(2,'0')),node('span',{},node('strong',{},friendly(item.camera?.mode??'Plan')),node('small',{},typeof item.purpose==='string'?item.purpose:'Intention à renseigner'))));
 card.addEventListener('toggle',()=>{if(card.open)shotIndex=index;});
 card.append(node('div',{class:'plan-body'},
  textField('Intention narrative',item.purpose,v=>changeField([...path,'purpose'],v),{help:'Quel élément de l’histoire ce plan aide-t-il à comprendre ?'}),
  cueFields(item,path),
  node('div',{class:'two-col'},selectField('Décor du plan',item.environment,catalog.environments,v=>replace(setEnvironment(episode,[...path,'environment'],v))),selectField('Caméra',item.camera?.mode,catalog.cameras,v=>{
   let e=patch(episode,[...path,'camera','mode'],v);const c=e.direction.scenes[pi].shots[index].camera;
   if(v==='orbit'){c.angleFrom??=-.15;c.angleTo??=.15;}if(v==='follow')c.track??=item.actors?.guardian?'guardian':'ghost';replace(e);
  })),
  node('fieldset',{},node('legend',{},'Personnages visibles'),node('div',{class:'checks'},checkbox('Gardien',item.actors?.guardian,v=>changeField([...path,'actors','guardian'],v)),checkbox('Spectre',item.actors?.ghost,v=>changeField([...path,'actors','ghost'],v)))),
  node('div',{class:'two-col'},selectField('Transition entrante',item.transition?.type,catalog.transitions,v=>{
   let e=patch(episode,[...path,'transition','type'],v);e=patch(e,[...path,'transition','durationFrames'],v==='cut'?0:Math.max(6,item.transition?.durationFrames??0));replace(e);
  }),numberField('Transition (images)',item.transition?.durationFrames,v=>changeField([...path,'transition','durationFrames'],v),{min:0,max:30,step:1})),
  node('details',{class:'advanced-controls'},node('summary',{},'Réglages 3D du cadrage'),
   vectorFields('Caméra au départ',item.camera?.from,[...path,'camera','from']),vectorFields('Caméra à l’arrivée',item.camera?.to,[...path,'camera','to']),
   vectorFields('Point visé au départ',item.camera?.targetFrom,[...path,'camera','targetFrom']),vectorFields('Point visé à l’arrivée',item.camera?.targetTo,[...path,'camera','targetTo']),
   node('div',{class:'two-col'},numberField('Angle de champ départ (°)',item.camera?.fovFrom,v=>changeField([...path,'camera','fovFrom'],v),{min:25,max:65}),numberField('Angle de champ arrivée (°)',item.camera?.fovTo,v=>changeField([...path,'camera','fovTo'],v),{min:25,max:65})),
   ['follow'].includes(item.camera?.mode)||item.camera?.track?selectField('Personnage suivi',item.camera?.track,['guardian','ghost'],v=>changeField([...path,'camera','track'],v)):null,
   item.camera?.mode==='orbit'?node('div',{class:'two-col'},numberField('Orbite départ (radians)',item.camera?.angleFrom,v=>changeField([...path,'camera','angleFrom'],v),{min:-3,max:3}),numberField('Orbite arrivée (radians)',item.camera?.angleTo,v=>changeField([...path,'camera','angleTo'],v),{min:-3,max:3})):null),
  atlasSelectionInfo(item.atlas,[...path,'atlas']),button('Choisir un lieu Atlas pour ce plan',()=>{shotIndex=index;atlasTarget='shot';view='atlas';render();}),
  elementControls([...path,'elements'],item.elements,{inherit:true}),
  s.livingWorld?node('details',{},node('summary',{},'Personnages Living Worlds dans ce plan'),small('Les personnages et leurs déplacements héritent de la scène. Ces animations remplacent la pose à partir du début du plan.'),
   ...(s.livingWorld.cast??[]).map(a=>selectField(charactersById.get(a.characterId)?.names.fr??a.id,item.livingWorld?.animations?.find(o=>o.id===a.id)?.animation??a.animation,livingAnimations,v=>{const old=item.livingWorld?.animations??[];worldChange([...path,'livingWorld','animations'],[...old.filter(o=>o.id!==a.id),{id:a.id,animation:v,transitionFrames:12}]);})),
   button('Hériter des animations de la scène',()=>replace(removeProperty(episode,[...path,'livingWorld'])))):null,
  actionTools(()=>{shotIndex=Math.max(0,index-1);replace(moveShot(episode,sceneIndex,index,-1),{message:'Plan déplacé. Ses ancrages sont conservés : vérifiez leur ordre.'});},()=>{shotIndex=index+1;replace(moveShot(episode,sceneIndex,index,1),{message:'Plan déplacé. Ses ancrages sont conservés : vérifiez leur ordre.'});},()=>{try{replace(deleteShot(episode,sceneIndex,index),{message:index===0?'Plan supprimé. Le nouveau premier plan commence à zéro. Annuler reste disponible.':'Plan supprimé.'});}catch(e){toast(e.message);}},index===0,index===p.shots.length-1,p.shots.length<=1)
 ));return card;
}
function clipCard(item,index,kind){
 if(!record(item))return node('div',{class:'card'},'Entrée illisible : utilisez le mode JSON avancé.');
 const pi=directionIndex(),family=kind==='actions'?'actions':'events',path=['direction','scenes',pi,family,index];
 return node('details',{class:'plan-card',open:false},node('summary',{},node('span',{class:'number-badge'},index+1),node('strong',{},kind==='actions'?`${friendly(item.actor)} · ${friendly(item.animation)}`:friendly(item.type))),
  node('div',{class:'plan-body'},textField('Intention narrative',item.purpose,v=>changeField([...path,'purpose'],v)),
   kind==='actions'?node('div',{class:'two-col'},selectField('Personnage',item.actor,['guardian','ghost'],v=>{let e=patch(episode,[...path,'actor'],v);e=patch(e,[...path,'animation'],catalog.animations[v][0]);replace(e);}),selectField('Animation',item.animation,catalog.animations[item.actor]??[],v=>changeField([...path,'animation'],v))):selectField('Effet',item.type,catalog.effects,v=>{let e=patch(episode,[...path,'type'],v);if(v==='beam'&&!e.direction.scenes[pi].events[index].to)e=patch(e,[...path,'to'],[0,.2,0]);replace(e);}),
   cueFields(item,path),numberField('Durée (s)',Number(item.durationFrames)/30,v=>changeField([...path,'durationFrames'],v===null?null:Math.round(v*30)),{min:kind==='actions'?0.4:0.1,step:0.1}),
   kind==='actions'?node('details',{class:'advanced-controls'},node('summary',{},'Déplacement et hauteur'),vectorFields('Départ',item.from,[...path,'from']),vectorFields('Arrivée',item.to,[...path,'to']),numberField('Hauteur du saut',item.height??1.3,v=>changeField([...path,'height'],v),{min:0,max:3})):node('div',{},numberField('Intensité (0–1)',item.strength,v=>changeField([...path,'strength'],v),{min:0,max:1,step:.1}),node('details',{class:'advanced-controls'},node('summary',{},'Position de l’effet'),vectorFields('Origine',item.position,[...path,'position']),item.type==='beam'?vectorFields('Extrémité',item.to,[...path,'to']):null)),
   button('Supprimer',()=>{const e=clone(episode);e.direction.scenes[pi][family].splice(index,1);replace(e);},{class:'danger-quiet'})
  ));
}
function atlasSelectionInfo(ref,path){
 if(!ref)return null;
 let label;try{label=resolveAtlas(ref).label;}catch{label='Référence Atlas à corriger';}
 return node('div',{class:'atlas-selection'},node('strong',{},'Atlas · '+label),small('Ce lieu est prioritaire sur le décor générique correspondant. Les plans « Décor de la scène » héritent du lieu de scène.'),button('Retirer cette sélection Atlas',()=>replace(removeProperty(episode,path)),{class:'danger-quiet'}));
}
function atlasPanel(){
 const matches=()=>searchAtlas(atlasFilters);
 const panel=node('section',{class:'atlas-panel'},node('nav',{class:'atlas-tabs'},button('← Épisode',()=>{view='episode';render();}),button('Atlas',()=>{}, {'aria-current':'page'}),button('Démo Atlas',()=>{view='episode';createProject(clone(atlasDemo),'Démo Atlas chargée.');})),
  node('div',{class:'card'},node('p',{class:'eyebrow'},'DESTINY EXPLAINED · 0.3'),node('h1',{},'Atlas de Destiny'),small(`${atlas.locations.length} fiches sourcées · inventaire partiel, extensible. Présence dans un manifest ≠ disponibilité actuelle. Les noms français éditoriaux sont signalés.`),
   node('p',{},`Projet : ${episode.title??'Sans titre'} · scène ${sceneIndex+1} · plan ${shotIndex+1}`),small('Une sélection est enregistrée dans le projet local et son export JSON. Les anciens champs et les champs inconnus sont conservés.')));
 function refreshResults(){const region=panel.querySelector('#atlas-results');if(region)region.replaceChildren(results());}
 const query=textField('Rechercher en français ou anglais',atlasFilters.query,value=>{atlasFilters.query=value;atlasLimit=20;refreshResults();},{id:'atlas-search',help:'Noms, alias et identifiants. Les accents sont facultatifs.'});
 const filters=node('div',{class:'card atlas-filters'},query,
  selectField('Catégorie',atlasFilters.category,['',...categories],value=>{atlasFilters.category=value;atlasLimit=20;refreshResults();},'atlas-category'),
  selectField('Civilisation',atlasFilters.civilization,['',...[...new Set(atlas.locations.flatMap(p=>p.civilizations))].sort()],value=>{atlasFilters.civilization=value;atlasLimit=20;refreshResults();},'atlas-civilization'),
  selectField('Époque',atlasFilters.era,['',...[...new Set(atlas.locations.flatMap(p=>[...p.eras,...p.variants.flatMap(v=>v.eras)]))].sort()],value=>{atlasFilters.era=value;atlasLimit=20;refreshResults();},'atlas-era'),
  selectField('Destination ou région parente',atlasFilters.parentId,['',...atlas.locations.filter(p=>!['zone','activity-site','historical-site','lore-world'].includes(p.category)).map(p=>p.id)],value=>{atlasFilters.parentId=value;atlasLimit=20;refreshResults();},'atlas-parent'));
 // Use localized place names in navigation; empty filters mean all values.
 for(const select of filters.querySelectorAll('select'))for(const option of select.options){if(option.value==='')option.textContent='Tous';else if(select.id==='atlas-parent')option.textContent=locationsById.get(option.value)?.names.fr??option.value;}
 function results(){
  const found=matches(),listNode=node('div',{class:'atlas-cards'});
  listNode.append(node('p',{class:'hint',id:'atlas-count'},`${found.length} résultat(s). ${atlasFilters.parentId?'Enfants directs de '+locationsById.get(atlasFilters.parentId)?.names.fr:''}`));
  if(atlasFilters.parentId)listNode.append(button('↑ Remonter au parent',()=>{atlasFilters.parentId=locationsById.get(atlasFilters.parentId)?.parentId??'';atlasLimit=20;render();}));
  for(const place of found.slice(0,atlasLimit)){
   const currentScene=sceneList(episode)[sceneIndex];
   const currentRef=atlasTarget==='shot'?planFor(episode,currentScene?.id)?.shots?.[shotIndex]?.atlas:currentScene?.atlas;
   let variantId=atlasVariants.get(place.id)??(currentRef?.locationId===place.id?currentRef.variantId??'':'');
   const fidelity=place.canonStatus==='editorial-container'?'Conteneur éditorial, pas un nom propre de lieu canonique':place.canonStatus==='manifest-attested'?'Nom et parent attestés par le manifest ; carte non vérifiée':place.appearance.evidence==='game'?'Environnement montré en jeu (référence partielle)':place.appearance.evidence==='lore-and-cinematic'?'Lore et images cinématiques partielles':'Lieu décrit dans le lore / connaissance limitée';
   const card=node('article',{class:'card atlas-card','data-place-id':place.id},node('h2',{},place.names.fr),node('p',{class:'hint'},place.names.en),node('p',{class:'pill'},friendly(place.category)),small(fidelity),small(place.render.mode==='dedicated'?'Décor dédié, stylisé ; pas une reproduction exacte.':'Décor modulaire de substitution · reconstitution artistique.'),small('Nom français : '+(place.frenchNameStatus==='editorial-translation'?'traduction éditoriale':place.frenchNameStatus==='untranslated'?'non traduit':'issu du manifest / nom officiel abrégé')),);
   const variant=selectField('Variante historique',variantId,['',...place.variants.map(v=>v.id)],value=>{atlasVariants.set(place.id,value);variantId=value;},'atlas-variant-'+place.id);
   for(const option of variant.querySelector('select').options)option.textContent=option.value?place.variants.find(v=>v.id===option.value)?.names.fr??option.value:'État de référence';
   if(place.variants.length)card.append(variant,small('Les variantes historiques sont des reconstitutions artistiques, même si le lieu actuel possède un décor dédié.'));
   const select=(target)=>{
    try{
     let path;if(target==='scene')path=['scenes',sceneIndex,'atlas'];
     else{const pi=directionIndex();if(pi<0)throw new Error('Activez les plans cinématiques avant de sélectionner un lieu de plan.');const shots=episode.direction.scenes[pi].shots;if(!shots[shotIndex])throw new Error('Sélectionnez un plan existant.');path=['direction','scenes',pi,'shots',shotIndex,'atlas'];}
     atlasTarget=target==='scene'?'scene':'shot';
     replace(setAtlasReference(episode,path,place.id,(atlasVariants.get(place.id)??variantId)||undefined),{message:`${place.names.fr} enregistré pour ${target==='scene'?'la scène':'le plan'}.`});
    }catch(error){toast(error.message);}
   };
   card.append(node('div',{class:'button-row'},button('Utiliser pour la scène',()=>select('scene'),{class:'primary'}),button('Utiliser pour le plan',()=>select('shot'),{disabled:directionIndex()<0})));
   if(atlas.locations.some(p=>p.parentId===place.id))card.append(button('Explorer les zones',()=>{atlasFilters.parentId=place.id;atlasFilters.query='';atlasLimit=20;render();}));
   const refs=new Set([...place.sources,...place.variants.flatMap(v=>v.sources)]);
   card.append(node('details',{},node('summary',{},'Sources et fiabilité'),small('Note documentaire (anglais) : '+place.appearance.note),small('Certitude d’apparence : '+({partial:'partielle',unknown:'inconnue',documented:'documentée'}[place.appearance.confidence])),...Array.from(refs,id=>{const source=sourcesById.get(id);return source?node('p',{},node('a',{href:source.url,target:'_blank',rel:'noopener noreferrer'},source.title),small(({'primary-manifest':'Manifest Bungie (primaire)','primary-lore-archive':'Archive du lore (primaire)',secondary:'Référence communautaire (secondaire)'}[source.kind])+' · '+(source.locator??'consultée le '+source.checkedAt))):small('Source inconnue : '+id);})));listNode.append(card);
  }
  if(found.length>atlasLimit)listNode.append(button('Afficher 20 fiches de plus',()=>{atlasLimit+=20;refreshResults();}));
  if(!found.length)listNode.append(small('Aucun résultat dans cet inventaire partiel. Vérifiez les filtres ou consultez les lacunes documentées.'));
  return listNode;
 }
 panel.append(filters,node('div',{id:'atlas-results'},results()),node('details',{class:'card'},node('summary',{},'Couverture et lieux encore manquants'),...atlas.knownGaps.map(g=>small(g))),node('div',{class:'bottom-bar'},button('← Épisode',()=>{view='episode';render();}),button('Exporter JSON',()=>exportFile(false),{class:'primary'}),button('Copie pour rendu',()=>exportFile(true))));
 return panel;
}
const openElementPanels=new Set();
function elementControls(path,items,{inherit=false}={}){
 const panelKey=path.join('.');
 const inherited=inherit&&items===undefined;
 const entries=list(items);
 const panel=node('details',{class:'advanced-controls voxel-elements',open:openElementPanels.has(panelKey)},node('summary',{},inherit?'Éléments voxel de ce plan':'Éléments voxel de la scène'),
  small('Éléments de décor réutilisables. Le Gardien et le Spectre principaux restent pilotés par les animations du récit. Maximum 12 éléments et 256 particules par liste.'),
  inherit?selectField('Source des éléments',inherited?'scene':'custom',['scene','custom'],value=>{
   if(value==='scene')replace(removeProperty(episode,path));
   else replace(patch(episode,path,clone(sceneList(episode)[sceneIndex]?.elements??[])));
  }):null,
  inherited?small('Les éléments de la scène sont hérités. Une liste propre au plan les remplace ; une liste vide les masque.'):node('div',{class:'element-list'},
   button('+ Ajouter un élément',()=>replace(patch(episode,path,[...entries,newElement()])),{class:'secondary',disabled:entries.length>=12}),
   ...entries.map((item,index)=>{
    if(!record(item))return small('Élément invalide : utilisez le JSON avancé.');
    const itemPath=[...path,index],particle=['snow','particles','light-fragments'].includes(item.type);
    return node('fieldset',{class:'element-card'},node('legend',{},`Élément ${index+1} · ${friendly(item.type)}`),
     selectField('Type d’élément',item.type,catalog.elementTypes,value=>{
      let e=patch(episode,[...itemPath,'type'],value);e=patch(e,[...itemPath,'animation'],catalog.elementAnimations[value][0]);replace(e);
     }),
     selectField('Animation de l’élément',item.animation??catalog.elementAnimations[item.type]?.[0],catalog.elementAnimations[item.type]??[],v=>changeField([...itemPath,'animation'],v)),
     vectorFields('Position de l’élément',item.position,[...itemPath,'position']),
     numberField('Échelle',item.scale??1,v=>changeField([...itemPath,'scale'],v),{min:.25,max:3,step:.1}),
     particle?node('div',{class:'two-col'},numberField('Nombre de particules',item.count??24,v=>changeField([...itemPath,'count'],v),{min:1,max:64,step:1}),numberField('Force de l’effet',item.strength??.65,v=>changeField([...itemPath,'strength'],v),{min:0,max:1,step:.1})):null,
     node('details',{class:'advanced-controls'},node('summary',{},'Rotation et graine déterministe'),vectorFields('Rotation (radians)',item.rotation??[0,0,0],[...itemPath,'rotation']),numberField('Graine',item.seed??0,v=>changeField([...itemPath,'seed'],v),{min:0,max:65535,step:1})),
     button('Supprimer cet élément',()=>{const e=clone(entries);e.splice(index,1);replace(patch(episode,path,e));},{class:'danger-quiet'}));
   })),
 );
 panel.addEventListener('toggle',()=>{if(panel.isConnected){if(panel.open)openElementPanels.add(panelKey);else openElementPanels.delete(panelKey);}});
 return panel;
}
function legacyControls(s){
 return node('section',{class:'card'},node('h3',{},'Mise en scène classique'),selectField('Caméra de scène',s.camera,catalog.basicCameras,v=>changeField(['scenes',sceneIndex,'camera'],v)),small('Les actions classiques sont conservées dans le JSON avancé. Ajouter des plans active le moteur cinématique ; leurs animations se règlent ensuite séparément.'),button('Activer les plans cinématiques',()=>{try{replace(addShot(episode,sceneIndex,0),{message:'Plans cinématiques activés. Les anciennes actions restent conservées dans le JSON.'});}catch(e){toast(e.message);}},{class:'secondary'}));
}
function sceneEditor(){
 const s=sceneList(episode)[sceneIndex];
 if(!record(s))return node('section',{class:'card'},node('h2',{},'Une scène à préparer'),small('Importez le modèle ou ajoutez une scène. Les données invalides restent accessibles dans le mode JSON avancé.'),button('Ajouter une scène',()=>replace(addScene(episode))));
 const p=planFor(episode,s.id);
 return node('section',{class:'scene-editor','aria-label':'Édition de la scène'},
  node('div',{class:'section-heading'},node('div',{},node('p',{class:'eyebrow'},`SCÈNE ${sceneIndex+1} / ${sceneList(episode).length}`),node('h2',{},'Le récit, puis les plans')),node('span',{class:'pill',id:'scene-duration-label'},secondsLabel(s.durationFrames))),
  node('div',{class:'card'},textField('Narration anglaise',s.narration,v=>changeField(['scenes',sceneIndex,'narration'],v,{dirty:true}),{area:true,id:'narration',rows:5,help:'Ce texte sera lu par Kokoro. Une modification remet la voix et les sous-titres en attente.'}),
   numberField('Durée de la scène (secondes)',Number(s.durationFrames)/(episode.format?.fps??30),v=>edit(setDuration(episode,sceneIndex,v===null?NaN:v)),{id:'scene-duration',min:1,step:.1,help:'Arrondie à l’image près. Les débuts des scènes suivantes sont recalculés ; les plans, animations et effets restent inchangés et sont revérifiés.'}),
   selectField('Décor de la scène',s.location,catalog.locations,v=>replace(setEnvironment(episode,['scenes',sceneIndex,'location'],v)),'scene-location'),
   small('Les plans réglés sur « Décor de la scène » suivent ce choix. Les anciens plans avec un décor explicite gardent leur choix.'),
   atlasSelectionInfo(s.atlas,['scenes',sceneIndex,'atlas']),button('Choisir un lieu dans l’Atlas',()=>{atlasTarget='scene';view='atlas';render();}),
   elementControls(['scenes',sceneIndex,'elements'],s.elements),
   actionTools(()=>{const i=sceneIndex;sceneIndex--;replace(moveScene(episode,i,-1));},()=>{const i=sceneIndex;sceneIndex++;replace(moveScene(episode,i,1));},()=>{const i=sceneIndex;sceneIndex=Math.max(0,i-1);replace(deleteScene(episode,i),{message:'Scène supprimée. Annuler reste disponible.'});},sceneIndex===0,sceneIndex===sceneList(episode).length-1,sceneList(episode).length<=1)),
  !p?legacyControls(s):node('div',{},node('div',{class:'tabs',role:'tablist','aria-label':'Mise en scène'},...['shots','actions','events'].map(key=>button(`${key==='shots'?'Plans':key==='actions'?'Animations':'Effets'} (${list(p[key]).length})`,()=>{tab=key;render();},{role:'tab','aria-selected':tab===key,class:tab===key?'active':''}))),
   tab==='shots'?node('section',{class:'tab-panel',role:'tabpanel','aria-label':'Plans'},small('Débuts vocaux estimés. Balayez la chronologie des plans ; chaque intention doit servir la narration.'),node('div',{id:'shot-timeline-region'},shotTimeline(s,p)),
    node('div',{class:'section-heading'},button('+ Ajouter un plan',()=>{try{const e=addShot(episode,sceneIndex,shotIndex);shotIndex++;replace(e);}catch(e){toast(e.message);}},{class:'secondary'}),button('Répartir les débuts',()=>{try{replace(spreadShots(episode,sceneIndex),{message:'Débuts répartis en images. Les anciens ancrages vocaux ont été remplacés ; Annuler les restaure.'});}catch(e){toast(e.message);}},{title:'Remplace les ancrages vocaux par des débuts régulièrement espacés.'})),small('Après déplacement, les ancrages sont conservés. « Répartir les débuts » les remplace explicitement par des images ; les autres réglages ne changent pas.'),...list(p.shots).map((item,i)=>shotCard(s,p,item,i))):
    node('section',{class:'tab-panel',role:'tabpanel','aria-label':tab==='actions'?'Animations':'Effets'},button(tab==='actions'?'+ Ajouter une animation':'+ Ajouter un effet',()=>{const e=clone(episode),pi=directionIndex();if(!Array.isArray(e.direction.scenes[pi][tab]))e.direction.scenes[pi][tab]=[];e.direction.scenes[pi][tab].push(tab==='actions'?newAction():newEvent());replace(e);},{class:'secondary'}),...list(p[tab]).map((item,i)=>clipCard(item,i,tab))))
 );
}
function exportFile(renderCopy=false){
 if(mode==='advanced'&&rawDraft!==JSON.stringify(episode,null,2)){toast('Appliquez ou annulez le brouillon JSON avant l’export.');return;}
 try{
  const data=renderCopy?compatibleCopy(episode):episode;
  const blob=new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=node('a',{href:url,download:`${String(episode.id??'episode').replace(/[^a-zA-Z0-9_-]/g,'-')}${renderCopy?'-render':''}.json`});
  document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);save();toast(renderCopy?'Copie pour rendu téléchargée. Le projet complet est conservé.':'JSON complet téléchargé, avec tous ses champs.');
 }catch(e){toast(`Export impossible : ${e.message.slice(0,250)}`);}
}
function advancedEditor(){
 const input=node('textarea',{id:'advanced-json',class:'json-editor',spellcheck:false,value:rawDraft,rows:24,'aria-label':'JSON avancé',onInput:e=>{rawDraft=e.target.value;scheduleSave();const status=$('#raw-status');try{parseImport(rawDraft);status.textContent='Syntaxe JSON lisible. Appliquez pour vérifier le moteur.';status.className='hint';}catch(error){status.textContent=error.message;status.className='hint error-text';}}});
 return node('section',{class:'card'},node('h2',{},'Le JSON, sans filtre'),small('Tous les champs sont conservés. Le brouillon, même incomplet, reste enregistré sur cet appareil.'),input,node('p',{id:'raw-status',class:'hint'},'Appliquez vos modifications pour mettre à jour les formulaires et la validation.'),node('div',{class:'button-row'},button('Appliquer le JSON',()=>{try{const raw=parseImport(rawDraft);replace(raw);mode='advanced';save();render();toast('JSON appliqué. Consultez la validation du moteur.');}catch(e){toast(e.message);}},{class:'primary'}),button('Annuler les modifications JSON',()=>{rawDraft=JSON.stringify(episode,null,2);save();render();})));
}
function render(){
 previewUnmount?.();previewUnmount=undefined;
 try{renderContent();}
 catch(error){
  // Invalid nested imports remain fully repairable in the advanced editor.
  mode='advanced';
  $('#app').replaceChildren(node('section',{class:'card'},node('h1',{},'Réparer le JSON importé'),small('Cette structure ne peut pas être affichée dans les formulaires. Vos données sont conservées ; corrigez les champs indiqués.'),advancedEditor(),validationBox(),button('Exporter JSON complet',()=>exportFile(false)),button('Charger le modèle Voyageur',()=>createProject(templateEpisode()))));
 }
}
function renderContent(){
 sceneIndex=Math.max(0,Math.min(sceneIndex,sceneList(episode).length-1));
 const app=$('#app');app.replaceChildren();
 const file=node('input',{type:'file',accept:'.json,application/json',id:'import-file',hidden:true,onChange:async e=>{
  const f=e.target.files?.[0];if(!f)return;
  try{if(f.size>2*1024*1024)throw new Error('Le fichier dépasse 2 Mo.');const raw=parseImport(await f.text());createProject(raw,'JSON importé intégralement.');}catch(error){toast(`Import impossible : ${error.message}`);}
 }});
 if(view==='storyboard'){app.append(file,storyboardPanel());return;}
 if(view==='characters'){app.append(file,charactersPanel());return;}
 if(view==='weather'){app.append(file,weatherPanel());return;}
 if(view==='atlas'){app.append(file,atlasPanel());return;}
 const modes=node('div',{class:'mode-switch','aria-label':'Mode d’édition'},...['beginner','advanced'].map(value=>button(value==='beginner'?'Débutant':'JSON avancé',()=>{
  if(value==='beginner'&&rawDraft!==JSON.stringify(episode,null,2)){toast('Appliquez ou annulez le brouillon JSON avant de changer de mode.');return;}
  mode=value;save();render();},{'aria-pressed':mode===value,class:mode===value?'selected':''})));
 const librarySelect=node('select',{id:'project-select','aria-label':'Projet enregistré',onChange:e=>switchProject(e.target.value)},...library.map(p=>node('option',{value:p.key,selected:p.key===active},typeof p.episode?.title==='string'?p.episode.title:'Sans titre')));
 app.append(file,node('nav',{class:'atlas-tabs','aria-label':'Studio'},button('Épisode',()=>{}, {'aria-current':'page'}),button('Storyboard Shorts',()=>{view='storyboard';render();},{id:'storyboard-tab'}),...['characters','weather'].map(key=>button(key==='characters'?'Personnages':'Météo',()=>{if(rawDirty()){toast('Appliquez le brouillon JSON.');return;}view=key;render();},{id:key+'-tab'})),button('Atlas',()=>{if(rawDirty()){toast('Appliquez ou annulez le brouillon JSON avant d’ouvrir l’Atlas.');return;}atlasTarget='scene';view='atlas';render();},{id:'atlas-tab'})),node('section',{class:'intro'},node('div',{},node('p',{class:'eyebrow'},'VOTRE PROCHAIN SHORT'),node('h1',{},'Une histoire. Plusieurs plans.'),node('p',{class:'intro-copy'},'Écrivez ici. Générez votre vidéo dans Colab. Vos projets restent sur votre téléphone.')),node('div',{class:'hero-art','aria-hidden':'true'},node('i'),node('i'),node('i'))),
  node('section',{class:'project-shelf'},node('label',{},node('span',{class:'eyebrow'},'MES PROJETS'),librarySelect),node('div',{class:'button-row'},button('+ Nouveau',()=>createProject(newEpisode(),'Nouvel épisode créé.')),button('Modèle Voyageur',()=>createProject(templateEpisode(),'Modèle du Voyageur chargé, sans modification.')),button('Démo 4 décors',()=>createProject(demoEpisode(),'Démonstration des quatre décors chargée.')))),
  node('section',{class:'button-row'},...[[whirlwindDemo,'Démo Tourbillon'],[europaDemo,'Démo Europe'],[fundamentDemo,'Démo Fundament']].map(([e,label])=>button(label,()=>createProject(clone(e))))),
  hybridLaunch(),
  node('section',{class:'project-head'},node('div',{},node('p',{class:'eyebrow'},'ÉPISODE EN COURS'),node('h2',{id:'project-heading'},typeof episode.title==='string'?episode.title:'Épisode sans titre'),node('p',{id:'episode-stat',class:'hint'},`${sceneList(episode).length} scènes · ${secondsLabel(episode.format?.durationFrames)} · 1080 × 1920`)),modes),
  node('div',{class:'edit-toolbar'},node('span',{id:'save-status',class:storageError?'error-text':'hint'},storageError||'Sauvegarde locale automatique'),node('div',{class:'button-row'},button('↶ Annuler',()=>{if(rawDirty()){toast('Appliquez ou annulez le brouillon JSON avant de revenir en arrière.');return;}if(!undo.length)return;redo.push(clone(episode));replace(undo.pop(),{remember:false});},{id:'undo-button',disabled:undo.length===0}),button('↷ Rétablir',()=>{if(rawDirty()){toast('Appliquez ou annulez le brouillon JSON avant de rétablir.');return;}if(!redo.length)return;undo.push(clone(episode));replace(redo.pop(),{remember:false});},{id:'redo-button',disabled:redo.length===0}),button('Enregistrer',()=>{save();toast(storageError||'Projet enregistré sur cet appareil.');}))),
  mode==='beginner'?node('section',{class:'card episode-fields'},textField('Titre de l’épisode',episode.title,v=>changeField(['title'],v),{id:'episode-title'}),
   episode.direction?selectField('Intensité cinématique',episode.direction?.intensity,catalog.intensity,v=>changeField(['direction','intensity'],v), 'intensity'):node('span',{class:'pill'},'Épisode classique'),
   node('details',{class:'episode-options'},node('summary',{},'Identifiant et fichier de sortie'),textField('Identifiant de l’épisode',episode.id,v=>changeField(['id'],v),{id:'episode-id',help:'Lettres, chiffres, tirets et underscores, sans espace.'}),textField('Sortie vidéo',episode.render?.output,v=>changeField(['render','output'],v),{help:'Exemple : out/mon-episode.mp4'}))):null,
  node('section',{class:'timeline-card'},node('div',{class:'section-heading'},node('h2',{},'Votre chronologie'),node('span',{class:'pill'},'30 images / s')),small('Balayez pour parcourir les scènes. Les durées sont recalculées après ajout, suppression ou déplacement.'),node('div',{id:'timeline-region'},timeline())),
  mode==='advanced'?advancedEditor():node('div',{class:'workspace'},node('aside',{class:'scene-rail','aria-label':'Scènes'},node('div',{class:'section-heading'},node('h2',{},'Scènes'),button('+',()=>{const e=addScene(episode);sceneIndex=sceneList(e).length-1;shotIndex=0;replace(e);},{'aria-label':'Ajouter une scène'})),node('div',{class:'scene-list'},...sceneList(episode).map((s,i)=>button([node('span',{class:'eyebrow'},`SCÈNE ${String(i+1).padStart(2,'0')}`),node('strong',{},typeof s?.narration==='string'?s.narration.slice(0,65):'À renseigner'),node('small',{},secondsLabel(s?.durationFrames))],()=>{sceneIndex=i;shotIndex=0;render();},{class:i===sceneIndex?'scene-button selected':'scene-button','aria-pressed':i===sceneIndex})))),sceneEditor()),
  node('div',{id:'validation-region'},validationBox()),
  node('section',{class:'card transfer'},node('p',{class:'eyebrow'},'DE L’ÉCRITURE À LA VIDÉO'),node('h2',{},'La suite se passe dans Colab'),node('p',{},'Téléchargez une copie pour rendu, ouvrez le notebook puis importez ce fichier depuis votre téléphone. Kokoro crée la voix ; Remotion calcule le MP4.'),
   node('div',{class:'button-row'},button('Copie pour rendu',()=>exportFile(true),{class:'secondary',id:'export-render'}),node('a',{class:'button-link',href:'https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/main/remotion/tts/Editor-Colab.ipynb',target:'_blank',rel:'noopener noreferrer'},'Ouvrir Colab ↗')),
   small('Le JSON complet conserve tous les champs. La copie pour rendu écarte uniquement les champs non reconnus par le schéma actuel, sans changer votre projet. Aucun MP4 n’est généré dans ce site.'),node('a',{href:'./GUIDE.html'},'Aide et publication GitHub Pages')),
  node('footer',{class:'page-footer'},'Projet de fans non officiel · Sans affiliation avec Bungie · Aucune connexion à un compte'),
  node('nav',{class:'bottom-bar','aria-label':'Fichiers'},button('↥ Importer',()=>$('#import-file').click(),{id:'import-button'}),button('↓ Exporter JSON',()=>exportFile(false),{class:'primary',id:'export-button'}),node('a',{href:'#validation-region',class:'button-link'},'Validation'))
 );
}
const characterFilters={query:'',civilization:'',faction:''};
function worldChange(path,value){let e=patch(episode,path,value);e.schemaVersion='0.4.0';replace(e);}
function ensureLiving(){
 const s=episode.scenes[sceneIndex];if(s.livingWorld)return;
 worldChange(['scenes',sceneIndex,'livingWorld'],{mode:'reconstruction',cast:[],groups:[]});
}
function livingHeader(title){return node('div',{class:'section-heading'},node('h1',{},title),button('← Épisode',()=>{view='episode';render();}));}
function castCard(a,i,base=['scenes',sceneIndex,'livingWorld','cast']){
 const path=[...base,i],c=charactersById.get(a.characterId);
 return node('details',{class:'card cast-card',open:true},node('summary',{},c?.names.fr??a.characterId),
  small(c?.identityNote??'Personnage inconnu.'),
  selectField('Variante du personnage',a.variantId??c?.variants[0]?.id,c?.variants.map(v=>v.id)??[],v=>worldChange([...path,'variantId'],v)),
  selectField('Animation du personnage',a.animation??'idle',livingAnimations,v=>worldChange([...path,'animation'],v)),
  vectorFields('Position du personnage',a.position,[...path,'position']),
  node('div',{class:'two-col'},numberField('Début du personnage (images)',a.startFrame??0,v=>changeField([...path,'startFrame'],v),{min:0,step:1}),numberField('Durée du personnage (images)',a.durationFrames,v=>changeField([...path,'durationFrames'],v),{min:1,step:1})),
  node('details',{},node('summary',{},'Trajectoire et changements d’animation'),
   ...(a.path?.waypoints??[]).map((p,j)=>node('div',{},vectorFields(`Point ${j+1}`,p.position,[...path,'path','waypoints',j,'position']),numberField('Pause (images)',p.pauseFrames??0,v=>changeField([...path,'path','waypoints',j,'pauseFrames'],v),{min:0,step:1}))),
   a.path?numberField('Vitesse (unités/s)',a.path.speed,v=>changeField([...path,'path','speed'],v),{min:.05,max:12}):button('Créer une trajectoire',()=>worldChange([...path,'path'],{waypoints:[{position:a.position,pauseFrames:0},{position:[Math.min(18,a.position[0]+2),a.position[1],a.position[2]-1],pauseFrames:0}],speed:.5})),
   ...(a.clips??[]).map((clip,j)=>node('div',{class:'card'},selectField('Animation programmée',clip.animation,livingAnimations,v=>worldChange([...path,'clips',j,'animation'],v)),numberField('Début animation (images)',clip.startFrame,v=>changeField([...path,'clips',j,'startFrame'],v),{min:0,step:1}),numberField('Durée animation (images)',clip.durationFrames,v=>changeField([...path,'clips',j,'durationFrames'],v),{min:1,step:1}))),
   button('Programmer une animation',()=>worldChange([...path,'clips'],[...(a.clips??[]),{animation:'interact',startFrame:Math.floor(a.durationFrames/2),durationFrames:Math.ceil(a.durationFrames/2),transitionFrames:12}]))),
  button('Retirer ce personnage',()=>{let parent=episode;for(const k of base)parent=parent[k];worldChange(base,parent.filter((_,j)=>j!==i));},{class:'danger-quiet'})
 );
}
function charactersPanel(){
 const s=episode.scenes[sceneIndex],w=s?.livingWorld;
 const filters=node('div',{class:'two-col'},textField('Recherche personnages FR/EN',characterFilters.query,v=>{characterFilters.query=v;update();},{id:'character-search'}),selectField('Civilisation',characterFilters.civilization,['',...civilizations],v=>{characterFilters.civilization=v;update();}),selectField('Faction',characterFilters.faction,['',...new Set(characterCatalog.characters.map(c=>c.faction))],v=>{characterFilters.faction=v;update();}));
 const results=node('div',{id:'character-results'});
 function update(){results.replaceChildren(...searchCharacters(characterFilters.query,characterFilters.civilization,characterFilters.faction).slice(0,16).map(c=>node('details',{class:'card character-result','data-character-id':c.id},node('summary',{},c.names.fr+' · '+c.names.en),small(c.visual.silhouette),small(c.visual.note),small(c.identityNote),...c.sources.map(id=>{const src=characterCatalog.sources.find(s=>s.id===id);return node('a',{href:src.url,target:'_blank',rel:'noopener noreferrer'},src.title+' ↗ ');}),button('Ajouter à la scène',()=>{ensureLiving();const path=['scenes',sceneIndex,'livingWorld','cast'];const current=episode.scenes[sceneIndex].livingWorld.cast;worldChange(path,[...current,{id:slug('pnj'),characterId:c.id,variantId:c.variants[0].id,position:[current.length*1.1,0,-2],animation:'idle',startFrame:0,durationFrames:s.durationFrames,clips:[]}]);}))));}
 update();
 return node('section',{},livingHeader('Personnages'),small(`Scène ${sceneIndex+1} · 16 résultats maximum affichés. Affinez la recherche. Budget total : 32 personnages.`),filters,results,
  node('h2',{},'Personnages dans la scène'),w?selectField('Mode narratif',w.mode??'reconstruction',['canonical','reconstruction','alternate-history'],v=>worldChange(['scenes',sceneIndex,'livingWorld','mode'],v)):small('Ajoutez un personnage pour activer les mondes vivants.'),
  ...(w?.cast??[]).map((a,i)=>castCard(a,i)),
  node('h2',{},'Groupes de figurants'),...(w?.groups??[]).map((g,i)=>{const path=['scenes',sceneIndex,'livingWorld','groups',i];return node('details',{class:'card',open:true},node('summary',{},g.id),numberField('Nombre de figurants',g.count,v=>changeField([...path,'count'],v),{min:1,max:24,step:1}),selectField('Population',g.member.characterId,characterCatalog.characters.filter(c=>['civilian','scientist','soldier','creature'].includes(c.archetype)).map(c=>c.id),v=>{const m={...g.member,characterId:v};delete m.variantId;worldChange([...path,'member'],m);}),selectField('Formation',g.formation,['grid','line','scatter'],v=>worldChange([...path,'formation'],v)),selectField('Comportement',g.behavior,['idle','walk','flee'],v=>worldChange([...path,'behavior'],v)),numberField('Graine du groupe',g.seed,v=>changeField([...path,'seed'],v),{min:0,max:2147483647,step:1}),numberField('Espacement',g.spacing,v=>changeField([...path,'spacing'],v),{min:.5,max:3}),vectorFields('Origine du groupe',g.member.position,[...path,'member','position']),button('Retirer ce groupe',()=>worldChange(['scenes',sceneIndex,'livingWorld','groups'],w.groups.filter((_,j)=>j!==i))));}),
  button('Ajouter un groupe',()=>{ensureLiving();const w=episode.scenes[sceneIndex].livingWorld;worldChange(['scenes',sceneIndex,'livingWorld','groups'],[...w.groups,{id:slug('groupe'),member:{id:'template',characterId:'eliksni-civilian',position:[-2,0,-4],animation:'idle',startFrame:0,durationFrames:s.durationFrames,clips:[]},count:4,seed:42,formation:'grid',spacing:1,behavior:'idle',sizeVariation:.08}]);}),
  node('div',{id:'validation-region'},validationBox()));
}
function weatherPanel(){
 const s=episode.scenes[sceneIndex],w=s?.weather,path=['scenes',sceneIndex,'weather'];
 const preset=weatherPresets[s?.atlas?.locationId??s?.location];
 const create=type=>worldChange(path,{type,intensity:.5,windDirection:0,windSpeed:3,visibility:1,startFrame:0,durationFrames:s.durationFrames,seed:42,transitionFrames:Math.min(60,s.durationFrames),dayPhase:.5,particleBudget:64});
 return node('section',{},livingHeader('Météo'),small(`Scène ${sceneIndex+1} · ${preset?.note??'Préréglages artistiques ; compatibilité du lieu non documentée.'}`),
  selectField('Préréglage météo',w?.type??'clear',preset?.types??weatherTypes,v=>create(v)),
  !w?button('Activer la météo',()=>create('clear')):node('div',{class:'card'},selectField('Condition météo',w.type,weatherTypes,v=>worldChange([...path,'type'],v)),
   numberField('Intensité météo',w.intensity,v=>changeField([...path,'intensity'],v),{min:0,max:1,step:.05}),
   numberField('Direction du vent (degrés)',w.windDirection??0,v=>changeField([...path,'windDirection'],v),{min:-180,max:180}),numberField('Vitesse du vent',w.windSpeed??0,v=>changeField([...path,'windSpeed'],v),{min:0,max:30}),numberField('Visibilité',w.visibility??1,v=>changeField([...path,'visibility'],v),{min:.05,max:1,step:.05}),
   numberField('Début météo (images)',w.startFrame??0,v=>changeField([...path,'startFrame'],v),{min:0,step:1}),numberField('Durée météo (images)',w.durationFrames,v=>changeField([...path,'durationFrames'],v),{min:1,step:1}),numberField('Graine météo',w.seed,v=>changeField([...path,'seed'],v),{min:0,max:2147483647,step:1}),numberField('Budget particules',w.particleBudget??64,v=>changeField([...path,'particleBudget'],v),{min:0,max:128,step:1}),
   numberField('Heure solaire (0 nuit, 0,5 midi)',w.dayPhase??.5,v=>changeField([...path,'dayPhase'],v),{min:0,max:1,step:.05}),
   numberField('Cycle jour/nuit (images)',w.dayCycleFrames??720,v=>changeField([...path,'dayCycleFrames'],v),{min:30,max:18000,step:1}),
   selectField('Évolution vers',w.to?.type??w.type,weatherTypes,v=>worldChange([...path,'to'],{type:v,intensity:.85,windDirection:w.windDirection??0,windSpeed:12,visibility:.4})),
   w.to?node('div',{},numberField('Intensité finale',w.to.intensity,v=>changeField([...path,'to','intensity'],v),{min:0,max:1,step:.05}),numberField('Durée de transition météo (images)',w.transitionFrames??60,v=>changeField([...path,'transitionFrames'],v),{min:0,max:s.durationFrames,step:1})):null,
   button('Retirer la météo',()=>replace(removeProperty(episode,path)))),
  small('Aperçu : les paramètres sont validés ci-dessous. Le rendu animé s’effectue dans Colab.'),node('div',{id:'validation-region'},validationBox()));
}

let storyboardIndex=0,previewUnmount;
function shortsEdit(path,value,{full=false,voice=false}={}){let e=patch(episode,path,value);if(voice)invalidateVoice(e);if(full)replace(e);else edit(e);}
function storyboardPanel(){
 if(!episode.shorts)return node('section',{},livingHeader('Hybrid Shorts'),node('h2',{},'Créer un Short vertical'),small('Les projets existants restent disponibles dans l’éditeur Épisode. Choisissez un modèle pour créer un nouveau projet hybride.'),hybridLaunch());
 storyboardIndex=Math.max(0,Math.min(storyboardIndex,episode.scenes.length-1));const s=episode.scenes[storyboardIndex],v=s.visual,path=['scenes',storyboardIndex],stat=pacing(episode);
 const back=()=>{previewUnmount?.();previewUnmount=undefined;view='episode';sceneIndex=storyboardIndex;render();};
 return node('section',{class:'hybrid-storyboard'},node('div',{class:'section-heading'},node('h1',{},'Storyboard hybride'),node('a',{href:'./HYBRID-GUIDE.html'},'Guide mobile'),button('← Épisode',back)),
  textField('Titre du Short',episode.title,x=>shortsEdit(['title'],x)),small(`${stat.total.toFixed(1)} s · ${episode.scenes.length} plans · Hook ${stat.hook.toFixed(1)} s · Moyenne ${stat.average.toFixed(1)} s · ${Math.round(stat.wpm)} mots/min · Budget voix ${stat.narrationBudget.toFixed(1)} s · ${Object.entries(stat.visualSeconds).map(([type,sec])=>friendly(type)+' '+sec.toFixed(1)+' s').join(' / ')}`),
  node('div',{class:'button-row'},button('Démo Riis',()=>{storyboardIndex=0;createProject(clone(hybridRiis));}),button('Démo Oryx',()=>{storyboardIndex=0;createProject(clone(hybridOryx));}),button('Démo Jardin noir',()=>{storyboardIndex=0;createProject(clone(hybridGarden));})),
  node('nav',{class:'storyboard-list','aria-label':'Plans du storyboard'},...episode.scenes.map((shot,i)=>button(`${i+1} · ${friendly(shot.visual?.type)} · ${(shot.durationFrames/30).toFixed(1)} s`,()=>{previewUnmount?.();storyboardIndex=i;render();},{class:i===storyboardIndex?'selected':'','aria-current':i===storyboardIndex?'step':undefined}))),
  node('div',{class:'button-row'},button('Ajouter un plan',()=>{storyboardIndex=episode.scenes.length;replace(addStoryboard(episode));}),button('Dupliquer le plan',()=>{const e=duplicateStoryboard(episode,storyboardIndex);storyboardIndex++;replace(e);}),button('Monter le plan',()=>{const i=storyboardIndex;storyboardIndex=Math.max(0,i-1);replace(moveScene(episode,i,-1));},{disabled:storyboardIndex===0}),button('Descendre le plan',()=>{const i=storyboardIndex;storyboardIndex=Math.min(episode.scenes.length-1,i+1);replace(moveScene(episode,i,1));},{disabled:storyboardIndex===episode.scenes.length-1}),button('Supprimer le plan',()=>{if(!confirm('Supprimer ce plan et son contenu ? Annuler reste disponible dans l’éditeur Épisode.'))return;const i=storyboardIndex;storyboardIndex=Math.max(0,i-1);replace(deleteScene(episode,i));},{disabled:episode.scenes.length<=1,class:'danger-quiet'})),
  node('section',{class:'card'},node('h2',{},`Plan ${storyboardIndex+1}`),
   selectField('Type de plan',v.type,sceneTypes,x=>replace(setStoryboardType(episode,storyboardIndex,x))),
   small('Changer de type conserve les personnages et les contenus précédents dans le projet complet. Les personnages restent masqués sur les plans graphiques. La copie pour rendu écarte les brouillons de types inactifs.'),
   numberField('Durée du plan (secondes)',s.durationFrames/30,x=>replace(resizeStoryboard(episode,storyboardIndex,x)),{min:.5,max:60,step:.1}),
   textField('Narration anglaise',s.narration,x=>shortsEdit([...path,'narration'],x,{voice:true}),{area:true,help:'Kokoro sera généré dans Colab. Le texte doit tenir dans la durée du plan.'}),
   textField('Titre à l’écran',v.headline,x=>shortsEdit([...path,'visual','headline'],x)),
   selectField('Transition du plan',v.transition.type,transitionTypes,x=>shortsEdit([...path,'visual','transition'],{type:x,durationFrames:x==='cut'?0:12},{full:true})),
   numberField('Durée de transition (images)',v.transition.durationFrames,x=>shortsEdit([...path,'visual','transition','durationFrames'],x),{min:0,max:24,step:1}),
   hybridVisualControls(s,path),
   textField('Sources du plan (identifiants séparés par virgule)',v.sources.join(', '),x=>shortsEdit([...path,'visual','sources'],x.split(',').map(s=>s.trim()).filter(Boolean))),
   selectField('Associer une source existante','',['',...new Set([...atlas.sources,...characterCatalog.sources,...episode.shorts.sources].map(src=>src.id))],id=>{if(id&&!v.sources.includes(id))shortsEdit([...path,'visual','sources'],[...v.sources,id],{full:true});}),
   node('details',{},node('summary',{},'Sources disponibles'),...v.sources.map(id=>{const url=sourceUrl(episode,id);return url?node('a',{href:url,target:'_blank',rel:'noopener noreferrer'},sourceTitle(episode,id)+' ↗ '):small('Source inconnue : '+id);}),small('Vous pouvez ajouter une référence documentaire dans les réglages Sources ci-dessous.'))),
  node('section',{class:'card'},node('h2',{},'Narration, sous-titres et sources'),
   selectField('Modèle narratif',episode.shorts.template,Object.keys(templateLabels),x=>{let e=patch(episode,['shorts','template'],x);if(x==='what-if')e.shorts.mode='hypothesis';replace(e);}),
   selectField('Statut narratif',episode.shorts.mode,['canonical','reconstruction','hypothesis','alternate-history'],x=>shortsEdit(['shorts','mode'],x,{full:true})),
   selectField('Confiance documentaire',episode.shorts.confidence,['documented','partial','unknown'],x=>shortsEdit(['shorts','confidence'],x)),
   selectField('Style des sous-titres',episode.shorts.captions.style,captionStyles,x=>shortsEdit(['shorts','captions','style'],x)),
   numberField('Position basse captions (pixels)',episode.shorts.captions.bottomPx,x=>shortsEdit(['shorts','captions','bottomPx'],x),{min:280,max:520,step:10}),
   numberField('Mots par segment',episode.shorts.captions.maxWords,x=>shortsEdit(['shorts','captions','maxWords'],x),{min:2,max:6,step:1}),
   small(captionTiming(episode).exact?'Timestamps complets validés : aperçu des captions aligné.':'Sans timestamps complets : aperçu silencieux et minutage estimé, puis alignement Kokoro dans Colab.'),
   node('label',{class:'field'},node('span',{},'Importer les mots alignés Kokoro'),node('input',{type:'file',accept:'.json',onChange:async ev=>{try{const f=ev.target.files?.[0];if(!f)return;const words=JSON.parse(await f.text());validateWords(words,episode);shortsEdit(['shorts','alignedWords'],words,{full:true});}catch(e){toast('Alignement refusé : '+e.message);}}})),
   ...(episode.shorts.sources??[]).map((src,i)=>node('details',{class:'card',open:true},node('summary',{},src.title||'Nouvelle source'),textField('Identifiant de source',src.id,x=>shortsEdit(['shorts','sources',i,'id'],x)),textField('Titre documentaire',src.title,x=>shortsEdit(['shorts','sources',i,'title'],x)),textField('URL documentaire HTTPS',src.url,x=>shortsEdit(['shorts','sources',i,'url'],x)),textField('Passage ou repère',src.locator,x=>shortsEdit(['shorts','sources',i,'locator'],x)))),
   button('Ajouter une source',()=>shortsEdit(['shorts','sources'],[...episode.shorts.sources,{id:slug('source'),title:'Référence à compléter',url:'https://www.ishtar-collective.net/',locator:'Passage précis à compléter'}],{full:true}))),
  hybridAudioControls(),
  node('section',{class:'card'},node('h2',{},'Aperçu du Short'),small('Le même composant anime l’aperçu et la vidéo finale. Le brouillon réduit la résolution interne voxel ; la voix est générée dans Colab.'),
   button('Charger l’aperçu',async()=>{try{previewUnmount?.();const copy=compatibleCopy(episode);const {mountPreview}=await import('./hybrid-preview.js');previewUnmount=mountPreview(document.querySelector('#hybrid-preview'),copy);}catch(e){toast('Aperçu impossible : '+e.message);}}),node('div',{id:'hybrid-preview',class:'hybrid-preview','aria-label':'Lecteur du Short'})),
  node('div',{id:'validation-region'},validationBox()),
  node('div',{class:'button-row'},button('Enregistrer le Short',()=>{save();toast(storageError||'Short enregistré.');}),button('Exporter Short JSON',()=>exportFile(false)),button('Copie Short pour rendu',()=>exportFile(true)),node('a',{class:'button-link',href:'https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/main/remotion/tts/Editor-Colab.ipynb',target:'_blank',rel:'noopener noreferrer'},'Rendre dans Colab ↗'))
 );
}
function hybridVisualControls(s,path){
 const v=s.visual,p=[...path,'visual'];
 if(v.type==='text')return node('div',{},selectField('Rôle du texte',v.kind,['hook','quote','question','reveal','conclusion'],x=>shortsEdit([...p,'kind'],x)),textField('Texte explicatif',v.body,x=>shortsEdit([...p,'body'],x),{area:true}));
 if(v.type==='voxel')return node('div',{},atlasSelectionInfo(s.atlas,[...path,'atlas']),button('Lieu et variante Atlas',()=>{sceneIndex=storyboardIndex;view='atlas';atlasTarget='scene';render();}),button('Personnages et animations',()=>{sceneIndex=storyboardIndex;view='characters';render();}),button('Météo du plan',()=>{sceneIndex=storyboardIndex;view='weather';render();}),selectField('Mouvement de caméra',planFor(episode,s.id)?.shots[0]?.camera.mode??'dolly',['dolly','zoom','perspective'],x=>{const pi=episode.direction.scenes.findIndex(p=>p.sceneId===s.id);shortsEdit(['direction','scenes',pi,'shots',0,'camera','mode'],x);}),button('Réglages détaillés de caméra',()=>{sceneIndex=storyboardIndex;view='episode';render();}));
 if(v.type==='map')return node('div',{},small('Positions en pourcentages schématiques ; aucune coordonnée astronomique canonique.'),...v.nodes.map((n,i)=>node('details',{class:'card',open:true},node('summary',{},n.label),textField('Étiquette du lieu',n.label,x=>shortsEdit([...p,'nodes',i,'label'],x)),selectField('Lieu Atlas du marqueur',n.locationId??'',['',...atlas.locations.filter(a=>['lore-world','stellar-body','destination-region'].includes(a.category)).map(a=>a.id)],x=>{let e=patch(episode,[...p,'nodes',i,'locationId'],x);if(!x)delete e.scenes[storyboardIndex].visual.nodes[i].locationId;replace(e);}),...['X','Y'].map((axis,j)=>numberField('Carte '+axis,n.position[j],x=>shortsEdit([...p,'nodes',i,'position',j],x),{min:0,max:100})))),button('Ajouter un marqueur',()=>shortsEdit([...p,'nodes'],[...v.nodes,{id:slug('point'),label:'Nouveau lieu',position:[50,50]}],{full:true})),...v.routes.map((r,i)=>node('div',{class:'two-col'},selectField('Départ du trajet',r.from,v.nodes.map(n=>n.id),x=>shortsEdit([...p,'routes',i,'from'],x)),selectField('Arrivée du trajet',r.to,v.nodes.map(n=>n.id),x=>shortsEdit([...p,'routes',i,'to'],x)))),button('Ajouter une connexion',()=>{if(v.nodes.length<2)return;shortsEdit([...p,'routes'],[...v.routes,{from:v.nodes[0].id,to:v.nodes[1].id,label:''}],{full:true});}),numberField('Zoom carte au départ',v.camera.zoomFrom,x=>shortsEdit([...p,'camera','zoomFrom'],x),{min:1,max:2}),numberField('Zoom carte à la fin',v.camera.zoomTo,x=>shortsEdit([...p,'camera','zoomTo'],x),{min:1,max:2}));
 if(v.type==='timeline')return node('div',{},...v.events.map((ev,i)=>node('details',{class:'card',open:true},node('summary',{},ev.label),textField('Événement',ev.label,x=>shortsEdit([...p,'events',i,'label'],x)),textField('Période',ev.period,x=>shortsEdit([...p,'events',i,'period'],x)),textField('Date attestée (vide si inconnue)',ev.date??'',x=>shortsEdit([...p,'events',i,'date'],x||null)),selectField('Confiance de l’événement',ev.confidence,['documented','partial','unknown'],x=>shortsEdit([...p,'events',i,'confidence'],x)),textField('Sources de l’événement',ev.sources.join(', '),x=>shortsEdit([...p,'events',i,'sources'],x.split(',').map(s=>s.trim()).filter(Boolean))))),button('Ajouter un événement',()=>shortsEdit([...p,'events'],[...v.events,{id:slug('event'),label:'Événement à documenter',period:'Période inconnue',date:null,confidence:'unknown',sources:v.sources}],{full:true})));
 return node('div',{},...v.cards.map((c,i)=>node('details',{class:'card',open:true},node('summary',{},c.title),textField('Titre de carte',c.title,x=>shortsEdit([...p,'cards',i,'title'],x)),textField('Explication de carte',c.body,x=>shortsEdit([...p,'cards',i,'body'],x),{area:true}),...['X','Y'].map((axis,j)=>numberField('Graphique '+axis,c.position[j],x=>shortsEdit([...p,'cards',i,'position',j],x),{min:0,max:100})))),button('Ajouter une carte explicative',()=>shortsEdit([...p,'cards'],[...v.cards,{id:slug('card'),title:'Point à documenter',body:'Explication à compléter.',position:[48,50]}],{full:true})));
}
function hybridAudioControls(){
 return node('section',{class:'card'},node('h2',{},'Pistes audio facultatives'),numberField('Volume narration',episode.shorts.audio.voiceVolume,x=>shortsEdit(['shorts','audio','voiceVolume'],x),{min:0,max:1,step:.05}),small('Aucune musique ni ressource externe nécessaire. Importer uniquement un fichier dont vous pouvez déclarer la provenance et la licence. Maximum 512 Kio par piste ; l’audio est embarqué dans le JSON.'),
  node('label',{class:'field'},node('span',{},'Importer une piste locale'),node('input',{type:'file',accept:'audio/wav,audio/mpeg,audio/ogg',onChange:ev=>{const file=ev.target.files?.[0];if(!file)return;if(file.size>512*1024){toast('Piste supérieure à 512 Kio.');return;}const reader=new FileReader();reader.onload=()=>{const track={id:slug('audio'),kind:'ambience',source:reader.result,startFrame:episode.scenes[storyboardIndex].startFrame,durationFrames:episode.scenes[storyboardIndex].durationFrames,volume:.25,fadeInFrames:12,fadeOutFrames:12,ducking:.3,provenance:{title:file.name,creator:'À renseigner',license:'original',attribution:'Provenance à confirmer avant publication'}};shortsEdit(['shorts','audio','tracks'],[...episode.shorts.audio.tracks,track],{full:true});};reader.readAsDataURL(file);}})),
  ...episode.shorts.audio.tracks.map((t,i)=>{const p=['shorts','audio','tracks',i];return node('details',{class:'card',open:true},node('summary',{},t.provenance.title),selectField('Type de piste',t.kind,['effect','ambience','music'],x=>shortsEdit([...p,'kind'],x)),numberField('Volume de piste',t.volume,x=>shortsEdit([...p,'volume'],x),{min:0,max:1,step:.05}),numberField('Volume relatif pendant la voix',t.ducking,x=>shortsEdit([...p,'ducking'],x),{min:0,max:1,step:.05}),numberField('Début audio (images)',t.startFrame,x=>shortsEdit([...p,'startFrame'],x),{min:0,step:1}),numberField('Durée audio (images)',t.durationFrames,x=>shortsEdit([...p,'durationFrames'],x),{min:1,step:1}),numberField('Fondu entrant (images)',t.fadeInFrames,x=>shortsEdit([...p,'fadeInFrames'],x),{min:0,max:90,step:1}),numberField('Fondu sortant (images)',t.fadeOutFrames,x=>shortsEdit([...p,'fadeOutFrames'],x),{min:0,max:90,step:1}),textField('Auteur de la ressource',t.provenance.creator,x=>shortsEdit([...p,'provenance','creator'],x)),selectField('Licence déclarée',t.provenance.license,['original','CC0','CC-BY'],x=>shortsEdit([...p,'provenance','license'],x)),textField('URL de licence',t.provenance.licenseUrl??'',x=>{if(x)shortsEdit([...p,'provenance','licenseUrl'],x);else edit(removeProperty(episode,[...p,'provenance','licenseUrl']));}),textField('Attribution',t.provenance.attribution,x=>shortsEdit([...p,'provenance','attribution'],x)),button('Retirer la piste',()=>shortsEdit(['shorts','audio','tracks'],episode.shorts.audio.tracks.filter((_,j)=>i!==j),{full:true})));})
 );
}
function hybridLaunch(){
 let script='',subject='Your Destiny topic',template='destiny-mysteries';
 return node('section',{class:'card'},node('h2',{},'Créer un Short'),textField('Sujet du Short',subject,x=>{subject=x;}),selectField('Structure narrative',template,Object.keys(templateLabels),x=>{template=x;}),textField('Script anglais (paragraphes par plan)',script,x=>{script=x;},{area:true,help:'Aucun fait n’est généré automatiquement. Le texte saisi reste entièrement éditable.'}),button('Créer le storyboard',()=>{storyboardIndex=0;view='storyboard';createProject(newHybridProject(template,script,subject));},{class:'primary'}),button('Ouvrir la démo Riis',()=>{storyboardIndex=0;view='storyboard';createProject(clone(hybridRiis));}));
}

try{
 const saved=JSON.parse(localStorage.getItem(KEY)||'null');
 if(saved?.version===1&&Array.isArray(saved.projects)){library=saved.projects.filter(p=>record(p.episode)&&typeof p.key==='string');active=saved.active;}
}catch{storageError='Impossible de lire les sauvegardes locales. Exportez votre travail avant de fermer la page.';}
if(!library.length){const e=templateEpisode();active=slug('projet');library=[{key:active,episode:e,rawDraft:JSON.stringify(e,null,2),mode:'beginner',updatedAt:new Date().toISOString()}];}
const initial=current()??library[0];active=initial.key;episode=clone(initial.episode);rawDraft=initial.rawDraft??JSON.stringify(episode,null,2);mode=initial.mode??'beginner';
render();
window.addEventListener('pagehide',save);

if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{});
