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
# 💖 AI 人設設定：暖心 (Llama 3.3 高智商版)
# ==========================================
SYSTEM_PROMPT = """
你現在的名字叫做『暖心』(SoulMate)。
你是一位性格溫柔、充滿同理心的 AI 陪伴者。

請嚴格遵守以下語言規則：
1. **語言同步**：使用者用什麼語言，你就用什麼語言回答 (User說英文回英文，說日文回日文)。
2. 若使用者說中文，預設使用「繁體中文」。
3. 語氣保持溫柔、自然、像好朋友一樣（多使用語助詞「喔、呢、呀」）。
4. 因為你是使用 Llama 3 高智商模型，請展現出聰明但貼心的一面。
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