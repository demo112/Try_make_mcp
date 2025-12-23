# RAGFlow API Reference (Verified)

本文档记录了在项目开发过程中经过实际验证可用的 RAGFlow API 接口。由于 RAGFlow 版本迭代较快，官方文档可能滞后，请以本文档为准。

**当前验证版本**: RAGFlow v0.10.0+ (推测) / v1.0 API

## 1. 认证 (Authentication)

所有接口均需通过 HTTP Header 进行 Bearer Token 认证。

*   **Header**: `Authorization: Bearer <YOUR_API_KEY>`

## 2. 知识库管理 (Knowledge Base / Dataset)

### 2.1 获取知识库列表

*   **Endpoint**: `GET /api/v1/datasets`
*   **Query Parameters**:
    *   `page`: 页码 (默认 1)
    *   `page_size`: 每页数量 (默认 30)
*   **Response**:
    ```json
    {
      "code": 0,
      "message": "",
      "data": [
        {
          "id": "fcf0b044d4c911f083cd9a521ad2f171",
          "name": "Project_Knowledge_Base",
          "avatar": "",
          "tenant_id": "...",
          "description": "...",
          "permission": "me",
          "document_count": 5,
          "chunk_count": 120,
          "parse_status": "1",
          "create_date": "...",
          "update_date": "..."
        }
      ],
      "total": 1
    }
    ```

### 2.2 获取知识库文件列表

*   **Endpoint**: `GET /api/v1/datasets/{dataset_id}/documents`
*   **Path Parameters**:
    *   `dataset_id`: 知识库 ID
*   **Query Parameters**:
    *   `page`: 页码
    *   `page_size`: 每页数量
    *   `keywords`: (可选) 文件名搜索关键词
*   **Response**:
    ```json
    {
      "code": 0,
      "message": "",
      "data": [
        {
          "id": "doc_id_123",
          "name": "UserManual.md",
          "chunk_count": 25,
          "run_status": "1", // 1=Parsed
          "create_date": "..."
        }
      ],
      "total": 5
    }
    ```

## 3. 检索 (Retrieval)

### 3.1 检索知识切片 (Retrieve Chunks) - **核心接口**

*   **Endpoint**: `POST /api/v1/retrieval`
*   **Description**: 不经过 LLM 生成，直接根据 Query 召回相关的向量切片。速度极快，适合纯检索场景。
*   **Request Body**:
    ```json
    {
      "question": "安防",                  // 检索关键词
      "dataset_ids": ["fcf0...171"],      // 目标知识库 ID 列表
      "page": 1,
      "page_size": 30,
      "similarity_threshold": 0.2,        // 相似度阈值 (0~1)
      "vector_similarity_weight": 0.3,    // 向量检索权重 (vs 关键词检索)
      "top_k": 1024                       // 初筛候选数量
    }
    ```
*   **Response**:
    ```json
    {
      "code": 0,
      "message": "",
      "data": {
        "chunks": [  // 注意：某些版本数据包裹在 chunks 字段下
          {
            "chunk_id": "...",
            "content_with_weight": "安防APP是...", // 切片内容
            "doc_id": "...",
            "doc_name": "UserManual.md",
            "similarity": 0.8651,
            "vector_similarity": 0.85,
            "term_similarity": 0.88
          }
        ],
        "total": 22
      }
    }
    ```

## 4. 对话 (Chat / Generation)

### 4.1 AI 问答 (Chat Completion)

*   **Endpoint**: `POST /api/v1/chats_openai/{chat_id}/chat/completions`
*   **Warning**: 此接口包含 LLM 生成环节，可能响应较慢 (10s+)，需设置较长的 Timeout。
*   **Path Parameters**:
    *   `chat_id`: 在 RAGFlow 界面创建的 Chat Assistant ID。
*   **Request Body** (OpenAI 兼容格式):
    ```json
    {
      "messages": [
        {"role": "user", "content": "什么是安防？"}
      ],
      "stream": false,
      "quote": true // 请求返回引用源
    }
    ```
*   **Response**:
    ```json
    {
      "code": 0,
      "data": {
        "answer": "安防是指...",
        "reference": [
           {"doc_name": "...", "content": "..."}
        ]
      },
      "choices": [...] // OpenAI 兼容字段
    }
    ```
