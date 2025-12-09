# GetInRAGFlow 需求分析与实现

## 1. 简介
本方案旨在解决评审工作流中产生的大量待澄清点问题。通过集成 RAGFlow 知识库，自动检索已有方案和文档，为新特性的待澄清点提供高质量的解答，并建立质量评估机制。

## 2. 核心价值
- **效率提升**：自动化回答重复性或已有文档覆盖的澄清问题。
- **质量保障**：防止因遗漏旧有知识而导致的新方案设计缺陷。
- **知识复用**：激活沉淀的文档资产，服务于新特性评审。

## 3. 6A 工作流状态
- [x] Stage 0: Initialization
- [x] Stage 1: Align
- [x] Stage 2: Architect
- [x] Stage 3: Atomize
- [x] Stage 4: Approve
- [x] Stage 5: Automate
- [x] Stage 6: Assess

## 4. 快速开始
### 配置
在 `.env` 中设置：
```bash
RAGFLOW_API_KEY=your_key
RAGFLOW_HOST=http://your_host
```

### 使用
调用 MCP 工具 `process_review_doc`，传入评审问题文档路径。
