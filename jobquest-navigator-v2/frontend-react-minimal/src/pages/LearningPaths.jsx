import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import './LearningPaths.css';

const LearningPaths = () => {
  const { user } = useAuth();
  const { showSuccess, showInfo } = useToast();
  const [selectedPath, setSelectedPath] = useState(null);
  const [userProgress, setUserProgress] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock data for learning paths
    const mockProgress = {
      'frontend-dev': 65,
      'backend-dev': 30,
      'fullstack-dev': 45,
      'data-science': 20,
      'devops': 10,
      'mobile-dev': 0
    };
    setUserProgress(mockProgress);
    setLoading(false);
  }, []);

  const learningPaths = [
    {
      id: 'frontend-dev',
      title: 'Frontend Development',
      description: 'Master modern frontend technologies and frameworks',
      duration: '6-8 months',
      level: 'Beginner to Advanced',
      skills: ['HTML/CSS', 'JavaScript', 'React', 'TypeScript', 'Web APIs'],
      icon: '🎨',
      color: 'bg-blue-500'
    },
    {
      id: 'backend-dev',
      title: 'Backend Development',
      description: 'Build scalable server-side applications and APIs',
      duration: '8-10 months',
      level: 'Intermediate',
      skills: ['Node.js', 'Python', 'Database Design', 'API Development', 'Cloud Services'],
      icon: '⚙️',
      color: 'bg-green-500'
    },
    {
      id: 'fullstack-dev',
      title: 'Full Stack Development',
      description: 'Comprehensive end-to-end development skills',
      duration: '12-15 months',
      level: 'Beginner to Advanced',
      skills: ['Frontend', 'Backend', 'Databases', 'DevOps', 'System Design'],
      icon: '🔧',
      color: 'bg-purple-500'
    },
    {
      id: 'data-science',
      title: 'Data Science & Analytics',
      description: 'Analyze data and build machine learning models',
      duration: '10-12 months',
      level: 'Intermediate',
      skills: ['Python', 'Statistics', 'Machine Learning', 'Data Visualization', 'SQL'],
      icon: '📊',
      color: 'bg-orange-500'
    },
    {
      id: 'devops',
      title: 'DevOps & Cloud',
      description: 'Infrastructure, automation, and deployment',
      duration: '8-10 months',
      level: 'Intermediate to Advanced',
      skills: ['Docker', 'Kubernetes', 'CI/CD', 'AWS/Azure', 'Monitoring'],
      icon: '☁️',
      color: 'bg-indigo-500'
    },
    {
      id: 'mobile-dev',
      title: 'Mobile Development',
      description: 'Build native and cross-platform mobile apps',
      duration: '6-8 months',
      level: 'Beginner to Intermediate',
      skills: ['React Native', 'Flutter', 'iOS/Android', 'Mobile UI/UX', 'App Store'],
      icon: '📱',
      color: 'bg-pink-500'
    }
  ];

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 60) return 'bg-blue-500';
    if (progress >= 40) return 'bg-yellow-500';
    if (progress >= 20) return 'bg-orange-500';
    return 'bg-gray-300';
  };

  const handleStartPath = (pathId) => {
    // In a real app, this would start the learning path
    console.log('Starting learning path:', pathId);
    // For now, just show a message
    const pathTitle = learningPaths.find(p => p.id === pathId)?.title;
    showSuccess(`Starting ${pathTitle} learning path!`);
  };

  return (
    <div className="page-container">
      <div className="container">
        {/* Header */}
        <div className="page-header">
          <div className="header-content">
            <h1 className="page-title">Learning Paths</h1>
            <p className="page-description">
              Structured learning roadmaps to advance your career in technology
            </p>
          </div>
          <div className="header-actions">
            <Link to="/skills" className="btn btn-outline">
              View Skills Assessment
            </Link>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="progress-overview card mb-8">
          <div className="card-header">
            <h3>Your Learning Progress</h3>
          </div>
          <div className="card-body">
            <div className="progress-summary">
              <div className="summary-stat">
                <div className="stat-number">
                  {Object.values(userProgress).filter(p => p > 0).length}
                </div>
                <div className="stat-label">Active Paths</div>
              </div>
              <div className="summary-stat">
                <div className="stat-number">
                  {Math.round(Object.values(userProgress).reduce((a, b) => a + b, 0) / Object.values(userProgress).length)}%
                </div>
                <div className="stat-label">Average Progress</div>
              </div>
              <div className="summary-stat">
                <div className="stat-number">
                  {Object.values(userProgress).filter(p => p >= 80).length}
                </div>
                <div className="stat-label">Completed</div>
              </div>
            </div>
          </div>
        </div>

        {/* Learning Paths Grid */}
        <div className="learning-paths-grid">
          {learningPaths.map(path => (
            <div key={path.id} className="learning-path-card card">
              <div className="card-body">
                <div className="path-header">
                  <div className={`path-icon ${path.color}`}>
                    {path.icon}
                  </div>
                  <div className="path-info">
                    <h3 className="path-title">{path.title}</h3>
                    <p className="path-level">{path.level}</p>
                  </div>
                </div>

                <p className="path-description">{path.description}</p>
                
                <div className="path-meta">
                  <div className="meta-item">
                    <span className="meta-label">Duration:</span>
                    <span className="meta-value">{path.duration}</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="progress-section">
                  <div className="progress-header">
                    <span className="progress-label">Progress</span>
                    <span className="progress-percentage">{userProgress[path.id] || 0}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className={`progress-fill ${getProgressColor(userProgress[path.id] || 0)}`}
                      style={{ width: `${userProgress[path.id] || 0}%` }}
                    ></div>
                  </div>
                </div>

                {/* Skills */}
                <div className="skills-section">
                  <h4 className="skills-title">Key Skills</h4>
                  <div className="skills-tags">
                    {path.skills.map(skill => (
                      <span key={skill} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="path-actions">
                  {userProgress[path.id] > 0 ? (
                    <button 
                      className="btn btn-primary btn-block"
                      onClick={() => handleStartPath(path.id)}
                    >
                      Continue Learning
                    </button>
                  ) : (
                    <button 
                      className="btn btn-outline btn-block"
                      onClick={() => handleStartPath(path.id)}
                    >
                      Start Path
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Recommendations */}
        <div className="recommendations-section">
          <div className="card">
            <div className="card-header">
              <h3>Recommended for You</h3>
            </div>
            <div className="card-body">
              <div className="recommendation-content">
                <div className="recommendation-icon">🎯</div>
                <div className="recommendation-text">
                  <h4>Based on your skills assessment</h4>
                  <p>We recommend starting with <strong>Frontend Development</strong> to build on your existing web development knowledge.</p>
                </div>
                <div className="recommendation-action">
                  <Link to="/skills" className="btn btn-primary">
                    Take Skills Assessment
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningPaths;