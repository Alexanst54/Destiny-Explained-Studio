import {atlasRefSchema} from '../remotion/atlas/index.ts';
// Shared by the static app, Node tests and Colab import. The engine stays strict;
// the editor keeps the original object and creates an explicitly separate projection.
import {locations,elementTypes,elementAnimations,defaultElementAnimation,environmentDefinitions} from '../remotion/src/voxel/library/catalog.ts';
import demo from '../remotion/episodes/voxel_worlds_demo.json' with {type:'json'};
import {episodeSchema} from '../remotion/src/voxel/episode/schema.ts';
import {directionSchema} from '../remotion/src/voxel/cinematic/schema.ts';
import {resolveDirection,estimatedWords,resolveCue} from '../remotion/src/voxel/cinematic/timeline.ts';
import template from '../remotion/episodes/traveler_episode_002_cinematic.json' with {type:'json'};
export const clone=value=>structuredClone(value);
const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const unwrap=s=>['optional','default','nullable'].includes(s.def.type)?unwrap(s.def.innerType):s.def.type==='union'?s.options.flatMap(unwrap):[s];
export function engineProjection(raw){
 const unknown=[];
 const walk=(schemas,value,path)=>{
  const options=schemas.flatMap(unwrap);
  const objects=options.filter(s=>s.def.type==='object');
  if(object(value)&&objects.length){
   const fields=new Map();
   for(const s of objects)for(const [key,child]of Object.entries(s.shape))fields.set(key,[...(fields.get(key)??[]),child]);
   const result={};
   for(const key of Object.keys(value)){
    if(!fields.has(key)){unknown.push([...path,key].join('.'));continue;}
    Object.defineProperty(result,key,{value:walk(fields.get(key),value[key],[...path,key]),enumerable:true,writable:true,configurable:true});
   }
   return result;
  }
  const arrays=options.filter(s=>s.def.type==='array');
  if(Array.isArray(value)&&arrays.length)return value.map((v,i)=>walk(arrays.map(s=>s.element),v,[...path,i]));
  return clone(value);
 };
 return {episode:walk([episodeSchema],raw,[]),unknown};
}
const planSchema=directionSchema.shape.scenes.element;
const shotSchema=planSchema.shape.shots.element;
const variants=planSchema.shape.actions.element.options;
export const catalog={
 locations,elementTypes,elementAnimations,
 cameras:shotSchema.shape.camera.shape.mode.options,
 environments:shotSchema.shape.environment.options,
 transitions:shotSchema.shape.transition.shape.type.options,
 intensity:directionSchema.shape.intensity.options,
 effects:planSchema.shape.events.element.shape.type.options,
 animations:Object.fromEntries(variants.map(s=>[s.shape.actor.value,s.shape.animation.options])),
 basicAnimations:Object.fromEntries(episodeSchema.shape.scenes.element.shape.actions.element.options.map(s=>[s.shape.actor.value,s.shape.animation.options])),
 basicCameras:episodeSchema.shape.scenes.element.shape.camera.options,
 basicEffects:episodeSchema.shape.scenes.element.shape.effects.element.options,
};
export function parseImport(text){
 const raw=JSON.parse(text);
 if(!object(raw))throw new Error('Le fichier doit contenir un objet épisode JSON.');
 return raw;
}
export const templateEpisode=()=>clone(template);
export const demoEpisode=()=>clone(demo);
export const slug=prefix=>`${prefix}-${globalThis.crypto?.randomUUID?.().slice(0,8)??Math.random().toString(36).slice(2,10)}`;
export function newShot(id=slug('plan'),frame=0){return {id,at:{sceneFrame:frame},purpose:'Présenter le sujet de ce passage.',environment:'scene',actors:{guardian:true,ghost:true},
 camera:{mode:'dolly',from:[0,4.4,13],to:[0,4.8,12],targetFrom:[0,3,-2],targetTo:[0,3,-2],fovFrom:42,fovTo:42},transition:{type:'cut',durationFrames:0}};}
export function newAction(actor='guardian'){return {id:slug('action'),actor,animation:catalog.animations[actor][0],at:{sceneFrame:0},durationFrames:60,from:actor==='guardian'?[0,.02,0]:[.6,3.4,0],to:actor==='guardian'?[0,.02,0]:[.6,3.4,0],height:1.3,purpose:'Accompagner le passage raconté.'};}
export function newEvent(){return {id:slug('effet'),type:'particles',at:{sceneFrame:0},durationFrames:45,position:[0,.5,0],strength:.5,purpose:'Souligner un élément de la narration.'};}
export function newEpisode(){
 const e=templateEpisode();e.id=slug('episode');e.title='Nouvel épisode';
 e.scenes=[{id:'scene-01',startFrame:0,durationFrames:240,location:'the-tower',camera:'wide-tilt-up',actions:[{actor:'guardian',animation:'idle'},{actor:'ghost',animation:'hover'}],effects:['soft-daylight'],narration:'What mysteries does the Traveler hold?'}];
 e.direction={version:1,intensity:'balanced',scenes:[{sceneId:'scene-01',shots:[newShot('plan-01')],actions:[],events:[]}]};
 e.notes=['Épisode créé dans l’éditeur mobile.'];e.render.output='out/episode.mp4';
 return reflow(e);
}
export const sceneList=e=>Array.isArray(e.scenes)?e.scenes:[];
export const planFor=(e,id)=>Array.isArray(e.direction?.scenes)?e.direction.scenes.find(s=>s.sceneId===id):undefined;
export function patch(raw,path,value){
 const e=clone(raw);let at=e;
 for(let i=0;i<path.length;i++){
  const key=path[i];if(['__proto__','prototype','constructor'].includes(String(key)))throw new Error('Chemin de champ interdit.');
  if(i===path.length-1){at[key]=clone(value);break;}
  if(!object(at[key])&&!Array.isArray(at[key]))at[key]=typeof path[i+1]==='number'?[]:{};
  at=at[key];
 }
 return e;
}
export function invalidateVoice(e){
 if(object(e.audio?.voiceover))e.audio.voiceover.status='to-generate';
 if(object(e.subtitles))e.subtitles.status='pending-voiceover-alignment';
 return e;
}
export function reflow(raw){
 const e=clone(raw);let cursor=0;
 for(const s of sceneList(e)){if(!object(s))continue;s.startFrame=cursor;cursor+=Number.isInteger(s.durationFrames)&&s.durationFrames>0?s.durationFrames:0;}
 if(!object(e.format))e.format={width:1080,height:1920,fps:30};
 e.format.durationFrames=cursor;
 if(Array.isArray(e.direction?.scenes)){
  const rest=[...e.direction.scenes],ordered=[];
  for(const s of sceneList(e)){const i=rest.findIndex(p=>p.sceneId===s.id);if(i>=0)ordered.push(...rest.splice(i,1));}
  e.direction.scenes=[...ordered,...rest]; // Unmatched advanced entries are never silently lost.
 }
 return invalidateVoice(e);
}
export function setDuration(raw,index,seconds){
 const fps=raw.format?.fps??30;
 return reflow(patch(raw,['scenes',index,'durationFrames'],Number.isFinite(seconds)?Math.round(seconds*fps):null));
}
export function moveScene(raw,index,delta){
 const e=clone(raw),to=index+delta;if(to<0||to>=sceneList(e).length)return e;
 [e.scenes[index],e.scenes[to]]=[e.scenes[to],e.scenes[index]];return reflow(e);
}
export function addScene(raw){
 const e=clone(raw),id=slug('scene');if(!Array.isArray(e.scenes))e.scenes=[];
 e.scenes.push({id,startFrame:0,durationFrames:240,location:'the-tower',camera:'wide-tilt-up',actions:[{actor:'guardian',animation:'idle'}],effects:['soft-daylight'],narration:'Tell the next part of the story.'});
 if(e.direction){if(!Array.isArray(e.direction.scenes))e.direction.scenes=[];e.direction.scenes.push({sceneId:id,shots:[newShot()],actions:[],events:[]});}
 return reflow(e);
}
export function deleteScene(raw,index){
 const e=clone(raw);if(sceneList(e).length<=1)throw new Error('Conservez au moins une scène.');
 const removed=e.scenes.splice(index,1)[0];
 if(Array.isArray(e.direction?.scenes))e.direction.scenes=e.direction.scenes.filter(p=>p.sceneId!==removed.id);
 return reflow(e);
}
export function enableDirection(raw){
 const e=clone(raw);if(e.direction)return e;
 e.direction={version:1,intensity:'balanced',scenes:sceneList(e).map(s=>({sceneId:s.id,shots:[newShot()],actions:[],events:[]}))};
 if(!object(e.render))e.render={output:'out/episode.mp4',codec:'h264'};
 e.render.composition='VoxelCinematicEpisode';return e;
}
export function shotStart(e,scene,shot){
 try{return resolveCue(shot.at,scene,estimatedWords(e))-scene.startFrame;}catch{return null;}
}
export function addShot(raw,sceneIndex,afterIndex){
 const e=enableDirection(raw),s=e.scenes[sceneIndex],p=planFor(e,s.id);
 if(!p)throw new Error('La mise en scène ne correspond pas à cette scène.');
 const i=Math.max(0,Math.min(afterIndex,p.shots.length-1));
 const start=shotStart(e,s,p.shots[i])??0,end=p.shots[i+1]?shotStart(e,s,p.shots[i+1]):s.durationFrames;
 if(end===null||end-start<24)throw new Error('Pas assez de place : augmentez la durée ou modifiez les débuts de plans.');
 p.shots.splice(i+1,0,newShot(slug('plan'),Math.floor((start+end)/2)));
 return e;
}
export function moveShot(raw,sceneIndex,index,delta){
 const e=clone(raw),p=planFor(e,e.scenes[sceneIndex].id),to=index+delta;
 if(!p||to<0||to>=p.shots.length)return e;
 [p.shots[index],p.shots[to]]=[p.shots[to],p.shots[index]];return e;
}
export function frameCue(old,frame){const cue=object(old)?clone(old):{};delete cue.phrase;delete cue.occurrence;delete cue.offsetFrames;cue.sceneFrame=frame;return cue;}
export function phraseCue(old,phrase){const cue=object(old)?clone(old):{};delete cue.sceneFrame;cue.phrase=phrase;return cue;}
export function deleteShot(raw,sceneIndex,index){
 const e=clone(raw),p=planFor(e,e.scenes[sceneIndex].id);
 if(!p||p.shots.length<=1)throw new Error('Conservez au moins un plan.');
 p.shots.splice(index,1);if(index===0)p.shots[0].at=frameCue(p.shots[0].at,0);return e;
}
export function spreadShots(raw,sceneIndex){
 const e=clone(raw),s=e.scenes[sceneIndex],p=planFor(e,s.id);
 if(!p||s.durationFrames<p.shots.length*12)throw new Error('La scène est trop courte pour ces plans.');
 p.shots.forEach((shot,i)=>{shot.at=frameCue(shot.at,Math.floor(i*s.durationFrames/p.shots.length));});return e;
}
function staticTiming(e){
 const errors=[],ids=new Set();
 const add=(path,message)=>errors.push({path,message});
 for(const [i,p]of (e.direction?.scenes??[]).entries()){
  const s=e.scenes[i];if(!s||s.id!==p.sceneId){add(`direction.scenes.${i}.sceneId`,'L’ordre des mises en scène doit correspondre aux scènes.');continue;}
  const all=[...p.shots,...p.actions,...p.events];
  for(const item of all){
   if(ids.has(item.id))add(item.id,'Identifiant de plan, animation ou effet dupliqué.');ids.add(item.id);
   if('sceneFrame'in item.at&&(item.at.sceneFrame>=s.durationFrames||item.at.sceneFrame<0))add(item.id,'Le début sort de la scène.');
   if(item.durationFrames>s.durationFrames||('sceneFrame'in item.at&&item.at.sceneFrame+(item.durationFrames??0)>s.durationFrames))add(item.id,'La durée dépasse la fin de la scène.');
  }
  p.shots.forEach((shot,j)=>{
   if(j===0&&'sceneFrame'in shot.at&&shot.at.sceneFrame!==0)add(shot.id,'Le premier plan doit commencer à zéro.');
   const next=p.shots[j+1];
   if('sceneFrame'in shot.at&&(!next||'sceneFrame'in next.at)){
    const length=(next?.at.sceneFrame??s.durationFrames)-shot.at.sceneFrame;
    if(length<12)add(shot.id,'Les plans doivent être ordonnés et durer au moins 12 images.');
    if(shot.transition.durationFrames*2>length)add(shot.id,'La transition est trop longue pour ce plan.');
   }
  });
  for(const actor of ['guardian','ghost']){
   const a=p.actions.filter(x=>x.actor===actor&&'sceneFrame'in x.at).sort((a,b)=>a.at.sceneFrame-b.at.sceneFrame);
   for(let j=1;j<a.length;j++)if(a[j].at.sceneFrame<a[j-1].at.sceneFrame+a[j-1].durationFrames)add(a[j].id,'Deux animations du même personnage se chevauchent.');
  }
 }
 return errors;
}
function issueMessage(issue){
 const types={string:'texte',number:'nombre',boolean:'booléen',array:'liste',object:'objet'};
 if(issue.code==='invalid_type')return `Valeur attendue : ${types[issue.expected]??issue.expected}.`;
 if(issue.code==='invalid_value')return 'Valeur non compatible avec le moteur actuel.';
 if(issue.code==='invalid_union')return 'Structure incohérente : vérifiez les champs et les ancrages de début.';
 if(issue.code==='too_small')return `Valeur ou taille minimale : ${issue.minimum}.`;
 if(issue.code==='too_big')return `Valeur ou taille maximale : ${issue.maximum}.`;
 const known={"Unknown Atlas location":"Lieu inconnu dans l’Atlas.","Unknown historical variant for this location":"Variante historique inconnue pour ce lieu.","Environment must be declared":"Ce décor doit être déclaré dans environments. Le sélecteur de décor le fait automatiquement.","Duplicate environment declaration":"Décor déclaré plusieurs fois.","Animation incompatible with this voxel element":"Cette animation n’est pas compatible avec cet élément voxel.","Duplicate voxel element id":"Identifiant d’élément voxel dupliqué.","Voxel element particle budget exceeds 256":"Le budget de 256 particules par liste est dépassé.","Duplicate scene id":"Identifiant de scène dupliqué.","Conflicting Guardian actions":"Des actions du Gardien sont contradictoires.","Duplicate action":"Action dupliquée.","Duplicate effect":"Effet dupliqué.","Cinematic composition requires direction":"La composition cinématique exige une mise en scène.","Direction requires the cinematic composition":"La mise en scène exige VoxelCinematicEpisode.","Resurrection action and beam must occur together":"La résurrection et son rayon doivent être présents ensemble.","Resurrection requires at least 120 frames":"La résurrection classique exige au moins 120 images."};
 if(known[issue.message])return known[issue.message];
 if(issue.message.startsWith('Expected '))return 'Le début des scènes doit être continu, sans trou ni chevauchement. '+issue.message.match(/\d+/)?.[0]+' images attendues.';
 if(issue.message.startsWith('Scene total'))return 'La durée totale ne correspond pas à la somme des scènes.';
 if(issue.code==='invalid_format')return 'Format invalide pour ce champ.';
 return issue.message;
}
export function validateEpisode(raw){
 const {episode,unknown}=engineProjection(raw);
 const parsed=episodeSchema.safeParse(episode),errors=[],warnings=[];
 if(!parsed.success)for(const issue of parsed.error.issues)errors.push({path:issue.path.join('.'),message:issueMessage(issue)});
 else{
  const e=parsed.data;
  if(!/^[a-zA-Z0-9_-]+$/.test(e.id))errors.push({path:'id',message:'Kokoro exige un identifiant sans espaces ni caractères spéciaux.'});
  for(const s of e.scenes)if(!/^[a-zA-Z0-9_-]+$/.test(s.id))errors.push({path:s.id,message:'Kokoro exige un identifiant de scène sans espaces.'});
  errors.push(...staticTiming(e));
  if(e.direction)try{resolveDirection(e,estimatedWords(e));}catch(error){
   const soft=e.direction.scenes.some(p=>[...p.shots,...p.actions,...p.events].some(x=>'phrase'in x.at));
   if(soft&&/outside|exceeds|ordered|too long|transition exceeds/i.test(error.message))warnings.push(`Minutage vocal estimé : ${error.message}. Colab vérifiera les mots réels.`);
   else errors.push({path:'direction',message:error.message});
  }
  warnings.push('Les débuts liés à des phrases sont estimés ici. Le contrôle définitif se fait avec la voix Kokoro dans Colab.');
 }
 if(unknown.length)warnings.unshift(`${unknown.length} champ(s) non reconnu(s) conservé(s). Le moteur strict les refuse ; seule la copie pour rendu les écarte.`);
 return {episode,unknown,errors,warnings,valid:errors.length===0,strict:errors.length===0&&unknown.length===0};
}
export function compatibleCopy(raw){const result=validateEpisode(raw);if(!result.valid)throw new Error(result.errors.map(e=>`${e.path} : ${e.message}`).join('\n'));return clone(result.episode);}
export function secondsLabel(frames,fps=30){return `${(Number(frames||0)/fps).toFixed(2).replace('.',',')} s`;}

export function setEnvironment(raw,path,value){
 const e=patch(raw,path,value);
 const id=['tower','golden-age-vision','collapse-vision'].includes(value)?'the-tower':value;
 if(environmentDefinitions[id]){
  if(!Array.isArray(e.environments))e.environments=[];
  if(!e.environments.some(x=>x?.id===id))e.environments.push(clone(environmentDefinitions[id]));
 }
 return e;
}
export function newElement(type='crystal'){
 return {id:slug('element'),type,position:type==='ghost'?[2,3.2,0]:type==='guardian'?[2,0,0]:type==='snow'?[0,0,0]:[3,0,-3],
  animation:defaultElementAnimation(type),scale:1,seed:0,...(['snow','particles','light-fragments'].includes(type)?{count:24,strength:.65}:{})};
}
export function removeProperty(raw,path){
 const e=clone(raw);let at=e;for(const key of path.slice(0,-1))at=at[key];delete at[path.at(-1)];return e;
}

export function setAtlasReference(raw,path,locationId,variantId){
 atlasRefSchema.parse({locationId,...(variantId?{variantId}:{})});
 let old=raw;for(const key of path)old=old?.[key];
 const ref=object(old)?clone(old):{};ref.locationId=locationId;
 if(variantId)ref.variantId=variantId;else delete ref.variantId;
 const next=patch(raw,path,ref);next.schemaVersion='0.3.0';
 if(path[0]==='direction'){
  const shotPath=path.slice(0,-1);let shot=next;for(const key of shotPath)shot=shot[key];shot.environment='scene';
 }
 return next;
}
