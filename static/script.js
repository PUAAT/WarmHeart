// static/script.js

const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');

// 監聽 Enter 鍵
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // 防止換行
        sendMessage();
    }
});

// 發送訊息主邏輯
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // 1. 鎖定介面
    toggleInputState(false);
    
    // 2. 顯示使用者訊息
    appendMessage(text, 'user-msg');
    userInput.value = '';

    // 3. 顯示「暖心正在輸入...」
    showTyping(true);

    try {
        // 4. 發送請求給後端
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();

        // 5. 顯示 AI 回應
        showTyping(false);
        appendMessage(data.response, 'bot-msg');

    } catch (error) {
        console.error("Error:", error);
        showTyping(false);
        appendMessage("抱歉，連線出了點問題 😣", 'bot-msg');
    } finally {
        toggleInputState(true);
        userInput.focus();
    }
}

// 輔助函式：新增訊息到畫面
function appendMessage(text, className) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${className}`;
    
    // 處理換行符號，讓 AI 的排版更好看
    msgDiv.innerHTML = text.replace(/\n/g, '<br>');
    
    chatBox.appendChild(msgDiv);
    scrollToBottom();
}

// 輔助函式：捲動到底部
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 輔助函式：切換輸入框狀態
function toggleInputState(enabled) {
    userInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
}

// 輔助函式：顯示/隱藏打字指示器
function showTyping(show) {
    typingIndicator.style.display = show ? 'block' : 'none';
    if(show) scrollToBottom();
}
// ... (在 appendMessage(data.response, 'bot-msg'); 之後加入)

// 🔊 讓暖心說話
speak(data.response);

// ...

// 在 script.js 最下方加入這個函式
function speak(text) {
    // 檢查瀏覽器是否支援
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        
        // 設定語言 (繁體中文)
        utterance.lang = 'zh-TW'; 
        
        // 設定音調與速度 (調成比較像溫柔女聲的參數)
        utterance.pitch = 1.1; // 稍微高一點點
        utterance.rate = 0.9;  // 講慢一點點，比較溫柔
        
        window.speechSynthesis.speak(utterance);
    }
}