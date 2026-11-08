import unittest,tempfile,json
from pathlib import Path
from core import run

class Tests(unittest.TestCase):
 def test_sample(self):self.assertEqual(len(run({})['items']),1)
 def test_no_match(self):self.assertEqual(run({'query':'does-not-exist'})['items'],[])
 def test_missing(self):
  with self.assertRaises(Exception):run({'catalog':{'count':1,'items':[{}]}})
 def test_count(self):
  with self.assertRaises(Exception):run({'catalog':{'count':2,'items':[]}})

if __name__=="__main__":unittest.main()
