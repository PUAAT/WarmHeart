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

// static/script.js

// ... (前面的變數宣告不變) ...

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    toggleInputState(false);
    appendMessage(text, 'user-msg');
    userInput.value = '';
    showTyping(true);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();

        showTyping(false);
        appendMessage(data.response, 'bot-msg');

        // 🔊 關鍵修改：如果有收到音檔，就播放出來
        if (data.audio) {
            playAudio(data.audio);
        }

    } catch (error) {
        console.error("Error:", error);
        showTyping(false);
        appendMessage("抱歉，連線出了點問題 😣", 'bot-msg');
    } finally {
        toggleInputState(true);
        userInput.focus();
    }
}

// ... (appendMessage 等其他函式不變) ...

// 🔊 新增播放音效的函式
function playAudio(base64String) {
    // 建立一個音訊物件
    const audio = new Audio("data:audio/mp3;base64," + base64String);
    
    // 設定音量
    audio.volume = 1.0;
    
    // 播放
    audio.play().catch(e => {
        console.error("播放失敗 (可能是瀏覽器阻擋自動播放):", e);
    });
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