"""Blender worker: build once, update transforms, atomically commit each frame."""
import argparse
import json
from pathlib import Path
import resource
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from contract import load
from import_scene import build_scene
from persistent_scene import SceneUpdater
from sequence import atomic, digest, png_valid, sha


def main(argv):
    import bpy
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('job')
    a = p.parse_args(argv)
    job = json.loads(Path(a.job).read_text())
    folder = Path(a.job).resolve().parent
    started = time.monotonic()
    first = load(folder / f'{job["indices"][0]:05d}.json')
    scene, objects, info = build_scene(first, device=job['device'], scale=job['scale'], threads=job['threads'])
    updater = SceneUpdater(scene, objects, first)
    if bpy.context.window:
        bpy.context.window.scene = scene
    build_seconds = time.monotonic() - started
    for index in job['indices']:
        frame_started = time.monotonic()
        data = load(folder / f'{index:05d}.json')
        updater.update(data)
        output = folder / f'{index:05d}.png'
        temporary = output.with_name(output.stem + '.partial.png')
        temporary.unlink(missing_ok=True)
        scene.render.filepath = str(temporary)
        try:
            bpy.ops.render.render(write_still=True, scene=scene.name)
        except RuntimeError as error:
            if info['selected'] != 'GPU' or job['device'] != 'auto':
                raise
            info['notes'].append('GPU render failed; CPU retry: ' + str(error))
            scene.cycles.device = 'CPU'
            info.update(selected='CPU', backend=None, devices=[])
            bpy.ops.render.render(write_still=True, scene=scene.name)
        width = scene.render.resolution_x * job['scale'] // 100
        height = scene.render.resolution_y * job['scale'] // 100
        if not png_valid(temporary, width, height):
            raise RuntimeError('Invalid rendered PNG')
        temporary.replace(output)
        report = {'rendered': True, 'renderer': 'persistent', 'source': data['source'],
                  'configuration': info.copy(), 'blenderVersion': bpy.app.version_string,
                  'secondsInsideBlender': round(time.monotonic()-frame_started, 6),
                  'sceneBuildSeconds': build_seconds, 'width': width, 'height': height,
                  'maxProcessRssKiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  'memoryScope': 'Blender process high-water RSS on Linux; excludes GPU memory.'}
        atomic(output.with_suffix('.report.json'), report)
        atomic(output.with_suffix('.done.json'), {'key': digest(data), 'pngSha256': sha(output), 'configuration': info.copy()})
        print('BATCH_FRAME ' + json.dumps({'index': index, 'report': report}), flush=True)


if __name__ == '__main__':
    main(sys.argv[sys.argv.index('--')+1:])
