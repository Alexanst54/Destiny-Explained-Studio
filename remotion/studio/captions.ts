export type Word={text:string;start:number;end:number};
/** Speech-aligned half-open intervals, never estimated uniform word durations. */
export const captionsAt=(words:Word[],seconds:number)=>words.filter(w=>seconds>=w.start&&seconds<w.end).map(w=>w.text).join(' ');
