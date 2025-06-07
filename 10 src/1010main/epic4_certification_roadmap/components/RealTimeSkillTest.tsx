import React, { useState } from 'react';
import SkillGapService from '../services/skillGapService';

const RealTimeSkillTest: React.FC = () => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const skillGapService = new SkillGapService();

  const testAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Sample resume
      const sampleResume = `
        Software Developer with 2 years of experience in web development.
        Proficient in JavaScript and React. Basic knowledge of Python.
        Looking to enhance skills in cloud technologies.
      `;
      
      const result = await skillGapService.analyzeUserSkills(
        sampleResume,
        'Senior Software Engineer'
      );
      
      setAnalysis(result);
    } catch (err) {
      setError('Failed to analyze skills. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Real-Time Skill Gap Analysis</h2>
      
      <button 
        onClick={testAnalysis} 
        disabled={loading}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: loading ? 'not-allowed' : 'pointer',
          marginBottom: '20px'
        }}
      >
        {loading ? 'Analyzing...' : 'Analyze Skills'}
      </button>

      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          {error}
        </div>
      )}

      {analysis && (
        <div>
          <h3>Analysis Results</h3>
          <div style={{ display: 'grid', gap: '20px' }}>
            {analysis.recommendations.map((skill: any) => (
              <div 
                key={skill.skill}
                style={{
                  padding: '15px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  backgroundColor: '#f8f9fa'
                }}
              >
                <h4 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>
                  {skill.skill}
                </h4>
                
                <div style={{ marginBottom: '10px' }}>
                  <p><strong>Current Level:</strong> {skill.currentLevel}/5</p>
                  <p><strong>Required Level:</strong> {skill.requiredLevel}/5</p>
                  <p><strong>Gap:</strong> {skill.gap}</p>
                  <p><strong>Market Trend:</strong> {skill.marketTrend}</p>
                  <p><strong>Priority:</strong> {skill.priority.toFixed(1)}</p>
                </div>

                <div>
                  <strong>Recommendations:</strong>
                  <ul style={{ marginTop: '5px' }}>
                    {skill.recommendations.map((rec: string, index: number) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeSkillTest; 