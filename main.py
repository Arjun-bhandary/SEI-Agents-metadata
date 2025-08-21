from fastapi import FastAPI, UploadFile, File,Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from typing import Dict
import shutil
import os
import pandas as pd
from Agents import Paper  # assume your code is in paper_parser.py
from datasets import Dataset
app = FastAPI()

key = os.getenv('GEMINI_API_KEY')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/paper/metadata")
async def extract_metadata(file: UploadFile = File(...)):
    try:
        # Save uploaded file to a temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        paper = Paper(pdf_path=tmp_path)
        metadata = paper.get_meta_data()

        os.remove(tmp_path)
        return JSONResponse(content=metadata)

    except Exception as e:
        return {"error": str(e)}


@app.post("/paper/summary")
async def extract_summary(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        paper = Paper(pdf_path=tmp_path)
        summary = paper.get_summary()

        os.remove(tmp_path)
        return JSONResponse(content=summary)

    except Exception as e:
        return {"error": str(e)}


ds = Dataset()

# Endpoint: Generate Metadata
@app.post("/dataset/metadata")
async def generate_metadata_endpoint(
    description: str = Form(...),
    file: UploadFile = None
) -> Dict:
    # Save uploaded file locally
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call Dataset method
    result = ds.generate_metadata(description, temp_path, os.getenv("GEMINI_API_KEY"))

    # Clean up file
    os.remove(temp_path)

    return result


# Endpoint: Generate Summary
@app.post("/dataset/summary")
async def generate_summary_endpoint(
    description: str = Form(...),
    file: UploadFile = None
) -> Dict:
    # Save uploaded file locally
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call Dataset method
    result = ds.generate_summary(description, temp_path, os.getenv("GEMINI_API_KEY"))

    # Clean up file
    os.remove(temp_path)

    return result