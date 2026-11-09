"""Render-affecting source fingerprints, independent of documentation and output paths."""
import hashlib
from pathlib import Path


def render_signature(source):
    source=Path(source)
    paths=['import_scene.py','contract.py','characters/vex_bosses.py','environments/venus.py','environments/vault_of_glass.py',
           'venus_vault/geometry.py','venus_vault/request.py','venus_vault/camera.py','venus_vault/design.py','venus_vault/renderer.py','venus_vault/atlas-bindings.json']
    paths += ['cinematic_vex/'+n+'.py' for n in ['atheon','templar','animation','materials','shapes','throne']]
    hashes={p:hashlib.sha256((source/'remotion/blender'/p).read_bytes()).hexdigest() for p in paths if (source/'remotion/blender'/p).is_file()}
    hashes['comparison_worker']=hashlib.sha256(Path(__file__).with_name('comparison_worker.py').read_bytes()).hexdigest()
    return hashes
