# Releasing gds-agent

Every step here is run by a maintainer. Nothing publishes automatically until you push a `v*` tag.

## One-time prerequisites

1. **PyPI trusted publishing**: on pypi.org, add this repo's `release.yml` workflow as a trusted publisher for the `gds-agent` project (Manage → Publishing). No API token needed afterwards.
2. **MCP registry ownership**: the marker `<!-- mcp-name: io.github.neo4j-contrib/gds-agent -->` must be present in `mcp_server/README.md` (the PyPI long-description) in the release that reaches PyPI — the registry verifies ownership by finding it on pypi.org. Publishing under `io.github.neo4j-contrib` uses GitHub OIDC auth from this repo's Actions, which must belong to the `neo4j-contrib` org.
3. **Marketplace/plugin**: no registration needed — users add this GitHub repo directly. Optional: submit the plugin to Anthropic's community marketplace at https://platform.claude.com/plugins/submit (run `claude plugin validate .` first).

## Per-release steps

1. Update `CHANGELOG.md` (move entries under the new version heading).
2. Bump every manifest in lockstep:
   ```bash
   python3 scripts/bump_version.py 1.0.0
   python3 scripts/bump_version.py --check
   ```
   This updates `mcp_server/pyproject.toml`, `.claude-plugin/plugin.json`, `server.json` (both fields), `mcp_server/manifest.json`, and `gemini-extension.json`. Claude Code only offers plugin updates when `plugin.json`'s version changes.
3. Run the test suite and formatting checks (`uv run pytest tests -v`, `uv run ruff format --check`) inside `mcp_server/`.
4. **Smoke-test the MCPB bundle locally** (uv-type bundles are still marked experimental by the MCPB spec):
   ```bash
   npx -y @anthropic-ai/mcpb pack mcp_server /tmp/gds-agent.mcpb
   ```
   Double-click `/tmp/gds-agent.mcpb` to install into Claude Desktop, fill in credentials, confirm tools list and one algorithm runs. If uv-type fails on a target platform, the fallback is `server.type: "python"` with dependencies vendored into `server/lib`.
5. **Smoke-test the skill zip**: build it like CI does (folder at zip root):
   ```bash
   (cd skills && zip -r /tmp/neo4j-graph-data-scientist-skill.zip neo4j-graph-data-scientist)
   ```
   Upload via Claude Desktop → Settings → Customize → Skills (requires code execution enabled) and confirm it triggers on a graph question.
6. Commit the version bump, then tag and push:
   ```bash
   git tag v1.0.0 && git push origin main v1.0.0
   ```
   The tag triggers `release.yml`, which: verifies the tag matches the manifests → builds and publishes to PyPI → publishes `server.json` to the MCP registry → packs the `.mcpb` → zips the skill → attaches all artifacts to a GitHub release.
7. After the workflow finishes: verify the PyPI page renders, `uvx gds-agent@latest` starts, the registry entry appears (`https://registry.modelcontextprotocol.io/v0/servers?search=gds-agent`), and the GitHub release carries the `.mcpb` + skill zip.
8. In a Claude Code checkout: `/plugin marketplace update neo4j-gds` then `/plugin update gds-agent` to confirm the plugin update flows.

## Registry note

The first `mcp-publisher publish` can only succeed after the PyPI release containing the `mcp-name:` marker is live (step 6 ordering inside the workflow handles this; if the registry step races PyPI's CDN, re-run the job).
