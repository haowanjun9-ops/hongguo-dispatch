/**
 * 测试CDP连接：尝试导航到报表页面，检查是否已登录
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

async function navigate(url) {
    await send('Page.navigate', { url });
}

async function sleep(sec) {
    return new Promise(r => setTimeout(r, sec * 1000));
}

async function main() {
    try {
        const targets = JSON.parse(await httpGet('http://127.0.0.1:9222/json/list'));
        console.log('找到标签页:', targets.length);
        targets.forEach((t, i) => console.log(`  [${i}] ${t.title.slice(0,60)} | ${t.url.slice(0,80)}`));

        const target = targets[0];
        const wsUrl = `ws://127.0.0.1:9222/devtools/page/${target.id}`;
        console.log('\n连接到:', wsUrl);
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

        await send('Page.enable');
        await send('Runtime.enable');

        // 先检查当前URL
        const curUrl = await evaluate('location.href');
        console.log('\n当前URL:', curUrl);

        // 尝试导航到报表页面
        const reportUrl = 'https://apex.whaleidea.cn/star/report';
        console.log('导航到:', reportUrl);
        await navigate(reportUrl);
        await sleep(5);

        const newUrl = await evaluate('location.href');
        const title = await evaluate('document.title');
        console.log('导航后URL:', newUrl);
        console.log('页面标题:', title);

        // 检查是否有表格或分页元素
        const hasTable = await evaluate('document.querySelectorAll("table").length');
        const hasPagination = await evaluate('document.querySelector(".arco-pagination, .pagination")?.className || "none"');
        const curPage = await evaluate('(function(){var ap=document.querySelector(".arco-pagination-item-active");return ap?ap.textContent.trim():"?";})()');
        console.log('表格数量:', hasTable);
        console.log('分页元素:', hasPagination);
        console.log('当前页码:', curPage);

        // 如果还在登录页，尝试打印登录相关的信息
        if (newUrl.includes('login')) {
            console.log('\n仍在登录页面，检查登录表单...');
            const loginForm = await evaluate('JSON.stringify({forms: document.forms.length, inputs: document.querySelectorAll("input").length, hasLoginBtn: !!document.querySelector(\'button[type="submit"], .login-btn, [class*="login"]\')})');
            console.log('登录表单信息:', loginForm);
            // 获取当前cookies
            await send('Network.enable');
            const cookies = await send('Network.getCookies', { urls: [newUrl] });
            console.log('Cookies数量:', cookies.cookies?.length || 0);
            cookies.cookies?.forEach(c => console.log(`  ${c.name}=${c.value.slice(0,30)}... domain=${c.domain}`));
        } else {
            console.log('\n成功进入报表页面！尝试提取第1页数据...');
            const data = await evaluate(`
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
`);
            console.log('提取结果前500字符:', data.slice(0, 500));
        }

        ws.close();
    } catch (e) {
        console.error('ERROR:', e.message);
        console.error(e.stack);
        if (ws) try { ws.close(); } catch(_) {}
        process.exit(1);
    }
}

main();
