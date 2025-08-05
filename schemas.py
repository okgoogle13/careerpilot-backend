from pydantic import BaseModel, Field
from typing import List

class GeneratedContent(BaseModel):
    """Defines the structured output for the AI model."""
    cover_letter_text: str = Field(description="The full, generated text of the cover letter.")
    resume_text: str = Field(description="The generated 2-3 paragraph resume summary.")
    extracted_keywords: List[str] = Field(description="A list of the top 5-7 skills and keywords extracted from the job description.")
    suggested_tone: str = Field(description="The tone of voice used for the generated content (e.g., 'Professional and Enthusiastic').")
