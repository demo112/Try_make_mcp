# FINAL_安防APP知识库

## 项目总结
本项目成功构建了一个面向 ragflow 服务的安防APP文档知识库。通过 6A 工作流的规范执行，我们生成了结构化、高质量的 Markdown 文档集合。

## 成果产出
- **文档路径**: `docs/安防APP知识库/content/`
- **文档数量**: 17 个核心 Markdown 文件
- **覆盖范围**: 安装注册、设备管理、实时预览、录像回放、报警配置、常见问题。

## 使用指南
### 接入 ragflow
1. 登录 ragflow 控制台。
2. 创建新的 Knowledge Base。
3. 选择“上传文件”或“同步文件夹”。
4. 指向本项目生成的 `docs/安防APP知识库/content/` 目录。
5. 设置解析规则（Chunk method）为 "General" 或 "Manual"（基于 Markdown 标题）。

## 维护建议
- 建议定期根据用户反馈更新 FAQ 部分。
- 后续可添加截图（Image）以增强文档可读性，但需注意 RAG 对图片的解析能力。
