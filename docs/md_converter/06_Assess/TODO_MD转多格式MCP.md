# TODO_MD转多格式MCP

## 1. 待优化项
- [ ] **跨平台字体支持**: 增加对 Linux/MacOS 的字体自动检测逻辑，或将字体文件打包到项目中。
- [ ] **图片处理**: 支持 Markdown 中的图片标签，将其嵌入到 Word/PDF 中。
- [ ] **复杂样式增强**: 优化 HTML 到 Docx 的映射逻辑，支持 Blockquote, CodeBlock 等样式。
- [ ] **批量转换接口**: 增加 `convert_batch` 工具，支持目录级转换。

## 2. 已知缺陷
- 若 Markdown 表格格式不规范，Excel 提取可能失败或错位。
- PDF 生成在某些特殊字符下可能报错。
