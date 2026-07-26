import requests
import os
import json
import base64

token = os.environ['VERCEL_TOKEN']

# 读取文件并 base64 编码
with open('api/proxy.py', 'rb') as f:
    proxy_b64 = base64.b64encode(f.read()).decode()

with open('requirements.txt', 'rb') as f:
    req_b64 = base64.b64encode(f.read()).decode()

with open('vercel.json', 'rb') as f:
    vercel_b64 = base64.b64encode(f.read()).decode()

payload = {
    "name": "claude-proxy",
    "files": [
        {"file": "api/proxy.py", "data": proxy_b64},
        {"file": "requirements.txt", "data": req_b64},
        {"file": "vercel.json", "data": vercel_b64}
    ],
    "projectSettings": {
        "framework": None
    },
    "target": "production"
}

r = requests.post(
    "https://api.vercel.com/v13/deployments",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json=payload
)

print(r.status_code)
print(json.dumps(r.json(), indent=2))
