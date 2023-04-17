from fastapi import FastAPI, File, UploadFile, Request
from fastapi.templating import Jinja2Templates
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox
import tabula
import os
from PyPDF2 import PdfReader
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/extract/")
async def extract_text(request: Request, file: UploadFile = File(...)):
    # Save the uploaded PDF file to a "uploads" directory
    with open(os.path.join("uploads", file.filename), "wb") as f:
        f.write(file.file.read())

    # Extract the text from the uploaded PDF file
    pdf_path = os.path.join("uploads", file.filename)
    with open(pdf_path, "rb") as f:
        pdf_reader = PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    # Render the "result.html" template with the extracted text
    return templates.TemplateResponse("result.html", {"request": request, "filename": file.filename, "text": text})


@app.post("/extract_diagrammed/")
async def extract_diagrammed_text(request: Request, file: UploadFile = File(...)):
    # Extract the text from the uploaded PDF file
    pdf_path = os.path.join("uploads", file.filename)
    text = ""
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            print(element)
            if isinstance(element, LTTextBox):
                text += element.get_text()

    return templates.TemplateResponse("result.html", {"request": request, "filename": file.filename, "text": text, "element": element})


@app.post("/extract_tabular/")
async def extract_tabular_text(request: Request, file: UploadFile = File(...)):

    # Save the uploaded PDF file to a "uploads" directory
    with open(os.path.join("uploads", file.filename), "wb") as f:
        f.write(file.file.read())

    # Extract the tables from the uploaded PDF file using Tabula
    pdf_path = os.path.join("uploads", file.filename)
    tables = tabula.read_pdf(pdf_path, pages="all")
    for table in tables:
        print(table.values.tolist())
    return templates.TemplateResponse("result.html", {"request": request, "filename": file.filename, "table": table.values.tolist()})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
