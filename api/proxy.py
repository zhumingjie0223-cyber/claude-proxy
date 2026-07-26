from flask import Flask, request, jsonify
import anthropic
import os
import hashlib
import json
import time

app = Flask(__name__)

# 内存缓存
cache = {}

def make_key(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

@app.route('/v1/messages', methods=['POST'])
def proxy():
    data = request.get_json()
    
    # 生成缓存 key
    cache_key = make_key(data)
    
    # 检查缓存
    if cache_key in cache:
        cached_data, expire = cache[cache_key]
        if time.time() < expire:
            return jsonify({"from_cache": True, **cached_data})
    
    # 调用 Claude
    try:
        client = anthropic.Anthropic(api_key=os.environ.get('CLAUDE_API_KEY'))
        
        response = client.messages.create(
            model=data.get('model', 'claude-3-5-sonnet-20241022'),
            max_tokens=data.get('max_tokens', 4096),
            messages=data.get('messages', []),
            system=data.get('system'),
            temperature=data.get('temperature', 1.0)
        )
        
        result = {
            "id": response.id,
            "type": response.type,
            "role": response.role,
            "content": [{"type": c.type, "text": c.text} for c in response.content],
            "model": response.model,
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
        
        # 写缓存（5 分钟）
        cache[cache_key] = (result, time.time() + 300)
        
        return jsonify({"from_cache": False, **result})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run()
