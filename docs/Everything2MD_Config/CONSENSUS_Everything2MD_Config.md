# 共识文档 (CONSENSUS) - Everything2MD 配置增强

## 1. 需求定义
### 1.1 核心功能
- **环境文件加载**: 服务启动时自动加载 `src/apps/everything2md/.env` 文件。
- **自定义路径支持**: 读取 `LIBREOFFICE_PATH` 和 `PANDOC_PATH` 环境变量。
- **路径验证**: 
  - 如果环境变量已设置且路径有效，直接使用。
  - 如果环境变量已设置但路径无效，**抛出异常并终止启动**（Explicit is better than implicit）。
  - 如果环境变量未设置，回退到原有查找逻辑（系统 PATH -> 默认路径）。

### 1.2 验收标准
- [ ] 在 `.env` 中设置有效路径，服务能正常调用对应工具。
- [ ] 在 `.env` 中设置无效路径，服务启动失败并报错。
- [ ] 不存在 `.env` 时，服务行为与之前一致（自动查找）。

## 2. 技术实现方案
### 2.1 依赖变更
- 添加 `python-dotenv` 到 `requirements.txt`。

### 2.2 代码变更 (`server.py`)
- 引入 `dotenv.load_dotenv`。
- 修改 `find_executable` 函数或其调用方，优先检查 `os.getenv`。
- 增加 `validate_custom_path` 逻辑。

### 2.3 配置文件
- 新增 `.env.example` 模板文件，包含注释说明。

## 3. 边界条件
- 仅支持绝对路径配置。
- Windows 下路径分隔符需注意转义或使用正斜杠，但在 `.env` 中通常不需要额外转义。
