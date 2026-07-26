from http.server import BaseHTTPRequestHandler
import requests
import os
import json
import hashlib
import time

# 内存缓存
cache = {}

def make_key(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/v1/messages':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            # 生成缓存 key
            cache_key = make_key(data)
            
            # 检查缓存
            if cache_key in cache:
                cached_data, expire = cache[cache_key]
                if time.time() < expire:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    result = {"from_cache": True, **cached_data}
                    self.wfile.write(json.dumps(result).encode())
                    return
            
            # 转发到商家 API
            try:
                api_url = os.environ.get('CLAUDE_API_URL', 'https://apiclaude.cc')
                api_key = os.environ.get('CLAUDE_API_KEY')
                
                headers = {
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                
                if api_key:
                    headers["x-api-key"] = api_key
                
                response = requests.post(
                    f"{api_url}/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                
                result = response.json()
                
                # 写缓存（5 分钟）
                cache[cache_key] = (result, time.time() + 300)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                output = {"from_cache": False, **result}
                self.wfile.write(json.dumps(output).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
