"""
AgentMagnet — Automatic registration on ALL platforms.
Run this to register on 20+ platforms in one shot.

Usage:
    python scripts/register_everywhere.py
    python scripts/register_everywhere.py --dry-run
    python scripts/register_everywhere.py --mcp-only
"""

import asyncio, json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Register AgentMagnet everywhere")
    parser.add_argument("--dry-run", action="store_true", help="Dry run only")
    parser.add_argument("--mcp-only", action="store_true", help="Only MCP directories")
    args = parser.parse_args()

    dry_run = args.dry_run
    print("=" * 60)
    print("  AGENTMAGNET — REGISTRATION ON ALL PLATFORMS")
    print("=" * 60)

    # Step 1: MCP Directories
    print("\n[1/5] Registering on MCP Directories...")
    from agentmagnet.propagation.directories import register_all as register_mcp
    results = await register_mcp(dry_run=dry_run)
    registered = sum(1 for r in results if r["status"] in ("dry_run", 200, 201, "manual_action_required"))
    failed = sum(1 for r in results if r["status"] not in ("dry_run", 200, 201, "manual_action_required"))

    print(f"  Directories: {len(results)} total, {registered} OK, {failed} failed")
    for r in results:
        status_char = "+" if r["status"] in ("dry_run", 200, 201) else "~" if r["status"] == "manual_action_required" else "-"
        print(f"  [{status_char}] {r['directory']}: {r['status']}")

    if args.mcp_only:
        print(f"\n[+] MCP registration complete! {registered}/{len(results)} OK")
        return

    # Step 2: Claude Desktop config
    print("\n[2/5] Creating Claude Desktop config...")
    claude_config = {
        "mcpServers": {
            "agentmagnet": {
                "command": "python",
                "args": ["-m", "agentmagnet"],
                "env": {},
            }
        }
    }
    if os.name == "nt":
        config_path = os.path.expandvars(r"%APPDATA%\Claude\claude_desktop_config.json")
    else:
        config_path = os.path.expanduser("~/.config/Claude/claude_desktop_config.json")

    if dry_run:
        print(f"  [~] Would create: {config_path}")
    else:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(claude_config, f, indent=2)
        print(f"  [+] Created: {config_path}")
        print(f"  [!] Restart Claude Desktop to see AgentMagnet in your tools")

    # Step 3: OpenAI GPT Action
    print("\n[3/5] Preparing OpenAI GPT Action...")
    gpt_spec_path = os.path.join(os.path.dirname(__file__), '..',
                                  'agentmagnet', 'propagation', 'openai_gpt_action.json')
    if dry_run:
        print(f"  [~] GPT Action spec at: {gpt_spec_path}")
    else:
        print(f"  [+] GPT Action spec ready: {gpt_spec_path}")
        print(f"  [!] Go to https://chatgpt.com/gpts/editor and create a new GPT")
        print(f"      Paste openai_gpt_action.json content into Actions section")

    # Step 4: Cursor config
    print("\n[4/5] Creating Cursor config...")
    cursor_config = {
        "mcpServers": {
            "agentmagnet": {
                "command": "python",
                "args": ["-m", "agentmagnet"],
            }
        }
    }
    cursor_path = os.path.join(os.path.dirname(__file__), '..', '.cursor', 'mcp.json')
    if dry_run:
        print(f"  [~] Would create: {cursor_path}")
    else:
        os.makedirs(os.path.dirname(cursor_path), exist_ok=True)
        with open(cursor_path, "w") as f:
            json.dump(cursor_config, f, indent=2)
        print(f"  [+] Cursor config created: {cursor_path}")

    # Step 5: Verify deployment
    print("\n[5/5] Verifying deployment...")
    import httpx
    try:
        from agentmagnet.config import settings
        url = settings.server_url
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{url}/health")
            if resp.status_code == 200:
                print(f"  [+] Server active: {url}")
            else:
                print(f"  [!] Server responded with status {resp.status_code}")
    except Exception as e:
        print(f"  [!] Could not verify server: {e}")
        print(f"  [!] Deploy to Render first or run locally:")
        print(f"      python -m agentmagnet.http_server")

    print("\n" + "=" * 60)
    print("  REGISTRATION COMPLETE!")
    print("=" * 60)
    print(f"""
Summary:
  [+] {registered} MCP directories registered
  [+] Configs ready: Claude Desktop, Cursor
  [+] GPT Action spec ready for ChatGPT
  [+] {len(results)} platforms covered

Manual steps remaining:
  1. Create GPT at chatgpt.com/gpts/editor
  2. PR to github.com/punkpeye/awesome-mcp-servers
  3. Post on ProductHunt
  4. Share claude_desktop_config.json with developer friends
""")


if __name__ == "__main__":
    asyncio.run(main())
