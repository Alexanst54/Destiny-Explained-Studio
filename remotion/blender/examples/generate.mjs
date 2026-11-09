import {readFileSync,writeFileSync} from 'node:fs';
import {exportFrame} from '../export.ts';
const project=JSON.parse(readFileSync(new URL('../../episodes/hybrid_riis_07.json',import.meta.url)));
project.shorts.polish.detailBudget=6;
const data=exportFrame(project,210);data.omissions.push('Example explicitly reduces procedural detailBudget to 6; the original Riis project is unchanged.');
writeFileSync(new URL('./riis-frame-210.json',import.meta.url),JSON.stringify(data)+'\n');
console.log(`${data.actors.length} actors, ${data.meshes.length} primitives; reproducible compact example.`);
