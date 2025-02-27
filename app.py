import streamlit as st
import os
from groq import Groq
import sqlparse
from dotenv import load_dotenv
import mysql.connector
import psycopg2
import sqlite3
import pyodbc
import pandas as pd

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

def connect_database(db_type, params):
    try:
        if db_type == "MySQL":
            connection = mysql.connector.connect(
                host=params['host'],
                user=params['user'],
                password=params['password'],
                database=params['database'],
                port=params.get('port', 3306)
            )
        elif db_type == "PostgreSQL":
            connection = psycopg2.connect(
                host=params['host'],
                user=params['user'],
                password=params['password'],
                database=params['database'],
                port=params.get('port', 5432)
            )
        elif db_type == "SQLite":
            connection = sqlite3.connect(params['database'])
        elif db_type == "SQL Server":
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={params['host']};"
                f"DATABASE={params['database']};"
                f"UID={params['user']};"
                f"PWD={params['password']}"
            )
        return connection
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return None

def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        return columns, results
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return None, None

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

# Database Connection Section
st.sidebar.title("Database Connection")

db_type = st.sidebar.selectbox(
    "Select Database Type",
    ["MySQL", "PostgreSQL", "SQLite", "SQL Server"]
)

# Database connection parameters
if db_type != "SQLite":
    host = st.sidebar.text_input("Host")
    port = st.sidebar.text_input("Port", value="3306" if db_type == "MySQL" else "5432")
    database = st.sidebar.text_input("Database Name")
    user = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
else:
    database = st.sidebar.text_input("Database File Path")

# Connect button
if st.sidebar.button("Connect to Database"):
    if db_type == "SQLite":
        connection_params = {"database": database}
    else:
        connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
    
    connection = connect_database(db_type, connection_params)
    if connection:
        st.sidebar.success("Connected successfully!")
        st.session_state['db_connection'] = connection
    else:
        st.sidebar.error("Connection failed!")

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
                
                # Execute SQL button (only if connected to database)
                if 'db_connection' in st.session_state:
                    if st.button("Execute SQL"):
                        columns, results = execute_query(st.session_state['db_connection'], formatted_sql)
                        if results is not None:
                            st.subheader("Query Results:")
                            st.dataframe(pd.DataFrame(results, columns=columns))
                
                # Copy SQL button
                st.button("Copy SQL", on_click=lambda: st.write(formatted_sql))
    else:
        st.warning("Please provide all required files and a question.")

# Footer
st.markdown("---")
st.markdown("Developed by Gabriel Martins")

# Cleanup database connection when the app is closed
def cleanup():
    if 'db_connection' in st.session_state:
        st.session_state['db_connection'].close()

# Register the cleanup function
import atexit
atexit.register(cleanup)