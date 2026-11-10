import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,Sequence,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import {captionsAt} from './captions';
import {sceneFrameSource,validateEpisodeTimeline,type CompleteEpisodeProps,type EpisodeScene} from './episode_timeline';
const Scene:React.FC<{scene:EpisodeScene;height:number;fps:number}>=({scene,height,fps})=>{
 const localFrame=useCurrentFrame();const caption=captionsAt(scene.words,localFrame/fps);
 return <AbsoluteFill><Img src={staticFile(sceneFrameSource(scene.id,localFrame))} style={{width:'100%',height:'100%',objectFit:'contain'}}/><Audio src={staticFile(`scenes/${scene.id}/speech.wav`)}/><div style={{position:'absolute',top:'4%',left:'5%',right:'5%',color:'white',fontFamily:'sans-serif',textShadow:'0 2px 5px black',fontSize:Math.max(14,height*.028),overflowWrap:'anywhere'}}>{scene.title&&<div style={{fontWeight:800}}>{scene.title}</div>}<div>{scene.label}</div></div>{caption&&<div style={{position:'absolute',bottom:'9%',left:'5%',right:'5%',textAlign:'center',color:'white',fontFamily:'sans-serif',fontWeight:700,fontSize:Math.max(18,height*.045),textShadow:'0 2px 5px black',backgroundColor:'rgba(0,0,0,.65)',padding:8,overflowWrap:'anywhere'}}>{caption}</div>}</AbsoluteFill>;
};
export const CompleteEpisode:React.FC<CompleteEpisodeProps>=(props)=>{const p=validateEpisodeTimeline(props);return <AbsoluteFill style={{backgroundColor:'black'}}>{p.scenes.map(s=><Sequence key={s.id} from={s.startFrame} durationInFrames={s.durationFrames}><Scene scene={s} height={p.height} fps={p.fps}/></Sequence>)}</AbsoluteFill>};
const defaults:CompleteEpisodeProps={width:360,height:640,fps:30,frames:1,scenes:[{id:'preview',label:'Preview',title:'',startFrame:0,durationFrames:1,words:[]}]};
const Root=()=> <Composition id="CompleteAtheonEpisode" component={CompleteEpisode} width={360} height={640} fps={30} durationInFrames={1} defaultProps={defaults} calculateMetadata={({props})=>{const p=validateEpisodeTimeline(props);return {width:p.width,height:p.height,fps:p.fps,durationInFrames:p.frames};}}/>;
registerRoot(Root);
