# functions/flows/interview_flow.py

import genkit
import json

# 1. Import from our centralized modules
from functions.schemas import InterviewPrepData, InterviewPrepOutput, User
from functions.services.ai_service import perplexity_client
from functions.config import DEFAULT_GENERATION_MODEL


# 2. Define the Genkit flow
@genkit.flow(
    name="interviewPrepFlow",
    input_schema=InterviewPrepData,
    output_schema=InterviewPrepOutput,
)
async def interviewPrepFlow(data: InterviewPrepData, user: User) -> InterviewPrepOutput:
    """
    This agent takes a job description and user documents to generate a
    comprehensive and personalized interview preparation guide.
    """
    print(f"Agent 'interviewPrepFlow' started for user: {user.uid} ({user.email}).")

    # 3. Use the imported services (Agent Tools)
    # The Perplexity client is a mock, so this will return placeholder data.
    # In a real implementation, you would extract the company name from the job description.
    company_name = "ExampleCorp" # Placeholder
    company_insights_data = perplexity_client.company_deep_dive(company_name)

    # 4. Construct the prompt for the generative model
    prompt = f"""
        You are an expert career coach for the Australian Community Services sector.
        You MUST return a valid JSON object with the following keys: "company_insights", "key_competencies", "interview_questions".
        The "key_competencies" and "interview_questions" fields must be arrays of strings.

        Based on the user's resume, cover letter, and deep company insights, generate
        a set of likely interview questions and key competencies to highlight.

        Company Insights: {company_insights_data['culture']}
        Job Description: {data.job_description}
        User's Resume: {data.resume}

        Generate a list of 5 key competencies and 5 potential interview questions.
    """

    # 5. Call the generative model
    print("Generating interview prep with the LLM...")
    llm = genkit.get_model(DEFAULT_GENERATION_MODEL)
    result = await llm.generate(prompt)
    raw_text_output = result.text()
    print(f"LLM Raw Output: {raw_text_output}")


    # 6. Format and return the structured output
    try:
        output_data = json.loads(raw_text_output)
        # Use the schema to validate and instantiate the output object.
        return InterviewPrepOutput(**output_data)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error decoding JSON from model response: {e}")
        # Provide a structured error that fits the schema
        return InterviewPrepOutput(
            company_insights="Error: Failed to parse content from AI model.",
            key_competencies=["Error: Failed to parse content from AI model."],
            interview_questions=["Error: Failed to parse content from AI model."]
        )