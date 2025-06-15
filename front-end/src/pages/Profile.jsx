import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    fullName: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1 234 567 8900',
    location: 'New York, USA',
    bio: 'Experienced software developer with a passion for creating innovative solutions.',
    skills: ['JavaScript', 'React', 'Node.js', 'Python'],
    experience: [
      {
        title: 'Senior Software Engineer',
        company: 'Tech Corp',
        duration: '2020 - Present',
        description: 'Leading development of enterprise applications.'
      }
    ],
    education: [
      {
        degree: 'Bachelor of Science in Computer Science',
        school: 'University of Technology',
        year: '2016 - 2020'
      }
    ]
  });

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    setIsEditing(false);
    // Here we would typically save the data to the backend
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar">
          <img src="https://via.placeholder.com/150" alt="Profile" />
          {!isEditing && (
            <button className="edit-avatar-btn">Change Photo</button>
          )}
        </div>
        <div className="profile-info">
          {isEditing ? (
            <input
              type="text"
              name="fullName"
              value={profileData.fullName}
              onChange={handleInputChange}
              className="profile-input"
            />
          ) : (
            <h1>{profileData.fullName}</h1>
          )}
          <p className="profile-title">Software Developer</p>
          <div className="profile-actions">
            {isEditing ? (
              <button className="save-btn" onClick={handleSave}>Save Changes</button>
            ) : (
              <button className="edit-btn" onClick={handleEdit}>Edit Profile</button>
            )}
          </div>
        </div>
      </div>

      <div className="profile-content">
        <section className="profile-section">
          <h2>Contact Information</h2>
          <div className="contact-info">
            <div className="info-item">
              <label>Email</label>
              {isEditing ? (
                <input
                  type="email"
                  name="email"
                  value={profileData.email}
                  onChange={handleInputChange}
                  className="profile-input"
                />
              ) : (
                <p>{profileData.email}</p>
              )}
            </div>
            <div className="info-item">
              <label>Phone</label>
              {isEditing ? (
                <input
                  type="tel"
                  name="phone"
                  value={profileData.phone}
                  onChange={handleInputChange}
                  className="profile-input"
                />
              ) : (
                <p>{profileData.phone}</p>
              )}
            </div>
            <div className="info-item">
              <label>Location</label>
              {isEditing ? (
                <input
                  type="text"
                  name="location"
                  value={profileData.location}
                  onChange={handleInputChange}
                  className="profile-input"
                />
              ) : (
                <p>{profileData.location}</p>
              )}
            </div>
          </div>
        </section>

        <section className="profile-section">
          <h2>About</h2>
          {isEditing ? (
            <textarea
              name="bio"
              value={profileData.bio}
              onChange={handleInputChange}
              className="profile-textarea"
            />
          ) : (
            <p>{profileData.bio}</p>
          )}
        </section>

        <section className="profile-section">
          <h2>Skills</h2>
          <div className="skills-list">
            {profileData.skills.map((skill, index) => (
              <span key={index} className="skill-tag">{skill}</span>
            ))}
            {isEditing && (
              <button className="add-skill-btn">+ Add Skill</button>
            )}
          </div>
        </section>

        <section className="profile-section">
          <h2>Experience</h2>
          {profileData.experience.map((exp, index) => (
            <div key={index} className="experience-item">
              <h3>{exp.title}</h3>
              <p className="company">{exp.company}</p>
              <p className="duration">{exp.duration}</p>
              <p>{exp.description}</p>
            </div>
          ))}
          {isEditing && (
            <button className="add-experience-btn">+ Add Experience</button>
          )}
        </section>

        <section className="profile-section">
          <h2>Education</h2>
          {profileData.education.map((edu, index) => (
            <div key={index} className="education-item">
              <h3>{edu.degree}</h3>
              <p className="school">{edu.school}</p>
              <p className="year">{edu.year}</p>
            </div>
          ))}
          {isEditing && (
            <button className="add-education-btn">+ Add Education</button>
          )}
        </section>
      </div>
    </div>
  );
};

export default Profile; 