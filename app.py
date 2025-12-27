import streamlit as st
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="FriendBot (Llama 3)", page_icon="🦙")
st.title("💬 Chat with 'FriendBot'")

# --- 1. SETUP API ---
# In Streamlit Cloud, set this in "Secrets" as GROQ_API_KEY
# locally, you can paste the key directly to test (but don't commit it!)
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = "PASTE_YOUR_GSK_KEY_HERE_FOR_LOCAL_TESTING"

client = Groq(api_key=api_key)

# --- 2. LOAD DATA ---
@st.cache_resource
def load_system_instruction():
    try:
        with open("chat_history.txt", "r", encoding="utf-8") as f:
            chat_log = f.read()
    except FileNotFoundError:
        return "You are a helpful assistant." 

    return f"""
    You are a chatbot simulating a person based on the attached chat logs. 
    Your goal is to reply exactly as this person would (tone, slang, humor).
    
    --- CHAT HISTORY ---
    {chat_log}
    """

system_instruction = load_system_instruction()

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. DISPLAY CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. HANDLE INPUT ---
if prompt := st.chat_input("Type a message..."):
    # Show User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response
    with st.chat_message("assistant"):
        # Construct the full message history for the API
        # We put the system instruction FIRST
        messages_payload = [
            {"role": "system", "content": system_instruction}
        ]
        # Add the conversation history
        for m in st.session_state.messages:
            messages_payload.append({"role": m["role"], "content": m["content"]})

        try:
            stream = client.chat.completions.create(
                model="llama3-70b-8192", # Very smart, open source model
                messages=messages_payload,
                temperature=0.7,
                max_tokens=1024,
                stream=True,
            )
            
            # Stream the response (looks cool, like typing)
            response = st.write_stream(stream)
            
        except Exception as e:
            st.error(f"Error: {e}")
            response = "Sorry, I crashed."

    st.session_state.messages.append({"role": "assistant", "content": response})
