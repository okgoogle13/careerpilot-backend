# functions/flows/interview_flow.py

import genkit

# 1. Import from our centralized modules
# Schemas define the data structure for input, output, and the authenticated user.
from functions.schemas import InterviewPrepData, InterviewPrepOutput, User
# Services provide access to external APIs like Perplexity or Pinecone.
from functions.services.ai_service import perplexity_client
# The config file holds non-secret settings like model names.
from functions.config import DEFAULT_GENERATION_MODEL


# 2. Define the Genkit flow
# This flow represents the "Supercharged Interview Coach" agent.
@genkit.flow(
    name="interviewPrepFlow",
    input_schema=InterviewPrepData,
    output_schema=InterviewPrepOutput,
)
def interviewPrepFlow(data: InterviewPrepData, user: User) -> InterviewPrepOutput:
    """
    This agent takes a job description and user documents to generate a
    comprehensive and personalized interview preparation guide.

    Args:
        data: The input data containing the job description, resume, and cover letter.
        user: The authenticated user object, provided by the auth dependency.
    """
    print(f"Agent 'interviewPrepFlow' started for user: {user.uid} ({user.email}).")
    print("Analyzing job description for interview prep...")

    # 3. Use the imported services (Agent Tools)
    # This demonstrates how the agent would use its tools to gather information.
    # In a real implementation, you might extract the company name from the job description.
    company_name = "ExampleCorp" # Placeholder
    company_insights_data = perplexity_client.company_deep_dive(company_name)


    # 4. Construct the prompt for the generative model
    # This is where the core "intelligence" of the agent lies. You would create a
    # detailed prompt that includes the job description, user's documents, and the
    # data gathered from your tools.
    prompt = f"""
        You are an expert career coach for the Australian Community Services sector.
        Based on the user's resume, cover letter, and deep company insights, generate
        a set of likely interview questions and key competencies to highlight.

        Company Insights: {company_insights_data['culture']}
        Job Description: {data.job_description}
        User's Resume: {data.resume}

        Generate a list of 5 key competencies and 5 potential interview questions.
    """

    # 5. Call the generative model
    # In a real implementation, you would use a Genkit model object here.
    # llm = genkit.get_model(DEFAULT_GENERATION_MODEL)
    # result = await llm.generate(prompt)
    # For now, we use placeholder data.

    # 6. Format and return the structured output
    # The output must conform to the InterviewPrepOutput schema.
    return {
        "company_insights": f"Key insight based on research: {company_insights_data['culture']}",
        "key_competencies": [
            "Stakeholder Engagement (as seen in resume)",
            "Client-Centered Care",
            "NDIS Frameworks Compliance",
            "Team Leadership and Collaboration",
            "Crisis Management"
        ],
        "interview_questions": [
            "Tell me about a time you managed a complex client case from start to finish.",
            "Describe a situation where you had a conflict with a stakeholder. How did you resolve it?",
            "How do you stay up-to-date with changes to the NDIS?",
            "What is your greatest weakness?",
            "Why do you want to work for our organization specifically?"
        ]
    }