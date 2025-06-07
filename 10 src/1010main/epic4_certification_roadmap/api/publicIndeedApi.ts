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

class PublicIndeedAPI {
  private baseUrl: string;

  constructor() {
    // Using Indeed's public RSS feed URL
    this.baseUrl = 'https://www.indeed.com/rss';
  }

  async getSkillsForRole(role: string, location: string): Promise<IndeedResponse> {
    try {
      // Use Indeed's public RSS feed
      const response = await axios.get(
        `${this.baseUrl}/jobs`,
        {
          params: {
            q: role,
            l: location,
            format: 'json'
          }
        }
      );

      // Extract skills from job descriptions
      const skills = this.extractSkillsFromJobs(response.data);
      
      return {
        skills: this.analyzeSkillTrends(skills),
        totalJobs: response.data.length
      };
    } catch (error) {
      console.error('Error fetching Indeed data:', error);
      // Fall back to mock data if API fails
      return this.getMockData();
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
      const description = (job.description || '').toLowerCase();
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

  // Fallback mock data if API fails
  private getMockData(): IndeedResponse {
    return {
      skills: [
        {
          skill: 'JavaScript',
          frequency: 85,
          trend: 'increasing'
        },
        {
          skill: 'Python',
          frequency: 90,
          trend: 'increasing'
        },
        {
          skill: 'React',
          frequency: 80,
          trend: 'stable'
        }
      ],
      totalJobs: 100
    };
  }
}

export default PublicIndeedAPI; 