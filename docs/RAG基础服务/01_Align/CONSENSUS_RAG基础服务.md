# 共识文档：RAG基础服务 (Consensus)

## 1. 系统概述
本系统是一个标准的 MCP Server，提供对 RAGFlow 知识库的全生命周期管理能力，并封装了"智能澄清建议"的高级业务逻辑。

## 2. 接口规范 (Interface Specification)

### 2.1 知识库管理 (Dataset Ops)
| 工具名称 | 描述 | 参数 |
| :--- | :--- | :--- |
| `create_dataset` | 创建新知识库 | `name` (名称), `avatar` (可选), `description` (可选) |
| `delete_dataset` | 删除知识库 | `id` (知识库ID) |
| `list_datasets` | 列出所有知识库 | `page`, `page_size` |
| `update_dataset` | 更新知识库信息 | `id`, `name` (可选), `description` (可选) |

### 2.2 文档管理 (Document Ops)
| 工具名称 | 描述 | 参数 |
| :--- | :--- | :--- |
| `upload_document` | 上传文件到知识库 | `dataset_id`, `file_path` (本地绝对路径) |
| `delete_document` | 删除文件 | `document_id` |
| `list_documents` | 列出知识库文件 | `dataset_id`, `page`, `page_size`, `keywords` |
| `get_document_status` | 获取文件解析状态 | `document_id` |

### 2.3 业务场景 (Business Logic)
| 工具名称 | 描述 | 参数 |
| :--- | :--- | :--- |
| `fill_clarification_suggestions` | 场景一控制器：智能填充澄清建议 (编排原子工具) | `doc_path` (Markdown路径), `dataset_id` (知识库ID) |
| `create_shadow_file` | 原子工具：创建影子副本 | `file_path` |
| `extract_questions_from_doc` | 原子工具：从文档提取问题 | `file_path` |
| `apply_suggestions_to_doc` | 原子工具：将建议回填至文档 | `file_path`, `suggestions_map` (JSON string: {line_idx: content}) |
| `retrieve_rag_suggestion` | 原子工具：获取单条建议 | `dataset_id`, `query` |

## 3. 技术约束
1. **鉴权**: 使用 `RAGFLOW_API_KEY` 环境变量。
2. **传输**: 标准 Stdio JSON-RPC 2.0。
3. **文件处理**:
   - 上传时需处理文件读取权限。
   - 场景一生成建议时，**必须**使用"影子文件"机制 (`_ai_revision.md`)，严禁直接覆盖原文件。
4. **日志**: 所有操作记录到 `logs/mcp_server.log`，禁止输出到控制台。

## 4. 交付标准
- [ ] 源代码 (Python 3.10+)
- [ ] 可执行文件 (EXE)
- [ ] 完整 API 文档
- [ ] 场景一的测试用例验证
