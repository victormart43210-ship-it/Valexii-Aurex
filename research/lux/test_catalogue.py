"""Offline regression tests for the LUX catalogue."""
import json
import tempfile
import unittest
from pathlib import Path
from research.lux.catalogue import import_jsonl, search, validate

BASE = {"id":"test-1","title":"Example source","url":"https://example.org/book",
        "systems":["LUX","AUREX"],"purpose":"Evidence comparison","kind":"book",
        "status":"DISCOVERED","admission":"NOT_ADMITTED","rights":"NOT_REVIEWED",
        "full_text_downloaded":False}

class CatalogueTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(dict(BASE))["id"],"test-1")
    def test_no_authority_escalation(self):
        for field,value in [("admission","ADMITTED"),("rights","PUBLIC_DOMAIN"),("full_text_downloaded",True)]:
            r=dict(BASE); r[field]=value
            with self.assertRaises(ValueError): validate(r)
    def test_reject_unsafe_url(self):
        for url in ["http://example.org","file:///etc/passwd","https://user:pass@example.org"]:
            r=dict(BASE); r["url"]=url
            with self.assertRaises(ValueError): validate(r)
    def test_import_and_search(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); f=p/"sources.jsonl"; db=p/"catalogue.sqlite"
            f.write_text(json.dumps(BASE)+"\n",encoding="utf-8")
            self.assertEqual(import_jsonl(db,f),1)
            self.assertEqual(import_jsonl(db,f),1)
            self.assertEqual(len(search(db,"Example",system="LUX")),1)
            self.assertEqual(search(db,"Example",system="DISPATER"),[])
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); f=p/"sources.jsonl"
            f.write_text(json.dumps(BASE)+"\n"+json.dumps(BASE)+"\n")
            with self.assertRaises(ValueError): import_jsonl(p/"db.sqlite",f)

if __name__=="__main__":
    unittest.main()
