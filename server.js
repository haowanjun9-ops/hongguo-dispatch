const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = process.env.PORT || 3000;
const QUOTA = 6;
const TYPES = { real: '真人', ai: 'AI', second: '二剪' };
const STORE = path.join(process.env.DATA_DIR || __dirname, 'data.json');
const PASSCODE = process.env.PASSCODE || '';        // 普通用户密码（只读 + 派单）
const ADMIN_PASSCODE = process.env.ADMIN_PASSCODE || PASSCODE; // 管理员密码；未单独设置时退化为等于 PASSCODE

const SEED = {
  real: {
    accounts: ["未来成长日记","智能效率社","学霸的隐藏武器","次元创意工坊","NPCCCCC","会爆","对啊对啊对","寻剧千百遍","券券喂饱你","追剧老伙计","外卖阿彭","超荟看剧","出片达人小葵","好剧治愈所","追剧充电站","剧剧大世界"],
    tasks: ["7576849166903738387","7566460022732111881","7566460271952281626","7576848881806622726","7661895222078521354","7661895103413239817","7661894455893196810","7661894329392349226"]
  },
  ai: {
    accounts: ["效率火箭","苏苏说说看","苏苏有话说","推啊推啊推","动态漫不打烊","小余爱追剧","追剧小雷达","看剧会上瘾"],
    tasks: ["7626972396727304228","7660403527034355763"]
  },
  second: {
    accounts: ["超能工具箱","我的智能外挂","董小姐自媒体"],
    tasks: ["7566459273833037878","7565814540873711643","7661894113079836698","7661893595297562643"]
  }
};

function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }
function todayStr() { const d = new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }

let state;
function seedState() {
  const s = { lastResetDate: todayStr(), accounts: [], tasks: [], logs: [] };
  for (const t of Object.keys(SEED)) {
    SEED[t].tasks.forEach(id => s.tasks.push({ id: uid(), taskId: id, type: t }));
    SEED[t].accounts.forEach((name, i) => {
      const task = s.tasks.filter(x => x.type === t)[i % SEED[t].tasks.length];
      s.accounts.push({ id: uid(), name, type: t, taskId: task.id, used: 0, createdAt: Date.now() });
    });
  }
  return s;
}
function loadState() {
  try { state = JSON.parse(fs.readFileSync(STORE, 'utf8')); }
  catch (e) { state = seedState(); }
  ensureFresh();
  saveState();
}
function saveState() { try { fs.writeFileSync(STORE, JSON.stringify(state, null, 2)); } catch (e) {} }
function ensureFresh() {
  if (state.lastResetDate !== todayStr()) {
    state.accounts.forEach(a => a.used = 0);
    state.lastResetDate = todayStr();
    log('reset', '跨天自动刷新，今日计数清零');
  }
}
function taskIdOf(id) { const t = state.tasks.find(x => x.id === id); return t ? t.taskId : '—'; }
function log(type, text) { state.logs.unshift({ ts: Date.now(), type, text }); if (state.logs.length > 60) state.logs.length = 60; }
// 角色判定：admin=管理员（全部权限） user=普通用户（只读+派单） null=未授权
function roleOfPass(p) {
  if (!PASSCODE && !ADMIN_PASSCODE) return 'admin'; // 未设任何密码：开放模式，视为管理员
  if (ADMIN_PASSCODE && p === ADMIN_PASSCODE) return 'admin';
  if (PASSCODE && p === PASSCODE) return 'user';
  return null;
}
function roleOfHeader(req) { return roleOfPass(req.headers['x-passcode'] || ''); }
function publicState() { return { needPasscode: !!PASSCODE, lastResetDate: state.lastResetDate, accounts: state.accounts, tasks: state.tasks, logs: state.logs }; }
function typeRemaining(type) { return state.accounts.filter(a => a.type === type).reduce((s, a) => s + (QUOTA - a.used), 0); }

// 服务端原子分配：谁先请求谁先占，避免重复
function allocate(type, need) {
  const accs = state.accounts.filter(a => a.type === type && a.used < QUOTA)
    .map(a => ({ a, left: QUOTA - a.used }))
    .sort((x, y) => y.left - x.left);
  let remaining = need;
  const plan = [];
  for (const it of accs) {
    if (remaining <= 0) break;
    const give = Math.min(it.left, remaining);
    plan.push({ accId: it.a.id, name: it.a.name, taskId: taskIdOf(it.a.taskId), before: it.a.used, give });
    it.a.used += give;
    remaining -= give;
  }
  const assigned = need - remaining;
  if (assigned > 0) { log('dispatch', `派单 ${TYPES[type]} ${assigned} 条（${plan.length} 个账号）`); saveState(); broadcast(); }
  return { plan, assigned, shortfall: remaining };
}

// SSE 实时同步
const clients = new Set();
function broadcast() {
  const data = 'data: ' + JSON.stringify(publicState()) + '\n\n';
  clients.forEach(r => { try { r.write(data); } catch (e) {} });
}

function readBody(req) {
  return new Promise(res => {
    let b = '';
    req.on('data', c => b += c);
    req.on('end', () => { try { res(b ? JSON.parse(b) : {}); } catch (e) { res({}); } });
  });
}
function send(res, code, obj) { res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)); }

const server = http.createServer(async (req, res) => {
  ensureFresh();
  const url = req.url.split('?')[0];

  if (req.method === 'GET' && (url === '/' || url === '/index.html')) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(fs.readFileSync(path.join(__dirname, 'public', 'index.html')));
    return;
  }
  if (req.method === 'GET' && url === '/api/state') { send(res, 200, publicState()); return; }

  if (req.method === 'GET' && url === '/api/events') {
    res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' });
    res.write('retry: 3000\n\n');
    res.write('data: ' + JSON.stringify(publicState()) + '\n\n');
    clients.add(res);
    const ping = setInterval(() => { try { res.write(': ping\n\n'); } catch (e) {} }, 25000);
    req.on('close', () => { clearInterval(ping); clients.delete(res); });
    return;
  }

  if (req.method === 'POST') {
    const body = await readBody(req);
    if (url === '/api/auth') {
      const role = roleOfPass(body.passcode || '');
      if (!role) return send(res, 401, { ok: false });
      return send(res, 200, { ok: true, role });
    }
    const role = roleOfHeader(req);
    if (!role) return send(res, 403, { error: '需要访问密码' });
    if (role !== 'admin') return send(res, 403, { error: '需要管理员权限' });
    if (url === '/api/dispatch') {
      const need = parseInt(body.need, 10);
      const type = body.type;
      if (!TYPES[type] || !need || need < 1) return send(res, 400, { error: '参数错误' });
      const r = allocate(type, need);
      return send(res, 200, r);
    }
    if (url === '/api/inc') {
      const a = state.accounts.find(x => x.id === body.id);
      if (a && a.used < QUOTA) { a.used++; log('inc', `「${a.name}」+1（${a.used}/${QUOTA}）`); saveState(); broadcast(); }
      return send(res, 200, { ok: true });
    }
    if (url === '/api/dec') {
      const a = state.accounts.find(x => x.id === body.id);
      if (a && a.used > 0) { a.used--; log('dec', `「${a.name}」−1（${a.used}/${QUOTA}）`); saveState(); broadcast(); }
      return send(res, 200, { ok: true });
    }
    if (url === '/api/account') {
      const name = (body.name || '').trim();
      const type = body.type;
      const taskId = body.taskId;
      if (!name || !TYPES[type] || !taskId) return send(res, 400, { error: '参数错误' });
      state.accounts.push({ id: uid(), name, type, taskId, used: 0, createdAt: Date.now() });
      log('account', `新增账号「${name}」(${TYPES[type]})`); saveState(); broadcast();
      return send(res, 200, { ok: true });
    }
    if (url === '/api/task') {
      const id = (body.taskId || '').trim();
      const type = body.type;
      if (!id || !TYPES[type]) return send(res, 400, { error: '参数错误' });
      if (state.tasks.some(t => t.taskId === id && t.type === type)) return send(res, 400, { error: '任务已存在' });
      state.tasks.push({ id: uid(), taskId: id, type });
      log('task', `新增任务 ${id} (${TYPES[type]})`); saveState(); broadcast();
      return send(res, 200, { ok: true });
    }
    if (url === '/api/reassign') {
      const a = state.accounts.find(x => x.id === body.id);
      if (a && state.tasks.some(t => t.id === body.taskId)) { a.taskId = body.taskId; saveState(); broadcast(); }
      return send(res, 200, { ok: true });
    }
    if (url === '/api/reset') {
      state.accounts.forEach(a => a.used = 0); state.lastResetDate = todayStr();
      log('reset', '手动刷新，今日计数清零'); saveState(); broadcast();
      return send(res, 200, { ok: true });
    }
  }

  if (req.method === 'DELETE' && url.startsWith('/api/account/')) {
    const role = roleOfHeader(req);
    if (!role) return send(res, 403, { error: '需要访问密码' });
    if (role !== 'admin') return send(res, 403, { error: '需要管理员权限' });
    const id = url.split('/').pop();
    state.accounts = state.accounts.filter(x => x.id !== id);
    saveState(); broadcast();
    return send(res, 200, { ok: true });
  }

  send(res, 404, { error: 'not found' });
});

loadState();
setInterval(ensureFresh, 60000); // 每分钟检查跨天
server.listen(PORT, () => {
  console.log('红果素材分发平台已启动');
  if (PASSCODE) console.log('  用户密码(PASSCODE): ' + PASSCODE + '  （只读 + 派单）');
  if (ADMIN_PASSCODE && ADMIN_PASSCODE !== PASSCODE) console.log('  管理密码(ADMIN_PASSCODE): ' + ADMIN_PASSCODE + '  （可增删账号/任务）');
  else if (PASSCODE) console.log('  未单独设置 ADMIN_PASSCODE，当前 PASSCODE 同时是管理员密码');
  console.log('  本机:  http://localhost:' + PORT);
  const ifs = os.networkInterfaces();
  for (const k of Object.keys(ifs)) {
    for (const n of ifs[k]) {
      if (n.family === 'IPv4' && !n.internal) console.log('  局域网: http://' + n.address + ':' + PORT);
    }
  }
});
