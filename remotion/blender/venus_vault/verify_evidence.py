"""Verify shipped Blender evidence against current geometry, input hashes and media bytes."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from venus_vault.geometry import digest
from venus_vault.design import generate_design
from venus_vault.request import validate
from venus_vault.camera import camera_pose

ROOT=Path(__file__).resolve().parents[3]


def verify(root=ROOT):
    root=Path(root);directory=root/'docs/previews/venus-vault';e=json.loads((directory/'evidence.json').read_text())
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    for p,h in e['renderInputHashes'].items():assert sha(root/p)==h, 'Render input changed: '+p
    for item in e['renders']:
        report=json.loads((directory/item['report']).read_text());r=validate(report['request'])
        assert report['status']=='success' and len(report['frames'])==r['frames'],item['id']
        assert [f['frame'] for f in report['frames']]==list(range(r['startFrame'],r['startFrame']+r['frames']))
        for frame in report['frames']:
            assert frame['camera']==json.loads(json.dumps(camera_pose(r['environmentId'],r['camera'],frame['frame'],r['fps']))),'Stale camera: '+item['id']
        env,boss,dust=generate_design(r)
        assert digest({'environment':env,'boss':boss,'dust':dust})==report['configuration']['designSha256'],'Stale design: '+item['id']
        for png in item['pngs']:
            payload=(directory/png['file']).read_bytes();frame=next(f for f in report['frames'] if f['frame']==png['frame'])
            assert payload[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',payload[16:24])==(r['width'],r['height'])
            assert len(payload)==frame['bytes'] and hashlib.sha256(payload).hexdigest()==frame['sha256'],'PNG differs: '+png['file']
        if 'video' in item:
            video=directory/item['video']['file'];assert sha(video)==item['video']['sha256']
            info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True))
            stream=next(s for s in info['streams'] if s['codec_type']=='video')
            assert stream['codec_name']=='h264' and stream['pix_fmt']=='yuv420p'
            assert (stream['width'],stream['height'],int(stream['nb_frames']))==(r['width'],r['height'],r['frames'])
            assert abs(float(info['format']['duration'])-r['frames']/r['fps'])<.01
            assert len({f['sha256'] for f in report['frames']})==r['frames'],'Repeated animation frames'
    return len(e['renders'])

if __name__=='__main__':print('Verified',verify(),'actual Blender renders and their shipped media')
