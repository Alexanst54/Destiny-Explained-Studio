import assert from 'node:assert/strict';
import test from 'node:test';
import {particleSeed, resurrectionState, VOXEL_DURATION, VOXEL_FPS} from '../src/voxel/timeline.ts';

test('15 seconds at 30 fps, including first and last frame', () => {
  assert.equal(VOXEL_FPS, 30);
  assert.equal(VOXEL_DURATION, 450);
  assert.equal(resurrectionState(0).rise, 0);
  assert.equal(resurrectionState(449).rise, 1);
  assert.equal(resurrectionState(449).guardianRotation, 0);
  assert.equal(resurrectionState(449).beam, 0);
});

test('the Guardian rises monotonically and the beam only lights the resurrection', () => {
  let previousRise = 0;
  for (let frame = 0; frame < VOXEL_DURATION; frame++) {
    const state = resurrectionState(frame);
    assert.ok(state.rise >= previousRise && state.rise <= 1);
    assert.ok(state.beam >= 0 && state.beam <= 1);
    for (const value of Object.values(state)) {
      if (typeof value === 'number') assert.ok(Number.isFinite(value));
    }
    if (frame < 60 || frame >= 255) assert.equal(state.beam, 0);
    previousRise = state.rise;
  }
  assert.ok(resurrectionState(165).beam > 0.9);
  assert.ok(resurrectionState(165).rise > 0 && resurrectionState(165).rise < 1);
});

test('random-access evaluation reproduces the same frames and particle seeds', () => {
  const frames = [0, 165, 449, 60, 240, 120];
  const expected = frames.map(resurrectionState);
  for (const frame of [...frames].reverse()) {
    assert.deepEqual(resurrectionState(frame), expected[frames.indexOf(frame)]);
  }
  for (let i = 0; i < 48; i++) {
    for (let channel = 0; channel < 4; channel++) {
      const seed = particleSeed(i, channel);
      assert.ok(seed >= 0 && seed < 1);
      assert.equal(seed, particleSeed(i, channel));
    }
  }
});
