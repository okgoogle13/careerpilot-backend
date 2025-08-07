# functions/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import genkit
from genkit.ext.fastapi import configure_genkit

# Import from our new, structured modules
from functions.config import API_TITLE, API_DESCRIPTION
from functions.schemas import JobDescription, GeneratedContent, InterviewPrepData, InterviewPrepOutput, User
from functions.auth import get_current_user
from functions.flows.generation_flow import generateFlow
from functions.flows.interview_flow import interviewPrepFlow

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
)

# CORS Middleware
origins = [
    "http://localhost:5173",
    "httpsa://careerpilot-431505.web.app",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Define Flows with Authentication
# We add `dependencies=[Depends(get_current_user)]` to protect the endpoint.
# Now, a valid Firebase Auth token is required to call this flow.
genkit.define_flow(
    name="generate",
    input_schema=JobDescription,
    output_schema=GeneratedContent,
    dependencies=[Depends(get_current_user)],
)(generateFlow)

genkit.define_flow(
    name="interview-prep",
    input_schema=InterviewPrepData,
    output_schema=InterviewPrepOutput,
    dependencies=[Depends(get_current_user)],
)(interviewPrepFlow)

# Mount Genkit flows onto the FastAPI app
configure_genkit(app)

# Health check endpoint (does not require auth)
@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "API is operational"}