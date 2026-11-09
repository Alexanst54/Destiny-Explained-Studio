/** Emit the shared Python/Blender render request from an actual Atlas selection. */
import {writeFileSync} from 'node:fs';
import {selectBlenderAsset,blenderSelections} from '../atlas/universal/blender.ts';
const [id,out,options='{}']=process.argv.slice(2);
if(!id||!out)throw Error('Usage: node --experimental-strip-types scripts/select-blender-asset.mjs ID OUTPUT [JSON_OPTIONS]\nImplemented: '+blenderSelections.join(', '));
writeFileSync(out,JSON.stringify(selectBlenderAsset(id,JSON.parse(options)),null,2)+'\n');
