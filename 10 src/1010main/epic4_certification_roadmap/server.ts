const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const RealTimeAPI = require('./api/realTimeApi').default;
import { Request, Response } from 'express';
const app = express();
const port = 3001;

// Serve static files
app.use(express.static(path.join(__dirname)));
app.use(bodyParser.json());

// Serve the test page
app.get('/', (req: Request, res: Response) => {
    res.sendFile(path.join(__dirname, 'test.html'));
});

// API endpoint for skill gap analysis (now using spaCy-based extraction)
app.post('/api/skillgap/analyze', async (req: Request, res: Response) => {
    const { resume } = req.body;
    try {
        // Use the new spaCy-based skill extraction and certification mapping
        const { extractSkillsWithSpacy, mapSkillsToCertifications } = require('./api/skillCertApi');
        const skills = await extractSkillsWithSpacy(resume);
        const certifications = mapSkillsToCertifications(skills);
        res.json({ skills, certifications });
    } catch (error: unknown) {
        let message = 'Unknown error';
        if (error && typeof error === 'object' && 'message' in error) {
            message = (error as any).message;
        }
        res.status(500).json({ error: 'Skill analysis failed', details: message });
    }
});

// API endpoint for skill and certification analysis
app.post('/api/skillcert/analyze', async (req: Request, res: Response) => {
    const { resume } = req.body;
    try {
        // Dynamically import to avoid circular issues
        const { extractSkillsWithSpacy, mapSkillsToCertifications } = require('./api/skillCertApi');
        const skills = await extractSkillsWithSpacy(resume);
        const certifications = mapSkillsToCertifications(skills);
        res.json({ skills, certifications });
    } catch (error: unknown) {
        let message = 'Unknown error';
        if (error && typeof error === 'object' && 'message' in error) {
            message = (error as any).message;
        }
        res.status(500).json({ error: 'Skill/certification analysis failed', details: message });
    }
});

app.listen(port, () => {
    console.log(`Test server running at http://localhost:${port}`);
}); 