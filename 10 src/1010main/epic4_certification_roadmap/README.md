# Skill Gap Analysis Tool

A real-time skill gap analysis tool that helps users identify their current skill levels, required skill levels for their target role, and provides personalized recommendations for skill development.

## Features

- Real-time skill analysis based on job market data
- Detailed skill gap assessment
- Personalized learning paths
- Certification recommendations
- Market trend analysis
- Priority-based skill development recommendations

## Technologies Used

- Node.js
- Express.js
- React
- TypeScript
- Axios
- Cheerio

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:3000`

## Project Structure

```
epic4_certification_roadmap/
├── api/
│   └── realTimeApi.ts
├── services/
│   └── skillGapService.ts
├── components/
│   └── RealTimeSkillTest.tsx
├── test.html
├── server.js
├── package.json
└── tsconfig.json
```

## Usage

1. Enter your resume or skills in the text area
2. Specify your target role
3. Click "Analyze Skills" to get:
   - Current skill levels
   - Required skill levels
   - Skill gaps
   - Market trends
   - Priority scores
   - Detailed recommendations
   - Certification paths
   - Learning paths

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Indeed API for job market data
- Various certification providers for their programs
- Open source community for tools and libraries 