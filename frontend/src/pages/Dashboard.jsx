import React from 'react';
import './Dashboard.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const user = {
  name: 'Jane Doe',
  email: 'jane.doe@email.com',
  avatar: '',
};

const appliedJobs = [
  { id: 1, title: 'Frontend Developer', company: 'TechCorp', status: 'Under Review' },
  { id: 2, title: 'UI/UX Designer', company: 'Designify', status: 'Interview Scheduled' },
];

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      {/* <img src={logo} alt="JobQuest Logo" className="dashboard-logo" /> */}
      <div className="dashboard-profile">
        <div className="dashboard-avatar">
          {user.avatar ? <img src={user.avatar} alt="avatar" /> : <div className="avatar-placeholder">{user.name[0]}</div>}
        </div>
        <div className="dashboard-info">
          <h1 className="dashboard-title">{user.name}</h1>
          <p>{user.email}</p>
        </div>
      </div>
      <div className="dashboard-applied">
        <h3>Applied Jobs</h3>
        <ul>
          {appliedJobs.map(job => (
            <li key={job.id} className="applied-job">
              <span className="job-title">{job.title}</span>
              <span className="job-company">{job.company}</span>
              <span className="job-status">{job.status}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Dashboard; 