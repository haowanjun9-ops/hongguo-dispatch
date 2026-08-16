#!/usr/bin/env python3
"""Connect to browser via CDP and extract star report data."""
import json
import websocket
import urllib.request
import time

CDP_HTTP = "http://127.0.0.1:9222"
SAVE_PATH = "/workspace/star_report_data.json"

def list_pages():
    with urllib.request.urlopen(CDP_HTTP + "/json") as r:
        pages = json.loads(r.read())
    return pages

def get_data_via_cdp():
    pages = list_pages()
    target_ws = None
    for p in pages:
        if "apex.whaleidea.cn" in p.get("url", ""):
            target_ws = p.get("webSocketDebuggerUrl")
            print(f"Found page: {p.get('url')}")
            break
    if not target_ws:
        target_ws = pages[0]["webSocketDebuggerUrl"]
        print(f"Using first page: {pages[0].get('url')}")

    ws = websocket.create_connection(
        target_ws,
        timeout=60,
    )
    msg_id = [0]
    def send(method, params=None):
        msg_id[0] += 1
        payload = {"id": msg_id[0], "method": method}
        if params: payload["params"] = params
        ws.send(json.dumps(payload))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == msg_id[0]:
                return resp

    r = send("Runtime.evaluate", {
        "expression": "JSON.stringify({ count: window.__allData?.length, total: window.__allData?.[0]?.data?.total, hasData: !!window.__allData })",
        "returnByValue": True
    })
    print("Check:", r.get("result", {}).get("result", {}).get("value"))

    print("Extracting data...")
    r = send("Runtime.evaluate", {
        "expression": "JSON.stringify(window.__allData.map(d => ({ url: d.url, items: d.data && d.data.items })))",
        "returnByValue": True
    })
    value = r.get("result", {}).get("result", {}).get("value")
    if not value:
        print("No value returned")
        return

    print(f"Got data size: {len(value)} bytes")
    data = json.loads(value)
    print(f"Pages captured: {len(data)}")

    all_items = []
    seen_urls = set()
    for d in data:
        if d.get("url") in seen_urls:
            continue
        seen_urls.add(d["url"])
        if d.get("items"):
            all_items.extend(d["items"])

    print(f"Total items: {len(all_items)}")

    output = {
        "total_cost": "117042.2701",
        "total": 1020,
        "items": all_items
    }
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)
    print(f"Saved to {SAVE_PATH}")

    ws.close()

if __name__ == "__main__":
    get_data_via_cdp()
