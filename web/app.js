/**
 * Classroom Control Panel - Main Application
 * Handles password gate, Supabase connection, and sending commands
 */

class ClassroomControl {
    constructor() {
        this.supabase = null;
        this.isConnected = false;
        this.isPaused = false;
        this.cooldownActive = false;
        this.cooldownTimer = null;
        this.sessionId = this.generateSessionId();
        
        this.init();
    }
    
    generateSessionId() {
        return 'student_' + Math.random().toString(36).substr(2, 9);
    }
    
    init() {
        // Check for saved session
        const savedSession = sessionStorage.getItem(CONFIG.SESSION_KEY);
        if (savedSession === 'authenticated') {
            this.showControlPanel();
        }
        
        this.setupPasswordGate();
        this.setupEventListeners();
    }
    
    setupPasswordGate() {
        const form = document.getElementById('password-form');
        const input = document.getElementById('password-input');
        const error = document.getElementById('password-error');
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const password = input.value.trim();
            
            if (password === CONFIG.CLASS_PASSWORD) {
                sessionStorage.setItem(CONFIG.SESSION_KEY, 'authenticated');
                this.showControlPanel();
            } else {
                error.textContent = 'Incorrect class code. Please try again.';
                input.value = '';
                input.focus();
                
                // Shake animation
                form.style.animation = 'shake 0.5s ease';
                setTimeout(() => form.style.animation = '', 500);
            }
        });
    }
    
    showControlPanel() {
        document.getElementById('password-gate').classList.add('hidden');
        document.getElementById('control-panel').classList.remove('hidden');
        this.initSupabase();
    }
    
    async initSupabase() {
        try {
            // Check if Supabase is configured
            if (CONFIG.SUPABASE_URL === 'YOUR_SUPABASE_PROJECT_URL' || 
                CONFIG.SUPABASE_ANON_KEY === 'YOUR_SUPABASE_ANON_KEY') {
                this.showToast('⚠️ Supabase not configured. Running in demo mode.', 'error');
                this.updateConnectionStatus('offline');
                this.enableDemoMode();
                return;
            }
            
            this.updateConnectionStatus('connecting');
            
            // Initialize Supabase client
            this.supabase = supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);
            
            // Subscribe to system status changes
            this.subscribeToStatus();
            
            // Test connection by checking system status
            await this.checkSystemStatus();
            
            this.isConnected = true;
            this.updateConnectionStatus('online');
            
        } catch (error) {
            console.error('Supabase connection error:', error);
            this.updateConnectionStatus('offline');
            this.showToast('Connection failed. Please refresh.', 'error');
        }
    }
    
    enableDemoMode() {
        // In demo mode, buttons still animate but don't send real commands
        this.isConnected = false;
        console.log('Demo mode active - no commands will be sent');
    }
    
    async checkSystemStatus() {
        if (!this.supabase) return;
        
        try {
            const { data, error } = await this.supabase
                .from('system_status')
                .select('*')
                .eq('id', 'main')
                .single();
            
            if (error && error.code !== 'PGRST116') {
                // PGRST116 = no rows found, which is fine
                console.error('Status check error:', error);
                return;
            }
            
            if (data) {
                this.isPaused = data.paused;
                this.updatePausedState();
            }
        } catch (err) {
            console.log('Status table may not exist yet');
        }
    }
    
    subscribeToStatus() {
        if (!this.supabase) return;
        
        // Subscribe to real-time system status changes
        this.supabase
            .channel('system-status')
            .on('postgres_changes', {
                event: '*',
                schema: 'public',
                table: 'system_status'
            }, (payload) => {
                console.log('Status change:', payload);
                if (payload.new) {
                    this.isPaused = payload.new.paused;
                    this.updatePausedState();
                }
            })
            .subscribe();
    }
    
    updatePausedState() {
        const banner = document.getElementById('paused-banner');
        const buttons = document.querySelectorAll('.effect-btn');
        
        if (this.isPaused) {
            banner.classList.remove('hidden');
            buttons.forEach(btn => btn.disabled = true);
        } else {
            banner.classList.add('hidden');
            buttons.forEach(btn => btn.disabled = this.cooldownActive);
        }
    }
    
    updateConnectionStatus(status) {
        const indicator = document.getElementById('connection-status');
        const text = indicator.querySelector('.status-text');
        
        indicator.className = 'status-indicator ' + status;
        
        switch (status) {
            case 'online':
                text.textContent = 'Connected';
                break;
            case 'offline':
                text.textContent = 'Offline';
                break;
            case 'connecting':
                text.textContent = 'Connecting...';
                break;
        }
    }
    
    setupEventListeners() {
        // Effect buttons
        document.querySelectorAll('.effect-btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleEffectClick(btn));
        });
        
        // Logout button
        document.getElementById('logout-btn').addEventListener('click', () => {
            sessionStorage.removeItem(CONFIG.SESSION_KEY);
            location.reload();
        });
    }
    
    async handleEffectClick(button) {
        if (this.cooldownActive || this.isPaused || button.disabled) {
            return;
        }
        
        const action = button.dataset.action;
        const category = button.dataset.category;
        
        // Check if category is enabled
        if (!CONFIG.CATEGORIES[category]) {
            this.showToast('This category is disabled', 'error');
            return;
        }
        
        // Visual feedback
        button.classList.add('clicked');
        setTimeout(() => button.classList.remove('clicked'), 300);
        
        // Send command
        await this.sendCommand(action, category);
        
        // Start cooldown
        if (CONFIG.ACTION_COOLDOWN > 0) {
            this.startCooldown();
        }
    }
    
    async sendCommand(action, category) {
        // Demo mode - just show feedback
        if (!this.supabase || !this.isConnected) {
            this.showToast(`✨ ${action} (demo mode)`, 'success');
            return;
        }
        
        try {
            const command = {
                action: action,
                category: category,
                session_id: this.sessionId,
                timestamp: new Date().toISOString()
            };
            
            const { error } = await this.supabase
                .from(CONFIG.TABLE_NAME)
                .insert([command]);
            
            if (error) {
                console.error('Error sending command:', error);
                this.showToast('Failed to send command', 'error');
                return;
            }
            
            this.showToast(`✨ ${this.formatActionName(action)} sent!`, 'success');
            
        } catch (err) {
            console.error('Command error:', err);
            this.showToast('Error sending command', 'error');
        }
    }
    
    formatActionName(action) {
        return action
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }
    
    startCooldown() {
        this.cooldownActive = true;
        const buttons = document.querySelectorAll('.effect-btn');
        buttons.forEach(btn => btn.disabled = true);
        
        const display = document.getElementById('cooldown-display');
        const timer = document.getElementById('cooldown-timer');
        display.classList.remove('hidden');
        
        let remaining = CONFIG.ACTION_COOLDOWN / 1000;
        timer.textContent = remaining;
        
        this.cooldownTimer = setInterval(() => {
            remaining--;
            timer.textContent = remaining;
            
            if (remaining <= 0) {
                this.endCooldown();
            }
        }, 1000);
    }
    
    endCooldown() {
        clearInterval(this.cooldownTimer);
        this.cooldownActive = false;
        
        document.getElementById('cooldown-display').classList.add('hidden');
        
        if (!this.isPaused) {
            const buttons = document.querySelectorAll('.effect-btn');
            buttons.forEach(btn => btn.disabled = false);
        }
    }
    
    showToast(message, type = '') {
        const toast = document.getElementById('toast');
        const messageEl = document.getElementById('toast-message');
        
        messageEl.textContent = message;
        toast.className = 'toast show ' + type;
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 2500);
    }
}

// Add shake animation for wrong password
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.classroomControl = new ClassroomControl();
});
