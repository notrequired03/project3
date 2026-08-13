document.addEventListener('DOMContentLoaded', () => {
    // Auth & Screens
    const loginScreen = document.getElementById('loginScreen');
    const appContainer = document.getElementById('appContainer');
    const loginForm = document.getElementById('loginForm');
    const loginUsername = document.getElementById('loginUsername');
    const loginPassword = document.getElementById('loginPassword');
    const logoutBtn = document.getElementById('logoutBtn');

    // Header Status & Quick Toggle
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const botActiveToggle = document.getElementById('botActiveToggle');
    const quickToggleBtn = document.getElementById('quickToggleBtn');
    const infoBotStatus = document.getElementById('infoBotStatus');
    const infoLastPost = document.getElementById('infoLastPost');

    // Stats Elements
    const statTotalPosts = document.getElementById('statTotalPosts');
    const statTotalReplies = document.getElementById('statTotalReplies');
    const statInterval = document.getElementById('statInterval');

    // Navigation Tabs
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    // Controls Form
    const scheduleForm = document.getElementById('scheduleForm');
    const postInterval = document.getElementById('postInterval');
    const postIntervalVal = document.getElementById('postIntervalVal');
    const autoReplyEnabled = document.getElementById('autoReplyEnabled');
    const targetKeywords = document.getElementById('targetKeywords');

    // Persona Form
    const personaForm = document.getElementById('personaForm');
    const personaPrompt = document.getElementById('personaPrompt');
    const resetPersonaBtn = document.getElementById('resetPersonaBtn');

    // Preview & Test Studio
    const generatePreviewBtn = document.getElementById('generatePreviewBtn');
    const mockContent = document.getElementById('mockContent');
    const customPostText = document.getElementById('customPostText');
    const postNowBtn = document.getElementById('postNowBtn');

    // Logs Console
    const logsConsole = document.getElementById('logsConsole');
    const refreshLogsBtn = document.getElementById('refreshLogsBtn');
    const toastContainer = document.getElementById('toastContainer');

    // Toast Notification Helper
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerText = message;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    // Check Login Session
    function checkAuth() {
        const isLoggedIn = sessionStorage.getItem('isLoggedIn') === 'true';
        if (isLoggedIn) {
            loginScreen.classList.add('hidden');
            appContainer.classList.remove('hidden');
            loadConfig();
            fetchStats();
            fetchLogs();
        } else {
            loginScreen.classList.remove('hidden');
            appContainer.classList.add('hidden');
        }
    }

    // Login Submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const user = loginUsername.value.trim();
        const pass = loginPassword.value.trim();

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: user, password: pass })
            });

            const data = await res.json();
            if (res.ok && data.status === 'success') {
                sessionStorage.setItem('isLoggedIn', 'true');
                sessionStorage.setItem('adminUser', user);
                showToast(data.message, 'success');
                checkAuth();
            } else {
                showToast(data.message || 'Invalid username or password!', 'error');
            }
        } catch (err) {
            showToast('Network error during login attempt', 'error');
        }
    });

    // Logout Action
    logoutBtn.addEventListener('click', () => {
        sessionStorage.removeItem('isLoggedIn');
        sessionStorage.removeItem('adminUser');
        showToast('Logged out.', 'info');
        checkAuth();
    });

    // Tab Navigation
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            navButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const tabId = `tab-${btn.dataset.tab}`;
            document.getElementById(tabId).classList.add('active');

            if (btn.dataset.tab === 'logs') {
                fetchLogs();
            }
        });
    });

    // Slider text display update
    postInterval.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        const postsPerDay = Math.round((24 * 60) / val);
        postIntervalVal.innerText = `${val} Mins (~${postsPerDay} posts/day)`;
    });

    // Fetch Stats & Config
    async function fetchStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            if (data.status === 'success') {
                const stats = data.stats || {};
                statTotalPosts.innerText = stats.total_posts || 0;
                statTotalReplies.innerText = stats.total_replies || 0;
                statInterval.innerText = `${data.post_interval_minutes || 30} Mins`;
                infoLastPost.innerText = stats.last_post_time || 'No posts yet';
            }
        } catch (err) {
            console.error('Failed to fetch stats:', err);
        }
    }

    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            const data = await res.json();
            if (data.status === 'success') {
                const cfg = data.config;

                postInterval.value = cfg.post_interval_minutes || 30;
                const postsPerDay = Math.round((24 * 60) / (cfg.post_interval_minutes || 30));
                postIntervalVal.innerText = `${cfg.post_interval_minutes || 30} Mins (~${postsPerDay} posts/day)`;

                autoReplyEnabled.checked = cfg.auto_reply_enabled !== false;
                targetKeywords.value = (cfg.target_keywords || []).join(', ');
                personaPrompt.value = cfg.persona_prompt || '';

                const isBotActive = cfg.bot_enabled && data.scheduler_active;
                botActiveToggle.checked = isBotActive;
                updateStatusUI(isBotActive);
            }
        } catch (err) {
            console.error('Failed to load configuration:', err);
        }
    }

    function updateStatusUI(isActive) {
        if (isActive) {
            statusDot.className = 'status-dot active';
            statusText.innerText = 'Bot Active & Scheduled';
            infoBotStatus.innerText = 'ACTIVE (Running)';
            infoBotStatus.className = 'info-value text-emerald';
        } else {
            statusDot.className = 'status-dot inactive';
            statusText.innerText = 'Bot Paused';
            infoBotStatus.innerText = 'PAUSED';
            infoBotStatus.className = 'info-value';
        }
    }

    // Toggle Bot Enable/Disable
    async function toggleBotStatus(enable) {
        try {
            const res = await fetch('/api/toggle_bot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enable: enable })
            });
            const data = await res.json();
            if (data.status === 'success') {
                botActiveToggle.checked = data.bot_enabled;
                updateStatusUI(data.bot_enabled);
                showToast(data.bot_enabled ? 'Bot started successfully!' : 'Bot paused.', 'success');
                fetchLogs();
            }
        } catch (err) {
            showToast('Failed to toggle bot status', 'error');
        }
    }

    botActiveToggle.addEventListener('change', (e) => {
        toggleBotStatus(e.target.checked);
    });

    quickToggleBtn.addEventListener('click', () => {
        toggleBotStatus(!botActiveToggle.checked);
    });

    // Save Schedule & Keywords
    scheduleForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const keywordsArray = targetKeywords.value.split(',').map(k => k.trim()).filter(k => k.length > 0);
        const payload = {
            post_interval_minutes: parseInt(postInterval.value),
            auto_reply_enabled: autoReplyEnabled.checked,
            target_keywords: keywordsArray
        };

        try {
            const res = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast('Schedule & keywords updated!', 'success');
                loadConfig();
                fetchStats();
            }
        } catch (err) {
            showToast('Failed to update schedule', 'error');
        }
    });

    // Save Persona
    personaForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const res = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ persona_prompt: personaPrompt.value })
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast('AI Persona updated!', 'success');
            }
        } catch (err) {
            showToast('Failed to update AI Persona', 'error');
        }
    });

    resetPersonaBtn.addEventListener('click', () => {
        personaPrompt.value = "You are the unhinged, hilarious, savagely witty social media manager for chathere.online (a modern, instant, zero-lag random video & text chat platform where people connect instantly for free without signup). Your tone is heavily inspired by Ryanair's official Twitter account: sarcastic, self-aware, meme-heavy, snappy, trolling rival legacy chat sites (like dead Omegle clones, laggy Discord calls, awkward video apps), and roasting relatable internet behavior. Keep tweets under 240 characters. ALWAYS include or reference chathere.online or #chathere in a clever/funny way.";
        showToast('Persona reset to default Ryanair template.', 'info');
    });

    // Generate Tweet Preview
    generatePreviewBtn.addEventListener('click', async () => {
        generatePreviewBtn.disabled = true;
        generatePreviewBtn.innerText = '✨ Generating...';

        try {
            const res = await fetch('/api/preview_tweet', { method: 'POST' });
            const data = await res.json();
            if (data.status === 'success') {
                mockContent.innerText = data.preview;
                customPostText.value = data.preview;
                showToast('Sample Ryanair-style tweet generated!', 'success');
            } else {
                showToast(data.error || 'Failed to generate preview', 'error');
            }
        } catch (err) {
            showToast('Error generating preview', 'error');
        } finally {
            generatePreviewBtn.disabled = false;
            generatePreviewBtn.innerText = '✨ Generate AI Tweet Preview';
        }
    });

    // Post Now Button
    postNowBtn.addEventListener('click', async () => {
        const textToPost = customPostText.value.trim();
        postNowBtn.disabled = true;
        postNowBtn.innerText = '🚀 Publishing to Twitter...';

        try {
            const res = await fetch('/api/post_now', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ custom_text: textToPost })
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast('Tweet published successfully!', 'success');
                fetchLogs();
                fetchStats();
            } else {
                showToast(data.error || 'Failed to post tweet', 'error');
            }
        } catch (err) {
            showToast('Error publishing tweet', 'error');
        } finally {
            postNowBtn.disabled = false;
            postNowBtn.innerText = '🚀 Post Tweet Now to Twitter';
        }
    });

    // Fetch Logs
    async function fetchLogs() {
        try {
            const res = await fetch('/api/logs');
            const data = await res.json();
            if (data.status === 'success') {
                logsConsole.innerHTML = '';
                if (data.logs.length === 0) {
                    logsConsole.innerHTML = '<div class="log-entry">No logs recorded yet.</div>';
                    return;
                }
                data.logs.forEach(log => {
                    const div = document.createElement('div');
                    div.className = `log-entry ${log.level}`;
                    div.innerText = `[${log.timestamp}] [${log.level}] ${log.message}`;
                    logsConsole.appendChild(div);
                });
            }
        } catch (err) {
            console.error('Failed to fetch logs:', err);
        }
    }

    refreshLogsBtn.addEventListener('click', fetchLogs);

    // Init & Polling
    checkAuth();
    setInterval(() => {
        if (sessionStorage.getItem('isLoggedIn') === 'true') {
            fetchStats();
            fetchLogs();
        }
    }, 6000);
});
