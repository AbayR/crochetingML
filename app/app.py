from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
import requests
from transformers import TextStreamer
from unsloth import FastVisionModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve HTML from static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Load model once at startup
model, tokenizer = FastVisionModel.from_pretrained("your-hf-username/your-lora-model", load_in_4bit=False)
FastVisionModel.for_inference(model)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

@app.post("/generate")
async def generate_pattern(file: UploadFile = File(...), prompt: str = Form("")):
    image_bytes = await file.read()
    headers = {"Authorization": "Bearer hf_YOUR_TOKEN"}
    response = requests.post(
        "https://api-inference.huggingface.co/models/your-username/your-lora-model",
        headers=headers,
        files={"inputs": image_bytes},
        data={"parameters": {"prompt": prompt}},
    )
    result = response.json()
    return {"pattern": result.get("generated_text", "")}
