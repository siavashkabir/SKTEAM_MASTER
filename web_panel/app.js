const API_URL = 'https://skteamapi.sk-team-it.workers.dev';
let authToken = localStorage.getItem('sk_temp_token') || '';

function getHeaders() { return { 'Authorization': 'Bearer ' + authToken, 'Content-Type': 'application/json' }; }

async function login() {
    const passInput = document.getElementById('password-input');
    const pass = passInput ? passInput.value.trim() : '';
    if(!pass) return alert('رمز عبور را وارد کنید.');
    
    try {
        const res = await fetch(API_URL + '/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pass }) });
        const data = await res.json();
        
        if (data.success && data.token) { 
            authToken = data.token; 
            localStorage.setItem('sk_temp_token', authToken); 
            
            // اجبار به مخفی کردن صفحه لاگین و نمایش پنل
            document.getElementById('login-screen').style.display = 'none'; 
            document.getElementById('main-panel').style.display = 'flex'; 
            document.getElementById('main-panel').classList.remove('hidden');
            
            initApp(); 
        } else { 
            alert('خطا: ' + (data.error || 'رمز عبور اشتباه است')); 
        }
    } catch(e) { 
        alert('خطای شبکه: ' + e.message); 
    }
}

// اگر از قبل لاگین بود
window.addEventListener('load', () => { 
    if(authToken) {
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('main-panel').style.display = 'flex';
        document.getElementById('main-panel').classList.remove('hidden');
        initApp();
    }
});

function initApp() {
    checkStatus(); loadBots(); loadMetrics(); loadKeys(); loadBackups(); loadCronJobs();
    if(typeof initChat === 'function') initChat();
    setInterval(() => { checkStatus(); loadMetrics(); }, 5000);
    setInterval(() => { loadBots(); }, 10000);
}

function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    if (btn) btn.classList.add('active');
    if (tabId === 'bots') loadBots();
    if (tabId === 'dashboard') { loadMetrics(); }
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.innerText = msg; toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 3000);
}

async function apiFetch(endpoint, options = {}) {
    if (!options.headers) options.headers = getHeaders();
    const res = await fetch(API_URL + endpoint, options);
    if (res.status === 401) {
        authToken = ''; localStorage.removeItem('sk_temp_token');
        document.getElementById('login-screen').style.display = 'flex';
        document.getElementById('main-panel').style.display = 'none';
        throw new Error('Unauthorized');
    }
    return res.json();
}

function checkStatus() { apiFetch('/api/status').then(d => { document.getElementById('status-dot').className = d.status === 'online' ? 'dot online' : 'dot'; document.getElementById('status-text').innerText = d.status === 'online' ? 'آنلاین' : 'قطع'; }).catch(e => {}); }
function loadMetrics() { apiFetch('/api/get_metrics').then(d => { if(!d.metrics) return; const m = d.metrics; const agentPing = d.agentPing; let agentStatus = agentPing < 150000 ? "متصل" : "قطع"; let agentColor = agentPing < 150000 ? "var(--success)" : "var(--danger)"; document.getElementById('metrics-container').innerHTML = `<div class="widget"><div class="widget-title">💻 CPU</div><div class="widget-value">${m.cpu || 'N/A'}</div></div><div class="widget"><div class="widget-title">🧠 RAM</div><div class="widget-value">${m.ram || 'N/A'}</div></div><div class="widget"><div class="widget-title">💾 Disk</div><div class="widget-value">${m.disk || 'N/A'}</div></div><div class="widget"><div class="widget-title">🔋 Battery</div><div class="widget-value">${m.battery || 'N/A'}</div></div><div class="widget" style="border-color:${agentColor};"><div class="widget-title">📡 ایجنت</div><div class="widget-value" style="color:${agentColor};">${agentStatus}</div></div>`; }).catch(e => {}); }
function loadBots() { apiFetch('/api/get_bots').then(bots => { if(!bots.length) { document.getElementById('bots-container').innerHTML = '<p>رباتی یافت نشد.</p>'; return; } document.getElementById('bots-container').innerHTML = bots.map(b => `<div class="bot-card"><div class="bot-header"><div><b>${b.name}</b><div class="bot-stats">CPU: ${b.cpu} | RAM: ${b.ram}</div></div><span class="dot ${b.status === 'online' ? 'online' : ''}"></span></div></div>`).join(''); }).catch(e => {}); }
function loadKeys() { apiFetch('/api/get_settings').then(k => { if(k.GROQ_API_KEY) document.getElementById('key-groq').value = k.GROQ_API_KEY; if(k.OPENROUTER_KEY) document.getElementById('key-or').value = k.OPENROUTER_KEY; if(k.DEEPSEEK_API_KEY) document.getElementById('key-ds').value = k.DEEPSEEK_API_KEY; }).catch(e => {}); }
function loadBackups() { apiFetch('/api/get_backups').then(data => { if(!data.length) { document.getElementById('backups-container').innerHTML = '<p>هیچ بکاپی نیست.</p>'; return; } document.getElementById('backups-container').innerHTML = data.map(b => `<div class="backup-card"><div>${b.name}</div></div>`).join(''); }).catch(e => {}); }
function loadCronJobs() { apiFetch('/api/get_cron_jobs').then(jobs => { const list = document.getElementById('cron-list'); if(!list) return; if(!jobs.length) { list.innerHTML = '<p>هیچ زمان‌بندی نیست.</p>'; return; } list.innerHTML = jobs.map(j => `<div>⏰ ${j.time} - ${j.action}</div>`).join(''); }).catch(e => {}); }
function logUserChat(text) { console.log("User:", text); }
function logAIChat(text) { console.log("AI:", text); }
