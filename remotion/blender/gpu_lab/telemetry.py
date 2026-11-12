"""Device-wide subsecond sampling and process CPU; no kernel-occupancy claims."""
import json,os,shutil,subprocess,threading,time
from pathlib import Path

class Monitor:
 def __init__(self,path,pid,interval=.5):
  self.path=Path(path);self.pid=pid;self.interval=interval;self.phase='startup';self.stop=threading.Event();self.samples=[];self.error=None;self.previous=None;self.gpu=None
 def emit(self,item):
  self.samples.append(item)
  with self.path.open('a') as f:f.write(json.dumps(item)+'\n')
 def cpu_loop(self):
  while not self.stop.is_set():
   now=time.time()
   try:
    values=Path(f'/proc/{self.pid}/stat').read_text().rsplit(')',1)[1].split();cpu=(int(values[11])+int(values[12]))/os.sysconf('SC_CLK_TCK');rss=int(values[21])*os.sysconf('SC_PAGE_SIZE');percent=(cpu-self.previous[1])/(now-self.previous[0])*100 if self.previous else None;self.previous=(now,cpu)
    self.emit(dict(kind='cpu',epochSeconds=now,phase=self.phase,processCpuPercentOneCore=percent,processRssBytes=rss,processCpuSeconds=cpu))
   except (OSError,ValueError,IndexError):pass
   self.stop.wait(self.interval)
 def gpu_loop(self):
  binary=shutil.which('nvidia-smi')
  if not binary:self.error='nvidia-smi unavailable';return
  try:
   self.gpu=subprocess.Popen([binary,'--query-gpu=uuid,name,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw','--format=csv,noheader,nounits','--loop-ms',str(round(self.interval*1000))],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
   for line in self.gpu.stdout:
    if self.stop.is_set():break
    parts=[s.strip() for s in line.split(',')]
    if len(parts)!=7:continue
    def number(s):
     try:return float(s)
     except ValueError:return None
    uid,name,util,memutil,used,total,power=parts
    self.emit(dict(kind='gpu',epochSeconds=time.time(),phase=self.phase,uuid=uid,name=name,utilizationPercent=number(util),memoryUtilizationPercent=number(memutil),memoryMiB=number(used),totalMemoryMiB=number(total),powerWatts=number(power)))
   if self.gpu.poll() not in [None,0]:self.error=self.gpu.stderr.read()[-1000:]
  except OSError as e:self.error=str(e)
 def __enter__(self):
  self.path.parent.mkdir(parents=True,exist_ok=True);self.threads=[threading.Thread(target=f,daemon=True) for f in [self.cpu_loop,self.gpu_loop]]
  for t in self.threads:t.start()
  return self
 def __exit__(self,*args):
  self.stop.set()
  if self.gpu and self.gpu.poll() is None:self.gpu.terminate()
  for t in self.threads:t.join(timeout=3)
  if self.gpu:
   try:self.gpu.wait(timeout=2)
   except subprocess.TimeoutExpired:self.gpu.kill();self.gpu.wait()
 def report(self):
  gpu=[s for s in self.samples if s['kind']=='gpu'];cpu=[s for s in self.samples if s['kind']=='cpu']
  def values(rows,key):return [s[key] for s in rows if s.get(key) is not None]
  def mean(v):return sum(v)/len(v) if v else None
  return dict(intervalSeconds=self.interval,gpuSamples=len(gpu),gpuUuids=sorted({s['uuid'] for s in gpu}),meanGpuUtilizationPercent=mean(values(gpu,'utilizationPercent')),peakVramMiB=max(values(gpu,'memoryMiB'),default=None),meanPowerWatts=mean(values(gpu,'powerWatts')),peakPowerWatts=max(values(gpu,'powerWatts'),default=None),meanProcessCpuPercentOneCore=mean(values(cpu,'processCpuPercentOneCore')),peakProcessRssBytes=max(values(cpu,'processRssBytes'),default=None),error=self.error,scope='Device-wide ~500ms samples can miss shorter bursts; not CUDA occupancy. CPU percent uses one core=100%, so multithreaded values may exceed 100%.')
