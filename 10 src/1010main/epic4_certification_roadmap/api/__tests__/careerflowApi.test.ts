import CareerflowAPI from '../careerflowApi';

describe('CareerflowAPI', () => {
  let api: CareerflowAPI;

  beforeEach(() => {
    api = new CareerflowAPI();
  });

  it('should analyze skill gaps', async () => {
    const mockResume = 'Sample resume content';
    const mockTargetRole = 'Software Engineer';
    
    const result = await api.analyzeSkillGaps(mockResume, mockTargetRole);
    
    expect(result).toHaveProperty('skillGaps');
    expect(result).toHaveProperty('marketDemand');
    expect(Array.isArray(result.skillGaps)).toBe(true);
  });

  it('should get market demand for skills', async () => {
    const mockSkills = ['JavaScript', 'Python', 'React'];
    
    const result = await api.getMarketDemand(mockSkills);
    
    expect(Array.isArray(result)).toBe(true);
    expect(result[0]).toHaveProperty('skill');
    expect(result[0]).toHaveProperty('demand');
    expect(result[0]).toHaveProperty('trend');
  });
}); 