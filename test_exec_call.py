import json, urllib.request, sys

# Try multiple likely endpoints
endpoints = []
for port in [8999, 9000, 9001, 9002, 19090, 19091, 18080, 18081, 9090, 9091, 9092]:
    for path in ["/", "/mcp", "/jsonrpc", "/rpc", "/tool", "/tools", "/call", "/exec", "/v1", "/v1/mcp", "/api/mcp"]:
        endpoints.append((port, path))

mcp_init = {"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}},"id":1}
tools_list = {"jsonrpc":"2.0","method":"tools/list","id":2}

for port, path in endpoints:
    url = f"http://127.0.0.1:{port}{path}"
    try:
        req = urllib.request.Request(url, data=json.dumps(tools_list).encode(), headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=1) as resp:
            body = resp.read().decode()
            if body and len(body.strip()) > 0 and "not found" not in body.lower() and "route not found" not in body.lower():
                print(f"HIT port={port} path={path}: {body[:200]}")
    except Exception as e:
        pass
    sys.stdout.write(".")
    sys.stdout.flush()

print(" DONE")
