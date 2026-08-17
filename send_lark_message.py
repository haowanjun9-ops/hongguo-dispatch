#!/usr/bin/env python3
"""Send Feishu message via lark-cli"""
import subprocess
import sys

CHAT_ID = "oc_74cf357efbbda7b35af5078abcb29bdb"
MD_FILE = "/workspace/star_report_message_2026-08-17_00-12.txt"

with open(MD_FILE, "r", encoding="utf-8") as f:
    markdown_content = f.read()

print(f"Markdown content length: {len(markdown_content)} chars")
print("---Content preview---")
print(markdown_content[:300])
print("---------------------")

# First check auth status
print("\n=== Checking lark-cli auth status ===")
try:
    auth_check = subprocess.run(
        ["lark-cli", "auth", "status"],
        capture_output=True, text=True, timeout=15
    )
    print("auth status stdout:", auth_check.stdout[:500])
    print("auth status stderr:", auth_check.stderr[:500])
except Exception as e:
    print(f"Auth check error: {e}")

# Send message via lark-cli using --markdown
print("\n=== Sending Feishu message ===")
cmd = [
    "lark-cli", "im", "+messages-send",
    "--as", "user",
    "--chat-id", CHAT_ID,
    "--markdown", markdown_content
]

try:
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=30
    )
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print(f"stdout: {result.stdout[:2000]}")
    if result.stderr:
        print(f"stderr: {result.stderr[:2000]}")
    sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print("ERROR: Command timed out after 30s")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
