#!/usr/bin/env node

/**
 * Simple connection test script
 * Verifies OBS WebSocket connection
 */

const OBSWebSocket = require('obs-websocket-js').default;
require('dotenv').config();

const obs = new OBSWebSocket();

const OBS_HOST = process.env.OBS_HOST || 'localhost';
const OBS_PORT = process.env.OBS_PORT || 4455;
const OBS_PASSWORD = process.env.OBS_PASSWORD || '';

console.log('\n🧪 Testing OBS Connection...\n');
console.log('Configuration:');
console.log(`  Host: ${OBS_HOST}`);
console.log(`  Port: ${OBS_PORT}`);
console.log(`  Password: ${OBS_PASSWORD ? '***' + OBS_PASSWORD.slice(-3) : '(none)'}`);
console.log('');

async function testConnection() {
    try {
        console.log('Attempting to connect...');
        await obs.connect(`ws://${OBS_HOST}:${OBS_PORT}`, OBS_PASSWORD);
        
        console.log('✅ SUCCESS! Connected to OBS WebSocket\n');
        
        // Get OBS version
        const version = await obs.call('GetVersion');
        console.log('OBS Information:');
        console.log(`  OBS Studio Version: ${version.obsVersion}`);
        console.log(`  WebSocket Version: ${version.obsWebSocketVersion}`);
        console.log('');
        
        // Get scenes
        const scenes = await obs.call('GetSceneList');
        console.log('Available Scenes:');
        scenes.scenes.forEach(scene => {
            const indicator = scene.sceneName === scenes.currentProgramSceneName ? '→' : ' ';
            console.log(`  ${indicator} ${scene.sceneName}`);
        });
        console.log('');
        
        // Try to get sources from current scene
        try {
            const sceneItems = await obs.call('GetSceneItemList', {
                sceneName: scenes.currentProgramSceneName
            });
            
            console.log(`Sources in "${scenes.currentProgramSceneName}":`);
            if (sceneItems.sceneItems && sceneItems.sceneItems.length > 0) {
                sceneItems.sceneItems.forEach(item => {
                    console.log(`  • ${item.sourceName}`);
                });
            } else {
                console.log('  (no sources found)');
            }
            console.log('');
        } catch (err) {
            console.log('Could not retrieve scene sources');
        }
        
        console.log('✅ All tests passed! OBS is ready.');
        console.log('');
        console.log('Next steps:');
        console.log('  1. Start the server: npm start');
        console.log('  2. Open http://localhost:3000');
        console.log('  3. Login with password: student123');
        console.log('');
        
        await obs.disconnect();
        process.exit(0);
        
    } catch (error) {
        console.log('❌ FAILED to connect to OBS\n');
        console.log('Error:', error.message);
        console.log('');
        console.log('Troubleshooting:');
        console.log('  1. Make sure OBS Studio is running');
        console.log('  2. Go to Tools → WebSocket Server Settings in OBS');
        console.log('  3. Check "Enable WebSocket server"');
        console.log('  4. Verify the password matches your .env file');
        console.log('  5. Verify port is 4455 (or matches your .env)');
        console.log('');
        console.log('Your .env file should have:');
        console.log('  OBS_HOST=localhost');
        console.log('  OBS_PORT=4455');
        console.log('  OBS_PASSWORD=your_obs_password');
        console.log('');
        
        process.exit(1);
    }
}

testConnection();
