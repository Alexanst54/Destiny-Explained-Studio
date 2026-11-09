/** Deterministic, offline audit. Counts declarations and fixture references, not runtime reachability. */
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {existsSync,readFileSync,writeFileSync,realpathSync} from 'node:fs';
import {dirname,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {atlas} from '../atlas/index.ts';
import {characterCatalog as characters} from '../characters/index.ts';
import {families,modules} from '../atlas/schema.ts';
import {rigArchetypes,rigAnimations} from '../animation/schema.ts';
import {environmentDefinitions} from '../src/voxel/library/catalog.ts';
import {episodeSchema} from '../src/voxel/episode/schema.ts';
import {universalAtlas} from '../atlas/universal/index.ts';

const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const sha = data => createHash('sha256').update(data).digest('hex');
const read = path => readFileSync(resolve(ROOT,path));
const git = (...args) => execFileSync('git',['-C',ROOT,...args],{encoding:'utf8'}).trim();
const counts = (rows,field) => Object.fromEntries([...new Set(rows.map(field))].sort().map(key=>[key,rows.filter(row=>field(row)===key).length]));
const scopes=['remotion/atlas/','remotion/characters/','remotion/living/','remotion/animation/','remotion/src/voxel/library/','remotion/blender/','remotion/episodes/','remotion/hybrid/','remotion/polish/','editor/','docs/assets/','docs/images/'];
export function validateAssetFiles(catalog,root=ROOT) {
  for (const asset of catalog.assets) {
    const path=resolve(root,asset.path);
    if (!existsSync(path) || !realpathSync(path).startsWith(realpathSync(root)+'/')) throw Error('Missing or out-of-repository asset: '+asset.id);
    const code=readFileSync(path,'utf8');
    const declaration=asset.kind.startsWith('blender-')?new RegExp(`^def ${asset.symbol}\\(`,'m'):new RegExp(`export (?:const|function) ${asset.symbol}\\b`);
    if (!declaration.test(code)) throw Error('Asset entry point absent: '+asset.id);
    if (asset.kind==='remotion-family' && (asset.path!=='remotion/atlas/recipes.ts'||asset.symbol!=='atlasRecipe'||asset.selector!=='family='+asset.families[0]||!families.includes(asset.families[0]))) throw Error('Unknown existing family selector: '+asset.id);
    if (asset.kind==='remotion-environment') {
      const key=asset.selector.replace(/^location=/,'');
      if (environmentDefinitions[key]?.model!==asset.id||asset.path!=='remotion/src/voxel/library/Library.tsx'||asset.symbol!=='VoxelEnvironment') throw Error('Unknown existing environment selector: '+asset.id);
    }
    if (asset.kind.startsWith('blender-') && !({ 'blender-riis-v1':['remotion/blender/environments/riis.py','atlas=riis/before-whirlwind'], 'blender-venus-v1':['remotion/blender/environments/venus.py','atlas=venus'], 'blender-templars-well-v1':['remotion/blender/environments/vault_of_glass.py','arena=arena-templars-well'], 'blender-glass-throne-v1':['remotion/blender/environments/vault_of_glass.py','arena=arena-glass-throne'], 'blender-templar-v1':['remotion/blender/characters/vex_bosses.py','boss=boss-templar'], 'blender-atheon-v1':['remotion/blender/characters/vex_bosses.py','boss=boss-atheon']}[asset.id]?.every((v,i)=>v===[asset.path,asset.selector][i]) && asset.symbol==='generate')) throw Error('New Blender generator needs explicit audit support: '+asset.id);
  }
  for (const profile of catalog.reuseProfiles) for (const reference of profile.reusableFiles) {
    const path=resolve(root,reference.path);
    if (!existsSync(path)||!realpathSync(path).startsWith(realpathSync(root)+'/')) throw Error('Missing reuse component: '+profile.id+'/'+reference.path);
    const code=readFileSync(path,'utf8');
    if (!(reference.path.endsWith('.py') ? new RegExp(`^def ${reference.symbol}\\(`,'m') : new RegExp(`export (?:const|function) ${reference.symbol}\\b`)).test(code)) throw Error('Reuse component symbol absent: '+profile.id+'/'+reference.symbol);
  }
  if (sha(readFileSync(resolve(root,catalog.legacy.catalogPath)))!==catalog.legacy.catalogSha256) throw Error('Legacy catalog checksum changed; explicit incremental review required');
}

export function auditAssets() {
  validateAssetFiles(universalAtlas);
  const tracked=git('ls-files').split('\n');
  const inputFiles=tracked.filter(path=>scopes.some(scope=>path.startsWith(scope))&&!path.startsWith('remotion/atlas/universal/')).sort();
  const files=inputFiles.map(path=>({path,bytes:read(path).byteLength,sha256:sha(read(path))}));
  const episodes=tracked.filter(path=>/^remotion\/episodes\/[^/]+\.json$/.test(path)).sort();
  const refs={locations:new Map(),variants:new Map(),characters:new Map(),environments:new Map()};
  const missing=[];const media=[];
  const add=(kind,id,episode)=>{const set=refs[kind].get(id)??new Set();set.add(episode);refs[kind].set(id,set);};
  const inspect=(value,episode)=>{
    if (!value||typeof value!=='object') return;
    if (Array.isArray(value)) {for(const item of value)inspect(item,episode);return;}
    if (value.atlas?.locationId) {
      const ref=value.atlas,p=atlas.locations.find(p=>p.id===ref.locationId);add('locations',ref.locationId,episode);
      if (!p)missing.push({episode,kind:'location',id:ref.locationId});
      if (ref.variantId) {add('variants',ref.locationId+'/'+ref.variantId,episode);if(!p?.variants.some(v=>v.id===ref.variantId))missing.push({episode,kind:'variant',id:ref.locationId+'/'+ref.variantId});}
    }
    if (typeof value.characterId==='string') {add('characters',value.characterId,episode);if(!characters.characters.some(c=>c.id===value.characterId))missing.push({episode,kind:'character',id:value.characterId});}
    if (typeof value.location==='string'&&environmentDefinitions[value.location])add('environments',value.location,episode);
    if (typeof value.environment==='string') {const name=value.environment==='tower'?'the-tower':value.environment;if(environmentDefinitions[name])add('environments',name,episode);}
    if (typeof value.source==='string'&&value.source.startsWith('assets/')) media.push({episode,path:value.source,status:value.status??'unspecified',tracked:tracked.includes('remotion/public/'+value.source)});
    for(const child of Object.values(value))inspect(child,episode);
  };
  const fixtureInfo=episodes.map(path=>{const raw=JSON.parse(read(path));episodeSchema.parse(raw);inspect(raw,path);return {path,schemaVersion:raw.schemaVersion,composition:raw.render.composition,durationFrames:raw.format.durationFrames,sha256:sha(read(path))};});
  const usage=Object.fromEntries(Object.entries(refs).map(([kind,map])=>[kind,Object.fromEntries([...map].sort(([a],[b])=>a.localeCompare(b)).map(([id,paths])=>[id,[...paths].sort()]))]));
  const context=JSON.parse(read('remotion/atlas/universal/audit-context.json'));
  const comparison=context.initialBranchDifferences;
  const sharedInputs=context.sharedInputHashes.map(({path,sha256})=>({path,unchangedBetweenBranches:sha(read(path))===sha256}));
  const binaries=tracked.filter(path=>/\.(?:blend|glb|gltf|fbx|obj|usd|usdz)$/i.test(path));
  return {
    auditDate:context.auditDate,context:{...context,initialBranchDifferences:comparison,sharedInputs},
    method:'Fichiers Git suivis, schémas exécutés, références structurées des 12 épisodes fournis. Pas de recherche exhaustive de reachability dynamique, pas de téléchargement ni rendu. Fichiers ignorés (Kokoro, caches) hors inventaire versionné.',
    legacy:{locationCount:atlas.locations.length,variantCount:atlas.locations.reduce((n,p)=>n+p.variants.length,0),dedicatedLocations:atlas.locations.filter(p=>p.render.mode==='dedicated').map(p=>({id:p.id,...p.render})),modularLocationCount:atlas.locations.filter(p=>p.render.mode==='modular-reconstruction').length,families:[...families],modules:[...modules],sourceCount:atlas.sources.length},
    characters:{count:characters.characters.length,variantCount:characters.characters.reduce((n,c)=>n+c.variants.length,0),modelKindsUsed:counts(characters.characters,c=>c.visual.model),rigArchetypes:[...rigArchetypes],rigAnimations:[...rigAnimations]},
    versioned3dModels:binaries,fixtures:fixtureInfo,usage,
    notReferencedByFixtures:{locations:atlas.locations.filter(p=>!refs.locations.has(p.id)).map(p=>p.id),characters:characters.characters.filter(c=>!refs.characters.has(c.id)).map(c=>c.id)},
    missingReferences:missing,mediaReferences:media,
    universalAssetRegistrations:universalAtlas.assets.map(a=>({id:a.id,kind:a.kind,path:a.path,selector:a.selector})),
    reusePlanCount:universalAtlas.assetReusePlans.length,reuseProfileCount:universalAtlas.reuseProfiles.length,pinnedSourceCount:universalAtlas.sources.filter(s=>s.verification==='retrieved').length,
    missingBossAssets:universalAtlas.bosses.filter(b=>b.visualStatus==='placeholder').map(b=>b.id),
    files,
  };
}

export function auditMarkdown(a) {
  const lines=[
    '# Audit des assets — première étape de l’issue #18','',
    `Audit du ${a.auditDate}. Branche observée au départ : \`${a.context.initialBranch}\` (\`${a.context.initialBranchRevision.slice(0,7)}\`, PR #17). Implémentation indépendante depuis \`main\` (\`${a.context.baseRevision.slice(0,7)}\`). Aucun asset existant supprimé ou remplacé.`,
    '', '## Méthode et preuve reproductible','',
    'Exécuter depuis `remotion/` : `npm run audit:assets` ; vérifier sans réécriture : `npm run audit:assets -- --check`. [asset-audit.json](../remotion/atlas/universal/asset-audit.json) contient chemins, tailles, SHA-256 et références par épisode. Les schémas historiques sont exécutés. L’audit fonctionne hors ligne.',
    '',`L’inventaire porte sur **${a.files.length} fichiers suivis**, **${a.fixtures.length} épisodes JSON**, les catalogues, moteurs, bridges et assets compilés. Les médias Kokoro et caches ignorés ne sont pas des fichiers d’assets versionnés ; les références à générer sont signalées séparément. Un fichier présent ou une référence textuelle ne démontre pas son rendu ni sa fidélité canonique.`,
    '', '## Inventaire réel','',
    '| Élément | Présent | Interprétation |','| --- | ---: | --- |',
    `| Lieux Atlas 0.3 | ${a.legacy.locationCount} | IDs et catalogue conservés intégralement |`,
    `| Variantes historiques imbriquées | ${a.legacy.variantCount} | IDs locaux conservés ; pas des modèles uniques |`,
    `| Décors dédiés stylisés | ${a.legacy.dedicatedLocations.length} | Bibliothèque voxel existante, pas des cartes officielles exactes |`,
    `| Lieux en reconstruction modulaire | ${a.legacy.modularLocationCount} | Recettes partagées, pas ${a.legacy.modularLocationCount} assets distincts |`,
    `| Familles / modules | ${a.legacy.families.length} / ${a.legacy.modules.length} | Réutilisables dans Remotion |`,
    `| Personnages / variantes | ${a.characters.count} / ${a.characters.variantCount} | Silhouettes partagées ; une apparence inconnue reste inconnue |`,
    `| Archétypes de rig / animations 0.7 | ${a.characters.rigArchetypes.length} / ${a.characters.rigAnimations.length} | Fonctions déterministes existantes |`,
    `| Modèles .blend/.glb/.gltf/.fbx/.obj/.usd/.usdz versionnés | ${a.versioned3dModels.length} | Bibliothèque actuelle procédurale, pas collection Blender native |`,
    '', '### Décors à réutiliser','',
    '| Lieu Atlas | Modèle / bibliothèque existante | Compatibilité Blender actuelle |','| --- | --- | --- |',
    ...a.legacy.dedicatedLocations.map(p=>`| ${p.id} | ${environmentDefinitions[p.environment].model} — VoxelEnvironment | Export de scène limité ; géométrie complète de ce décor non transférée |`),
    '', 'Les recettes sont dans `remotion/atlas/recipes.ts`, les 16 modules dans `geometry.ts`, les décors dans `src/voxel/library/Library.tsx` et `layout.ts`. Les recettes historiques restent intactes ; Vénus/Caveau dispose maintenant de générateurs Blender séparés, stylisés et non cartographiquement fidèles. Mars et Lune/Cropta restent à adapter.',
    '', '### Personnages, animation et composition','',
    `Styles utilisés par le registre : ${Object.entries(a.characters.modelKindsUsed).map(([k,n])=>`${k} (${n})`).join(', ')}. Le style unknown est un marqueur, pas une apparence attestée. Rigs : ${a.characters.rigArchetypes.join(', ')}.`,
    '', 'Réutiliser `characters/models/VoxelCharacter.tsx`, `living/` (cast/groupes), `animation/rig.ts`, `director.ts` et `camera.ts`, `polish/` (variation, environnement, caméra) et `hybrid/` (composition, sources, audio/captions). Une silhouette générique n’est pas un modèle de boss validé. Les '+a.missingBossAssets.length+' entrées de boss recensées restent sans modèle dédié assigné ; leurs plans de réemploi sont documentaires.',
    '', '## Références réellement utilisées et manquantes','',
    `Les ${a.fixtures.length} épisodes suivis passent le schéma historique : ${Object.entries(counts(a.fixtures,f=>f.schemaVersion)).map(([k,n])=>`${k} (${n})`).join(', ')}. Le JSON de chaque épisode est empreinté ; aucune timeline, voix ou caption n’est modifiée.`,
    '',`Références explicites dans ces fixtures : **${Object.keys(a.usage.locations).length} lieux Atlas**, **${Object.keys(a.usage.characters).length} personnages**, **${Object.keys(a.usage.environments).length} décors** ; références catalogue inconnues : **${a.missingReferences.length}**. Détails fichier par fichier dans le JSON.`,
    '',`**${a.notReferencedByFixtures.locations.length} lieux** et **${a.notReferencedByFixtures.characters.length} personnages** n’ont pas de référence explicite dans ces épisodes. Cela ne prouve pas qu’ils sont inutilisés : l’éditeur et les sélections dynamiques peuvent les utiliser. Aucun nettoyage n’est proposé.`,
    '', `Assets de boss absents dans le nouveau registre : ${a.missingBossAssets.join(', ')}. Ce sont des placeholders documentaires. Athéon et le Templier sont les deux modèles Blender dédiés de cette extension ; les autres arènes restent des plans de réemploi, sauf les trois décors Vénus/Caveau explicitement enregistrés.`,
    '', '## Compatibilité Blender : limites constatées dans le code','',
    '- `blender/export.ts` exporte des primitives box/sphere et matrices de rigs 0.7 pour les plans voxel dirigés. Les Guardian/Ghost historiques et acteurs actifs sans rig sont rejetés explicitement ; aucun acteur n’est silencieusement supprimé.',
    '- Le bridge n’exporte pas les `atlasBoxes` complets ni les décors dédiés : scène de base simplifiée, blocs polish, props terminal et rigs. La présence d’un lieu dans le catalogue ne prouve pas sa géométrie Blender.',
    '- Sky gradient, brouillard, particules, decals, weather geometry et éléments voxel historiques ne sont pas transférés intégralement. Les omissions sont déclarées dans les snapshots. Kokoro, captions, labels et montage restent dans Remotion.',
    '- `blender/environments/riis.py::generate` est un générateur réutilisable existant, limité à `riis/before-whirlwind`. Il utilise les primitives, matériaux, profils et haze existants ; ce n’est ni un fichier .blend ni un générateur universel Vex/Ruche/Cabal.',
    '- Extension Vénus/Caveau opt-in : trois décors et deux boss originaux, géométrie voxel, couleurs, détection GPU et logs partagés avec le bridge. Les rendus CPU sont documentés séparément dans `blender/venus_vault/VALIDATION.md` ; ils ne valident pas Colab/T4.',
    '- Les exemples de snapshots, contrats TS/Python, importeur et deux notebooks existants sont conservés. Aucun test de rendu GPU/Colab/Android n’est ajouté ou revendiqué par cet audit statique.',
    '', '## Branche initiale et indépendance de la PR #17','',
    `Les ${a.context.sharedInputs.length} entrées de catalogue/géométrie/export comparées sont identiques entre main et la branche initiale : **${a.context.sharedInputs.every(f=>f.unchangedBetweenBranches)?'oui':'non — voir JSON'}**. Les différences de PR #17 sont consignées, sans les importer.`,
    '', 'PR #17 ajoute notamment le worker Blender persistant, CUDA/telemetry, les tests de reprise et la preuve MP4. Ces changements ne sont pas sur main. Cette fondation ne les recopie pas, ne les fusionne pas et ne dépend pas de leur exécution. La prise en charge GPU persistante reste un travail indépendant.',
    '', '## Adaptations suivantes, après cette première étape','',
    '1. Relire et compléter les relations et la provenance ; dédoublonner par IDs stables, sans supprimer les fiches historiques homonymes.',
    '2. Vénus/Caveau constitue le premier pilote rendu ; poursuivre la revue visuelle, puis adapter Mars et Lune/Cropta avec les mêmes exigences de preuve.',
    '3. Ajouter l’import incrémental puis les filtres éditeur ; conserver le contrat d’épisode et les timelines existants.',
    '', 'Voir [ATLAS-COVERAGE.md](ATLAS-COVERAGE.md) pour les sources, relations et lacunes de cette tranche. Aucun rendu intégral de 35 secondes ni remplacement destructif.', '',
  ];
  return lines.join('\n');
}

if (process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const report=auditAssets();
  if(report.missingReferences.length)throw Error('Broken legacy references; see audit');
  for(const [file,text] of [['remotion/atlas/universal/asset-audit.json',JSON.stringify(report,null,2)+'\n'],['docs/ASSET-AUDIT.md',auditMarkdown(report)]]) {
    const path=resolve(ROOT,file);
    if(process.argv.includes('--check')) {if(!existsSync(path)||readFileSync(path,'utf8')!==text)throw Error('Stale audit: '+file);}
    else writeFileSync(path,text);
  }
  console.log(JSON.stringify({files:report.files.length,fixtures:report.fixtures.length,locations:report.legacy.locationCount,characters:report.characters.count,missingReferences:report.missingReferences.length,versioned3dModels:report.versioned3dModels.length}));
}
