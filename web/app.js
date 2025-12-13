// Configuration - Update this with your server URL
const SERVER_URL = 'http://localhost:8080'; // Change this to your server's public IP/domain

let authenticated = false;
let authToken = null;
let currentScene = null;
let currentSource = null;
let currentFilter = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if already authenticated (stored in sessionStorage)
    const storedAuth = sessionStorage.getItem('classroomAuth');
    if (storedAuth) {
        authToken = storedAuth;
        authenticated = true;
        showControlScreen();
        checkStatus();
    }

    // Enter key to login
    document.getElementById('password-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            login();
        }
    });
});

function showMessage(message, type = 'info') {
    const messageArea = document.getElementById('message-area');
    messageArea.textContent = message;
    messageArea.className = `message-area ${type}`;
    setTimeout(() => {
        messageArea.textContent = '';
        messageArea.className = 'message-area';
    }, 5000);
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    if (connected) {
        statusEl.textContent = '✓ Connected';
        statusEl.className = 'status-badge connected';
    } else {
        statusEl.textContent = '✗ Disconnected';
        statusEl.className = 'status-badge disconnected';
    }
}

function updateEmergencyStatus(enabled) {
    const statusEl = document.getElementById('emergency-status');
    if (enabled) {
        statusEl.classList.remove('hidden');
    } else {
        statusEl.classList.add('hidden');
    }
}

async function login() {
    const password = document.getElementById('password-input').value;
    const errorEl = document.getElementById('login-error');

    if (!password) {
        errorEl.textContent = 'Please enter a password';
        return;
    }

    try {
        const response = await fetch(`${SERVER_URL}/auth`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password: password })
        });

        const data = await response.json();

        if (data.success) {
            authenticated = true;
            authToken = password; // Store password as token for subsequent requests
            sessionStorage.setItem('classroomAuth', password);
            showControlScreen();
            checkStatus();
            errorEl.textContent = '';
        } else {
            errorEl.textContent = data.message || 'Invalid password';
            document.getElementById('password-input').value = '';
        }
    } catch (error) {
        errorEl.textContent = 'Connection error. Make sure the server is running.';
        console.error('Login error:', error);
    }
}

function showControlScreen() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('control-screen').classList.remove('hidden');
    refreshScenes();
}

async function checkStatus() {
    try {
        const response = await fetch(`${SERVER_URL}/health`);
        const data = await response.json();
        
        updateConnectionStatus(data.obs_connected);
        updateEmergencyStatus(data.emergency_stop);
        
        if (data.emergency_stop) {
            showMessage('⚠️ Emergency stop is active. All controls are disabled.', 'error');
            disableControls();
        } else {
            enableControls();
        }
    } catch (error) {
        updateConnectionStatus(false);
        showMessage('Cannot connect to server. Make sure it is running.', 'error');
        console.error('Status check error:', error);
    }
}

function disableControls() {
    document.getElementById('toggle-filter-btn').disabled = true;
    document.getElementById('enable-filter-btn').disabled = true;
    document.getElementById('disable-filter-btn').disabled = true;
    document.getElementById('scene-select').disabled = true;
    document.getElementById('source-select').disabled = true;
    document.getElementById('filter-select').disabled = true;
}

function enableControls() {
    document.getElementById('scene-select').disabled = false;
    if (currentScene) {
        document.getElementById('source-select').disabled = false;
    }
    if (currentSource) {
        document.getElementById('filter-select').disabled = false;
    }
    if (currentFilter) {
        document.getElementById('toggle-filter-btn').disabled = false;
        document.getElementById('enable-filter-btn').disabled = false;
        document.getElementById('disable-filter-btn').disabled = false;
    }
}

async function refreshScenes() {
    try {
        const response = await fetch(`${SERVER_URL}/obs/scenes`);
        const data = await response.json();

        const sceneSelect = document.getElementById('scene-select');
        sceneSelect.innerHTML = '<option value="">Select a scene...</option>';
        
        data.scenes.forEach(scene => {
            const option = document.createElement('option');
            option.value = scene;
            option.textContent = scene;
            sceneSelect.appendChild(option);
        });

        sceneSelect.addEventListener('change', function() {
            currentScene = this.value;
            if (currentScene) {
                loadSources(currentScene);
            } else {
                document.getElementById('source-select').innerHTML = '<option value="">Select a scene first</option>';
                document.getElementById('filter-select').innerHTML = '<option value="">Select a source first</option>';
                currentSource = null;
                currentFilter = null;
                disableControls();
            }
        });

        showMessage('Scenes loaded successfully', 'success');
    } catch (error) {
        showMessage('Error loading scenes: ' + error.message, 'error');
        console.error('Error loading scenes:', error);
    }
}

async function loadSources(sceneName) {
    try {
        const response = await fetch(`${SERVER_URL}/obs/sources?scene=${encodeURIComponent(sceneName)}`);
        const data = await response.json();

        const sourceSelect = document.getElementById('source-select');
        sourceSelect.innerHTML = '<option value="">Select a source...</option>';
        
        data.sources.forEach(source => {
            const option = document.createElement('option');
            option.value = source.name;
            option.textContent = source.name;
            sourceSelect.appendChild(option);
        });

        sourceSelect.addEventListener('change', function() {
            currentSource = this.value;
            if (currentSource) {
                loadFilters(currentSource);
            } else {
                document.getElementById('filter-select').innerHTML = '<option value="">Select a source first</option>';
                currentFilter = null;
                disableControls();
            }
        });

        showMessage(`Loaded ${data.sources.length} sources`, 'success');
    } catch (error) {
        showMessage('Error loading sources: ' + error.message, 'error');
        console.error('Error loading sources:', error);
    }
}

async function loadFilters(sourceName) {
    try {
        const response = await fetch(`${SERVER_URL}/obs/filters?source=${encodeURIComponent(sourceName)}`);
        const data = await response.json();

        const filterSelect = document.getElementById('filter-select');
        filterSelect.innerHTML = '<option value="">Select a filter...</option>';
        
        data.filters.forEach(filter => {
            const option = document.createElement('option');
            option.value = filter.name;
            option.textContent = `${filter.name} (${filter.type}) ${filter.enabled ? '✓' : '✗'}`;
            option.dataset.enabled = filter.enabled;
            filterSelect.appendChild(option);
        });

        filterSelect.addEventListener('change', function() {
            currentFilter = this.value;
            if (currentFilter) {
                enableControls();
            } else {
                disableControls();
            }
        });

        showMessage(`Loaded ${data.filters.length} filters`, 'success');
    } catch (error) {
        showMessage('Error loading filters: ' + error.message, 'error');
        console.error('Error loading filters:', error);
    }
}

async function toggleFilter() {
    if (!currentSource || !currentFilter) {
        showMessage('Please select a source and filter first', 'error');
        return;
    }

    try {
        const response = await fetch(`${SERVER_URL}/obs/filter/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source: currentSource,
                filter: currentFilter
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage(`Filter "${currentFilter}" ${data.enabled ? 'enabled' : 'disabled'}`, 'success');
            // Refresh filters to update status
            loadFilters(currentSource);
        } else {
            showMessage('Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showMessage('Error toggling filter: ' + error.message, 'error');
        console.error('Toggle filter error:', error);
    }
}

async function setFilter(enabled) {
    if (!currentSource || !currentFilter) {
        showMessage('Please select a source and filter first', 'error');
        return;
    }

    try {
        const response = await fetch(`${SERVER_URL}/obs/filter/set`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source: currentSource,
                filter: currentFilter,
                enabled: enabled
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage(`Filter "${currentFilter}" ${enabled ? 'enabled' : 'disabled'}`, 'success');
            // Refresh filters to update status
            loadFilters(currentSource);
        } else {
            showMessage('Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showMessage('Error setting filter: ' + error.message, 'error');
        console.error('Set filter error:', error);
    }
}

async function emergencyStop() {
    if (!confirm('Are you sure you want to activate emergency stop? This will disable all controls.')) {
        return;
    }

    if (!authToken) {
        showMessage('Authentication required', 'error');
        return;
    }

    try {
        const response = await fetch(`${SERVER_URL}/emergency/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                password: authToken
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('⚠️ EMERGENCY STOP ACTIVATED - All controls disabled', 'error');
            updateEmergencyStatus(true);
            disableControls();
            checkStatus();
        } else {
            showMessage('Error: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        showMessage('Error activating emergency stop: ' + error.message, 'error');
        console.error('Emergency stop error:', error);
    }
}

// Periodic status check
setInterval(checkStatus, 10000); // Check every 10 seconds
