import streamlit as st
from agent import run_agent

st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="centered")

st.title("AI Agent")
st.caption("Ask me anything · Search the web · Draft an email")

# Show intent badge colours
INTENT_LABELS = {
    "search": ("🔍 Web Search", "#1a73e8"),
    "email":  ("✉️ Email Draft", "#34a853"),
    "chat":   ("💬 Chat",        "#9e9e9e"),
}

# Initialise chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "intent" in msg:
            label, colour = INTENT_LABELS.get(msg["intent"], ("", "#9e9e9e"))
            st.markdown(
                f'<span style="background:{colour};color:white;padding:2px 8px;'
                f'border-radius:12px;font-size:0.75rem">{label}</span>',
                unsafe_allow_html=True,
            )
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask something, search the web, or say 'draft an email to...'"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, intent = run_agent(
                prompt,
                # Pass history without the message we just appended
                st.session_state.messages[:-1],
            )

        label, colour = INTENT_LABELS.get(intent, ("", "#9e9e9e"))
        st.markdown(
            f'<span style="background:{colour};color:white;padding:2px 8px;'
            f'border-radius:12px;font-size:0.75rem">{label}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response, "intent": intent}
    )
