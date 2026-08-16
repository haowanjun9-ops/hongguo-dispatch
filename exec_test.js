const WebSocket = require('ws');
const http = require('http');

// 尝试通过不同端口查找MCP调用入口
async function testPort(port, path='/') {
    return new Promise((resolve) => {
        const options = {
            hostname: 'localhost',
            port: port,
            path: path,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 2000
        };
        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve({port, path, status: res.statusCode, body: data.slice(0,200)}));
        });
        req.on('error', (e) => resolve({port, path, error: e.message}));
        req.on('timeout', () => { req.destroy(); resolve({port, path, error: 'timeout'}); });
        req.write(JSON.stringify({
            jsonrpc: '2.0',
            id: 1,
            method: 'tools/call',
            params: {
                name: 'Exec',
                arguments: { code: 'text(42)' }
            }
        }));
        req.end();
    });
}

async function testMCPFormat() {
    // 测试标准MCP JSON-RPC格式
    const tests = [
        { port: 9000, path: '/' },
        { port: 9001, path: '/' },
        { port: 9002, path: '/' },
        { port: 8999, path: '/' },
        { port: 13080, path: '/' },
        { port: 19091, path: '/' },
        { port: 9000, path: '/mcp' },
        { port: 8999, path: '/mcp' },
        { port: 9002, path: '/api/v1/mcp' },
    ];
    
    for (const t of tests) {
        const r = await testPort(t.port, t.path);
        if (!r.error && r.status !== 404) {
            console.log(`✅ port=${r.port} path=${r.path} status=${r.status} body=${r.body}`);
        } else if (r.error && !r.error.includes('timeout') && !r.error.includes('ECONNREFUSED')) {
            console.log(`❓ port=${r.port} path=${r.path} error=${r.error}`);
        }
    }
    
    // 测试WebSocket MCP连接 (9000端口之前有响应)
    console.log('\n=== 测试WebSocket 9000端口 ===');
    try {
        const ws = new WebSocket('ws://localhost:9000/', {
            handshakeTimeout: 3000,
        });
        ws.on('open', () => {
            console.log('WS connected! Sending initialize...');
            ws.send(JSON.stringify({
                jsonrpc: '2.0',
                id: 1,
                method: 'initialize',
                params: {
                    protocolVersion: '2024-11-05',
                    capabilities: {},
                    clientInfo: { name: 'test-client', version: '1.0' }
                }
            }));
            setTimeout(() => {
                console.log('Sending tools/list...');
                ws.send(JSON.stringify({
                    jsonrpc: '2.0',
                    id: 2,
                    method: 'tools/list',
                    params: {}
                }));
            }, 1000);
            setTimeout(() => {
                ws.close();
                console.log('WS closed');
            }, 3000);
        });
        ws.on('message', (data) => {
            const msg = data.toString();
            console.log('WS msg:', msg.slice(0, 500));
        });
        ws.on('error', (e) => console.log('WS error:', e.message));
    } catch (e) {
        console.log('WS exception:', e.message);
    }
}

testMCPFormat();
