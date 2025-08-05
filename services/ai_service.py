import os
import json
import requests
import google.generativeai as genai
from pydantic import BaseModel
from . import config
from schemas import GeneratedContent, InterviewPrepOutput
from .vector_db_service import vector_db_service

def get_secret(secret_id, project_id):
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

class CompanyDiveRequest(BaseModel):
    company_name: str

@define_tool(
    name="companyDeepDive",
    description="Performs a deep, synthesized research dive on a company to find its mission, values, culture, recent news, and key projects. Use this for comprehensive background checks.",
    input_schema=CompanyDiveRequest,
)
def company_deep_dive(req: CompanyDiveRequest) -> str:
    api_key = ""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        api_key = get_secret("PERPLEXITY_API_KEY", project_id)
    else:
        api_key = os.getenv("PERPLEXITY_API_KEY")

    if not api_key:
        return "Error: Perplexity API key is not configured."

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3-sonar-large-32k-online",
        "messages": [
            {"role": "system", "content": "You are an expert business analyst. Provide a concise but comprehensive brief on the requested company."},
            {"role": "user", "content": f"Provide a business brief for the company: '{req.company_name}'. Focus on their mission, stated values, company culture, and any major recent news or projects relevant to someone applying for a job there."},
        ],
    }
    
    try:
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except requests.RequestException as e:
        print(f"Error calling Perplexity API: {e}")
        return f"Error: Could not retrieve deep dive info. {str(e)}"

class DocumentSearchRequest(BaseModel):
    query: str

@define_tool(
    name="retrieveUserDocuments",
    description="Search and retrieve relevant text from the user's uploaded historical job application documents to understand their skills and writing style.",
    input_schema=DocumentSearchRequest,
)
def retrieve_user_documents(req: DocumentSearchRequest) -> str:
    print(f"AI Tool: Retrieving documents for query: '{req.query}'")
    retrieved_docs = vector_db_service.retrieve(req.query, k=3)
    return "\n\n---\n\n".join([doc['text'] for doc in retrieved_docs])

class AIService:
    def __init__(self, embedder, generator):
        self.embedder = embedder
        self.generator = generator

    def generate_document_agentic(self, job_description: str) -> GeneratedContent:
        agent_prompt = f"{config.GENERATION_SYSTEM_PROMPT}\n\n**HERE IS THE JOB DESCRIPTION:**\n{job_description}"
        try:
            response = genai.generate_text(
                model=self.generator,
                prompt=agent_prompt,
                config={"response_format": "json"},
                tools=[retrieve_user_documents, company_deep_dive]
            )
            return GeneratedContent.model_validate_json(response.result)
        except Exception as e:
            print(f"Error in document generation flow: {e}")
            raise

    def prepare_for_interview_agentic(self, job_description: str, resume_text: str, cover_letter_text: str) -> InterviewPrepOutput:
        agent_prompt = f"{config.INTERVIEW_PREP_SYSTEM_PROMPT}\n\n**JOB DESCRIPTION:**\n{job_description}\n\n**CANDIDATE'S RESUME:**\n{resume_text}\n\n**CANDIDATE'S COVER LETTER:**\n{cover_letter_text}"
        try:
            response = genai.generate_text(
                model=self.generator,
                prompt=agent_prompt,
                config={"response_format": "json"},
                tools=[company_deep_dive]
            )
            return InterviewPrepOutput.model_validate_json(response.result)
        except Exception as e:
            print(f"Error in interview prep flow: {e}")
            raise

ai_service = AIService(
    embedder=config.EMBEDDER_MODEL,
    generator=config.GENERATOR_MODEL
)