"""TravelGenie Live - AI Travel Concierge with Real APIs"""

import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from agent import app as agent_app, SYSTEM_PROMPT

st.set_page_config(page_title="TravelGenie Live ✈️", page_icon="✈️", layout="wide")

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        background: linear-gradient(135deg, #10b981, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    
    .subtitle { text-align: center; color: #94a3b8; margin-bottom: 0.5rem; }
    
    .live-badge {
        display: block;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
        width: fit-content;
        margin: 0 auto 1.5rem;
    }
    
    .api-status { padding: 0.5rem; border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.85rem; }
    .api-ok { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; }
    .api-error { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #ef4444; }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# ✈️ TravelGenie Live")
st.markdown('<p class="subtitle">AI Travel Concierge with Real-Time Data</p>', unsafe_allow_html=True)
st.markdown('<div class="live-badge">🟢 LIVE DATA</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🔌 API Status")
    
    api_status = {
        "Duffel (Flights)": bool(os.getenv("DUFFEL_API_KEY")),
        "Booking.com (Hotels)": bool(os.getenv("RAPIDAPI_KEY")),
        "OpenWeatherMap": bool(os.getenv("OPENWEATHERMAP_API_KEY")),
        "Google Places": bool(os.getenv("GOOGLE_PLACES_API_KEY")),
        "SerpAPI (Events)": bool(os.getenv("SERPAPI_API_KEY")),
        "Ticketmaster": bool(os.getenv("TICKETMASTER_API_KEY"))
    }
    
    for api, is_configured in api_status.items():
        status_class = "api-ok" if is_configured else "api-error"
        icon = "✅" if is_configured else "❌"
        st.markdown(f'<div class="api-status {status_class}">{icon} {api}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 💡 Try These")
    
    examples = [
        "Find flights from NYC to Paris for 2026-01-20",
        "What's the real weather in Tokyo?",
        "Show me attractions in Barcelona",
        "What events are happening in London?",
    ]
    
    for ex in examples:
        if st.button(f"📌 {ex[:32]}...", key=ex):
            st.session_state.suggested_prompt = ex
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage) and msg.content:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Handle suggested prompts
if "suggested_prompt" in st.session_state:
    prompt = st.session_state.suggested_prompt
    del st.session_state.suggested_prompt
    st.session_state.pending = prompt
    st.rerun()

# Chat input
user_input = st.chat_input("Ask about real flights, hotels, weather, or events! 🌍")

if "pending" in st.session_state:
    user_input = st.session_state.pending
    del st.session_state.pending

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Fetching REAL data..."):
            try:
                conversation = [SystemMessage(content=SYSTEM_PROMPT)] + list(st.session_state.messages)
                result = agent_app.invoke({"messages": conversation})
                
                new_messages = [m for m in result["messages"] if not isinstance(m, SystemMessage)]
                st.session_state.messages = new_messages
                
                final = result["messages"][-1]
                if isinstance(final, AIMessage) and final.content:
                    st.markdown(final.content)
                else:
                    st.markdown("Request processed. What else?")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.markdown('<p style="text-align:center;color:#64748b;">Powered by Gemini AI, Duffel, Booking.com, OpenWeatherMap, Google Places & SerpAPI</p>', unsafe_allow_html=True)
