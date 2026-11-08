import {clone,reflow,invalidateVoice,patch,slug,planFor} from './model.mjs';
import {newHybridShot,newVisual,defaultPlan} from '../remotion/hybrid/templates.ts';
export function addStoryboard(raw,type='text'){
 const e=clone(raw),s=newHybridShot(slug('shot'),type,150);e.scenes.push(s);e.direction.scenes.push(defaultPlan(s.id));return reflow(e);
}
export function duplicateStoryboard(raw,index){
 const e=clone(raw),s=clone(e.scenes[index]),old=planFor(e,s.id);s.id=slug('shot');e.scenes.splice(index+1,0,s);
 const plan=old?clone(old):defaultPlan(s.id);plan.sceneId=s.id;
 for(const key of ['shots','actions','events'])for(const item of plan[key])item.id=slug(key);
 e.direction.scenes.push(plan);return reflow(e);
}
export function setStoryboardType(raw,index,type){
 const e=clone(raw),s=e.scenes[index];if(s.visual.type===type)return e;
 s.editorVisualDrafts??={};s.editorVisualDrafts[s.visual.type]=clone(s.visual);
 s.visual=clone(s.editorVisualDrafts[type]??{...newVisual(type),headline:s.visual.headline,sources:s.visual.sources});
 if(type==='voxel'){s.atlas??={locationId:'riis',variantId:'before-whirlwind'};s.livingWorld??={mode:'reconstruction',cast:[],groups:[]};}
 return invalidateVoice(e);
}
export function resizeStoryboard(raw,index,seconds){return reflow(patch(raw,['scenes',index,'durationFrames'],Math.round(seconds*30)));}
