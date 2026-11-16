import React from 'react';
import {AbsoluteFill,Composition,Img,registerRoot,staticFile,useCurrentFrame} from 'remotion';
type Item={path:string;shotId:string;cameraId:string;sourceFrame:number;episodeFrame:number};
type Props={width:number;height:number;fps:number;items:Item[]};
const Movie:React.FC<Props>=({items,height})=>{const f=useCurrentFrame(),i=items[f];return <AbsoluteFill style={{background:'black'}}><Img src={staticFile(i.path)} style={{width:'100%',height:'100%'}}/><div style={{position:'absolute',left:'5%',right:'5%',top:'4%',color:'white',fontFamily:'sans-serif',fontSize:height*.024,background:'rgba(0,0,0,.75)',padding:8}}>MOTION DIAGNOSTIC · SILENT<br/>{i.shotId}<br/>Camera: {i.cameraId}<br/>Output {f} · source {i.sourceFrame} · episode {i.episodeFrame}</div></AbsoluteFill>;};
const Root=()=> <Composition id="AtheonMotionDiagnostic" component={Movie} width={540} height={960} fps={10} durationInFrames={30} defaultProps={{width:540,height:960,fps:10,items:[]}} calculateMetadata={({props})=>{if(![10,30].includes(props.fps)||props.items.length!==props.fps*3)throw Error('Only a three-second motion diagnostic is allowed');return {width:props.width,height:props.height,fps:props.fps,durationInFrames:props.items.length};}}/>;
registerRoot(Root);
