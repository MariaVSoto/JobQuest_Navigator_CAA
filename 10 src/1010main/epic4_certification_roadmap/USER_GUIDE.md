# Epic 4 Certification Roadmap - User Guide

This guide will help you set up, install, and run the Epic 4 Skill Gap Analysis tool on your local machine.

## Prerequisites
- Node.js (v16 or higher)
- npm (v8 or higher)
- Python 3 (for spaCy skill extraction)
- spaCy and en_core_web_sm model (see below)
- Git

## Installation Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/MariaVSoto/JobQuest_Navigator_CAA.git
   cd "JobQuest_Navigator_CAA/10 src/1010main/epic4_certification_roadmap"
   ```
2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```
3. **Install Python dependencies:**
   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
   ```
4. **Start the development server:**
   ```bash
   npx ts-node server.ts
   ```
5. **Open the test page:**
   - Go to [http://localhost:3001](http://localhost:3001) in your browser.

## Usage
- Paste your resume and enter your target role in the form.
- Click "Analyze Skills" to view your extracted skills and recommended certifications.
- The tool uses AI/NLP (spaCy) to extract skills from your resume and filters out generic/common words for more accurate results.

## Troubleshooting
- If you see errors about missing modules, run `npm install` (for Node) and `pip install spacy` (for Python) again.
- If the server does not start, make sure no other process is using port 3001.
- For Windows users, use PowerShell or Command Prompt as administrator if you encounter permission issues.
- If you see errors about missing spaCy models, run `python -m spacy download en_core_web_sm`.

## Notes
- All code for Epic 4 is self-contained in the `epic4_certification_roadmap` folder.
- For any issues, contact Ishan or open an issue in the repository. 