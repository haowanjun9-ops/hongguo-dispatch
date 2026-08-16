/**
 * CDP 单页采集 + 翻页脚本
 * 用法: node cdp_collect.js <目标页码范围说明>
 * 此脚本:
 *  1. 连接到当前标签页
 *  2. 等待2秒
 *  3. 提取当前页数据(用用户给的script)
 *  4. 输出 Result: "ESCAPED_JSON"
 *  5. 点击下一页或上一页
 *  6. 等待3秒
 */
const http = require('http');
const WebSocket = require('ws');
const { execSync } = require('child_process');

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
    const r = await send('Runtime.evaluate', {
        expression,
        returnByValue: true,
        awaitPromise: true
    });
    if (r.exceptionDetails) {
        throw new Error(r.exceptionDetails.exception?.description || 'Evaluate error');
    }
    return r.result.value;
}

async function sleep(sec) {
    return new Promise(r => setTimeout(r, sec * 1000));
}

const EXTRACT_SCRIPT = `
try {
  var h = ['素材ID（巨量）','标题','星图任务ID','星图任务名称','抖音号昵称','抖音号','视频播放链接','下单账户名称','消耗','产品名称','数据统计日期'];
  var t = document.querySelectorAll('table'); var dt = t[1] || t[0];
  var rows = dt.querySelectorAll('tr'); var data = [];
  for (var i=0;i<rows.length;i++){
    var cells=rows[i].querySelectorAll('td,th'); if(cells.length<h.length) continue;
    var row={}; for(var j=0;j<h.length;j++){var c=cells[j]; var a=c.querySelector('a[href]'); row[h[j]]={text:c.textContent.trim(),link:a?a.href:''};}
    data.push(row);
  }
  var ap=document.querySelector('.arco-pagination-item-active');
  JSON.stringify({headers:h,currentPage:ap?ap.textContent.trim():'?',data:data,dataCount:data.length,success:true});
} catch(e){JSON.stringify({error:e.message,success:false});}
`;

const NEXT_CLICK = `(function(){var nb=document.querySelector('.arco-pagination-item-next');if(nb&&nb.className.indexOf('disabled')===-1){nb.click();return'ok';}return'done';})()`;
const PREV_CLICK = `(function(){var pb=document.querySelector('.arco-pagination-item-previous');if(pb&&pb.className.indexOf('disabled')===-1){pb.click();return'ok';}return'done';})()`;
const GET_PAGE = `(function(){var ap=document.querySelector('.arco-pagination-item-active');return ap?ap.textContent.trim():'?';})()`;

async function gotoPage(targetPage) {
    // 点击分页条中对应页码或用跳转方式
    const script = `
    (function(target) {
        var items = document.querySelectorAll('.arco-pagination-list .arco-pagination-item');
        for (var i=0; i<items.length; i++) {
            var txt = items[i].textContent.trim();
            if (txt === String(target)) {
                items[i].click();
                return 'clicked-' + txt;
            }
        }
        // 如果没找到，尝试通过跳转（输入框方式）或前后翻
        return 'not-found';
    })(` + targetPage + `)`;
    return await evaluate(script);
}

async function main() {
    const args = process.argv.slice(2);
    const action = args[0] || 'extract_next'; // extract_next, extract_prev, extract_only, goto_N
    const outputFile = args[1] || '';
    
    try {
        // 1. 获取标签页
        const targets = JSON.parse(await httpGet('http://127.0.0.1:9222/json/list'));
        const whaleTargets = targets.filter(t => t.url.includes('whaleidea') || t.url.includes('apex'));
        let target = whaleTargets.length > 0 ? whaleTargets[0] : targets[0];
        
        if (!target) {
            console.error('ERROR: 找不到标签页');
            process.exit(1);
        }

        const wsUrl = `ws://127.0.0.1:9222/devtools/page/${target.id}`;
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

        // 处理 goto_N 动作
        if (action.startsWith('goto_')) {
            const targetPage = action.substring(5);
            console.error(`跳转到第 ${targetPage} 页...`);
            const r = await gotoPage(parseInt(targetPage));
            console.error(`跳转结果: ${r}`);
            await sleep(3);
            const cp = await evaluate(GET_PAGE);
            console.error(`当前页码: ${cp}`);
            ws.close();
            process.exit(0);
        }

        // 标准流程：wait 2s -> 提取 -> 翻页 -> wait 3s
        // Step 1: wait 2s
        console.error('等待 2 秒...');
        await sleep(2);

        // Step 2: 提取数据
        console.error('提取数据...');
        const extractedJsonStr = await evaluate(EXTRACT_SCRIPT);
        // 输出结果格式：Result: "ESCAPED_JSON"
        const outer = JSON.stringify(extractedJsonStr);
        process.stdout.write(`Result: ${outer}`);
        
        // 如果指定了输出文件，同时写一份
        if (outputFile) {
            const fs = require('fs');
            fs.writeFileSync(outputFile, `Result: ${outer}\n`);
        }

        // 解析提取到的页码用于日志
        try {
            const inner = JSON.parse(extractedJsonStr);
            console.error(`  提取成功: page=${inner.currentPage}, rows=${inner.dataCount}`);
        } catch(e) {}

        if (action === 'extract_only') {
            ws.close();
            process.exit(0);
        }

        // Step 3: 翻页
        console.error(action === 'extract_prev' ? '点击上一页...' : '点击下一页...');
        const clickScript = action === 'extract_prev' ? PREV_CLICK : NEXT_CLICK;
        const clickResult = await evaluate(clickScript);
        console.error(`  翻页结果: ${clickResult}`);

        // Step 4: wait 3s
        console.error('等待 3 秒...');
        await sleep(3);

        const finalPage = await evaluate(GET_PAGE);
        console.error(`  现在在第 ${finalPage} 页`);

        ws.close();
        process.exit(0);
    } catch (e) {
        console.error('ERROR:', e.message);
        if (ws) try { ws.close(); } catch(_) {}
        process.exit(1);
    }
}

main();
