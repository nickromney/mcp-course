"""Execute the published calculator and stdio tools without models, keys or network."""
import asyncio
import importlib.util
import json
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

    def test_vercel_demo_frontend_dependency_security_baseline(self):
        demo = ROOT / 'demos/06-deploy-simple-agent-mcp-vercel'
        manifest = json.loads((demo / 'package.json').read_text())
        lock = json.loads((demo / 'package-lock.json').read_text())
        self.assert_frontend_baseline(manifest, lock)

    def test_vercel_demo_frontend_baseline_rejects_original_affected_versions(self):
        demo = ROOT / 'demos/06-deploy-simple-agent-mcp-vercel'
        manifest = json.loads((demo / 'package.json').read_text())
        lock = json.loads((demo / 'package-lock.json').read_text())
        old_manifest = json.loads(json.dumps(manifest))
        old_lock = json.loads(json.dumps(lock))
        old_manifest['dependencies'].update({
            'next': '14.2.18', 'react': '18.3.1', 'react-dom': '18.3.1',
        })
        old_lock['packages']['']['dependencies'].update(old_manifest['dependencies'])
        old_lock['packages']['node_modules/next']['version'] = '14.2.18'
        old_lock['packages']['node_modules/react']['version'] = '18.3.1'
        old_lock['packages']['node_modules/react-dom']['version'] = '18.3.1'
        with self.assertRaisesRegex(AssertionError, 'Next.js'):
            self.assert_frontend_baseline(old_manifest, old_lock)

    def test_vercel_demo_frontend_baseline_rejects_unreviewed_next_major(self):
        demo = ROOT / 'demos/06-deploy-simple-agent-mcp-vercel'
        manifest = json.loads((demo / 'package.json').read_text())
        lock = json.loads((demo / 'package-lock.json').read_text())
        manifest['dependencies']['next'] = '16.0.0'
        lock['packages']['']['dependencies']['next'] = '16.0.0'
        lock['packages']['node_modules/next']['version'] = '16.0.0'
        with self.assertRaisesRegex(AssertionError, 'reviewed Next.js 15.5 branch'):
            self.assert_frontend_baseline(manifest, lock)

    def assert_frontend_baseline(self, manifest, lock):
        root_package = lock['packages']['']
        locked = lock['packages']
        dependencies = manifest['dependencies']
        for package in ('next', 'react', 'react-dom'):
            self.assertEqual(root_package['dependencies'][package], dependencies[package])
            self.assertEqual(locked[f'node_modules/{package}']['version'], dependencies[package])

        next_version = tuple(int(part) for part in dependencies['next'].split('.'))
        self.assertEqual(next_version[:2], (15, 5), 'Next.js must remain on the reviewed Next.js 15.5 branch')
        self.assertGreaterEqual(next_version, (15, 5, 28), 'Next.js is below the patched 15.5 baseline')
        react_version = tuple(int(part) for part in dependencies['react'].split('.'))
        react_dom_version = tuple(int(part) for part in dependencies['react-dom'].split('.'))
        self.assertGreaterEqual(react_version[0], 19, 'Next.js App Router requires React 19')
        self.assertEqual(react_version, react_dom_version, 'React and ReactDOM versions must match exactly')
        for package in ('@types/react', '@types/react-dom'):
            type_range = manifest['devDependencies'][package]
            self.assertRegex(type_range, r'^\^19\.\d+\.\d+$')
            type_entry = locked[f'node_modules/{package}']
            type_version = tuple(int(part) for part in type_entry['version'].split('.'))
            type_floor = tuple(int(part) for part in type_range[1:].split('.'))
            self.assertEqual(type_version[0], 19, f'{package} must use React 19 types')
            self.assertGreaterEqual(type_version, type_floor, f'{package} is below its declared range')
        for package, entry in locked.items():
            if package == 'node_modules/@next/env' or package.startswith('node_modules/@next/swc-'):
                self.assertEqual(entry['version'], dependencies['next'], f'{package} must match Next.js')
        sharp = locked.get('node_modules/sharp')
        self.assertIsNotNone(sharp, 'Next.js must resolve sharp for its patched image optimizer')
        self.assertGreaterEqual(tuple(int(part) for part in sharp['version'].split('.')), (0, 35, 5))
        for package, entry in locked.items():
            if package.startswith('node_modules/@img/sharp-'):
                self.assertGreaterEqual(tuple(int(part) for part in entry['version'].split('.')), (0, 35, 5))
