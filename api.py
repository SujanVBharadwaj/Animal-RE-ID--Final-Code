from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import cv2
import base64
from recall import run_recall_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploaded_images")
UPLOAD_DIR.mkdir(exist_ok=True)


def encode_image(path):
    img = cv2.imread(str(path))
    ok, buffer = cv2.imencode(".jpg", img)
    if not ok:
        return ""
    return base64.b64encode(buffer).decode("utf8")


@app.post("/identify")
async def identify_animal(file: UploadFile = File(...)):
    saved_path = UPLOAD_DIR / file.filename

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_recall_pipeline(saved_path)

    if result is None:
        return {"error": "Identification failed"}

    species = result["predicted_species"]
    best_match_path = result["best_match_image"]

    best_match_b64 = encode_image(best_match_path)

    return {
        "name": species,
        "databaseImage": best_match_b64
    }
