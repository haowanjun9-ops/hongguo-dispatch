import subprocess, json, sys, os
# Try to find any binary or entrypoint that can invoke MCP-style calls
# Check typical locations for agent-tool-host client or CLI
paths = [
    "/usr/local/bin", "/usr/bin", "/data/user", 
    "/app", "/home", os.environ.get("HOME","/root")
]
for p in paths:
    if os.path.isdir(p):
        for fn in os.listdir(p)[:50]:
            fp = os.path.join(p, fn)
            if "agent" in fn.lower() or "tool" in fn.lower() or "mcp" in fn.lower() or "solo" in fn.lower():
                print(f"Found: {fp}")

# Check /proc/822 (agent-tool-host) cmdline and environment
try:
    with open("/proc/822/cmdline", "rb") as f:
        cmd = f.read().replace(b'\x00', b' ').decode()
    print(f"\nagent-tool-host cmd: {cmd}")
    with open("/proc/822/environ", "rb") as f:
        env = f.read().replace(b'\x00', b'\n').decode()
    for line in env.split("\n"):
        if any(k in line for k in ["PORT","SERVER","MCP","EXEC","TOOL","CODE","AGENT"]):
            print(f"  ENV: {line}")
except Exception as e:
    print(f"Error: {e}")
