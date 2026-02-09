import streamlit as st

def generate_mental_wellness_tip(model):
    prompt = "Generate a short and inspiring mental wellness tip."
    response = model.generate_content(prompt)
    return response.text

def mental_health_chatbot_ui(model):
    # session states
    if 'mental_wellness_tip' not in st.session_state:
        try:
            st.session_state.mental_wellness_tip = generate_mental_wellness_tip(model)
        except Exception:
            st.session_state.mental_wellness_tip = "Take a moment to breathe deeply. Your mental health matters. 🧘"
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'chat_response' not in st.session_state:
        st.session_state.chat_response = None

    sidebar_style = """
        <style>
        section[data-testid="stSidebar"] > div {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        section[data-testid="stSidebar"] > div > div {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        section[data-testid="stSidebar"] div:has(img) {
            padding-top: 0 !important;
            margin-top: -7px !important;
        }
        </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)

    st.sidebar.markdown('<div style="margin-top: -100px;"></div>', unsafe_allow_html=True)

    st.sidebar.image(
        "not2.png",
        width=265,
        use_container_width=False
    )
    
    st.markdown(
        '<h2 class="page-title" style="text-align: center; margin-top: -30px;">Health Support Chatbot 🤖</h2>',
        unsafe_allow_html=True
    )
    st.write("**Welcome! I'm here to provide support and resources for mental well-being.**")
    st.write("")
    
    st.sidebar.header("Today's Wellness Tip")
    st.sidebar.info(st.session_state.mental_wellness_tip)

    st.sidebar.write("**Guidelines for using a chatbot**")

    st.sidebar.write("""
    1. **Be Clear**: Ask direct and specific questions.
    2. **Use Simple Language**: Keep it easy to understand.
    3. **Stay Focused**: Stick to one topic at a time.
    4. **Be Patient**: Wait for a response.
    5. **Provide Feedback**: Clarify if needed.

    **Note: This is not a substitute for professional mental health advice.**
    """)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("How can I help you today?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        chatbot_prompt = (
            f"You are a friendly and empathetic mental health support chatbot. "
            f"Respond thoughtfully to: {prompt}"
        )
        try:
            response = model.generate_content(chatbot_prompt)
            st.session_state.chat_response = response.text
        except Exception as e:
            st.session_state.chat_response = f"⚠️ Sorry, I'm temporarily unavailable due to API limits. Please try again later."
        
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.chat_response})
        with st.chat_message("assistant"):
            st.markdown(st.session_state.chat_response)