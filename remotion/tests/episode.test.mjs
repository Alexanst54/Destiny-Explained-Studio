import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {episodeSchema, episodeWarnings, validateWords} from '../src/voxel/episode/schema.ts';
import {findScene, sceneState, cameraPose, captionWords} from '../src/voxel/episode/state.ts';
const raw = JSON.parse(readFileSync(new URL('../episodes/traveler_episode_002.json',import.meta.url),'utf8'));
const clone = () => structuredClone(raw);

test('the supplied episode is 1800 frames with contiguous scene boundaries', () => {
  const e = episodeSchema.parse(raw);
  assert.equal(e.scenes.reduce((n,s) => n+s.durationFrames,0),1800);
  for (const scene of e.scenes) {
    assert.equal(findScene(e,scene.startFrame).id,scene.id);
    assert.equal(findScene(e,scene.startFrame+scene.durationFrames-1).id,scene.id);
  }
  assert.throws(() => findScene(e,1800));
  assert.ok(episodeWarnings(e).some(w => w.includes('silent')));
  assert.ok(episodeWarnings(e).some(w => w.includes('estimated')));
});

test('reject invalid intervals, references, actions, asset paths and unsupported options', () => {
  const mutations = [
    e => e.scenes[1].startFrame++, e => e.scenes[0].durationFrames=0,
    e => e.format.durationFrames++, e => e.scenes[1].id=e.scenes[0].id,
    e => e.scenes[0].camera='unknown', e => e.scenes[0].location='moon',
    e => e.scenes[0].actions[0].animation='hover', e => e.scenes[0].actions[0].actor='unknown',
    e => e.scenes[4].effects=[], e => e.scenes[0].effects=['unknown'],
    e => e.audio.voiceover.source='../secret.wav', e => e.render.output='../main.mp4',
    e => e.characters[1]=e.characters[0], e => e.environments[0].props.fill('traveler-sphere'),
    e => e.scenes[0].actions.push({actor:'guardian',animation:'look-up'}),
    e => e.style='other', e => e.format.fps=60, e => e.extra=true,
  ];
  for (const mutate of mutations) {
    const e = clone(); mutate(e);
    assert.equal(episodeSchema.safeParse(e).success,false);
  }
});

test('all frames have finite camera and animation state; seeking is reproducible', () => {
  const e = episodeSchema.parse(raw);
  for (let frame=0;frame<1800;frame++) {
    const scene=findScene(e,frame);
    const state=sceneState(scene,frame,30);
    const camera=cameraPose(scene.camera,state.progress);
    assert.ok([...camera.position,...camera.target].every(Number.isFinite));
    assert.ok(state.rise>=0 && state.rise<=1 && state.beam>=0 && state.beam<=1);
    if (scene.id !== 'scene-05') assert.equal(state.rise,1);
    assert.ok(captionWords(scene,frame).length<=6);
  }
  const scene=e.scenes[4];
  const state=sceneState(scene,1310,30);
  sceneState(e.scenes[0],0,30);
  assert.deepEqual(sceneState(scene,1310,30),state);
  assert.equal(sceneState(scene,1200,30).rise,0);
  assert.equal(sceneState(scene,1499,30).rise,1);
});

test('alignment must match narration, stay ordered and remain inside the episode', () => {
  const e=episodeSchema.parse(raw);
  const tokens=e.scenes.flatMap(s => s.narration.split(/\s+/));
  const words=tokens.map((text,i) => ({text,start:i*0.3,end:(i+1)*0.3}));
  assert.equal(validateWords(words,e).length,tokens.length);
  assert.throws(() => validateWords([{text:'wrong',start:0,end:1}],e));
  const overlap=structuredClone(words);overlap[1].start=0;
  assert.throws(() => validateWords(overlap,e));
  const overflow=structuredClone(words);overflow.at(-1).end=61;
  assert.throws(() => validateWords(overflow,e));
});

test('CLI accepts preview and refuses a final render with pending assets', () => {
  const options={cwd:new URL('..',import.meta.url),encoding:'utf8'};
  const invoke=(...args) => spawnSync(process.execPath,['--experimental-strip-types','scripts/episode.mjs','validate',...args],options);
  assert.equal(invoke('--preview').status,0);
  const final=invoke();
  assert.equal(final.status,1);
  assert.match(final.stderr,/Voiceover is not ready/);
  assert.equal(invoke('--preview','--frames=1800-1801').status,1);
});

test('ready mode checks real WAV duration, missing files and aligned word files', async t => {
  if (spawnSync('ffprobe',['-version']).status !== 0) {
    t.skip('ffprobe is required for the final audio validation test');
    return;
  }
  const {mkdtempSync,writeFileSync,rmSync} = await import('node:fs');
  const {join,basename} = await import('node:path');
  const {fileURLToPath} = await import('node:url');
  const root=fileURLToPath(new URL('..',import.meta.url));
  const dir=mkdtempSync(join(root,'public','episode-validation-'));
  try {
    const e=clone();
    e.audio.voiceover.status='ready'; e.subtitles.status='ready';
    e.audio.voiceover.source=`${basename(dir)}/voice.wav`;
    e.subtitles.source=`${basename(dir)}/words.json`;
    const tokens=e.scenes.flatMap(s => s.narration.split(/\s+/));
    const words=tokens.map((text,i) => ({text,start:i*0.3,end:(i+1)*0.3}));
    writeFileSync(join(dir,'words.json'),JSON.stringify(words));
    writeFileSync(join(dir,'episode.json'),JSON.stringify(e));
    const writeWav = seconds => {
      const samples=8000*seconds, data=Buffer.alloc(44+samples*2);
      data.write('RIFF');data.writeUInt32LE(data.length-8,4);data.write('WAVEfmt ',8);
      data.writeUInt32LE(16,16);data.writeUInt16LE(1,20);data.writeUInt16LE(1,22);
      data.writeUInt32LE(8000,24);data.writeUInt32LE(16000,28);
      data.writeUInt16LE(2,32);data.writeUInt16LE(16,34);data.write('data',36);
      data.writeUInt32LE(samples*2,40);writeFileSync(join(dir,'voice.wav'),data);
    };
    const invoke=() => spawnSync(process.execPath,['--experimental-strip-types','scripts/episode.mjs',
      'validate',join(dir,'episode.json')],{cwd:root,encoding:'utf8'});
    writeWav(60);assert.equal(invoke().status,0);
    writeWav(61);assert.equal(invoke().status,1);
    writeWav(1);assert.equal(invoke().status,1);
    rmSync(join(dir,'voice.wav'));assert.equal(invoke().status,1);
  } finally {rmSync(dir,{recursive:true,force:true});}
});
