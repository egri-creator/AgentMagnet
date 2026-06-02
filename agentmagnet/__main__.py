"""AgentMagnet MCP Server entry point (stdio mode).

Run locally:
    python -m agentmagnet

Run HTTP server (VPS):
    python -m agentmagnet.http_server
"""

import anyio
from .server import AgentMagnetServer


def main():
    server = AgentMagnetServer()
    anyio.run(server.run_stdio)


if __name__ == "__main__":
    main()
