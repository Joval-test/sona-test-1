import streamlit as st
import openai
import config
from langchain.schema import SystemMessage,HumanMessage, AIMessage
from core.vector_store import query_collections
from core.prompts import create_system_message
from apps.utils.summary_status import prepare_summary, prepare_status
from apps.utils.stage_logger import stage_log

@stage_log(stage=1)
def handle_user_input(llm, embeddings, company_collection, user_info):
    if st.session_state.conversation_ended:
        st.write("Conversation has ended. Please refresh the page to start a new conversation.")
    else:
        user_input = st.chat_input("Your response:")
        
        if user_input:
            st.session_state.messages.append(HumanMessage(content=user_input))
            st.chat_message("user").write(user_input)
            
            context = query_collections(user_input, company_collection, user_info, embeddings, llm)
            st.session_state.messages[0] = create_system_message(context)
            try:
                response = llm.invoke(st.session_state.messages)
                st.session_state.messages.append(AIMessage(content=response.content))
                st.chat_message("assistant", avatar=config.ICON_PATH).write(response.content)
                
                if "have a great day" in response.content.lower():
                    conversation = st.session_state.messages
                    messages_content = [f"{type(message).__name__}: {message.content}" 
                        for message in conversation 
                        if not isinstance(message, SystemMessage)]
                    print("\n".join(messages_content))
                    prompt_summary = f"From this conversation between the AI agent and the consumer prepare a summary of the conversation {messages_content} in 50 words, provide everything including the contact details."
                    prompt_status = f"Based on the following conversation {messages_content}, can you categorize the user's interest level as one of the following: 'Hot': very interested, 'Warm': partially interested, or 'Cold': not interested? Give just one word answer"
                    df = st.session_state.user_data_df
                    df_userid = str(st.session_state.userid)
                    prepare_summary(llm, prompt_summary, df, df_userid)
                    prepare_status(llm, prompt_status, df, df_userid)
                    st.session_state.conversation_ended = True
                    st.session_state.show_chat = False  # Hide chat input
                    st.rerun()
                    st.write("Conversation has ended. Please refresh the page to start a new conversation.")
            except openai.BadRequestError as e:
                error_message = str(e)
                if "content_filter" in error_message:
                    st.error("Your message was flagged by our content policy. Please rephrase and try again.")
                    st.session_state.conversation_ended = True
                    st.session_state.show_chat = False  # Hide chat input
                    st.rerun()
                else:
                    st.error(f"An error occurred: {error_message}")
                    st.rerun()