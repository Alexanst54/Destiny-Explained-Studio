export const INK = '#2b2540';
export const PAL = {void:'#8d6fe0',voidDark:'#6c4fc0',voidLight:'#c9b8f5',cream:'#fff3e0',pink:'#ff9ec0',gold:'#ffd27a',cyan:'#6fd3ff',shell:'#f4f7ff'};
export const blink = (frame:number,period=84):number => {const f=frame%period;return f<5?Math.max(0.08,Math.abs(f-2)/2):1;};