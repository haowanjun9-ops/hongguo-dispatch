const WebSocket = require('ws');
const url = 'ws://127.0.0.1:9222/devtools/page/2B5AFC6CBB3F6907FE77E2544AFD7C91';

const tries = [
  { headers: {} },
  { headers: { 'Origin': 'http://127.0.0.1:9222' } },
  { headers: { 'Origin': 'devtools://devtools' } },
  { headers: { 'Authorization': 'Bearer test' } },
];

let idx = 0;
function tryNext() {
  if (idx >= tries.length) {
    console.log('所有尝试都失败');
    process.exit(1);
  }
  const opts = tries[idx++];
  console.log(`\n尝试 ${idx}: headers=${JSON.stringify(opts.headers)}`);
  const ws = new WebSocket(url, opts);
  let done = false;
  
  ws.on('open', () => {
    console.log('  SUCCESS: WebSocket opened!');
    ws.send(JSON.stringify({id:1,method:'Runtime.evaluate',params:{expression:'document.title',returnByValue:true}}));
  });
  ws.on('message', (d) => {
    const msg = d.toString();
    console.log('  MSG:', msg.substring(0, 200));
    done = true;
    ws.close();
    process.exit(0);
  });
  ws.on('error', (e) => {
    console.log('  ERROR:', e.message);
    setTimeout(tryNext, 300);
  });
  ws.on('unexpected-response', (req, res) => {
    console.log('  UNEXPECTED RESPONSE:', res.statusCode, res.statusMessage);
    let data = '';
    res.on('data', c => data += c);
    res.on('end', () => {
      console.log('  Body:', data.substring(0, 200));
      setTimeout(tryNext, 300);
    });
  });
  setTimeout(() => { if (!done) { ws.close(); setTimeout(tryNext, 300); } }, 3000);
}
tryNext();
