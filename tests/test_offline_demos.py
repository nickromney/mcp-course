"""Execute the published calculator and stdio tools without models, keys or network."""
import asyncio
import importlib.util
import re
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
class StubMCP:
    def __init__(self, *args): pass
    def tool(self): return lambda function: function
class OfflineDemos(unittest.TestCase):
    def calculator(self):
        text = (ROOT / 'demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md').read_text()
        blocks = re.findall(r'```python\n(.*?)```', text, re.S)
        block = next(block for block in blocks if 'async def calculate(' in block)
        namespace = {'mcp': StubMCP()}
        exec(compile(block, 'published-calculator', 'exec'), namespace)
        return namespace['calculate']
    def test_published_calculator(self):
        calculate = self.calculator()
        for expression, expected in [('2 * (3 + 4)', '14'), ('-6 / 2', '-3.0'), ('0', '0')]:
            self.assertEqual(asyncio.run(calculate(expression)), expected)
        for expression in ["__import__('os').system('echo bad')", '1 ** 100', '[1][0]', 'True', '1e309', '1e13', '1 / 0', '1+' * 80 + '1', '+' * 18 + '1']:
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                asyncio.run(calculate(expression))
    def test_link_tools_no_keys_no_network(self):
        modules = {name: types.ModuleType(name) for name in ['mcp','mcp.server','mcp.server.fastmcp']}
        modules['mcp.server.fastmcp'].FastMCP = StubMCP
        spec = importlib.util.spec_from_file_location('link_fixture', ROOT / 'demos/05-automations-agent/link_checker_mcp_server.py')
        module = importlib.util.module_from_spec(spec)
        with tempfile.TemporaryDirectory() as directory, patch.dict(sys.modules, modules):
            # Import-time reports directory already exists in this isolated checkout.
            spec.loader.exec_module(module)
            fixture = Path(directory) / 'fixture.md'; fixture.write_text('[a](https://fixture.invalid/a) https://fixture.invalid/a\n')
            self.assertEqual(module.list_markdown_files(directory), str(fixture))
            self.assertEqual(module.extract_links(str(fixture)), 'https://fixture.invalid/a')
            module.REPORTS_DIR = directory
            self.assertIn('Wrote:', module.write_report('fixture.md', 'Synthetic report'))
            self.assertEqual(fixture.read_text(), 'Synthetic report')
            self.assertIn('Error:', module.write_report('../escape.md', 'blocked'))
