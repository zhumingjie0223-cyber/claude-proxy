// Cloudflare Workers - Claude API 中转站（带 Prompt Caching）
export default {
  async fetch(request, env) {
    // CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': '*',
        }
      });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // 只转发 /v1/messages
    if (path !== '/v1/messages' && path !== '/messages') {
      return new Response('Not Found', { status: 404 });
    }

    try {
      const body = await request.json();

      // 自动注入 cache_control 到 system prompt
      if (body.system) {
        if (typeof body.system === 'string') {
          body.system = [{
            type: 'text',
            text: body.system,
            cache_control: { type: 'ephemeral' }
          }];
        } else if (Array.isArray(body.system) && body.system.length > 0) {
          // 给最后一个 system block 加 cache_control
          const last = body.system[body.system.length - 1];
          if (!last.cache_control) {
            last.cache_control = { type: 'ephemeral' };
          }
        }
      }

      // 转发到 apiclaude.cc
      const upstream = await fetch('https://apiclaude.cc/v1/messages', {
        method: 'POST',
        headers: {
          'x-api-key': env.APICLAUDE_KEY,
          'anthropic-version': '2023-06-01',
          'content-type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      const result = await upstream.json();

      return new Response(JSON.stringify(result), {
        status: upstream.status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });

    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
}
