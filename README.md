## Cortex MCP Overview

>[!NOTE]
>**Research Preview**
>
>Not seeing the results you expect? This is an early version of the Cortex MCP. Please send feedback and bug reports to Cortex Customer Engineering.

Cortex MCP is a Model Context Protocol server that provides access to the Cortex API. It uses relevant context from your workspace, ensuring awareness of your system's structure when answering your questions.

You can query information in natural language, powering faster decisions and efficient processes. For example:

- Who is the right person to handle an incident with backend-server?
- Show me the services that belong to the platform engineering team
- We're having an incident with backend-server, give me a summary of information to help handle the incident

## Requirements

Before getting started, you'll need:

- **MCP Client**: Claude Desktop or other MCP-compatible client
- **Cortex Personal Access Token**: [Create a token](https://docs.cortex.io/settings/api-keys/personal-tokens) in your Cortex workspace settings.

## Installation

Then configure your MCP client. We've tested this with Claude Desktop, and Cursor, but it should work with any MCP-compatible client.:

### Claude Desktop

```json
{
  "mcpServers": {
    "cortex": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env",
        "CORTEX_API_TOKEN=YOUR_API_TOKEN_HERE",
        "ghcr.io/cortexapps/cortex-mcp:latest"
      ]
    }
  }
}
```


### Cursor

```json
{
  "mcpServers": {
    "cortex": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env",
        "CORTEX_API_TOKEN=YOUR_API_TOKEN_HERE",
        "ghcr.io/cortexapps/cortex-mcp:latest"
      ]
    }
  }
}

```

### VSCode

[VS Code MCP Servers Documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)

Sample `.vscode/mcp.json`

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "cortex-key",
      "description": "Cortex API Key",
      "password": true
    }
  ],
  "servers": {
    "Cortex": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "ghcr.io/cortexapps/cortex-mcp:latest"
      ],
      "env": {
        "CORTEX_API_TOKEN": "${input:cortex-key}"
      }
    }
  }
}

```


## Support

- GitHub Issues: https://github.com/cortexapps/cortex-mcp/issues
- Email: help@cortex.io

## License

MIT License - see [LICENSE](LICENSE) file for details.
