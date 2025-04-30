from fastapi import FastAPI
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

app = FastAPI()

# Define model directory for persistence
MODEL_DIR = "/model/codellama-7b"

# Download and load CodeLlama-7B
def load_model():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    model_name = "codellama/CodeLlama-7b-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=MODEL_DIR)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        cache_dir=MODEL_DIR,
        torch_dtype=torch.float16,
        load_in_8bit=True,
        device_map="auto"
    )
    return tokenizer, model

tokenizer, model = load_model()

@app.post("/generate")
async def generate_code(prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"], max_length=200, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"code": response}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}