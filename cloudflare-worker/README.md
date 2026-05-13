# Try_make_mcp — Cloudflare Worker MCP Server

MCP Factory 的 Cloudflare Workers 远程端点部署包。

## 部署步骤（Cooper，约5分钟）

### 1. 注册 Cloudflare（免费，无需信用卡）
- 访问 https://dash.cloudflare.com/sign-up
- 用 GitHub 登录最快

### 2. 安装 Wrangler CLI
```bash
npm install -g wrangler
```

### 3. 登录 Cloudflare
```bash
wrangler login
# 浏览器会自动打开授权页面
```

### 4. 部署
```bash
cd /tmp/try_make_mcp/cloudflare-worker
wrangler deploy
```

### 5. 记录 URL
部署成功后会输出类似：
```
Published try-make-mcp (1.37 sec)
  https://try-make-mcp.your-subdomain.workers.dev
```

### 6. 更新 server.json
将 `remotes` 中的 URL 替换为实际部署地址：
```json
{
  "remotes": [
    {
      "url": "https://try-make-mcp.your-subdomain.workers.dev/mcp",
      "transport": "streamable-http"
    }
  ]
}
```

### 7. 发布到 MCP Registry
```bash
mcp-publisher publish
```

## 费用

**Cloudflare Workers 免费套餐：**
- 100,000 请求/天
- 10ms CPU 时间/请求
- 无需信用卡

**对于 MCP 开发来说完全够用。**

## 包含的工具

| 工具名 | 描述 |
|--------|------|
| markdown_to_html | Markdown → HTML 转换 |
| generate_uuid | UUID v4 生成 |
| timestamp | UTC 时间戳 + 格式化日期 |
| json_format | JSON 验证和美化 |
| text_analysis | 文本统计（字数/句数/阅读时间） |
| base64_encode | Base64 编码 |
| base64_decode | Base64 解码 |
| url_encode | URL 编码 |

## 验证

部署后访问 `https://your-worker.workers.dev/health` 查看状态。

## 支持

- streamable-http (推荐): POST /mcp
- sse (旧版兼容): GET /sse
