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

# 履歴保存機能
def save_history():
    filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(st.session_state["messages"], f, ensure_ascii=False, indent=4)
    st.success(f"履歴が保存されました: {filename}")

# 履歴ロード機能
def load_history():
    try:
        with open("chat_history.json", "r", encoding="utf-8") as f:
            st.session_state["messages"] = json.load(f)
        st.success("以前の履歴を読み込みました。")
    except FileNotFoundError:
        st.warning("保存された履歴が見つかりませんでした。")

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
        "この視点をさらに広げるにはどんな質問が有効ですか？",
        "次にどのような行動を取るべきですか？",
        "他者の意見を取り入れるならどうしますか？"
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

# シミュレーション機能
def interactive_simulation():
    st.write("### インタラクティブシミュレーション")
    scenario = random.choice([
        "チームでの意見交換を円滑に進める方法を考える",
        "新しいプロジェクトの計画を立てる",
        "お客さまからのフィードバックに対応する",
        "経営陣向けの説明を円滑に進める方法を考える",
        "対立する意見を持つ人々の対立状態を解消する"
    ])
    st.write(f"シナリオ: {scenario}")
    user_action = st.text_input("この状況でどう対応しますか？")

    if user_action:
        st.write("🤖 コーチのフィードバック: よい視点です。さらに考えるべきポイントは...")

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

    # パーソナライズ提案
    if progress["third_learning"] > 3:
        st.write("おすすめの提案: 高度なケーススタディ")
        st.write("リンク: [ケーススタディの例](https://example.com/case-study)")
    elif progress["second_learning"] > 3:
        st.write("おすすめの提案: 思考パターンを深めるための読書")
        st.write("リンク: [関連書籍](https://example.com/books)")
    elif progress["first_learning"] > 3:
        st.write("おすすめの提案: 新しいスキルを学ぶためのオンライン講座")
        st.write("リンク: [オンライン講座](https://example.com/online-course)")
    else:
        st.write("おすすめの提案: 基礎知識を復習するための教材")
        st.write("リンク: [基礎教材](https://example.com/basic-material)")

    # Reflectionノート
    st.write("#### Reflectionノート")
    reflection = st.text_area("提案を受けて考えたことを記録してください:")
    if st.button("Reflectionを保存"):
        with open("reflection_notes.json", "a", encoding="utf-8") as f:
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "reflection": reflection
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        st.success("Reflectionが保存されました！")

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
st.title("AI Coach べいとそん: 学びの段階・シミュレーション・次のステップに向けたおすすめの提案")

st.text_area("今の気持ち", key="feeling", height=100, placeholder="例: 最近落ち込んでいる")
st.text_area("学びたいこと", key="learning_goal", height=100, placeholder="例: チームでのコミュニケーションスキルを向上させたい")

if st.button("送信", on_click=communicate):
    save_history()

if st.button("履歴を読み込む"):
    load_history()

if st.session_state["messages"]:
    messages = st.session_state["messages"]
    for message in reversed(messages[1:]):
        timestamp = message.get("timestamp", "")
        speaker = "🙂" if message["role"] == "user" else "🤖"
        st.write(f"{speaker} ({timestamp}): {message['content']}")

# サマリー表示
if st.button("学びの段階を見える化する"):
    visualize_progress()

if st.button("シミュレーションにより学ぶ"):
    interactive_simulation()

if st.button("次のステップに向けたおすすめ提案を確認する"):
    personalized_recommendation()
