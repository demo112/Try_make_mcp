# GetInRAGFlow MCP Server

> **v2.0 - Evolutionary Documentation Assistant**

GetInRAGFlow 是一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 构建的智能文档工作流服务。它深度集成了 RAGFlow 知识库能力，不仅能够辅助回答技术评审中的待澄清问题，更能基于决策结果**自动进化设计文档**，实现“文档即代码”的持续迭代闭环。

---

## 核心特性 (Features)

本项目采用**四核引擎 (Four-Core Engines)** 架构，覆盖从问题澄清 to 知识沉淀的全生命周期：

### 1. 🧠 推理引擎 (Inference Engine)
- **智能澄清**: 读取 `04_评审问题记录.md`，自动检索 L1/L2 知识库，填充高置信度的参考建议。
- **RAG 集成**: 深度对接 RAGFlow，支持多数据集联合检索与重排序。

### 2. 🧬 进化引擎 (Evolution Engine) **[核心能力]**
- **方案迭代**: 基于人工确认的澄清结论，自动定位并修订原方案文档 (`v1.0` -> `v1.1`)。
- **自我进化**: 支持 Append (追加) 与 Rewrite (重写) 模式，自动生成修订日志 (Revision Log)。

### 3. 🛡️ 治理引擎 (Governance Engine)
- **元数据合规**: 强制检查文档的 Product/Module/Version 元数据，确保资产可被索引。
- **红蓝对抗**: (Preview) 在知识入库前执行冲突检测，防止新知识与旧规范矛盾。

### 4. ♻️ 生命周期引擎 (Lifecycle Engine)
- **知识收割**: 自动从澄清文档中提取“已解决”的高价值问答对。
- **分层晋升**: 支持将知识精准推送至 L1 (企业级) 或 L2 (产品族) 知识库目录。

---

## 快速开始 (Quick Start)

### 前置要求
- Python 3.10+
- [RAGFlow](https://github.com/infiniflow/ragflow) 账号及 API Key
- MCP 兼容客户端 (如 Claude Desktop, Trae, Cursor 等)

### 1. 安装依赖
```bash
# 在项目根目录
python -m pip install -r requirements.txt
```

### 2. 环境变量配置
在 `.env` 文件中配置 RAGFlow 连接信息：

```ini
# RAGFlow Configuration
RAGFLOW_API_KEY=your_api_key_here
RAGFLOW_HOST=https://demo.ragflow.io
RAGFLOW_CHAT_ID=your_chat_id_optional
```

### 3. 启动服务
```bash
# 调试模式启动
python -m src.apps.rag_flow_mcp.server

# 或通过 MCP Inspector 调试
npx @modelcontextprotocol/inspector py src/apps/rag_flow_mcp/server.py
```

---

## 工具列表 (Available Tools)

### 主线任务：澄清与进化

| 工具名称 | 描述 | 输入参数 |
| :--- | :--- | :--- |
| `fill_clarification_suggestions` | **[推理]** 自动填充评审问题的 AI 建议 | `doc_path`: 评审记录文档路径 |
| `evolve_scheme_document` | **[进化]** 基于澄清结论进化方案文档 | `scheme_doc_path`: 原方案路径<br>`clarification_doc_path`: 澄清文档路径 |

### 支线任务：治理与沉淀

| 工具名称 | 描述 | 输入参数 |
| :--- | :--- | :--- |
| `check_metadata_compliance` | **[治理]** 检查文档元数据合规性 | `doc_path`: 文档路径 |
| `harvest_knowledge_candidates` | **[收割]** 提取待沉淀的知识候选 | `doc_path`: 澄清文档路径 |
| `promote_knowledge` | **[晋升]** 将知识存入知识库 | `candidate_json`: 候选数据<br>`target_kb_path`: 目标知识库目录 |

---

## 最佳实践 (Best Practices)

1.  **文档元数据**: 始终在 Markdown 头部包含 YAML Frontmatter，以便引擎识别知识归属。
    ```yaml
    ---
    product: MySaaS
    module: Auth
    version: 1.0
    ---
    ```
2.  **人工确认**: `Inference Engine` 仅提供建议，必须经由人工在文档中填写 `**回答**：...` 后，`Evolution Engine` 才会触发进化。
3.  **知识分层**: 建议将 `target_kb_path` 指向不同的目录结构 (e.g., `knowledge/L1_Enterprise`, `knowledge/L2_Product`) 以实现分层管理。

---

## 开发与测试 (Development)

运行端到端验证脚本，测试所有引擎的联动：

```bash
python -m src.apps.rag_flow_mcp.test_flow
```

该脚本会：
1. 创建 Mock 方案与澄清文档。
2. 模拟 AI 建议填充。
3. 模拟人工决策与文档进化。
4. 模拟知识收割与存储。

---

## 许可证 (License)

MIT License
