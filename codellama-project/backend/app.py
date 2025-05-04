from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = FastAPI()

# Environment variables for PostgreSQL
DB_HOST = os.getenv("DB_HOST", "postgres-service.default.svc.cluster.local")
DB_NAME = os.getenv("DB_NAME", "codellama")
DB_USER = os.getenv("DB_USER", "codellama")
DB_PASSWORD = os.getenv("DB_PASSWORD", "securepassword")
DB_PORT = os.getenv("DB_PORT", "5432")

# Model directory for persistence
MODEL_DIR = "/model/codellama-7b"

# Initialize PostgreSQL connection
def init_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# Download and load CodeLlama-7B
def load_model():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    model_path = "/model/fine_tuned" if os.path.exists("/model/fine_tuned") else "codellama/CodeLlama-7b-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_path, cache_dir=MODEL_DIR)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        cache_dir=MODEL_DIR,
        torch_dtype=torch.float16,
        load_in_8bit=True,
        device_map="auto"
    )
    return tokenizer, model

tokenizer, model = load_model()

class Prompt(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_code(prompt: Prompt):
    inputs = tokenizer(prompt.prompt, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"], max_length=200, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Save to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (prompt, response, timestamp) VALUES (%s, %s, %s)",
        (prompt.prompt, response, datetime.utcnow())
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"code": response}

@app.get("/history")
async def get_history():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT prompt, response, timestamp FROM chat_history ORDER BY timestamp DESC")
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"history": history}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}