// Additive selection API for the sidecar library. Does not write or migrate episodes.
import fs from 'node:fs';
const path = new URL('../../../docs/universal-library/catalog.json', import.meta.url);
export function libraryIndex() { return JSON.parse(fs.readFileSync(path, 'utf8')); }
export function libraryEntity(id) {
  const entry = libraryIndex().entities.find(e => e.id === id);
  if (!entry) throw new Error(`Unknown Atlas ID: ${id}`);
  return entry;
}
export function selectLibrary(id, {variant = null, arena = null, lod = 0} = {}) {
  let e = libraryEntity(id);
  if (variant) {
    if (!e.variants.includes(variant)) throw new Error('Variant belongs to another boss');
    e = libraryEntity(variant);
  }
  if (!Number.isInteger(lod) || lod < 0 || lod > 2) throw new Error('Invalid LOD');
  if (!e.implementation) throw new Error('No dedicated implementation; generic substitution prohibited');
  if (arena && arena !== (e.implementation.environmentId ?? e.id)) throw new Error('Arena not implemented');
  return {selectionId: e.id, environmentId: e.implementation.environmentId ?? e.id, provider: e.implementation.provider, lod, animations: e.implementation.animations};
}
