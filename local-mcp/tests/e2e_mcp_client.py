#!/usr/bin/env python3
"""End-to-end MCP test for local-mcp: spawn the real server via `uv run`,
list tools, and exercise local_outline (deterministic), local_read,
local_write AND local_edit (model-backed, qwen2.5-coder:3b)."""
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = "/home/aldo/dev/local-mcp/server.py"
TEST_FILE = "/home/aldo/dev/local-mcp/tests/test_guards.py"
SCRATCH = "/home/aldo/dev/local-mcp/tests/e2e_scratch.py"


async def main() -> int:
    params = StdioServerParameters(
        command="uv",
        args=["run", SERVER],
        env={
            "PATH": "/home/aldo/.local/bin:/usr/local/bin:/usr/bin:/bin",
            "HOME": "/home/aldo",
        },
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            print("TOOLS:", names)
            assert names == ["local_edit", "local_outline", "local_read", "local_snippet", "local_write"], "tool list mismatch"

            # 1. Deterministic structural read (no model call)
            res = await session.call_tool("local_outline", {"files": [TEST_FILE]})
            text = res.content[0].text if res.content else ""
            print("\n=== local_outline ===")
            print(text[:300])
            assert not res.isError, "local_outline failed"

            # 2. Model-backed read
            res2 = await session.call_tool(
                "local_read",
                {"files": [TEST_FILE], "instruction": "What does this test file check? One sentence."},
            )
            text2 = res2.content[0].text if res2.content else ""
            print("\n=== local_read ===")
            print(text2[:300])
            assert not res2.isError, "local_read failed"

            # 3. Model-backed write into the repo tests dir
            if os.path.exists(SCRATCH):
                os.remove(SCRATCH)
            res3 = await session.call_tool(
                "local_write",
                {"path": SCRATCH, "instruction": "Write a tiny Python function add(a,b) returning a+b with a docstring."},
            )
            text3 = res3.content[0].text if res3.content else ""
            print("\n=== local_write ===")
            print(text3[:200])
            assert not res3.isError, "local_write failed"
            assert os.path.exists(SCRATCH), "file not created"

            # 4. Model-backed EDIT: extend the scratch file
            res4 = await session.call_tool(
                "local_edit",
                {"files": [SCRATCH], "instruction": "Add a multiply(a,b) function to this file."},
            )
            text4 = res4.content[0].text if res4.content else ""
            print("\n=== local_edit ===")
            print(text4[:200])
            assert not res4.isError, "local_edit failed"
            content = open(SCRATCH).read()
            print("--- final file has multiply:", "multiply" in content)

    print("\nE2E OK")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
