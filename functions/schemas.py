# functions/schemas.py
from zod import z

# Schema for Agent 1: Document Writer & Job Analyzer
JobDescription = z.object({
    'job_description': z.string(),
})

GeneratedContent = z.object({
    'analysis': z.string(),
    'cover_letter': z.string(),
    'resume_summary': z.string(),
})

# Schema for Agent 2: Supercharged Interview Coach
InterviewPrepData = z.object({
    'job_description': z.string(),
    'resume': z.string(),
    'cover_letter': z.string(),
})

InterviewPrepOutput = z.object({
    'company_insights': z.string(),
    'key_competencies': z.array(z.string()),
    'interview_questions': z.array(z.string()),
})

# Schema for Authenticated User Data
class User(z.Base):
    uid: str
    email: str