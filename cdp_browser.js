/**
 * CDP 浏览器自动化脚本
 * 通过 Chrome DevTools Protocol 直接连接浏览器
 */
const http = require('http');
const WebSocket = require('ws');

function httpGet(url) {
    return new Promise((resolve, reject) => {
        http.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

let ws = null;
let msgId = 0;
const pending = new Map();

function send(method, params = {}) {
    return new Promise((resolve, reject) => {
        const id = ++msgId;
        pending.set(id, { resolve, reject });
        ws.send(JSON.stringify({ id, method, params }));
    });
}

async function main() {
    try {
        // 1. 获取可用的页面标签
        const targets = JSON.parse(await httpGet('http://127.0.0.1:9222/json/list'));
        console.log('当前标签页:', targets.map(t => ({ id: t.id, title: t.title, url: t.url })));

        // 2. 找到鲸准报表页面或使用第一个页面
        let target = targets.find(t => t.url.includes('whaleidea') || t.url.includes('apex'));
        let targetId;
        if (target) {
            console.log('找到鲸准报表页面:', target.url);
            targetId = target.id;
        } else {
            console.log('未找到鲸准页面，使用第一个标签页并导航...');
            target = targets[0];
            targetId = target.id;
        }

        // 3. 连接 WebSocket
        const wsUrl = `ws://127.0.0.1:9222/devtools/page/${targetId}`;
        console.log('连接到:', wsUrl);
        ws = new WebSocket(wsUrl);

        await new Promise((resolve, reject) => {
            ws.on('open', resolve);
            ws.on('error', reject);
        });

        ws.on('message', (data) => {
            const msg = JSON.parse(data.toString());
            if (msg.id && pending.has(msg.id)) {
                const { resolve, reject } = pending.get(msg.id);
                pending.delete(msg.id);
                if (msg.error) reject(new Error(msg.error.message));
                else resolve(msg.result);
            }
        });

        // 4. 如果不是鲸准页面，导航过去
        if (!target.url.includes('whaleidea')) {
            console.log('导航到 https://apex.whaleidea.cn/star/report ...');
            await send('Page.enable');
            await send('Page.navigate', { url: 'https://apex.whaleidea.cn/star/report' });
            await new Promise(r => setTimeout(r, 5000));
            console.log('导航完成，等待页面加载...');
        }

        // 5. 获取当前页码
        const pageResult = await send('Runtime.evaluate', {
            expression: `(function(){
                var ap=document.querySelector('.arco-pagination-item-active');
                var url=location.href;
                var title=document.title;
                return JSON.stringify({currentPage:ap?ap.textContent.trim():'?',url:url,title:title,hasTable:!!document.querySelectorAll('table').length});
            })()`,
            returnByValue: true
        });

        console.log('页面状态:', pageResult.result.value);

    } catch (e) {
        console.error('ERROR:', e.message);
        process.exit(1);
    } finally {
        if (ws) ws.close();
        process.exit(0);
    }
}

main();
