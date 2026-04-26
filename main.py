from typing import Any, Dict, List

import streamlit as st

from backend.core import run_llm


def _format_sources(context_docs: List[Any]) -> List[str]:
    return [
        str((meta.get("source") or "Unknown")) # format the sources
        for doc in (context_docs or []) # get the metadata from the documents
        if (meta := (getattr(doc, "metadata", None) or {})) is not None # get the metadata from the documents
    ]


st.set_page_config(page_title="LangChain Documentation Helper", layout="centered")#set the page config layout
st.title("LangChain Documentation Helper")#set the title

with st.sidebar:
    st.subheader("Session")#set the subheader
    if st.button("Clear chat", use_container_width=True):
        st.session_state.pop("messages", None)#clear the messages
        st.rerun()#rerun the app

if "messages" not in st.session_state:
    st.session_state.messages = [#initialize the messages
        {
            "role": "assistant",
            "content": "Ask me anything about LangChain docs. I’ll retrieve relevant context and cite sources.",#initialize the artificial messages
            "sources": [],#initialize the sources
        }
    ]#initialize the messages

for msg in st.session_state.messages:#loop through the messages
    with st.chat_message(msg["role"]):#create a chat message with the role
        st.markdown(msg["content"])#display the message
        if msg.get("sources"):#if the sources are not empty
            with st.expander("Sources"):#create an expander for the sources
                for s in msg["sources"]:#loop through the sources   
                    st.markdown(f"- {s}")#display the source

prompt = st.chat_input("Ask a question about LangChain…")#get the prompt
if prompt:#if the prompt is not empty
    st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})#append the prompt to the messages
    with st.chat_message("user"):#create a chat message with the role user
        st.markdown(prompt)#display the prompt

    with st.chat_message("assistant"):#create a chat message with the role assistant
        try:#try to generate the answer,try block is used to catch any errors that occur during the execution of the code
            with st.spinner("Retrieving docs and generating answer…"):#show a spinner while generating the answer
                result: Dict[str, Any] = run_llm(prompt)#run the RAG pipeline
                answer = str(result.get("answer", "")).strip() or "(No answer returned.)"#get the answer
                sources = _format_sources(result.get("context", []))#format the sources

            st.markdown(answer)#display the answer  
            if sources:
                with st.expander("Sources"):
                    for s in sources:#loop through the sources
                        st.markdown(f"- {s}")#display the source

            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}#append the answer to the messages
            )
        except Exception as e:#if an error occurs from the try block
            st.error("Failed to generate a response.")#display the error
            st.exception(e)#display the exception
