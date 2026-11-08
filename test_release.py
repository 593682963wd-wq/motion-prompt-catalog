"""作者：Wangyuan；日期：2026-11-08。职责：通过合成输入复验已确认缺陷。"""
import unittest,json,copy
from pathlib import Path
from core import run
import catalog
class ReleaseTests(unittest.TestCase):
 def test_null_prompt_rejected(self) -> None:
  data=json.loads(Path('catalog.json').read_text());data['items'][0]['original_prompt_zh']=None
  with self.assertRaises(catalog.CatalogError):run({'catalog':data})
 def test_inline_preview_retained_without_external_manifest(self) -> None:
  data=json.loads(Path('catalog.json').read_text());data['items'][0]['preview_local_url']='preview.gif'
  self.assertEqual(run({'catalog':data})['items'][0]['preview_local_url'],'preview.gif')
