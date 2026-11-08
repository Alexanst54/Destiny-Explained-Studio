import base from '../episodes/living_europa.json' with {type:'json'};
import {templateIds} from './schema.ts';
export const templateLabels:Record<string,string>={'did-you-know':'Did You Know?','the-story-of':'The Story of…','destiny-mysteries':'Destiny Mysteries',timeline:'Timeline','what-if':'What If?','character-origins':'Character Origins'};
export const roles=['Hook','Contexte','Développement','Révélation','Conclusion'];
export function newVisual(type:string){
 const shared={headline:'',transition:{type:'fade',durationFrames:12},sources:[]};
 if(type==='map')return {...shared,type,nodes:[{id:'origin',label:'Riis',locationId:'riis',position:[25,45]},{id:'destination',label:'Unknown destination',position:[75,65]}],routes:[{from:'origin',to:'destination',label:'Schematic route'}],camera:{from:[50,50],to:[52,52],zoomFrom:1,zoomTo:1.1}};
 if(type==='timeline')return {...shared,type,events:[{id:'event-1',label:'Krill origins',period:'Ancient past',date:null,confidence:'partial',sources:['books-of-sorrow']},{id:'event-2',label:'The worm pact',period:'After the Krill origins',date:null,confidence:'partial',sources:['books-of-sorrow']}]};
 if(type==='graphic')return {...shared,type,cards:[{id:'card-1',title:'Your sourced point',body:'Edit this explanation.',position:[50,35]},{id:'card-2',title:'What remains unknown',body:'Separate facts from interpretation.',position:[50,68]}],connections:[{from:'card-1',to:'card-2',label:''}]};
 if(type==='text')return {...shared,type,body:'Write your question or conclusion.',kind:'question'};
 return {...shared,type:'voxel'};
}
export function newHybridShot(id='shot-01',type='text',durationFrames=150){
 return {id,startFrame:0,durationFrames,location:'the-tower',camera:'medium-guardian',actions:[{actor:'guardian',animation:'idle'}],effects:[],narration:'Replace this line with your sourced narration.',visual:newVisual(type),...(type==='voxel'?{atlas:{locationId:'riis',variantId:'before-whirlwind'},livingWorld:{mode:'reconstruction',era:'pre-whirlwind',cast:[],groups:[]}}:{})};
}
export function defaultPlan(sceneId:string){return {sceneId,shots:[{id:sceneId+'-camera',at:{sceneFrame:0},purpose:'Show the visual supporting this part of the narration.',environment:'scene',actors:{guardian:false,ghost:false},camera:{mode:'dolly',from:[2,3.8,13],to:[1,3.4,12],targetFrom:[0,1.6,-3],targetTo:[0,1.8,-4],fovFrom:48,fovTo:46},transition:{type:'cut',durationFrames:0}}],actions:[],events:[]};}
export function newHybridProject(template:typeof templateIds[number]='did-you-know',script='',subject='Your Destiny topic'){
 const e=structuredClone(base) as any;e.schemaVersion='0.5.0';e.id='hybrid-short';e.title=subject;e.render={composition:'HybridShort',output:'out/hybrid-short.mp4',codec:'h264'};
 e.shorts={version:1,template,mode:template==='what-if'?'hypothesis':'reconstruction',confidence:'unknown',sources:[],captions:{style:'dynamic-shorts',bottomPx:350,maxWords:5},audio:{voiceVolume:1,tracks:[]},quality:'cpu'};
 let paragraphs=script.trim()?script.trim().split(/\n\s*\n/):[];
 if(paragraphs.length===1){const tokens=script.trim().split(/\s+/),cuts=[0,.12,.32,.52,.8,1];paragraphs=cuts.slice(0,-1).map((from,i)=>tokens.slice(Math.floor(from*tokens.length),Math.floor(cuts[i+1]*tokens.length)).join(' '));}
 e.scenes=roles.map((role,i)=>{const s=newHybridShot('shot-'+(i+1),i===1?'voxel':i===2?'map':i===3?'graphic':'text',i===0?90:165);s.visual.headline=role;if(paragraphs[i])s.narration=paragraphs[i];return s;});
 // Preserve every supplied paragraph, including scripts longer than the template.
 for(let i=5;i<paragraphs.length;i++){const s=newHybridShot('shot-'+(i+1),'text',150);s.narration=paragraphs[i];e.scenes.push(s);}
 let cursor=0;for(const s of e.scenes){s.startFrame=cursor;cursor+=s.durationFrames;}e.format.durationFrames=cursor;
 e.direction={version:1,intensity:'balanced',scenes:e.scenes.map((s:any)=>defaultPlan(s.id))};e.notes=['Hybrid Shorts template: placeholders require the author’s own sourced facts.'];return e;
}
