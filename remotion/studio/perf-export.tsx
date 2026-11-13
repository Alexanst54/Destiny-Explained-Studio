/** Representative benchmark montage, never published as an actual pilot. */
import React from 'react';
import {AbsoluteFill,Composition,Img,registerRoot,staticFile,useCurrentFrame} from 'remotion';
type Props={width:number;height:number;paths:string[]};
const Montage:React.FC<Props>=({paths})=>{const frame=useCurrentFrame();return <AbsoluteFill><Img src={staticFile(paths[frame])} style={{width:'100%',height:'100%'}}/><div style={{position:'absolute',top:20,left:20,color:'white',background:'black',fontSize:18}}>BENCHMARK · NOT THE EPISODE</div></AbsoluteFill>;};
const Root=()=> <Composition id="PerformanceMontage" component={Montage} width={540} height={960} fps={30} durationInFrames={1} defaultProps={{width:540,height:960,paths:['preview.png']}} calculateMetadata={({props})=>({width:props.width,height:props.height,durationInFrames:props.paths.length})}/>;
registerRoot(Root);
