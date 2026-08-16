const WebSocket = require('ws');
const http = require('http');

// Step 1: 获取标签页列表
const options = {
  hostname: '127.0.0.1',
  port: 9222,
  path: '/json/list',
  method: 'GET',
  headers: { 'Host': '127.0.0.1' }
};

const req = http.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    try {
      const targets = JSON.parse(data);
      const whale = targets.find(t => t.title && t.title.includes('鲸准'));
      if (!whale) {
        console.log('ERROR: No whale page found. Targets:', JSON.stringify(targets, null, 2));
        process.exit(1);
      }
      console.log('Found whale page:', JSON.stringify({
        id: whale.id,
        title: whale.title,
        url: whale.url,
        type: whale.type
      }, null, 2));
      
      // Step 2: 连接到目标页面的WebSocket
      const wsUrl = whale.webSocketDebuggerUrl;
      console.log('\nConnecting to:', wsUrl);
      const ws = new WebSocket(wsUrl);
      let msgId = 0;
      const pending = new Map();
      
      ws.on('open', async () => {
        console.log('WebSocket connected!');
        
        // 发送命令的辅助函数
        function send(method, params = {}) {
          const id = ++msgId;
          const msg = JSON.stringify({ id, method, params });
          return new Promise((resolve, reject) => {
            pending.set(id, { resolve, reject, timeout: setTimeout(() => reject(new Error('timeout: ' + method)), 10000) });
            ws.send(msg);
          });
        }
        
        ws.on('message', (data) => {
          const msg = JSON.parse(data.toString());
          if (msg.id && pending.has(msg.id)) {
            const { resolve, timeout } = pending.get(msg.id);
            clearTimeout(timeout);
            pending.delete(msg.id);
            resolve(msg.result);
          } else if (msg.method) {
            // console.log('Event:', msg.method);
          }
        });
        
        try {
          // 先获取当前页面的URL和标题
          const nav = await send('Page.getNavigationHistory');
          console.log('\nCurrent entry:', nav.entries[nav.currentIndex] ? 
            JSON.stringify({title: nav.entries[nav.currentIndex].title, url: nav.entries[nav.currentIndex].url}) : 'N/A');
          
          // 评估页面脚本：检查是否在报表页，当前是第几页
          const evalResult = await send('Runtime.evaluate', {
            expression: `(function(){
              try {
                var url = location.href;
                var title = document.title;
                var tables = document.querySelectorAll('table').length;
                var ap = document.querySelector('.arco-pagination-item-active');
                var currentPage = ap ? ap.textContent.trim() : '?';
                var nextBtn = document.querySelector('.arco-pagination-item-next');
                var prevBtn = document.querySelector('.arco-pagination-item-previous');
                var nextDisabled = nextBtn ? nextBtn.className.indexOf('disabled') !== -1 : true;
                var prevDisabled = prevBtn ? prevBtn.className.indexOf('disabled') !== -1 : true;
                // 表格内容预览：第一个表格的前5行前3列
                var t = document.querySelectorAll('table');
                var dt = t[1] || t[0];
                var sample = [];
                if (dt) {
                  var rows = dt.querySelectorAll('tr');
                  for (var i = 0; i < Math.min(rows.length, 8); i++) {
                    var cells = rows[i].querySelectorAll('td,th');
                    var row = [];
                    for (var j = 0; j < Math.min(cells.length, 4); j++) {
                      row.push(cells[j].textContent.trim().substring(0, 20));
                    }
                    sample.push(row);
                  }
                }
                return JSON.stringify({
                  url: url,
                  docTitle: title,
                  tableCount: tables,
                  currentPage: currentPage,
                  hasNextBtn: !!nextBtn,
                  nextDisabled: nextDisabled,
                  hasPrevBtn: !!prevBtn,
                  prevDisabled: prevDisabled,
                  sampleRows: sample,
                  sampleCount: sample.length
                }, null, 2);
              } catch(e) {
                return JSON.stringify({error: e.message});
              }
            })()`,
            returnByValue: true
          });
          
          console.log('\n=== Page Status ===');
          console.log(evalResult.result ? evalResult.result.value : JSON.stringify(evalResult));
          
          // 完成
          ws.close();
          process.exit(0);
          
        } catch (err) {
          console.error('CDP Error:', err.message);
          ws.close();
          process.exit(1);
        }
      });
      
      ws.on('error', err => {
        console.error('WebSocket error:', err.message);
        process.exit(1);
      });
      
    } catch (err) {
      console.error('Parse error:', err.message, 'Raw data:', data.substring(0, 200));
      process.exit(1);
    }
  });
});

req.on('error', err => console.error('HTTP error:', err.message));
req.end();
