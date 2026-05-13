/**
 * Try_make_mcp — Cloudflare Worker MCP Server (Remote / Streamable HTTP)
 * 
 * 支持 streamable-http 和 sse 两种传输方式。
 * 内置 Freemium API Key 验证（Stripe Checkout 集成就绪）。
 * 
 * 部署步骤（Cooper）:
 * 1. 注册 Cloudflare 账号: https://dash.cloudflare.com/sign-up
 * 2. 安装 wrangler: npm install -g wrangler
 * 3. 登录: wrangler login
 * 4. cd /tmp/try_make_mcp/cloudflare-worker
 * 5. wrangler deploy
 * 6. 记下输出的 URL (如 https://try-make-mcp.your-subdomain.workers.dev)
 * 
 * 变现模式（Stripe Checkout）:
 * 1. 注册 Stripe: https://dashboard.stripe.com/register
 * 2. 创建 Checkout Session → 用户付款后获得 API key
 * 3. 在 wrangler.toml 或 Cloudflare Dashboard 设置环境变量:
 *    - STRIPE_SECRET_KEY: sk_live_...
 *    - STRIPE_PRICE_ID: price_... (产品价格ID)
 *    - VALID_API_KEYS: "key1,key2,key3" (已验证的API key列表)
 * 4. 部署: wrangler deploy
 * 
 * 免费层: 无需 API key，每工具每 IP 10次/天
 * 付费层: 传入 api_key 参数，无限调用
 */

// ─── Freemium Configuration ───────────────────────────────────
// 免费 tier 每 IP 每天 10 次调用
const FREE_TIER_DAILY_LIMIT = 10;

// 需要付费的工具（免费层限流，付费层无限）
// 'all' = 所有工具都限流, [] = 所有工具都免费
const PAID_TOOLS = ['all'];

// 你的 Stripe Checkout URL（Cooper 注册 Stripe 后替换）
// 示例: https://buy.stripe.com/xxx
const STRIPE_CHECKOUT_URL = 'https://buy.stripe.com/YOUR_LINK_HERE';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, MCP-Protocol-Version',
      'Access-Control-Expose-Headers': 'Mcp-Session-Id',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    // Stripe Checkout redirect
    if (url.pathname === '/subscribe') {
      return Response.redirect(STRIPE_CHECKOUT_URL, 302);
    }

    // Pricing info page
    if (url.pathname === '/pricing') {
      return new Response(JSON.stringify({
        name: 'try-make-mcp',
        pricing: {
          free: {
            price: '$0',
            limits: `${FREE_TIER_DAILY_LIMIT} tool calls per day per IP`,
            auth: 'None required',
          },
          pro: {
            price: '$0.01/call (pay-as-you-go)',
            limits: 'Unlimited',
            auth: 'Stripe API key via tool parameter',
            subscribe: '/subscribe',
          },
        },
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }

    // MCP endpoint (POST /mcp)
    if (url.pathname === '/mcp' && request.method === 'POST') {
      return handleMCPRequest(request, corsHeaders, env);
    }

    // SSE endpoint (GET /sse) — legacy transport
    if (url.pathname === '/sse' && request.method === 'GET') {
      return handleSSERequest(corsHeaders);
    }

    // Health check + info
    if (url.pathname === '/' || url.pathname === '/health') {
      return new Response(JSON.stringify({
        name: 'try-make-mcp',
        version: '2.0.0',
        description: 'MCP Factory — Multi-tool MCP server with freemium API key auth',
        transport: ['streamable-http', 'sse'],
        endpoints: {
          mcp: '/mcp',
          sse: '/sse',
          subscribe: '/subscribe',
          pricing: '/pricing',
        },
        tools: getToolList(),
        freemium: {
          free_tier_limit: FREE_TIER_DAILY_LIMIT,
          auth_mode: 'api_key_parameter',
        },
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }

    return new Response('Not Found', { status: 404, headers: corsHeaders });
  },
};

// ─── Tool Definitions ────────────────────────────────────────────

function getToolList() {
  return [
    {
      name: 'markdown_to_html',
      description: 'Convert Markdown text to HTML. Useful for content formatting.',
      inputSchema: {
        type: 'object',
        properties: {
          markdown: { type: 'string', description: 'The Markdown text to convert' },
        },
        required: ['markdown'],
      },
    },
    {
      name: 'generate_uuid',
      description: 'Generate a random UUID v4 string.',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'timestamp',
      description: 'Get the current UTC timestamp and formatted date string.',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'json_format',
      description: 'Validate and pretty-print JSON data.',
      inputSchema: {
        type: 'object',
        properties: {
          data: { type: 'string', description: 'JSON string to validate and format' },
        },
        required: ['data'],
      },
    },
    {
      name: 'text_analysis',
      description: 'Analyze text: count characters, words, sentences, and estimate reading time.',
      inputSchema: {
        type: 'object',
        properties: {
          text: { type: 'string', description: 'The text to analyze' },
        },
        required: ['text'],
      },
    },
    {
      name: 'base64_encode',
      description: 'Encode text to base64.',
      inputSchema: {
        type: 'object',
        properties: {
          text: { type: 'string', description: 'Text to encode' },
        },
        required: ['text'],
      },
    },
    {
      name: 'base64_decode',
      description: 'Decode base64 to text.',
      inputSchema: {
        type: 'object',
        properties: {
          encoded: { type: 'string', description: 'Base64 string to decode' },
        },
        required: ['encoded'],
      },
    },
    {
      name: 'url_encode',
      description: 'URL-encode a string.',
      inputSchema: {
        type: 'object',
        properties: {
          text: { type: 'string', description: 'Text to URL-encode' },
        },
        required: ['text'],
      },
    },
  ];
}

// ─── Streamable HTTP Handler ─────────────────────────────────────

// ─── API Key Validation ────────────────────────────────────────

/**
 * 验证 API key。模式与 BGPT MCP 一致：
 * - api_key 作为 tool call 参数传入
 * - 如果提供了有效 key → 付费层，无限调用
 * - 如果没有 key → 免费层，基于 IP 的限流
 */
function validateApiKey(apiKey, env) {
  if (!apiKey) return { valid: false, tier: 'free' };
  
  // 检查环境变量中的有效 key 列表
  // 格式: "sk_live_xxx,sk_live_yyy,sk_live_zzz"
  const validKeys = env?.VALID_API_KEYS || '';
  const keyList = validKeys.split(',').map(k => k.trim()).filter(k => k.length > 0);
  
  if (keyList.includes(apiKey)) {
    return { valid: true, tier: 'pro' };
  }
  
  // 可选: 通过 Stripe API 验证（Cooper 设置 STRIPE_SECRET_KEY 后启用）
  // const stripeKey = env?.STRIPE_SECRET_KEY;
  // if (stripeKey) { /* call Stripe API to verify */ }
  
  return { valid: false, tier: 'free' };
}

/**
 * 检查免费层限流（基于 CF-KV 或简单的全局计数器）
 * 在 Cloudflare Workers 免费套餐中，用 KV 做计数最可靠。
 * 这里用内存计数（单实例），生产环境建议用 KV:
 * 
 *   const count = await env.USAGE_KV.get(ipKey) || 0;
 *   if (count >= FREE_TIER_DAILY_LIMIT) → deny
 *   await env.USAGE_KV.put(ipKey, count + 1, { expirationTtl: 86400 });
 */
function checkFreeTierLimit(ip) {
  // 生产环境: 用 Cloudflare KV
  // 开发环境: 简单的内存计数（每次 Worker 冷启动重置）
  if (!globalThis.__freeTierUsage) globalThis.__freeTierUsage = {};
  const key = `ip:${ip}:${new Date().toISOString().split('T')[0]}`;
  const count = globalThis.__freeTierUsage[key] || 0;
  globalThis.__freeTierUsage[key] = count + 1;
  return count < FREE_TIER_DAILY_LIMIT;
}

// ─── Streamable HTTP Handler ─────────────────────────────────────

async function handleMCPRequest(request, corsHeaders, env) {
  try {
    const body = await request.json();
    const { method, params, id } = body;
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';

    let result;
    let isError = false;

    switch (method) {
      case 'initialize':
        result = {
          protocolVersion: '2025-03-26',
          capabilities: {
            tools: { listChanged: false },
          },
          serverInfo: {
            name: 'try-make-mcp',
            version: '2.0.0',
          },
        };
        break;

      case 'notifications/initialized':
        // No response needed for notifications
        return new Response(null, { status: 204, headers: corsHeaders });

      case 'tools/list':
        result = { tools: getToolList() };
        break;

      case 'tools/call': {
        const toolName = params?.name;
        const args = params?.arguments || {};
        const apiKey = args.api_key;  // BGPT 模式: api_key 作为工具参数

        // 检查此工具是否需要付费验证
        const needsAuth = PAID_TOOLS.includes('all') || PAID_TOOLS.includes(toolName);
        
        if (needsAuth) {
          const auth = validateApiKey(apiKey, env);
          
          if (auth.tier === 'pro') {
            // ✅ 付费用户: 直接执行
            result = await handleToolCall(params);
            if (result.isError) {
              isError = true;
              result = result.content;
            } else {
              result = result.content;
            }
          } else {
            // 免费层: 检查限流
            const allowed = checkFreeTierLimit(clientIP);
            if (allowed) {
              result = await handleToolCall(params);
              if (result.isError) {
                isError = true;
                result = result.content;
              } else {
                result = result.content;
              }
            } else {
              // ❌ 免费额度用完: 返回 MCP Payment Required error
              // 参考: MCP GitHub Discussion #2436 提议的 error code -32042
              isError = true;
              result = {
                code: -32042,
                message: 'Payment required: Free tier daily limit reached',
                data: {
                  limit: FREE_TIER_DAILY_LIMIT,
                  subscribe: '/subscribe',
                  pricing: '/pricing',
                  tip: 'Add an api_key parameter to your tool call for unlimited access. Get one at /subscribe',
                },
              };
            }
          }
        } else {
          // 非付费工具: 直接执行
          result = await handleToolCall(params);
          if (result.isError) {
            isError = true;
            result = result.content;
          } else {
            result = result.content;
          }
        }
        break;
      }

      case 'ping':
        result = {};
        break;

      default:
        isError = true;
        result = {
          code: -32601,
          message: `Method not found: ${method}`,
        };
    }

    const response = {
      jsonrpc: '2.0',
      id: id ?? null,
      ...(isError ? { error: result } : { result }),
    };

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders,
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({
      jsonrpc: '2.0',
      id: null,
      error: {
        code: -32700,
        message: 'Parse error: ' + err.message,
      },
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  }
}

// ─── Tool Implementation ─────────────────────────────────────────

async function handleToolCall(params) {
  const { name, arguments: args } = params;

  try {
    switch (name) {
      case 'markdown_to_html':
        return {
          content: [{
            type: 'text',
            text: markdownToHTML(args.markdown || ''),
          }],
        };

      case 'generate_uuid':
        return {
          content: [{
            type: 'text',
            text: crypto.randomUUID(),
          }],
        };

      case 'timestamp':
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              iso: new Date().toISOString(),
              unix: Date.now(),
              date: new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZoneName: 'short',
              }),
            }, null, 2),
          }],
        };

      case 'json_format':
        return {
          content: [{
            type: 'text',
            text: JSON.stringify(JSON.parse(args.data), null, 2),
          }],
        };

      case 'text_analysis':
        return {
          content: [{
            type: 'text',
            text: analyzeText(args.text || ''),
          }],
        };

      case 'base64_encode':
        return {
          content: [{
            type: 'text',
            text: btoa(args.text || ''),
          }],
        };

      case 'base64_decode':
        return {
          content: [{
            type: 'text',
            text: atob(args.encoded || ''),
          }],
        };

      case 'url_encode':
        return {
          content: [{
            type: 'text',
            text: encodeURIComponent(args.text || ''),
          }],
        };

      default:
        return {
          isError: true,
          content: [{
            type: 'text',
            text: `Unknown tool: ${name}`,
          }],
        };
    }
  } catch (err) {
    return {
      isError: true,
      content: [{
        type: 'text',
        text: `Tool error: ${err.message}`,
      }],
    };
  }
}

// ─── Utility Functions ───────────────────────────────────────────

function markdownToHTML(md) {
  let html = md
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold and italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');

  return `<p>${html}</p>`;
}

function analyzeText(text) {
  const chars = text.length;
  const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
  const readingTime = Math.max(1, Math.ceil(words / 200));

  return JSON.stringify({
    characters: chars,
    words,
    sentences,
    averageWordLength: words > 0 ? (chars / words).toFixed(1) : 0,
    estimatedReadingTime: `${readingTime} min`,
  }, null, 2);
}

// ─── SSE Handler (Legacy) ────────────────────────────────────────

function handleSSERequest(corsHeaders) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      // Send initial MCP endpoint info
      const initData = JSON.stringify({
        jsonrpc: '2.0',
        id: null,
        result: {
          protocolVersion: '2025-03-26',
          capabilities: { tools: { listChanged: false } },
          serverInfo: { name: 'try-make-mcp', version: '1.0.0' },
        },
      });

      controller.enqueue(encoder.encode(`data: ${initData}\n\n`));

      // Keep alive
      const keepAlive = setInterval(() => {
        controller.enqueue(encoder.encode(': keepalive\n\n'));
      }, 30000);

      // Clean up on close
      // Note: In production, handle message events from the client
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      ...corsHeaders,
    },
  });
}
