"""Fast Cycles device discovery, without constructing any boss or rendering a frame."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'blender'))
import bpy
from import_scene import choose_device
out=Path(sys.argv[sys.argv.index('--')+1]);info=choose_device(bpy.context.scene,'auto')
info.update(blenderVersion=bpy.app.version_string,probeOnly=True,renderingValidated=False)
out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(info,indent=2));tmp.replace(out)
print('DEVICE_PROBE '+json.dumps(info))
