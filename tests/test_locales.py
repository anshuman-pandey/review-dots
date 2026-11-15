import json,re,unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class CatalogTests(unittest.TestCase):
 def test_catalog_completeness_and_parameters(self):
  raw=(ROOT/'static/messages.js').read_text();catalog=json.loads(raw.removeprefix('globalThis.APP_MESSAGES = ').rstrip(';\n'))
  for source,values in catalog.items():
   self.assertEqual(set(values),{'de','es','ja','zh-CN','zh-TW'})
   for translated in values.values():self.assertTrue(translated);self.assertEqual(sorted(re.findall(r'\{\d+\}',source)),sorted(re.findall(r'\{\d+\}',translated)))
  class Parser(HTMLParser):
   def handle_starttag(inner,tag,attrs):
    for key,value in attrs:
     if key.startswith('data-i18n'):self.assertIn(value,catalog)
  Parser().feed((ROOT/'static/index.html').read_text())
  for file in ['reviews.py','server.py']:
   for message in re.findall(r'''Invalid\(['"]([^'"]+)['"]\)''',(ROOT/file).read_text()):self.assertIn(message,catalog)
