import tempfile
from fastapi import FastAPI,UploadFile, File
from app.services.pdf.timetableparse import process_file

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/uploadpdf")
async def upload_pdf(file: UploadFile = File(...)):
    #Getting actual bytes from the file
    pdf_bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
        temp.write(pdf_bytes)
        temp.flush()
        temp_path = temp.name
        
        await process_file(temp_path)

        import os
        os.remove(temp_path)

    return {"message": "timetable successfully added to google calendar"}