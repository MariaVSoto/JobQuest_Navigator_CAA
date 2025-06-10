import openai
from models.suggestion import Suggestion
from typing import List, Dict
import os

class AIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key

    def generate_suggestions(self, resume: Dict, job: Dict) -> List[Suggestion]:
        """
        Generate suggestions for improving the resume based on the job description
        """
        try:
            # Prepare the prompt for OpenAI
            prompt = self._create_prompt(resume, job)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional resume reviewer and career coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Parse the response and create suggestions
            suggestions = self._parse_ai_response(response.choices[0].message.content)
            return suggestions

        except Exception as e:
            raise Exception(f"Error generating suggestions: {str(e)}")

    def _create_prompt(self, resume: Dict, job: Dict) -> str:
        """
        Create a prompt for the AI model
        """
        return f"""
        Please analyze this resume against the job description and provide specific suggestions for improvement.
        
        Job Title: {job.get('title')}
        Job Description: {job.get('description')}
        
        Resume Content:
        {resume.get('content')}
        
        Please provide suggestions in the following areas:
        1. Keywords and skills to add
        2. Format improvements
        3. Content enhancements
        
        Format each suggestion with:
        - Type (keyword/format/content)
        - Specific suggestion
        - Confidence score (0-1)
        """

    def _parse_ai_response(self, response: str) -> List[Suggestion]:
        """
        Parse the AI response into structured suggestions
        """
        suggestions = []
        # Implementation of parsing logic
        # This would convert the AI's text response into structured Suggestion objects
        return suggestions 