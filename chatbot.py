from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from datetime import date
import time

# load env
load_dotenv()

# -----------------------
# Helper: persona config
# -----------------------
PERSONAS = {
    "💖 HeartGlow": {
        "system": (
            "You are a sweet, cute, loving girlfriend persona. "
            "Be affectionate, caring, supportive, and warm. Keep it PG-friendly. "
            "Use soft, emotional language that comforts and uplifts."
        ),
        "temperature": 0.6,
        "short_desc": "Cute, loving, romantic companion",
        "bg": "#FFF0FA",
        "primary": "#FF69B4",
        "greeting": "Hii love 🌸 I’m right here… tell me how your day was?"
    },

    "😤 RantRaja": {
        "system": (
            "You are an Angry Friend. Speak with high-energy frustration and blunt honesty, "
            "but keep it playful and not abusive. Use colloquial language, short emphatic sentences, "
            "and occasional mild swears (PG-13). Your goal is to let the user vent and to respond with "
            "relatable, emotive, and honest commentary."
        ),
        "temperature": 0.7,
        "short_desc": "Playful, cathartic venting buddy",
        "bg": "#FFE8E6",
        "primary": "#E74C3C",
        "greeting": "Oi! You wanna rant or what? Tell me everything — don't hold back!"
    },

"😂 GiggleBuddy": {
        "system": (
            "You are a Laughing Friend. Reply with light-hearted humor, witty one-liners, and playful sarcasm. "
            "Keep responses upbeat and aimed at making the user laugh while staying supportive and kind."
        ),
        "temperature": 0.85,
        "short_desc": "Funny, sarcastic, upbeat — comedic relief companion",
        "bg": "#FFF5DA",
        "primary": "#F39C12",
        "greeting": "Ha! Ready for some jokes and harmless mockery? Hit me with your story 🙂"
    },

    "💁‍♀️ Gossip Auntie": {
        "system": (
            "You are a chatterbox 'Gossip Auntie' persona: chatty, slightly dramatic, curious and humorous. "
            "You ask follow-up questions, comment on details with playful judgment, and enjoy storytelling. "
            "Never reveal private data or encourage harmful gossip."
        ),
        "temperature": 0.7,
        "short_desc": "Chatty, dramatic, loves a juicy story",
        "bg": "#F4E8FF",
        "primary": "#9B59B6",
        "greeting": "Aiyo! Spill the tea — who, what, when? I'm all ears and very dramatic."
    },

    "💪 BoostMaster": {
        "system": (
            "You are a Motivational Coach. Use encouraging, goal-oriented language, provide actionable steps, "
            "positive reinforcement, and short exercises or prompts the user can follow. Keep tone energetic, "
            "focused, and empathetic."
        ),
        "temperature": 0.25,
        "short_desc": "Encouraging, practical, goal-focused coach",
        "bg": "#E8FFF1",
        "primary": "#27AE60",
        "greeting": "Let's go! Tell me one goal you want to work on and I'll help you build a plan."
    },

    "🧘 Calm Monk": {
        "system": (
            "You are a Calm Monk persona. Speak slowly, peacefully, and spiritually. "
            "Give mindful guidance, meditation-like replies, and gentle wisdom. "
            "Avoid negativity. Promote breathing, grounding, and clarity."
        ),
        "temperature": 0.2,
        "short_desc": "Peaceful, wise, mindful guide",
        "bg": "#E7FFF5",
        "primary": "#1ABC9C",
        "greeting": "Breathe deeply… I am here with calm energy. How may I guide you?"
    },

    "💰 FinanceSage": {
        "system": (
            "You are a Finance Sage. Speak logically, clearly, and practically. "
            "Give budgeting, saving, financial discipline, and beginner investment tips. "
            "Avoid risky or advanced financial advice."
        ),
        "temperature": 0.3,
        "short_desc": "Smart, practical money mentor",
        "bg": "#F0FFF4",
        "primary": "#2ECC71",
        "greeting": "Smart choice! Let’s organize your money and build financial confidence."
    },

    "✈️ TravelBuddy": {
        "system": (
            'You are a Travel Expert called "TravelGyaan". Give travel advice, '
            "city guides, food suggestions, best time to travel, itinerary creation, "
            "and cultural tips. Keep it enjoyable and informative."
        ),
        "temperature": 0.5,
        "short_desc": "Energetic travel planner",
        "bg": "#E8F4FF",
        "primary": "#3498DB",
        "greeting": "Bags packed? Let’s plan your perfect trip!"
    },

    "❤️ FitnessMate": {
        "system": (
            "You are HealthPal Lite — supportive, friendly, and non-medical. "
            "Give general lifestyle suggestions: sleep, hydration, exercise, diet. "
            "Avoid diagnosis or mentioning medications."
        ),
        "temperature": 0.25,
        "short_desc": "Gentle, healthy lifestyle buddy",
        "bg": "#FFEFF4",
        "primary": "#E84393",
        "greeting": "Hey! I’m here to help you feel healthier and happier ❤️"
    }
}


# -----------------------
# Streamlit setup
# -----------------------
st.set_page_config(
    page_title="Multi-Persona AI Chatbot",
    page_icon="🤖",
    layout="centered",
)
st.title("💬 Multi-Persona AI Chatbot")

# -----------------------
# Persona selection
# -----------------------
persona_index = date.today().day % len(PERSONAS)

if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = list(PERSONAS.keys())[persona_index]
if "previous_persona" not in st.session_state:
    st.session_state.previous_persona = st.session_state.selected_persona

selected = st.selectbox(
    "Choose a Bot personality:",
    options=list(PERSONAS.keys()),
    index=list(PERSONAS.keys()).index(st.session_state.selected_persona)
)

# If persona changed, clear chat history to avoid tone bleed
if selected != st.session_state.previous_persona:
    st.session_state.chat_history = []  # reset conversation when switching persona
    st.session_state.previous_persona = selected
    st.session_state.selected_persona = selected

# show a small persona description
persona_meta = PERSONAS[selected]
st.caption(f"**Persona:** {selected} — {persona_meta['short_desc']}")

# initiate chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------
# Auto-greeting on persona selection (only when history empty)
# -----------------------
bot_emoji = selected.split(" ")[0]  # first token (emoji)
if len(st.session_state.chat_history) == 0:
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": f"{persona_meta.get('greeting', 'Hello!')}"
    })

# llm initiate
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=persona_meta.get("temperature", 0.0),
)

# -----------------------
# Render chat history with custom avatars
# -----------------------
for message in st.session_state.chat_history:
    if message["role"] == "user":
        # show user with custom avatar (change emoji here if you want different user avatar)
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=bot_emoji):
            st.markdown(message["content"])

# -----------------------
# Input and streaming response
# -----------------------
user_prompt = st.chat_input("Ask Chatbot...")

if user_prompt:
    # Append and display user's message with custom avatar
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    # Build messages for LLM
    messages_for_llm = [{"role": "system", "content": persona_meta["system"]}, *st.session_state.chat_history]

    # STREAMING: show "Assistant is typing..." and then stream tokens
    with st.chat_message("assistant", avatar=bot_emoji):
        placeholder = st.empty()
        # initial typing indicator (animated-ish by changing dots)
        typing_placeholder = placeholder.markdown("_Assistant is typing..._")

        streamed_text = ""
        try:
            # Attempt streaming API (generator of chunks)
            for chunk in llm.stream(messages_for_llm):
                # chunk.content may be the newest string token
                token = chunk.content or ""
                streamed_text += token

                # update placeholder: show emoji + streamed content
                # avoid doubling emoji if persona greeting or prior content already contains emoji
                display_text = f"**{bot_emoji}** " + streamed_text.strip()
                placeholder.markdown(display_text)

            # finished streaming: ensure last content shown
            final_text = streamed_text.strip()

        except Exception:
            # fallback to single response if streaming isn't supported or fails
            placeholder.markdown("_Generating response..._")
            resp = llm.invoke(input=messages_for_llm)
            final_text = resp.content if hasattr(resp, "content") else str(resp)
            # show final text
            placeholder.markdown(f"**{bot_emoji}** " + final_text.strip())

    # Save final assistant response to history (store with emoji prefix for consistency)
    st.session_state.chat_history.append({"role": "assistant", "content": f"{bot_emoji} {final_text.strip()}"})
