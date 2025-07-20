import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import unifiedUserService from '../services/unifiedUserService';
import './Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const { user, updateUserProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [profileData, setProfileData] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    bio: '',
    current_job_title: '',
    years_of_experience: '',
    industry: '',
    career_level: '',
    job_search_status: 'not_looking',
    salary_expectation_min: '',
    salary_expectation_max: '',
    preferred_work_type: ''
  });

  // Load user profile data on component mount
  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const profile = await unifiedUserService.getUserProfile();
        if (profile) {
          setProfileData({
            full_name: profile.full_name || '',
            email: profile.email || '',
            phone_number: profile.phone_number || '',
            bio: profile.bio || '',
            current_job_title: profile.current_job_title || '',
            years_of_experience: profile.years_of_experience || '',
            industry: profile.industry || '',
            career_level: profile.career_level || '',
            job_search_status: profile.job_search_status || 'not_looking',
            salary_expectation_min: profile.salary_expectation_min || '',
            salary_expectation_max: profile.salary_expectation_max || '',
            preferred_work_type: profile.preferred_work_type || ''
          });
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
        setError('Failed to load profile data');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      loadProfile();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleEdit = () => {
    setIsEditing(true);
    setError(null);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      // Prepare update data (exclude email as it's usually not editable)
      const updateData = {
        full_name: profileData.full_name,
        phone_number: profileData.phone_number,
        bio: profileData.bio,
        current_job_title: profileData.current_job_title,
        years_of_experience: profileData.years_of_experience ? parseInt(profileData.years_of_experience) : null,
        industry: profileData.industry,
        career_level: profileData.career_level,
        job_search_status: profileData.job_search_status,
        salary_expectation_min: profileData.salary_expectation_min ? parseFloat(profileData.salary_expectation_min) : null,
        salary_expectation_max: profileData.salary_expectation_max ? parseFloat(profileData.salary_expectation_max) : null,
        preferred_work_type: profileData.preferred_work_type
      };

      const updatedProfile = await unifiedUserService.updateProfile(updateData);
      
      if (updatedProfile) {
        // Update the context with new user data
        await updateUserProfile(updatedProfile);
        setIsEditing(false);
      }
    } catch (err) {
      console.error('Failed to save profile:', err);
      setError('Failed to save profile changes. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setError(null);
    // Reset form data to original user data
    if (user) {
      setProfileData({
        full_name: user.full_name || '',
        email: user.email || '',
        phone_number: user.phone_number || '',
        bio: user.bio || '',
        current_job_title: user.current_job_title || '',
        years_of_experience: user.years_of_experience || '',
        industry: user.industry || '',
        career_level: user.career_level || '',
        job_search_status: user.job_search_status || 'not_looking',
        salary_expectation_min: user.salary_expectation_min || '',
        salary_expectation_max: user.salary_expectation_max || '',
        preferred_work_type: user.preferred_work_type || ''
      });
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <div className="profile-header">
        <div className="profile-avatar">
          <img 
            src={user?.profile_picture || "https://via.placeholder.com/150"} 
            alt="Profile" 
          />
          {!isEditing && (
            <button className="edit-avatar-btn">Change Photo</button>
          )}
        </div>
        <div className="profile-info">
          {isEditing ? (
            <input
              type="text"
              name="full_name"
              value={profileData.full_name}
              onChange={handleInputChange}
              placeholder="Full Name"
              className="profile-input"
            />
          ) : (
            <h1>{profileData.full_name || 'No Name Set'}</h1>
          )}
          <p className="profile-title">{profileData.current_job_title || 'Job Title Not Set'}</p>
          <div className="profile-actions">
            {isEditing ? (
              <div className="edit-actions">
                <button 
                  className="save-btn" 
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button 
                  className="cancel-btn" 
                  onClick={handleCancel}
                  disabled={saving}
                >
                  Cancel
                </button>
              </div>
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
              <p>{profileData.email}</p>
              {isEditing && (
                <small className="info-note">Email cannot be changed</small>
              )}
            </div>
            <div className="info-item">
              <label>Phone</label>
              {isEditing ? (
                <input
                  type="tel"
                  name="phone_number"
                  value={profileData.phone_number}
                  onChange={handleInputChange}
                  placeholder="Phone number"
                  className="profile-input"
                />
              ) : (
                <p>{profileData.phone_number || 'Not provided'}</p>
              )}
            </div>
            <div className="info-item">
              <label>Job Title</label>
              {isEditing ? (
                <input
                  type="text"
                  name="current_job_title"
                  value={profileData.current_job_title}
                  onChange={handleInputChange}
                  placeholder="Current job title"
                  className="profile-input"
                />
              ) : (
                <p>{profileData.current_job_title || 'Not provided'}</p>
              )}
            </div>
            <div className="info-item">
              <label>Industry</label>
              {isEditing ? (
                <input
                  type="text"
                  name="industry"
                  value={profileData.industry}
                  onChange={handleInputChange}
                  placeholder="Industry"
                  className="profile-input"
                />
              ) : (
                <p>{profileData.industry || 'Not provided'}</p>
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
              placeholder="Tell us about yourself..."
              className="profile-textarea"
              rows="4"
            />
          ) : (
            <p>{profileData.bio || 'No bio provided'}</p>
          )}
        </section>

        <section className="profile-section">
          <h2>Professional Information</h2>
          <div className="professional-info">
            <div className="info-row">
              <div className="info-item">
                <label>Years of Experience</label>
                {isEditing ? (
                  <input
                    type="number"
                    name="years_of_experience"
                    value={profileData.years_of_experience}
                    onChange={handleInputChange}
                    placeholder="Years"
                    min="0"
                    max="50"
                    className="profile-input"
                  />
                ) : (
                  <p>{profileData.years_of_experience ? `${profileData.years_of_experience} years` : 'Not provided'}</p>
                )}
              </div>
              <div className="info-item">
                <label>Career Level</label>
                {isEditing ? (
                  <select
                    name="career_level"
                    value={profileData.career_level}
                    onChange={handleInputChange}
                    className="profile-select"
                  >
                    <option value="">Select career level</option>
                    <option value="entry">Entry Level</option>
                    <option value="junior">Junior</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Lead</option>
                    <option value="manager">Manager</option>
                  </select>
                ) : (
                  <p>{profileData.career_level ? profileData.career_level.charAt(0).toUpperCase() + profileData.career_level.slice(1) : 'Not provided'}</p>
                )}
              </div>
            </div>
            
            <div className="info-row">
              <div className="info-item">
                <label>Job Search Status</label>
                {isEditing ? (
                  <select
                    name="job_search_status"
                    value={profileData.job_search_status}
                    onChange={handleInputChange}
                    className="profile-select"
                  >
                    <option value="not_looking">Not Looking</option>
                    <option value="passively_looking">Passively Looking</option>
                    <option value="actively_looking">Actively Looking</option>
                    <option value="urgently_looking">Urgently Looking</option>
                  </select>
                ) : (
                  <p>{profileData.job_search_status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                )}
              </div>
              <div className="info-item">
                <label>Preferred Work Type</label>
                {isEditing ? (
                  <select
                    name="preferred_work_type"
                    value={profileData.preferred_work_type}
                    onChange={handleInputChange}
                    className="profile-select"
                  >
                    <option value="">Select work type</option>
                    <option value="on_site">On-site</option>
                    <option value="remote">Remote</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="flexible">Flexible</option>
                  </select>
                ) : (
                  <p>{profileData.preferred_work_type ? profileData.preferred_work_type.replace('_', '-').charAt(0).toUpperCase() + profileData.preferred_work_type.slice(1) : 'Not provided'}</p>
                )}
              </div>
            </div>

            <div className="info-row">
              <div className="info-item">
                <label>Salary Expectation (Min)</label>
                {isEditing ? (
                  <input
                    type="number"
                    name="salary_expectation_min"
                    value={profileData.salary_expectation_min}
                    onChange={handleInputChange}
                    placeholder="Minimum salary"
                    min="0"
                    className="profile-input"
                  />
                ) : (
                  <p>{profileData.salary_expectation_min ? `$${parseInt(profileData.salary_expectation_min).toLocaleString()}` : 'Not provided'}</p>
                )}
              </div>
              <div className="info-item">
                <label>Salary Expectation (Max)</label>
                {isEditing ? (
                  <input
                    type="number"
                    name="salary_expectation_max"
                    value={profileData.salary_expectation_max}
                    onChange={handleInputChange}
                    placeholder="Maximum salary"
                    min="0"
                    className="profile-input"
                  />
                ) : (
                  <p>{profileData.salary_expectation_max ? `$${parseInt(profileData.salary_expectation_max).toLocaleString()}` : 'Not provided'}</p>
                )}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Profile; 