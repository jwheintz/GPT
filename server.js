const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const OBSWebSocket = require('obs-websocket-js').default;
const bcrypt = require('bcryptjs');
const cors = require('cors');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// OBS WebSocket connection
const obs = new OBSWebSocket();
let isOBSConnected = false;

// Kill switch state
let killSwitchActive = false;

// Configuration
const PORT = process.env.PORT || 3000;
const OBS_HOST = process.env.OBS_HOST || 'localhost';
const OBS_PORT = process.env.OBS_PORT || 4455;
const OBS_PASSWORD = process.env.OBS_PASSWORD || '';
const TEACHER_PASSWORD_HASH = process.env.TEACHER_PASSWORD_HASH || bcrypt.hashSync('teacher123', 10);
const STUDENT_PASSWORD_HASH = process.env.STUDENT_PASSWORD_HASH || bcrypt.hashSync('student123', 10);

// Rate limiting
const rateLimitMap = new Map();
const RATE_LIMIT_WINDOW = 5000; // 5 seconds
const MAX_REQUESTS_PER_WINDOW = 10;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Connect to OBS
async function connectToOBS() {
    try {
        await obs.connect(`ws://${OBS_HOST}:${OBS_PORT}`, OBS_PASSWORD);
        isOBSConnected = true;
        console.log('✓ Connected to OBS WebSocket');
        
        // Listen for disconnection
        obs.on('ConnectionClosed', () => {
            isOBSConnected = false;
            console.log('✗ Disconnected from OBS');
            // Try to reconnect after 5 seconds
            setTimeout(connectToOBS, 5000);
        });
    } catch (error) {
        console.error('Failed to connect to OBS:', error.message);
        isOBSConnected = false;
        // Retry connection after 5 seconds
        setTimeout(connectToOBS, 5000);
    }
}

// Rate limiting check
function checkRateLimit(identifier) {
    const now = Date.now();
    const userRequests = rateLimitMap.get(identifier) || [];
    
    // Filter out old requests
    const recentRequests = userRequests.filter(time => now - time < RATE_LIMIT_WINDOW);
    
    if (recentRequests.length >= MAX_REQUESTS_PER_WINDOW) {
        return false;
    }
    
    recentRequests.push(now);
    rateLimitMap.set(identifier, recentRequests);
    return true;
}

// WebSocket connection handling
wss.on('connection', (ws, req) => {
    const clientIp = req.socket.remoteAddress;
    console.log(`New WebSocket connection from ${clientIp}`);
    
    let isAuthenticated = false;
    let isTeacher = false;
    
    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            
            // Handle authentication
            if (data.type === 'auth') {
                const password = data.password;
                const role = data.role || 'student';
                
                if (role === 'teacher' && bcrypt.compareSync(password, TEACHER_PASSWORD_HASH)) {
                    isAuthenticated = true;
                    isTeacher = true;
                    ws.send(JSON.stringify({ type: 'auth_success', role: 'teacher' }));
                    console.log(`Teacher authenticated from ${clientIp}`);
                } else if (role === 'student' && bcrypt.compareSync(password, STUDENT_PASSWORD_HASH)) {
                    isAuthenticated = true;
                    isTeacher = false;
                    ws.send(JSON.stringify({ type: 'auth_success', role: 'student' }));
                    console.log(`Student authenticated from ${clientIp}`);
                } else {
                    ws.send(JSON.stringify({ type: 'auth_failed', message: 'Invalid password' }));
                    return;
                }
                
                // Send current state
                ws.send(JSON.stringify({ 
                    type: 'state_update',
                    killSwitch: killSwitchActive,
                    obsConnected: isOBSConnected
                }));
                return;
            }
            
            // Require authentication for all other commands
            if (!isAuthenticated) {
                ws.send(JSON.stringify({ type: 'error', message: 'Not authenticated' }));
                return;
            }
            
            // Handle kill switch (teacher only)
            if (data.type === 'kill_switch') {
                if (!isTeacher) {
                    ws.send(JSON.stringify({ type: 'error', message: 'Unauthorized' }));
                    return;
                }
                killSwitchActive = data.enabled;
                console.log(`Kill switch ${killSwitchActive ? 'ACTIVATED' : 'deactivated'} by teacher`);
                
                // Broadcast to all clients
                wss.clients.forEach(client => {
                    if (client.readyState === WebSocket.OPEN) {
                        client.send(JSON.stringify({ 
                            type: 'kill_switch_update', 
                            enabled: killSwitchActive 
                        }));
                    }
                });
                return;
            }
            
            // Block student commands if kill switch is active
            if (killSwitchActive && !isTeacher) {
                ws.send(JSON.stringify({ 
                    type: 'error', 
                    message: 'Commands are currently disabled by teacher' 
                }));
                return;
            }
            
            // Rate limiting for students
            if (!isTeacher && !checkRateLimit(clientIp)) {
                ws.send(JSON.stringify({ 
                    type: 'error', 
                    message: 'Rate limit exceeded. Please wait a moment.' 
                }));
                return;
            }
            
            // Handle OBS commands
            if (data.type === 'obs_command') {
                if (!isOBSConnected) {
                    ws.send(JSON.stringify({ 
                        type: 'error', 
                        message: 'OBS is not connected' 
                    }));
                    return;
                }
                
                await handleOBSCommand(data.command, data.params, ws);
            }
            
        } catch (error) {
            console.error('WebSocket message error:', error);
            ws.send(JSON.stringify({ 
                type: 'error', 
                message: 'Invalid message format' 
            }));
        }
    });
    
    ws.on('close', () => {
        console.log(`WebSocket connection closed from ${clientIp}`);
    });
});

// Handle OBS commands
async function handleOBSCommand(command, params, ws) {
    try {
        let result;
        
        switch (command) {
            case 'toggle_filter':
                // Toggle a filter on a source
                const filterStatus = await obs.call('GetSourceFilter', {
                    sourceName: params.sourceName,
                    filterName: params.filterName
                });
                
                await obs.call('SetSourceFilterEnabled', {
                    sourceName: params.sourceName,
                    filterName: params.filterName,
                    filterEnabled: !filterStatus.filterEnabled
                });
                
                ws.send(JSON.stringify({ 
                    type: 'command_success', 
                    message: `Filter "${params.filterName}" ${!filterStatus.filterEnabled ? 'enabled' : 'disabled'}` 
                }));
                
                // Broadcast to all clients for visual feedback
                broadcastToAll({ 
                    type: 'filter_toggled', 
                    sourceName: params.sourceName,
                    filterName: params.filterName,
                    enabled: !filterStatus.filterEnabled
                });
                break;
                
            case 'set_filter_settings':
                // Change filter settings
                await obs.call('SetSourceFilterSettings', {
                    sourceName: params.sourceName,
                    filterName: params.filterName,
                    filterSettings: params.settings
                });
                
                ws.send(JSON.stringify({ 
                    type: 'command_success', 
                    message: `Filter settings updated` 
                }));
                break;
                
            case 'trigger_scene':
                // Switch to a specific scene
                await obs.call('SetCurrentProgramScene', {
                    sceneName: params.sceneName
                });
                
                ws.send(JSON.stringify({ 
                    type: 'command_success', 
                    message: `Switched to scene "${params.sceneName}"` 
                }));
                
                broadcastToAll({ 
                    type: 'scene_changed', 
                    sceneName: params.sceneName
                });
                break;
                
            case 'toggle_source':
                // Toggle source visibility
                const itemId = await obs.call('GetSceneItemId', {
                    sceneName: params.sceneName,
                    sourceName: params.sourceName
                });
                
                const itemStatus = await obs.call('GetSceneItemEnabled', {
                    sceneName: params.sceneName,
                    sceneItemId: itemId.sceneItemId
                });
                
                await obs.call('SetSceneItemEnabled', {
                    sceneName: params.sceneName,
                    sceneItemId: itemId.sceneItemId,
                    sceneItemEnabled: !itemStatus.sceneItemEnabled
                });
                
                ws.send(JSON.stringify({ 
                    type: 'command_success', 
                    message: `Source "${params.sourceName}" ${!itemStatus.sceneItemEnabled ? 'shown' : 'hidden'}` 
                }));
                break;
                
            case 'get_filters':
                // Get all filters for a source (teacher only)
                const filters = await obs.call('GetSourceFilterList', {
                    sourceName: params.sourceName
                });
                
                ws.send(JSON.stringify({ 
                    type: 'filters_list', 
                    filters: filters.filters 
                }));
                break;
                
            case 'get_scenes':
                // Get all scenes (teacher only)
                const scenes = await obs.call('GetSceneList');
                
                ws.send(JSON.stringify({ 
                    type: 'scenes_list', 
                    scenes: scenes.scenes 
                }));
                break;
                
            default:
                ws.send(JSON.stringify({ 
                    type: 'error', 
                    message: 'Unknown command' 
                }));
        }
        
    } catch (error) {
        console.error('OBS command error:', error);
        ws.send(JSON.stringify({ 
            type: 'error', 
            message: `OBS error: ${error.message}` 
        }));
    }
}

// Broadcast message to all connected clients
function broadcastToAll(message) {
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(message));
        }
    });
}

// API endpoint to check server status
app.get('/api/status', (req, res) => {
    res.json({
        server: 'running',
        obsConnected: isOBSConnected,
        killSwitch: killSwitchActive,
        timestamp: new Date().toISOString()
    });
});

// API endpoint to generate password hashes (for setup only)
app.post('/api/hash-password', (req, res) => {
    const { password } = req.body;
    if (!password) {
        return res.status(400).json({ error: 'Password required' });
    }
    const hash = bcrypt.hashSync(password, 10);
    res.json({ hash });
});

// Start server
server.listen(PORT, () => {
    console.log(`\n🚀 Classroom OBS Control Server`);
    console.log(`================================`);
    console.log(`Server running on port ${PORT}`);
    console.log(`\nAccess the interface at:`);
    console.log(`  Local: http://localhost:${PORT}`);
    console.log(`\nConnecting to OBS...`);
    connectToOBS();
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    if (isOBSConnected) {
        await obs.disconnect();
    }
    process.exit(0);
});
