import gzip
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('manifest_import', Path(__file__).resolve().parents[1]/'atlas/import_manifest.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ManifestImportTests(unittest.TestCase):
    def tables(self):
        return {'DestinyPlaceDefinition': {'-1': {'placeName': 'The Reef', 'hash': 4294967295}},
                'DestinyDestinationDefinition': {'2': {'displayProperties': {'name':'Europa'}, 'placeHash':4294967295}},
                'DestinyActivityDefinition': {'3': {'activityName':'A mission','destinationHash':2},'4': {'redacted':True,'activityName':'Hidden'}}}

    def test_d1_d2_names_unsigned_hashes_redaction_and_links(self):
        t=self.tables();f=self.tables();f['DestinyPlaceDefinition']['-1']['placeName']='Le Récif'
        result=m.normalize(t,f,'D1','fixture')
        self.assertEqual(len(result['candidates']),3)
        self.assertEqual(result['candidates'][0]['hash'],'4294967295')
        self.assertEqual(result['candidates'][0]['names']['fr'],'Le Récif')
        self.assertEqual(result['unresolvedLinks'],[])
        self.assertTrue(all(x['reviewStatus']=='candidate-not-a-verified-place' for x in result['candidates']))
        self.assertEqual(result,m.normalize(t,f,'D1','fixture'))

    def test_missing_french_and_unresolved_links_are_explicit(self):
        t=self.tables();t['DestinyActivityDefinition']['3']['destinationHash']=99
        result=m.normalize(t)
        self.assertEqual(len(result['unresolvedLinks']),1)
        self.assertEqual(result['candidates'][0]['frenchNameStatus'],'untranslated')

    def test_json_gzip_and_component_directories(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);tables=self.tables()
            (p/'all.json').write_text(json.dumps(tables))
            with gzip.open(p/'all.json.gz','wt') as f:json.dump(tables,f)
            self.assertEqual(m.load_tables(p/'all.json','en'),tables)
            self.assertEqual(m.load_tables(p/'all.json.gz','en'),tables)
            for component,data in tables.items():(p/('en-'+component+'.json')).write_text(json.dumps(data))
            self.assertEqual(m.load_tables(p,'en'),tables)
            (p/'bad.json').write_text('{}')
            with self.assertRaises(ValueError):m.load_tables(p/'bad.json','en')

    def test_sqlite_and_bungie_zip_content_files_are_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);db=p/'fixture.sqlite'
            with sqlite3.connect(db) as c:
                for component,rows in self.tables().items():
                    c.execute(f'CREATE TABLE "{component}" (id INTEGER, json TEXT)')
                    c.executemany(f'INSERT INTO "{component}" VALUES (?,?)',[(int(k),json.dumps(v)) for k,v in rows.items()])
            before=db.read_bytes();raw=m.load_tables(db,'en');self.assertIn('4294967295',raw['DestinyPlaceDefinition']);self.assertEqual(before,db.read_bytes())
            with zipfile.ZipFile(p/'world.content','w') as z:z.write(db,'../../unsafe.content')
            self.assertEqual(m.load_tables(p/'world.content','en'),raw)
            self.assertFalse((p/'unsafe.content').exists())
            with zipfile.ZipFile(p/'bad.zip','w') as z:z.writestr('a.content','x');z.writestr('b.content','y')
            with self.assertRaises(ValueError):m.load_tables(p/'bad.zip','en')


if __name__=='__main__':unittest.main()
