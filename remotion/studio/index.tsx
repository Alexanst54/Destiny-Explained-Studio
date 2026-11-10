import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import {captionsAt,type Word} from './captions';
export type StudioProps={width:number;height:number;fps:number;frames:number;words:Word[];subtitles:boolean;music:boolean};
export const Studio:React.FC<StudioProps>=(p)=>{const frame=useCurrentFrame();const caption=captionsAt(p.words,frame/p.fps);return <AbsoluteFill style={{backgroundColor:'black'}}><Img src={staticFile(`frames/frame-${String(frame).padStart(6,'0')}.png`)} style={{width:'100%',height:'100%',objectFit:'contain'}}/><Audio src={staticFile('narration.wav')}/>{p.music&&<Audio src={staticFile('music.wav')} volume={0.12} loop/>}{p.subtitles&&caption&&<div style={{position:'absolute',bottom:'9%',left:'5%',right:'5%',textAlign:'center',color:'white',fontFamily:'sans-serif',fontWeight:700,fontSize:Math.max(18,p.height*.045),textShadow:'0 2px 5px black',backgroundColor:'rgba(0,0,0,.65)',padding:8,overflowWrap:'anywhere'}}>{caption}</div>}</AbsoluteFill>};
const defaults:StudioProps={width:320,height:240,fps:24,frames:48,words:[],subtitles:true,music:false};
const Root=()=> <Composition id="DestinyProductionStudio" component={Studio} width={320} height={240} fps={24} durationInFrames={48} defaultProps={defaults} calculateMetadata={({props})=>({width:props.width,height:props.height,fps:props.fps,durationInFrames:props.frames})}/>;
registerRoot(Root);
