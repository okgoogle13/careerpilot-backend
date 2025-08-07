# functions/flows/generation_flow.py

import genkit

# 1. Import all necessary modules
# Schemas for data structure and user authentication
from functions.schemas import JobDescription, GeneratedContent, User
# The generative model configuration
from functions.config import DEFAULT_GENERATION_MODEL
# The services that act as our agent's tools
from functions.services.ai_service import perplexity_client
from functions.services.vector_db_service import pinecone_client


# 2. Define the Genkit flow for the "Document Writer & Job Analyzer" agent
@genkit.flow(
    name="generateFlow",
    input_schema=JobDescription,
    output_schema=GeneratedContent,
)
def generateFlow(data: JobDescription, user: User) -> GeneratedContent:
    """
    This agent analyzes a job description and uses Retrieval-Augmented Generation (RAG)
    to create application documents tailored to the user's experience stored in Pinecone.

    Args:
        data: The input containing the job description.
        user: The authenticated user object from the auth dependency.
    """
    print(f"Agent 'generateFlow' started for user: {user.uid} ({user.email}).")
    
    # 3. Use the vector DB service to retrieve user-specific context (RAG)
    # This is the "retrieveUserDocuments" tool in action.
    # We query for context related to the job description itself.
    if pinecone_client:
        context_from_db = pinecone_client.query_for_context(
            query_text=data.job_description,
            user_id=user.uid,
            top_k=3 # Get the top 3 most relevant chunks of experience
        )
    else:
        print("WARN: Pinecone client not available. Proceeding without RAG context.")
        context_from_db = []

    # Join the retrieved text chunks into a single string for the prompt
    retrieved_experience = "\n- ".join(context_from_db)

    # 4. Construct a more powerful prompt using the retrieved context
    # This is the "Augmented" part of RAG. We are augmenting the prompt with facts.
    prompt = f"""
        You are an expert career document writer for the Australian Community Services sector.
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

    # 5. Call the generative model (placeholder for now)
    # llm = genkit.get_model(DEFAULT_GENERATION_MODEL)
    # result = await llm.generate(prompt)

    # 6. Format and return the structured output, now powered by RAG
    return {
        "analysis": "This role requires strong stakeholder engagement, a skill clearly demonstrated in your past projects.",
        "cover_letter": f"As demonstrated in my background, where I {context_from_db[0] if context_from_db else 'managed complex cases'}, I am confident I possess the skills required for this role.",
        "resume_summary": f"A summary that now reflects your specific experience: {retrieved_experience}",
    }