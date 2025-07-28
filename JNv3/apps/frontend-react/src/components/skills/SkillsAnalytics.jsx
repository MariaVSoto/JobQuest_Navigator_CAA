import React, { useState, useEffect } from 'react';
import './SkillsAnalytics.css';

const SkillsAnalytics = ({ userSkills, userCertifications }) => {
  const [analytics, setAnalytics] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('diversity');

  useEffect(() => {
    if (userSkills && userCertifications) {
      calculateAnalytics();
    }
  }, [userSkills, userCertifications]);

  const calculateAnalytics = () => {
    const analytics = {
      diversity: calculateDiversity(),
      marketAlignment: calculateMarketAlignment(),
      learningVelocity: calculateLearningVelocity(),
      categoryDistribution: getCategoryDistribution(),
      proficiencyProgress: getProficiencyProgress(),
      skillGaps: identifySkillGaps()
    };
    setAnalytics(analytics);
  };

  const calculateDiversity = () => {
    const categories = new Set();
    userSkills.forEach(skill => {
      if (skill.skill?.category) {
        categories.add(skill.skill.category);
      }
    });
    
    const score = Math.min(100, (categories.size / 8) * 100); // Assuming 8 major categories
    return {
      score: Math.round(score),
      categories: categories.size,
      trend: score > 60 ? 'up' : score > 30 ? 'stable' : 'down'
    };
  };

  const calculateMarketAlignment = () => {
    const highDemandSkills = userSkills.filter(skill => 
      skill.skill?.market_demand === 'high' || skill.skill?.is_trending
    );
    
    const percentage = userSkills.length > 0 
      ? Math.round((highDemandSkills.length / userSkills.length) * 100)
      : 0;
    
    return {
      percentage,
      trend: percentage > 70 ? 'up' : percentage > 40 ? 'stable' : 'down'
    };
  };

  const calculateLearningVelocity = () => {
    const now = new Date();
    const threeMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());
    
    const recentSkills = userSkills.filter(skill => {
      const createdDate = new Date(skill.created_at || skill.date_added);
      return createdDate >= threeMonthsAgo;
    });
    
    const skillsPerMonth = recentSkills.length / 3;
    
    return {
      skillsPerMonth: skillsPerMonth.toFixed(1),
      trend: skillsPerMonth > 2 ? 'up' : skillsPerMonth > 0.5 ? 'stable' : 'down'
    };
  };

  const getCategoryDistribution = () => {
    const distribution = {};
    userSkills.forEach(skill => {
      const category = skill.skill?.category || 'Other';
      distribution[category] = (distribution[category] || 0) + 1;
    });
    
    return Object.entries(distribution).map(([name, value]) => ({
      name,
      value,
      percentage: Math.round((value / userSkills.length) * 100)
    }));
  };

  const getProficiencyProgress = () => {
    const proficiencyLevels = ['beginner', 'intermediate', 'advanced', 'expert'];
    const distribution = {};
    
    proficiencyLevels.forEach(level => {
      distribution[level] = userSkills.filter(skill => 
        skill.proficiency_level === level
      ).length;
    });
    
    return distribution;
  };

  const identifySkillGaps = () => {
    // Mock skill gaps based on user's current skills
    const commonGaps = [
      {
        skill: 'Cloud Computing',
        demand: 'high',
        reason: 'Highly demanded in current market',
        priority: 'high'
      },
      {
        skill: 'Data Analysis',
        demand: 'medium',
        reason: 'Complements existing technical skills',
        priority: 'medium'
      },
      {
        skill: 'Project Management',
        demand: 'medium',
        reason: 'Important for career advancement',
        priority: 'low'
      }
    ];
    
    return commonGaps.slice(0, 3);
  };

  const MetricCard = ({ title, value, subtitle, trend, onClick, isSelected }) => (
    <div 
      className={`metric-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="metric-header">
        <h3 className="metric-title">{title}</h3>
        <div className={`trend-indicator ${trend}`}>
          {trend === 'up' && '📈'}
          {trend === 'down' && '📉'}
          {trend === 'stable' && '➡️'}
        </div>
      </div>
      
      <div className="metric-value">{value}</div>
      <div className="metric-subtitle">{subtitle}</div>
    </div>
  );

  const CategoryChart = ({ data }) => (
    <div className="category-chart">
      <h4>Skill Categories</h4>
      <div className="chart-bars">
        {data.map((category, index) => (
          <div key={category.name} className="chart-bar">
            <div className="bar-label">{category.name}</div>
            <div className="bar-container">
              <div 
                className="bar-fill"
                style={{ 
                  width: `${category.percentage}%`,
                  backgroundColor: `hsl(${index * 45}, 70%, 60%)`
                }}
              ></div>
            </div>
            <div className="bar-value">{category.value}</div>
          </div>
        ))}
      </div>
    </div>
  );

  const ProficiencyChart = ({ data }) => (
    <div className="proficiency-chart">
      <h4>Proficiency Distribution</h4>
      <div className="proficiency-bars">
        {Object.entries(data).map(([level, count]) => (
          <div key={level} className="proficiency-item">
            <div className="proficiency-label">{level}</div>
            <div className="proficiency-bar">
              <div 
                className={`proficiency-fill proficiency-${level}`}
                style={{ height: `${(count / Math.max(...Object.values(data))) * 100}%` }}
              ></div>
            </div>
            <div className="proficiency-count">{count}</div>
          </div>
        ))}
      </div>
    </div>
  );

  const SkillGapAnalysis = ({ gaps }) => (
    <div className="skill-gaps">
      <h4>Recommended Skills</h4>
      <div className="gaps-list">
        {gaps.map((gap, index) => (
          <div key={index} className={`gap-item priority-${gap.priority}`}>
            <div className="gap-header">
              <h5 className="gap-skill">{gap.skill}</h5>
              <span className={`demand-badge demand-${gap.demand}`}>
                {gap.demand} demand
              </span>
            </div>
            <p className="gap-reason">{gap.reason}</p>
            <button className="add-skill-btn">
              Add to Learning Goals
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  if (!analytics) {
    return (
      <div className="skills-analytics loading">
        <div className="loading-spinner"></div>
        <p>Calculating insights...</p>
      </div>
    );
  }

  return (
    <div className="skills-analytics">
      <div className="analytics-header">
        <h3>Skills Analytics</h3>
        <p>Insights into your skill portfolio and growth opportunities</p>
      </div>

      <div className="analytics-grid">
        <MetricCard
          title="Skill Diversity"
          value={`${analytics.diversity.score}%`}
          subtitle={`${analytics.diversity.categories} categories`}
          trend={analytics.diversity.trend}
          onClick={() => setSelectedMetric('diversity')}
          isSelected={selectedMetric === 'diversity'}
        />
        
        <MetricCard
          title="Market Alignment"
          value={`${analytics.marketAlignment.percentage}%`}
          subtitle="Skills matching job demand"
          trend={analytics.marketAlignment.trend}
          onClick={() => setSelectedMetric('market')}
          isSelected={selectedMetric === 'market'}
        />
        
        <MetricCard
          title="Learning Velocity"
          value={analytics.learningVelocity.skillsPerMonth}
          subtitle="Skills added/month"
          trend={analytics.learningVelocity.trend}
          onClick={() => setSelectedMetric('velocity')}
          isSelected={selectedMetric === 'velocity'}
        />
      </div>

      <div className="analytics-charts">
        <div className="chart-section">
          <CategoryChart data={analytics.categoryDistribution} />
        </div>
        
        <div className="chart-section">
          <ProficiencyChart data={analytics.proficiencyProgress} />
        </div>
      </div>

      <SkillGapAnalysis gaps={analytics.skillGaps} />
    </div>
  );
};

export default SkillsAnalytics;