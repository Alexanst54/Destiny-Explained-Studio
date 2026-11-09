"""Atomic provenance-bound cache, CRC and decompressed scanline validation for RGB PNGs."""
import hashlib,json,os,struct,zlib
from pathlib import Path
from .registry import ROOT

def atomic_json(path,data):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');os.replace(tmp,path)

def source_hashes():
    paths=[ROOT/'remotion/atlas/universal/catalog.json']
    for folder in ['universal','venus_vault','cinematic_vex','characters','environments']:
        paths.extend((ROOT/'remotion/blender'/folder).glob('*.py'));paths.extend((ROOT/'remotion/blender'/folder).glob('*.json'))
    paths += [ROOT/'remotion/blender/import_scene.py',ROOT/'remotion/blender/contract.py',ROOT/'remotion/blender/render_universal.py']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}

def fingerprint(request,device,threads):
    return hashlib.sha256(json.dumps(dict(request=request,device=device,threads=threads,sources=source_hashes()),sort_keys=True).encode()).hexdigest()

def valid_png(path,width,height,expected_sha=None):
    try:
        b=Path(path).read_bytes()
        if len(b)<60 or b[:8]!=b'\x89PNG\r\n\x1a\n' or expected_sha and hashlib.sha256(b).hexdigest()!=expected_sha:return False
        offset=8;data=[];header=None;end=False
        while offset<len(b):
            size=struct.unpack('>I',b[offset:offset+4])[0];kind=b[offset+4:offset+8];payload=b[offset+8:offset+8+size];crc=b[offset+8+size:offset+12+size]
            if len(crc)!=4 or zlib.crc32(kind+payload)&0xffffffff!=struct.unpack('>I',crc)[0]:return False
            if kind==b'IHDR':header=struct.unpack('>IIBBBBB',payload)
            if kind==b'IDAT':data.append(payload)
            offset+=size+12
            if kind==b'IEND':end=True;break
        if not end or offset!=len(b) or header!=(width,height,8,2,0,0,0):return False
        raw=zlib.decompress(b''.join(data));stride=width*3+1
        return len(raw)==stride*height and all(raw[y*stride]<=4 for y in range(height))
    except (OSError,ValueError,struct.error,zlib.error):return False
