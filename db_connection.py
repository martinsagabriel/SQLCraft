import streamlit as st
import mysql.connector
import psycopg2
import sqlite3
import pyodbc
import pandas as pd
import json
from pathlib import Path

# Create connections directory if it doesn't exist
CONNECTIONS_DIR = Path("connections")
CONNECTIONS_DIR.mkdir(exist_ok=True)

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
        print(connection)
        return connection
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return None

def execute_query(connection, query):
    print(query)
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        print(results)
        columns = [desc[0] for desc in cursor.description]
        print(columns)
        cursor.close()
        results_list = [list(row) for row in results]
        df = pd.DataFrame(results_list)
        df.columns = columns
        return df
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return None, None
    
def save_connection(name, db_type, params):
    """Save connection parameters to a JSON file"""
    connection_data = {
        "name": name,
        "type": db_type,
        "params": params
    }
    
    file_path = CONNECTIONS_DIR / f"{name}.json"
    with open(file_path, 'w') as f:
        json.dump(connection_data, f)
    return True

def load_saved_connections():
    """Load all saved connections"""
    connections = {}
    for file_path in CONNECTIONS_DIR.glob("*.json"):
        with open(file_path, 'r') as f:
            connection_data = json.load(f)
            connections[connection_data["name"]] = connection_data
    return connections

def delete_connection(name):
    """Delete a saved connection"""
    file_path = CONNECTIONS_DIR / f"{name}.json"
    if file_path.exists():
        file_path.unlink()
        return True
    return False

st.subheader("Your SELECT")
# User question field
user_question = st.text_area("Query", height=150)

# Database Connection Section
st.sidebar.title("Database Connection")

# Add tabs for New Connection and Saved Connections
connection_tab, saved_connections_tab = st.sidebar.tabs(["New Connection", "Saved Connections"])

with connection_tab:
    db_type = st.selectbox(
        "Select Database Type",
        ["MySQL", "PostgreSQL", "SQLite", "SQL Server"]
    )

    # Connection name for saving
    connection_name = st.text_input("Connection Name")

    # Database connection parameters
    if db_type != "SQLite":
        host = st.text_input("Host")
        port = st.text_input("Port", value="3306" if db_type == "MySQL" else "5432")
        database = st.text_input("Database Name")
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
    else:
        database = st.text_input("Database File Path")

    col1, col2 = st.columns(2)
    
    with col1:
        # Connect button
        if st.button("Connect"):
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
                st.success("Connected successfully!")
                st.session_state['db_connection'] = connection
                
                # Save connection if name is provided
                if connection_name:
                    save_connection(connection_name, db_type, connection_params)
                    st.success(f"Connection '{connection_name}' saved!")
            else:
                st.error("Connection failed!")

with saved_connections_tab:
    saved_connections = load_saved_connections()
    
    if not saved_connections:
        st.info("No saved connections found")
    else:
        selected_connection = st.selectbox(
            "Select a saved connection",
            list(saved_connections.keys())
        )
        
        if selected_connection:
            conn_data = saved_connections[selected_connection]
            
            # Display connection details
            st.write("Connection Details:")
            details = {
                "Type": conn_data["type"],
                "Database": conn_data["params"].get("database", ""),
                "Host": conn_data["params"].get("host", ""),
                "Port": conn_data["params"].get("port", "")
            }
            for key, value in details.items():
                if value:  # Only show non-empty values
                    st.text(f"{key}: {value}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Connect to Selected"):
                    connection = connect_database(
                        conn_data["type"],
                        conn_data["params"]
                    )
                    if connection:
                        st.success("Connected successfully!")
                        st.session_state['db_connection'] = connection
                    else:
                        st.error("Connection failed!")
            
            with col2:
                if st.button("Delete Connection"):
                    if delete_connection(selected_connection):
                        st.success(f"Connection '{selected_connection}' deleted!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to delete connection!")

if 'db_connection' in st.session_state:
    if st.button("Execute SQL"):
        df = execute_query(st.session_state['db_connection'], user_question)
        st.dataframe(df)