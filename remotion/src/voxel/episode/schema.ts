import {hybridVisualSchema,shortsSchema} from '../../../hybrid/schema.ts';
import {allSourceIds,visualReferences,hybridWarnings} from '../../../hybrid/state.ts';
import {livingWorldSchema} from '../../../living/schema.ts';
import {weatherSchema,weatherWarnings} from '../../../weather/schema.ts';
import {loreWarnings} from '../../../living/director.ts';
import {z} from 'zod';
import {atlasRefSchema} from '../../../atlas/index.ts';
import {locationSchema,environmentDeclarationSchema,elementsSchema,resolveEnvironment} from '../library/catalog.ts';
import {directionSchema} from '../cinematic/schema.ts';

const text = z.string().trim().min(1);
const frames = z.number().int().nonnegative();
const publicPath = text.refine(p => !p.startsWith('/') && !p.includes('..') &&
  !/[\\:\x00-\x1f]/.test(p), 'Use a relative public/ asset path without traversal');
export const cameras = ['wide-tilt-up', 'slow-orbit-traveler', 'push-in-sky',
  'close-up-ghost', 'medium-guardian', 'wide-pullback'] as const;
export const effects = ['soft-daylight', 'golden-glow', 'sky-darken', 'distant-lightning',
  'light-particles', 'resurrection-beam', 'voxel-particles', 'traveler-halo'] as const;
const action = z.discriminatedUnion('actor', [
  z.object({actor: z.literal('guardian'), animation: z.enum(['idle', 'look-up', 'resurrect'])}).strict(),
  z.object({actor: z.literal('ghost'), animation: z.enum(['hover', 'scan'])}).strict(),
]);
const scene = z.object({id: text, startFrame: frames,
  durationFrames: z.number().int().min(30), location: locationSchema, atlas:atlasRefSchema.optional(), livingWorld:livingWorldSchema.optional(), weather:weatherSchema.optional(), elements:elementsSchema.optional(),
  visual:hybridVisualSchema.optional(), camera: z.enum(cameras), actions: z.array(action).min(1),
  effects: z.array(z.enum(effects)), narration: text}).strict();

export const episodeSchema = z.object({
  schemaVersion: z.enum(['0.1.0-draft','0.1','0.1.0','0.2','0.2.0','0.3.0','0.4.0','0.5.0']), id: text, title: text, language: z.literal('en-US'),
  format: z.object({width: z.literal(1080), height: z.literal(1920), fps: z.literal(30),
    durationFrames: z.number().int().positive().max(18000)}).strict(),
  style: z.literal('classic-voxel'), setting: locationSchema, disclaimer: text,
  audio: z.object({voiceover: z.object({enabled: z.boolean(), language: z.literal('en-US'),
    source: publicPath, status: z.enum(['to-generate', 'ready'])}).strict(), music: z.null()}).strict(),
  characters: z.array(z.discriminatedUnion('id', [
    z.object({id: z.literal('guardian'), model: z.literal('voxel-guardian-v1')}).strict(),
    z.object({id: z.literal('ghost'), model: z.literal('voxel-ghost-v1')}).strict(),
  ])).length(2),
  environments: z.array(environmentDeclarationSchema).min(1).max(4),
  scenes: z.array(scene).min(1),
  subtitles: z.object({mode: z.literal('word-aligned'), language: z.literal('en-US'),
    source: publicPath, status: z.enum(['pending-voiceover-alignment', 'ready']),
    maxLines: z.literal(2), safeAreaBottomPx: z.number().int().min(250).max(700)}).strict(),
  render: z.object({composition: z.enum(['VoxelEpisode','VoxelCinematicEpisode','HybridShort']),
    output: text.regex(/^out\/[a-zA-Z0-9_-]+\.mp4$/), codec: z.literal('h264')}).strict(),
  notes: z.array(text),
  shorts:shortsSchema.optional(), direction: directionSchema.optional(),
}).strict().superRefine((episode, ctx) => {
  const issue = (path: (string | number)[], message: string) =>
    ctx.addIssue({code: z.ZodIssueCode.custom, path, message});
  if (new Set(episode.characters.map(c => c.id)).size !== 2)
    issue(['characters'], 'Declare Guardian and Ghost exactly once');
  const declared = new Set(episode.environments.map(e=>e.id));
  if(declared.size!==episode.environments.length)issue(['environments'],'Duplicate environment declaration');
  episode.environments.forEach((e,i)=>{
    if(new Set(e.props).size!==3)issue(['environments',i,'props'],'Declare all three distinct environment props');
  });
  if(!declared.has(episode.setting))issue(['setting'],'Environment must be declared');
  episode.scenes.forEach((scene,i)=>{
    if(!declared.has(scene.location))issue(['scenes',i,'location'],'Environment must be declared');
    const plan=episode.direction?.scenes.find(p=>p.sceneId===scene.id);
    const checkLiving=(shot:import('../../../living/schema').LivingShot|undefined,weather:typeof scene.weather,path:(string|number)[])=>{
      const cast=shot?.cast??scene.livingWorld?.cast??[],groups=shot?.groups??scene.livingWorld?.groups??[];
      if(cast.length+groups.reduce((n,g)=>n+g.count,0)>32)issue(path,'CPU population budget exceeds 32');
      const keys=[...cast.map(a=>a.id),...groups.map(g=>g.id)];if(new Set(keys).size!==keys.length)issue(path,'Duplicate living world id');
      for(const a of [...cast,...groups.map(g=>g.member)])if(a.startFrame+a.durationFrames>scene.durationFrames)issue(path,'Character exceeds scene');
      if(weather&&weather.startFrame+weather.durationFrames>scene.durationFrames)issue(path,'Weather exceeds scene');
      for(const o of shot?.animations??[])if(!cast.some(a=>a.id===o.id)&&!groups.some(g=>Array.from({length:g.count},(_,i)=>g.id+':'+i).includes(o.id)))issue(path,'Unknown shot character animation target');
    };
    checkLiving(undefined,scene.weather,['scenes',i,'livingWorld']);
    plan?.shots.forEach((shot,j)=>{
      checkLiving(shot.livingWorld,shot.weather??scene.weather,['direction','scenes',i,'shots',j,'livingWorld']);
      const env=resolveEnvironment(shot.environment,scene.location);
      const id=env==='tower'||env==='golden-age-vision'||env==='collapse-vision'?'the-tower':env;
      if(id!=='light-space'&&!declared.has(id))issue(['direction','scenes',i,'shots',j,'environment'],'Environment must be declared');
    });
  });
  if (episode.render.composition==='VoxelCinematicEpisode' && !episode.direction)
    issue(['direction'], 'Cinematic composition requires direction');
  if (episode.direction && !['VoxelCinematicEpisode','HybridShort'].includes(episode.render.composition))
    issue(['render','composition'], 'Direction requires the cinematic composition');
  if(episode.render.composition==='HybridShort'){
    if(new TextEncoder().encode(JSON.stringify(episode)).byteLength>2*1024*1024)issue(['shorts'],'Hybrid project exceeds the 2 MiB editor/Colab transfer limit');
    if(episode.schemaVersion!=='0.5.0'||!episode.shorts||!episode.direction)issue(['shorts'],'HybridShort requires version 0.5.0, shorts settings and direction');
    if(episode.format.durationFrames<450||episode.format.durationFrames>1800)issue(['format','durationFrames'],'Hybrid Shorts must last 15–60 seconds');
    const sourceIds=new Set([...allSourceIds,...(episode.shorts?.sources.map(s=>s.id)??[])]);
    for(const id of episode.shorts?.sources.map(s=>s.id)??[])if(allSourceIds.has(id))issue(['shorts','sources'],'Project source shadows an existing source id');
    episode.scenes.forEach((s,i)=>{
      if(s.narration.split(/\s+/).some(w=>w.length>120))issue(['scenes',i,'narration'],'Caption word exceeds 120 characters; edit spacing');
      if(s.livingWorld?.mode==='alternate-history'&&!['hypothesis','alternate-history'].includes(episode.shorts?.mode??''))issue(['shorts','mode'],'Alternate Living World requires a hypothetical Short mode');
      if(!s.visual)issue(['scenes',i,'visual'],'Every hybrid storyboard shot requires a visual');
      else {if(s.visual.transition.durationFrames*2>s.durationFrames)issue(['scenes',i,'visual','transition'],'Transition exceeds half of shot');for(const id of visualReferences(s.visual))if(!sourceIds.has(id))issue(['scenes',i,'visual','sources'],'Unknown hybrid source');}
    });
    for(const t of episode.shorts?.audio.tracks??[])if(t.startFrame+t.durationFrames>episode.format.durationFrames)issue(['shorts','audio'],'Audio track exceeds project duration');
  }else if(episode.shorts||episode.scenes.some(s=>s.visual))issue(['render','composition'],'Hybrid content requires HybridShort; no silent omission');
  const ids = new Set<string>();
  let cursor = 0;
  episode.scenes.forEach((s, i) => {
    if (ids.has(s.id)) issue(['scenes', i, 'id'], 'Duplicate scene id');
    ids.add(s.id);
    if (s.startFrame !== cursor) issue(['scenes', i, 'startFrame'], `Expected ${cursor}: no gaps or overlaps`);
    cursor += s.durationFrames;
    const actions = s.actions.map(a => `${a.actor}:${a.animation}`);
    if (new Set(actions).size !== actions.length) issue(['scenes', i, 'actions'], 'Duplicate action');
    const guardianActions = s.actions.filter(a => a.actor === 'guardian');
    if (guardianActions.length > 1) issue(['scenes', i, 'actions'], 'Conflicting Guardian actions');
    const revive = s.actions.some(a => a.animation === 'resurrect');
    if (revive !== s.effects.includes('resurrection-beam'))
      issue(['scenes', i, 'effects'], 'Resurrection action and beam must occur together');
    if (revive && s.durationFrames < 120)
      issue(['scenes', i, 'durationFrames'], 'Resurrection requires at least 120 frames');
    if (new Set(s.effects).size !== s.effects.length) issue(['scenes', i, 'effects'], 'Duplicate effect');
  });
  if (cursor !== episode.format.durationFrames)
    issue(['format', 'durationFrames'], `Scene total is ${cursor} frames`);
});
export type VoxelEpisodeDef = z.infer<typeof episodeSchema>;
export type VoxelSceneDef = VoxelEpisodeDef['scenes'][number];

export const alignedWordsSchema = z.array(z.object({text,
  start: z.number().finite().nonnegative(), end: z.number().finite().positive()}).strict()).min(1);
export type AlignedWord = z.infer<typeof alignedWordsSchema>[number];
export const validateWords = (input: unknown, episode: VoxelEpisodeDef) => {
  const words = alignedWordsSchema.parse(input);
  let end = 0;
  for (const word of words) {
    if (word.start < end || word.end <= word.start || word.end > episode.format.durationFrames / episode.format.fps)
      throw new Error('Aligned words must be ordered, non-overlapping and inside the episode');
    end = word.end;
  }
  const normalize = (value: string) => value.toLowerCase().replace(/[^a-z0-9]/g, '');
  if (normalize(words.map(w => w.text).join(' ')) !== normalize(episode.scenes.map(s => s.narration).join(' ')))
    throw new Error('Aligned words must match the episode narration');
  // Associate words with scene narration, rather than allowing an aligned transcript
  // to drift into the next scene while remaining inside the total episode duration.
  let character = 0;
  const boundaries = episode.scenes.map(scene => {
    const from = character;
    character += normalize(scene.narration).length;
    return {scene, from, to: character};
  });
  character = 0;
  for (const word of words) {
    const count = normalize(word.text).length;
    const boundary = boundaries.find(b => character >= b.from && character + count <= b.to);
    if (!count || !boundary || word.start < boundary.scene.startFrame / episode.format.fps - 1e-6 ||
      word.end > (boundary.scene.startFrame + boundary.scene.durationFrames) / episode.format.fps + 1e-6)
      throw new Error('Aligned words must remain inside their narration scene');
    character += count;
  }
  return words;
};
export const episodeWarnings = (episode: VoxelEpisodeDef): string[] => {
  const warnings: string[] = [];
  if (episode.audio.voiceover.enabled && episode.audio.voiceover.status !== 'ready')
    warnings.push('Voiceover is pending: preview is silent.');
  if (episode.subtitles.status !== 'ready')
    warnings.push('Word alignment is pending: preview captions use estimated timing.');
  for (const s of episode.scenes) {
    warnings.push(...loreWarnings(s.livingWorld,s.atlas),...weatherWarnings(s.atlas?.locationId,s.weather));
    const plan=episode.direction?.scenes.find(p=>p.sceneId===s.id);
    if(!plan)warnings.push(...loreWarnings(s.livingWorld,s.atlas,undefined,{guardian:s.actions.some(a=>a.actor==='guardian'),ghost:s.actions.some(a=>a.actor==='ghost')}));
    for(const shot of plan?.shots??[]){
      const ref=shot.atlas??(shot.environment==='scene'?s.atlas:undefined);
      warnings.push(...loreWarnings(s.livingWorld,ref,shot.livingWorld,shot.actors),...weatherWarnings(ref?.locationId??(shot.environment==='scene'?s.location:shot.environment),shot.weather??s.weather));
    }
    const wpm = s.narration.split(/\s+/).length * 60 * episode.format.fps / s.durationFrames;
    if (wpm > 180) warnings.push(`${s.id}: ${Math.round(wpm)} words/min; review pacing.`);
  }
  warnings.push(...hybridWarnings(episode));
  return [...new Set(warnings)];
};
