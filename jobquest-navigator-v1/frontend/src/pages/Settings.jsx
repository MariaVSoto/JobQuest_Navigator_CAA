import React, { useState } from 'react';
import './Settings.css';

const Settings = () => {
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      applicationUpdates: true,
      jobAlerts: true,
      marketingEmails: false
    },
    privacy: {
      profileVisibility: 'public',
      showEmail: false,
      showPhone: false
    },
    preferences: {
      jobAlerts: true,
      weeklyDigest: true,
      darkMode: false,
      language: 'en'
    }
  });

  const handleNotificationChange = (setting) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [setting]: !prev.notifications[setting]
      }
    }));
  };

  const handlePrivacyChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      privacy: {
        ...prev.privacy,
        [setting]: value
      }
    }));
  };

  const handlePreferenceChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [setting]: value
      }
    }));
  };

  const handleSaveSettings = () => {
    // TODO: Implement API call to save settings
    console.log('Saving settings:', settings);
  };

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1>Settings</h1>
        <p>Manage your account settings and preferences</p>
      </div>

      <div className="settings-content">
        {/* Notifications Section */}
        <section className="settings-section">
          <h2>Notifications</h2>
          <div className="settings-group">
            <div className="setting-item">
              <div className="setting-info">
                <h3>Email Notifications</h3>
                <p>Receive notifications via email</p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.email}
                  onChange={() => handleNotificationChange('email')}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Application Updates</h3>
                <p>Get notified about your application status changes</p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.applicationUpdates}
                  onChange={() => handleNotificationChange('applicationUpdates')}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Job Alerts</h3>
                <p>Receive alerts for new job opportunities</p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.jobAlerts}
                  onChange={() => handleNotificationChange('jobAlerts')}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Marketing Emails</h3>
                <p>Receive promotional emails and updates</p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.marketingEmails}
                  onChange={() => handleNotificationChange('marketingEmails')}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </section>

        {/* Privacy Section */}
        <section className="settings-section">
          <h2>Privacy</h2>
          <div className="settings-group">
            <div className="setting-item">
              <div className="setting-info">
                <h3>Profile Visibility</h3>
                <p>Control who can see your profile</p>
              </div>
              <select
                value={settings.privacy.profileVisibility}
                onChange={(e) => handlePrivacyChange('profileVisibility', e.target.value)}
                className="select-input"
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
                <option value="connections">Connections Only</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Show Email</h3>
                <p>Display your email on your profile</p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.privacy.showEmail}
                  onChange={() => handlePrivacyChange('showEmail', !settings.privacy.showEmail)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Show Phone</h3>
                <p>Display your phone number on your profile</p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.privacy.showPhone}
                  onChange={() => handlePrivacyChange('showPhone', !settings.privacy.showPhone)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </section>

        {/* Preferences Section */}
        <section className="settings-section">
          <h2>Preferences</h2>
          <div className="settings-group">
            <div className="setting-item">
              <div className="setting-info">
                <h3>Job Alert Frequency</h3>
                <p>How often you want to receive job alerts</p>
              </div>
              <select
                value={settings.preferences.jobAlerts ? 'daily' : 'weekly'}
                onChange={(e) => handlePreferenceChange('jobAlerts', e.target.value === 'daily')}
                className="select-input"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Weekly Digest</h3>
                <p>Receive a weekly summary of your job search activity</p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.preferences.weeklyDigest}
                  onChange={() => handlePreferenceChange('weeklyDigest', !settings.preferences.weeklyDigest)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Dark Mode</h3>
                <p>Switch between light and dark theme</p>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={settings.preferences.darkMode}
                  onChange={() => handlePreferenceChange('darkMode', !settings.preferences.darkMode)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Language</h3>
                <p>Select your preferred language</p>
              </div>
              <select
                value={settings.preferences.language}
                onChange={(e) => handlePreferenceChange('language', e.target.value)}
                className="select-input"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </select>
            </div>
          </div>
        </section>

        <div className="settings-actions">
          <button className="save-button" onClick={handleSaveSettings}>
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings; 