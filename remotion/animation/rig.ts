import type {Rig,RigAnimation} from './schema';
import {clamp,smooth,random} from '../characters/animations/state.ts';
export type Vec=[number,number,number];
export type Bone={id:string;parent:string|null;at:Vec;size?:Vec;offset?:Vec;material?:number;detail?:number};
export const armCount=(r:Rig)=>r.archetype==='servitor'?0:['humanoid','dreg'].includes(r.archetype)?2:4;
export function rigBones(r:Rig):Bone[]{
 if(r.archetype==='servitor')return [{id:'pelvis',parent:null,at:[0,1.25,0],size:[1.2,1.2,1.2],material:0},{id:'head',parent:'pelvis',at:[0,0,.62],size:[.46,.46,.12],material:2},{id:'halo',parent:'pelvis',at:[0,0,0],size:[1.48,.22,.3],material:1,detail:1}];
 const bulky=r.archetype==='captain'?1.3:r.archetype==='dreg'?.8:1,w=r.width*bulky,l=r.limbLength;
 const bones:Bone[]=[{id:'pelvis',parent:null,at:[0,.94*l,0],size:[.62*w,.28,.38],material:0},{id:'torso',parent:'pelvis',at:[0,.25,0],size:[.8*w,.65,.43],offset:[0,.28,0],material:0},{id:'head',parent:'torso',at:[0,.92,0],size:[.56,.5,.48],material:1},
 {id:'eyes',parent:'head',at:[0,.08,.25],size:[.38,.08,.05],material:2},...[-1,1].map(side=>({id:'eye-'+side,parent:'head',at:[side*.14,.21,.25] as Vec,size:[.07,.07,.04] as Vec,material:2,detail:2})),...[-1,1].map(side=>({id:'mandible-'+side,parent:'head',at:[side*.24,-.16,.24] as Vec,size:[.12,.25,.16] as Vec,material:0,detail:1}))];
 for(const [side,name] of [[-1,'L'],[1,'R']] as const){
  bones.push({id:'hip'+name,parent:'pelvis',at:[side*.22*w,-.05,0],size:[.23,.43*l,.27],offset:[0,-.215*l,0],material:0},{id:'knee'+name,parent:'hip'+name,at:[0,-.43*l,0],size:[.21,.4*l,.24],offset:[0,-.2*l,0],material:1},{id:'foot'+name,parent:'knee'+name,at:[0,-.4*l,.08],size:[.29,.15,.43],material:0});
  for(let row=0;row<armCount(r)/2;row++){const key=(row?'lower':'upper')+name;
   bones.push({id:'shoulder-'+key,parent:'torso',at:[side*.51*w,.56-row*.38,0],size:[.22,.38*l,.23],offset:[0,-.19*l,0],material:row?1:0},{id:'elbow-'+key,parent:'shoulder-'+key,at:[0,-.38*l,0],size:[.2,.33*l,.21],offset:[0,-.165*l,0],material:1},{id:'hand-'+key,parent:'elbow-'+key,at:[0,-.35*l,.03],size:[.23,.17,.26],material:0});
   bones.push({id:'finger-'+key,parent:'hand-'+key,at:[side*.1,-.04,.14],size:[.07,.14,.16],material:1,detail:2});
   if(r.archetype==='captain'&&row===0)bones.push({id:'armor-'+key,parent:'shoulder-'+key,at:[0,0,0],size:[.45,.27,.5],material:1,detail:1});
  }
 }
 if(['elder','civilian'].includes(r.archetype))bones.push({id:'sash',parent:'torso',at:[0,.3,.25],size:[.16,.7,.07],material:1},{id:'coat',parent:'pelvis',at:[0,-.2,-.23],size:[.68*w,.75,.1],material:1,detail:1});
 if(r.archetype==='vandal')bones.push({id:'pack',parent:'torso',at:[0,.35,-.3],size:[.44,.55,.22],material:1,detail:1});
 if(r.archetype==='elder')bones.push({id:'staff',parent:'hand-lowerR',at:[.1,-.1,.1],size:[.08,1.4,.08],material:1});
 return bones;
}
export type Pose={rotation:Record<string,Vec>;lift:number;yaw:number};
export function animationPose(animation:RigAnimation,frame:number,seed:number,duration=90,reduced=false):Pose{
 const t=frame/30,phase=random(seed,0)*6.28,s=Math.sin(t*(animation==='walk'?6:animation==='sprint'?13:10)+phase),p=smooth(frame/Math.max(1,duration-1));
 const pose:Pose={rotation:{pelvis:[0,0,0],torso:[0,0,0],head:[0,0,0]},lift:Math.sin(t*2+phase)*.012,yaw:0};
 const set=(id:string,x=0,y=0,z=0)=>{pose.rotation[id]=[x,y,z];};
 const moving=['walk','run','sprint','flee','stop'].includes(animation),fast=animation!=='walk',fade=animation==='stop'?1-p:1;
 if(moving){const k=(animation==='sprint'?1:fast?.75:.4)*fade;pose.lift=Math.abs(s)*.045*fade;set('torso',fast?.16:0,Math.sin(t*3+phase)*.035);for(const [side,name]of [[-1,'L'],[1,'R']]as const){set('hip'+name,s*side*k);set('knee'+name,Math.max(0,-s*side)*k*1.4);set('foot'+name,-Math.max(0,-s*side)*k*.4);for(let row=0;row<2;row++){const key=(row?'lower':'upper')+name;set('shoulder-'+key,-s*side*k*(row?.55:1),0,side*.12);set('elbow-'+key,-.25-Math.max(0,s*side)*.5);}}}
 else for(const side of ['L','R'])for(const row of ['upper','lower'])set('elbow-'+row+side,-.14);
 switch(animation){
 case 'turn':pose.yaw=Math.PI*p;break;
 case 'look-around':set('head',0,Math.sin(t*1.2+phase)*.65);break;
 case 'point':set('shoulder-upperR',-1.45,0,-.2);set('elbow-upperR',-.12);set('head',-.12,.3);break;
 case 'talk-gesture':for(const side of ['L','R']){set('shoulder-upper'+side,-.4+Math.sin(t*3+(side==='L'?0:1))*.25);set('elbow-upper'+side,-.55+Math.sin(t*4)*.2);}set('torso',0,Math.sin(t*2)*.05);break;
 case 'react':set('torso',-.1,0,.07*Math.sin(p*Math.PI));set('head',-.45);for(const side of ['L','R'])set('shoulder-upper'+side,-.8);break;
 case 'fear':set('torso',.22);set('head',-.2,Math.sin(t*3+phase)*.18);for(const side of ['L','R']){set('shoulder-upper'+side,-.9);set('elbow-upper'+side,-.9);}break;
 case 'fall':set('pelvis',0,0,1.4*p);pose.lift=-.65*p;break;
 case 'kneel':set('hipR',-.8);set('kneeR',1.5);set('hipL',-.4);set('kneeL',.8);set('torso',.15);pose.lift=-.5;break;
 case 'celebrate':for(const [side,name]of [[-1,'L'],[1,'R']]as const){set('shoulder-upper'+name,-2.5,0,side*.2);set('elbow-upper'+name,-.4+Math.sin(t*4)*.2);}break;
 case 'look-at-sky':set('head',-.65);set('torso',-.08);break;
 }
 if(reduced){pose.lift=0;for(const key of ['torso','head'])if(['idle','look-around','talk-gesture','fear','celebrate'].includes(animation))pose.rotation[key]=[0,0,0];}
 return pose;
}
export function blendPose(a:Pose,b:Pose,t:number):Pose{const p=clamp(t),rotation:Record<string,Vec>={};for(const id of new Set([...Object.keys(a.rotation),...Object.keys(b.rotation)])){const x=a.rotation[id]??[0,0,0],y=b.rotation[id]??[0,0,0];rotation[id]=x.map((v,i)=>v+(y[i]-v)*p) as Vec;}return {rotation,lift:a.lift+(b.lift-a.lift)*p,yaw:a.yaw+(b.yaw-a.yaw)*p};}
export function poseForRig(r:Rig,animation:RigAnimation,frame:number,duration=90,reduced=false):Pose{
 const p=animationPose(animation,frame,r.seed,duration,reduced);if(r.archetype==='servitor'&&animation==='celebrate'&&!reduced){p.lift+=Math.sin(frame/12)*.1;p.rotation.pelvis[1]+=Math.sin(frame/18)*.3;}return p;
}
export function adaptRigPose(r:Rig,p:Pose):Pose{
 if(r.archetype!=='servitor')return p;const root=p.rotation.pelvis??[0,0,0],torso=p.rotation.torso??[0,0,0],head=p.rotation.head??[0,0,0];return {...p,rotation:{pelvis:root.map((v,i)=>v+torso[i]+head[i]) as Vec,head:[0,0,0]}};
}
export function rigPose(r:Rig,local:number,reduced=false,fallback?:Pose):Pose{
 const base=fallback??poseForRig(r,r.animation,local+r.phaseOffset,90,reduced),clip=r.clips.find(c=>local>=c.startFrame&&local<c.startFrame+c.durationFrames);if(!clip)return adaptRigPose(r,base);
 const f=local-clip.startFrame,w=smooth(f/Math.max(1,clip.transitionFrames))*smooth((clip.durationFrames-f)/Math.max(1,clip.transitionFrames));return adaptRigPose(r,blendPose(base,poseForRig(r,clip.animation,f+r.phaseOffset,clip.durationFrames,reduced),w));
}
// Pure forward kinematics for tests, framing and attachment tools.
export function jointPositions(bones:Bone[],pose:Pose):Record<string,Vec>{
 const result:Record<string,Vec>={},transforms:Record<string,{p:Vec;m:number[][]}>={},identity=[[1,0,0],[0,1,0],[0,0,1]];
 const mul=(a:number[][],b:number[][])=>a.map(row=>b[0].map((_,j)=>row.reduce((s,v,k)=>s+v*b[k][j],0)));
 for(const bone of bones){const parent=bone.parent?transforms[bone.parent]:{p:[0,0,0] as Vec,m:identity};if(!parent)throw new Error('Rig parent must precede child');const [x,y,z]=pose.rotation[bone.id]??[0,0,0],cx=Math.cos(x),sx=Math.sin(x),cy=Math.cos(y),sy=Math.sin(y),cz=Math.cos(z),sz=Math.sin(z),rot=mul(mul([[1,0,0],[0,cx,-sx],[0,sx,cx]],[[cy,0,sy],[0,1,0],[-sy,0,cy]]),[[cz,-sz,0],[sz,cz,0],[0,0,1]]);const p=parent.p.map((v,i)=>v+parent.m[i].reduce((s,n,j)=>s+n*bone.at[j],0)) as Vec;transforms[bone.id]={p,m:mul(parent.m,rot)};result[bone.id]=p;}
 return result;
}
