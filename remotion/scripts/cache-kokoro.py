"""Fetch the pinned Kokoro resources during setup, or verify an offline installation."""
import argparse
import json
from pathlib import Path
from huggingface_hub import hf_hub_download
ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    config = json.loads((ROOT/'config/narration.json').read_text())['kokoro']
    for name in ['config.json', 'kokoro-v1_0.pth', f"voices/{config['voice']}.pt"]:
        path = hf_hub_download(repo_id=config['repo'], revision=config['revision'], filename=name,
                               local_files_only=args.offline)
        if not Path(path).is_file():
            raise RuntimeError(f'Missing cached model resource: {name}')
        print(f'{name}: ready ({Path(path).stat().st_size} bytes)')
    print('Pinned Kokoro resources ready. Narration may use HF_HUB_OFFLINE=1.')

if __name__ == '__main__':
    main()
