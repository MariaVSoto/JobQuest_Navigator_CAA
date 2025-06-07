import axios from 'axios';

interface JobSkill {
  skill: string;
  frequency: number;
  trend: 'increasing' | 'decreasing' | 'stable';
}

interface IndeedResponse {
  skills: JobSkill[];
  totalJobs: number;
}

class IndeedAPI {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    this.baseUrl = 'https://api.indeed.com/v2';
    this.apiKey = process.env.INDEED_API_KEY || '';
  }

  async getSkillsForRole(role: string, location: string): Promise<IndeedResponse> {
    try {
      // First, get job listings for the role
      const jobsResponse = await axios.get(
        `${this.baseUrl}/jobs/search`,
        {
          params: {
            query: role,
            location: location,
            limit: 100
          },
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
          },
        }
      );

      // Extract skills from job descriptions
      const skills = this.extractSkillsFromJobs(jobsResponse.data.results);
      
      return {
        skills: this.analyzeSkillTrends(skills),
        totalJobs: jobsResponse.data.totalResults
      };
    } catch (error) {
      console.error('Error fetching Indeed data:', error);
      throw error;
    }
  }

  private extractSkillsFromJobs(jobs: any[]): string[] {
    const commonSkills = [
      'JavaScript', 'Python', 'Java', 'React', 'Node.js', 'SQL',
      'AWS', 'Docker', 'Kubernetes', 'TypeScript', 'Angular', 'Vue.js',
      'C#', 'C++', 'Ruby', 'PHP', 'Go', 'Rust', 'Swift', 'Kotlin'
    ];

    const skills: string[] = [];
    jobs.forEach(job => {
      const description = job.description.toLowerCase();
      commonSkills.forEach(skill => {
        if (description.includes(skill.toLowerCase())) {
          skills.push(skill);
        }
      });
    });

    return skills;
  }

  private analyzeSkillTrends(skills: string[]): JobSkill[] {
    const skillCounts = new Map<string, number>();
    
    // Count skill frequencies
    skills.forEach(skill => {
      skillCounts.set(skill, (skillCounts.get(skill) || 0) + 1);
    });

    // Convert to array and calculate trends
    return Array.from(skillCounts.entries()).map(([skill, count]) => ({
      skill,
      frequency: count,
      trend: this.determineTrend(count, skills.length)
    })).sort((a, b) => b.frequency - a.frequency);
  }

  private determineTrend(frequency: number, totalJobs: number): 'increasing' | 'decreasing' | 'stable' {
    const percentage = (frequency / totalJobs) * 100;
    if (percentage > 70) return 'increasing';
    if (percentage < 30) return 'decreasing';
    return 'stable';
  }
}

export default IndeedAPI; 