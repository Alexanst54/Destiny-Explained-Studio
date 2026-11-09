"""Verify the partial dedicated model's actual Blender media and technical provenance."""
import hashlib,json,subprocess,sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import ROOT,resolve
from universal.cache import valid_png
from universal.crota import generate,arena,camera
from venus_vault.geometry import digest

def verify():
    base=ROOT/'docs/universal-library/crota';e=json.loads((base/'evidence.json').read_text());resolve('boss-crota',arena_id=e['environmentId'])
    if e['status']!='partial-dedicated-prototype' or e['userApproved']:raise ValueError('Prototype improperly promoted')
    if {v['view'] for v in e['views']}!={'front','three-quarter','silhouette','environment','attack'}:raise ValueError('Missing view')
    for v in e['views']:
        p=base/v['report'];report=json.loads(p.read_text());r=report['request'];c=report['configuration'];clip=v['view']=='attack'
        if hashlib.sha256(p.read_bytes()).hexdigest()!=v['reportSha256'] or report['status']!='success':raise ValueError('Invalid report')
        if c['bossDesignSha256']!=digest(generate(r['seed'],r['quality'],r['lod'])) or c['designSha256']!=digest(arena(r['seed'],r['quality'],r['lod'])):raise ValueError('Geometry changed')
        if r['lod']!=0 or r['quality']!=('balanced' if clip else 'cinematic') or len(report['frames'])!=(24 if clip else 1):raise ValueError('Wrong settings')
        for frame in report['frames'].values():
            expected=camera(r['view'],frame['sourceFrame'],r['fps']);matrix=frame['cameraMatrix']
            if any(abs(matrix[i][3]-expected['position'][i])>1e-4 for i in range(3)):raise ValueError('Camera translation changed')
            direction=[expected['target'][i]-expected['position'][i] for i in range(3)];length=math.sqrt(sum(x*x for x in direction))
            if any(abs(-matrix[i][2]-direction[i]/length)>1e-4 for i in range(3)):raise ValueError('Camera direction changed')
        for i in v['images']:
            if i['sha256']!=report['frames'][str(i['index'])]['sha256'] or not valid_png(base/i['path'],r['width'],r['height'],i['sha256']):raise ValueError('Invalid image')
        if clip:
            p=base/v['video']['path']
            if hashlib.sha256(p.read_bytes()).hexdigest()!=v['video']['sha256']:raise ValueError('Invalid video hash')
            d=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,nb_frames,width,height,avg_frame_rate,duration','-of','json',str(p)]))['streams'][0]
            if d['codec_name']!='h264' or d['pix_fmt']!='yuv420p' or int(d['nb_frames'])!=24 or d['avg_frame_rate']!='24/1' or abs(float(d['duration'])-1)>.02:raise ValueError('Video metadata differs')
            decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-f','framemd5','-']).decode()
            frame_hashes=[line.rsplit(',',1)[1].strip() for line in decoded.splitlines() if line and not line.startswith('#')]
            if len(frame_hashes)!=24 or len(set(frame_hashes))<20:raise ValueError('Decoded animation is frozen or incomplete')
            if len({f['sha256'] for f in report['frames'].values()})!=24:raise ValueError('Repeated animation frames')
    regression=e.get('providerRefactorRegression')
    if regression:
        if hashlib.sha256((base/regression['image']).read_bytes()).hexdigest()!=regression['sha256'] or hashlib.sha256((base/regression['report']).read_bytes()).hexdigest()!=regression['reportSha256']:raise ValueError('Regression proof hash differs')
        def rgb(path):return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','rawvideo','-pix_fmt','rgb24','-'])
        a,b=rgb(base/'front.png'),rgb(base/regression['image'])
        if a!=b or hashlib.sha256(a).hexdigest()!=regression['rgbSha256']:raise ValueError('RGB regression failed')
    if e['nativeBlender']['evaluations']!=192 or not e['nativeBlender']['staticResources'] or e['nativeBlender']['maxNormalizedBoundsOverflow']!=0:raise ValueError('Native check failed')
    return dict(stills=4,balancedAnimationFrames=24,status=e['status'])

if __name__=='__main__':print('CROTA_MEDIA',json.dumps(verify()))
