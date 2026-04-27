# Great Filmmakers — DXT Bundle

Claude Desktop extension for `great-filmmakers`. Same twelve filmmaker personas and seven slash commands as the Claude Code plugin, packaged as a Desktop Extension (DXT).

## Build the bundle

```bash
cd distribution/dxt
npm install
npx @anthropic-ai/dxt pack
```

The pack command produces `great-filmmakers.dxt` in this directory. Share that file with collaborators — they double-click it to install.

## Tools exposed

The MCP server in `server/index.js` exposes eight tools:

| Tool | Maps to |
|---|---|
| `list_filmmakers` | Browse the twelve personas with one-line blurbs |
| `filmmakers_channel` | The Claude Code skill `/filmmakers-channel <persona>` |
| `filmmakers_crew` | The Claude Code skill `/filmmakers-crew <source-file> [--backend ...]` |
| `filmmakers_project_init` | The Claude Code skill `/filmmakers-project-init` |
| `filmmakers_build_keyframes` | The Claude Code skill `/filmmakers-build-keyframes <source-file>` |
| `filmmakers_critique` | The Claude Code skill `/filmmakers-critique <content>` |
| `filmmakers_debate` | The Claude Code skill `/filmmakers-debate <topic> <a> <b>` |
| `filmmakers_edit` | The Claude Code skill `/filmmakers-edit <content>` |

`filmmakers_project_init` and `filmmakers_build_keyframes` require Claude Desktop's filesystem access to be configured for the user's project directory.

## Persona files

Each tool that loads a persona reads from `server/personas/`. These are byte-for-byte copies of the persona files in `agents/` at the plugin root. The smoke test verifies the two directories stay in sync:

```bash
cp agents/*.md distribution/dxt/server/personas/
bash tests/smoke.sh
```

## Versioning

The DXT version must match `package.json` and `.claude-plugin/plugin.json`. The smoke test validates this. To bump versions:

```bash
# Update all four:
.claude-plugin/plugin.json
package.json
distribution/dxt/manifest.json
distribution/dxt/package.json
distribution/dxt/server/index.js  # the new Server({version: "x.y.z"}) line

bash tests/smoke.sh
```

## Notes

- The DXT bundle was new in v1.10.0 (2026-04-26). Earlier versions of great-filmmakers shipped without a DXT, requiring users to install the Claude Code plugin instead.
- Filesystem-touching tools (project_init, build_keyframes) return prompt text describing what should happen on disk; the actual filesystem work happens through Claude Desktop's filesystem MCP integration. Pattern matches the other constellation plugins.
- For the Claude Code experience, install the plugin instead: `/plugin install great-filmmakers@sethshoultes`.
