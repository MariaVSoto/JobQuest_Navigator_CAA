"""
PDF Processing Service for Resume Parsing
"""

import logging
import re
import io
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None

logger = logging.getLogger(__name__)


class PDFParsingService:
    """Service for parsing PDF resumes and extracting structured data"""
    
    def __init__(self):
        """Initialize the PDF parsing service"""
        if not PyPDF2 or not pdfplumber:
            logger.warning("PDF processing libraries not available. Install PyPDF2 and pdfplumber.")
    
    def extract_text_from_pdf(self, pdf_data: bytes) -> str:
        """Extract raw text from PDF file"""
        try:
            # Try pdfplumber first (better text extraction)
            if pdfplumber:
                with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text
            
            # Fallback to PyPDF2
            if PyPDF2:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            
            raise Exception("No PDF processing libraries available")
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def parse_resume_data(self, pdf_text: str) -> Dict[str, Any]:
        """Parse structured resume data from PDF text"""
        try:
            # Clean and normalize text
            text = self._clean_text(pdf_text)
            
            extracted_data = {
                'personal_info': self._extract_personal_info(text),
                'summary': self._extract_summary(text),
                'experience': self._extract_experience(text),
                'education': self._extract_education(text),
                'skills': self._extract_skills(text),
                'projects': self._extract_projects(text)
            }
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error parsing resume data: {e}")
            raise Exception(f"Failed to parse resume data: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize PDF text"""
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\n', ' ')
        return text.strip()
    
    def _extract_personal_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract personal information from resume text"""
        personal_info = {
            'full_name': None,
            'email': None,
            'phone': None,
            'location': None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            personal_info['email'] = email_match.group()
        
        # Extract phone number
        phone_patterns = [
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            r'\b\d{3}-\d{3}-\d{4}\b',
            r'\b\(?(\d{3})\)?\s*-?\s*(\d{3})\s*-?\s*(\d{4})\b'
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                personal_info['phone'] = phone_match.group()
                break
        
        # Extract name (first significant text, often at the beginning)
        lines = text.split('\n')[:5]  # Check first few lines
        for line in lines:
            line = line.strip()
            if len(line) > 2 and len(line.split()) <= 4:  # Likely a name
                # Avoid headers like "RESUME", "CV", etc.
                if not re.search(r'\b(resume|cv|curriculum|vitae)\b', line.lower()):
                    if not re.search(r'@|\d{3}[-.\s]\d{3}', line):  # Not email or phone
                        personal_info['full_name'] = line
                        break
        
        # Extract location (common patterns)
        location_patterns = [
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City, ST
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City Name, ST
            r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b'  # City, Country
        ]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, text)
            if location_match:
                personal_info['location'] = location_match.group()
                break
        
        return personal_info
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary or objective"""
        summary_keywords = [
            'summary', 'objective', 'profile', 'overview', 'about',
            'professional summary', 'career objective', 'career summary'
        ]
        
        for keyword in summary_keywords:
            pattern = rf'\b{keyword}\b:?\s*(.{{1,500}}?)(?:\n\n|\b(?:experience|education|skills|work|employment)\b)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 20:  # Minimum length for meaningful summary
                    return summary
        
        return None
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text"""
        experience = []
        
        # Find experience section
        exp_keywords = ['experience', 'work', 'employment', 'professional experience', 'work history']
        
        for keyword in exp_keywords:
            pattern = rf'\b{keyword}\b(.*?)(?:\b(?:education|skills|projects|certifications)\b|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                exp_section = match.group(1)
                experience = self._parse_experience_entries(exp_section)
                break
        
        return experience
    
    def _parse_experience_entries(self, exp_text: str) -> List[Dict[str, Any]]:
        """Parse individual experience entries"""
        entries = []
        
        # Split by potential job entries (dates often indicate new entries)
        date_pattern = r'\b(?:20\d{2}|19\d{2})\b'
        parts = re.split(f'({date_pattern})', exp_text)
        
        current_entry = {}
        for i, part in enumerate(parts):
            if re.match(date_pattern, part):
                # This is a date
                if current_entry:
                    entries.append(current_entry)
                current_entry = {
                    'start_date': part,
                    'end_date': None,
                    'current': False,
                    'company': None,
                    'position': None,
                    'description': None
                }
            elif current_entry and part.strip():
                # Extract company and position from the text
                lines = part.strip().split('\n')[:3]  # First few lines likely contain company/position
                for line in lines:
                    line = line.strip()
                    if line and not current_entry.get('company'):
                        current_entry['company'] = line
                    elif line and not current_entry.get('position'):
                        current_entry['position'] = line
                    else:
                        break
                
                # Rest is description
                if len(lines) > 2:
                    current_entry['description'] = ' '.join(lines[2:])
        
        if current_entry:
            entries.append(current_entry)
        
        return entries[:5]  # Limit to 5 most recent entries
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        education = []
        
        # Find education section
        edu_keywords = ['education', 'academic', 'qualifications', 'degrees']
        
        for keyword in edu_keywords:
            pattern = rf'\b{keyword}\b(.*?)(?:\b(?:experience|skills|projects|certifications)\b|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                edu_section = match.group(1)
                education = self._parse_education_entries(edu_section)
                break
        
        return education
    
    def _parse_education_entries(self, edu_text: str) -> List[Dict[str, Any]]:
        """Parse individual education entries"""
        entries = []
        
        # Common degree patterns
        degree_patterns = [
            r'\b(bachelor|master|phd|doctorate|associate|b\.?[as]\.?|m\.?[as]\.?|ph\.?d\.?)\b',
            r'\b(degree|diploma|certificate)\b'
        ]
        
        lines = edu_text.split('\n')
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line contains a degree
            for pattern in degree_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if current_entry:
                        entries.append(current_entry)
                    
                    current_entry = {
                        'degree': line,
                        'school': None,
                        'field': None,
                        'start_date': None,
                        'end_date': None,
                        'current': False,
                        'gpa': None
                    }
                    
                    # Extract year if present
                    year_match = re.search(r'\b(20\d{2}|19\d{2})\b', line)
                    if year_match:
                        current_entry['end_date'] = year_match.group()
                    
                    break
            else:
                # This line might contain school name
                if current_entry and not current_entry.get('school'):
                    current_entry['school'] = line
        
        if current_entry:
            entries.append(current_entry)
        
        return entries[:3]  # Limit to 3 entries
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        skills = []
        
        # Find skills section
        skills_keywords = ['skills', 'technical skills', 'core competencies', 'technologies', 'expertise']
        
        for keyword in skills_keywords:
            pattern = rf'\b{keyword}\b:?\s*(.*?)(?:\n\n|\b(?:experience|education|projects|certifications)\b|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                skills_text = match.group(1)
                skills = self._parse_skills_list(skills_text)
                break
        
        # If no dedicated skills section, extract common technical terms
        if not skills:
            skills = self._extract_technical_terms(text)
        
        return skills[:20]  # Limit to 20 skills
    
    def _parse_skills_list(self, skills_text: str) -> List[str]:
        """Parse skills from skills section text"""
        skills = []
        
        # Split by common delimiters
        skill_items = re.split(r'[,\n•·\-\|]', skills_text)
        
        for item in skill_items:
            skill = item.strip()
            if skill and len(skill) > 1 and len(skill) < 50:  # Reasonable skill length
                skills.append(skill)
        
        return skills
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract common technical terms from the entire text"""
        # Common technical skills and tools
        tech_terms = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'React', 'Angular', 'Vue',
            'Node.js', 'Django', 'Flask', 'FastAPI', 'Spring', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
            'Git', 'Linux', 'HTML', 'CSS', 'TypeScript', 'GraphQL', 'REST',
            'Machine Learning', 'AI', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy'
        ]
        
        found_skills = []
        for term in tech_terms:
            if re.search(rf'\b{re.escape(term)}\b', text, re.IGNORECASE):
                found_skills.append(term)
        
        return found_skills
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract project information"""
        projects = []
        
        # Find projects section
        project_keywords = ['projects', 'personal projects', 'portfolio', 'work samples']
        
        for keyword in project_keywords:
            pattern = rf'\b{keyword}\b(.*?)(?:\b(?:experience|education|skills|certifications)\b|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                project_section = match.group(1)
                projects = self._parse_project_entries(project_section)
                break
        
        return projects
    
    def _parse_project_entries(self, project_text: str) -> List[Dict[str, Any]]:
        """Parse individual project entries"""
        entries = []
        
        # Split by bullet points or line breaks
        lines = project_text.split('\n')
        current_project = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # New project (usually starts with project name)
            if not current_project.get('name') and len(line) < 100:
                current_project = {
                    'name': line,
                    'description': None,
                    'technologies': None,
                    'link': None
                }
            elif current_project:
                # Check if this is a URL
                if re.search(r'https?://', line):
                    current_project['link'] = line
                    entries.append(current_project)
                    current_project = {}
                else:
                    # Add to description
                    if current_project.get('description'):
                        current_project['description'] += ' ' + line
                    else:
                        current_project['description'] = line
        
        if current_project:
            entries.append(current_project)
        
        return entries[:5]  # Limit to 5 projects


# Global instance
pdf_service = PDFParsingService()