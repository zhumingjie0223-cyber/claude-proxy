from flask import Flask, request, jsonify
import requests
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
    
    # 转发到商家 API
    try:
        api_url = os.environ.get('CLAUDE_API_URL', 'https://apiclaude.cc')
        api_key = os.environ.get('CLAUDE_API_KEY')
        
        response = requests.post(
            f"{api_url}/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json=data,
            timeout=60
        )
        
        result = response.json()
        
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
