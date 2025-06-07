import axios from 'axios';

// Types for Careerflow API responses
interface SkillGap {
  skill: string;
  currentLevel: number;
  requiredLevel: number;
  gap: number;
  recommendations: string[];
}

interface CareerflowResponse {
  skillGaps: SkillGap[];
  marketDemand: {
    skill: string;
    demand: number;
    trend: 'increasing' | 'decreasing' | 'stable';
  }[];
}

class CareerflowAPI {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    this.baseUrl = process.env.CAREERFLOW_API_URL || 'https://api.careerflow.com/v1';
    this.apiKey = process.env.CAREERFLOW_API_KEY || '';
  }

  async analyzeSkillGaps(resume: string, targetRole: string): Promise<CareerflowResponse> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/analyze`,
        {
          resume,
          targetRole,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error analyzing skill gaps:', error);
      throw error;
    }
  }

  async getMarketDemand(skills: string[]): Promise<CareerflowResponse['marketDemand']> {
    try {
      const response = await axios.get(
        `${this.baseUrl}/market-demand`,
        {
          params: { skills: skills.join(',') },
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching market demand:', error);
      throw error;
    }
  }
}

export default CareerflowAPI; 