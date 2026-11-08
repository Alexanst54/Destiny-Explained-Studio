import {z} from 'zod';
export const weatherTypes=['clear','clouds','rain','thunderstorm','snow','blizzard','fog','sandstorm','strong-wind','spores','energy','supernatural'] as const;
const condition={type:z.enum(weatherTypes),intensity:z.number().min(0).max(1),windDirection:z.number().min(-180).max(180).default(0),windSpeed:z.number().min(0).max(30).default(0),visibility:z.number().min(.05).max(1).default(1)};
export const weatherSchema=z.object({...condition,startFrame:z.number().int().min(0).max(18000).default(0),durationFrames:z.number().int().min(1).max(18000),seed:z.number().int().min(0).max(2147483647),transitionFrames:z.number().int().min(0).max(1800).default(60),to:z.object(condition).strict().optional(),dayPhase:z.number().min(0).max(1).default(.5),dayCycleFrames:z.number().int().min(30).max(18000).optional(),particleBudget:z.number().int().min(0).max(128).default(64)}).strict().superRefine((w,ctx)=>{if(w.transitionFrames>w.durationFrames)ctx.addIssue({code:'custom',message:'Weather transition exceeds duration'});});
export type Weather=z.infer<typeof weatherSchema>;
export const weatherPresets:Record<string,{types:typeof weatherTypes[number][];note:string}>={
 europa:{types:['clear','snow','blizzard'],note:'Ambiance glaciaire proposée, sans affirmation historique.'},
 titan:{types:['rain','thunderstorm','strong-wind'],note:'Tempête océanique illustrative.'},
 mars:{types:['clear','sandstorm'],note:'Poussières désertiques illustratives.'},
 'black-garden':{types:['spores','fog','energy'],note:'Particules artistiques, sans nature biologique affirmée.'},
 riis:{types:['clear','clouds','thunderstorm'],note:'Tourbillon : tempête métaphorique, pas une météo canonique attestée.'},
 mercury:{types:['clear','energy'],note:'Éclairage variable selon la reconstitution choisie.'},
 fundament:{types:['fog','rain','thunderstorm','supernatural'],note:'Atmosphère océanique illustrative du récit des Livres du Malheur.'},
};
export function weatherWarnings(locationId:string|undefined,weather:Weather|undefined){
 if(!weather)return [];const p=locationId?weatherPresets[locationId]:undefined;
 return p?[...new Set([weather.type,weather.to?.type].filter(Boolean))].filter(t=>!p.types.includes(t!)).map(t=>`Météo ${t} inhabituelle pour ${locationId} : reconstitution artistique à confirmer.`):['Compatibilité météo non documentée pour ce lieu.'];
}
