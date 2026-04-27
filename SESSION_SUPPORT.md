# GDS Session Support (Aura Graph Analytics)

The MCP server now supports both GDS Plugin (on-prem Neo4j) and GDS Aura Graph Analytics (sessions) modes.

## Mode Detection

The server automatically detects which mode to use by checking if `gds.session.list()` is available:
- If available → **Session Mode** (Aura Graph Analytics)
- If not available → **Plugin Mode** (on-prem GDS)

## Session Mode Configuration

When using Aura Graph Analytics, you need to provide Aura API credentials as environment variables:

```bash
export AURA_API_CLIENT_ID="your-client-id"
export AURA_API_CLIENT_SECRET="your-client-secret"
export AURA_API_PROJECT_ID="your-project-id"
```

### Optional Environment Variables

- `SESSION_MEMORY_GB`: Memory size for the session in GB (default: 8)
- `SESSION_NAME`: Name for the session (default: "mcp_gds_session")
- `SESSION_TTL_HOURS`: Time-to-live for the session in hours (default: 24)

Example:
```bash
export SESSION_MEMORY_GB=16
export SESSION_NAME="my_analysis_session"
export SESSION_TTL_HOURS=48
```

## Session Lifecycle

### Lazy Initialization
Sessions are created on-demand when the first graph projection or algorithm is run, not at server startup. This prevents wasting resources on unused sessions.

### Available Session Tools

When in session mode, the server exposes additional tools:

1. **list_sessions**: List all GDS sessions
2. **delete_session**: Delete a specific session or the current session
3. **recreate_session**: Recreate the current session with a new memory size (useful for OOM errors)

### Handling Out-of-Memory Errors

If you encounter OOM errors during graph projection or algorithm execution:

1. Use the `recreate_session` tool with a larger memory size:
   ```json
   {
     "tool": "recreate_session",
     "arguments": {
       "memoryGB": 16
     }
   }
   ```

2. Or set the environment variable and restart the server:
   ```bash
   export SESSION_MEMORY_GB=16
   ```

## Graph Projections

The server uses **Cypher projections** for both modes:
- **Plugin mode**: Uses `gds.graph.project()`
- **Session mode**: Uses `gds.graph.project.remote()`

The projection logic automatically selects the appropriate function based on the detected mode.

## Algorithm Support

Most GDS algorithms work identically in both modes. However, session mode has some limitations:

### Unsupported Algorithms in Session Mode
- Random Walk
- HITS
- Topological Sort
- Triangles (listing)
- GraphSAGE

### Execution Modes
All supported algorithms work with:
- `stream` mode
- `mutate` mode
- `write` mode (requires write-back configuration)
- `stats` mode

## Example Usage

### Plugin Mode (on-prem)
```bash
python -m mcp_server_neo4j_gds.server bolt://localhost:7687 neo4j password
```

### Session Mode (Aura)
```bash
export AURA_API_CLIENT_ID="..."
export AURA_API_CLIENT_SECRET="..."
export AURA_API_PROJECT_ID="..."
export SESSION_MEMORY_GB=8

python -m mcp_server_neo4j_gds.server neo4j+s://xxxxx.databases.neo4j.io neo4j password
```

## Troubleshooting

### "Missing Aura API credentials" Error
Ensure all three environment variables are set:
- `AURA_API_CLIENT_ID`
- `AURA_API_CLIENT_SECRET`
- `AURA_API_PROJECT_ID`

### Session Creation Failures
- Check that your Aura instance supports sessions
- Verify your API credentials are correct
- Ensure you have sufficient quota for the requested memory size

### Graph Projection Errors
- Sessions only support Cypher projections, not native projections
- The server automatically handles this, but custom projection queries must use Cypher syntax

## Technical Details

### Session Manager
The `SessionManager` class handles:
- Mode detection via `detect_mode()`
- Lazy session creation via `create_or_get_session()`
- Session lifecycle management
- Credential initialization

### Graph Projection
The `projected_graph()` function in `gds.py` automatically:
- Detects the current mode
- Uses `gds.graph.project.remote()` for sessions
- Uses `gds.graph.project()` for plugin mode
- Handles graph cleanup in both modes
