import {characterVisual} from '../characters/index.ts';
import {resolveAtlas} from '../atlas/index.ts';
import type {AtlasReference} from '../atlas/index';
import type {LivingWorld,LivingShot} from './schema';
import {expandGroup} from '../characters/animations/state.ts';
export function directWorld(world:LivingWorld|undefined,shot?:LivingShot){return [...(shot?.cast??world?.cast??[]),...(shot?.groups??world?.groups??[]).flatMap(expandGroup)].slice(0,32);}
// Independent partial orders; no invented ordering between Riis and human history.
const eraChains=[['golden-age','post-collapse','dark-age','city-age','red-war','post-forsaken','beyond-light','post-sagira'],['ancient','post-pact','post-oryx'],['pre-whirlwind','post-whirlwind'],['golden-age','post-exo-program']];
const later=(candidate:string,era:string)=>eraChains.some(chain=>chain.includes(candidate)&&chain.includes(era)&&chain.indexOf(candidate)>chain.indexOf(era));
export function loreWarnings(world:LivingWorld|undefined,reference?:AtlasReference,shot?:LivingShot,legacyActors?:{guardian:boolean;ghost:boolean}){
 if(!world&&!shot)return [];
 const warnings:string[]=[],atlas=reference?resolveAtlas(reference):undefined;
 const era=world?.era??atlas?.variant?.eras[0]??atlas?.location.eras[0],krill=reference?.locationId==='fundament'&&reference.variantId==='krill-origins';
 if(world?.mode==='alternate-history')warnings.push('HISTOIRE ALTERNATIVE — ne représente pas un fait du canon.');
 if(!era)warnings.push('Époque inconnue : cohérence historique non vérifiée.');
 if((krill||era==='golden-age'||era==='pre-whirlwind')&&(legacyActors?.guardian||legacyActors?.ghost))warnings.push('Gardien/Spectre moderne visible avant son apparition.');
 for(const a of directWorld(world,shot)){
  const {variant:v,visual}=characterVisual(a.characterId,a.variantId);
  const label=a.id.includes(':')?a.id.split(':')[0]+' (groupe)':a.id;
  if(krill&&v.civilization!=='krill')warnings.push(`${label} : civilisation incompatible avec Fundament avant la Ruche.`);
  if(era&&v.eras.length&&v.eras.every(e=>later(e,era)))warnings.push(`${label} : variante postérieure à l’époque choisie (${v.eras.join(', ')}).`);
  if(visual.certainty!=='stylized-documented')warnings.push(`${label} : apparence ${visual.certainty==='unknown'?'inconnue, modèle masqué':'reconstituée artistiquement'}, non officielle.`);
  if(world?.mode==='canonical'&&(a.palette||a.equipment))warnings.push(`${label} : équipement/palette personnalisé, reconstitution visuelle.`);
 }return [...new Set(warnings)];
}
export function narrativeLabel(world?:LivingWorld){return world?.mode==='alternate-history'?'ALTERNATE HISTORY · NOT CANON':world?'ARTISTIC RECONSTRUCTION · STYLIZED CHARACTERS':undefined;}
