const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = process.env.PORT || 3000;
const QUOTA = 6;
const DEFAULT_TYPES = [
  { id: 'real', name: '真人', color: '#15a34a' },
  { id: 'ai', name: 'AI', color: '#2563eb' },
  { id: 'second', name: '二剪', color: '#7c3aed' }
];
const TYPE_COLORS = ['#15a34a', '#2563eb', '#7c3aed', '#dc2626', '#0891b2', '#ea580c', '#4f46e5', '#db2777', '#65a30d', '#9333ea'];
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
  const s = { lastResetDate: todayStr(), accounts: [], tasks: [], logs: [], types: DEFAULT_TYPES.map(t => ({ ...t })) };
  for (const t of Object.keys(SEED)) {
    SEED[t].tasks.forEach(id => s.tasks.push({ id: uid(), taskId: id, type: t }));
    SEED[t].accounts.forEach((name, i) => {
      const task = s.tasks.filter(x => x.type === t)[i % SEED[t].tasks.length];
      s.accounts.push({ id: uid(), name, type: t, taskId: task.id, used: {}, createdAt: Date.now() });
    });
  }
  return s;
}
function migrateAccountUsed() {
  for (const a of state.accounts) {
    if (typeof a.used === 'number') {
      const old = a.used;
      a.used = {};
      if (a.taskId && state.tasks.some(t => t.id === a.taskId)) a.used[a.taskId] = old;
    }
    if (!a.used || typeof a.used !== 'object') a.used = {};
    if (a.disabled === undefined) a.disabled = false;
    if (a.quota === undefined) a.quota = null;
  }
}
function loadState() {
  try { state = JSON.parse(fs.readFileSync(STORE, 'utf8')); }
  catch (e) { state = seedState(); }
  if (!state.types || !state.types.length) state.types = DEFAULT_TYPES.map(t => ({ ...t }));
  migrateAccountUsed();
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
function log(type, text, who) { const isSys = (who === '系统' || who == null); state.logs.unshift({ ts: Date.now(), type, role: isSys ? 'system' : 'admin', who: who || '系统', text }); if (state.logs.length > 80) state.logs.length = 80; }
// 角色判定：admin=管理员（全部权限） user=普通用户（只读+派单） null=未授权
function roleOfPass(p) {
  if (!PASSCODE && !ADMIN_PASSCODE) return 'admin'; // 未设任何密码：开放模式，视为管理员
  if (ADMIN_PASSCODE && p === ADMIN_PASSCODE) return 'admin';
  if (PASSCODE && p === PASSCODE) return 'user';
  return null;
}
function roleOfHeader(req) { return roleOfPass(req.headers['x-passcode'] || ''); }
function publicState() { return { needPasscode: !!PASSCODE, lastResetDate: state.lastResetDate, accounts: state.accounts, tasks: state.tasks, types: state.types }; }
function typeRemaining(type) {
  const tasks = state.tasks.filter(t => t.type === type);
  const accs = state.accounts.filter(a => a.type === type);
  return accs.reduce((sum, a) => sum + tasks.reduce((s, t) => s + (QUOTA - (a.used[t.id] || 0)), 0), 0);
}
function validType(type) { return state.types.some(x => x.id === type); }
function typeName(type) { const t = state.types.find(x => x.id === type); return t ? t.name : type; }
function typeColor(type) { const t = state.types.find(x => x.id === type); return t ? t.color : '#64748b'; }
function accountUsed(a, taskId) { return (a.used && a.used[taskId]) || 0; }
function accountTotalUsed(a) { return Object.values(a.used || {}).reduce((s, n) => s + n, 0); }
function accountQuota(a) { return (a.quota === undefined || a.quota === null) ? QUOTA : Math.max(1, parseInt(a.quota, 10) || 1); }
function accountCapacity(a) { return Math.max(1, state.tasks.filter(t => t.type === a.type).length) * accountQuota(a); }
function typeTasks(type) { return state.tasks.filter(t => t.type === type); }

// 服务端原子分配：每个账号对每个任务都有 QUOTA 条额度；谁先请求谁先占，避免重复
function allocate(type, need, who) {
  const tasks = typeTasks(type);
  const accs = state.accounts.filter(a => a.type === type && !a.disabled);
  let pairs = [];
  for (const a of accs) {
    const q = accountQuota(a);
    for (const t of tasks) {
      const left = q - (a.used[t.id] || 0);
      if (left > 0) pairs.push({ a, t, left });
    }
  }
  // 优先使用剩余额度最大的组合，让分配更均匀
  pairs.sort((x, y) => y.left - x.left || x.a.name.localeCompare(y.a.name, 'zh'));
  let remaining = need;
  const plan = [];
  for (const p of pairs) {
    if (remaining <= 0) break;
    const give = Math.min(p.left, remaining);
    const before = p.a.used[p.t.id] || 0;
    p.a.used[p.t.id] = before + give;
    plan.push({ accId: p.a.id, name: p.a.name, taskId: p.t.taskId, taskDbId: p.t.id, before, give });
    remaining -= give;
  }
  const assigned = need - remaining;
  if (assigned > 0) { log('dispatch', `派单 ${typeName(type)} ${assigned} 条（${plan.length} 个组合）`, who); saveState(); broadcast(); }
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

  if (req.method === 'GET' && url === '/api/logs') {
    const role = roleOfHeader(req);
    if (!role) return send(res, 403, { error: '需要访问密码' });
    if (role !== 'admin') return send(res, 403, { error: '需要管理员权限' });
    return send(res, 200, { logs: state.logs });
  }
  if (req.method === 'GET' && url === '/api/types') {
    return send(res, 200, { types: state.types });
  }

  if (req.method === 'POST') {
    const body = await readBody(req);
    if (url === '/api/auth') {
      const role = roleOfPass(body.passcode || '');
      if (!role) return send(res, 401, { ok: false });
      return send(res, 200, { ok: true, role });
    }
    // 自动分配：所有已认证用户可用
    if (url === '/api/dispatch') {
      const role = roleOfHeader(req);
      if (!role) return send(res, 403, { error: '需要访问密码' });
      const who = ((body && body.adminName) || '').trim() || (role === 'admin' ? '管理员' : '用户');
      const need = parseInt(body.need, 10);
      const type = body.type;
      if (!validType(type) || !need || need < 1) return send(res, 400, { error: '参数错误' });
      const r = allocate(type, need, who);
      return send(res, 200, r);
    }

    // 以下管理接口仅管理员可用
    const role = roleOfHeader(req);
    if (!role) return send(res, 403, { error: '需要访问密码' });
    if (role !== 'admin') return send(res, 403, { error: '需要管理员权限' });
    const who = ((body && body.adminName) || '').trim() || '管理员';
    if (url === '/api/type') {
      const name = (body.name || '').trim();
      if (!name) return send(res, 400, { error: '类型名称不能为空' });
      if (state.types.some(t => t.name === name)) return send(res, 400, { error: '类型名称已存在' });
      const id = (body.id || 't-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5)).slice(0, 24);
      if (state.types.some(t => t.id === id)) return send(res, 400, { error: '类型ID已存在' });
      const color = TYPE_COLORS[state.types.length % TYPE_COLORS.length];
      state.types.push({ id, name, color });
      log('system', `新增素材类型「${name}」`, who); saveState(); broadcast();
      return send(res, 200, { ok: true, type: { id, name, color } });
    }
    if (url === '/api/inc') {
      const a = state.accounts.find(x => x.id === body.id);
      if (a && !a.disabled) {
        const tasks = typeTasks(a.type);
        const q = accountQuota(a);
        const cand = tasks
          .map(t => ({ t, used: a.used[t.id] || 0 }))
          .filter(x => x.used < q)
          .sort((x, y) => x.used - y.used || (x.t.id === a.taskId ? -1 : 0));
        if (cand.length) {
          const t = cand[0].t;
          a.used[t.id] = (a.used[t.id] || 0) + 1;
          log('inc', `「${a.name}」任务 ${t.taskId} +1（${a.used[t.id]}/${q}）`, who);
          saveState(); broadcast();
        }
      }
      return send(res, 200, { ok: true });
    }
    if (url === '/api/dec') {
      const a = state.accounts.find(x => x.id === body.id);
      if (a) {
        const tasks = typeTasks(a.type);
        const cand = tasks
          .map(t => ({ t, used: a.used[t.id] || 0 }))
          .filter(x => x.used > 0)
          .sort((x, y) => y.used - x.used || (x.t.id === a.taskId ? -1 : 0));
        if (cand.length) {
          const t = cand[0].t;
          a.used[t.id] = (a.used[t.id] || 0) - 1;
          if (!a.used[t.id]) delete a.used[t.id];
          log('dec', `「${a.name}」任务 ${t.taskId} −1（${a.used[t.id] || 0}/${accountQuota(a)}）`, who);
          saveState(); broadcast();
        }
      }
      return send(res, 200, { ok: true });
    }
    if (url === '/api/account') {
      const type = body.type;
      const taskId = body.taskId || state.tasks.find(t => t.type === type)?.id || '';
      if (!validType(type)) return send(res, 400, { error: '参数错误' });
      // 支持两种格式：1) names + 统一 quota（旧） 2) accounts: [{name,quota?}]
      let items = [];
      if (Array.isArray(body.accounts)) {
        items = body.accounts.map(a => ({ name: (a.name || '').trim(), quota: a.quota }));
      } else {
        const names = Array.isArray(body.names) ? body.names : [body.name];
        const quota = body.quota === undefined || body.quota === '' ? null : parseInt(body.quota, 10);
        items = names.map(name => ({ name: (name || '').trim(), quota }));
      }
      let added = 0;
      for (const item of items) {
        const name = item.name;
        if (!name) continue;
        const quota = item.quota === undefined || item.quota === '' || item.quota === null ? null : Math.max(1, parseInt(item.quota, 10) || 1);
        state.accounts.push({ id: uid(), name, type, taskId, used: {}, disabled: false, quota, createdAt: Date.now() });
        const qText = quota ? `（限${quota}条/任务）` : '';
        log('account', `新增账号「${name}」(${typeName(type)})${qText}`, who);
        added++;
      }
      if (added) { saveState(); broadcast(); }
      return send(res, 200, { ok: true, added });
    }
    if (url === '/api/task') {
      const ids = Array.isArray(body.taskIds) ? body.taskIds : [body.taskId];
      const type = body.type;
      if (!validType(type)) return send(res, 400, { error: '参数错误' });
      let added = 0;
      for (const item of ids) {
        const id = (item || '').trim();
        if (!id) continue;
        if (state.tasks.some(t => t.taskId === id && t.type === type)) continue;
        state.tasks.push({ id: uid(), taskId: id, type });
        log('task', `新增任务 ${id} (${typeName(type)})`, who);
        added++;
      }
      if (added) { saveState(); broadcast(); }
      return send(res, 200, { ok: true, added });
    }
    if (url === '/api/reassign') {
      const a = state.accounts.find(x => x.id === body.id);
      if (a && state.tasks.some(t => t.id === body.taskId)) { a.taskId = body.taskId; saveState(); broadcast(); }
      return send(res, 200, { ok: true });
    }
    if (url === '/api/reset') {
      state.accounts.forEach(a => a.used = {});
      state.lastResetDate = todayStr();
      log('reset', '手动刷新，今日计数清零', who); saveState(); broadcast();
      return send(res, 200, { ok: true });
    }
    if (url === '/api/account/toggle') {
      const a = state.accounts.find(x => x.id === body.id);
      if (a) { a.disabled = !a.disabled; log('account', `「${a.name}」${a.disabled ? '已停用' : '已启用'}`, who); saveState(); broadcast(); }
      return send(res, 200, { ok: true, disabled: a ? a.disabled : false });
    }
    if (url === '/api/account/quota') {
      const a = state.accounts.find(x => x.id === body.id);
      if (a) {
        const q = body.quota === undefined || body.quota === '' || body.quota === null ? null : Math.max(1, parseInt(body.quota, 10));
        a.quota = q;
        log('account', `「${a.name}」配额设为 ${q === null ? '默认' : q + '条/任务'}`, who);
        saveState(); broadcast();
      }
      return send(res, 200, { ok: true, quota: a ? a.quota : null });
    }
  }

  if (req.method === 'DELETE' && url.startsWith('/api/account/')) {
    const role = roleOfHeader(req);
    if (!role) return send(res, 403, { error: '需要访问密码' });
    if (role !== 'admin') return send(res, 403, { error: '需要管理员权限' });
    const body = await readBody(req);
    const who = ((body && body.adminName) || '').trim() || '管理员';
    const id = url.split('/').pop();
    const a = state.accounts.find(x => x.id === id);
    state.accounts = state.accounts.filter(x => x.id !== id);
    if (a) log('account', `删除账号「${a.name}」(${typeName(a.type)})`, who);
    saveState(); broadcast();
    return send(res, 200, { ok: true });
  }
  if (req.method === 'DELETE' && url.startsWith('/api/task/')) {
    const role = roleOfHeader(req);
    if (!role) return send(res, 403, { error: '需要访问密码' });
    if (role !== 'admin') return send(res, 403, { error: '需要管理员权限' });
    const body = await readBody(req);
    const who = ((body && body.adminName) || '').trim() || '管理员';
    const id = url.split('/').pop();
    const t = state.tasks.find(x => x.id === id);
    if (t) {
      state.tasks = state.tasks.filter(x => x.id !== id);
      // 清理已不存在的任务在账号 used 中的计数
      state.accounts.forEach(a => { if (a.used && a.used[id]) delete a.used[id]; });
      log('task', `删除任务 ${t.taskId} (${typeName(t.type)})`, who); saveState(); broadcast();
    }
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
