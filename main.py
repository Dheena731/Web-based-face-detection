from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import face_recognition
import numpy as np
import pickle
import cv2

# Load your encodings
with open("face_encodings.pkl", "rb") as f:
    data = pickle.load(f)  # expects dict: {"encodings": [...], "names": [...]}

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/recognize_face")
async def recognize_face(image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)

    results = []

    for (box, encoding) in zip(boxes, encodings):
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matchedIdxs:
                matched_name = data["names"][i]
                counts[matched_name] = counts.get(matched_name, 0) + 1

            name = max(counts, key=counts.get)

        top, right, bottom, left = box
        results.append({
            "name": name,
            "box": [left, top, right - left, bottom - top]
        })

    return JSONResponse(content={"results": results})
