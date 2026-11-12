import type {Word} from './captions';
export type Cue={start:number;end:number;words:Word[]};
/** Group native words without inventing/replacing their acoustic timestamps. */
export const groupWords=(words:Word[]):Cue[]=>{
 const cues:Cue[]=[];let pending:Word[]=[];
 const flush=()=>{if(pending.length)cues.push({start:pending[0].start,end:pending[pending.length-1].end,words:pending});pending=[];};
 for(const w of words){
  if(!Number.isFinite(w.start)||!Number.isFinite(w.end)||w.end<=w.start||w.start<0)throw Error('Invalid native word');
  const last=pending[pending.length-1];if(last&&w.start<last.end-0.001)throw Error('Overlapping words');
  if(last&&(w.start-last.end>.35||pending.length>=6||[...pending.map(x=>x.text),w.text].join(' ').length>32||w.end-pending[0].start>2.6))flush();
  pending.push(w);if(/[.!?;:]$/.test(w.text))flush();
 }
 flush();return cues;
};
export const cueAt=(cues:Cue[],seconds:number)=>cues.find(c=>seconds>=c.start&&seconds<c.end);
