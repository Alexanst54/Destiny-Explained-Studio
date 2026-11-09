"""One PNG with live Blender logs, bounded runtime and machine-readable outcome."""
import argparse
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import time
from contract import load


def stream_process(command,log,timeout=600,heartbeat=15):
    if not isinstance(timeout,(int,float)) or isinstance(timeout,bool) or not 1<=timeout<=7200:raise ValueError('Timeout must be 1–7200 seconds')
    started=time.monotonic();last=started;log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('wb') as sink:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
        selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ)
        try:
            while selector.get_map():
                now=time.monotonic()
                if now-started>timeout:raise TimeoutError(f'Render exceeded {timeout}s; process group stopped. See {log}')
                for key,_ in selector.select(timeout=min(.5,max(.01,timeout-(now-started)))):
                    chunk=os.read(key.fileobj.fileno(),8192)
                    if not chunk:selector.unregister(key.fileobj);continue
                    sink.write(chunk);sink.flush();print(chunk.decode('utf-8',errors='replace'),end='',flush=True)
                if time.monotonic()-last>=heartbeat:
                    print(f'[Blender running: {time.monotonic()-started:.0f}s / {timeout}s; log {log.name}]',flush=True);last=time.monotonic()
            remaining=timeout-(time.monotonic()-started)
            if remaining<=0:raise TimeoutError(f'Render exceeded {timeout}s')
            code=process.wait(timeout=remaining)
            if code:raise RuntimeError(f'Blender exited {code}; see {log}')
        except BaseException:
            if process.poll() is None:
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                process.wait()
            raise
        finally:selector.close();process.stdout.close()
    return round(time.monotonic()-started,3)


def render_one(snapshot,output,blender='blender',device='auto',scale=25,threads=2,timeout=600):
    load(snapshot)
    if device not in ['auto','cpu'] or type(scale) is not int or not 10<=scale<=100 or type(threads) is not int or not 1<=threads<=64:raise ValueError('Invalid render options')
    output=Path(output).resolve()
    if output.suffix.lower()!='.png':raise ValueError('Only PNG supported')
    if output.exists():raise ValueError('Output already exists: choose a fresh name to avoid stale evidence')
    binary=shutil.which(blender)
    if not binary:raise RuntimeError('Blender executable not found')
    command=[binary,'--background','--factory-startup','--python-exit-code','1','--python',str(Path(__file__).with_name('import_scene.py').resolve()),'--',str(Path(snapshot).resolve()),str(output),'--device',device,'--scale',str(scale),'--threads',str(threads)]
    outcome={'command':command,'timeoutSeconds':timeout,'status':'failed'}
    try:
        outcome['wallSeconds']=stream_process(command,output.with_suffix('.log'),timeout)
        report=json.loads(output.with_suffix('.report.json').read_text())
        if not output.is_file() or not report['rendered']:raise RuntimeError('Blender returned without a rendered PNG/report')
        outcome.update(status='success',pngBytes=output.stat().st_size,report=report)
        print('BENCHMARK '+json.dumps(outcome),flush=True)
        return outcome
    except Exception as error:
        outcome['error']=str(error);raise
    finally:
        output.with_suffix('.benchmark.json').write_text(json.dumps(outcome,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output');p.add_argument('--blender',default='blender');p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--scale',type=int,default=25);p.add_argument('--threads',type=int,default=2);p.add_argument('--timeout',type=int,default=600);a=p.parse_args();render_one(a.input,a.output,a.blender,a.device,a.scale,a.threads,a.timeout)
if __name__=='__main__':main()
