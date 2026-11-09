import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from import_scene import choose_device


class Devices(unittest.TestCase):
    def test_cuda_first_and_only_selected_backend_enabled(self):
        devices=[types.SimpleNamespace(name=name,type=kind,use=True) for name,kind in [('Tesla T4','CUDA'),('Tesla T4 OptiX','OPTIX'),('CPU','CPU')]]
        prefs=types.SimpleNamespace(devices=devices,get_devices=lambda:None)
        bpy=types.SimpleNamespace(context=types.SimpleNamespace(preferences=types.SimpleNamespace(addons={'cycles':types.SimpleNamespace(preferences=prefs)})))
        scene=types.SimpleNamespace(cycles=types.SimpleNamespace(device=None))
        with patch.dict(sys.modules,{'bpy':bpy}):result=choose_device(scene,'auto')
        self.assertEqual(result['backend'],'CUDA');self.assertEqual(result['devices'],['Tesla T4']);self.assertEqual([d.use for d in devices],[True,False,False]);self.assertEqual(scene.cycles.device,'GPU')

    def test_missing_gpu_and_explicit_cpu(self):
        prefs=types.SimpleNamespace(devices=[],get_devices=lambda:None)
        bpy=types.SimpleNamespace(context=types.SimpleNamespace(preferences=types.SimpleNamespace(addons={'cycles':types.SimpleNamespace(preferences=prefs)})))
        scene=types.SimpleNamespace(cycles=types.SimpleNamespace(device=None))
        with patch.dict(sys.modules,{'bpy':bpy}):
            result=choose_device(scene,'auto');self.assertEqual(result['selected'],'CPU');self.assertTrue(result['notes'])
            self.assertEqual(choose_device(scene,'cpu')['selected'],'CPU')
