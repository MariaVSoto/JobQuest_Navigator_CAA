import spacy
import json
import os
from pathlib import Path
from collections import defaultdict

class SkillExtractor:
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Load known skills and certifications
        base_dir = Path(__file__).resolve().parent.parent
        skills_path = base_dir / "data" / "skills-list.json"
        cert_path = base_dir / "data" / "certificationMap.json"
        
        with open(skills_path, "r", encoding="utf-8") as f:
            skills_data = json.load(f)
            self.KNOWN_SKILLS = set([v.lower() for v in skills_data.values()])

        with open(cert_path, "r", encoding="utf-8") as f:
            self.CERT_MAP = json.load(f)

        # Generic skills to filter out
        self.GENERIC_SKILLS = {
            "communication", "teamwork", "leadership", "management",
            "project management", "customer service", "adaptability",
            "problem-solving", "research", "organization"
        }

        self.DOMAIN_MAP = [
            {
                'domain': 'it',
                'title_keywords': ["devops", "engineer", "developer", "it", "security", "cloud", "sysadmin", "linux", "python", "software", "network", "database", "data engineer", "administrator", "support"],
                'skill_keywords': ["python", "aws", "cloud", "devops", "linux", "sql", "security", "network", "infrastructure", "system administration", "database", "automation", "programming", "software", "azure", "gcp", "terraform", "ansible", "kubernetes", "docker", "penetration", "forensic", "cyber", "mlops"],
                'cert_name_patterns': ["aws", "azure", "gcp", "cloud", "devops", "security", "cissp", "oscp", "red hat", "python", "linux", "network", "sql", "database", "support", "comptia", "scrum", "agile", "machine learning", "data engineer", "data analytics", "data visualization", "tableau", "power bi", "oracle", "sas", "statistical", "predictive", "cbip", "ceh", "ccna", "gsec", "ccsp", "terraform", "ansible", "metasploit", "wireshark", "nmap", "sqlmap", "volatility"]
            },
            {
                'domain': 'data',
                'title_keywords': ["data analyst", "data scientist", "analytics", "bi", "business intelligence", "statistician", "data engineer"],
                'skill_keywords': ["data analysis", "data visualization", "tableau", "power bi", "sql", "statistics", "analytics", "predictive", "machine learning", "deep learning", "sas", "etl", "reporting", "data science", "data cleaning", "data interpretation", "data warehousing"],
                'cert_name_patterns': ["data analytics", "data visualization", "tableau", "power bi", "cbip", "predictive", "statistical", "sas", "machine learning", "deep learning", "data engineer"]
            },
            {
                'domain': 'sales',
                'title_keywords': ["sales", "crm", "account manager", "business development", "marketing", "customer service", "brand", "lead generation", "relationship manager"],
                'skill_keywords': ["sales", "crm", "lead generation", "customer service", "negotiation", "presentation", "branding", "brand management", "marketing", "communication", "business development", "account management", "relationship management", "pipeline", "prospecting", "closing", "customer relationship"],
                'cert_name_patterns': ["sales", "crm", "brand", "communication", "presentation", "business", "marketing", "brand management", "customer", "relationship", "effective communication", "brand management", "critical thinking", "problem-solving", "excel", "office", "pmp", "project management"]
            },
            {
                'domain': 'healthcare',
                'title_keywords': ["nurse", "medical", "health", "patient", "clinical", "pharmacy", "care", "bls", "acls", "emr", "medication"],
                'skill_keywords': ["nursing", "patient care", "healthcare", "clinical", "bls", "acls", "emr", "medication administration", "patient safety", "pharmacology", "medical records", "health information", "life support", "emergency care", "cardiac care"],
                'cert_name_patterns': ["nurse", "medical", "health", "bls", "acls", "emr", "medication", "patient", "clinical", "pharmacy", "life support", "emergency"]
            },
            {
                'domain': 'design',
                'title_keywords': ["designer", "ux", "ui", "visual", "creative", "branding", "art", "material design", "figma", "adobe", "canva", "interaction design"],
                'skill_keywords': ["design", "ux", "ui", "visual design", "graphic design", "branding", "adobe", "figma", "canva", "material design", "user experience", "user interface", "prototyping", "wireframing", "design systems", "art direction", "creative direction"],
                'cert_name_patterns': ["design", "ux", "ui", "adobe", "figma", "canva", "branding", "visual", "material design", "art direction", "interaction design", "prototyping", "wireframing"]
            },
            {
                'domain': 'project',
                'title_keywords': ["project manager", "scrum", "agile", "pmp", "product owner", "project coordinator"],
                'skill_keywords': ["project management", "scrum", "agile", "sprint planning", "stakeholder management", "team leadership", "project planning", "project execution", "product owner"],
                'cert_name_patterns': ["pmp", "project management", "scrum", "agile", "csm", "psm", "stakeholder", "team leadership"]
            }
        ]

    def normalize_skill(self, skill):
        """Normalize skill name for matching"""
        return skill.lower().strip()

    def extract_skills(self, text):
        """Extract skills from text using spaCy and known skills list, prioritizing multi-word and context skills."""
        doc = self.nlp(text)
        skills = set()
        # First, check for multi-word skills (bigrams)
        for i in range(len(doc) - 1):
            bigram = f"{self.normalize_skill(doc[i].text)} {self.normalize_skill(doc[i+1].text)}"
            if bigram in self.KNOWN_SKILLS and bigram not in self.GENERIC_SKILLS:
                skills.add(bigram)
        # Then, check for single-word skills
        for i, token in enumerate(doc):
            token_text = self.normalize_skill(token.text)
            if token_text in self.KNOWN_SKILLS and token_text not in self.GENERIC_SKILLS:
                skills.add(token_text)
            # Contextual match
            if token.pos_ in ['NOUN', 'PROPN']:
                context = ' '.join([t.text for t in doc[max(0, i-2):min(len(doc), i+3)]])
                for known_skill in self.KNOWN_SKILLS:
                    if known_skill in context.lower() and known_skill not in self.GENERIC_SKILLS:
                        skills.add(known_skill)
        return list(skills)

    def build_role_skill_profile(self, job_descriptions):
        """Build a skill profile from job descriptions"""
        profile = {
            'frequencies': defaultdict(int),
            'contexts': defaultdict(list)
        }
        
        for desc in job_descriptions:
            doc = self.nlp(desc)
            
            # Extract skills and their context
            for i, token in enumerate(doc):
                token_text = self.normalize_skill(token.text)
                
                # Check for exact matches
                if token_text in self.KNOWN_SKILLS and token_text not in self.GENERIC_SKILLS:
                    profile['frequencies'][token_text] += 1
                    context = ' '.join([t.text for t in doc[max(0, i-2):min(len(doc), i+3)]])
                    profile['contexts'][token_text].append(context)
                
                # Check for multi-word skills
                if i < len(doc) - 1:
                    bigram = f"{token_text} {self.normalize_skill(doc[i+1].text)}"
                    if bigram in self.KNOWN_SKILLS and bigram not in self.GENERIC_SKILLS:
                        profile['frequencies'][bigram] += 1
                        context = ' '.join([t.text for t in doc[max(0, i-2):min(len(doc), i+3)]])
                        profile['contexts'][bigram].append(context)
        
        return profile

    def detect_domain(self, job_title, skills):
        """Detect the most likely domain for a job based on title and skills."""
        title = (job_title or "").lower()
        skills_lower = set([self.normalize_skill(s) for s in (skills or [])])
        for entry in self.DOMAIN_MAP:
            if any(kw in title for kw in entry['title_keywords']):
                return entry['domain']
            if any(kw in skills_lower for kw in entry['skill_keywords']):
                return entry['domain']
        return None

    def get_certifications(self, skills, role_profile=None, job_title=None):
        """Get relevant certifications based on skills, role profile, and job title (for domain filtering)."""
        certifications = []
        seen_names = set()
        # Detect domain using job title and skills
        domain = self.detect_domain(job_title, skills)
        # Sort skills by frequency if role profile is provided
        if role_profile and 'frequencies' in role_profile:
            sorted_skills = sorted(
                skills,
                key=lambda x: role_profile['frequencies'].get(x, 0),
                reverse=True
            )
        else:
            sorted_skills = skills
        for skill in sorted_skills:
            skill_lower = self.normalize_skill(skill)
            for cert_skill, cert_data in self.CERT_MAP.items():
                if cert_data['name'] not in seen_names:
                    relevant_skills = cert_data.get('relevant_skills', [])
                    match_score = 0
                    matched_skills = []
                    for rel_skill in relevant_skills:
                        rel_skill_lower = rel_skill.lower()
                        if skill_lower == rel_skill_lower:
                            match_score += 3
                            matched_skills.append(rel_skill)
                        elif skill_lower.replace('/', ' ').replace('-', ' ') == rel_skill_lower.replace('/', ' ').replace('-', ' '):
                            match_score += 2
                            matched_skills.append(rel_skill)
                        elif skill_lower in rel_skill_lower and len(skill_lower) > 2:
                            match_score += 1
                            matched_skills.append(rel_skill)
                    # Only include certifications with significant matches
                    if match_score >= 3 and matched_skills:
                        # Filter by domain if detected
                        if domain:
                            domain_entry = next((d for d in self.DOMAIN_MAP if d['domain'] == domain), None)
                            if domain_entry:
                                # Only include certs whose name or relevant_skills match domain patterns
                                cert_name = cert_data['name'].lower()
                                cert_skills = [s.lower() for s in relevant_skills]
                                if not (any(pat in cert_name for pat in domain_entry['cert_name_patterns']) or any(pat in s for pat in domain_entry['cert_name_patterns'] for s in cert_skills)):
                                    continue
                        certifications.append({
                            'name': cert_data['name'],
                            'link': cert_data['link'],
                            'description': cert_data['description'],
                            'matched_skills': matched_skills,
                            'relevance_score': match_score
                        })
                        seen_names.add(cert_data['name'])
        certifications.sort(key=lambda x: x['relevance_score'], reverse=True)
        return certifications