"""AI-powered CV parsing service."""
import io
import json
import logging
from typing import Dict, Any
import PyPDF2
from docx import Document
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class AIParserService:
    """Service for parsing CVs using AI."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text from file based on extension."""
        if filename.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_content)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    async def parse_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Parse CV text using OpenAI to extract structured information.
        
        Args:
            cv_text: Raw text extracted from CV
            
        Returns:
            Dictionary containing parsed information
        """
        try:
            prompt = f"""
Extract the following information from this CV/resume text and return it as a JSON object:
- name (string): Full name of the candidate
- email (string): Email address
- phone (string): Phone number
- linkedin (string): LinkedIn profile URL (if available)
- skills (array of strings): List of technical and professional skills
- experience_years (number): Total years of work experience
- education (string): Highest education degree and institution

CV Text:
{cv_text}

Return ONLY a valid JSON object with the above fields. If a field is not found, use null for strings/numbers or empty array for skills.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert CV parser. Extract structured information from resumes accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            parsed_data = json.loads(result_text.strip())
            
            logger.info(f"Successfully parsed CV for: {parsed_data.get('name', 'Unknown')}")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from OpenAI response: {e}")
            logger.error(f"Response text: {result_text}")
            raise ValueError("Failed to parse CV: Invalid JSON response from AI")
        except Exception as e:
            logger.error(f"Error parsing CV with AI: {e}")
            raise


# Singleton instance
ai_parser_service = AIParserService()

