from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from firebase_functions import storage_fn, scheduler_fn, options
from services.ai_service import ai_service
from services.firebase_service import firebase_service
from services.gcp_service import gcp_service
from services.vector_db_service import vector_db_service
from auth import get_current_user
from schemas import GeneratedContent, InterviewPrepOutput
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

options.set_global_options(region="australia-southeast1")
load_dotenv()
app = FastAPI()

origins = ["http://localhost:5173"] # Add your deployed URL later
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class GenerationRequest(BaseModel):
    job_description: str

class InterviewPrepRequest(BaseModel):
    job_description: str
    resume_text: str
    cover_letter_text: str

@app.post("/generate", response_model=GeneratedContent)
async def generate_application_documents(req: GenerationRequest, user: dict = Depends(get_current_user)):
    try:
        print(f"Starting AGENTIC workflow for user: {user.get('uid')}")
        return ai_service.generate_document_agentic(job_description=req.job_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview-prep", response_model=InterviewPrepOutput)
async def prepare_for_interview(req: InterviewPrepRequest, user: dict = Depends(get_current_user)):
    try:
        print(f"Starting INTERVIEW PREP workflow for user: {user.get('uid')}")
        return ai_service.prepare_for_interview_agentic(
            job_description=req.job_description,
            resume_text=req.resume_text,
            cover_letter_text=req.cover_letter_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@storage_fn.on_object_finalized()
def process_and_embed_document(event: storage_fn.CloudEvent):
    # ... (This function remains the same as the bug-fixed version)