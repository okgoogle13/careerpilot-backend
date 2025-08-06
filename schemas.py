from pydantic import BaseModel, Field
from typing import List, Optional

# --- Schemas for Agent 1: Document Writer & Analyzer ---

class JobAnalysis(BaseModel):
    """A structured analysis of the job description."""
    experience_level: str = Field(description="The estimated experience level required (e.g., 'Entry-level', 'Mid-level', 'Senior').")
    top_3_must_haves: List[str] = Field(description="A list of the three most critical, non-negotiable qualifications mentioned.")
    potential_red_flags: str = Field(description="Any potential red flags or unusual requirements noted in the job description (e.g., 'Vague responsibilities', 'Extensive travel required').")

class GeneratedContent(BaseModel):
    """Defines the structured output for the Document Writer Agent."""
    analysis: JobAnalysis
    cover_letter_text: str = Field(description="The full, generated text of the cover letter.")
    resume_text: str = Field(description="The generated 2-3 paragraph resume summary.")
    extracted_keywords: List[str] = Field(description="A list of the top 5-7 skills and keywords extracted from the job description.")
    suggested_tone: str = Field(description="The tone of voice used for the generated content.")

# --- Schemas for Agent 2: Supercharged Interview Coach ---

class CompanyInsights(BaseModel):
    culture_and_values: str = Field(description="A summary of the company's culture and core values.")
    recent_news_or_projects: str = Field(description="A brief on recent company news or key projects relevant to the role.")

class KeyCompetency(BaseModel):
    competency: str = Field(description="A key skill or competency required by the job description.")
    framing_suggestion: str = Field(description="A suggestion on how the candidate can frame their experience to highlight this competency, using their resume as a reference.")

class InterviewQuestion(BaseModel):
    question: str = Field(description="The interview question.")
    category: str = Field(description="The category of the question (e.g., 'Behavioral', 'Technical', 'Situational').")
    suggested_answer_points: List[str] = Field(description="Bullet-point speaking notes for a strong answer, tailored from the candidate's resume and cover letter.")

class WeaknessQuestionApproach(BaseModel):
    strategy: str = Field(description="The recommended strategy for answering the 'what are your weaknesses?' question.")
    example_answer: str = Field(description="A tailored example answer based on the candidate's profile.")

class InterviewPrepOutput(BaseModel):
    """Defines the structured output for the Supercharged Interview Coach Agent."""
    company_insights: CompanyInsights = Field(description="Crucial background information about the hiring organization.")
    key_competencies_to_highlight: List[KeyCompetency] = Field(description="The most important skills to focus on and how to frame them.")
    potential_questions: List[InterviewQuestion] = Field(description="A list of likely interview questions with tailored talking points.")
    weakness_question_approach: WeaknessQuestionApproach = Field(description="A specific strategy and example for the 'greatest weakness' question.")
    questions_to_ask_interviewer: List[str] = Field(description="A list of insightful questions the candidate should ask.")
    thank_you_note_draft: str = Field(description="A professionally written draft of a thank-you email to the interviewer.")