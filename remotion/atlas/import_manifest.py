"""Offline, standard-library importer. Never treats a manifest row as a verified place.

Accepts component directories, combined JSON (.gz), or Bungie world SQLite (.zip).
Outputs review candidates with unsigned stable hashes and unresolved-link reports.
No downloads, API keys, third-party Python modules, SQL writes or catalog overwrites.
"""
import argparse
from contextlib import closing
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile

COMPONENTS = ('DestinyPlaceDefinition', 'DestinyDestinationDefinition', 'DestinyActivityDefinition')
LIMIT = 256 * 1024 * 1024


def unsigned(value):
    return str(int(value) & 0xffffffff)


def read_json(path):
    if path.stat().st_size > LIMIT:
        raise ValueError('Manifest file exceeds 256 MiB')
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rb') as stream:
        content = stream.read(LIMIT + 1)
    if len(content) > LIMIT:
        raise ValueError('Expanded JSON exceeds 256 MiB')
    return json.loads(content)


def sqlite_tables(path):
    result = {}
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for component in COMPONENTS:
            result[component] = {}
            if component not in tables:
                continue
            # Identifiers come only from the fixed whitelist above.
            for row_id, payload in db.execute(f'SELECT id,json FROM "{component}"'):
                result[component][unsigned(row_id)] = json.loads(payload)
    return result


def load_tables(path, locale):
    path = Path(path)
    if path.is_dir():
        tables = {}
        for component in COMPONENTS:
            candidates = [path / f'{locale}-{component}.json', path / locale / f'{component}.json', path / f'{component}.json']
            found = next((p for p in candidates if p.exists()), None)
            if found is None:
                raise ValueError(f'Missing component: {component} ({locale})')
            tables[component] = read_json(found)
        return tables
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            members = [m for m in archive.infolist() if not m.is_dir() and (m.filename.endswith(('.content', '.sqlite', '.db')))]
            if len(members) != 1 or members[0].file_size > LIMIT:
                raise ValueError('ZIP must contain exactly one world SQLite file, <=256 MiB')
            # Do not extract attacker-controlled ZIP filenames.
            with tempfile.TemporaryDirectory() as tmp:
                local = Path(tmp) / 'world.content'
                with archive.open(members[0]) as stream:
                    data = stream.read(LIMIT + 1)
                if len(data) > LIMIT:
                    raise ValueError('Expanded SQLite exceeds 256 MiB')
                local.write_bytes(data)
                return sqlite_tables(local)
    if path.suffix in ('.content', '.sqlite', '.db'):
        return sqlite_tables(path)
    data = read_json(path)
    if not isinstance(data, dict) or not all(c in data for c in COMPONENTS):
        raise ValueError('Combined JSON must contain all three component tables')
    return {c: data[c] for c in COMPONENTS}


def display(row, component):
    prefix = {'DestinyPlaceDefinition':'place', 'DestinyDestinationDefinition':'destination', 'DestinyActivityDefinition':'activity'}[component]
    props = row.get('displayProperties', {})
    return {'name': props.get('name', row.get(prefix+'Name', '')) or '',
            'description': props.get('description', row.get(prefix+'Description', '')) or ''}


def normalize(english, french=None, game='D2', version='unspecified'):
    french = french or {}
    candidates, unresolved = [], []
    if any(not isinstance(english.get(c, {}), dict) for c in COMPONENTS):
        raise ValueError('Component tables must be objects indexed by hash')
    known_hashes = {c: {unsigned(k) for k in english.get(c, {})} for c in COMPONENTS}
    for component in COMPONENTS:
        table = english.get(component, {})
        if not isinstance(table, dict):
            raise ValueError(f'{component} must be an object indexed by hash')
        translated = {unsigned(k): v for k, v in french.get(component, {}).items()}
        for key, row in sorted(table.items(), key=lambda pair: int(pair[0]) & 0xffffffff):
            if not isinstance(row, dict):
                raise ValueError('Definition must be an object')
            if row.get('redacted'):
                continue
            h = unsigned(row.get('hash', key))
            en = display(row, component)['name'].strip()
            if not en:
                continue
            fr = display(translated.get(h, {}), component)['name'].strip()
            links = []
            for field, target in [('placeHash', COMPONENTS[0]), ('destinationHash', COMPONENTS[1])]:
                value = row.get(field)
                if value:
                    target_hash = unsigned(value)
                    target_rows = known_hashes[target]
                    links.append({'component': target, 'hash': target_hash})
                    if target_hash not in target_rows:
                        unresolved.append({'component': component, 'hash': h, 'targetComponent': target, 'targetHash': target_hash})
            candidates.append({'id': f'bungie-{game.lower()}-{component}-{h}',
                               'names': {'en': en, 'fr': fr or en}, 'frenchNameStatus': 'official-manifest' if fr else 'untranslated',
                               'component': component, 'hash': h, 'game': game, 'manifestVersion': version,
                               'description': display(row, component)['description'],
                               'links': links, 'reviewStatus': 'candidate-not-a-verified-place',
                               'availability': 'manifest-presence-does-not-prove-playability'})
    return {'format': 'atlas-manifest-candidates-v1', 'game': game, 'version': version,
            'candidates': candidates, 'unresolvedLinks': unresolved}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--en', required=True, type=Path)
    parser.add_argument('--fr', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--game', choices=['D1', 'D2'], default='D2')
    parser.add_argument('--version', default='unspecified')
    args = parser.parse_args()
    result = normalize(load_tables(args.en, 'en'), load_tables(args.fr, 'fr') if args.fr else None, args.game, args.version)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output.exists():
        raise ValueError('Output exists; choose a new review file (no automatic overwrite)')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded)
    print(json.dumps({'candidates': len(result['candidates']), 'unresolvedLinks': len(result['unresolvedLinks']),
                      'outputSha256': hashlib.sha256(encoded.encode()).hexdigest()}, indent=2))


if __name__ == '__main__':
    main()
