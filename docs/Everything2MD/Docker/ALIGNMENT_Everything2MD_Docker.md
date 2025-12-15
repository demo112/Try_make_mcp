# 对齐文档 (ALIGNMENT) - Everything2MD Docker 化

## 1. 背景与目标
### 1.1 背景
Everything2MD 依赖以下外部工具：
- **Python 3.10+**: 运行 MCP 服务器和 PyMuPDF。
- **LibreOffice**: 处理 DOCX, XLSX, PPTX 等格式。
- **Pandoc**: 处理文档格式转换 (HTML -> Markdown)。

在 Windows/Mac/Linux 上手动配置这些环境（尤其是路径）非常繁琐且容易出错。Docker 化可以将这些依赖封装在一个镜像中。

### 1.2 目标
- 构建一个包含所有依赖的 Docker 镜像。
- 提供 `docker-compose.yml` 方便一键启动。
- 确保容器内服务可以通过 MCP 协议与宿主机的 Claude Desktop 或其他客户端通信。

## 2. 现有环境分析
- **操作系统**: 宿主机为 Windows，Docker 容器通常基于 Linux (Debian/Ubuntu/Alpine)。
- **LibreOffice**: Linux 版 LibreOffice (`libreoffice-headless`) 易于安装。
- **Pandoc**: Linux 版 Pandoc 易于安装。
- **中文字体**: 容器内需要安装中文字体，否则 LibreOffice 转换中文文档会乱码。

## 3. 需求澄清 (Q&A)
- **Q**: 基础镜像是由于体积考虑选 Alpine 还是兼容性考虑选 Debian/Ubuntu？
  - **A**: LibreOffice 在 Alpine 上可能比较折腾，推荐使用 **Debian Slim** 或 **Ubuntu**，兼容性最好。
- **Q**: MCP 服务如何暴露？
  - **A**: MCP 使用 Stdio 通信时，Docker 需要以交互模式运行 (`docker run -i`) 将 stdin/stdout 映射出来。或者使用 SSE (HTTP) 模式。目前 FastMCP 默认支持 stdio。如果是 Stdio 模式，Docker 容器启动命令直接就是 MCP server。
- **Q**: 文件如何交互？
  - **A**: MCP 需要读取宿主机文件。必须使用 **Volume Mapping** (挂载卷)，将宿主机的文件目录映射到容器内。例如 `-v /c/Users:/host_files`。这会带来路径转换问题（宿主机路径 `C:\...` vs 容器路径 `/host_files/...`）。
  - **挑战**: MCP Client (Claude) 发送给 Server 的是宿主机路径。Server 在 Docker 内运行，无法直接访问宿主机路径。
  - **解决方案**: 
    1.  **路径重写**: 在 MCP Server 端拦截路径，将 `C:\` 替换为挂载点 `/mnt/c/`。
    2.  **限制范围**: 仅支持特定挂载目录下的文件。
    3.  **简化方案**: 假设用户知道映射规则，或者 Server 自动探测。鉴于这是本地工具，我们可以先实现基础的 Docker 化，路径问题由用户挂载时解决（即用户需要传入容器内的路径，或者我们做一个简单的路径映射器）。
    **决策**: 为了简化，第一版 Docker 化主要解决环境打包。关于路径，我们可以在 Server 启动时通过环境变量配置 `HOST_MOUNT_PREFIX` 和 `CONTAINER_MOUNT_POINT` 来做自动替换。

## 4. 交付物
- `Dockerfile`
- `docker-compose.yml`
- `src/apps/everything2md/path_mapper.py` (辅助路径转换)
- 更新的 `Readme.md` (使用指南)
