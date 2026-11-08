import {clone} from './model.mjs';
import {projectPolishSchema,cameraDirectorSchema,characterDirectorSchema,environmentDirectorSchema} from '../remotion/polish/schema.ts';
export function enablePolish(raw){const e=clone(raw);if(!e.shorts)throw new Error('Ouvrez un storyboard hybride pour activer les réglages 0.6.');e.schemaVersion='0.6.0';e.shorts.polish??=projectPolishSchema.parse({version:1});return e;}
export const newCamera=(preset,durationFrames)=>cameraDirectorSchema.parse({preset,durationFrames});
export const newPerformance=durationFrames=>characterDirectorSchema.parse({durationFrames});
export const newEnvironment=preset=>environmentDirectorSchema.parse({preset});
