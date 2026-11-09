import {characterVisual} from '../remotion/characters/index.ts';
import {clone,patch,slug} from './model.mjs';
import {studioSchema,rigSchema} from '../remotion/animation/schema.ts';
import {packRig,eliksniPack} from '../remotion/animation/pack.ts';
export function enableStudio(raw,index){const e=clone(raw),s=e.scenes[index];if(s.visual?.type!=='voxel')throw new Error('Le Blocking Studio nécessite un plan voxel.');e.schemaVersion='0.7.0';s.livingWorld??={mode:'reconstruction',props:[],cast:[],groups:[]};s.livingWorld.cast??=[];s.livingWorld.groups??=[];s.livingWorld.props??=[];s.livingWorld.studio={...studioSchema.parse({version:1}),...(s.livingWorld.studio??{})};return e;}
export function addPackActor(raw,index,kind='civilian'){
 const e=enableStudio(raw,index),s=e.scenes[index],w=s.livingWorld,p=eliksniPack.find(p=>p.id===kind);if(!p)throw new Error('Archétype inconnu.');if(w.cast.length+w.groups.reduce((n,g)=>n+g.count,0)>=32)throw new Error('Budget CPU : 32 personnages maximum. Aucun personnage supprimé.');
 const id=slug('eliksni');w.cast.push({id,characterId:p.characterId,...(kind==='civilian'?{}:{variantId:'reconstruction'}),position:[Math.min(12,w.cast.length*1.4-2),0,-2],rotation:0,scale:1,startFrame:0,durationFrames:s.durationFrames,animation:'idle',clips:[],rig:packRig(kind,42+w.cast.length*7919)});return e;
}
export function addRigClip(raw,index,actorIndex){const e=enableStudio(raw,index),a=e.scenes[index].livingWorld.cast[actorIndex];if(!a.rig)throw new Error('Activez le rig avant une action.');let start=0;for(const c of a.rig.clips){if(c.startFrame>start)break;start=Math.max(start,c.startFrame+c.durationFrames);}const next=a.rig.clips.find(c=>c.startFrame>=start),duration=Math.min(60,(next?.startFrame??a.durationFrames)-start);if(duration<1)throw new Error('Aucune période libre : ajustez les actions existantes.');a.rig.clips.push({animation:'look-at-sky',startFrame:start,durationFrames:duration,transitionFrames:Math.min(12,Math.floor(duration/2))});a.rig.clips.sort((a,b)=>a.startFrame-b.startFrame);return e;}
export function blockingPreset(raw,index,kind){let e=enableStudio(raw,index),s=e.scenes[index],w=s.livingWorld;if(!w.cast.length){for(let n=0;n<3;n++)e=addPackActor(e,index,n===0?'elder':'civilian');s=e.scenes[index];w=s.livingWorld;}
 const ids=w.cast.filter(a=>a.rig).map(a=>a.id);if(!ids.length)throw new Error('Ajoutez au moins un personnage rig 2.0.');const id=slug('relation'),duration=s.durationFrames;
 if(kind==='conversation'&&ids.length<2)throw new Error('La conversation demande deux personnages.');
 w.studio.interactions.push(kind==='conversation'?{id,kind:'face',actors:[ids[0]],targetId:ids[1],startFrame:0,durationFrames:duration,transitionFrames:12,spacing:1.3,intensity:1}:{id,kind:kind==='exodus'?'flee':'react',actors:ids,...(kind==='sky'?{targetPoint:[0,9,-6]}:{}),startFrame:0,durationFrames:duration,transitionFrames:12,spacing:1.3,intensity:1});
 w.studio.camera={mode:kind==='conversation'?'two-shot':'group',targets:kind==='conversation'?ids.slice(0,2):ids,startFrame:0,durationFrames:duration,intensity:.6,margin:1.2,side:'left'};return e;
}

export function rigForCharacter(actor){
 const pack=eliksniPack.find(p=>p.characterId===actor.characterId);if(pack)return packRig(pack.id);
 const model=characterVisual(actor.characterId,actor.variantId).visual.model;
 if(['unknown','sphere','drone','beast','terminal'].includes(model))throw new Error('Ce personnage conserve son modèle non humanoïde historique ; aucun rig adapté n’est disponible ici.');
 return rigSchema.parse({version:1,archetype:model==='four-arm'?'four-arm':'humanoid'});
}
