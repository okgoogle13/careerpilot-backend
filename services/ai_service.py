import os
import json
import requests
import google.generativeai as genai
from pydantic import BaseModel

import config
from schemas import GeneratedContent, InterviewPrepOutput
from services.gcp_service import gcp_service
from services.vector_db_service import vector_db_service

# --- Agentic Tools ---

def company_deep_dive(company_name: str) -> str:
    """
    Performs a deep, synthesized research dive on a company to find its mission,
    values, culture, recent news, and key projects.
    """
    print(f"AI Tool: Performing deep dive for company: '{company_name}'")
    try:
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            api_key = gcp_service.get_secret("PERPLEXITY_API_KEY")
    except Exception as e:
        return f"Error: Perplexity API key is not configured. {e}"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3-sonar-large-32k-online",
        "messages": [
            {"role": "system", "content": "You are an expert business analyst. Provide a concise but comprehensive brief on the requested company."},
            {"role": "user", "content": f"Provide a business brief for the company: '{company_name}'. Focus on their mission, stated values, company culture, and any major recent news or projects relevant to someone applying for a job there."},
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

class AIService:
    def __init__(self, generator_model_name: str):
        # This model is configured for tool use and JSON output.
        self.generative_model = genai.GenerativeModel(model_name=generator_model_name)

    def generate_document_agentic(self, job_description: str, user_id: str) -> GeneratedContent:
        agent_prompt = f"{config.GENERATION_SYSTEM_PROMPT}\n\n**HERE IS THE JOB DESCRIPTION:**\n{job_description}"

        # Define the document retrieval tool within this scope to capture user_id
        def retrieve_user_documents(query: str) -> str:
            """
            Search and retrieve relevant text from the user's uploaded historical
            job application documents to understand their skills and writing style.
            """
            print(f"AI Tool: Retrieving documents for user '{user_id}' with query: '{query}'")
            retrieved_docs = vector_db_service.retrieve(query=query, user_id=user_id, k=5)
            if not retrieved_docs:
                return "No relevant documents found for the user."
            return "\n\n---\n\n".join([doc['text'] for doc in retrieved_docs])

        print(f"Starting AGENTIC workflow for user: {user_id}")
        try:
            response = self.generative_model.generate_content(
                agent_prompt,
                tools=[retrieve_user_documents, company_deep_dive],
                generation_config={"response_mime_type": "application/json"},
            )
            return GeneratedContent.model_validate_json(response.text)
        except Exception as e:
            print(f"Error in document generation flow: {e}")
            raise

    def prepare_for_interview_agentic(self, job_description: str, resume_text: str, cover_letter_text: str, user_id: str) -> InterviewPrepOutput:
        agent_prompt = f"{config.INTERVIEW_PREP_SYSTEM_PROMPT}\n\n**JOB DESCRIPTION:**\n{job_description}\n\n**CANDIDATE'S RESUME:**\n{resume_text}\n\n**CANDIDATE'S COVER LETTER:**\n{cover_letter_text}"

        print(f"Starting INTERVIEW PREP workflow for user: {user_id}")
        try:
            response = self.generative_model.generate_content(
                agent_prompt,
                tools=[company_deep_dive],
                generation_config={"response_mime_type": "application/json"},
            )
            return InterviewPrepOutput.model_validate_json(response.text)
        except Exception as e:
            print(f"Error in interview prep flow: {e}")
            raise

# Singleton instance
ai_service = AIService(generator_model_name=config.GENERATOR_MODEL)