# 共识文档 (CONSENSUS) - Everything2MD Docker 化

## 1. 需求定义
### 1.1 核心功能
- **全栈镜像**: 包含 Python, LibreOffice, Pandoc, 中文字体。
- **路径映射支持**: 解决宿主机路径 (Windows) 与容器路径 (Linux) 不一致的问题。
- **Stdio 通信**: 支持通过 `docker run -i` 与宿主机 MCP Client 通信。

### 1.2 验收标准
- [ ] Docker 镜像构建成功，体积合理 (< 2GB)。
- [ ] 容器内能够成功转换 DOCX, PDF 等文件。
- [ ] 中文文档转换无乱码（字体支持）。
- [ ] 路径映射机制工作正常（宿主机传入 `C:\Doc\test.docx`，容器内自动识别为 `/mnt/c/Doc/test.docx`）。

## 2. 技术实现方案
### 2.1 Dockerfile 设计
- **Base Image**: `python:3.10-slim-bullseye` (Debian 11)
- **System Deps**: `libreoffice`, `pandoc`, `fonts-noto-cjk`, `tini` (作为 init 进程)
- **Python Deps**: `pip install -r requirements.txt`

### 2.2 路径映射逻辑 (`path_mapper.py`)
- 在 `server.py` 中引入路径处理逻辑。
- 环境变量:
  - `HOST_ROOT`: 宿主机挂载根路径 (e.g., `C:\`)
  - `CONTAINER_ROOT`: 容器内挂载点 (e.g., `/mnt/c/`)
- 逻辑: 当收到 `source_path` 时，如果以 `HOST_ROOT` 开头，替换为 `CONTAINER_ROOT`。

### 2.3 启动脚本
- `entrypoint.sh`: 检查环境，启动 MCP Server。

## 3. 风险与约束
- **性能**: Docker 在 Windows 上运行（WSL2）会有一定的 IO 性能损耗，但对于文档转换可接受。
- **权限**: 容器内以 root 运行还是非 root？建议默认 root 以避免读写宿主机映射文件的权限问题（虽然不安全，但对于本地工具最方便）。
