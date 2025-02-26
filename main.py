import os
from groq import Groq
import sqlparse
from dotenv import load_dotenv

load_dotenv('.env')

MODEL = "llama3-70b-8192"

with open('system_prompt.txt', 'r') as file:
  BASE_PROMPT = file.read()

with open('schema.txt', 'r') as file:
  BASE_SCHEMA = file.read()

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
    full_prompt = BASE_PROMPT.format(user_question="Liste os produtos mais vendidos em 2024", schema=BASE_SCHEMA)
    print(full_prompt)
    
    response = generate_sql(client, full_prompt, MODEL)
    print(format_sql(response))