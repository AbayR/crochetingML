import base64
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post("/generate")
async def generate_pattern(file: UploadFile = File(...), prompt: str = Form("")):
    image_bytes = await file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Authorization": "Bearer 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", 
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": base64_image
    }

    response = requests.post(
        "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
        headers=headers,
        json=payload
    )

    try:
        result = response.json()
        print("DEBUG:", result)

        if isinstance(result, list) and "generated_text" in result[0]:
            return {"pattern": result[0]["generated_text"]}
        else:
            return {"pattern": f"No output or unknown format. Raw: {result}"}
    except Exception as e:
        return {"pattern": f"Error: {str(e)}\nRaw: {response.content.decode('utf-8', 'ignore')}"}
