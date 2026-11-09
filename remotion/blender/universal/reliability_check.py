"""Real-Blender cache/lock/corruption check. Choose a fresh output directory."""
import argparse,fcntl,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.cache import atomic_json,source_hashes

def main():
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--blender',default='blender');a=p.parse_args();base=Path(a.output).resolve()
    if base.exists():raise ValueError('Use a fresh test directory')
    base.mkdir(parents=True);out=base/'render';cli=Path(__file__).resolve().parents[1]/'render_universal.py'
    cmd=[sys.executable,str(cli),'arena-golgoroth-s-cellar',str(out),'--family-study','--family','hive','--quality','draft','--lod','0','--width','320','--height','240','--blender',a.blender]
    def run(extra=(),success=True):
        r=subprocess.run(cmd+list(extra),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
        with (base/'commands.log').open('a') as log:log.write(r.stdout+'\n')
        assert (r.returncode==0)==success,r.stdout
        return json.loads((out/'progress.json').read_text())
    first=run();assert first['renderedThisRun']==1
    resumed=run(['--resume']);assert resumed['cacheHits']==1 and resumed['renderedThisRun']==0 and resumed['configuration']['designCacheHit']
    intact=(out/'progress.json').read_bytes()
    run(['--resume','--seed','43'],False);assert intact==(out/'progress.json').read_bytes()
    with (out/'render.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);run(['--resume'],False)
    assert intact==(out/'progress.json').read_bytes()
    (out/'design-cache.json').write_text('{corrupt');rebuilt=run(['--resume']);assert rebuilt['cacheHits']==1 and not rebuilt['configuration']['designCacheHit']
    (out/'frame-0000.png').write_bytes(b'corrupt');repaired=run(['--resume']);assert repaired['cacheHits']==0 and repaired['renderedThisRun']==1 and repaired['configuration']['designCacheHit']
    atomic_json(base/'result.json',dict(status='passed',realBlender=True,device=first['configuration']['selected'],completeResume=dict(cacheHits=1,rendered=0,designCacheHit=True),changedSeedRejected=True,concurrentWriterRejected=True,corruptDesignRebuilt=True,corruptPngRenderedAgain=True,sourceHashes=source_hashes(),interSessionBlendCache=False))
    print('UNIVERSAL_RELIABILITY passed')

if __name__=='__main__':main()
