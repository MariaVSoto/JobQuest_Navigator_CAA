import React, { useState } from 'react';
import './InterviewPrep.css';

const InterviewPrep = () => {
  const [activeTab, setActiveTab] = useState('tips');
  const [selectedCategory, setSelectedCategory] = useState('general');

  const interviewTips = {
    general: [
      {
        title: "Research the Company",
        content: "Learn about the company's history, mission, values, and recent news. This shows your interest and helps you tailor your responses."
      },
      {
        title: "Practice Common Questions",
        content: "Prepare answers for common interview questions like 'Tell me about yourself' and 'Why do you want to work here?'"
      },
      {
        title: "Dress Appropriately",
        content: "Choose professional attire that matches the company culture. When in doubt, it's better to be slightly overdressed."
      }
    ],
    technical: [
      {
        title: "Review Technical Concepts",
        content: "Brush up on key technical concepts and be prepared to explain your thought process during problem-solving."
      },
      {
        title: "Prepare Your Portfolio",
        content: "Have your projects and code samples ready to discuss. Be prepared to explain your technical decisions."
      },
      {
        title: "Practice Coding",
        content: "Practice coding problems and system design questions. Focus on explaining your approach clearly."
      }
    ],
    behavioral: [
      {
        title: "Use the STAR Method",
        content: "Structure your answers using Situation, Task, Action, and Result to provide clear, concise responses."
      },
      {
        title: "Prepare Examples",
        content: "Have specific examples ready that demonstrate your skills, achievements, and how you handle challenges."
      },
      {
        title: "Show Enthusiasm",
        content: "Express genuine interest in the role and company. Ask thoughtful questions about the position."
      }
    ]
  };

  const commonQuestions = {
    general: [
      {
        question: "Tell me about yourself.",
        answer: "Focus on your professional background, key achievements, and what makes you a good fit for the role."
      },
      {
        question: "Why do you want to work here?",
        answer: "Show your research and explain how your skills and values align with the company's mission."
      },
      {
        question: "Where do you see yourself in 5 years?",
        answer: "Discuss your career goals and how they align with the company's growth opportunities."
      }
    ],
    technical: [
      {
        question: "Explain a technical concept to a non-technical person.",
        answer: "Use analogies and simple language to break down complex concepts."
      },
      {
        question: "How do you handle technical challenges?",
        answer: "Describe your problem-solving process and how you learn from difficult situations."
      },
      {
        question: "What's your approach to learning new technologies?",
        answer: "Explain your learning process and how you stay updated with industry trends."
      }
    ],
    behavioral: [
      {
        question: "Tell me about a time you faced a challenge at work.",
        answer: "Use the STAR method to describe the situation, your actions, and the positive outcome."
      },
      {
        question: "How do you handle conflict in the workplace?",
        answer: "Focus on communication, collaboration, and finding mutually beneficial solutions."
      },
      {
        question: "Describe a successful project you worked on.",
        answer: "Highlight your role, the challenges overcome, and the impact of the project."
      }
    ]
  };

  const resources = [
    {
      title: "Interview Preparation Guide",
      type: "PDF",
      description: "Comprehensive guide covering all aspects of interview preparation",
      link: "#"
    },
    {
      title: "Common Interview Questions",
      type: "PDF",
      description: "List of frequently asked questions with sample answers",
      link: "#"
    },
    {
      title: "Technical Interview Tips",
      type: "Video",
      description: "Video series on preparing for technical interviews",
      link: "#"
    },
    {
      title: "Behavioral Interview Workshop",
      type: "Video",
      description: "Workshop on mastering behavioral interview questions",
      link: "#"
    }
  ];

  return (
    <div className="interview-prep-container">
      <div className="interview-prep-header">
        <h1>Interview Preparation</h1>
        <p>Get ready for your next interview with our comprehensive resources</p>
      </div>

      <div className="interview-prep-content">
        <div className="interview-tabs">
          <button
            className={activeTab === 'tips' ? 'active' : ''}
            onClick={() => setActiveTab('tips')}
          >
            Interview Tips
          </button>
          <button
            className={activeTab === 'questions' ? 'active' : ''}
            onClick={() => setActiveTab('questions')}
          >
            Common Questions
          </button>
          <button
            className={activeTab === 'resources' ? 'active' : ''}
            onClick={() => setActiveTab('resources')}
          >
            Resources
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'tips' && (
            <div className="tips-section">
              <div className="category-selector">
                <button
                  className={selectedCategory === 'general' ? 'active' : ''}
                  onClick={() => setSelectedCategory('general')}
                >
                  General
                </button>
                <button
                  className={selectedCategory === 'technical' ? 'active' : ''}
                  onClick={() => setSelectedCategory('technical')}
                >
                  Technical
                </button>
                <button
                  className={selectedCategory === 'behavioral' ? 'active' : ''}
                  onClick={() => setSelectedCategory('behavioral')}
                >
                  Behavioral
                </button>
              </div>

              <div className="tips-list">
                {interviewTips[selectedCategory].map((tip, index) => (
                  <div key={index} className="tip-card">
                    <h3>{tip.title}</h3>
                    <p>{tip.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'questions' && (
            <div className="questions-section">
              <div className="category-selector">
                <button
                  className={selectedCategory === 'general' ? 'active' : ''}
                  onClick={() => setSelectedCategory('general')}
                >
                  General
                </button>
                <button
                  className={selectedCategory === 'technical' ? 'active' : ''}
                  onClick={() => setSelectedCategory('technical')}
                >
                  Technical
                </button>
                <button
                  className={selectedCategory === 'behavioral' ? 'active' : ''}
                  onClick={() => setSelectedCategory('behavioral')}
                >
                  Behavioral
                </button>
              </div>

              <div className="questions-list">
                {commonQuestions[selectedCategory].map((item, index) => (
                  <div key={index} className="question-card">
                    <h3>{item.question}</h3>
                    <p>{item.answer}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'resources' && (
            <div className="resources-section">
              <div className="resources-list">
                {resources.map((resource, index) => (
                  <div key={index} className="resource-card">
                    <div className="resource-type">{resource.type}</div>
                    <h3>{resource.title}</h3>
                    <p>{resource.description}</p>
                    <a href={resource.link} className="resource-link">
                      View Resource
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterviewPrep; 