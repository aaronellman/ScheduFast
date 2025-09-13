from fastapi import FastAPI,UploadFile, File
from app.services.pdf.timetableparse import process_file
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.middleware.cors import CORSMiddleware
import os
from utils import save_temp_file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/uploadpdf")
async def upload_pdf(file: UploadFile = File(...)):
    #Getting actual bytes from the file
    pdf_bytes = await file.read()

    temp_path = save_temp_file(pdf_bytes)
        
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, process_file, temp_path)

    os.remove(temp_path)

    return {"message": "File Uploaded Successfully"}

#ping endpoint for workflow to keep website awake
@app.get("/ping")
def ping():
    return {"status": "ok"}