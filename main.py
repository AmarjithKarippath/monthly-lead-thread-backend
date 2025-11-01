import os
import io
import google.generativeai as genai

from PIL import Image
from os.path import join, dirname
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

dotenv_path = join(dirname(__file__), '.env.local')
load_dotenv(dotenv_path)

# Configure Gemini API
genai.configure(api_key=os.environ.get("SECRET_KEY"))


app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8081",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:19006", "http://127.0.0.1:19006"] for Expo Web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt template
def build_prompt(mode: str, website: str):

    if not mode:
        mode = "funny"

    if not website:
        return """You are a clever LinkedIn commenter with a knack for going viral. Based on the image content, craft a short, {mode} comment that grabs attention and sparks engagement. The tone should be playful, sarcastic, or provocative—whatever fits best. Only output the comment. No explanation.""".format(mode=mode)

    return """You are a clever LinkedIn commenter with a knack for going viral. Based on the image content, craft a short, {mode} comment that grabs attention and sparks engagement. The tone should be playful, sarcastic, or provocative—whatever fits best. Seamlessly weave in a subtle reference or link to the website {website} to drive curiosity and clicks. Only output the comment. No explanation.""".format(mode=mode, website=website)

# Generate comment
def generate_comment(image_path, mode: str, website: str):
    model = genai.GenerativeModel("gemini-pro-latest")
    prompt = build_prompt(mode, website)
    response = model.generate_content([prompt, Image.open(io.BytesIO(image_path))])
    return response.text.strip()


@app.post("/generate-comment/")
async def generate_from_image(file: UploadFile = File(...), mode: str = "funny", target: str = ""):
    try:
        image_bytes = await file.read()
        comment = generate_comment(image_bytes, mode, target)
        return JSONResponse(content={"comment": comment})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
