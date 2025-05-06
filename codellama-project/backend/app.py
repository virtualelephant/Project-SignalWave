from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Set up logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.info("Starting app.py")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://codellama.home.virtualelephant.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables for PostgreSQL
DB_HOST = os.getenv("DB_HOST", "postgres-service.codellama.svc.cluster.local")
DB_NAME = os.getenv("DB_NAME", "codellama")
DB_USER = os.getenv("DB_USER", "codellama")
DB_PASSWORD = os.getenv("DB_PASSWORD", "securepassword")
DB_PORT = os.getenv("DB_PORT", "5432")

# Model directory for persistence
MODEL_DIR = "/model/codellama-7b"

# Initialize PostgreSQL connection
def init_db():
    try:
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
        logger.info("PostgreSQL database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL: {str(e)}")

try:
    init_db()
except Exception as e:
    logger.error("Database initialization failed, but continuing startup")

# Download and load CodeLlama-7B
def load_model():
    try:
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)
        model_path = "/model/fine_tuned" if os.path.exists("/model/fine_tuned") else "codellama/CodeLlama-7b-hf"
        logger.info(f"Loading model from {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path, cache_dir=MODEL_DIR)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            cache_dir=MODEL_DIR,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        logger.info("Model loaded successfully")
        return tokenizer, model
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

try:
    tokenizer, model = load_model()
except Exception as e:
    logger.error("Model loading failed, exiting")
    raise

class Prompt(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_code(prompt: Prompt):
    try:
        inputs = tokenizer(prompt.prompt, return_tensors="pt")
        outputs = model.generate(inputs["input_ids"], max_length=200, num_return_sequences=1)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Save to PostgreSQL
        try:
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
            logger.info("Saved prompt and response to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to save to PostgreSQL: {str(e)}")
        
        return {"code": response}
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        return {"error": str(e)}

@app.get("/history")
async def get_history():
    try:
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
    except Exception as e:
        logger.error(f"Failed to fetch history: {str(e)}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}