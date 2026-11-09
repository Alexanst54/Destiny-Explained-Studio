import {rigSchema} from './schema.ts';
export const eliksniPack=[
 {id:'dreg',characterId:'eliksni-dreg',label:'Dreg — deux bras',height:1.65,width:.85,animation:'look-around',source:'wiki-eliksni-dreg',period:'modern'},
 {id:'vandal',characterId:'eliksni-vandal',label:'Vandal — quatre bras',height:2.3,width:.9,animation:'walk',source:'wiki-eliksni-vandal',period:'modern'},
 {id:'captain',characterId:'eliksni-captain',label:'Captain — quatre bras',height:2.9,width:1.2,animation:'point',source:'wiki-eliksni-captain',period:'modern'},
 {id:'servitor',characterId:'eliksni-servitor',label:'Servitor — machine flottante',height:2.2,width:1,animation:'idle',source:'wiki-eliksni-servitor',period:'unknown'},
 {id:'civilian',characterId:'eliksni-civilian',label:'Civil éliksni — reconstitution',height:2.3,width:1,animation:'talk-gesture',source:'wiki-eliksni-civilian',period:'reconstruction'},
 {id:'elder',characterId:'eliksni-elder',label:'Ancien — rôle artistique',height:2.4,width:.95,animation:'look-around',source:'wiki-eliksni-civilian',period:'reconstruction'},
] as const;
export function packRig(id:string,seed=42){const p=eliksniPack.find(p=>p.id===id);if(!p)throw new Error('Unknown Eliksni archetype');return rigSchema.parse({version:1,archetype:p.id,height:p.height,width:p.width,animation:p.animation,seed});}
