import streamlit as st
import os
from groq import Groq
import sqlparse
from dotenv import load_dotenv
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="SQL Generator - SQLCraft",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Loading environment variables
load_dotenv('.env')

# Settings
MODEL = "llama3-70b-8192"

# Prompt template global
PROMPT_TEMPLATE = """Você tem a tarefa de gerar consultas SQL para o banco de dados com base nas perguntas do usuário sobre os dados armazenados nessas tabelas:

Banco de dados:
--------
{schema}
--------

Dada a pergunta de um usuário sobre esses dados, escreva uma consulta SQL válida que extraia ou calcule com precisão as informações solicitadas dessas tabelas e siga as práticas recomendadas de SQL para otimizar a legibilidade e o desempenho, quando aplicável.

Aqui estão algumas dicas para escrever consultas:
* Todas as tabelas referenciadas DEVEM ter alias
* não inclui implicitamente uma cláusula GROUP BY
* CURRENT_DATE obtém a data de hoje
* Campos agregados como COUNT(*) devem ser nomeados apropriadamente
* Nunca inclua employee_id na saída - mostre o nome do funcionário em vez disso

Question:
--------
{user_question}
--------

Observação:
---------
* Apresente apenas a consulta SQL, sem explicações ou comentários.
---------"""

# Groq API key input
groq_api_key = st.sidebar.text_input("Digite sua chave API do Groq:", type="password")
if groq_api_key:
    client = Groq(api_key=groq_api_key)
    has_api_key = True
else:
    has_api_key = False

def generate_sql(client, prompt, model):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating SQL: {str(e)}")
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
    
    # Schema file upload
    schema_file = st.file_uploader("Upload schema file", type=['txt', 'sql'])

with col2:
    st.subheader("Your Question")
    # User question field
    user_question = st.text_area("Type your question in natural language", height=150)

# Generate SQL button
if st.button("Generate SQL", type="primary"):
    if not has_api_key:
        st.warning("Por favor, insira sua chave API do Groq na barra lateral para continuar.")
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
            response = generate_sql(client, full_prompt, MODEL)
            
            if response:
                st.success("SQL generated successfully!")
                
                # Displaying formatted SQL
                st.subheader("Generated SQL:")
                formatted_sql = format_sql(response).replace("```sql", "").replace("```", "")
                st.code(formatted_sql, language="sql")
                
                # Copy SQL button
                st.button("Copy SQL", 
                         on_click=lambda: st.write(formatted_sql))
    else:
        st.warning("Por favor, forneça o arquivo de esquema e uma pergunta.")

# Footer
st.markdown("---")
st.markdown("Developed by Gabriel Martins")