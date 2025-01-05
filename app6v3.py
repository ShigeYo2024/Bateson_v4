import streamlit as st
import openai
import json  # 記録保存用
from textblob import TextBlob
import matplotlib.pyplot as plt
import random
from datetime import datetime  # 日付管理用

# OpenAI APIキーの設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": """あなたはグレゴリー・ベイトソンの教育モデルに基づいた教育コーチです。以下を行います：\n1. 感情状態を分析。\n2. 学習段階に応じた対話を提供。\n3. 内省を促進。"""}
    ]
if "progress" not in st.session_state:
    st.session_state["progress"] = {"zero_learning": 0, "first_learning": 0, "second_learning": 0, "third_learning": 0}
if "feeling" not in st.session_state:
    st.session_state["feeling"] = ""
if "learning_goal" not in st.session_state:
    st.session_state["learning_goal"] = ""


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

# 学習段階ごとのメッセージを生成する関数
def generate_stage_message(stage, user_input):
    if stage == "zero_learning":
        return f"あなたの基本知識を確認します: {user_input}"
    elif stage == "first_learning":
        return f"新しい方法について考えてみましょう: {user_input}"
    elif stage == "second_learning":
        return f"あなたの考え方やパターンに焦点を当てます: {user_input}"
    elif stage == "third_learning":
        return f"より大きな視点であなたの世界観を再構築してみましょう: {user_input}"

# 次に考えるべき質問の提案
def propose_next_questions():
    return [
        "この視点をさらに広げるには、どんなことを考えるのがよいですか？",
        "次にどのような行動を取るべきですか？",
        "他者の意見を取り入れるとすれば、どのような点を考慮しますか？"
    ]

# 学習進捗を更新する関数
def update_progress(stage):
    if stage in st.session_state["progress"]:
        st.session_state["progress"][stage] += 1

# 学習進捗の可視化
def visualize_progress():
    progress = st.session_state["progress"]
    stages = list(progress.keys())
    values = list(progress.values())

    plt.figure(figsize=(8, 6))
    plt.bar(stages, values, color='skyblue')
    plt.title("学習進捗の可視化")
    plt.xlabel("学習段階")
    plt.ylabel("対話数")
    st.pyplot(plt)

# 推薦エンジン
def personalized_recommendation():
    st.write("### あなたにおすすめの提案")
    progress = st.session_state["progress"]

    # 進捗グラフを表示
    st.write("#### あなたの進捗状況")
    stages = list(progress.keys())
    values = list(progress.values())
    fig, ax = plt.subplots()
    ax.bar(stages, values, color="skyblue")
    ax.set_title("進捗状況")
    ax.set_xlabel("学習段階")
    ax.set_ylabel("対話数")
    st.pyplot(fig)


# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    # ユーザーのメッセージを追加
    user_message = {
        "role": "user", 
        "content": st.session_state["feeling"] + " " + st.session_state["learning_goal"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(user_message)

    # 感情分析の結果を追加
    emotion = analyze_emotion(user_message["content"])
    messages.append({"role": "assistant", "content": f"感情分析結果: {emotion}"})

    # 学習段階の判定 (仮のロジック)
    if "基礎" in user_message["content"]:
        stage = "zero_learning"
    elif "方法" in user_message["content"]:
        stage = "first_learning"
    elif "パターン" in user_message["content"]:
        stage = "second_learning"
    else:
        stage = "third_learning"

    # 学習進捗を更新
    update_progress(stage)

    # 学習段階に基づくメッセージ生成
    stage_message = generate_stage_message(stage, user_message["content"])
    messages.append({"role": "assistant", "content": stage_message})

    # 次の候補質問を提案
    next_questions = propose_next_questions()
    messages.append({"role": "assistant", "content": f"次に考えるべき点: {', '.join(next_questions)}"})

    # OpenAI API呼び出し
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )
        bot_message = response["choices"][0]["message"]
        messages.append(bot_message)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

    # 入力フィールドをクリア
    st.session_state["feeling"] = ""
    st.session_state["learning_goal"] = ""

# ユーザーインターフェイスの構築
st.title("AI Coach: 感情分析・学びたいことの整理・次のステップに向けて")

st.text_area("今の気持ち", key="feeling", height=100, placeholder="例: チーム内の対立を和らげてストレスレベルを下げたい")
st.text_area("学びたいこと", key="learning_goal", height=100, placeholder="例: 歴史上の人物で似たような状況に置かれた人の課題克服方法を学びたい")

if st.button("送信", on_click=communicate):
    communicate()
    save_history()

if st.session_state["messages"]:
    messages = st.session_state["messages"]
    for message in reversed(messages[1:]):
        timestamp = message.get("timestamp", "")
        speaker = "🙂" if message["role"] == "user" else "コーチから"
        st.write(f"{speaker} ({timestamp}): {message['content']}")

# サマリー表示
if st.button("学びの段階を見える化する"):
    visualize_progress()

