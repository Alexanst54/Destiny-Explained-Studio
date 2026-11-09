"""Versioned opt-in request. Historical renderer contracts remain unchanged."""
from .registry import resolve
VIEWS=('front','three-quarter','silhouette','environment','reveal','close-up')

def request(selection,quality='balanced',seed=42,lod=0,frames=1,fps=24,width=640,height=800,start_frame=0,animation='idle',view='environment',arena=None,variant=None,family_study=False,family=None,environment_variant='sanctum'):
    for key,value,lo,hi in [('seed',seed,0,2147483647),('lod',lod,0,2),('frames',frames,1,120),('width',width,320,1920),('height',height,240,1920),('start_frame',start_frame,0,17999)]:
        if type(value) is not int or not lo<=value<=hi:raise ValueError('Invalid '+key)
    if type(fps) is not int or fps not in [24,30] or width%2 or height%2 or start_frame+frames>18000:raise ValueError('Invalid frame range or dimensions')
    if quality not in ['draft','balanced','cinematic'] or view not in VIEWS or environment_variant not in ['sanctum','causeway','courtyard']:raise ValueError('Unknown quality, view or environment variant')
    binding=resolve(selection,arena,variant,family_study,family)
    if binding['entity']['kind']=='environment' and view!='environment':raise ValueError('Environment selections require --view environment; anatomical views require a dedicated boss')
    animations=binding['entity']['implementation']['animations'] if binding['entity']['implementation'] else ['idle']
    if animation not in animations:raise ValueError('Unsupported animation for selected implementation')
    return dict(version=1,selectionId=selection,variantId=variant,binding=binding,quality=quality,seed=seed,lod=lod,frames=frames,fps=fps,width=width,height=height,startFrame=start_frame,animation=animation,view=view,environmentVariant=environment_variant)

def validate(r):
    fresh=request(r['selectionId'],r['quality'],r['seed'],r['lod'],r['frames'],r['fps'],r['width'],r['height'],r['startFrame'],r['animation'],r['view'],r['binding']['environmentId'] if r['binding']['entity']['kind']!='environment' else None,r['variantId'],r['binding']['provider']=='family-study',r['binding'].get('familyId'),r['environmentVariant'])
    if r!=fresh:raise ValueError('Request differs from current Atlas/registry')
    return fresh
