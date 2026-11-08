import type {VoxelBox,Vec3} from '../src/voxel/library/layout';
import {particleSeed} from '../src/voxel/timeline.ts';
import type {AtlasRecipe} from './recipes';
import type {AtlasModule} from './schema';

// Each module emits bounded cubes. They share two instanced material batches.
export function moduleBoxes(module:AtlasModule,recipe:AtlasRecipe,frame:number):VoxelBox[]{
 const out:VoxelBox[]=[],{ground,structure,accent}=recipe.palette;
 const noise=(i:number,c:number)=>particleSeed(i+(recipe.seed%65536),c);
 const box=(p:Vec3,s:Vec3,color=structure,emissive=false)=>out.push({position:p,size:s,color,emissive});
 switch(module){
  case 'terrain':
   if(recipe.modules.includes('ocean')){
    box([0,-.2,1],[5.4,.4,7],ground);
    for(let i=0;i<10;i++)box([(i%2?1:-1)*(4+noise(i,1)*6),-.05+noise(i,2),-3-noise(i,3)*12],[2.8+noise(i,4)*2,.8+noise(i,5),3],ground);
   }else{box([0,-.25,0],[28,.5,30],ground);
    for(const side of [-1,1])for(let i=0;i<5;i++)box([side*(5+i*1.8),.3+noise(i,6),-5-noise(i,7)*10],[3.2,1+noise(i,8)*2.5,4],ground);}
   break;
  case 'human':
   for(const side of [-1,1])for(let i=0;i<4;i++){
    const x=side*(4.8+i*.75),y=1.2+i*.3,z=-3-i*3.2;
    box([x,y,z],[2.2,y*2,2.6]);box([x,y*2+.12,z],[2.5,.24,2.8],ground);
    box([x,y+.2,z+1.32],[1.1,.16,.06],accent,true);
   }break;
  case 'golden-age':
   for(const side of [-1,1])for(let i=0;i<3;i++){
    const x=side*(4.5+i),z=-4-i*4;
    box([x,2.6,z],[.6,5.2,.8]);box([x,5.2,z],[1.5,.3,1.4]);box([x,2.4,z+.44],[.1,4,.05],accent,true);
   }
   box([0,5.2,-12],[12,.35,1.5]);box([0,.25,-5],[4,.5,3]);break;
  case 'vex':
   for(const side of [-1,1]){
    box([side*3.5,3,-10],[1.2,6,1.3]);box([side*2.82,3,-9.3],[.12,5,.1],accent,true);
    for(let i=0;i<4;i++)box([side*(5+i*.6),.8+i*.4,-5-i*2],[1.6,1.6+i*.8,1.6]);
   }box([0,6,-10],[8,1,1.3]);break;
  case 'hive':
   for(const side of [-1,1])for(let i=0;i<4;i++){
    const x=side*(4.6+i*.6),z=-3-i*3;
    for(let j=0;j<5;j++)box([x,1+j*.9,z],[1.6-j*.24,.9,1.7-j*.22]);
    box([x,.9,z+1],[.3,1,.12],accent,true);
   }break;
  case 'cabal':
   for(const side of [-1,1]){
    box([side*5,2.5,-5],[3.8,5,5]);box([side*5,5,-5],[4.3,.6,5.3],ground);
    box([side*3.6,2.5,-2.45],[.24,3,.1],accent,true);
    for(let i=0;i<4;i++)box([side*5,1+i,-10],[4-i*.5,1,4]);
   }break;
  case 'eliksni':
   for(const side of [-1,1])for(let i=0;i<3;i++){
    const x=side*(4.5+i*1.3),z=-3-i*4;
    box([x,2.6+i*.8,z],[.6,5.2+i*1.6,.7]);
    box([x,4.9+i*.8,z],[1.7,.35,1.1]);
    for(let j=0;j<3;j++)box([x+side*(.3+j*.22),3.5-j*.5,z+.2],[.6,.4,.3],accent);
   }break;
  case 'awoken':
   for(const side of [-1,1])for(let i=0;i<4;i++){
    const x=side*(4.6+i*.8),z=-4-i*3;
    box([x,2.5+i*.35,z],[.5,5+i*.7,.6]);box([x,4+i*.3,z],[1.5,.2,1.2],accent,true);
    box([x,5.6+i*.35,z],[.28,.8,.3]);
   }box([0,.2,-5],[5,.4,3]);break;
  case 'pyramid':
   for(const z of [-6,-12])for(let row=0;row<8;row++)for(const side of [-1,1]){
    box([side*(7-row*.6),row+.5,z],[1.4,1,1.4]);box([side*(6.2-row*.6),row+.5,z+.73],[.08,.6,.08],accent,true);
   }break;
  case 'bray':
   for(const side of [-1,1]){
    box([side*5,1.7,-4],[2.8,3.4,3.2]);box([side*5,3.5,-4],[3.2,.3,3.5]);
    box([side*5,2,-2.35],[2,.6,.1],accent,true);
    for(let i=0;i<3;i++)box([side*(4+i),.5,-9],[1,.9,2],ground);
   }
   box([0,4.6,-12],[11,.6,1.5]);
   for(const side of [-1,1])box([side*4.8,2.2,-12],[1,4.4,1.5]);
   box([0,4.6,-11.2],[2.4,.18,.1],accent,true);break;
  case 'future-city':
   for(let i=0;i<16;i++){
    const x=(i-7.5)*1.5,h=2+noise(i,9)*5,z=-16-noise(i,10)*3;
    box([x,h/2,z],[1,h,1.4]);
    for(let j=0;j<3;j++)box([x,(j+1)*h/4,z+.73],[.14,.18,.06],accent,true);
   }break;
  case 'cosmic':
   for(let i=0;i<30;i++)box([(noise(i,11)-.5)*22,1+noise(i,12)*11,-7-noise(i,13)*12],[.06,.06,.06],accent,true);
   for(let i=0;i<5;i++)box([(i-2)*2.1,5.5+Math.abs(i-2)*.6,-12],[1,.2,1],structure);break;
  case 'vegetation':
   for(const side of [-1,1])for(let i=0;i<7;i++){
    const x=side*(3.7+noise(i,14)*4),z=-2-i*2;
    box([x,.1,z],[1.8,.3,1.8],'#65845c');
    for(let j=0;j<3;j++)box([x+(j-1)*.4,.45,z],[.18,.5,.18],j%2?'#d3ae98':'#96ac78');
   }break;
  case 'ocean':
   box([0,-.8,0],[34,.15,38],'#2d6875');
   for(let i=0;i<20;i++)box([(noise(i,15)-.5)*24,-.68,-2-noise(i,16)*17],[1+noise(i,17)*3,.04,.08],accent,true);break;
  case 'snow':
   for(let i=0;i<12;i++)box([(i%2?1:-1)*(4+noise(i,18)*6),.2,-2-noise(i,19)*17],[2,.5,2.7],'#d4e5eb');break;
  case 'weather':
   for(let i=0;i<12;i++){
    const drift=Math.sin(frame/240+noise(i,20)*6)*.35;
    box([(i-5.5)*2.5+drift,8+noise(i,21)*2,-9-noise(i,22)*7],[3.7,.35+noise(i,23)*.6,1.3],'#647e86');
   }break;
 }
 return out;
}
export const atlasBoxes=(recipe:AtlasRecipe,frame:number)=>recipe.modules.flatMap(module=>moduleBoxes(module,recipe,frame));
