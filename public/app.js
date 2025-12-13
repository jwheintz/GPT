// WebSocket connection
let ws = null;
let isAuthenticated = false;
let isTeacher = false;
let killSwitchActive = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;

// Configuration
const WS_URL = getWebSocketURL();

// Get WebSocket URL from current location or config
function getWebSocketURL() {
    // Check if there's a configured server URL (for when hosted on external site)
    const configuredServer = localStorage.getItem('serverURL');
    if (configuredServer) {
        return configuredServer.replace('http://', 'ws://').replace('https://', 'wss://');
    }
    
    // Default to current host
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}`;
}

// DOM Elements
const loginContainer = document.getElementById('login-container');
const controlPanel = document.getElementById('control-panel');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const roleBadge = document.getElementById('role-badge');
const serverStatus = document.getElementById('server-status');
const obsStatus = document.getElementById('obs-status');
const wsStatus = document.getElementById('ws-status');
const teacherControls = document.getElementById('teacher-controls');
const studentControls = document.getElementById('student-controls');
const killSwitchToggle = document.getElementById('kill-switch');
const killSwitchLabel = document.getElementById('kill-switch-label');
const killSwitchMessage = document.getElementById('kill-switch-message');
const activityFeed = document.getElementById('activity-feed');

// Check server status on load
checkServerStatus();

// Event Listeners
loginBtn.addEventListener('click', handleLogin);
passwordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleLogin();
});
logoutBtn.addEventListener('click', handleLogout);

if (killSwitchToggle) {
    killSwitchToggle.addEventListener('change', handleKillSwitch);
}

// Attach click handlers to all control buttons
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.control-btn');
    if (btn && !btn.disabled) {
        handleControlClick(btn);
    }
});

// Check server status via HTTP
async function checkServerStatus() {
    try {
        const response = await fetch(`${WS_URL.replace('ws://', 'http://').replace('wss://', 'https://')}/api/status`);
        const data = await response.json();
        
        if (data.server === 'running') {
            serverStatus.textContent = 'Online';
            serverStatus.className = 'status-indicator online';
        }
    } catch (error) {
        serverStatus.textContent = 'Offline';
        serverStatus.className = 'status-indicator offline';
    }
}

// Handle Login
function handleLogin() {
    const password = passwordInput.value.trim();
    const role = document.querySelector('input[name="role"]:checked').value;
    
    if (!password) {
        showLoginError('Please enter a password');
        return;
    }
    
    loginBtn.disabled = true;
    loginBtn.textContent = 'Connecting...';
    loginError.textContent = '';
    
    connectWebSocket(password, role);
}

// Connect to WebSocket
function connectWebSocket(password, role) {
    try {
        ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            updateConnectionStatus(true);
            
            // Send authentication
            ws.send(JSON.stringify({
                type: 'auth',
                password: password,
                role: role
            }));
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleServerMessage(data);
            } catch (error) {
                console.error('Failed to parse message:', error);
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };
        
        ws.onclose = () => {
            console.log('WebSocket disconnected');
            updateConnectionStatus(false);
            
            if (isAuthenticated && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttempts++;
                addActivityMessage(`Connection lost. Reconnecting... (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
                setTimeout(() => {
                    const savedPassword = passwordInput.value;
                    const savedRole = isTeacher ? 'teacher' : 'student';
                    connectWebSocket(savedPassword, savedRole);
                }, 3000);
            }
        };
        
    } catch (error) {
        console.error('Failed to connect:', error);
        showLoginError('Failed to connect to server');
        loginBtn.disabled = false;
        loginBtn.textContent = 'Enter Classroom';
    }
}

// Handle Server Messages
function handleServerMessage(data) {
    switch (data.type) {
        case 'auth_success':
            handleAuthSuccess(data.role);
            break;
            
        case 'auth_failed':
            handleAuthFailed(data.message);
            break;
            
        case 'state_update':
            updateState(data);
            break;
            
        case 'kill_switch_update':
            updateKillSwitch(data.enabled);
            break;
            
        case 'command_success':
            addActivityMessage(data.message, 'success');
            break;
            
        case 'filter_toggled':
            addActivityMessage(`${data.filterName} ${data.enabled ? 'enabled' : 'disabled'}`, 'info');
            break;
            
        case 'scene_changed':
            addActivityMessage(`Scene changed to ${data.sceneName}`, 'info');
            break;
            
        case 'error':
            addActivityMessage(data.message, 'error');
            break;
            
        case 'filters_list':
        case 'scenes_list':
            // Handle configuration data
            console.log('Received config:', data);
            break;
    }
}

// Handle Authentication Success
function handleAuthSuccess(role) {
    isAuthenticated = true;
    isTeacher = role === 'teacher';
    reconnectAttempts = 0;
    
    loginContainer.style.display = 'none';
    controlPanel.style.display = 'block';
    
    roleBadge.textContent = isTeacher ? 'Teacher' : 'Student';
    roleBadge.style.background = isTeacher ? '#ef4444' : '#4f46e5';
    
    if (isTeacher) {
        teacherControls.style.display = 'block';
    } else {
        teacherControls.style.display = 'none';
    }
    
    addActivityMessage(`Welcome! You are logged in as ${role}.`, 'success');
}

// Handle Authentication Failed
function handleAuthFailed(message) {
    showLoginError(message || 'Invalid password');
    loginBtn.disabled = false;
    loginBtn.textContent = 'Enter Classroom';
    
    if (ws) {
        ws.close();
        ws = null;
    }
}

// Show Login Error
function showLoginError(message) {
    loginError.textContent = message;
    passwordInput.classList.add('error');
    setTimeout(() => {
        passwordInput.classList.remove('error');
    }, 3000);
}

// Handle Logout
function handleLogout() {
    if (ws) {
        ws.close();
        ws = null;
    }
    
    isAuthenticated = false;
    isTeacher = false;
    reconnectAttempts = 0;
    
    loginContainer.style.display = 'block';
    controlPanel.style.display = 'none';
    passwordInput.value = '';
    loginError.textContent = '';
    
    // Clear activity feed
    activityFeed.innerHTML = '<p class="feed-empty">Waiting for activities...</p>';
}

// Update Connection Status
function updateConnectionStatus(connected) {
    wsStatus.className = 'status-dot ' + (connected ? 'connected' : 'disconnected');
}

// Update State
function updateState(state) {
    if (state.obsConnected !== undefined) {
        obsStatus.className = 'status-dot ' + (state.obsConnected ? 'connected' : 'disconnected');
    }
    
    if (state.killSwitch !== undefined) {
        updateKillSwitch(state.killSwitch);
    }
}

// Update Kill Switch
function updateKillSwitch(enabled) {
    killSwitchActive = enabled;
    
    if (killSwitchToggle) {
        killSwitchToggle.checked = enabled;
    }
    
    if (killSwitchLabel) {
        killSwitchLabel.textContent = enabled ? 'Student Controls DISABLED' : 'Student Controls Active';
        killSwitchLabel.className = 'kill-switch-status' + (enabled ? ' active' : '');
    }
    
    // Update student view
    if (!isTeacher) {
        killSwitchMessage.style.display = enabled ? 'block' : 'none';
        
        // Disable all control buttons
        const controlButtons = document.querySelectorAll('.control-btn');
        controlButtons.forEach(btn => {
            btn.disabled = enabled;
        });
    }
}

// Handle Kill Switch Toggle
function handleKillSwitch() {
    if (!isTeacher) return;
    
    const enabled = killSwitchToggle.checked;
    
    sendCommand({
        type: 'kill_switch',
        enabled: enabled
    });
    
    addActivityMessage(`Kill switch ${enabled ? 'ACTIVATED' : 'deactivated'}`, enabled ? 'error' : 'success');
}

// Handle Control Button Click
function handleControlClick(btn) {
    if (killSwitchActive && !isTeacher) {
        addActivityMessage('Controls are currently disabled', 'error');
        return;
    }
    
    const command = btn.dataset.command;
    const params = {};
    
    // Extract parameters from data attributes
    if (btn.dataset.source) params.sourceName = btn.dataset.source;
    if (btn.dataset.filter) params.filterName = btn.dataset.filter;
    if (btn.dataset.scene) params.sceneName = btn.dataset.scene;
    
    // Visual feedback
    btn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        btn.style.transform = '';
    }, 200);
    
    sendCommand({
        type: 'obs_command',
        command: command,
        params: params
    });
}

// Send Command to Server
function sendCommand(command) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        addActivityMessage('Not connected to server', 'error');
        return;
    }
    
    try {
        ws.send(JSON.stringify(command));
    } catch (error) {
        console.error('Failed to send command:', error);
        addActivityMessage('Failed to send command', 'error');
    }
}

// Add Activity Message
function addActivityMessage(message, type = 'info') {
    // Remove empty placeholder if exists
    const emptyMsg = activityFeed.querySelector('.feed-empty');
    if (emptyMsg) {
        emptyMsg.remove();
    }
    
    const item = document.createElement('div');
    item.className = 'feed-item';
    
    const messageSpan = document.createElement('span');
    messageSpan.className = 'feed-item-message';
    
    // Add icon based on type
    const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ';
    messageSpan.textContent = `${icon} ${message}`;
    
    if (type === 'error') {
        messageSpan.style.color = '#ef4444';
    } else if (type === 'success') {
        messageSpan.style.color = '#10b981';
    }
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'feed-item-time';
    timeSpan.textContent = new Date().toLocaleTimeString();
    
    item.appendChild(messageSpan);
    item.appendChild(timeSpan);
    
    activityFeed.insertBefore(item, activityFeed.firstChild);
    
    // Keep only last 50 items
    while (activityFeed.children.length > 50) {
        activityFeed.removeChild(activityFeed.lastChild);
    }
}

// Configuration Panel (Teacher only)
const refreshConfigBtn = document.getElementById('refresh-config-btn');
const showConfigBtn = document.getElementById('show-config-btn');
const configEditor = document.getElementById('config-editor');

if (refreshConfigBtn) {
    refreshConfigBtn.addEventListener('click', () => {
        if (isTeacher) {
            addActivityMessage('Refreshing configuration...', 'info');
            // Request scenes and filters
            sendCommand({
                type: 'obs_command',
                command: 'get_scenes',
                params: {}
            });
        }
    });
}

if (showConfigBtn) {
    showConfigBtn.addEventListener('click', () => {
        if (configEditor) {
            configEditor.style.display = configEditor.style.display === 'none' ? 'block' : 'none';
        }
    });
}

// Allow configuration of server URL
function configureServerURL() {
    const url = prompt('Enter your server URL (e.g., http://yourserver.com:3000):', localStorage.getItem('serverURL') || '');
    if (url) {
        localStorage.setItem('serverURL', url);
        alert('Server URL configured. Please refresh the page.');
    }
}

// Expose configuration function to console
window.configureServerURL = configureServerURL;

console.log('Classroom Control Panel loaded');
console.log('To configure a custom server URL, run: configureServerURL()');
