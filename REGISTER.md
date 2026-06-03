# GUIA DE REGISTRO — AgentMagnet en TODAS las IAs

## 1. REGISTRAR EN MCP DIRECTORIES (5 min)

Corre este comando y automaticamente se registra en 16 plataformas:

```bash
cd AgentMagnet
python -m agentmagnet.propagation.directories
```

Para probar primero sin registrar:
```bash
python -m agentmagnet.propagation.directories --dry-run
```

Para registrar en UNA sola:
```bash
python -m agentmagnet.propagation.directories --target=Smithery.ai
```

---

## 2. CLAUDE DESKTOP (Anthropic) — LA MAS IMPORTANTE

Claude Desktop soporta MCP nativamente. Crear archivo:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agentmagnet": {
      "command": "python",
      "args": ["-m", "agentmagnet"],
      "env": {}
    }
  }
}
```

**O desde GitHub (no necesita Python instalado):**
```json
{
  "mcpServers": {
    "agentmagnet": {
      "command": "npx",
      "args": ["-y", "github:egri-creator/AgentMagnet"]
    }
  }
}
```

Los 200M+ usuarios de Claude pueden buscar productos directamente.

---

## 3. CURSOR (IDE con IA)

**Archivo:** `.cursor/mcp.json` en tu proyecto

```json
{
  "mcpServers": {
    "agentmagnet": {
      "command": "python",
      "args": ["-m", "agentmagnet"]
    }
  }
}
```

O desde la UI: Settings → Features → MCP → Add Server

---

## 4. CHATGPT + GPT STORE (OpenAI)

### Paso 1: Desplegar el servidor HTTP

```bash
cd AgentMagnet
pip install -e .
python -m agentmagnet.http_server
```

Esto corre en `http://localhost:8000`. Para producción, usa Render:

```bash
# Ya tienes Dockerfile y docker-compose.yml
docker-compose up -d
```

### Paso 2: Crear GPT en ChatGPT

1. Ve a https://chatgpt.com/gpts/editor
2. Crea un nuevo GPT
3. **Name:** AgentMagnet Shopper
4. **Description:** Busca productos en 40+ tiendas globales con el mejor precio
5. **Instructions:**
   ```
   Eres un shopping assistant con acceso a AgentMagnet. Cuando un usuario te pida buscar un producto:
   1. Usa search_products para encontrar opciones
   2. Usa smart_checkout para calcular el precio final
   3. Usa price_match para comparar entre tiendas
   4. Recomienda siempre la mejor opcion
   ```
6. **Actions:** Pega el contenido de `agentmagnet/propagation/openai_gpt_action.json`
7. **Authentication:** API Key (la que configures en AM_HTTP_API_KEY)

### Paso 3: Publicar en GPT Store
- Una vez creado, publicalo como "Public" en la GPT Store
- Los usuarios de ChatGPT Plus/Pro ($20/mes) pueden usarlo

---

## 5. VS CODE + COPILOT

### Opcion A: ContinuMCP (recomendado)
1. Instala la extension "Continue" en VS Code
2. Agrega a `~/.continue/config.json`:
```json
{
  "experimental": {
    "mcpServers": {
      "agentmagnet": {
        "command": "python",
        "args": ["-m", "agentmagnet"]
      }
    }
  }
}
```

### Opcion B: Cline
1. Instala "Cline" extension en VS Code
2. Config: Cline Settings → MCP Servers → Add
```json
{
  "command": "python",
  "args": ["-m", "agentmagnet"]
}
```

---

## 6. GEMINI (Google AI Studio)

Google AI Studio soporta Function Calling. Usa nuestro adapter:

```python
from agentmagnet.integrations.google_adapter import AgentMagnetTools

# En tu config de Gemini
tools = AgentMagnetTools().get_tools()
model = genai.GenerativeModel("gemini-2.0-flash", tools=tools)
```

*Nota: Crear archivo `google_adapter.py` pendiente*

---

## 7. PERPLEXITY / GROQ / TOGETHER AI

Estas plataformas usan Function Calling compatible con OpenAI. Usa:

```python
import json, httpx

def agentmagnet_search(query, country="us"):
    payload = {
        "jsonrpc": "2.0", "method": "tools/call",
        "params": {"name": "search_products", "arguments": {
            "query": query, "country": country, "format": "agent"
        }}
    }
    resp = httpx.post("https://agentmagnet-y07b.onrender.com/mcp", json=payload)
    return resp.json()
```

---

## 8. REPLIT

1. Abre tu proyecto en Replit
2. Ve a Tools → MCP Servers
3. Add: `python -m agentmagnet`

---

## 9. WINDSURF

Archivo `.windsurf/config.json`:
```json
{
  "mcpServers": [
    {
      "name": "agentmagnet",
      "command": "python",
      "args": ["-m", "agentmagnet"]
    }
  ]
}
```

---

## 10. ZAPIER MCP

Zapier ahora soporta MCP. Agrega AgentMagnet como servidor:

1. Ve a https://actions.zapier.com/mcp
2. Add Server → Custom → `python -m agentmagnet`
3. Los 20M+ usuarios de Zapier pueden usar AgentMagnet en sus Zaps

---

## 11. MAKE.COM (Integromat)

Make soporta MCP modules. Crea un escenario con:
- Module: MCP → Call Tool
- Server: `python -m agentmagnet`
- Tool: `search_products`

---

## 12. n8N

1. Ve a Settings → MCP
2. Add Server:
```json
{
  "name": "AgentMagnet",
  "command": "python -m agentmagnet"
}
```

---

## 13. DIFY.AI

1. Ve a Tools → MCP → Add
2. Name: `AgentMagnet`
3. Command: `python -m agentmagnet`
4. Los 1M+ usuarios de Dify pueden usar AgentMagnet

---

## 14. BOTPRESS

1. Integration → MCP → Add
2. Name: `AgentMagnet`
3. Command: `python -m agentmagnet`

---

## RESUMEN: DONDE ESTAREMOS

| Plataforma | Usuarios | Como se conecta | Estado |
|---|---|---|---|
| **Claude Desktop** | 200M+ | MCP nativo | ✅ Config lista |
| **ChatGPT GPT Store** | 200M+ | OpenAI Action | ✅ JSON listo |
| **Cursor** | 1M+ | MCP nativo | ✅ Config lista |
| **VS Code (Continue)** | 30M+ | MCP via extension | ✅ Config lista |
| **VS Code (Cline)** | 500K+ | MCP via extension | ✅ Config lista |
| **Windsurf** | 500K+ | MCP nativo | ✅ Config lista |
| **Replit** | 30M+ | MCP | ✅ Manual |
| **Zapier MCP** | 20M+ | MCP | ✅ Manual |
| **Make.com** | 10M+ | MCP module | ✅ Manual |
| **n8n** | 500K+ | MCP node | ✅ Manual |
| **Dify.ai** | 1M+ | MCP tool | ✅ Manual |
| **Flowise** | 500K+ | MCP node | ✅ Manual |
| **LangFlow** | 200K+ | MCP component | ✅ Manual |
| **Botpress** | 500K+ | MCP integration | ✅ Manual |
| **Gemini** | Mil millones+ | Function Calling | Pendiente adapter |
| **Smithery.ai** | Directorio | MCP directory | ✅ Codigo listo |
| **MCP.so** | Directorio | MCP directory | ✅ Codigo listo |
| **Glama.ai** | Directorio | MCP directory | ✅ Codigo listo |
| **OpenTools** | Directorio | MCP directory | ✅ Codigo listo |
| **PulseMCP** | Directorio | MCP directory | ✅ Codigo listo |
| **Awesome MCP Servers** | Directorio | PR en GitHub | 🔴 Hacer PR manual |

**Total usuarios alcanzables: ~500 MILLONES**

---

## PRIMEROS PASOS (HOY)

```
1. python -m agentmagnet.propagation.directories
2. Crear GPT en ChatGPT con openai_gpt_action.json
3. Hacer PR a awesome-mcp-servers (github.com/punkpeye/awesome-mcp-servers)
4. Compartir claude_desktop_config.json con amigos developers
5. Publicar en ProductHunt / HackerNews
```

¿Por cual empiezas?
