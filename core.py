"""作者：Wangyuan；日期：2026-10-29；职责：显式目录的校验与检索，无网络预览抓取。"""
import tempfile,json
from pathlib import Path
import catalog

def run(payload):
    if not isinstance(payload,dict):raise TypeError('输入须对象')
    with tempfile.TemporaryDirectory() as d:
        if 'catalog' in payload:
            path=Path(d)/'catalog.json';path.write_text(json.dumps(payload['catalog']),encoding='utf-8')
        else:path=Path(__file__).parent/'catalog.json'
        catalog.CATALOG_PATH=path;catalog.PREVIEWS_PATH=Path(d)/'absent.json';catalog.load_catalog.cache_clear();catalog.load_previews.cache_clear()
        data=catalog.load_catalog();query=str(payload.get('query','')).lower()
        return {'items':[item for item in data['items'] if query in json.dumps(item,ensure_ascii=False).lower()],'summary':catalog.catalog_summary()}
