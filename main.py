import os
from groq import Groq
import sqlparse
from dotenv import load_dotenv
import argparse

load_dotenv('.env')

MODEL = "llama3-70b-8192"

def load_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

client = Groq(
  api_key=os.getenv('GROQ_API_KEY')
)

def generate_sql(client, prompt, model):
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

def format_sql(raw_sql: str) -> str:
    return sqlparse.format(raw_sql, reindent=True, keyword_case='upper')

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Gerador de SQL usando IA')
  parser.add_argument('--prompt', required=True, help='Caminho para o arquivo de prompt do sistema')
  parser.add_argument('--schema', required=True, help='Caminho para o arquivo de schema')
  parser.add_argument('--question', required=True, help='Pergunta do usuário')
  
  args = parser.parse_args()
  
  BASE_PROMPT = load_file(args.prompt)
  BASE_SCHEMA = load_file(args.schema)
  
  full_prompt = BASE_PROMPT.format(user_question=args.question, schema=BASE_SCHEMA)
      
  response = generate_sql(client, full_prompt, MODEL)
  print(format_sql(response))