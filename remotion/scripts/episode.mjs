import {readFileSync, existsSync, mkdirSync, writeFileSync, unlinkSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {episodeSchema, episodeWarnings, validateWords} from '../src/voxel/episode/schema.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const command = args.shift();
const source = args[0] && !args[0].startsWith('--') ? args.shift() : 'episodes/traveler_episode_002.json';
const preview = args.includes('--preview');
const allowed = /^(--preview|--frames=\d+-\d+|--browser-executable=.+|--concurrency=[1-4])$/;
try {
  if (!['validate','render'].includes(command) || args.some(a => !allowed.test(a)))
    throw new Error('Usage: episode.mjs validate|render [episode.json] [--preview] [--frames=start-end] [--browser-executable=path] [--concurrency=1-4]');
  const episode = episodeSchema.parse(JSON.parse(readFileSync(resolve(root,source),'utf8')));
  console.log(`${episode.id}: ${episode.scenes.length} scenes, ${episode.format.durationFrames} frames, ${episode.format.durationFrames/episode.format.fps}s`);
  let alignedWords;
  const warnings = episodeWarnings(episode);
  if (preview) {
    console.warn('PREVIEW: audio disabled and subtitle timing estimated.');
    warnings.forEach(w => console.warn(w));
  } else {
    const voiceover = episode.audio.voiceover;
    if (voiceover.enabled && voiceover.status !== 'ready') throw new Error('Voiceover is not ready; use --preview for a silent draft');
    if (episode.subtitles.status !== 'ready') throw new Error('Aligned subtitles are not ready; use --preview');
    const wordsPath = resolve(root,'public',episode.subtitles.source);
    if (!existsSync(wordsPath)) throw new Error(`Missing aligned words: ${wordsPath}`);
    alignedWords = validateWords(JSON.parse(readFileSync(wordsPath,'utf8')),episode);
    if (voiceover.enabled) {
      const audioPath = resolve(root,'public',voiceover.source);
      if (!existsSync(audioPath)) throw new Error(`Missing voiceover: ${audioPath}`);
      const probe = spawnSync('ffprobe',['-v','error','-show_entries','format=duration','-of','json',audioPath],{encoding:'utf8'});
      if (probe.error || probe.status !== 0) throw new Error('ffprobe is required to validate voiceover duration');
      const seconds = Number(JSON.parse(probe.stdout).format?.duration);
      if (!Number.isFinite(seconds) || seconds > episode.format.durationFrames/episode.format.fps || seconds < alignedWords.at(-1).end)
        throw new Error('Voiceover duration must cover all aligned words and fit inside the episode');
    }
    warnings.forEach(w => console.warn(w));
  }
  const range = args.find(a => a.startsWith('--frames='));
  if (range) {
    const [start,end] = range.slice(9).split('-').map(Number);
    if (start > end || end >= episode.format.durationFrames) throw new Error('Invalid test frame range');
  }
  if (command === 'render') {
    mkdirSync(resolve(root,'out'),{recursive:true});
    const propsPath = resolve(root,'out',`.episode-props-${process.pid}.json`);
    const output = preview ? episode.render.output.replace(/\.mp4$/, '-preview.mp4') : episode.render.output;
    try {
      writeFileSync(propsPath,JSON.stringify({episode,preview,alignedWords}));
      const result = spawnSync(process.execPath,[resolve(root,'node_modules/@remotion/cli/remotion-cli.js'),
        'render','src/index.ts',episode.render.composition,output,
        '--codec=h264','--pixel-format=yuv420p',...(args.some(a => a.startsWith('--concurrency=')) ? [] : ['--concurrency=1']),'--gl=swangle',`--props=${propsPath}`,
        ...args.filter(a => a !== '--preview')],{cwd:root,stdio:'inherit'});
      if (result.error || result.status !== 0) throw new Error(`Render failed: ${result.error?.message ?? result.status}`);
    } finally {unlinkSync(propsPath);}
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}
