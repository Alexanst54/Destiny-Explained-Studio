import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from render_one import stream_process,render_one

class Runner(unittest.TestCase):
    def test_streamed_output_and_errors(self):
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()) as output:
            log=Path(folder)/'test.log'
            seconds=stream_process([sys.executable,'-c',"import sys;sys.stdout.write('no-newline');sys.stdout.flush()"],log,5)
            self.assertEqual(log.read_text(),'no-newline');self.assertIn('no-newline',output.getvalue());self.assertGreater(seconds,0)
            with self.assertRaisesRegex(RuntimeError,'exited 7'):stream_process([sys.executable,'-c','raise SystemExit(7)'],log,5)
    def test_timeout_and_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            log=Path(folder)/'timeout.log';start=time.monotonic()
            with self.assertRaises(TimeoutError):stream_process([sys.executable,'-c','import time;time.sleep(30)'],log,1)
            self.assertLess(time.monotonic()-start,4)
            for timeout in [0,True,7201]:
                with self.assertRaises(ValueError):stream_process([],log,timeout)
            for option in [{'scale':0},{'threads':0},{'device':'bogus'}]:
                with self.assertRaises(ValueError):render_one(ROOT/'examples/riis-frame-210.json',Path(folder)/'x.png',**option)
            with self.assertRaises(RuntimeError):render_one(ROOT/'examples/riis-frame-210.json',Path(folder)/'x.png',blender='not-a-real-blender')
    def test_failure_report_and_fresh_output(self):
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            out=Path(folder)/'failed.png'
            # Python deliberately rejects Blender arguments: exercise a failed executable without a costly render.
            with self.assertRaises(RuntimeError):render_one(ROOT/'examples/riis-frame-210.json',out,blender=sys.executable)
            report=json.loads(out.with_suffix('.benchmark.json').read_text());self.assertEqual(report['status'],'failed');self.assertIn('error',report)
            out.write_bytes(b'old')
            with self.assertRaises(ValueError):render_one(ROOT/'examples/riis-frame-210.json',out)

if __name__=='__main__':unittest.main()
