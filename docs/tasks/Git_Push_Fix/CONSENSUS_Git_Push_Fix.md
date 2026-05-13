# 共识文档：Git 推送修复方案

## 1. 需求描述
解决 `git push` 时的 `schannel: failed to receive handshake` 错误。

## 2. 技术实现方案
### 核心变更
修改 Git 的 SSL 处理库配置。Windows Git 安装版通常包含 `schannel` (Windows 原生) 和 `openssl` (开源通用)。`openssl` 在处理代理和复杂网络环境时通常表现更佳。

### 执行命令
```bash
git config --global http.sslBackend openssl
```

### 回滚方案
如果修改后出现证书错误，可回滚：
```bash
git config --global http.sslBackend schannel
```

## 3. 验收标准
- 执行 `git push` 不再报错 `schannel` 相关错误。
- 代码成功推送到远程仓库。
