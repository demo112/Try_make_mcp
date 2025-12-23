# 任务分解：Git 推送修复

## 任务清单

### Task 1: 切换 SSL 后端
- **输入**: 当前 Git 配置
- **操作**: 执行 `git config --global http.sslBackend openssl`
- **输出**: 配置已更新
- **验收**: `git config --global --get http.sslBackend` 返回 `openssl`

### Task 2: 验证推送
- **依赖**: Task 1
- **操作**: 执行 `git push`
- **预期**: 推送成功
- **异常处理**: 如果失败，记录新报错，进入 Task 3

### Task 3: 代理排查 (备选)
- **触发条件**: Task 2 失败且报错为连接超时
- **操作**: 
  - 取消代理: `git config --global --unset http.proxy`
  - 取消代理: `git config --global --unset https.proxy`
- **再次验证**: 执行 `git push`

### Task 4: 记录与清理
- **操作**: 更新 ACCEPTANCE 文档，删除临时分支（如果有）
