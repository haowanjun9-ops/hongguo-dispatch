#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 lark-cli 发送飞书消息，避免 shell 转义问题
"""
import subprocess
import sys
import os
import json

CHAT_ID = "oc_74cf357efbbda7b35af5078abcb29bdb"
MD_FILE = "/workspace/feishu_message.md"

def main():
    # 读取 markdown 内容
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print(f"Markdown length: {len(md_content)} chars")
    print("--- Preview start ---")
    print(md_content[:500])
    print("--- Preview end ---")
    print()
    
    # 构造命令
    # 使用 lark-cli im +messages-send --as user --chat-id <id> --markdown "<content>"
    cmd = [
        "lark-cli", "im", "+messages-send",
        "--as", "user",
        "--chat-id", CHAT_ID,
        "--markdown", md_content
    ]
    
    env = os.environ.copy()
    env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"] = "1"
    env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"] = "1"
    
    print(f"Executing: lark-cli im +messages-send --as user --chat-id {CHAT_ID} --markdown ...")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=60
        )
        
        print("STDOUT:")
        print(result.stdout)
        print()
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            print()
        
        print(f"Exit code: {result.returncode}")
        
        # 解析返回 JSON
        try:
            if result.stdout.strip():
                data = json.loads(result.stdout)
                if data.get("ok"):
                    print("[SUCCESS] Message sent successfully!")
                    message_id = data.get("data", {}).get("message_id", "unknown")
                    print(f"  Message ID: {message_id}")
                    sys.exit(0)
                else:
                    print(f"[FAILED] API error: {data.get('error', {}).get('message')}")
                    print(f"  Full error: {json.dumps(data.get('error', {}), ensure_ascii=False)}")
                    sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[WARNING] Could not parse JSON output: {e}")
        
        if result.returncode == 0:
            print("[SUCCESS] (exit code 0, but could not parse JSON)")
            sys.exit(0)
        else:
            print("[FAILED] Non-zero exit code")
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Command timed out after 60s")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
