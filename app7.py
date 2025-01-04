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
        {"role": "system", "content": """
        あなたはグレゴリー・ベイトソンの教育モデルに基づいた教育コーチです。以下を行います：
        1. 感情状態を分析。
        2. 学習段階に応じた対話を提供。
        3. 内省を促進。
        4. DX推進スキルを強化。
        5. ケースシナリオに基づくディスカッションをサポート。
        """}
    ]
if "progress" not in st.session_state:
    st.session_state["progress"] = {"zero_learning": 0, "first_learning": 0, "second_learning": 0, "third_learning": 0}

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

# 各役割の議論スタイルを反映
def ceo_contribution(context):
    return f"社長: CFOとの協議を踏まえ、{context} に関する最終決断を下します。"

def cfo_contribution(context):
    return f"CFO: 財務的な観点から、{context} の費用対効果を考えます。"

def cio_contribution(context):
    return f"CIO: システム全体の観点から、{context} の影響を評価します。"

def cro_contribution(context):
    return f"CRO: リスクの視点で、{context} の潜在的な問題を検討します。"

def nishiyama_contribution(context):
    contributions = [
        f"西山圭太: 現場でのデータ収集が不十分ではありませんか？ {context} について、現場の意見をもっと反映すべきでは？",
        f"西山圭太: このDX施策が本当に現場での運用につながると考えていますか？",
        f"西山圭太: データ活用の観点から、具体的なKPIの設計が必要です。この点をどうお考えですか？"
    ]
    return random.choice(contributions)

def tomiyama_contribution(context):
    contributions = [
        f"冨山和彦: この施策が全社的な価値を生むかどうか、十分に検討されていますか？ {context} のリスクをどう考えていますか？",
        f"冨山和彦: 部分最適ではなく全体最適を目指すべきです。この計画はその点でどのように機能しますか？",
        f"冨山和彦: 経営資源の配分を考慮し、長期的な視点でこの施策の意義を再考すべきではありませんか？"
    ]
    return random.choice(contributions)

# ケースシナリオを生成する関数
def generate_case_scenario():
    context = "データサイエンティストとエンジニアの連携不足が指摘されているプロジェクト"
    scenarios = [
        f"【成功ケース】{context}について、議論を通じて課題を解消し、プロジェクトが成功。\n"
        f"{ceo_contribution(context)} {cfo_contribution(context)} {cio_contribution(context)} {cro_contribution(context)} {nishiyama_contribution(context)} {tomiyama_contribution(context)}",

        f"【失敗ケース】{context}において連携が改善されず、プロジェクトが失敗。\n"
        f"{ceo_contribution(context)} {cfo_contribution(context)} {cio_contribution(context)} {cro_contribution(context)} {nishiyama_contribution(context)} {tomiyama_contribution(context)}",

        f"【判断がつかないケース】{context}について評価が分かれ、激しい議論が交わされる。\n"
        f"{ceo_contribution(context)} {cfo_contribution(context)} {cio_contribution(context)} {cro_contribution(context)} {nishiyama_contribution(context)} {tomiyama_contribution(context)}"
    ]
    return random.choice(scenarios)

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

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    # ユーザーのメッセージを追加
    user_message = {
        "role": "user", 
        "content": st.session_state["user_input"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(user_message)

    # 感情分析の結果を追加
    emotion = analyze_emotion(st.session_state["user_input"])
    messages.append({"role": "assistant", "content": f"感情分析結果: {emotion}"})

    # 学習段階の判定 (仮のロジック)
    if "基礎" in st.session_state["user_input"]:
        stage = "zero_learning"
    elif "方法" in st.session_state["user_input"]:
        stage = "first_learning"
    elif "パターン" in st.session_state["user_input"]:
        stage = "second_learning"
    else:
        stage = "third_learning"

    # 学習進捗を更新
    update_progress(stage)

    # 学習段階に基づくメッセージ生成
    stage_message = generate_stage_message(stage, st.session_state["user_input"])
    messages.append({"role": "assistant", "content": stage_message})

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

    st.session_state["user_input"] = ""

# ユーザーインターフェイスの構築
st.title("AI Coach べいとそん: 学びの段階・シミュレーション・次のステップに向けたおすすめの提案")

st.session_state["feeling"] = ""
st.session_state["learning_goal"] = ""
st.text_area("今の気持ち", key="feeling", height=100, placeholder="例: 最近落ち込んでいる")
st.text_area("学びたいこと", key="learning_goal", height=100, placeholder="例: チームでのコミュニケーションスキルを向上させたい")
st.session_state["user_input"] = st.session_state.get("feeling", "") + " " + st.session_state.get("learning_goal", "")

if st.button("送信", on_click=communicate):
    pass

if st.button("ケースシナリオを生成する"):
    st.write(f"シナリオ: {generate_case_scenario()}")

if st.button("学びの段階を見える化する"):
    visualize_progress()
