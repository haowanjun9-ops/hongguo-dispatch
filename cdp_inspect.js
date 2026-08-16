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

async function evaluate(expression) {
    const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'Eval error');
    return r.result.value;
}

async function main() {
    const targets = JSON.parse(await httpGet('http://127.0.0.1:9222/json/list'));
    const target = targets.find(t => t.url.includes('whaleidea') || t.url.includes('apex')) || targets[0];
    ws = new WebSocket(`ws://127.0.0.1:9222/devtools/page/${target.id}`);
    await new Promise((r, j) => { ws.on('open', r); ws.on('error', j); });
    ws.on('message', d => {
        const m = JSON.parse(d.toString());
        if (m.id && pending.has(m.id)) { const {resolve, reject} = pending.get(m.id); pending.delete(m.id); m.error?reject(new Error(m.error.message)):resolve(m.result); }
    });

    const info = await evaluate(`
    (function(){
        var ap = document.querySelector('.arco-pagination-item-active');
        var allItems = document.querySelectorAll('[class*="pagination"]');
        var pageItems = document.querySelectorAll('.arco-pagination-item');
        var prevBtn = document.querySelector('.arco-pagination-item-previous');
        var nextBtn = document.querySelector('.arco-pagination-item-next');
        var result = {
            activePage: ap?ap.textContent.trim():'?',
            activeHTML: ap?ap.outerHTML:'',
            prevClass: prevBtn?prevBtn.className:'',
            nextClass: nextBtn?nextBtn.className:'',
            prevDisabled: prevBtn?(prevBtn.className.indexOf('disabled')>=0):'na',
            nextDisabled: nextBtn?(nextBtn.className.indexOf('disabled')>=0):'na',
            paginationClasses: Array.from(allItems).map(e=>e.className).filter(c=>c).slice(0,10),
            pageItemList: Array.from(pageItems).map(e=>({text:e.textContent.trim(),cls:e.className})).slice(0,20)
        };
        return JSON.stringify(result,null,2);
    })()
    `);
    console.log(info);
    ws.close();
}
main().catch(e=>{console.error(e);process.exit(1);});
