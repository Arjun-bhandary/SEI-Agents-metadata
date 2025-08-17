from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import os
from Agents import Paper  # assume your code is in paper_parser.py

app = FastAPI()

@app.post("/metadata")
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


@app.post("/summary")
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
