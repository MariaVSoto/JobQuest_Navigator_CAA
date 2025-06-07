import RealTimeAPI from '../api/realTimeApi';

export class SkillGapService {
  private api: RealTimeAPI;

  constructor() {
    this.api = new RealTimeAPI();
  }

  async analyzeUserSkills(resume: string, targetRole: string) {
    try {
      // Get real-time skill data
      const jobData = await this.api.getSkillsForRole(targetRole);
      
      // Process the data
      const analysis = {
        skillGaps: jobData.skills.map(skill => ({
          skill: skill.skill,
          currentLevel: this.estimateCurrentLevel(resume, skill.skill),
          requiredLevel: 5, // High requirement for in-demand skills
          gap: 5 - this.estimateCurrentLevel(resume, skill.skill),
          recommendations: this.generateRecommendations(skill.skill),
          marketTrend: skill.trend
        })),
        marketDemand: jobData.skills
      };

      return {
        skillGaps: analysis.skillGaps,
        marketDemand: analysis.marketDemand,
        recommendations: this.processRecommendations(analysis.skillGaps, analysis.marketDemand)
      };
    } catch (error) {
      console.error('Error in skill gap analysis:', error);
      throw error;
    }
  }

  private estimateCurrentLevel(resume: string, skill: string): number {
    const lowerResume = resume.toLowerCase();
    const lowerSkill = skill.toLowerCase();
    
    // Check for skill mentions in resume
    if (lowerResume.includes(lowerSkill)) {
      // Check for experience indicators
      if (lowerResume.includes('expert') || lowerResume.includes('senior')) return 5;
      if (lowerResume.includes('advanced')) return 4;
      if (lowerResume.includes('intermediate')) return 3;
      if (lowerResume.includes('basic')) return 2;
      return 3; // Default to intermediate if mentioned
    }
    return 0; // Not mentioned
  }

  private generateRecommendations(skill: string): string[] {
    const recommendationMap: { [key: string]: string[] } = {
      'JavaScript': [
        'Complete Advanced JavaScript course on Udemy',
        'Build a full-stack application using Node.js',
        'Practice with React and TypeScript'
      ],
      'Python': [
        'Take Python for Data Science course',
        'Complete 3 Python projects on GitHub',
        'Learn Django framework'
      ],
      'React': [
        'Build a complex React application',
        'Learn Redux state management',
        'Practice with React hooks'
      ],
      'AWS': [
        'Complete AWS Solutions Architect certification',
        'Build a cloud-based application',
        'Practice with AWS services'
      ],
      'Docker': [
        'Learn Docker basics on Docker's official website',
        'Containerize a web application',
        'Practice with Docker Compose'
      ]
    };

    return recommendationMap[skill] || [
      'Take an online course in this skill',
      'Build a project using this technology',
      'Practice with real-world examples'
    ];
  }

  private processRecommendations(skillGaps: any[], marketDemand: any[]) {
    return skillGaps.map(gap => {
      const demand = marketDemand.find(d => d.skill === gap.skill);
      return {
        ...gap,
        priority: this.calculatePriority(gap.gap, demand?.trend)
      };
    }).sort((a, b) => b.priority - a.priority);
  }

  private calculatePriority(gap: number, trend: string): number {
    let priority = gap;
    switch (trend) {
      case 'increasing':
        priority *= 1.5;
        break;
      case 'decreasing':
        priority *= 0.5;
        break;
    }
    return priority;
  }
}

export default SkillGapService; 