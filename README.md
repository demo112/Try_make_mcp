# Try_make_mcp (MCP Factory)

A Model Context Protocol (MCP) service production factory. Standardizes and pipelines the creation of high-quality MCP services.

## Overview

Try_make_mcp provides a systematic approach to building and deploying MCP servers. It combines project templates, automated tooling, and quality validation to reduce the friction of MCP adoption.

## Core Applications

| App | Source | Description |
|-----|--------|-------------|
| **mcp_factory** | src/apps/mcp_factory | The MCP that produces MCPs — project initialization, building, and validation |
| **everything2md** | src/apps/everything2md | Convert PDF/Office/OCR documents to Markdown |
| **rag_flow_mcp** | src/apps/rag_flow_mcp | RAGFlow knowledge retrieval integration |
| **rag_eval_flow** | src/apps/rag_eval_flow | RAG evaluation and benchmarking tool |
| **md_converter** | src/apps/md_converter | Markdown to Word/PDF/Excel converter |

## Features

- **Standardized workflow**: Follow the 6A development process (Align → Authorize → Acquire → Author → Audit → Activate)
- **Project templates**: Jump-start new MCP servers with proven patterns
- **Automated verification**: Catch issues early with built-in testing
- **Documentation included**: Every app has comprehensive docs

## Quick Start

```bash
# Clone the repository
git clone https://github.com/demo112/Try_make_mcp.git
cd Try_make_mcp

# Install dependencies
pip install -r requirements.txt

# Explore the apps
ls src/apps/
```

## Project Structure

```
Try_make_mcp/
├── src/apps/           # MCP application source code
├── docs/               # Documentation for each app
├── tests/              # Test suites
├── scripts/            # Utility scripts
└── .trae/rules/        # Development workflow rules
```

## License

MIT

## Contributing

See `.trae/rules/project_rules.md` for the 6A development workflow.
