# 用户手册 (User Manual)

## 简介
`rag_eval_flow` 是一个用于自动化评估 RAG 系统质量的 MCP 工具。它支持从知识库生成问答对、模拟 RAG 问答过程以及自动化评分。

## 配置
在使用前，请确保项目根目录下的 `.env` 文件中包含有效的 LLM API Key：
```env
GEMINI_API_KEY=your_api_key_here
```

## 工具使用

### 1. 生成测试数据集
从你的知识库文档中自动生成问答对。

```json
{
  "name": "generate_test_dataset",
  "arguments": {
    "source_path": "C:/path/to/knowledge_base.md",
    "output_path": "C:/path/to/dataset.csv",
    "num_pairs": 20
  }
}
```

### 2. 执行问答测试
基于生成的问答对和知识库，模拟回答过程。

```json
{
  "name": "run_qa_test",
  "arguments": {
    "dataset_path": "C:/path/to/dataset.csv",
    "knowledge_base_path": "C:/path/to/knowledge_base.md",
    "output_path": "C:/path/to/qa_results.csv"
  }
}
```

### 3. 评估回答质量
将生成结果与标准答案对比，进行打分。

```json
{
  "name": "evaluate_answers",
  "arguments": {
    "qa_result_path": "C:/path/to/qa_results.csv",
    "standard_dataset_path": "C:/path/to/dataset.csv",
    "output_path": "C:/path/to/evaluation_report.csv"
  }
}
```

## 常见问题
*   **LLM 调用失败**: 请检查网络连接及 `.env` 中的 API Key 是否正确。
*   **文件路径**: 请务必使用绝对路径。
