"""Pure complete scene design shared by Blender construction and evidence verification."""
from venus_vault.geometry import Design, QUALITY
from venus_vault.request import validate
from environments import venus, vault_of_glass
from characters import vex_bosses


def generate_design(request):
    r=validate(request)
    env=venus.generate(r['seed'],r['quality']) if r['environmentId']=='venus' else vault_of_glass.generate(r['seed'],r['quality'],r['environmentId'])
    boss=vex_bosses.generate(r['bossId'],r['seed'],r['quality']) if r['bossId'] else None
    dust=Design('particles',r['seed']+1 if r['seed']<2147483647 else 0,r['quality'])
    for i in range(QUALITY[r['quality']]['particles']):
        x=dust.rng.uniform(-14,14);y=dust.rng.uniform(0,26);z=dust.rng.uniform(1,15);size=dust.rng.uniform(.018,.055)
        dust.box(str(i),(x,y,z),(size,size,size),'oracle' if r['environmentId']=='venus' else 'cyan')
    return env,boss,dust.result()
