"""Verify real before/after media, paired cameras, current LOD geometry and legacy preservation."""
import hashlib,json,math,struct,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cinematic_vex.render_validation import shot_spec
from venus_vault.request import select,validate
from venus_vault.camera import camera_pose
from venus_vault.design import generate_design
from venus_vault.geometry import digest
ROOT=Path(__file__).resolve().parents[3]


def verify(directory=None):
    directory=Path(directory or ROOT/'docs/previews/cinematic-vex-0.9.1');e=json.loads((directory/'evidence.json').read_text())
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    def png(path,width,height,expected):
        data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(width,height)
        assert sha(path)==expected,'PNG differs: '+str(path)
    assert e['status']=='complete' and len(e['stills'])==6 and len(e['clips'])==2
    for table in ['renderInputHashes','protectedInputHashes','historicalGalleryHashes']:
        for path,h in e[table].items():assert sha(ROOT/path)==h,'Input or historical artifact changed: '+path
    for pair in e['stills']:
        records={}
        for phase in ['before','after']:
            item=pair[phase];path=directory/item['report'];assert sha(path)==item['reportSha256']
            r=json.loads(path.read_text());records[phase]=r;definition=pair['definition']
            assert r['status']=='success' and r['phase']==phase
            assert r['shot']==shot_spec(definition,phase),'Camera/shot differs from the published specification'
            assert r['request']['quality']=='cinematic' and r['configuration']['samples']==128
            png(directory/item['png'],definition['width'],definition['height'],r['pngSha256'])
            if phase=='after':
                assert r['request'].get('lod')==0
                env,boss,dust=generate_design(validate(r['request']))
                assert digest(dict(environment=env,boss=boss,dust=dust))==r['configuration']['designSha256'],'Current geometry differs'
        a=records['before']['cameraMatrixWorld'];b=records['after']['cameraMatrixWorld'];dz=pair['definition'].get('beforeVerticalAlignment',0)
        for i in range(4):
            for j in range(4):assert abs(a[i][j]-b[i][j]-(dz if (i,j)==(2,3) else 0))<1e-5,'Paired camera matrices differ'
        assert records['before']['shot']['sharedCamera']['lens']==records['after']['shot']['sharedCamera']['lens']
    for item in e['clips']:
        report_path=directory/item['report'];assert sha(report_path)==item['reportSha256'];r=json.loads(report_path.read_text());q=validate(r['request']);spec=item['definition']
        assert r['status']=='success' and q['quality']=='balanced' and q['lod']==0 and r['configuration']['samples']==48
        for field in ['frames','fps','width','height','startFrame','animation','camera','lod','quality']:assert q[field]==spec[field]
        assert len(r['frames'])==q['frames'] and len({f['sha256'] for f in r['frames']})==q['frames']
        assert [f['frame'] for f in r['frames']]==list(range(q['startFrame'],q['startFrame']+q['frames']))
        for f in r['frames']:assert f['camera']==json.loads(json.dumps(camera_pose(q['environmentId'],q['camera'],f['frame'],q['fps'])))
        env,boss,dust=generate_design(q);assert digest(dict(environment=env,boss=boss,dust=dust))==r['configuration']['designSha256']
        for p in item['pngs']:png(directory/p['png'],q['width'],q['height'],r['frames'][p['index']]['sha256'])
        video=directory/item['video'];assert sha(video)==item['videoSha256']
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True));s=next(s for s in probe['streams'] if s['codec_type']=='video')
        assert s['codec_name']=='h264' and s['pix_fmt']=='yuv420p'
        assert (s['width'],s['height'],int(s['nb_frames']))==(q['width'],q['height'],q['frames'])
        assert abs(float(probe['format']['duration'])-q['frames']/q['fps'])<.01
    checks=e['nativeBlenderCheck'];assert checks['staticResources'] and checks['linkedGeometryReuse']
    assert checks['maxAnkleErrorMetres']<1e-4 and checks['maxStanceSlidingMetres']<1e-4 and checks['maxTerrainLayerContactErrorMetres']<=.04
    return {'cinematicPairs':len(e['stills']),'balancedClips':len(e['clips']),'protectedFiles':len(e['protectedInputHashes'])}

if __name__=='__main__':print('CINEMATIC_EVIDENCE',json.dumps(verify()))
