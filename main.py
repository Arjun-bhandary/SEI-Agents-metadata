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
from Formula import formula
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

form = formula()

@app.post("/formula/metadata")
async def get_metadata(user_input: str = Form(...), image: UploadFile = File(...)):
  # save temp file
  temp_path = f"temp_{image.filename}"
  with open(temp_path, "wb") as buffer:
    buffer.write(await image.read())
  
  result = form.extract_metadata(user_input, temp_path)
  os.remove(temp_path)  # cleanup
  return JSONResponse(content=result)

@app.post("/formula/summary")
async def get_summary(user_input: str = Form(...), image: UploadFile = File(...)):
  temp_path = f"temp_{image.filename}"
  with open(temp_path, "wb") as buffer:
    buffer.write(await image.read())
  
  result = form.extract_summary(user_input, temp_path)
  os.remove(temp_path)
  return JSONResponse(content=result)