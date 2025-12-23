# 验收测试报告 (Acceptance Report)

## 1. 测试概览
*   **测试时间**: 2025-12-11
*   **测试版本**: v1.0.0
*   **测试环境**: Windows 11, Python 3.10+, `.venv`

## 2. 功能测试
### 2.1 生成测试数据集
*   **输入**: Markdown 知识库。
*   **操作**: 调用 `generate_qa_pairs`。
*   **结果**: 成功生成 CSV 文件，包含 Question 和 Answer 列。
*   **状态**: ✅ 通过 (Mock 测试)

### 2.2 问答执行
*   **输入**: 生成的 CSV + 知识库。
*   **操作**: 调用 `run_rag_simulation`。
*   **结果**: 成功生成结果 CSV，包含 Generated Answer。
*   **状态**: ✅ 通过 (Mock 测试)

### 2.3 评估打分
*   **输入**: 结果 CSV + 标准 CSV。
*   **操作**: 调用 `evaluate_results`。
*   **结果**: 成功生成评估报告 CSV，包含 Score 和 Reason。
*   **状态**: ✅ 通过 (Mock 测试)

## 3. 代码质量
*   **Lint**: 无明显语法错误。
*   **结构**: 分层清晰 (`server.py` + `logic.py`)。
*   **依赖**: `pandas`, `litellm` 已加入环境。

## 4. 遗留问题
*   **Token 限制**: 目前仅做了简单的 100k 字符截断，对于超大文档需要实现切片检索 (Chunking)。
*   **模型配置**: 目前模型名称硬编码为 `gemini/gemini-2.0-flash-exp`，建议后续支持参数配置。

## 5. 结论
核心功能链路已打通，可作为 v1.0 版本交付。
