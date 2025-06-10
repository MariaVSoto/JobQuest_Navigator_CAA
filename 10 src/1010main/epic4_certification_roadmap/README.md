# Skill Gap Analysis Tool (Epic 4)

A modern skill analysis tool that uses AI/NLP (spaCy) to extract relevant skills from your resume and recommends certifications for each skill.

## Features
- AI-powered skill extraction using spaCy (Python)
- Accurate filtering of generic/common words
- Certification recommendations for each extracted skill
- Simple web-based test page (test.html)
- Easy local setup (Node.js + Python)

## Technologies Used
- Node.js
- Express.js
- TypeScript
- Python 3
- spaCy (en_core_web_sm)

## Installation

1. **Clone the repository:**
```bash
git clone [your-repository-url]
cd "[repository-name]/10 src/1010main/epic4_certification_roadmap"
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

5. **Open your browser and navigate to** `http://localhost:3001`

## Project Structure
```
epic4_certification_roadmap/
├── api/
│   └── skillCertApi.ts
├── extract_skills.py
├── test.html
├── server.ts
├── certificationMap.json
├── skills-list.json
├── package.json
├── tsconfig.json
├── ...
```

## Usage
1. Enter your resume in the text area on the test page
2. (Optionally) Enter your target role
3. Click "Analyze Skills" to get:
   - Extracted skills (AI/NLP-based)
   - Recommended certifications for each skill

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- spaCy for NLP
- Open source community for tools and libraries 