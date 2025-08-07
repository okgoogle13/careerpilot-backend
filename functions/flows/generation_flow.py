# functions/flows/generation_flow.py

import genkit
import json

# 1. Import all necessary modules
from functions.schemas import JobDescription, GeneratedContent, User
from functions.config import DEFAULT_GENERATION_MODEL
from functions.services.vector_db_service import pinecone_client


# 2. Define the Genkit flow for the "Document Writer & Job Analyzer" agent
@genkit.flow(
    name="generateFlow",
    input_schema=JobDescription,
    output_schema=GeneratedContent,
)
async def generateFlow(data: JobDescription, user: User) -> GeneratedContent:
    """
    This agent analyzes a job description and uses Retrieval-Augmented Generation (RAG)
    to create application documents tailored to the user's experience stored in Pinecone.

    Args:
        data: The input containing the job description.
        user: The authenticated user object from the auth dependency.
    """
    print(f"Agent 'generateFlow' started for user: {user.uid} ({user.email}).")
    
    # 3. Use the vector DB service to retrieve user-specific context (RAG)
    context_from_db = []
    if pinecone_client:
        print("Retrieving context from vector database...")
        context_from_db = await pinecone_client.query_for_context(
            query_text=data.job_description,
            user_id=user.uid,
            top_k=3
        )
    else:
        print("WARN: Pinecone client not available. Proceeding without RAG context.")

    retrieved_experience = "\n- ".join(context_from_db)

    # 4. Construct a powerful prompt using the retrieved context
    prompt = f"""
        You are an expert career document writer for the Australian Community Services sector.
        You MUST return a valid JSON object with the following keys: "analysis", "cover_letter", "resume_summary".

        A user is applying for a job with the following description:
        ---
        JOB DESCRIPTION: {data.job_description}
        ---

        I have retrieved the most relevant experience from the user's stored documents:
        ---
        RELEVANT USER EXPERIENCE:
        - {retrieved_experience}
        ---

        Based on BOTH the job description and the user's specific experience, perform the following tasks:
        1.  **Analysis:** Provide a brief analysis of the job.
        2.  **Cover Letter:** Draft a paragraph for a cover letter that highlights the user's relevant experience.
        3.  **Resume Summary:** Draft a 3-bullet point resume summary that directly targets this job.
    """

    # 5. Call the generative model
    print("Generating content with the LLM...")
    llm = genkit.get_model(DEFAULT_GENERATION_MODEL)
    result = await llm.generate(prompt)
    raw_text_output = result.text()
    print(f"LLM Raw Output: {raw_text_output}")

    # 6. Parse the model's response and return the structured output
    try:
        # The model should return a parsable JSON string.
        output_data = json.loads(raw_text_output)
        # Use the schema to validate and instantiate the output object.
        return GeneratedContent(**output_data)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error decoding JSON from model response: {e}")
        # Provide a structured error that fits the schema
        return GeneratedContent(
            analysis="Error: Failed to parse content from AI model.",
            cover_letter="Error: Failed to parse content from AI model.",
            resume_summary="Error: Failed to parse content from AI model."
        )