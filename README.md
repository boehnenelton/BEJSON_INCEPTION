---
project_name: Cli_Chunker
version: 2.5.0
status: Agent-Ready
relational_id: gcli-tool-cli-chunker-001
---

# Cli Chunker: Agentic Project Packager (AX-2026)

[Agent-Ready] [MCP-Compatible] [llms.txt: Verified]

Cli Chunker is a high-density project snapshot utility designed for the 2026 AI-Native development lifecycle. It transforms entire directory structures into single, high-fidelity BEJSON 104db payloads for rapid delivery to Large Language Models (LLMs) or for transient versioning. It features a robust indexing system for managing multiple projects and versions.

## 1. Core Philosophy
In the 2026 ecosystem, 'context is currency.' Cli Chunker focuses on transient context snapshots. It is optimized for speed, numeric indexing, and 'zero-config' operation, making it the primary tool for feeding codebase state into reasoning agents.

## 2. Feature Highlights
- **BEJSON 104db Standard**: High-fidelity, positional integrity, AI-readable.
- **Numeric Indexing**: Rapidly manage projects and history via simple IDs.
- **Versioned Archiving**: Automatic versioning (v1, v2...) for every chunk operation.
- **Project Registry**: Tracks source paths for one-click re-chunking.
- **Atomic Operations**: Prevents data corruption using `lib_bejson_core`.
- **MIME Evasion**: Appends `.txt` to bypass restricted file uploads on AI platforms.

## 3. High-Density Command Map

| Command | Action | Mission |
| :--- | :--- | :--- |
| `--chunk <DIR>` | Chunk | Snapshots a directory into a new versioned BEJSON chunk. |
| `--chunk-index <ID>` | Re-Chunk | Rapidly update a project by its registry ID. |
| `--list-project-index`| Discovery | List all registered projects with numeric IDs. |
| `--unchunk <FILE>` | Restore | Rebuilds a project directory from a BEJSON chunk. |
| `--unchunk-index <ID>`| Restore | Rebuilds a project from a historical ID. |
| `--list-unchunk-index`| Forensic | List all historical chunks with numeric IDs. |
| `--get-versions <ID>` | Audit | View all saved version folders for a project ID. |
| `--delete-version <ID> <v>`| Prune | Surgically remove a specific version (e.g., v1). |
| `--expell-project <ID>`| Registry | Remove project from registry (preserves files). |
| `--delete-project <ID>`| Wipe | Remove project from registry and delete ALL its chunks. |

### Global Options
- `--dest <DIR>`: Specify a custom output directory for unchunking operations.

## 4. Quick Start
```bash
# Register and chunk a new project
python3 Cli_Chunker.py --chunk ~/my-awesome-repo

# List projects to find your ID
python3 Cli_Chunker.py --list-project-index

# Re-chunk project #1
python3 Cli_Chunker.py --chunk-index 1

# Unchunk the most recent history entry
python3 Cli_Chunker.py --unchunk-index 1
```

## 5. Documentation Stack
- **Grounding**: [AGENTS.md](./AGENTS.md)
- **Technical Manual**: [DOCUMENTATION.md](./DOCUMENTATION.md)
- **Operational Logic**: [OPERATIONAL.md](./OPERATIONAL.md)
- **Typed Specification**: [SPECIFICATION.md](./SPECIFICATION.md)

---
Author: Elton Boehnen
Version: 2.5.0
Date: 2026-06-10
