import {createHash} from 'node:crypto';
import {Matrix4,Vector3,Quaternion,Euler,PerspectiveCamera,Color} from 'three';
import {episodeSchema,validateWords} from '../src/voxel/episode/schema.ts';
import {resolveDirection,estimatedWords,atFrame} from '../src/voxel/cinematic/timeline.ts';
import {voxelVisualEpisode} from '../hybrid/adapter.ts';
import {cameraState} from '../src/voxel/cinematic/motion.ts';
import {directCamera} from '../polish/camera.ts';
import {composeCamera} from '../animation/camera.ts';
import {evaluateStudio,lodFor} from '../animation/director.ts';
import {rigBones} from '../animation/rig.ts';
import {characterVisual} from '../characters/index.ts';
import {costumeVariation} from '../polish/characters.ts';
import {environmentBlocks,atmosphere,effectBudget} from '../polish/environment.ts';
import {environmentStyle,resolveEnvironment} from '../src/voxel/library/catalog.ts';
import {atlasRecipe} from '../atlas/recipes.ts';
import {weatherState} from '../weather/state.ts';
import {bridgeSchema} from './schema.ts';
import type {BridgeScene} from './schema';
type Vec=[number,number,number];
const transform=(position:Vec,rotation:Vec=[0,0,0],scale:Vec=[1,1,1])=>new Matrix4().compose(new Vector3(...position),new Quaternion().setFromEuler(new Euler(...rotation,'XYZ')),new Vector3(...scale));
export function exportFrame(input:unknown,frame:number,profile:'standard'|'cinematic'='standard'):BridgeScene{
 const e=episodeSchema.parse(input);if(!Number.isInteger(frame)||frame<0||frame>=e.format.durationFrames)throw new Error('Frame must be an integer inside the project');
 if(!e.direction||!['HybridShort','VoxelCinematicEpisode'].includes(e.render.composition))throw new Error('Bridge requires a directed cinematic/Hybrid scene; historical projects remain unchanged');
 const source=e.scenes.find(s=>frame>=s.startFrame&&frame<s.startFrame+s.durationFrames)!;
 if(e.render.composition==='HybridShort'&&source.visual?.type!=='voxel')throw new Error('Choose a voxel frame; maps, text, timeline and captions remain in Remotion');
 const words=e.shorts?.alignedWords?validateWords(e.shorts.alignedWords,e):undefined,project=e.render.composition==='HybridShort'?voxelVisualEpisode(e):e;
 const timeline=resolveDirection(project,words??estimatedWords(project)),resolved=atFrame(timeline,frame),{scene,shot,events}=resolved,local=frame-scene.start;
 if(shot.actors.guardian||shot.actors.ghost)throw new Error('Legacy Guardian/Ghost models are not supported by bridge v1; no actor was dropped');
 const actors=evaluateStudio(source.livingWorld,shot.livingWorld,local,false,shot.start-scene.start),studio=shot.livingWorld?.studio??source.livingWorld?.studio;
 const unsupported=actors.filter(a=>a.active&&!a.actor.rig);if(unsupported.length)throw new Error('Bridge v1 requires rig 0.7 for active actors: '+unsupported.map(a=>a.actor.id).join(', '));
 const base=directCamera(cameraState(timeline,scene,shot,frame,events),source.polish?.camera,local),camera=composeCamera(base,studio?.camera,actors,local);
 const cameraObject=new PerspectiveCamera(camera.fov,1080/1920,.1,400);cameraObject.position.set(...camera.position);cameraObject.lookAt(new Vector3(...camera.target));cameraObject.updateMatrixWorld();
 const env=resolveEnvironment(shot.environment,source.location),atlas=shot.atlas??(shot.environment==='scene'?source.atlas:undefined),recipe=atlas?atlasRecipe(atlas):undefined;
 const style=recipe?{...environmentStyle(env),sky:recipe.palette.sky,key:recipe.palette.accent,fill:'#9baed7',ambient:1.1}:environmentStyle(env),atmo=source.polish?.environment?atmosphere(source.polish.environment,local):undefined;
 const weather=shot.weather??source.weather,ws=weather?weatherState(weather,local):undefined,light=(ws?.active?ws.light:1)*(atmo?.light??1);
 const omissions=['Atlas/base stage is an explicitly simplified reconstruction: procedural blocks and a ground only.','Sky gradient, fog, particles, contact-shadow decals and visual event effects are not exported.','Narration, captions, montage and transitions remain in the original Remotion project.'];
 if(weather)omissions.push('Weather geometry is not exported; only its current lighting multiplier is retained.');
 if((shot.elements??source.elements??[]).length)omissions.push('Legacy voxel elements are not exported by bridge v1.');
 if(!words)omissions.push('Camera cue timing is estimated because inline aligned words are absent.');
 const result:BridgeScene={format:'destiny-blender-scene',version:1,exporterVersion:'0.8.1',coordinateSystem:'RIGHT_HANDED_Y_UP',matrixLayout:'column-major',profile,
 source:{projectId:e.id,projectVersion:e.schemaVersion,projectSha256:createHash('sha256').update(JSON.stringify(input)).digest('hex'),sceneId:source.id,shotId:shot.id,frame,localFrame:local,fps:30,timing:words?'aligned':'estimated',loreMode:e.shorts?.mode??source.livingWorld?.mode??'reconstruction',visualStatus:'artistic-reconstruction',...(atlas?{atlas}:{}),sourceIds:[...new Set([...(source.visual?.sources??[]),...actors.filter(a=>a.active).flatMap(a=>characterVisual(a.actor.characterId,a.actor.variantId).variant.sources)])]},
 resolution:{width:1080,height:1920},camera:{matrixWorld:cameraObject.matrixWorld.toArray(),position:camera.position,target:camera.target,verticalFov:camera.fov,near:.1,far:400},world:{color:atmo?.sky??style.sky,ambient:style.ambient*light},
 lights:[{id:'key',type:'sun',position:[4,7,5],target:[0,0,0],color:style.key,intensity:2.4*light},{id:'fill',type:'sun',position:[-5,4,-3],target:[0,0,0],color:style.fill,intensity:2*light}],materials:[],actors:[],meshes:[],omissions};
 const material=(color:string,emission=false)=>{const id='mat-'+color.slice(1).toLowerCase()+(emission?'-emission':'');if(!result.materials.some(m=>m.id===id))result.materials.push({id,color,emission,roughness:1});return id;};
 const box=(id:string,position:Vec,size:Vec,color:string,rotation:Vec=[0,0,0])=>result.meshes.push({id,geometry:'box',material:material(color),matrixWorld:transform(position,rotation,size).toArray()});
 box('ground',[0,-.075,0],[36,.15,36],'#68747f');
 if(source.polish?.environment){const budget=effectBudget(e.shorts?.polish,'final');environmentBlocks(source.polish.environment,local,budget.details).forEach((b,i)=>box('environment-'+i,b.position,b.size,b.color,[0,0,b.rotation]));result.lights.push({id:'atmosphere-rim',type:'sun',position:[-6,8,-8],target:[0,0,0],color:atmo!.horizon,intensity:atmo!.light*1.5});}
 for(const prop of source.livingWorld?.props??[]){box('prop-'+prop.id, [prop.position[0],prop.position[1]+.65,prop.position[2]],[.8,1.3,.5],'#67788d');box('prop-'+prop.id+'-screen',[prop.position[0],prop.position[1]+1,prop.position[2]+.27],[.65,.5,.05],'#72e3ee');}
 for(const s of actors){if(!s.active)continue;const a=s.actor,r=a.rig!,visual=characterVisual(a.characterId,a.variantId).visual,variation=costumeVariation(a),palette=a.palette??visual.palette;
  const body=a.director?'#'+new Color(palette[0]).offsetHSL(variation.hue,.02,0).getHexString():palette[0],materials=[material(body),material(palette[1]),material(palette[2],true)];
  const root=transform([s.position[0],s.position[1]+s.pose.lift+(r.archetype==='servitor'?Math.sin((r.seed+s.pose.lift)*.1)*.015:0),s.position[2]],[0,s.yaw,0],[s.scale*variation.width,s.scale,s.scale]),matrices=new Map<string,Matrix4>(),lod=lodFor(studio?.profile??'balanced',Math.hypot(...s.position.map((v,j)=>v-camera.position[j])));
  const actor:BridgeScene['actors'][number]={id:a.id,characterId:a.characterId,...(a.variantId?{variantId:a.variantId}:{}),rigArchetype:r.archetype,position:s.position,yaw:s.yaw,rootMatrix:root.toArray(),joints:[]};
  for(const b of rigBones(r)){const parent=b.parent?matrices.get(b.parent)!:root,m=parent.clone().multiply(transform(b.at,s.pose.rotation[b.id]??[0,0,0]));matrices.set(b.id,m);actor.joints.push({id:b.id,parent:b.parent,matrixWorld:m.toArray()});if(b.size&&(b.detail??0)<=lod)result.meshes.push({id:a.id+'/'+b.id,actorId:a.id,geometry:r.archetype==='servitor'&&b.id==='pelvis'?'sphere':'box',material:materials[b.material??0],matrixWorld:m.clone().multiply(transform(b.offset??[0,0,0],[0,0,0],b.size)).toArray()});}
  result.actors.push(actor);if((a.equipment??visual.equipment).length)result.omissions.push(a.id+': additional equipment panels from the Three.js renderer are omitted; base rig accessories are retained.');
 }
 return bridgeSchema.parse(result);
}
