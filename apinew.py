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
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploaded_images")
UPLOAD_DIR.mkdir(exist_ok=True)

def encode_image(path):
    """Encodes an image to a Base64 string specifically for HTML img tags."""
    if not Path(path).exists():
        return ""
    img = cv2.imread(str(path))
    if img is None:
        return ""
    ok, buffer = cv2.imencode(".jpg", img)
    if not ok:
        return ""
    b64_str = base64.b64encode(buffer).decode("utf8")
    # Add the data prefix so React can display it directly
    return f"data:image/jpeg;base64,{b64_str}"

@app.post("/identify")
async def identify_animal(file: UploadFile = File(...)):
    saved_path = UPLOAD_DIR / file.filename

    # Save the uploaded file locally
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run the pipeline
    result = run_recall_pipeline(saved_path)

    if result is None:
        return {"error": "Identification failed"}

    # 1. Extract Main Data
    species = result["predicted_species"].capitalize()
    best_match_path = result["best_match_image"]
    confidence_score = result.get("confidence", 0) * 100 # Convert 0.92 to 92.0

    # 2. Encode Main Images
    uploaded_b64 = encode_image(saved_path)
    database_b64 = encode_image(best_match_path)

    # 3. Process Gallery (Top 5 matches)
    gallery_images = []
    for item in result.get("ranked_gallery", []):
        gallery_images.append({
            "url": encode_image(item["image_path"]),
            "score": round(item["cosine_score"] * 100, 1)
        })

    # 4. Return format matching App.tsx "AnimalResult" interface
    return {
        "name": species,
        "confidence": round(confidence_score, 1),
        "imageUrl": uploaded_b64,       # The image they just uploaded
        "databaseImageUrl": database_b64, # The best match from DB
        "galleryImages": gallery_images   # The top 5 list
    }

