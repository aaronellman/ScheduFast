from fastapi import FastAPI,UploadFile, File

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/uploadpdf")
async def upload_pdf(file: UploadFile = File(...)):
    return {"filename": file.filename}