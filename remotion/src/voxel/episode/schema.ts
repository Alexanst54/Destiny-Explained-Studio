import {z} from 'zod';

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
  durationFrames: z.number().int().min(30), location: z.literal('the-tower'),
  camera: z.enum(cameras), actions: z.array(action).min(1),
  effects: z.array(z.enum(effects)), narration: text}).strict();

export const episodeSchema = z.object({
  schemaVersion: z.literal('0.1.0-draft'), id: text, title: text, language: z.literal('en-US'),
  format: z.object({width: z.literal(1080), height: z.literal(1920), fps: z.literal(30),
    durationFrames: z.number().int().positive().max(18000)}).strict(),
  style: z.literal('classic-voxel'), setting: z.literal('the-tower'), disclaimer: text,
  audio: z.object({voiceover: z.object({enabled: z.boolean(), language: z.literal('en-US'),
    source: publicPath, status: z.enum(['to-generate', 'ready'])}).strict(), music: z.null()}).strict(),
  characters: z.array(z.discriminatedUnion('id', [
    z.object({id: z.literal('guardian'), model: z.literal('voxel-guardian-v1')}).strict(),
    z.object({id: z.literal('ghost'), model: z.literal('voxel-ghost-v1')}).strict(),
  ])).length(2),
  environments: z.array(z.object({id: z.literal('the-tower'), model: z.literal('voxel-tower-v1'),
    props: z.array(z.enum(['traveler-sphere', 'last-city-silhouette', 'tower-balcony'])).length(3),
  }).strict()).length(1),
  scenes: z.array(scene).min(1),
  subtitles: z.object({mode: z.literal('word-aligned'), language: z.literal('en-US'),
    source: publicPath, status: z.enum(['pending-voiceover-alignment', 'ready']),
    maxLines: z.literal(2), safeAreaBottomPx: z.number().int().min(250).max(700)}).strict(),
  render: z.object({composition: z.literal('VoxelEpisode'),
    output: text.regex(/^out\/[a-zA-Z0-9_-]+\.mp4$/), codec: z.literal('h264')}).strict(),
  notes: z.array(text),
}).strict().superRefine((episode, ctx) => {
  const issue = (path: (string | number)[], message: string) =>
    ctx.addIssue({code: z.ZodIssueCode.custom, path, message});
  if (new Set(episode.characters.map(c => c.id)).size !== 2)
    issue(['characters'], 'Declare Guardian and Ghost exactly once');
  if (new Set(episode.environments[0].props).size !== 3)
    issue(['environments', 0, 'props'], 'Declare all three distinct environment props');
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
  return words;
};
export const episodeWarnings = (episode: VoxelEpisodeDef): string[] => {
  const warnings: string[] = [];
  if (episode.audio.voiceover.enabled && episode.audio.voiceover.status !== 'ready')
    warnings.push('Voiceover is pending: preview is silent.');
  if (episode.subtitles.status !== 'ready')
    warnings.push('Word alignment is pending: preview captions use estimated timing.');
  for (const s of episode.scenes) {
    const wpm = s.narration.split(/\s+/).length * 60 * episode.format.fps / s.durationFrames;
    if (wpm > 180) warnings.push(`${s.id}: ${Math.round(wpm)} words/min; review pacing.`);
  }
  return warnings;
};
