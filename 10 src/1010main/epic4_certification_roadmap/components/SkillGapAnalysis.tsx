import React, { useState } from 'react';
import SkillGapService from '../services/skillGapService';

interface SkillGapProps {
  resume: string;
  targetRole: string;
}

const SkillGapAnalysis: React.FC<SkillGapProps> = ({ resume, targetRole }) => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const skillGapService = new SkillGapService();

  const analyzeSkills = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await skillGapService.analyzeUserSkills(resume, targetRole);
      setAnalysis(result);
    } catch (err) {
      setError('Failed to analyze skills. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Analyzing your skills...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="skill-gap-analysis">
      <button onClick={analyzeSkills} disabled={loading}>
        Analyze Skills
      </button>

      {analysis && (
        <div className="analysis-results">
          <h2>Skill Gap Analysis</h2>
          <div className="skill-gaps">
            {analysis.recommendations.map((skill: any) => (
              <div key={skill.skill} className="skill-card">
                <h3>{skill.skill}</h3>
                <div className="skill-metrics">
                  <p>Current Level: {skill.currentLevel}</p>
                  <p>Required Level: {skill.requiredLevel}</p>
                  <p>Gap: {skill.gap}</p>
                  <p>Market Trend: {skill.marketTrend}</p>
                </div>
                <div className="recommendations">
                  <h4>Recommendations:</h4>
                  <ul>
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

export default SkillGapAnalysis; 