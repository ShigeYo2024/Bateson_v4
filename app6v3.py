import streamlit as st
import openai
import json
from datetime import datetime
from textblob import TextBlob
import os  # ファイルパス管理用

# OpenAI APIキーの設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# 履歴保存ディレクトリ
HISTORY_DIR = "chat_histories"

# 必要なディレクトリを作成
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 履歴保存機能
def save_history():
    filename = os.path.join(
        HISTORY_DIR, f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(st.session_state["messages"], f, ensure_ascii=False, indent=4)
    st.success(f"履歴が保存されました: {filename}")

# 履歴ロード機能
def load_history():
    uploaded_file = st.file_uploader("履歴ファイルを選択してください", type="json")
    if uploaded_file is not None:
        try:
            st.session_state["messages"] = json.load(uploaded_file)
            st.success("履歴を読み込みました。")
        except Exception as e:
            st.error(f"履歴の読み込みに失敗しました: {e}")

# 感情分析関数
def analyze_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.5:
        return "ポジティブ"
    elif polarity < -0.5:
        return "ネガティブ"
    else:
        return "ニュートラル"

# チャットボットとのやり取りを記録
def communicate():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feeling = st.session_state.get("feeling", "")
    learning_goal = st.session_state.get("learning_goal", "")

    user_message = {
        "role": "user",
        "timestamp": timestamp,
        "feeling": feeling,
        "learning_goal": learning_goal,
    }
    st.session_state["messages"].append(user_message)

    # 感情分析
    emotion = analyze_emotion(feeling)
    bot_message = {
        "role": "assistant",
        "timestamp": timestamp,
        "content": f"感情分析結果: {emotion}\n学びたいこと: {learning_goal}",
    }
    st.session_state["messages"].append(bot_message)

    st.session_state["feeling"] = ""
    st.session_state["learning_goal"] = ""

# UI構築
st.title("AI Coach べいとそん")

st.text_area("今の気持ち", key="feeling", height=100, placeholder="例: 最近落ち込んでいる")
st.text_area("学びたいこと", key="learning_goal", height=100, placeholder="例: チームでのコミュニケーションスキルを向上させたい")

if st.button("送信", on_click=communicate):
    save_history()

if st.button("履歴を読み込む"):
    load_history()

if st.session_state["messages"]:
    for message in reversed(st.session_state["messages"]):
        timestamp = message.get("timestamp", "")
        role = "🙂" if message["role"] == "user" else "🤖"
        feeling = message.get("feeling", "")
        learning_goal = message.get("learning_goal", "")
        content = message.get("content", "")
        st.write(f"{role} ({timestamp}): {feeling} {learning_goal} {content}")
