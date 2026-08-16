const WebSocket = require('ws');
const http = require('http');

function quickGet(urlStr) {
  return new Promise((resolve, reject) => {
    const u = new URL(urlStr);
    const req = http.request({hostname:u.hostname,port:u.port,path:u.pathname+u.search,method:'GET'}, (res) => {
      let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve(d));
    });
    req.on('error', reject);
    req.setTimeout(3000, () => { req.destroy(); reject(new Error('timeout')); });
    req.end();
  });
}

async function main() {
  let raw, targets;
  try {
    raw = await quickGet('http://127.0.0.1:9222/json/list');
    targets = JSON.parse(raw);
  } catch (e) {
    console.log('ERROR 获取 targets:', e.message);
    process.exit(1);
  }
  
  const whale = targets.find(t => (t.title||'').includes('鲸准') || (t.url||'').includes('whaleidea'));
  if (!whale) {
    console.log('ERROR: 无鲸准页面。Targets:', JSON.stringify(targets.map(t=>({title:t.title,url:t.url,type:t.type}))));
    process.exit(1);
  }
  
  console.log('使用 target:', JSON.stringify({title:whale.title,url:whale.url,id:whale.id.substring(0,10)+'...'}));
  console.log('WebSocket URL:', whale.webSocketDebuggerUrl);
  
  const ws = new WebSocket(whale.webSocketDebuggerUrl, { handshakeTimeout: 5000 });
  let id = 0;
  const pending = new Map();
  let opened = false;
  
  function send(method, params={}) {
    const cid = ++id;
    return new Promise((res, rej) => {
      const t = setTimeout(() => rej(new Error('timeout: '+method)), 10000);
      pending.set(cid, {resolve:(r)=>{clearTimeout(t);res(r)}, reject:(e)=>{clearTimeout(t);rej(e)}});
      ws.send(JSON.stringify({id:cid, method, params}));
    });
  }
  
  ws.on('open', async () => {
    opened = true;
    console.log('✓ WebSocket opened');
    try {
      // 先检查基本状态
      const r1 = await send('Runtime.evaluate', {
        expression: `JSON.stringify({
          href: location.href,
          title: document.title,
          tables: document.querySelectorAll('table').length,
          ap: (document.querySelector('.arco-pagination-item-active')||{}).textContent,
          bodyLen: document.body ? document.body.textContent.length : 0
        })`,
        returnByValue:true
      });
      console.log('页面状态:', r1.result ? r1.result.value : JSON.stringify(r1).substring(0,300));
      
      // 如果 URL 不是 report 页，尝试看一下内容中是否有报表或登录提示
      const r2 = await send('Runtime.evaluate', {
        expression: `(function(){
          var text = document.body ? document.body.textContent.substring(0, 500) : '';
          // 查找关键元素
          var tables = document.querySelectorAll('table');
          var sample = '';
          if (tables.length) {
            var t = tables[1] || tables[0];
            var rows = t.querySelectorAll('tr');
            if (rows.length) {
              var cells = rows[0].querySelectorAll('td,th');
              var vals = [];
              for (var i=0; i<Math.min(cells.length,8); i++) vals.push(cells[i].textContent.trim().substring(0,15));
              sample = vals.join(' | ');
            }
          }
          var pages = [];
          var items = document.querySelectorAll('.arco-pagination-item');
          for (var i=0; i<items.length; i++) pages.push(items[i].textContent.trim());
          return JSON.stringify({bodyPreview:text, firstTableRow:sample, pageButtons:pages});
        })()`,
        returnByValue:true
      });
      console.log('内容预览:', r2.result ? r2.result.value : JSON.stringify(r2).substring(0,300));
      
      ws.close();
      process.exit(0);
    } catch (e) {
      console.log('执行错误:', e.message);
      ws.close();
      process.exit(1);
    }
  });
  
  ws.on('unexpected-response', (req, res) => {
    let d=''; res.on('data',c=>d+=c); res.on('end',()=>{
      console.log('HTTP错误:', res.statusCode, d.substring(0,300));
      process.exit(1);
    });
  });
  ws.on('error', e => {
    if (!opened) console.log('WS错误:', e.message);
  });
  ws.on('close', () => {
    if (!opened) {
      console.log('WS关闭但未打开');
      process.exit(1);
    }
  });
}
main().catch(e => { console.log('Main error:', e.message); process.exit(1); });
