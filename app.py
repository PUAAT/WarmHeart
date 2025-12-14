import sys
import os
import asyncio
import base64
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import edge_tts
from langdetect import detect # 導入語言偵測功能

# ==========================================
# 🛠️ 基礎設定
# ==========================================
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    api_key = "gsk_error"
    print("❌ 警告：未設定 GROQ_API_KEY")

try:
    client = Groq(api_key=api_key)
except:
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

chat_history = []

# ==========================================
# 🔊 智慧語音生成 (自動切換口音)
# ==========================================
async def generate_voice_audio(text):
    try:
        # 1. 偵測 AI 回答的是哪國語言
        lang = detect(text)
        print(f"🌍 偵測語言: {lang}")
    except:
        lang = "zh-tw" # 偵測失敗就預設中文

    # 2. 根據語言選擇最適合的聲音
    if lang == "en":
        voice = "en-US-AriaNeural"      # 英文 (Aria, 溫柔美聲)
    elif lang == "ja":
        voice = "ja-JP-NanamiNeural"    # 日文 (Nanami, 甜美聲)
    elif lang == "ko":
        voice = "ko-KR-SunHiNeural"     # 韓文 (SunHi, 溫柔聲)
    else:
        voice = "zh-CN-XiaoxiaoNeural"  # 中文 (曉曉, 預設)

    print(f"🎙️ 使用聲音模型: {voice}")

    communicate = edge_tts.Communicate(text, voice)
    
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
            
    return base64.b64encode(audio_data).decode('utf-8')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    user_input = request.json.get("message")
    
    if not user_input:
        return jsonify({"response": "請輸入訊息喔！"})

    chat_history.append({'role': 'user', 'content': user_input})
    messages_payload = [{'role': 'system', 'content': SYSTEM_PROMPT}] + chat_history

    print(f"☁️ 暖心正在思考... (收到: {user_input})")

    try:
        # 1. 呼叫 Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload,
            temperature=0.7,
            max_tokens=1024
        )
        ai_reply = completion.choices[0].message.content
        print(f"✅ 文字回應：{ai_reply}")

        # 2. 生成語音 (會自動選聲音)
        print("🔊 正在合成語音...")
        audio_base64 = asyncio.run(generate_voice_audio(ai_reply))

        chat_history.append({'role': 'assistant', 'content': ai_reply})

        return jsonify({
            "response": ai_reply,
            "audio": audio_base64
        })

    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return jsonify({"response": "暖心現在連線有點問題。", "audio": None})

if __name__ == "__main__":
    app.run(debug=True, port=5000)





