# CONSENSUS_安防APP知识库

## 1. 需求确认
经分析，我们将构建一个通用的、功能完备的安防APP文档知识库。该知识库将作为 ragflow 服务的输入数据源。

## 2. 交付范围
我们将生成以下目录结构的 Markdown 文档：

```
knowledge_base/
├── 01_Getting_Started/    # 快速入门
├── 02_Device_Management/  # 设备管理
├── 03_Live_View/          # 实时预览
├── 04_Playback/           # 录像回放
├── 05_Alarm_Notification/ # 报警通知
└── 06_Support/            # 帮助与支持 (FAQ, Troubleshooting)
```

## 3. 规范约定
- **文件格式**: Markdown (.md)
- **元数据**: 每个文件头部包含 YAML Frontmatter，用于 RAG 更好地分类。
  ```yaml
  ---
  category: [模块名]
  tags: [关键词1, 关键词2]
  ---
  ```
- **内容风格**: 
  - 标题清晰 (H1, H2, H3)
  - 步骤分明 (1. 2. 3.)
  - 包含“注意事项”和“前提条件”

## 4. 验收标准
- 文档覆盖 ALIGNMENT 中定义的所有模块。
- 至少生成 15-20 个核心文档文件。
- Markdown 语法正确。
