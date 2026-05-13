# Try_make_mcp (MCP Factory)

<!-- mcp-name: io.github.demo112/try-make-mcp -->

> ⚡ A Model Context Protocol (MCP) service production factory. Build, validate, and deploy production-ready MCP servers in minutes.

[![MCP](https://img.shields.io/badge/MCP-Ready-blue)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/downloads/)

## 🚀 What is Try_make_mcp?

Try_make_mcp is a **systematic MCP development platform** that transforms the scattered, manual process of building MCP servers into a streamlined factory pipeline. Instead of starting from scratch every time, you use battle-tested templates and automation to go from idea → working MCP server → production deployment.

### Why MCP Factory?

| Approach | Time | Quality | Maintainability |
|----------|------|---------|-----------------|
| From scratch | Hours–Days | Varies | High effort |
| **Try_make_mcp** | **Minutes** | **Consistent** | **Low effort** |

## ✨ Core Applications

| App | Description |
|-----|-------------|
| **`mcp_factory`** | The MCP that produces MCPs — project initialization, building, and validation |
| **`everything2md`** | Convert PDF/Office/OCR documents to Markdown with structure preservation |
| **`md_converter`** | Markdown → Word/PDF/Excel with formatting fidelity |
| **`rag_flow_mcp`** | RAGFlow knowledge retrieval integration for RAG pipelines |
| **`rag_eval_flow`** | RAG evaluation and benchmarking across test datasets |

## 📦 Quick Start

```bash
# Install
git clone https://github.com/demo112/Try_make_mcp.git
cd Try_make_mcp
pip install -r requirements.txt

# Run any app
cd src/apps/md_converter
python server.py

# Or use the MCP factory to scaffold a new MCP server
cd src/apps/mcp_factory
python server.py
```

## 🏗️ Architecture

```
Try_make_mcp/
├── src/
│   ├── apps/              # 5 production MCP applications
│   │   ├── mcp_factory/   # Factory for creating new MCP servers
│   │   ├── everything2md/ # Universal document → Markdown
│   │   ├── md_converter/  # Markdown → Word/PDF/Excel
│   │   ├── rag_flow_mcp/  # RAGFlow integration
│   │   └── rag_eval_flow/ # RAG benchmarking
│   ├── factory/           # Core factory engine
│   │   ├── init_app.py    # Project scaffolding
│   │   └── build_app.py   # Build & package
│   └── common/            # Shared utilities
├── docs/                  # Documentation (EN + 中文)
├── tests/                 # Test suites
└── .trae/rules/           # 6A development workflow
```

## 🔄 6A Development Workflow

Try_make_mcp enforces a disciplined 6-stage process for every MCP server:

1. **Align** — Define the MCP's purpose and scope
2. **Authorize** — Set up permissions and dependencies
3. **Acquire** — Gather required resources and data
4. **Author** — Write the MCP server code
5. **Audit** — Run automated tests and validation
6. **Activate** — Deploy to production

## 🎯 Key Features

- **Zero-config templates**: Jump-start MCP servers with proven patterns
- **Automated testing**: Catch issues before deployment
- **Multi-format support**: PDF, Office, OCR, Markdown, Word, PDF, Excel
- **RAG-ready**: Built-in RAGFlow integration and evaluation tools
- **Bilingual docs**: English and Chinese documentation included

## 📖 Documentation

- [Getting Started Guide](docs/getting-started.md)
- [6A Workflow Reference](docs/6a-workflow.md)
- [MCP Server Patterns](docs/mcp-patterns.md)
- [中文文档](docs/README.zh.md)

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **MCP Framework**: [FastMCP](https://github.com/jlowin/fastmcp)
- **LLM Integration**: [LiteLLM](https://github.com/BerriAI/litellm)
- **Document Processing**: python-docx, xhtml2pdf, openpyxl, BeautifulSoup4
- **Testing**: pytest

## 🤝 Contributing

See `.trae/rules/project_rules.md` for the 6A development workflow guidelines.

## 📄 License

MIT License
