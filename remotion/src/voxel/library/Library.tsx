import React,{useLayoutEffect,useMemo,useRef} from 'react';
import {Color,InstancedMesh,Matrix4,Quaternion,Vector3} from 'three';
import {Block,Guardian,Ghost} from '../Models';
import {Tower,Traveler} from '../episode/Environment';
import {actorPose} from '../cinematic/motion';
import type {TimedAction} from '../cinematic/timeline';
import {environmentBoxes,elementParticle} from './layout';
import type {VoxelBox} from './layout';
import {defaultElementAnimation} from './catalog';
import type {Location,VoxelElement} from './catalog';

export const VoxelBatch:React.FC<{boxes:VoxelBox[]}>=({boxes})=>{
  const mesh=useRef<InstancedMesh>(null);
  useLayoutEffect(()=>{
    const matrix=new Matrix4(),rotation=new Quaternion(),color=new Color();
    boxes.forEach((box,i)=>{
      matrix.compose(new Vector3(...box.position),rotation,new Vector3(...box.size));
      mesh.current!.setMatrixAt(i,matrix);mesh.current!.setColorAt(i,color.set(box.color));
    });
    mesh.current!.instanceMatrix.needsUpdate=true;
    if(mesh.current!.instanceColor)mesh.current!.instanceColor.needsUpdate=true;
  },[boxes]);
  return <instancedMesh ref={mesh} args={[undefined,undefined,boxes.length]} frustumCulled={false}>
    <boxGeometry args={[1,1,1]}/>
    {boxes[0]?.emissive?<meshBasicMaterial/>:<meshStandardMaterial roughness={.9}/>}
  </instancedMesh>;
};
const Batches:React.FC<{boxes:VoxelBox[]}>=({boxes})=><group>
  <VoxelBatch boxes={useMemo(()=>boxes.filter(b=>!b.emissive),[boxes])}/>
  <VoxelBatch boxes={useMemo(()=>boxes.filter(b=>b.emissive),[boxes])}/>
</group>;
export const VoxelEnvironment:React.FC<{location:Location;halo?:boolean}>=({location,halo=false})=>{
  const boxes=useMemo(()=>environmentBoxes(location),[location]);
  return <group>
    {location==='the-tower'&&<><Tower/><Traveler halo={halo}/></>}
    <Batches boxes={boxes}/>
  </group>;
};
const ParticleField:React.FC<{item:VoxelElement;frame:number}>=({item,frame})=>{
  const boxes=Array.from({length:item.count??24},(_,i)=>{
    const p=elementParticle(item,i,frame);
    return {position:p.position,size:[p.scale,p.scale,p.scale] as [number,number,number],color:item.type==='snow'?'#dcecf5':item.type==='light-fragments'?'#ffe8a3':'#8deaff',emissive:true};
  });
  return <VoxelBatch boxes={boxes}/>;
};
export const VoxelElements:React.FC<{items:VoxelElement[];frame:number}>=({items,frame})=><group>
  {items.map(item=><LibraryElement key={item.id} item={item} frame={frame}/>)}
</group>;
const LibraryElement:React.FC<{item:VoxelElement;frame:number}>=({item,frame})=>{
  const animation=item.animation??defaultElementAnimation(item.type),t=frame/30;
  const pulse=animation==='pulse'?1+Math.sin(t*2+(item.seed??0))*.035*(item.strength??.65):1;
  const walk:TimedAction={id:item.id,actor:'guardian',animation:'walk',start:0,end:180,durationFrames:180,
    at:{sceneFrame:0},from:[-.8,0,0],to:[.8,0,0],height:0,purpose:'Reusable background Guardian patrol'};
  const phase=((frame%360)+360)%360;
  const pose=actorPose('guardian',[walk],phase<180?phase:359-phase,'balanced');
  if(phase>=180)pose.rotation[1]+=Math.PI;
  return <group position={item.position} rotation={item.rotation} scale={(item.scale??1)*pulse}>
    {item.type==='guardian'?<Guardian rise={1} t={t} pose={animation==='walk'?pose.joints:undefined}
      position={animation==='walk'?pose.position:[0,0,0]} rotation={animation==='walk'?pose.rotation:[0,0,0]}/>:
      item.type==='ghost'?<Ghost t={animation==='still'?0:t} position={[0,animation==='hover'?Math.sin(t*2.2)*.12:0,0]}/>:
      item.type==='vex-structure'?<group>
        <Block position={[0,.25,0]} size={[2.2,.5,2.2]} color="#555c51"/>
        {[-1,1].map(side=><group key={side}><Block position={[side*.75,1.5,0]} size={[.4,2.2,.6]} color="#8d8665"/>
          <Block position={[side*.5,1.5,.34]} size={[.08,1.7,.08]} color="#a8efd1" emissive/></group>)}
        <Block position={[0,2.5,0]} size={[1.9,.4,.7]} color="#8d8665"/>
      </group>:
      item.type==='crystal'?<group>
        {[-1,0,1].map((i)=><group key={i} position={[i*.4,.1,Math.abs(i)*.2]} rotation={[0,0,-i*.2]}>
          <Block position={[0,.65,0]} size={[.4,1.3-Math.abs(i)*.35,.4]} color="#75bad2"/>
          <Block position={[0,1.35-Math.abs(i)*.2,0]} size={[.23,.3,.23]} color="#b4f6f2" emissive/>
        </group>)}
      </group>:<ParticleField item={item} frame={frame}/>}
  </group>;
};
