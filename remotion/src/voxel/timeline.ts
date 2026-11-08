export const VOXEL_FPS = 30;
export const VOXEL_DURATION = 15 * VOXEL_FPS;
const clamp = (value: number) => Math.max(0, Math.min(1, value));
const smooth = (value: number) => {
  const x = clamp(value);
  return x * x * (3 - 2 * x);
};

// Pure functions: seeking, preview and parallel rendering use the same state.
export const resurrectionState = (frame: number) => {
  const t = Math.max(0, Math.min(VOXEL_DURATION - 1, frame)) / VOXEL_FPS;
  const rise = smooth((t - 4) / 4);
  const beam = smooth((t - 2) / 0.8) * (1 - smooth((t - 7.2) / 1.3));
  const orbit = smooth(t / 15);
  return {
    t,
    rise,
    beam,
    guardianX: -1.1 * (1 - rise),
    guardianY: 0.18 + Math.sin(rise * Math.PI) * 0.35,
    guardianRotation: (rise - 1) * Math.PI / 2,
    ghostY: 3.65 + Math.sin(t * 2.2) * 0.12,
    ghostX: (1 - smooth(t / 2)) * 1.6,
    cameraAngle: -0.38 + orbit * 0.8,
    cameraDistance: 10.5 - Math.sin(orbit * Math.PI) * 0.9,
    caption: t < 2 ? 'A fallen Guardian.' : t < 8
      ? 'A Ghost channels the Light.' : 'The Guardian rises again.',
  };
};

// Indexed integer hash: no random generator or mutable simulation state.
export const particleSeed = (index: number, channel: number): number => {
  let x = Math.imul(index + 1, 374761393) ^ Math.imul(channel + 1, 668265263);
  x = Math.imul(x ^ (x >>> 13), 1274126177);
  return ((x ^ (x >>> 16)) >>> 0) / 4294967296;
};
