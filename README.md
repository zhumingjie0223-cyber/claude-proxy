# Claude API 中转站

部署到 Vercel，缓存相同请求 5 分钟

## 部署

```bash
cd /var/minis/workspace/claude-proxy
vercel --prod
```

部署后在 Vercel Dashboard 设置环境变量：
- `CLAUDE_API_KEY` = 你的 Claude API Key

## 使用

```bash
curl -X POST https://你的域名.vercel.app/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

缓存命中时返回 `"from_cache": true`
