import streamlit as st
from src.graph import build_graph
from src.state import AgentState
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Claude-like appearance
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
        padding: 0;
    }
    
    /* Chat message container styling */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }

    /* User message alignment */
    /* Target the container when it has the user avatar */
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse !important;
        text-align: right;
    }
    
    /* Target the message content bubble for user */
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) > div[data-testid="stChatMessageContent"] {
        background: rgba(79, 172, 254, 0.15);
        border: 1px solid rgba(79, 172, 254, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-left: auto; 
        margin-right: 10px;
        max-width: 70%;
        text-align: right; 
    }

    /* Assistant message alignment */
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        flex-direction: row !important;
        text-align: left;
    }
    
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) > div[data-testid="stChatMessageContent"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-right: auto;
        margin-left: 10px;
        max-width: 70%;
        text-align: left;
    }

    /* Jumping dots animation */
    .jumping-dots {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        height: 20px;
        margin-left: 10px;
    }
    
    .dot {
        width: 8px;
        height: 8px;
        margin: 0 4px;
        background-color: #4faffe;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    .header-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
        padding: 40px 20px;
        text-align: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
    }
    
    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4faffe 0%, #00f0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 20px;
    }
    
    .success-message {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #22c55e;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #ef4444;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
if "processing" not in st.session_state:
    st.session_state.processing = False
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🤖 Personal AI Assistant</div>
    <div class="header-subtitle">Your intelligent companion for calendars, emails, messages & more</div>
</div>
""", unsafe_allow_html=True)

# Main chat interface
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Input and Processing State
if st.session_state.processing:
    # Disable input while processing
    st.chat_input("Processing...", disabled=True)
    
    # Show jumping dots and process
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("""
            <div class="jumping-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            """, unsafe_allow_html=True)
        
        try:
            # Create state from messages (make sure pending prompt is in messages)
            # The pending prompt was added to messages before setting processing=True
            state = AgentState(messages=st.session_state.messages)
            
            # Invoke graph
            result = st.session_state.graph.invoke(state, {'recursion_limit': 50})
            
            # Get assistant's last message
            assistant_response = None
            for msg in reversed(result["messages"]):
                if msg.get("role") == "assistant":
                    assistant_response = msg.get("content")
                    break
            
            # Update placeholder
            if assistant_response:
                placeholder.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                placeholder.empty()

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            placeholder.markdown(f'<div class="error-message">{error_msg}</div>', unsafe_allow_html=True)
        
        finally:
            # Reset state and rerun to unlock input
            st.session_state.processing = False
            st.session_state.pending_prompt = None
            st.rerun()

else:
    # Active input
    if user_input := st.chat_input("Say something..."):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.pending_prompt = user_input
        st.session_state.processing = True
        st.rerun()

# Sidebar with features
with st.sidebar:
    st.markdown("### Features")
    st.markdown("""
    ✅ **Calendar Management**
    - Add meetings
    - Update/reschedule events
    - Delete events
    - Set reminders
    
    ✅ **Communication**
    - Send Telegram messages
    - Send emails
    - Manage contacts
    
    ✅ **Memory System**
    - Save personal info
    - Recall memories
    - Update information
    
    ✅ **Task Planning**
    - Plan your day
    - Schedule activities
    - Organize workflow
    """)
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Current time
    st.markdown("---")
    st.markdown(f"**Current Time:** {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# Footer
st.markdown("""
---
<div style="text-align: center; color: rgba(255,255,255,0.4); font-size: 0.9rem; margin-top: 40px;">
    <p>Personal AI OS v1.0</p>
</div>
""", unsafe_allow_html=True)