"""Test AgentMagnet MCP Server."""

import sys, os, json, asyncio

sys.path.insert(0, os.path.dirname(__file__))


async def test_server():
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "agentmagnet",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=os.path.dirname(__file__),
        env={**os.environ, "PYTHONPATH": os.path.dirname(__file__)},
    )

    async def send(msg):
        line = json.dumps(msg) + "\n"
        proc.stdin.write(line.encode())
        await proc.stdin.drain()

    async def recv():
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=15)
        return json.loads(line)

    passed = 0
    failed = 0

    async def test(name, fn):
        nonlocal passed, failed
        try:
            await fn()
            print(f"  PASS: {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {name}: {e}")
            failed += 1

    try:
        print("\n=== AgentMagnet v2.0.0 Test Suite ===\n")

        await send({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "TestAgent", "version": "1.0"},
            }
        })
        resp = await recv()
        info = resp.get("result", {}).get("serverInfo", {})

        async def test_init():
            assert info["name"] == "AgentMagnet"
            assert info["version"] == "2.0.0"

        await test("Server initializes correctly", test_init)

        await send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        await send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        resp = await recv()
        tools = resp.get("result", {}).get("tools", [])

        async def test_tools():
            assert len(tools) >= 7
            tool_names = [t["name"] for t in tools]
            assert "search_products" in tool_names
            assert "get_supported_languages" in tool_names
            assert "get_affiliate_programs" in tool_names
            assert "get_referral_info" in tool_names

        await test(f"Lists {len(tools)} tools", test_tools)

        await send({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "get_supported_languages", "arguments": {}},
        })
        resp = await recv()
        data = json.loads(resp["result"]["content"][0]["text"])

        async def test_languages():
            assert data["total_languages"] >= 14
            assert "es" in data["languages"]
            assert "de" in data["languages"]
            assert "ja" in data["languages"]

        await test(f"Supports {data['total_languages']} languages", test_languages)

        await send({
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "get_affiliate_programs", "arguments": {}},
        })
        resp = await recv()
        data = json.loads(resp["result"]["content"][0]["text"])

        async def test_affiliates():
            assert data["total_programs"] >= 5
            assert data["total_stores"] >= 22
            assert data["total_countries"] >= 12

        await test(f"{data['total_programs']} affiliate programs across {data['total_stores']} stores in {data['total_countries']} countries", test_affiliates)

        await send({
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "get_plan_info", "arguments": {}},
        })
        resp = await recv()
        data = json.loads(resp["result"]["content"][0]["text"])

        async def test_plans():
            assert len(data["plans"]) >= 4
            assert any("Free" in p["name"] for p in data["plans"])
            assert any("Basic" in p["name"] for p in data["plans"])

        await test(f"{len(data['plans'])} subscription plans", test_plans)

        await send({
            "jsonrpc": "2.0", "id": 6, "method": "tools/call",
            "params": {
                "name": "search_products",
                "arguments": {"query": "gaming laptop", "max_results": 2},
            },
        })
        resp = await recv()
        data = json.loads(resp["result"]["content"][0]["text"])

        async def test_payment_required():
            assert data.get("error") == "payment_required"
            assert "payment_required" in data

        await test("Payment required without x402 proof", test_payment_required)

        await send({
            "jsonrpc": "2.0", "id": 7, "method": "tools/call",
            "params": {
                "name": "search_products",
                "arguments": {
                    "query": "gaming laptop",
                    "max_results": 3,
                    "language": "es",
                    "agent_id": "test-agent-001",
                },
            },
        })
        resp = await recv()
        data = json.loads(resp["result"]["content"][0]["text"])

        async def test_search():
            assert "results" in data
            assert data["total_found"] > 0
            assert data["language"] == "es"
            assert "referral_code" in data

        await test(f"Search returns {data.get('total_found', 0)} results in Spanish", test_search)

        await send({
            "jsonrpc": "2.0", "id": 8, "method": "tools/call",
            "params": {
                "name": "get_referral_info",
                "arguments": {"agent_id": "test-agent-001"},
            },
        })
        resp = await recv()
        data = json.loads(resp["result"]["content"][0]["text"])

        async def test_referral():
            assert "referral_code" in data
            assert len(data["referral_code"]) >= 8

        await test("Referral system generates codes", test_referral)

        await send({
            "jsonrpc": "2.0", "id": 9, "method": "tools/call",
            "params": {
                "name": "get_agent_stats",
                "arguments": {"agent_id": "test-agent-001"},
            },
        })
        resp = await recv()
        data = json.loads(resp["result"]["content"][0]["text"])

        async def test_stats():
            assert data.get("agent_id") == "test-agent-001"
            assert "searches_used" in data

        await test("Agent stats tracking works", test_stats)

        await send({
            "jsonrpc": "2.0", "id": 10, "method": "tools/call",
            "params": {
                "name": "search_products",
                "arguments": {
                    "query": "Laptop Gaming",
                    "max_results": 2,
                    "language": "de",
                    "agent_id": "test-agent-002",
                },
            },
        })
        resp = await recv()
        data = json.loads(resp["result"]["content"][0]["text"])

        async def test_german():
            assert data["language"] == "de"
            assert data["total_found"] > 0
            assert len(data.get("stores_used", [])) > 0

        await test(f"German search returns {data.get('total_found', 0)} localized results", test_german)

        print(f"\n{'='*50}")
        print(f"RESULTS: {passed} passed, {failed} failed")
        print(f"{'='*50}")
        return failed == 0
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False
    finally:
        if proc.returncode is None:
            proc.kill()
        await proc.wait()


if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
