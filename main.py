import os
import requests
import sqlparse
from dotenv import load_dotenv
import argparse

load_dotenv('.env')

def load_file(folder, file_name) -> str:
  file_path = os.path.join(folder, file_name)
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      return file.read()
  except FileNotFoundError:
    return ""
    
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
      print("Erro ao gerar SQL com o modelo local")
      return ""
  except Exception as e:
    print(f"Erro ao conectar com Ollama: {str(e)}")
    return ""

def format_sql(raw_sql: str) -> str:
  return sqlparse.format(raw_sql, reindent=True, keyword_case='upper')
  
def main(user_question):

  full_prompt = SYSTEM_PROMPT.format(user_question=user_question, schema=BASE_SCHEMA)
  
  response = generate_sql(full_prompt, MODEL)
  print(format_sql(response))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Gerador de SQL usando IA')
  
  parser.add_argument('--question', required=True, help='Pergunta do usuário')
  
  MODEL = "gemma3:1b"
  SYSTEM_PROMPT = load_file(folder='prompts', file_name='system_prompt.txt')
  BASE_SCHEMA = load_file(folder='schema', file_name='schema.txt')
  
  args = parser.parse_args()
  
  main(user_question=args.question)
      
  