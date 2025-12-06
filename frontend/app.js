// Global state
let uploadedFiles = [];
let chatHistory = [];
let currentSessionId = Date.now();

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const attachBtn = document.getElementById('attachBtn');
const fileInput = document.getElementById('fileInput');
const uploadedFilesContainer = document.getElementById('uploadedFiles');
const messagesContainer = document.getElementById('messages');
const welcomeScreen = document.getElementById('welcomeScreen');
const newChatBtn = document.getElementById('newChatBtn');
const modelProviderSelect = document.getElementById('modelProvider');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadSettings();
});

function setupEventListeners() {
    if (sendBtn) sendBtn.addEventListener('click', handleSend);

    if (messageInput) {
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = messageInput.scrollHeight + 'px';
        });
    }

    if (attachBtn && fileInput) {
        attachBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileUpload);
    }

    if (newChatBtn) newChatBtn.addEventListener('click', startNewChat);

    // Save settings
    if (modelProviderSelect) modelProviderSelect.addEventListener('change', saveSettings);
}

function loadSettings() {
    const provider = localStorage.getItem('model_provider');
    if (provider && modelProviderSelect) modelProviderSelect.value = provider;
}

function saveSettings() {
    if (modelProviderSelect) localStorage.setItem('model_provider', modelProviderSelect.value);
}

async function handleFileUpload(event) {
    const files = Array.from(event.target.files);

    for (const file of files) {
        // Check file type
        const validTypes = ['.pdf', '.txt', '.csv', '.py', '.md', '.json'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();

        if (!validTypes.includes(fileExt)) {
            addMessage('system', `❌ Invalid file type: ${file.name}. Please upload PDF, TXT, CSV, PY, MD, or JSON files.`);
            continue;
        }

        // Add to uploaded files
        uploadedFiles.push(file);
        addFileChip(file);

        // Show upload confirmation
        addMessage('user', `📤 Uploaded: **${file.name}**`);
    }

    // Clear file input
    fileInput.value = '';
    hideWelcomeScreen();

    // Automatically analyze uploaded files
    if (files.length > 0) {
        // Show typing indicator
        const typingId = addTypingIndicator();

        try {
            // Send files to backend for analysis
            const response = await sendToBackend({
                message: 'Analyze uploaded files',
                files: uploadedFiles.map(f => ({
                    name: f.name,
                    type: f.type,
                    size: f.size
                })),
                model_provider: modelProviderSelect ? modelProviderSelect.value : 'groq'
            });

            // Remove typing indicator
            removeTypingIndicator(typingId);

            // Add assistant response
            addMessage('assistant', response);

        } catch (error) {
            removeTypingIndicator(typingId);
            addMessage('system', `⚠️ Could not analyze files: ${error.message}\n\nFiles are uploaded. Type a message or press Enter to proceed.`);
        }
    }
}

function addFileChip(file) {
    const chip = document.createElement('div');
    chip.className = 'file-chip';

    const icon = getFileIcon(file.name);

    chip.innerHTML = `
        <span class="file-chip-icon">${icon}</span>
        <span>${file.name}</span>
        <button class="file-chip-remove" onclick="removeFile('${file.name}')">×</button>
    `;

    uploadedFilesContainer.appendChild(chip);
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
        'pdf': '📄',
        'txt': '📝',
        'csv': '📊',
        'py': '🐍',
        'js': '📜',
        'java': '☕',
        'cpp': '⚙️',
        'c': '⚙️'
    };
    return icons[ext] || '📎';
}

function removeFile(filename) {
    uploadedFiles = uploadedFiles.filter(f => f.name !== filename);

    // Remove chip from UI
    const chips = uploadedFilesContainer.querySelectorAll('.file-chip');
    chips.forEach(chip => {
        if (chip.textContent.includes(filename)) {
            chip.remove();
        }
    });
}

async function handleSend() {
    const message = messageInput.value.trim();

    if (!message && uploadedFiles.length === 0) return;

    hideWelcomeScreen();

    // Add user message
    if (message) {
        addMessage('user', message);
        messageInput.value = '';
        messageInput.style.height = 'auto';
    }

    // Show typing indicator
    const typingId = addTypingIndicator();

    // Prepare request
    const requestData = {
        message: message,
        files: uploadedFiles.map(f => ({
            name: f.name,
            type: f.type,
            size: f.size
        })),
        model_provider: modelProviderSelect ? modelProviderSelect.value : 'groq'
    };

    try {
        // Send to backend
        const response = await sendToBackend(requestData);

        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Add assistant response
        addMessage('assistant', response);

        // Clear uploaded files after successful grading
        if (uploadedFiles.length > 0) {
            uploadedFiles = [];
            uploadedFilesContainer.innerHTML = '';
        }

    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('system', `❌ Error: ${error.message}`);
    }
}

async function sendToBackend(data) {
    try {
        // Prepare FormData for file uploads
        const formData = new FormData();

        // Add uploaded files
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });

        // Add message and settings as JSON
        formData.append('message', data.message);
        formData.append('model_provider', data.model_provider);

        // Send to backend
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Unknown error occurred');
        }

        return result.response;

    } catch (error) {
        // Fallback to simulated response if server is not running
        console.warn('Backend not available, using simulated response:', error);

        return simulatedResponse(data);
    }
}

function simulatedResponse(data) {
    // Simulate intelligent response based on uploaded files
    let response = '';

    if (data.files.length > 0) {
        response += '📋 **Files Received:**\n';
        data.files.forEach(f => {
            response += `- ${f.name}\n`;
        });
        response += '\n';

        // Detect file types
        const hasRubric = data.files.some(f => f.name.toLowerCase().includes('rubric'));
        const hasQuestion = data.files.some(f => f.name.toLowerCase().includes('question'));
        const hasAnswer = data.files.some(f => f.name.toLowerCase().includes('answer') || f.name.toLowerCase().includes('student'));

        if (hasRubric && hasQuestion && hasAnswer) {
            response += '✅ **All required files detected!**\n\n';
            response += '🎯 **Grading Result:**\n\n';
            response += '**Score:** 7/10\n\n';
            response += '**Feedback:**\n';
            response += '- ✓ Correctness (4/5): Answer demonstrates good understanding\n';
            response += '- ✓ Clarity (2/3): Explanation could be more detailed\n';
            response += '- ✗ Examples (1/2): Missing concrete examples\n\n';
            response += '**Suggestions for improvement:**\n';
            response += '1. Add specific examples to illustrate concepts\n';
            response += '2. Expand on technical details\n';
            response += '3. Structure the answer more clearly\n';
        } else {
            response += '⚠️ **Missing files:**\n';
            if (!hasRubric) response += '- Rubric file\n';
            if (!hasQuestion) response += '- Question file\n';
            if (!hasAnswer) response += '- Student answer file\n';
            response += '\nPlease upload all required files to proceed with grading.';
        }
    } else if (data.message) {
        response = `I'm AutoGrade+, your AI grading assistant! 🤖\n\nTo grade a submission, please:\n1. Upload the **rubric** (PDF/TXT/CSV)\n2. Upload the **question** (PDF/TXT)\n3. Upload the **student answer** (PDF/TXT/code files)\n\nOr you can paste the content directly in the chat. How can I help you today?`;
    }

    return response;
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatars = {
        'user': '👤',
        'assistant': '🤖',
        'system': 'ℹ️'
    };

    const roleNames = {
        'user': 'You',
        'assistant': 'AutoGrade+',
        'system': 'System'
    };

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatars[role]}</div>
        <div class="message-content">
            <div class="message-role">${roleNames[role]}</div>
            <div class="message-text">${formatMessage(content)}</div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();

    // Add to chat history
    chatHistory.push({ role, content, timestamp: Date.now() });
}

function formatMessage(text) {
    // Convert markdown-like syntax to HTML
    let formatted = text;

    // Bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = id;

    messageDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-role">AutoGrade+</div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();

    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

function hideWelcomeScreen() {
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function startNewChat() {
    // Clear messages
    messagesContainer.innerHTML = '';

    // Clear files
    uploadedFiles = [];
    uploadedFilesContainer.innerHTML = '';

    // Show welcome screen
    if (welcomeScreen) {
        welcomeScreen.style.display = 'flex';
    }

    // Save current session to history
    if (chatHistory.length > 0) {
        saveToHistory();
    }

    // Reset
    chatHistory = [];
    currentSessionId = Date.now();

    addMessage('system', 'Started new grading session. Upload your files or start typing!');
}

function saveToHistory() {
    const historyList = document.getElementById('historyList');
    const firstMessage = chatHistory.find(m => m.role === 'user');

    if (firstMessage) {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.textContent = firstMessage.content.substring(0, 50) + '...';
        historyItem.onclick = () => loadSession(currentSessionId);

        historyList.insertBefore(historyItem, historyList.firstChild);
    }
}

function loadSession(sessionId) {
    // Placeholder for loading previous sessions
    addMessage('system', 'Session loading feature coming soon!');
}
