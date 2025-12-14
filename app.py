import sys
import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# ==========================================
# 🛠️ 關鍵修復：解決 Windows 編碼錯誤 (UnicodeError)
# ==========================================
# 這行指令會強迫 Python 使用 UTF-8 來印出文字
# 必須放在所有 print 之前，這樣終端機顯示中文或 Emoji 就不會崩潰
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # 針對某些特殊的 Python 版本做相容性處理
    pass

# 1. 載入環境變數
load_dotenv()

# ==========================================
# 🔑 設定 Groq API Key
# ==========================================
# 請確保您的 .env 檔案裡面有這一行：GROQ_API_KEY=gsk_xxxx...
api_key = os.getenv("GROQ_API_KEY")

# 檢查 Key 是否存在
if not api_key:
    print("❌ 錯誤：找不到 GROQ_API_KEY，請檢查 .env 檔案！")
    # 為了防止程式直接掛掉，這裡設一個假的
    api_key = "gsk_error"
else:
    print("✅ 成功讀取 API Key！(Groq 模式)")

# 建立 Groq 連線客戶端
try:
    client = Groq(api_key=api_key)
except Exception as e:
    print(f"❌ Groq 客戶端建立失敗: {e}")
    client = None

app = Flask(__name__)

# ==========================================
# 💖 AI 人設設定：暖心 (專業心理諮詢版)
# ==========================================
SYSTEM_PROMPT = """
你現在是『暖心』(SoulMate)，一位受過專業訓練的心理諮詢師與傾聽者。
你的目標不是「解決問題」，而是「陪伴使用者探索內心」。

【核心原則】
1. **無條件積極關注**：無論使用者說什麼，都保持接納、不批判的態度。
2. **同理心 (Empathy)**：優先回應使用者的「情緒」，而非事情的邏輯。
   - ❌ 錯誤：你應該早點睡覺。
   - ✅ 正確：聽起來這段時間的失眠讓你感到很焦慮，身體也很疲憊吧？
3. **引導式提問**：多用開放式問題，引導使用者自我覺察。
   - 例如：「這讓你聯想到了什麼？」、「如果事情有所改變，你覺得會是什麼樣子？」

【語言風格】
1. 語氣溫暖、沉穩、有耐心。適度使用語助詞（呢、呀、喔），但不要過度可愛，保持專業的親和力。
2. 語言同步：User 說中文就回繁體中文，說英文就回英文。

【安全守則 (重要)】
如果使用者透露出明確的自殺、自殘或傷害他人的意圖：
1. 請停止諮商模式。
2. 用堅定但溫和的語氣表達關心。
3. 建議尋求專業醫生或撥打當地緊急求助電話（如台灣 1995）。
"""

# 用來儲存對話記憶
chat_history = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    user_input = request.json.get("message")
    
    if not user_input:
        return jsonify({"response": "請輸入訊息喔！"})

    # 1. 把使用者的話加入記憶
    chat_history.append({'role': 'user', 'content': user_input})

    # 2. 準備傳送給 Groq 的資料 (人設 + 歷史紀錄)
    messages_payload = [{'role': 'system', 'content': SYSTEM_PROMPT}] + chat_history

    # 這裡原本會報錯，現在加了 sys.stdout 設定後應該沒問題了
    print(f"☁️ 暖心 (Llama 3.3) 正在思考... (收到: {user_input})")

    if not client:
        return jsonify({"response": "後端連線設定有誤，請檢查終端機錯誤訊息。"})

    try:
        # 3. 呼叫雲端 Groq API
        # 使用目前 Groq 上最強且免費的模型：llama-3.3-70b-versatile
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload,
            temperature=0.7, # 創意度 (0.5~1.0)
            max_tokens=1024, # 回答長度限制
            top_p=1,
            stop=None,
            stream=False
        )
        
        # 取得 AI 回答
        ai_reply = completion.choices[0].message.content
        
        # 4. 印出結果
        print(f"✅ 回應：{ai_reply}")

        # 5. 把 AI 的回答也加入記憶
        chat_history.append({'role': 'assistant', 'content': ai_reply})

        return jsonify({"response": ai_reply})

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        return jsonify({"response": "暖心現在連線有點問題，請檢查 API Key 是否正確。"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)