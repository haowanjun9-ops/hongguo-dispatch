const WebSocket = require('ws');
const http = require('http');

function httpGetJson(path) {
  return new Promise((resolve, reject) => {
    const req = http.request({hostname:'127.0.0.1',port:9222,path,method:'GET',headers:{'Host':'127.0.0.1'}}, (res) => {
      let d=''; res.on('data',c=>d+=c); res.on('end',()=>{try{resolve(JSON.parse(d))}catch(e){reject(e)}});
    });
    req.on('error', reject);
    req.end();
  });
}

function connectWS(url) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url);
    let msgId = 0;
    const pending = new Map();
    const listeners = new Map();
    
    function send(method, params={}) {
      const id = ++msgId;
      return new Promise((res, rej) => {
        pending.set(id, { res, rej, t: setTimeout(()=>rej(new Error('timeout: '+method)), 15000) });
        ws.send(JSON.stringify({id, method, params}));
      });
    }
    
    ws.on('open', () => {
      resolve({
        ws,
        send,
        on: (evt, cb) => listeners.set(evt, cb),
        close: () => ws.close()
      });
    });
    ws.on('message', (data) => {
      const msg = JSON.parse(data.toString());
      if (msg.id && pending.has(msg.id)) {
        const {res, t} = pending.get(msg.id);
        clearTimeout(t);
        pending.delete(msg.id);
        res(msg.result);
      } else if (msg.method && listeners.has(msg.method)) {
        listeners.get(msg.method)(msg.params);
      }
    });
    ws.on('error', reject);
  });
}

async function evaluate(conn, expr) {
  const r = await conn.send('Runtime.evaluate', {
    expression: expr,
    returnByValue: true,
    awaitPromise: true
  });
  if (r.exceptionDetails) {
    return { error: r.exceptionDetails.exception ? r.exceptionDetails.exception.description : String(r.exceptionDetails.text) };
  }
  return r.result ? r.result.value : r;
}

(async () => {
  try {
    const targets = await httpGetJson('/json/list');
    const whale = targets.find(t => t.title && t.title.includes('鲸准'));
    if (!whale) throw new Error('No whale page');
    
    console.log('=== 页面基本信息 ===');
    console.log('标题:', whale.title);
    console.log('报告URL:', whale.url);
    
    const conn = await connectWS(whale.webSocketDebuggerUrl);
    
    // 获取真实的location和页面内容
    const realUrl = await evaluate(conn, 'JSON.stringify({href:location.href, title:document.title, readyState:document.readyState})');
    console.log('\n=== 实际页面状态 ===');
    console.log(realUrl);
    
    // 检查是否有表格和分页
    const contentStatus = await evaluate(conn, `(function(){
      try {
        var tables = document.querySelectorAll('table');
        var ap = document.querySelector('.arco-pagination-item-active');
        var prev = document.querySelector('.arco-pagination-item-previous');
        var next = document.querySelector('.arco-pagination-item-next');
        var pagination = document.querySelector('.arco-pagination');
        
        // 获取所有分页按钮
        var pageItems = document.querySelectorAll('.arco-pagination-list .arco-pagination-item');
        var pageNumbers = [];
        for (var i=0; i<pageItems.length; i++) {
          pageNumbers.push(pageItems[i].textContent.trim());
        }
        
        // 检查是否有登录相关元素
        var loginForm = document.querySelector('form') || document.querySelector('[class*=login]');
        var loginBtns = document.querySelectorAll('button');
        var btnTexts = [];
        for (var i=0; i<Math.min(loginBtns.length, 10); i++) {
          btnTexts.push(loginBtns[i].textContent.trim().substring(0, 30));
        }
        
        // 前100字符body文本
        var bodyText = document.body ? document.body.textContent.substring(0, 300) : '(no body)';
        
        var t = tables[1] || tables[0];
        var firstRows = [];
        if (t) {
          var rows = t.querySelectorAll('tr');
          for (var i=0; i<Math.min(rows.length, 5); i++) {
            var cells = rows[i].querySelectorAll('td,th');
            var row = [];
            for (var j=0; j<Math.min(cells.length, 5); j++) {
              row.push(cells[j].textContent.trim().substring(0, 15));
            }
            firstRows.push(row);
          }
        }
        
        return JSON.stringify({
          tableCount: tables.length,
          currentPage: ap ? ap.textContent.trim() : null,
          paginationExist: !!pagination,
          paginationClass: pagination ? pagination.className : null,
          pageNumbers: pageNumbers,
          nextExist: !!next,
          nextDisabled: next ? next.className.indexOf('disabled') >= 0 : null,
          prevExist: !!prev,
          prevDisabled: prev ? prev.className.indexOf('disabled') >= 0 : null,
          hasLoginIndicator: !!loginForm,
          buttonTexts: btnTexts,
          firstSampleRows: firstRows,
          bodyPreview: bodyText
        }, null, 2);
      } catch(e) { return JSON.stringify({error:e.message}); }
    })()`);
    
    console.log('\n=== 内容状态 ===');
    console.log(contentStatus);
    
    // 如果在登录页，尝试导航到报表页
    const parsed = typeof contentStatus === 'string' ? JSON.parse(contentStatus) : contentStatus;
    if (!parsed.paginationExist && (parsed.hasLoginIndicator || whale.url.includes('/login'))) {
      console.log('\n=== 尝试导航到报表页 ===');
      await conn.send('Page.enable');
      await conn.send('Page.navigate', {url: 'https://apex.whaleidea.cn/star/report'});
      console.log('已发送导航命令，等待5秒...');
      await new Promise(r => setTimeout(r, 5000));
      
      const afterNav = await evaluate(conn, `JSON.stringify({
        href: location.href,
        title: document.title,
        tableCount: document.querySelectorAll('table').length,
        ap: (document.querySelector('.arco-pagination-item-active')||{}).textContent || null,
        body: document.body ? document.body.textContent.substring(0,200) : ''
      })`);
      console.log('导航后状态:', afterNav);
    }
    
    conn.close();
    process.exit(0);
  } catch (err) {
    console.error('ERROR:', err.message);
    process.exit(1);
  }
})();
