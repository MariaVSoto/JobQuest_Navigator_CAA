// Mock data for development and testing
const mockSkillGaps = [
  {
    skill: "JavaScript",
    currentLevel: 3,
    requiredLevel: 5,
    gap: 2,
    recommendations: [
      "Complete Advanced JavaScript course on Udemy",
      "Build a full-stack application using Node.js",
      "Practice with React and TypeScript"
    ]
  },
  {
    skill: "Python",
    currentLevel: 2,
    requiredLevel: 4,
    gap: 2,
    recommendations: [
      "Take Python for Data Science course",
      "Complete 3 Python projects on GitHub",
      "Learn Django framework"
    ]
  },
  {
    skill: "React",
    currentLevel: 3,
    requiredLevel: 5,
    gap: 2,
    recommendations: [
      "Build a complex React application",
      "Learn Redux state management",
      "Practice with React hooks"
    ]
  }
];

const mockMarketDemand = [
  {
    skill: "JavaScript",
    demand: 85,
    trend: "increasing"
  },
  {
    skill: "Python",
    demand: 90,
    trend: "increasing"
  },
  {
    skill: "React",
    demand: 80,
    trend: "stable"
  }
];

class MockCareerflowAPI {
  async analyzeSkillGaps(resume: string, targetRole: string) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      skillGaps: mockSkillGaps,
      marketDemand: mockMarketDemand
    };
  }

  async getMarketDemand(skills: string[]) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return mockMarketDemand.filter(demand => 
      skills.includes(demand.skill)
    );
  }
}

export default MockCareerflowAPI; 