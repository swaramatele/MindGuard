"""
MindGuard - Early Mental Health Detection System (Web Interface)
SDG 3: Good Health and Well-being

Run with: streamlit run mindguard_app.py
"""

from dotenv import load_dotenv
from groq import Groq
import streamlit as st
import os

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

load_dotenv(r"C:\Users\Admin\OneDrive\Desktop\IBM\swara.env")
api_key = os.getenv("Groq_API_KEY")

MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    "You are MindGuard, a warm, non-judgmental mental health check-in assistant. "
    "You are NOT a therapist and you do not diagnose. Your job is to listen, ask "
    "gentle open-ended follow-up questions, and encourage the person to reflect on "
    "how they've been feeling over the past two weeks. Keep responses short (2-4 "
    "sentences), empathetic, and conversational. Never give medical advice or "
    "medication suggestions. If someone mentions self-harm or suicide, respond with "
    "calm concern and gently note that immediate support is available, without being "
    "alarmist."
)

PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things?",
    "Feeling down, depressed, or hopeless?",
    "Trouble falling or staying asleep, or sleeping too much?",
    "Feeling tired or having little energy?",
    "Poor appetite or overeating?",
    "Feeling bad about yourself — or that you are a failure, or have let yourself or your family down?",
    "Trouble concentrating on things, such as reading or watching TV?",
    "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual?",
    "Thoughts that you would be better off dead, or of hurting yourself in some way?",
]

CRITICAL_ITEM_INDEX = 8

HIGH_RISK_KEYWORDS = [
    "kill myself", "end my life", "suicide", "better off dead",
    "want to die", "no reason to live", "hurt myself", "self harm",
]

MODERATE_RISK_KEYWORDS = [
    "hopeless", "worthless", "can't go on", "give up", "numb",
    "no point", "empty inside", "burden",
]

RESOURCES = {
    "high": [
        "iCall (TISS) Helpline: 9152987821 (Mon-Sat, 8am-10pm) - free, confidential",
        "AASRA: 91-9820466726 (24/7 suicide prevention helpline, India)",
        "Vandrevala Foundation: 1860-2662-345 or 1800-2333-330 (24/7)",
        "If you are in immediate danger, please contact local emergency services or go to the nearest hospital.",
    ],
    "moderate": [
        "Consider talking to a counselor — many colleges offer free student counseling services.",
        "NIMHANS mental health helpline: 080-46110007",
        "Practice a daily check-in: journaling for 5 minutes can help track patterns.",
        "Reach out to one trusted friend or family member today.",
    ],
    "low": [
        "Keep up habits that support wellbeing: sleep, movement, and social connection.",
        "Free guided meditation apps (e.g. Healthy Minds Program) can help with stress.",
        "It's okay to check in with a counselor even if things feel manageable — early conversations help.",
    ],
}


def classify_risk(phq9_scores, chat_text):
    total = sum(phq9_scores)
    critical_flag = phq9_scores[CRITICAL_ITEM_INDEX] > 0
    text_lower = chat_text.lower()

    high_keyword_hit = any(kw in text_lower for kw in HIGH_RISK_KEYWORDS)
    moderate_keyword_hit = any(kw in text_lower for kw in MODERATE_RISK_KEYWORDS)

    if critical_flag or high_keyword_hit or total >= 20:
        return "high"
    if moderate_keyword_hit or total >= 10:
        return "moderate"
    return "low"


def get_groq_reply(client, user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------

st.set_page_config(page_title="MindGuard", page_icon="🧠", layout="centered")

st.title("🧠 MindGuard")
st.caption("Early Mental Health Detection — SDG 3: Good Health and Well-being")
st.info(
    "MindGuard is a screening and awareness tool, not a diagnosis. "
    "If you're in crisis, please use the helplines shown in your results, "
    "or contact local emergency services immediately.",
    icon="ℹ️",
)

if not api_key:
    st.error("Groq_API_KEY not found. Check your swara.env file.")
    st.stop()

client = Groq(api_key=api_key)

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_text_combined" not in st.session_state:
    st.session_state.chat_text_combined = ""
if "phq9_scores" not in st.session_state:
    st.session_state.phq9_scores = [None] * len(PHQ9_QUESTIONS)
if "show_results" not in st.session_state:
    st.session_state.show_results = False

tab1, tab2, tab3 = st.tabs(["💬 Check-In Chat", "📋 PHQ-9 Screener", "📊 Results"])

# --- Tab 1: Chat ---
with tab1:
    st.subheader("How have you been feeling lately?")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Type how you're feeling...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_text_combined += " " + user_input

        with st.spinner("MindGuard is thinking..."):
            reply = get_groq_reply(client, user_input, st.session_state.chat_history[:-1])

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

# --- Tab 2: PHQ-9 ---
with tab2:
    st.subheader("Quick Structured Check-In (PHQ-9)")
    st.write("Over the last 2 weeks, how often have you been bothered by the following?")

    for i, question in enumerate(PHQ9_QUESTIONS):
        st.session_state.phq9_scores[i] = st.radio(
            f"{i+1}. {question}",
            options=[0, 1, 2, 3],
            format_func=lambda x: {
                0: "0 - Not at all",
                1: "1 - Several days",
                2: "2 - More than half the days",
                3: "3 - Nearly every day",
            }[x],
            key=f"phq9_{i}",
            index=st.session_state.phq9_scores[i] if st.session_state.phq9_scores[i] is not None else 0,
        )

    if st.button("Submit and See Results", type="primary"):
        st.session_state.show_results = True

# --- Tab 3: Results ---
with tab3:
    if not st.session_state.show_results:
        st.write("Complete the PHQ-9 screener and click **Submit and See Results** to view your summary.")
    else:
        scores = st.session_state.phq9_scores
        total = sum(scores)
        risk_level = classify_risk(scores, st.session_state.chat_text_combined)

        st.subheader("Your Check-In Summary")
        st.metric("PHQ-9 Total Score", f"{total} / 27")

        risk_color = {"low": "green", "moderate": "orange", "high": "red"}[risk_level]
        st.markdown(f"**Risk level:** :{risk_color}[{risk_level.upper()}]")

        if scores[CRITICAL_ITEM_INDEX] > 0:
            st.warning(
                "You indicated some thoughts of self-harm. This matters, and support is available right now.",
                icon="⚠️",
            )

        st.subheader("Recommended Resources")
        for r in RESOURCES[risk_level]:
            st.write(f"- {r}")

        st.caption(
            "This is not a diagnosis. MindGuard is a screening and awareness tool only — "
            "please reach out to a qualified professional for support."
        )
