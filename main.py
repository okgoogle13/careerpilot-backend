import os
import io
import re
import docx
import pypdf
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from firebase_functions import storage_fn, options
from firebase_admin import storage
from services.ai_service import ai_service
from services.firebase_service import firebase_service  # Imported for initialization side effect
from services.vector_db_service import vector_db_service
from auth import get_current_user
from schemas import GeneratedContent, InterviewPrepOutput
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Initialize services and settings
options.set_global_options(region="australia-southeast1")
load_dotenv()

# Ensure Firebase is initialized. This is crucial for the background function.
firebase_service

app = FastAPI()

# Configure CORS from environment variables for flexibility
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")
origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class GenerationRequest(BaseModel):
    job_description: str

class InterviewPrepRequest(BaseModel):
    job_description: str
    resume_text: str
    cover_letter_text: str

# --- API Endpoints ---
@app.post("/generate", response_model=GeneratedContent)
async def generate_application_documents(req: GenerationRequest, user: dict = Depends(get_current_user)):
    user_id = user.get("uid")
    if not user_id:
        raise HTTPException(status_code=403, detail="User ID not found in token.")
    try:
        return ai_service.generate_document_agentic(
            job_description=req.job_description,
            user_id=user_id
        )
    except Exception as e:
        print(f"Error in /generate endpoint: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during document generation.")

@app.post("/interview-prep", response_model=InterviewPrepOutput)
async def prepare_for_interview(req: InterviewPrepRequest, user: dict = Depends(get_current_user)):
    user_id = user.get("uid")
    if not user_id:
        raise HTTPException(status_code=403, detail="User ID not found in token.")
    try:
        return ai_service.prepare_for_interview_agentic(
            job_description=req.job_description,
            resume_text=req.resume_text,
            cover_letter_text=req.cover_letter_text,
            user_id=user_id
        )
    except Exception as e:
        print(f"Error in /interview-prep endpoint: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during interview preparation.")

# --- Background Cloud Functions ---
def simple_chunker(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """A simple text chunker based on words."""
    if not text:
        return []
    words = text.split()
    # If the text is smaller than the chunk size, return it as a single chunk.
    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

@storage_fn.on_object_finalized()
def process_and_embed_document(event: storage_fn.CloudEvent) -> None:
    """
    Triggered by a new file upload to Firebase Storage. It extracts text,
    chunks it, and upserts it to the vector DB, associated with a user.
    """
    bucket_name = event.data.bucket
    file_path = event.data.name
    print(f"Processing file: {file_path} in bucket: {bucket_name}")

    # The user_id is expected to be the first part of the file path.
    path_parts = file_path.split('/')
    if len(path_parts) < 2:
        print(f"Error: File path '{file_path}' does not contain a user ID prefix. Skipping.")
        return
    user_id = path_parts[0]

    if not (file_path.lower().endswith(".pdf") or file_path.lower().endswith(".docx")):
        print(f"Unsupported file type for '{file_path}'. Skipping.")
        return

    try:
        bucket = storage.bucket(bucket_name)
        blob = bucket.blob(file_path)
        file_bytes = blob.download_as_bytes()
        file_stream = io.BytesIO(file_bytes)

        text = ""
        if file_path.lower().endswith(".pdf"):
            reader = pypdf.PdfReader(file_stream)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        elif file_path.lower().endswith(".docx"):
            doc = docx.Document(file_stream)
            for para in doc.paragraphs:
                text += para.text + "\n"

        text = re.sub(r'\s+', ' ', text).strip()
        if not text:
            print(f"No text extracted from '{file_path}'.")
            return

        chunks = simple_chunker(text)
        print(f"Extracted and chunked text into {len(chunks)} chunks.")

        vector_db_service.upsert(chunks=chunks, user_id=user_id, source=file_path)
        print(f"Successfully processed and embedded document: {file_path}")

    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")
        raise