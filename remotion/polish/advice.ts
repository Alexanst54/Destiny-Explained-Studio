import type {VoxelEpisodeDef} from '../src/voxel/episode/schema';
import {contrastRatio} from './captions.ts';
export type Advice={code:string;sceneId?:string;message:string};
const profiles={documentary:{hook:4,static:7,wpm:175,text:160,variation:13,transition:.14},mysterious:{hook:5,static:9,wpm:155,text:140,variation:16,transition:.16},epic:{hook:3,static:6,wpm:185,text:120,variation:10,transition:.18},explainer:{hook:4,static:8,wpm:170,text:200,variation:14,transition:.13}};
export function editingAdvice(e:VoxelEpisodeDef):Advice[]{
 const result:Advice[]=[],profile=profiles[e.shorts?.polish?.pacingProfile??'documentary'];
 const add=(code:string,message:string,sceneId?:string)=>result.push({code,message,sceneId});
 if(e.scenes[0].durationFrames/30>profile.hook)add('long-hook','Introduction longue : envisager une question plus rapide.',e.scenes[0].id);
 let transitionFrames=0,stillRun=0;
 for(const s of e.scenes){const seconds=s.durationFrames/30,v=s.visual,world=s.livingWorld;
  const moving=!!s.polish?.camera&&s.polish.camera.preset!=='none'||!!s.polish?.environment||v?.type==='map'||v?.type==='timeline'||v?.type==='graphic'||[...(world?.cast??[]),...(world?.groups??[]).map(g=>g.member)].some(a=>a.path||['walk','run','flee','talk','interact'].includes(a.animation));
  if(!moving&&seconds>profile.static)add('static-shot','Plan statique prolongé : suggérer un mouvement ou une révélation.',s.id);
  stillRun=moving?0:stillRun+seconds;if(stillRun>profile.variation)add('no-variation','Longue période sans variation visuelle.',s.id);
  const text=(v?.headline??'')+' '+(v?.type==='text'?v.body:v?.type==='graphic'?v.cards.map(c=>c.title+' '+c.body).join(' '):'');
  if(text.length>profile.text)add('dense-text','Texte chargé : répartir les idées entre plusieurs cartes.',s.id);
  if(s.narration.split(/\s+/).length*60/seconds>profile.wpm)add('fast-narration','Narration rapide pour ce profil : allonger le plan ou raccourcir le passage.',s.id);
  if(s.narration.split(/\s+/).some(w=>w.length>28))add('caption-risk','Mot long : vérifier la lisibilité des captions dans l’aperçu.',s.id);
  transitionFrames+=v?.transition.durationFrames??0;
 }
 if(transitionFrames/e.format.durationFrames>profile.transition)add('excessive-transitions','Transitions nombreuses ou longues : envisager davantage de coupes simples.');
 const c=e.shorts?.captions;if(c){if((c.fontSize??46)>58&&c.maxWords>4)add('caption-density','Grande police et longs segments : vérifier les zones sûres.');if(contrastRatio(c.color??'#f7fbff')<4.5||contrastRatio(c.accent??'#ffe297')<4.5)add('caption-contrast','Contraste faible : choisir des couleurs plus lisibles sur le fond sombre.');}
 return result;
}
