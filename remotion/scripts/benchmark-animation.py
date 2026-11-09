"""Real CPU renders with sampled Node/Chromium/other process-tree RSS and PSS."""
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'out/animation-comparison'

def process_tree(root):
    rows={}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit(): continue
        try:
            stat=(entry/'stat').read_text(); after=stat.rsplit(')',1)[1].split(); ppid=int(after[1])
            command=(entry/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            rows[int(entry.name)]=(ppid,command,entry)
        except (OSError,ValueError): pass
    selected={root}
    while True:
        added={pid for pid,(parent,_,_) in rows.items() if parent in selected}
        if added<=selected: break
        selected|=added
    totals={k:{'rssKiB':0,'pssKiB':0,'processes':0} for k in ['node','chromium','other']}
    pss_complete=True
    for pid in selected:
        if pid not in rows: continue
        _,command,entry=rows[pid]
        category='chromium' if any(x in command.lower() for x in ['chromium','chrome-headless','chrome_crashpad']) and '/node ' not in command else 'node' if '/node ' in command or command.startswith('node ') else 'other'
        try:
            status=dict(line.split(':',1) for line in (entry/'status').read_text().splitlines() if ':' in line)
            rss=int(status.get('VmRSS','0 kB').split()[0]);pss=None
            try:
                for line in (entry/'smaps_rollup').read_text().splitlines():
                    if line.startswith('Pss:'): pss=int(line.split()[1]);break
            except OSError: pass
            if pss is None and rss>0: pss_complete=False
            totals[category]['rssKiB']+=rss;totals[category]['pssKiB']+=pss or 0;totals[category]['processes']+=1
        except (OSError,ValueError): pass
    return {'categories':totals,'rssKiB':sum(x['rssKiB'] for x in totals.values()),'pssKiB':sum(x['pssKiB'] for x in totals.values()),'pssComplete':pss_complete}

def render(label,episode,args,partial=False):
    filename=OUT/(label+'-input.json');filename.write_text(json.dumps(episode,indent=2)+'\n')
    command=[args.node,'--experimental-strip-types','scripts/episode.mjs','render',str(filename),'--concurrency=1','--browser-executable='+args.browser]
    if partial: command.append('--frames=210-221')
    peaks={'rssKiB':0,'pssKiB':0,'categories':{k:{'rssKiB':0,'pssKiB':0,'processes':0} for k in ['node','chromium','other']},'samples':0,'allSamplesPssComplete':True}
    start=time.monotonic()
    with (OUT/(label+'-render.log')).open('w') as log:
        child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while child.poll() is None:
            sample=process_tree(child.pid);peaks['samples']+=1;peaks['allSamplesPssComplete']&=sample['pssComplete']
            for key in ['rssKiB','pssKiB']:
                if sample[key]>peaks[key]:peaks[key]=sample[key];peaks['atPeak'+key]=sample
            for name,values in sample['categories'].items():
                for key,value in values.items():peaks['categories'][name][key]=max(peaks['categories'][name][key],value)
            time.sleep(.25)
        code=child.returncode
    result={'label':label,'exitCode':code,'wallSeconds':round(time.monotonic()-start,2),'memory':peaks,'sampleIntervalSeconds':.25,'scope':'Render process and observable descendants. RSS sums count shared pages more than once; PSS apportions shared pages. Category peaks need not coincide. Sampling can miss short peaks.','framesRequested':12 if partial else 1050}
    if code==0:
        video=ROOT/episode['render']['output'];result['bytes']=video.stat().st_size
        result['probe']=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration,sample_rate,channels','-of','json',str(video)]))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--node',default='node');parser.add_argument('--browser',default='/usr/bin/chromium');parser.add_argument('--mode',choices=['full','comparison','profiles'],default='full');args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True);cases=[]
    if args.mode in ['full','comparison']:
        for version in (['0.7'] if args.mode=='full' else ['0.5','0.6','0.7']):
            stem={'0.5':'hybrid_riis','0.6':'hybrid_riis_06','0.7':'hybrid_riis_07'}[version];e=json.loads((ROOT/('out/'+stem+'-ready.json')).read_text())
            label=('full-' if args.mode=='full' else 'sample-')+version
            if args.mode!='full':e['render']['output']='out/animation-'+label.replace('.','_')+'.mp4'
            cases.append((label,e))
    else:
        original=json.loads((ROOT/'out/hybrid_riis_07-ready.json').read_text())
        for profile in ['draft','balanced','final']:
            for count in [4,8,16]:
                e=copy.deepcopy(original);s=e['scenes'][1];w=s['livingWorld'];template=w['cast'][1];w['cast']=[]
                for i in range(count):
                    a=copy.deepcopy(template);a.update(id='bench-'+str(i),position=[(i%4-1.5)*1.6,0,-2-(i//4)*1.7]);a['rig'].update(seed=42+i*7919,phaseOffset=i*3,animation='walk',clips=[]);w['cast'].append(a)
                w['studio'].update(profile=profile,interactions=[]);w['studio']['camera'].update(mode='group',targets=[a['id'] for a in w['cast']]);label=profile+'-'+str(count);e['render']['output']='out/animation-'+label.replace('.','_')+'.mp4';cases.append((label,e))
    results=[]
    for label,e in cases:
        result=render(label,e,args,args.mode!='full');results.append(result);(OUT/('performance-'+args.mode+'.json')).write_text(json.dumps({'mode':args.mode,'results':results},indent=2)+'\n');print(label,result['exitCode'],result['wallSeconds'],'s',flush=True)
        if result['exitCode']:return result['exitCode']
    return 0
if __name__=='__main__':raise SystemExit(main())
