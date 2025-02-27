import streamlit as st
import os
from groq import Groq
import sqlparse
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="SQLCraft - SQL Generator",
    page_icon="🔍",
    layout="wide"
)

# Loading environment variables
load_dotenv('.env')

# Settings
MODEL = "llama3-70b-8192"

# Groq client initialization
client = Groq(
    api_key=os.getenv('GROQ_API_KEY')
)

def load_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return ""

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

# Streamlit interface
st.title("🔍 SQLCraft - SQL Generator")
st.markdown("---")

# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Configuration Files")
    
    # Prompt file upload
    prompt_file = st.file_uploader("Upload prompt file", type=['txt'])
    
    # Schema file upload
    schema_file = st.file_uploader("Upload schema file", type=['txt', 'sql'])

with col2:
    st.subheader("Your Question")
    # User question field
    user_question = st.text_area("Type your question in natural language", height=150)

# Generate SQL button
if st.button("Generate SQL", type="primary"):
    if prompt_file and schema_file and user_question:
        # Reading uploaded files
        prompt_content = prompt_file.getvalue().decode()
        schema_content = schema_file.getvalue().decode()
        
        # Building complete prompt
        full_prompt = prompt_content.format(
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
        st.warning("Please provide all required files and a question.")

# Footer
st.markdown("---")
st.markdown("Developed by Gabriel Martins")