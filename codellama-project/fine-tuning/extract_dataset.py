import psycopg2
import json
import os

DB_HOST = os.getenv("DB_HOST", "postgres-service.default.svc.cluster.local")
DB_NAME = os.getenv("DB_NAME", "codellama")
DB_USER = os.getenv("DB_USER", "codellama")
DB_PASSWORD = os.getenv("DB_PASSWORD", "securepassword")
DB_PORT = os.getenv("DB_PORT", "5432")

def extract_dataset(output_file):
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, response FROM chat_history")
    dataset = [{"prompt": row[0], "response": row[1]} for row in cursor.fetchall()]
    conn.close()
    
    with open(output_file, 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + '\n')

if __name__ == "__main__":
    extract_dataset('/model/dataset.jsonl')