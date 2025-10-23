"""AI-powered candidate scoring service."""
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class AIScorerService:
    """Service for scoring candidates against job descriptions."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    async def score_candidate(
        self,
        candidate_profile: Dict[str, Any],
        job_description: str,
        required_skills: List[str]
    ) -> Dict[str, float]:
        """
        Score a candidate against a job description.
        
        Args:
            candidate_profile: Parsed candidate information
            job_description: Job description text
            required_skills: List of required skills for the job
            
        Returns:
            Dictionary containing scores
        """
        try:
            candidate_summary = f"""
Candidate Profile:
- Name: {candidate_profile.get('name', 'N/A')}
- Skills: {', '.join(candidate_profile.get('skills', []))}
- Experience: {candidate_profile.get('experience_years', 0)} years
- Education: {candidate_profile.get('education', 'N/A')}
"""
            
            prompt = f"""
You are an expert recruiter. Score this candidate against the job requirements.

{candidate_summary}

Job Description:
{job_description}

Required Skills:
{', '.join(required_skills)}

Provide scores (0-100) for the following criteria:
1. skill_fit: How well the candidate's skills match the required skills
2. experience_fit: How well the candidate's experience level matches the job requirements
3. education_fit: How well the candidate's education matches the job requirements
4. keyword_match: How well the candidate's profile matches keywords in the job description

Return ONLY a valid JSON object with these four scores and an overall_score (weighted average: skill_fit 40%, experience_fit 30%, education_fit 15%, keyword_match 15%).

Example format:
{{
  "skill_fit": 85.0,
  "experience_fit": 75.0,
  "education_fit": 90.0,
  "keyword_match": 80.0,
  "overall_score": 82.5
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert recruiter who scores candidates objectively based on job requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            scores = json.loads(result_text.strip())
            
            # Validate scores
            required_keys = ["skill_fit", "experience_fit", "education_fit", "keyword_match", "overall_score"]
            for key in required_keys:
                if key not in scores:
                    raise ValueError(f"Missing score: {key}")
                if not isinstance(scores[key], (int, float)):
                    raise ValueError(f"Invalid score type for {key}")
                if not 0 <= scores[key] <= 100:
                    raise ValueError(f"Score out of range for {key}: {scores[key]}")
            
            logger.info(f"Successfully scored candidate: {candidate_profile.get('name', 'Unknown')} - Overall: {scores['overall_score']}")
            return scores
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from OpenAI response: {e}")
            logger.error(f"Response text: {result_text}")
            raise ValueError("Failed to score candidate: Invalid JSON response from AI")
        except Exception as e:
            logger.error(f"Error scoring candidate with AI: {e}")
            raise


# Singleton instance
ai_scorer_service = AIScorerService()

