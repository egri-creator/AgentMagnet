"""Test AgentMagnet HTTP Server."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from agentmagnet.http_server import app
from starlette.testclient import TestClient

client = TestClient(app)

resp = client.get("/health")
h = resp.json()
print(f"Health: {resp.status_code} - {h['status']}")

resp = client.get("/")
r = resp.json()
print(f"Root: {r['name']} v{r['version']}")

resp = client.post("/mcp", json={
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
               "clientInfo": {"name": "Test", "version": "1.0"}},
})
init = resp.json()
print(f"Init: {init['result']['serverInfo']['name']}")

resp = client.post("/mcp", json={
    "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {},
})
tools = resp.json()["result"]["tools"]
print(f"Tools: {len(tools)}")

resp = client.post("/mcp", json={
    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
    "params": {"name": "get_supported_languages", "arguments": {}},
})
data = json.loads(resp.json()["result"]["content"][0]["text"])
print(f"Languages: {data['total_languages']}")
print(f"Amazon stores: {len(data['amazon_stores'])}")
print(f"eBay stores: {len(data['ebay_stores'])}")

print("\n=== HTTP SERVER TEST PASSED ===")
