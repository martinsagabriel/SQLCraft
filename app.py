import streamlit as st
import sqlparse
import requests
from typing import List
import os

def get_local_models() -> List[str]:
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = [model['name'] for model in response.json()['models']]
            return models
        return []
    except:
        return []

def load_prompt_template() -> str:
    prompt_path = os.path.join('prompts', 'system_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"Arquivo de prompt não encontrado em: {prompt_path}")
        return ""

# Page configuration
st.set_page_config(
    page_title="SQLCraft",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Prompt template global
PROMPT_TEMPLATE = load_prompt_template()

# Sidebar com seleção de modelo
st.sidebar.title("Configurações")
available_models = get_local_models()

if not available_models:
    st.sidebar.error("Não foi possível conectar ao Ollama ou nenhum modelo foi encontrado. Certifique-se de que o Ollama está rodando.")
    selected_model = None
else:
    selected_model = st.sidebar.selectbox(
        "Selecione o modelo:",
        available_models
    )

def generate_sql(prompt: str, model: str) -> str:
    try:
        response = requests.post('http://localhost:11434/api/generate', 
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()['response']
        else:
            st.error("Erro ao gerar SQL com o modelo local")
            return ""
    except Exception as e:
        st.error(f"Erro ao conectar com Ollama: {str(e)}")
        return ""

def format_sql(raw_sql: str) -> str:
    return sqlparse.format(raw_sql, reindent=True, keyword_case='upper')

# Main page content
st.title("SQLCraft")
st.markdown("---")

# File upload at the top
st.subheader("Schema Configuration")
schema_file = st.file_uploader("Upload your database schema file", type=['txt', 'sql'])

# Adding some space
st.markdown("---")

# Chat-like conversation area
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.container():
        if message['type'] == 'user':
            st.markdown(f"**Question:** {message['content']}")
        else:
            st.markdown("**Generated SQL:**")
            st.code(message['content'], language="sql")
        st.markdown("---")

# Bottom input area with custom styling
st.markdown(
    """
    <style>
    .stTextArea textarea {
        border-radius: 10px;
    }
    .stButton button {
        border-radius: 20px;
        padding: 0.5rem 2rem;
    }
    div.block-container {
        padding-bottom: 5rem;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Input area at the bottom
with st.container():
    user_question = st.text_area("Type your question here", height=100, placeholder="Ask a question about your database...")
    col1, col2 = st.columns([4, 1])
    with col2:
        generate_button = st.button("Generate SQL", type="primary", use_container_width=True)

if generate_button:
    if not selected_model:
        st.warning("Please select a model in the sidebar to continue.")
    elif schema_file and user_question:
        # Reading schema file
        schema_content = schema_file.getvalue().decode()
        
        # Building complete prompt
        full_prompt = PROMPT_TEMPLATE.format(
            user_question=user_question,
            schema=schema_content
        )
        
        # Generating SQL
        with st.spinner("Generating SQL..."):
            response = generate_sql(full_prompt, selected_model)
            
            if response:
                formatted_sql = format_sql(response).replace("```sql", "").replace("```", "")
                
                # Add messages to chat history
                st.session_state.messages.append({'type': 'user', 'content': user_question})
                st.session_state.messages.append({'type': 'assistant', 'content': formatted_sql})
                
                # Force rerun to update chat
                st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Developed by Gabriel Martins</div>", 
    unsafe_allow_html=True
)