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
st.title("🔍 SQLCraft - SQL Generator")
st.markdown("---")

# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Configuration Files")
    schema_file = st.file_uploader("Upload schema file", type=['txt', 'sql'])

with col2:
    st.subheader("Your Question")
    user_question = st.text_area("Type your question in natural language", height=150)

# Generate SQL button
if st.button("Generate SQL", type="primary"):
    if not selected_model:
        st.warning("Por favor, selecione um modelo na barra lateral para continuar.")
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
                st.success("SQL gerado com sucesso!")
                
                # Displaying formatted SQL
                st.subheader("SQL Gerado:")
                formatted_sql = format_sql(response).replace("```sql", "").replace("```", "")
                st.code(formatted_sql, language="sql")
                
                # Copy SQL button
                st.button("Copiar SQL", 
                         on_click=lambda: st.write(formatted_sql))
    else:
        st.warning("Por favor, forneça o arquivo de esquema e uma pergunta.")

# Footer
st.markdown("---")
st.markdown("Developed by Gabriel Martins")