import unittest
from ai_suggestion.services.openai_service import generate_resume_suggestions, generate_job_match_suggestions

class TestAISuggestions(unittest.TestCase):

    def test_generate_resume_suggestions(self):
        resume_text = "Experienced software engineer with expertise in Python and Django."
        suggestions = generate_resume_suggestions(resume_text)
        self.assertIsInstance(suggestions, str)
        self.assertTrue(len(suggestions) > 0)

    def test_generate_job_match_suggestions(self):
        resume_text = "Experienced software engineer with expertise in Python and Django."
        job_matches = generate_job_match_suggestions(resume_text)
        self.assertIsInstance(job_matches, str)
        self.assertTrue(len(job_matches) > 0)

if __name__ == '__main__':
    unittest.main()
