# Deploy AgentMagnet

## Option 1: Local (stdio) — for Claude Desktop, Cursor, VS Code

```bash
pip install -r requirements.txt
python -m agentmagnet
```

Add to your MCP client config:
```json
{
  "mcpServers": {
    "agentmagnet": {
      "command": "python",
      "args": ["-m", "agentmagnet"],
      "env": {
        "PYTHONPATH": "/path/to/AgentMagnet"
      }
    }
  }
}
```

## Option 2: VPS (HTTP) — for remote agents worldwide

### Quick deploy (Hetzner $5/mo, DigitalOcean $6/mo, Linode $5/mo)

```bash
# On your VPS (Ubuntu/Debian):
apt update && apt install -y docker.io docker-compose
git clone https://github.com/YOUR_USER/agentmagnet.git
cd agentmagnet
cp .env.example .env
nano .env  # Add your affiliate tags and x402 wallet
docker-compose up -d
```

### Or manual deploy:

```bash
pip install -r requirements.txt uvicorn
AM_X402_WALLET_ADDRESS=0xYourWallet \
AM_AMAZON_STORE_TAGS='{"com":"tag-20","de":"tag-21","uk":"tag-22"}' \
python -m agentmagnet.http_server
```

### Verify it works:

```bash
curl http://YOUR_VPS_IP:8000/health
curl -X POST http://YOUR_VPS_IP:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"TestAgent","version":"1.0"}}}'
```

## Option 3: PyPI package (agents install anywhere)

```bash
pip install agentmagnet-mcp
agentmagnet  # starts the MCP server
```

## Propagation

### Register on MCP directories:
```bash
python -m agentmagnet.propagation.directories
```

### Auto-register all identities:
```bash
# Set multiple identities in .env:
AM_ADDITIONAL_IDENTITIES='[
  {"name":"ProductSearch","port":8001},
  {"name":"GlobalShop","port":8002},
  {"name":"PriceFinder","port":8003},
  {"name":"AgentCommerce","port":8004},
  {"name":"WorldProduct","port":8005}
]'
```

### Agent SDK — 3 lines:
```python
from agentmagnet.propagation.sdk import AgentMagnetClient
client = AgentMagnetClient(agent_id="my-agent", referral_code="YOUR_REFERRAL")
result = await client.search("laptop", language="de")
```

## Architecture

```
                    ┌──────────────┐
   Claude/Cursor ──▶│  stdio MCP   │◀─▶ Local agents
                    └──────┬───────┘
                           │ same codebase
                    ┌──────▼───────┐
   Remote agents ──▶│  HTTP MCP    │◀─▶ VPS (0.0.0.0:8000)
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   x402 USDC  │◀─▶ 22 Amazon stores
                    │   Affiliates │◀─▶ 22 eBay stores
                    │   Cache      │◀─▶ AliExpress/SaaS/B2B
                    └──────────────┘
```
