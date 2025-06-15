import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import JobListings from './pages/JobListings';
import JobApplicationForm from './pages/JobApplicationForm';
import JobMap from './pages/JobMap';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import JobDetails from './pages/JobDetails';
import SavedJobs from './pages/SavedJobs';
import ApplicationHistory from './pages/ApplicationHistory';
import Settings from './pages/Settings';
import NavBar from './components/NavBar';
import { JobProvider } from './context/JobContext';
import CompanyProfile from './pages/CompanyProfile';
import InterviewPrep from './pages/InterviewPrep';
import ResumeBuilder from './pages/ResumeBuilder';
import NotFound from './pages/NotFound';
import './App.css';

function App() {
  return (
    <JobProvider>
      <Router>
        <NavBar />
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/jobs" element={<JobListings />} />
          <Route path="/jobs/:jobId" element={<JobDetails />} />
          <Route path="/apply/:jobId" element={<JobApplicationForm />} />
          <Route path="/map" element={<JobMap />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/saved-jobs" element={<SavedJobs />} />
          <Route path="/application-history" element={<ApplicationHistory />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/company/:companyId" element={<CompanyProfile />} />
          <Route path="/interview-prep" element={<InterviewPrep />} />
          <Route path="/resume-builder" element={<ResumeBuilder />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </JobProvider>
  );
}

export default App;
