"""Optional sampled NVIDIA telemetry. Values are device-wide, not process-exclusive."""
import shutil
import subprocess
import time


class GpuMonitor:
    def __init__(self):
        self.binary = shutil.which('nvidia-smi')
        self.last = 0
        self.samples = []
        self.note = None if self.binary else 'nvidia-smi unavailable'

    def poll(self):
        if not self.binary or time.monotonic() - self.last < 5:
            return
        self.last = time.monotonic()
        try:
            text = subprocess.check_output([self.binary, '--query-gpu=uuid,name,memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True, timeout=1)
            for line in text.splitlines():
                uuid, name, memory, utilization = [v.strip() for v in line.split(',')]
                self.samples.append({'uuid': uuid, 'name': name, 'memoryMiB': float(memory), 'utilizationPercent': float(utilization), 'monotonicSeconds': self.last})
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            self.note = str(error)
            self.binary = None

    def report(self):
        return {'scope': 'Device-wide samples every >=5s; may include other processes and miss peaks.',
                'sampleCount': len(self.samples), 'samples': self.samples,
                'peakMemoryMiB': max((s['memoryMiB'] for s in self.samples), default=None),
                'meanUtilizationPercent': sum(s['utilizationPercent'] for s in self.samples)/len(self.samples) if self.samples else None,
                'note': self.note}
