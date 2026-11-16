import React,{useMemo} from 'react';
import {AbsoluteFill,Audio,Composition,Img,Sequence,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import {validateEpisodeTimeline,type CompleteEpisodeProps,type EpisodeScene} from './episode_timeline';
import {cueAt,groupWords} from './cinematic_captions';
type DirectedScene=EpisodeScene&{frameSources:string[]};
type Props=Omit<CompleteEpisodeProps,'scenes'>&{scenes:DirectedScene[]};
const checked=(p:Props)=>{validateEpisodeTimeline(p);for(const s of p.scenes)if(s.frameSources.length!==s.durationFrames||s.frameSources.some(x=>!/^scenes\/[a-z0-9-]+\/frames\/[a-z0-9-]+\/frame-\d{4}\.png$/.test(x)))throw Error('Incomplete directed image sequence');return p;};
const Scene:React.FC<{scene:DirectedScene;fps:number;height:number}>=({scene,fps,height})=>{
 const f=useCurrentFrame(),t=f/fps;const cues=useMemo(()=>groupWords(scene.words),[scene.words]);const cue=cueAt(cues,t);
 // Fade image only; never overlap, fade, accelerate or move original speech.
 const opacity=Math.min(1,(f+1)/8,(scene.durationFrames-f)/8);
 return <AbsoluteFill><Img src={staticFile(scene.frameSources[f])} style={{width:'100%',height:'100%',objectFit:'contain',opacity}}/><Audio src={staticFile(`scenes/${scene.id}/speech.wav`)}/>
 {t<5&&<div style={{position:'absolute',top:'6%',left:'8%',right:'16%',color:'white',fontFamily:'sans-serif',fontSize:height*.027,textShadow:'0 2px 5px black'}}>{scene.title&&<strong>{scene.title}<br/></strong>}{scene.label}</div>}
 {scene.id==='04-time'&&<div style={{position:'absolute',top:'14%',left:'8%',right:'16%',color:'#e3efff',fontFamily:'sans-serif',fontSize:height*.022,textShadow:'0 2px 4px black'}}>Vault-local timelines · visual reconstruction</div>}
 {cue&&<div style={{position:'absolute',bottom:'20%',left:'8%',right:'16%',textAlign:'center',fontFamily:'sans-serif',fontWeight:700,fontSize:height*.037,lineHeight:1.22,color:'white',background:'rgba(4,9,17,.80)',borderRadius:8,padding:'8px 10px',textShadow:'0 1px 3px black'}}>{cue.words.map((w,i)=><React.Fragment key={i}><span style={{color:t>=w.start&&t<w.end?'#aeeaff':'white'}}>{w.text}</span>{i<cue.words.length-1?' ':''}</React.Fragment>)}</div>}
 </AbsoluteFill>;
};
const Episode:React.FC<Props>=props=>{const p=checked(props);return <AbsoluteFill style={{background:'black'}}>{p.scenes.map(s=><Sequence key={s.id} from={s.startFrame} durationInFrames={s.durationFrames}><Scene scene={s} fps={p.fps} height={p.height}/></Sequence>)}</AbsoluteFill>;};
const defaults:Props={width:360,height:640,fps:30,frames:1,scenes:[{id:'preview',title:'',label:'Preview',startFrame:0,durationFrames:1,words:[],frameSources:['scenes/preview/frames/shot/frame-0000.png']}]};
const Root=()=> <Composition id="CinematicAtheonEpisode" component={Episode} width={360} height={640} fps={30} durationInFrames={1} defaultProps={defaults} calculateMetadata={({props})=>{const p=checked(props);return {width:p.width,height:p.height,fps:p.fps,durationInFrames:p.frames};}}/>;
registerRoot(Root);
