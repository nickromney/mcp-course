"""Real pinned MCP SDK acceptance; no model, provider, key, or HTTP calls."""
import asyncio
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


class SDKStdioAcceptance(unittest.IsolatedAsyncioTestCase):
    async def test_registered_tools_in_local_child(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            server = root / 'link_checker_mcp_server.py'
            shutil.copyfile(ROOT / 'demos/05-automations-agent/link_checker_mcp_server.py', server)
            fixture = root / 'fixture.md'
            fixture.write_text('[a](https://fixture.invalid/a) https://fixture.invalid/a\n')
            # Execute the shipped source with HTTP explicitly forbidden in the child.
            bootstrap = root / 'run.py'
            bootstrap.write_text(
                'import runpy, urllib.request\n'
                'def forbidden(*args, **kwargs):\n'
                '    raise RuntimeError("HTTP forbidden in offline acceptance")\n'
                'urllib.request.urlopen = forbidden\n'
                'runpy.run_path("link_checker_mcp_server.py", run_name="__main__")\n'
            )
            params = StdioServerParameters(command=sys.executable, args=[str(bootstrap)],
                                          cwd=str(root), env={'HOME': str(root)})
            async with asyncio.timeout(20):
                async with stdio_client(params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools = {tool.name: tool for tool in (await session.list_tools()).tools}
                        self.assertEqual(set(tools), {'list_markdown_files', 'extract_links', 'check_url', 'write_report'})
                        self.assertEqual(tools['extract_links'].inputSchema['required'], ['filepath'])
                        async def call(name, arguments):
                            result = await session.call_tool(name, arguments)
                            self.assertFalse(result.isError, result)
                            return '\n'.join(part.text for part in result.content if part.type == 'text')
                        self.assertEqual(await call('list_markdown_files', {'directory': str(root)}), str(fixture))
                        self.assertEqual(await call('extract_links', {'filepath': str(fixture)}), 'https://fixture.invalid/a')
                        written = await call('write_report', {'filename': 'acceptance.md', 'content': 'Synthetic report'})
                        self.assertEqual(written, f'Wrote: {root / "reports/acceptance.md"}')
                        self.assertEqual((root / 'reports/acceptance.md').read_text(), 'Synthetic report')
                        self.assertIn('Error:', await call('write_report', {'filename': '../escape.md', 'content': 'blocked'}))
                        self.assertFalse((root / 'escape.md').exists())
                        invalid = await session.call_tool('extract_links', {})
                        self.assertTrue(invalid.isError)

    async def test_published_calculator_registered_with_sdk(self):
        text = (ROOT / 'demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md').read_text()
        block = next(block for block in re.findall(r'```python\n(.*?)```', text, re.S)
                     if 'async def calculate(' in block)
        with tempfile.TemporaryDirectory() as directory:
            server = Path(directory) / 'calculator.py'
            server.write_text('from mcp.server.fastmcp import FastMCP\n'
                              'mcp = FastMCP("published-calculator")\n' + block +
                              '\nmcp.run(transport="stdio")\n')
            params = StdioServerParameters(command=sys.executable, args=[str(server)],
                                          env={'HOME': directory})
            async with asyncio.timeout(20):
                async with stdio_client(params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools = (await session.list_tools()).tools
                        self.assertEqual([tool.name for tool in tools], ['calculate'])
                        self.assertEqual(tools[0].inputSchema['required'], ['expression'])
                        for expression, expected in [('2 * (3 + 4)', '14'), ('0', '0')]:
                            result = await session.call_tool('calculate', {'expression': expression})
                            self.assertFalse(result.isError)
                            self.assertEqual(result.content[0].text, expected)
                        for expression in ["__import__('os')", '1 / 0', '1 ** 100']:
                            result = await session.call_tool('calculate', {'expression': expression})
                            self.assertTrue(result.isError)


if __name__ == '__main__':
    unittest.main()
