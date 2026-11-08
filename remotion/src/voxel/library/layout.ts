import {particleSeed} from '../timeline.ts';
import type {Location,VoxelElement} from './catalog';
export type Vec3 = [number,number,number];
export type VoxelBox = {position:Vec3;size:Vec3;color:string;emissive?:boolean};
// Box palettes are batched by material: hundreds of blocks, only a few draw calls.
export const environmentBoxes = (location:Location):VoxelBox[] => {
  const boxes:VoxelBox[]=[];
  const box=(position:Vec3,size:Vec3,color:string,emissive=false)=>boxes.push({position,size,color,emissive});
  if(location==='the-tower'){
    // The original balcony/Traveler remain the foreground; the City gains depth.
    for(let i=0;i<32;i++){
      const x=(i-15.5)*.85,h=1.1+particleSeed(i,31)*4.2,z=-13-particleSeed(i,32)*5;
      box([x,h/2-.8,z],[.65,h,.8],i%2?'#31475d':'#486078');
      for(let j=0;j<3;j++)box([x,h*(j+1)/4-.5,z+.42],[.15,.12,.04],'#f4d69a',true);
    }
    for(const side of [-1,1]){
      box([side*6,2,-5],[.7,4,.9],'#40566b');
      box([side*6,4.15,-5],[1.1,.3,1.3],'#8f9eaa');
      box([side*5.5,2.7,-4.9],[.5,1.8,.12],'#684b75');
      box([side*4.4,.035,-1],[.08,.05,4],'#a8dfe7',true);
    }
  }else if(location==='europa'){
    box([0,-.24,0],[30,.45,32],'#b6cfdf');
    box([0,-.005,1],[5,.05,9],'#779daf');
    for(const side of [-1,1])for(let i=0;i<7;i++){
      const x=side*(4+i*1.6),z=-5-particleSeed(i,14)*10,h=1.5+particleSeed(i,15)*5;
      box([x,h/2,z],[2.5,h,3],'#54788f');
      box([x,h+.12,z],[2.65,.3,3.1],'#d8e8ed');
      box([x-.5,h*.5,z+1.6],[.3,h*.65,.12],'#91dae5');
    }
    for(let i=0;i<5;i++)box([(i-2)*3,1+i%2,-18],[3,2+i%2,4],'#90adbd');
    box([-5,1.3,-3],[2.4,2.6,3],'#394c65');
    box([-5,2.7,-3],[2.7,.25,3.3],'#e4eff3');
    box([-5,1.6,-1.46],[1.6,.5,.09],'#f1b879',true);
    box([5,.22,1],[2.5,.4,2],'#d8e8ed');
  }else if(location==='black-garden'){
    box([0,-.25,0],[28,.5,30],'#314238');
    box([0,-.025,0],[4,.08,9],'#69786a');
    for(const side of [-1,1])for(let i=0;i<7;i++){
      const x=side*(3.8+i%3*2),z=2-i*2.1,h=.4+(i%3)*.45;
      box([x,h/2,z],[2.3,h,2.4],'#3d5146');
      box([x,h+.08,z],[2.5,.2,2.5],'#6b8055');
      for(let j=0;j<4;j++)box([x+(j%2-.5)*.6,h+.35,z+Math.floor(j/2)*.5],[.2,.35,.2],j%2?'#a95363':'#ca7c79');
    }
    // An open, square Vex gate: a focal point that does not block the actors.
    for(const side of [-1,1]){
      box([side*3.4,3,-10],[1.1,6,1.5],'#777355');
      box([side*2.77,3,-9.15],[.12,5,.12],'#a7d9ba',true);
      box([side*7,2,-8],[1.3,4,1.6],'#66684e');
    }
    box([0,6,-10],[7.9,1.1,1.5],'#8d8665');
    box([0,5.4,-9.15],[5.5,.12,.12],'#a7d9ba',true);
    for(let i=0;i<7;i++)box([(i-3)*2,1,-18],[1.6,2+(i%3),2],'#435748');
  }else{
    box([0,-.25,0],[24,.5,32],'#252535');
    box([0,.015,0],[4,.06,18],'#393748');
    // Stepped triangular ribs, entirely boxes, with an open central passage.
    for(const z of [-5,-11,-17])for(let row=0;row<9;row++){
      const x=7.7-row*.65;
      for(const side of [-1,1]){
        box([side*x,row+0.5,z],[1.6,1.05,1.3],'#373441');
        box([side*(x-.84),row+0.5,z+.68],[.1,.8,.09],'#d29857',true);
      }
    }
    for(const side of [-1,1]){
      box([side*8.8,4,-6],[1.4,8,25],'#24232f');
      box([side*2.7,.06,-2],[.08,.08,20],'#d29857',true);
    }
    box([0,.5,-9],[3,1,3],'#4b4250');
    for(let i=0;i<8;i++)box([0,2.1+i*.24,-10],[2.8-i*.3,.24,2.8-i*.3],i%3?'#3d3946':'#af8459');
  }
  return boxes;
};
const fract=(value:number)=>value-Math.floor(value);
// Pure, seekable particle coordinates; no delta time, random(), clocks or physics.
export const elementParticle = (item:VoxelElement,index:number,frame:number):{position:Vec3;scale:number} => {
  const seed=item.seed??0,noise=(channel:number)=>particleSeed(index+seed,channel);
  const animation=item.animation??(item.type==='snow'?'drift':item.type==='light-fragments'?'pulse':'drift');
  const t=animation==='still'?0:frame/30;
  const snow=item.type==='snow',storm=animation==='blizzard',strength=item.strength??.65;
  const speed=storm?2.2:0.55,extent=snow?13:4;
  const x=(fract(noise(40)+t*(storm?.095:.016)*strength)-.5)*extent;
  const y=snow?fract(noise(41)-t*.12*speed)*8:fract(noise(41)+t*.07)*4;
  const z=(noise(42)-.5)*(snow?16:4);
  const pulse=animation==='pulse'?.7+.3*Math.sin(t*2+index):1;
  return {position:[x,y,z],scale:(snow?.04:item.type==='light-fragments'?.1:.045)*(0.6+noise(43))*(.5+strength*.5)*pulse};
};
